import logging
from typing import Dict, Any

import requests

from five9_agent_sup_rest.config import CONTEXT_PATHS


class FiveNineRestMethod:
    """Base class for all Five9 REST API methods.

    Subclasses must define:
      - ``method``  — HTTP verb (``"GET"``, ``"POST"``, ``"PUT"``, ``"DELETE"``).
      - ``path``    — URL path segment appended after the context path.

    The ``context_path`` class attribute is set by :class:`SupervisorRestMethod`
    or :class:`AgentRestMethod` and selects the correct API service root.
    """

    def __init__(self, config, *args, **kwargs):
        self.call_count = 0
        self.update_config(config)

    def update_config(self, config):
        """Store the session config and (re-)register this instance as an observer.

        Called once at construction time and again by
        `Five9RestClientSessionConfig.notify_observers` whenever the session is
        re-authenticated. Re-registering on each call is intentional: if the
        config object itself is ever replaced, this method ensures the instance
        stays subscribed to the new one.
        """
        self.config = config
        config.subscribe_observer(self)

    def invoke(self, *args, **kwargs):
        """Build and send the HTTP request for this method.

        Constructs the full URL from the session config's ``base_api_url``,
        the class-level ``context_path``, and the instance ``path``.  Auth
        headers are pulled from the session config automatically.

        Keyword Args:
            payload (dict, optional): JSON body for non-GET requests.
            qstring_params (dict, optional): Query-string parameters.

        Returns:
            requests.Response: The raw response object. Callers should check
            ``response.status_code`` or call ``.json()`` / ``.text`` as needed.
        """
        url = f"{self.config.base_api_url}{self.context_path}{self.path}"
        qstring_params = kwargs.get("qstring_params", None)
        payload = kwargs.get("payload", None)

        req = requests.Request(
            method=self.method,
            url=url,
            headers=self.config.api_header,
        )

        if self.method != "GET" and payload:
            req.json = payload
        if qstring_params:
            req.params = qstring_params

        prepared_request = req.prepare()

        logging.debug(
            f"FiveNineRestMethod Prepared Request:\n{prepared_request.__dict__}"
        )

        try:
            self.response = requests.Session().send(prepared_request)
            # self.response.raise_for_status()
            logging.info(f"{self.method_name} - RESPONSE: {self.response.status_code}")
            logging.debug(f"{self.method_name} -    TEXT: {self.response.text}")

        except requests.exceptions.HTTPError as errh:
            logging.error(f"{self.method_name} - HTTP Error: {errh}")
        except requests.exceptions.ConnectionError as errc:
            logging.error(f"{self.method_name} - Error Connecting: {errc}")
        except requests.exceptions.Timeout as errt:
            logging.error(f"{self.method_name} - Timeout Error: {errt}")
        except requests.exceptions.RequestException as err:
            logging.error(f"{self.method_name} - Unexpected Error: {err}")
        
        return self.response


class SupervisorRestMethod(FiveNineRestMethod):
    """Base class for all Five9 Supervisor REST methods."""

    context_path = CONTEXT_PATHS["sup_rest"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    def method_name(self):
        return f"Supervisor:{self.__class__.__name__}" 

class AgentRestMethod(FiveNineRestMethod):
    """Base class for all Five9 Agent REST methods."""

    context_path = CONTEXT_PATHS["agent_rest"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    def method_name(self):
        return f"Agent:{self.__class__.__name__}" 
    