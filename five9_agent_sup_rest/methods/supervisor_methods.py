import logging

from .base import SupervisorRestMethod
from five9_agent_sup_rest.config import CONTEXT_PATHS
from five9_agent_sup_rest.exceptions import Five9DuplicateLoginError


class MaintenanceNoticesGet(SupervisorRestMethod):
    """Returns an array of maintenance notices.
    GET /supervisors/{supervisorId}/maintenance_notices

    """

    def invoke(self):
        self.method = "GET"
        self.path = f"/supervisors/{self.config.userId}/maintenance_notices"
        super().invoke()
        return self.response.json()


class MaintenanceNoticeAccept(SupervisorRestMethod):
    """ Returns an array of maintenance notices.
    PUT /supervisors/{supervisorId}/maintenance_notices/{noticeId}/accept

    """

    def invoke(self, noticeId):
        self.method = "PUT"
        self.path = f"/supervisors/{self.config.userId}/maintenance_notices/{noticeId}/accept"
        super().invoke()
        return self.response.json()


class SupervisorLoginState(SupervisorRestMethod):
    """Returns the current login state of the supervisor.
    GET /supervisors/{supervisorId}/login_state

    Common return values: ``"SELECT_STATION"``, ``"ACCEPT_NOTICE"``, ``"WORKING"``.
    """

    def invoke(self):
        self.method = "GET"
        self.path = f"/supervisors/{self.config.userId}/login_state"
        super().invoke()
        return self.response.text.strip('"')


class SupervisorSessionStart(SupervisorRestMethod):
    """Registers the station for the supervisor.
    PUT /supervisors/{supervisorId}/session_start

    The initial login state must be in SELECT_STATION state. This request
    modifies the supervisor’s login state. If successful, the request changes the
    LoginState value and sends the EVENT_STATION_UPDATED and
    EVENT_LOGIN_STATE_UPDATED events. The supervisor must have the
    CAN_RUN_WEB_AGENT permission
    """

    def invoke(self, stationId="", stationType="EMPTY", stationState="DISCONNECTED"):
        self.method = "PUT"
        self.path = f"/supervisors/{self.config.userId}/session_start"
        payload = {
            "state": stationState,
            "stationId": stationId,
            "stationType": stationType,
        }
        super().invoke(payload=payload)
        # Special handling for the supervisor session start response
        if self.response.status_code < 400:
            return self.response
        
        else:
            exception_details = self.response.json()
            if exception_details.get("five9ExceptionDetail", {}).get("context", {}).get("contextCode", "") == "DUPLICATE_LOGIN": 
                raise Five9DuplicateLoginError(f"Already Logged In: {self.response.status_code} - {self.response.json()}")
            raise Exception(f"Error: {self.response.status_code} - {self.response.text}")


class LogOut(SupervisorRestMethod):
    """Logs out the supervisor.
    PUT /auth/logout

    """

    def invoke(self):
        self.method = "POST"
        self.path = f"/auth/logout"
        super().invoke()
        return self.response

class DomainQueues(SupervisorRestMethod):
    """Returns an array of all queues in the domain.
    GET /orgs/{orgId}/skills

    """

    def invoke(self):
        self.method = "GET"
        self.path = f"/orgs/{self.config.orgId}/skills"
        super().invoke()
        return self.response.json()

class MigrateToMaintenanceHost:
    """Migrates the supervisor to the maintenance host.
    POST /supervisors/{supervisorId}/migrate

    """

    def invoke(self):
        self.method = "POST"
        self.path = f"/{self.config.userId}/migrate"
        self.qstring_params = {"migrateToMaintenanceHost": "true"}
        super().invoke()
        return self.response.json()


#### Alerts
class GetAlerts(SupervisorRestMethod):
    """Returns all configured queue alerts for the domain.
    GET /alerts
    """

    def invoke(self):
        self.method = "GET"
        self.path = "/alerts"
        super().invoke()
        return self.response.json()
    
class CreateAlert(SupervisorRestMethod):
    """Creates a new queue alert.
    POST /alerts

    Args:
        alert_data (dict): Alert configuration payload.
    """

    def invoke(self, alert_data):
        self.method = "POST"
        self.path = "/alerts"
        super().invoke(payload=alert_data)
        return self.response.json()
    
class UpdateAlert(SupervisorRestMethod):
    """Updates an existing queue alert.
    PUT /alerts/{alertId}

    Args:
        alert_id: ID of the alert to update.
        alert_data (dict): Updated alert configuration payload.
    """

    def invoke(self, alert_id, alert_data):
        self.method = "PUT"
        self.path = f"/alerts/{alert_id}"
        super().invoke(payload=alert_data)
        return self.response.json()


class DeleteAlert(SupervisorRestMethod):
    """Deletes a queue alert by ID.
    DELETE /alerts/{alertId}

    Args:
        alert_id: ID of the alert to delete.
    """

    def invoke(self, alert_id):
        self.method = "DELETE"
        self.path = f"/alerts/{alert_id}"
        super().invoke()
        return self.response.json()


class GetAlertByID(SupervisorRestMethod):
    """Returns a single queue alert by ID.
    GET /alerts/{alertId}

    Args:
        alert_id: ID of the alert to retrieve.
    """

    def invoke(self, alert_id):
        self.method = "GET"
        self.path = f"/alerts/{alert_id}"
        super().invoke()
        return self.response.json()


class GetDomainDispositions(SupervisorRestMethod):
    """Returns all call dispositions configured for the domain.
    GET /orgs/{orgId}/dispositions
    """

    def invoke(self):
        self.method = "GET"
        self.path = f"/orgs/{self.config.orgId}/dispositions"
        super().invoke()
        return self.response.json()
