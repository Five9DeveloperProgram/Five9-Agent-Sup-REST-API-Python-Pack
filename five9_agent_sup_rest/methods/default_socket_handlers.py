import logging

from five9_agent_sup_rest.config import CONTEXT_PATHS
from five9_agent_sup_rest import event_ids


class SocketEventHandler:
    """Base class for socket event handlers"""

    def __init__(self, *args, **kwargs):
        if not hasattr(self, "eventId"):
            self.eventId = kwargs.get("eventId", None)
        self.client = kwargs.get("client", None)

    async def handle(self, event):
        """Handles an event received from the socket"""
        logging.debug(
            f"Generic Handler EVENT: {event['context']['eventId']} - {event['context']['eventReason']}"
        )
        logging.debug(f"Payload:\n{event['payLoad']}\n")
        return



class DefaultEventHandler1010(SocketEventHandler):
    """Default handler for event 1010 - Successful Websocket Connection"""

    eventId = event_ids.SERVER_CONNECTED

    async def handle(self, event):
        logging.info(f"Default Handler EVENT: {event['context']['eventId']} - {event['context']['eventReason']}")        
        return

class DefaultEventHandler1202(SocketEventHandler):
    """Default handler for event 1202 - Pong"""

    eventId = event_ids.PONG

    async def handle(self, event):
        logging.info(f"Default Handler EVENT: {event['context']['eventId']} - {event['payLoad']}")
        return


class DefaultEventHandler70(SocketEventHandler):
    """Default handler for event 70 - Maintenance Started"""

    eventId = event_ids.EVENT_MAINTENANCE_STARTED

    async def handle(self, event):
        logging.info(f"MGR EVENT: {event['context']['eventId']} - {event['payLoad']}")
        return


class DefaultEventHandler73(SocketEventHandler):
    """Default handler for event 73 - Maintenance Completed"""

    eventId = event_ids.EVENT_MAINTENANCE_COMPLETED

    async def handle(self, event):
        logging.info(f"MGR EVENT: {event['context']['eventId']} - {event['payLoad']}")
        return


class DefaultEventHandler1000(SocketEventHandler):
    """Default handler for event 1000 - Server Unavailable

    Communication to VCC server was lost. The client should restart the session.
    """

    eventId = event_ids.SERVER_UNAVAILABLE

    async def handle(self, event):
        logging.warning(
            f"SERVER UNAVAILABLE EVENT: {event['context']['eventId']} - {event['payLoad']}"
        )
        return


class DefaultEventHandler1001(SocketEventHandler):
    """Default handler for event 1001 - Server Maintenance Switchover (Graceful)

    Domain moved to another server. The user is allowed to complete the current
    task before the domain is moved. Client should obtain new metadata and reload.
    """

    eventId = event_ids.SERVER_MAINTENANCE_SWITCHOVER_RELOGIN

    async def handle(self, event):
        logging.warning(
            f"MAINTENANCE SWITCHOVER EVENT: {event['context']['eventId']} - {event['payLoad']}"
        )
        self.client.session_configuration.update_config(event["payLoad"])
        if self.client.current_supervisor_login_state != "WORKING":
            self.client.supervisor.SessionStart.invoke()
            return "reconnect"
        return


class DefaultEventHandler1002(SocketEventHandler):
    """Default handler for event 1002 - Domain Migrated (Forced)

    The payLoad for this event contains the new metadata for the session to use.
    This event updates the session_configuration object with the new metadata, and
    then invokes the SessionStart method to reconnect the session using the new metadata.

    The return value of this handler is used to determine whether the session should
    reconnect or not. If the return value is "reconnect", the socket object which received
    the event will reconnect the session. If the return value is anything else, the socket
    will proceed as normal and the session will not reconnect.
    """

    eventId = event_ids.SERVER_MAINTENANCE_SWITCHOVER_RELOGIN_FORCED

    async def handle(self, event):
        logging.info(
            f"Default Handler EVENT: {event['context']['eventId']} - {event['context']['eventReason']} "
        )
        self.client.session_configuration.update_config(event["payLoad"])
        if self.client.current_supervisor_login_state != "WORKING":
            self.client.supervisor.SessionStart.invoke()
            return "reconnect"
        return


class DefaultEventHandler1003(SocketEventHandler):
    """Default handler for event 1003 - JMS Server Unavailable

    The server cannot receive events. Client should display a message and
    try to restart the session.
    """

    eventId = event_ids.JMS_SERVER_UNAVAILABLE

    async def handle(self, event):
        logging.warning(
            f"JMS SERVER UNAVAILABLE EVENT: {event['context']['eventId']} - {event['payLoad']}"
        )
        return


class DefaultEventHandler1020(SocketEventHandler):
    """Default handler for event 1020 - Duplicate Connection

    The server will immediately close the duplicate connection with reason
    code 3000.
    """

    eventId = event_ids.DUPLICATE_CONNECTION

    async def handle(self, event):
        logging.warning(
            f"DUPLICATE CONNECTION EVENT: {event['context']['eventId']} - "
            "Server is closing this connection."
        )
        return
