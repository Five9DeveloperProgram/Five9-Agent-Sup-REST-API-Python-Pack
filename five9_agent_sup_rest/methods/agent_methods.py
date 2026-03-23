import logging

from .base import AgentRestMethod
from five9_agent_sup_rest.config import CONTEXT_PATHS
from five9_agent_sup_rest.exceptions import Five9DuplicateLoginError

#####################################################################
# Agent and Agent REST API Session Start Methods
#####################################################################


class MaintenanceNoticesGet(AgentRestMethod):
    """Returns an array of maintenance notices.
    GET /agents/{agentId}/maintenance_notices

    """

    def invoke(self):
        self.method = "GET"
        self.path = f"/agents/{self.config.userId}/maintenance_notices"
        super().invoke()
        return self.response.json()


class MaintenanceNoticeAccept(AgentRestMethod):
    """ Returns an array of maintenance notices.
    PUT /agents/{agentId}/maintenance_notices/{noticeId}/accept

    """
    def invoke(self, noticeId):
        self.method = "PUT"
        self.path = f"/agents/{self.config.userId}/maintenance_notices/{noticeId}/accept"
        super().invoke()
        return self.response.json()
    

class AgentLoginState(AgentRestMethod):
    """Returns the current login state of the agent.
    GET /agents/{agentId}/login_state

    Common return values: ``"SELECT_STATION"``, ``"ACCEPT_NOTICE"``, ``"WORKING"``.
    """

    method_name = "Agent:AgentLoginState"

    def invoke(self):
        self.method = "GET"
        self.path = f"/agents/{self.config.userId}/login_state"
        super().invoke()
        return self.response.text.strip('"')


class AgentSessionStart(AgentRestMethod):
    """Registers the station for the agent.
    PUT /agents/{agentId}/session_start

    The initial login state must be in SELECT_STATION state. This request
    modifies the agent’s login state. If successful, the request changes the
    LoginState value and sends the EVENT_STATION_UPDATED and
    EVENT_LOGIN_STATE_UPDATED events. The agent must have the
    CAN_RUN_WEB_AGENT permission
    """

    def invoke(self, stationId="", stationType="EMPTY", stationState="DISCONNECTED"):
        self.method = "PUT"
        self.path = f"/agents/{self.config.userId}/session_start"
        payload = {
            "state": stationState,
            "stationId": stationId,
            "stationType": stationType,
        }
        super().invoke(payload=payload)
        if self.response.status_code < 400:
            return self.response
        
        else:
            exception_details = self.response.json()
            if exception_details.get("five9ExceptionDetail", {}).get("context", {}).get("contextCode", "") == "DUPLICATE_LOGIN": 
                raise Five9DuplicateLoginError(f"Already Logged In: {self.response.status_code} - {self.response.json()}")
            raise Exception(f"Error: {self.response.status_code} - {self.response.text}")
                
class LogOut(AgentRestMethod):
    """Logs out the agent.
    PUT /auth/logout

    """

    def invoke(self):
        self.method = "POST"
        self.path = f"/auth/logout"
        super().invoke()
        if self.response.status_code < 400:
            return
        
        else:
            raise Exception(f"Error: {self.response.status_code} - {self.response.text}")        
