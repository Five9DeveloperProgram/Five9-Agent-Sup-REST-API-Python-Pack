import asyncio
import inspect
import json
import logging

import requests
import websockets

from five9_agent_sup_rest.config import CONTEXT_PATHS
from five9_agent_sup_rest.config import SETTINGS

from five9_agent_sup_rest.exceptions import Five9DuplicateLoginError

from five9_agent_sup_rest.methods.base import SupervisorRestMethod, AgentRestMethod
from five9_agent_sup_rest.methods import agent_methods, supervisor_methods

from five9_agent_sup_rest.methods import default_socket_handlers


API_METHOD_MODULES = {
    "agent_methods": {
        "module": agent_methods,
        "sublass": AgentRestMethod,
    },
    "supervisor_methods": {
        "module": supervisor_methods,
        "sublass": SupervisorRestMethod,
    },
}


class Five9RestClientSessionConfig:
    """
    Holds session credentials and API endpoint URLs derived from the Five9 login
    response. Implements the Observable side of the Observer pattern.

    The problem this solves: each REST method object caches a reference to this
    config and reads `base_api_url` and `api_header` (which contains the bearer
    token) at call time. When the session is re-authenticated — e.g. after a
    token expiry — those values change. Rather than requiring callers to
    reinstantiate every method object, this class maintains a list of observer
    objects (the method instances) and notifies them all via `update_config`
    whenever new session metadata is processed. This keeps every method object
    automatically in sync with the latest credentials.
    """

    def __init__(self, *args, **kwargs):
        self.observers = []

        self.username = kwargs.get("username", "")
        self.password = kwargs.get("password", "")
        self.app_key = kwargs.get("app_key", "python_pack")

        self.login_payload = {
            "passwordCredentials": {
                "username": self.username,
                "password": self.password,
            },
            "appKey": "mypythonapp-supervisor-session",
            "policy": "AttachExisting",
        }
        self.region = kwargs.get("region", "US")
        self.login_url = kwargs.get(
            "login_url", SETTINGS[self.region].get("FIVENINE_VCC_LOGIN_URL", "")
        )

        # Skip login if session_metadata is provided (e.g., from SSO)
        session_metadata = kwargs.get("session_metadata")
        if session_metadata:
            self.cookies_header = ""
            self.session_metadata = session_metadata
            self.process_session_metadata()
        else:
            self.login()

    @classmethod
    def from_sso_metadata(cls, session_metadata: dict, app_key: str = "python_pack"):
        """
        Create a session config from SSO-obtained session metadata.
        
        This bypasses the normal login flow and uses pre-authenticated
        session metadata from the SSO module.
        
        Args:
            session_metadata: Dict returned by authenticate_with_saml(), containing:
                - tokenId, orgId, userId, context, metadata
                - _cookies: Cookie string from login_by_token response
            app_key: Application key for the session.
            
        Returns:
            Five9RestClientSessionConfig: Configured session ready for API calls.
        """
        instance = cls.__new__(cls)
        instance.observers = []
        instance.username = ""
        instance.password = ""
        instance.app_key = app_key
        instance.login_payload = {}
        instance.region = ""
        instance.login_url = ""
        # Use cookies from SSO response if available
        instance.cookies_header = session_metadata.get("_cookies", "")
        instance.session_metadata = session_metadata
        instance.process_session_metadata()
        return instance

    def login(self, *args, **kwargs):
        """Authenticate against the Five9 login endpoint and process the session.

        Stores cookies and calls process_session_metadata on success.
        Returns True if metadata was received, False otherwise.
        """
        self.session_metadata = None

        login_request = requests.post(self.login_url, json=self.login_payload)

        self.session_metadata = login_request.json()
        logging.debug(
            f"Five9RestClientSessionConfig - Login Result: {self.session_metadata}"
        )

        if login_request.status_code < 400:
            logging.debug(f"SESSION COOKIES {login_request.cookies}")
            self.cookies_header = "; ".join(
                [f"{cookie.name}={cookie.value}" for cookie in login_request.cookies]
            )

        if self.session_metadata:
            self.process_session_metadata()
            return True
        else:
            return False

    def process_session_metadata(self, *args, **kwargs):
        # Break down the processing into smaller, manageable parts
        self.set_api_urls()
        self.set_credentials()
        self.set_api_header()

        # Notify observers after processing is complete
        self.notify_observers()
        logging.debug(
            f"Metadata Processing Complete - Base API URL: {self.base_api_url}"
        )
        return True

    def set_api_urls(self):
        data_center_info = self.session_metadata["metadata"]["dataCenters"][0]
        api_url_info = data_center_info["apiUrls"][0]

        self.host = api_url_info["host"]
        self.port = api_url_info["port"]
        self.base_api_url = f"https://{self.host}:{self.port}"

        logging.debug(f"API URLs Set - Base API URL: {self.base_api_url}")

    def set_credentials(self):
        self.orgId = self.session_metadata["orgId"]
        self.userId = self.session_metadata["userId"]
        self.farmId = self.session_metadata["context"]["farmId"]
        self.tokenId = self.session_metadata["tokenId"]
        self.cloudClientUrl = self.session_metadata["context"].get("cloudClientUrl", "").rstrip("/")

        logging.debug(f"Credentials Set - UserID: {self.userId}, OrgID: {self.orgId}")

    def set_api_header(self):
        self.api_header = {
            "Authorization": f"Bearer-{self.tokenId}",
            "farmId": self.farmId,
            "Accept": "application/json, text/javascript",
            "Cookie": self.cookies_header,
        }
        logging.debug(
            f"API Header Set - Authorization Token: {self.api_header['Authorization']}"
        )

    def subscribe_observer(self, observer):
        """Register an observer to be notified when session metadata is refreshed.

        Called automatically by `FiveNineRestMethod.update_config` so that
        every method instance is kept up to date after a re-login.
        """
        if observer not in self.observers:
            self.observers.append(observer)

    def notify_observers(self, *args, **kwargs):
        """Push the updated config to all registered observers.

        Called at the end of `process_session_metadata` so that every
        registered REST method object receives the new base URL, auth header,
        and other session-derived values immediately after a login or re-login.
        """
        for observer in self.observers:
            observer.update_config(self)


class Five9RestClient:
    """Main entry point for interacting with the Five9 Agent/Supervisor REST API.

    Exposes two namespaces populated with all available API methods:
      - ``client.agent``      — Agent REST API methods
      - ``client.supervisor`` — Supervisor REST API methods

    After construction, call :meth:`initialize_supervisor_session` or
    :meth:`initialize_agent_session` to complete the login flow and open a
    WebSocket for real-time events.

    Args:
        username (str): Five9 agent or supervisor username.
        password (str): Corresponding Five9 password.
        stationId (str, optional): Station ID to register on session start.
            Defaults to ``""`` (no station).
        stationType (str, optional): Station type (e.g. ``"GATEWAY"``).
            Defaults to ``"EMPTY"``.
        stationState (str, optional): Initial station state.
            Defaults to ``"DISCONNECTED"``.
        custom_supervisor_methods (list, optional): Additional
            :class:`~five9_agent_sup_rest.methods.base.SupervisorRestMethod`
            subclasses to attach to ``client.supervisor``.
        custom_agent_methods (list, optional): Additional
            :class:`~five9_agent_sup_rest.methods.base.AgentRestMethod`
            subclasses to attach to ``client.agent``.
        custom_socket_handlers (list, optional): Additional
            :class:`~five9_agent_sup_rest.methods.default_socket_handlers.SocketEventHandler`
            subclasses to register on the WebSocket connection.
        socket_app_key (str, optional): Arbitrary identifier used in the
            WebSocket URI. Defaults to ``"python_pack_socket"``.
    """

    class RESTNamespace:
        """Dynamic namespace whose attributes are instantiated REST method objects.

        Built at client construction time by inspecting the given module for all
        subclasses of the expected base class and attaching an instance of each
        as an attribute named after the class.
        """

        def __init__(
            self, target_module, session_configuration: Five9RestClientSessionConfig
        ):
            for name, obj in inspect.getmembers(
                API_METHOD_MODULES[target_module]["module"]
            ):
                if inspect.isclass(obj) and issubclass(
                    obj, API_METHOD_MODULES[target_module]["sublass"]
                ):
                    setattr(self, name, obj(session_configuration))

    def __init__(self, *args, **kwargs):
        self.stationId = kwargs.get("stationId", "")
        self.stationType = kwargs.get("stationType", "EMPTY")
        self.stationState = kwargs.get("stationState", "DISCONNECTED")

        custom_supervisor_methods = kwargs.get("custom_supervisor_methods", [])
        custom_agent_methods = kwargs.get("custom_agent_methods", [])
        
        self.custom_socket_handlers = kwargs.get("custom_socket_handlers", {})
        self.socket_app_key = kwargs.get("socket_app_key", "python_pack_socket")

        self.logged_in = False

        # Support SSO: if session_metadata is provided, use it directly
        session_metadata = kwargs.get("session_metadata")
        if session_metadata:
            logging.info("Initializing VCC_Client from SSO session metadata")
            self.session_configuration = Five9RestClientSessionConfig.from_sso_metadata(
                session_metadata, app_key=self.socket_app_key
            )
        else:
            logging.info(f"Initializing VCC_Client for user: {kwargs['username']}")
            self.session_configuration = Five9RestClientSessionConfig(
                username=kwargs["username"],
                password=kwargs["password"],
                app_key=self.socket_app_key,
            )

        self.agent = self.RESTNamespace("agent_methods", self.session_configuration)
        self.supervisor = self.RESTNamespace(
            "supervisor_methods", self.session_configuration
        )

        for method in custom_supervisor_methods:
            if inspect.isclass(method) and issubclass(method, SupervisorRestMethod):
                setattr(
                    self.supervisor, method.__name__, method(self.session_configuration)
                )
                logging.info(f"Custom Supervisor Method Added: {method.__name__}")

        for method in custom_agent_methods:
            if inspect.isclass(method) and issubclass(method, AgentRestMethod):
                setattr(self.agent, method.__name__, method(self.session_configuration))
                logging.info(f"Custom Agent Method Added: {method.__name__}")

        self.extensions = {}

    def accept_maintenance_notices(self, user_type="supervisor"):
        """Fetch and accept any pending maintenance notices for the given user type.

        Five9 requires that outstanding maintenance notices are acknowledged
        before a session can reach the WORKING state.  ``initialize_supervisor_session``
        and ``initialize_agent_session`` call this automatically when
        ``auto_accept_notice=True``.

        Args:
            user_type (str): ``"supervisor"`` or ``"agent"``.
        """
        if user_type == "supervisor":
            logging.info(f"Accepting Maintenance Notice for Supervisor: {self.session_configuration.userId}")
            notices = self.supervisor.MaintenanceNoticesGet.invoke()
            for notice in notices:
                if notice["accepted"] == False:
                    self.supervisor.MaintenanceNoticeAccept.invoke(notice["id"])
                    logging.info(f"Accepted Maintenance Notice: {notice['id']}")

        if user_type == "agent":
            logging.info(f"Accepting Maintenance Notice for Agent: {self.session_configuration.userId}")
            notices = self.agent.MaintenanceNoticesGet.invoke()
            for notice in notices:
                if notice["accepted"] == False:
                    self.agent.MaintenanceNoticeAccept.invoke(notice["id"])
                    logging.info(f"Accepted Maintenance Notice: {notice['id']}")

    def initialize_supervisor_session(
        self, socket_handlers={}, auto_accept_notice=True
    ):
        """Complete the supervisor login flow and open a WebSocket connection.

        Handles all intermediate login states automatically:
          - ``SELECT_STATION`` → calls SupervisorSessionStart, then opens the socket.
          - ``ACCEPT_NOTICE``  → accepts maintenance notices (if auto_accept_notice),
            then continues.
          - ``WORKING``        → session already active, opens the socket directly.

        Args:
            socket_handlers (dict, optional): Additional event handlers to register
                on the socket beyond the built-in defaults.
            auto_accept_notice (bool): Whether to automatically accept pending
                maintenance notices. Defaults to True.

        Returns:
            True on success, False if a duplicate-login conflict was detected
            (the conflicting session is logged out automatically; the caller
            should retry).
        """
        current_supervisor_login_state = self.supervisor_login_state
        logging.debug(f"\n\nCurrent Supervisor Login State: {current_supervisor_login_state}")

        self.socket_handlers = socket_handlers
        
        current_supervisor_login_state = self.supervisor_login_state

        if current_supervisor_login_state == "WORKING":
            self.supervisor_socket = Five9Socket(
                self, "supervisor", self.socket_app_key
            )
            return True

        if current_supervisor_login_state in ["ACCEPT_NOTICE", "WORKING"]:
            if auto_accept_notice == True:
                self.accept_maintenance_notices(user_type="supervisor")

        if current_supervisor_login_state == "SELECT_STATION":
            try:
                session = self.supervisor.SupervisorSessionStart.invoke(
                    self.stationId, self.stationType, self.stationState
                )
                current_supervisor_login_state = self.supervisor_login_state
                if auto_accept_notice == True and current_supervisor_login_state == "ACCEPT_NOTICE":
                    self.accept_maintenance_notices(user_type="supervisor")
                
            except Five9DuplicateLoginError:
                logging.info(
                    "Supervisor already logged in, logging out, please try again."
                )
                self.supervisor.LogOut.invoke()
                return False

            logging.debug(f"SUPERVISOR SESSION STARTED Result: {session.__dict__}")
            self.supervisor_socket = Five9Socket(
                self, "supervisor", self.socket_app_key
            )
            return True

    def initialize_agent_session(self, auto_accept_notice=True):
        """Complete the agent login flow and open a WebSocket connection.

        Mirrors :meth:`initialize_supervisor_session` for the agent context.
        Handles SELECT_STATION, ACCEPT_NOTICE, and WORKING states.

        Args:
            auto_accept_notice (bool): Whether to automatically accept pending
                maintenance notices. Defaults to True.

        Returns:
            True on success, False if a duplicate-login conflict was detected
            (the conflicting session is logged out automatically; the caller
            should retry).
        """
           
        current_agent_login_state = self.agent_login_state

        if current_agent_login_state == "WORKING":
            self.supervisor_socket = Five9Socket(
                self, "supervisor", self.socket_app_key
            )
            return True

        if current_agent_login_state in ["ACCEPT_NOTICE", "WORKING"]:
            if auto_accept_notice == True:
                self.accept_maintenance_notices(user_type="agent")

        if current_agent_login_state == "SELECT_STATION":
            try:
                session = self.agent.AgentSessionStart.invoke(
                    self.stationId, self.stationType, self.stationState
                )
                current_agent_login_state = self.agent_login_state
                if auto_accept_notice == True:
                    self.accept_maintenance_notices(user_type="agent")

            except Five9DuplicateLoginError:
                logging.info("Agent already logged in, logging out, please try again.")
                self.agent.LogOut.invoke()
                return False

            logging.debug(f"AGENT SESSION STARTED Result: {session.__dict__}")

            self.agent_socket = Five9Socket(self, "agent", self.socket_app_key)
            return True

    @property
    def supervisor_login_state(self):
        """Current supervisor login state string from the Five9 API.

        Common values: ``"SELECT_STATION"``, ``"ACCEPT_NOTICE"``, ``"WORKING"``.
        """
        return self.supervisor.SupervisorLoginState.invoke()

    @property
    def agent_login_state(self):
        """Current agent login state string from the Five9 API.

        Common values: ``"SELECT_STATION"``, ``"ACCEPT_NOTICE"``, ``"WORKING"``.
        """
        return self.agent.AgentLoginState.invoke()


class Five9Socket:
    """Manages a Five9 WebSocket connection for real-time event streaming.

    Handles the full connection lifecycle: authentication headers, registering
    event handlers, sending keep-alive pings every 15 seconds, dispatching
    incoming events to the appropriate handler, and clean disconnection.

    Event handlers are subclasses of
    :class:`~five9_agent_sup_rest.methods.default_socket_handlers.SocketEventHandler`
    keyed by their ``eventId``.  Built-in handlers are registered automatically;
    additional handlers can be passed via ``custom_socket_handlers`` on
    :class:`Five9RestClient`.

    Args:
        client (Five9RestClient): The parent client instance.
        context (str): ``"agent"`` or ``"supervisor"`` — selects the correct
            WebSocket URI path.
        socket_app_key (str): Arbitrary identifier embedded in the WebSocket URI.
    """

    def __init__(self, client: Five9RestClient, context, socket_app_key):
        self.client = client
        self.socket_app_key = socket_app_key
        self.context_path = CONTEXT_PATHS[f"websocket_{context}"]
        self.uri = f"wss://{client.session_configuration.host}:{client.session_configuration.port}{self.context_path}"
        self.uri = self.uri.format(socket_app_key=self.socket_app_key)

        self.disconnect_event = asyncio.Event()
        self.disconnect_requested = False

        logging.debug(f"WebSocket URI: {self.uri}")

    def add_socket_handler(self, handler):
        """Register a custom event handler on this socket.

        The handler must be a subclass of :class:`SocketEventHandler` and have
        an ``eventId`` class attribute.  If these conditions are not met the
        handler is silently skipped.

        Args:
            handler: A :class:`SocketEventHandler` subclass (not an instance).
        """
        if (
            inspect.isclass(handler)
            and issubclass(handler, default_socket_handlers.SocketEventHandler)
            and hasattr(handler, "eventId")
        ):
            handler = handler(client=self.client)
            self.handlers[handler.eventId] = handler
            logging.debug(f"Handler Added: {handler.eventId}")

        else:
            logging.debug(f"Skipping {handler}")

    async def send_ping(self, websocket):
        while not self.disconnect_requested:
            try:
                await websocket.send("ping")
                logging.debug("Ping sent")

                # Create tasks from the coroutines
                sleep_task = asyncio.create_task(asyncio.sleep(15))
                event_task = asyncio.create_task(self.disconnect_event.wait())

                # Wait for either the sleep task to complete or the event task to be set
                done, pending = await asyncio.wait(
                    [sleep_task, event_task], return_when=asyncio.FIRST_COMPLETED
                )

                # Cancel any pending tasks to avoid them running in the background
                for task in pending:
                    task.cancel()
                    try:
                        await task
                    except asyncio.CancelledError:
                        pass

            except websockets.ConnectionClosed:
                logging.info("Connection closed, stopping ping.")
                break

    async def handle_messages(self, websocket):
        async for message in websocket:
            if self.disconnect_requested:
                logging.info(
                    "Socket Disconnect Requested by Client, stopping message handler."
                )
                break

            try:
                event = json.loads(message)
                event_id = event["context"]["eventId"]
            except (json.JSONDecodeError, KeyError, TypeError) as exc:
                logging.warning(f"Malformed WebSocket message, skipping: {exc}")
                continue

            handler = self.handlers.get(event_id, None)

            if not handler:
                logging.info(
                    f"No handler found for event {event_id}, creating generic handler."
                )
                handler = default_socket_handlers.SocketEventHandler(
                    client=self.client, eventId=event_id
                )
                self.handlers[event_id] = handler

            handled = await handler.handle(event)
            if handled == "reconnect":
                logging.info("Reconnecting socket.")
                await self.close()
                self.connect()

    async def listen_for_disconnect(self):
        # Get the event loop for the current thread,
        # and schedule the await_disconnect coroutine to run in the background
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, self._await_disconnect, loop)

    def _await_disconnect(self, loop):
        input("\nWebsocket Open, press Enter to disconnect...\n")
        self.disconnect_requested = True
        self.disconnect_event.set()  # Set the event to wake up the send_ping coroutine
        logging.info("Disconnect command received.")
        asyncio.run_coroutine_threadsafe(self.close(), loop)

    async def _connect(self):
        headers = {
            "Authorization": f"Bearer-{self.client.session_configuration.tokenId}",  # Use the token provided during initialization
            "Cookie": self.client.session_configuration.cookies_header,  # Use the cookies provided during initialization
        }

        self.handlers = {}

        for name, handler in inspect.getmembers(default_socket_handlers):
            if inspect.isclass(handler) and issubclass(
                handler, default_socket_handlers.SocketEventHandler
            ):
                self.add_socket_handler(handler)

        for handler in self.client.custom_socket_handlers:
            added = self.add_socket_handler(handler)
            logging.debug(f"Handler Added: {handler.eventId}")

        async with websockets.connect(self.uri, extra_headers=headers) as websocket:
            self.websocket = websocket
            # Run sending pings and message handler concurrently
            await asyncio.gather(
                self.send_ping(websocket),
                self.handle_messages(websocket),
                self.listen_for_disconnect(),
            )

    def connect(self):
        """Open the WebSocket connection and block until it is closed.

        Runs the async event loop synchronously.  This call blocks the calling
        thread until the user presses Enter (via the stdin disconnect listener)
        or an unrecoverable error occurs.
        """
        try:
            asyncio.run(self._connect())
        except Exception:
            logging.exception("Error in WebSocket connection.")

    async def close(self):
        """Gracefully close the WebSocket connection if it is currently open."""
        if hasattr(self, "websocket") and self.websocket and self.websocket.open:
            await self.websocket.close()
            logging.info("WebSocket closed.")
