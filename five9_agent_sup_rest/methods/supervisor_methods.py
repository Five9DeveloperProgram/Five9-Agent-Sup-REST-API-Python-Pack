import logging

import requests

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


class GetPermissions(SupervisorRestMethod):
    """Returns the permissions for the current user.
    GET /users/{userId}/permissions

    This is a mandatory call that populates cloud permissions for the session.
    """

    def invoke(self):
        self.method = "GET"
        self.path = f"/users/{self.config.userId}/permissions"
        super().invoke()
        return self.response.json()


class ExchangeFdmToken(SupervisorRestMethod):
    """Exchanges the VCC session token for a cloud JWT.
    POST {cloudTokenUrl}/cloudauthsvcs/v1/domains/{orgId}/exchangefdmtoken

    The returned access_token is a JWT suitable for cloud API endpoints
    (e.g. ACL service). Stores the token on the config as ``cloud_access_token``.
    """

    def invoke(self):
        self.method = "POST"
        url = f"{self.config.cloudClientUrl}/cloudauthsvcs/v1/domains/{self.config.orgId}/exchangefdmtoken"

        req = requests.Request(
            method=self.method,
            url=url,
            headers=self.config.api_header,
        )
        prepared_request = req.prepare()

        logging.debug(
            f"FiveNineRestMethod Prepared Request:\n{prepared_request.__dict__}"
        )

        try:
            self.response = requests.Session().send(prepared_request)
            logging.info(f"{self.method_name} - RESPONSE: {self.response.status_code}")
            logging.debug(f"{self.method_name} -    TEXT: {self.response.text}")
        except requests.exceptions.RequestException as err:
            logging.error(f"{self.method_name} - Error: {err}")

        result = self.response.json()
        if "access_token" in result:
            self.config.cloud_access_token = result["access_token"]
            logging.debug("Cloud access token stored on session config")
        return result


class GetCloudUiPermissions(SupervisorRestMethod):
    """Returns cloud UI permissions from the ACL service.
    GET {cloudClientUrl}/acl/v1/domains/{orgId}/my-ui-permissions

    Uses the cloudClientUrl from the login metadata rather than the
    standard API base URL. Requires a cloud JWT obtained via ExchangeFdmToken.
    """

    def invoke(self):
        self.method = "GET"
        url = f"{self.config.cloudClientUrl}/acl/v1/domains/{self.config.orgId}/my-ui-permissions"

        cloud_headers = {
            "Authorization": f"Bearer {self.config.cloud_access_token}",
            "Accept": "application/json",
        }

        req = requests.Request(
            method=self.method,
            url=url,
            headers=cloud_headers,
        )
        prepared_request = req.prepare()

        logging.debug(
            f"FiveNineRestMethod Prepared Request:\n{prepared_request.__dict__}"
        )

        try:
            self.response = requests.Session().send(prepared_request)
            logging.info(f"{self.method_name} - RESPONSE: {self.response.status_code}")
            logging.debug(f"{self.method_name} -    TEXT: {self.response.text}")
        except requests.exceptions.RequestException as err:
            logging.error(f"{self.method_name} - Error: {err}")

        return self.response.json()


class GetApplicationSeats(SupervisorRestMethod):
    """Returns application seat information for the org.
    GET /orgs/{orgId}/application_seats

    Requires Supervisor role with CAN_VIEW_ACTIVE_SESSIONS permission
    (cloud permission: agentsession.active-sessions.view).
    Must call GetPermissions first to populate cloud permissions.
    """

    def invoke(self):
        self.method = "GET"
        self.path = f"/orgs/{self.config.orgId}/application_seats"
        super().invoke()
        return self.response.json()
