import logging
import time

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

class MigrateToMaintenanceHost(SupervisorRestMethod):
    """Migrates the supervisor to the maintenance host.
    PUT /supervisors/{supervisorId}/migrate
    """

    def invoke(self):
        self.method = "PUT"
        self.path = f"/supervisors/{self.config.userId}/migrate"
        super().invoke(qstring_params={"migrateToMaintenanceHost": "true"})
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

        headers = dict(self.config.api_header)
        headers["f9-transaction-id"] = f"{self.config.app_key}_{int(time.time())}"

        req = requests.Request(
            method=self.method,
            url=url,
            headers=headers,
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
            "f9-transaction-id": f"{self.config.app_key}_{int(time.time())}",
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


#####################################################################
# Alerts (additional)
#####################################################################


class GetSupervisorAlerts(SupervisorRestMethod):
    """Gets all alerts for a supervisor.
    GET /supervisors/{supervisorId}/alerts
    """

    def invoke(self):
        self.method = "GET"
        self.path = f"/supervisors/{self.config.userId}/alerts"
        super().invoke()
        return self.response.json()


class GetSupervisorAlert(SupervisorRestMethod):
    """Gets a specific alert for a supervisor.
    GET /supervisors/{supervisorId}/alerts/{alertId}
    """

    def invoke(self, alertId):
        self.method = "GET"
        self.path = f"/supervisors/{self.config.userId}/alerts/{alertId}"
        super().invoke()
        return self.response.json()


class CreateSupervisorAlert(SupervisorRestMethod):
    """Creates an alert for a supervisor.
    POST /supervisors/{supervisorId}/alerts
    """

    def invoke(self, alert_data):
        self.method = "POST"
        self.path = f"/supervisors/{self.config.userId}/alerts"
        super().invoke(payload=alert_data)
        return self.response.json()


class UpdateSupervisorAlert(SupervisorRestMethod):
    """Updates an alert for a supervisor.
    PUT /supervisors/{supervisorId}/alerts/{alertId}
    """

    def invoke(self, alertId, alert_data):
        self.method = "PUT"
        self.path = f"/supervisors/{self.config.userId}/alerts/{alertId}"
        super().invoke(payload=alert_data)
        return self.response.json()


class DeleteSupervisorAlert(SupervisorRestMethod):
    """Deletes an alert for a supervisor.
    DELETE /supervisors/{supervisorId}/alerts/{alertId}
    """

    def invoke(self, alertId):
        self.method = "DELETE"
        self.path = f"/supervisors/{self.config.userId}/alerts/{alertId}"
        super().invoke()
        return self.response


#####################################################################
# Callbacks
#####################################################################


class GetAgentCallbacks(SupervisorRestMethod):
    """Gets the callbacks for a specific agent.
    GET /supervisors/{supervisorId}/agents/{agentId}/callbacks
    """

    def invoke(self, agentId):
        self.method = "GET"
        self.path = f"/supervisors/{self.config.userId}/agents/{agentId}/callbacks"
        super().invoke()
        return self.response.json()


class MoveCallback(SupervisorRestMethod):
    """Moves a callback from one agent to another.
    POST /supervisors/{supervisorId}/agents/{agentIdFrom}/callbacks/{callbackId}/move
    """

    def invoke(self, agentIdFrom, callbackId, move_data):
        self.method = "POST"
        self.path = f"/supervisors/{self.config.userId}/agents/{agentIdFrom}/callbacks/{callbackId}/move"
        super().invoke(payload=move_data)
        return self.response.json()


class MoveCallbacks(SupervisorRestMethod):
    """Moves multiple callbacks from one agent to another.
    POST /supervisors/{supervisorId}/agents/{agentIdFrom}/callbacks/move
    """

    def invoke(self, agentIdFrom, move_data):
        self.method = "POST"
        self.path = f"/supervisors/{self.config.userId}/agents/{agentIdFrom}/callbacks/move"
        super().invoke(payload=move_data)
        return self.response.json()


#####################################################################
# Calls and Recordings
#####################################################################


class MakeTestCall(SupervisorRestMethod):
    """Makes a test call.
    POST /supervisors/{supervisorId}/interactions/make_test_call
    """

    def invoke(self, call_data):
        self.method = "POST"
        self.path = f"/supervisors/{self.config.userId}/interactions/make_test_call"
        super().invoke(payload=call_data)
        return self.response.json()


class MakeSkillsTestCalls(SupervisorRestMethod):
    """Makes a test call to queues.
    POST /supervisors/{supervisorId}/interactions/make_skills_test_calls
    """

    def invoke(self, call_data):
        self.method = "POST"
        self.path = f"/supervisors/{self.config.userId}/interactions/make_skills_test_calls"
        super().invoke(payload=call_data)
        return self.response.json()


class MakeEchoCall(SupervisorRestMethod):
    """Makes an echo call.
    POST /supervisors/{supervisorId}/echo_call
    """

    def invoke(self):
        self.method = "POST"
        self.path = f"/supervisors/{self.config.userId}/echo_call"
        super().invoke()
        return self.response


class DeleteEchoCall(SupervisorRestMethod):
    """Deletes an echo call.
    DELETE /supervisors/{supervisorId}/echo_call
    """

    def invoke(self):
        self.method = "DELETE"
        self.path = f"/supervisors/{self.config.userId}/echo_call"
        super().invoke()
        return self.response


class CreateCallRecordingView(SupervisorRestMethod):
    """Creates a call recording view.
    POST /supervisors/{supervisorId}/agents/{agentId}/recording_views
    """

    def invoke(self, agentId, view_data):
        self.method = "POST"
        self.path = f"/supervisors/{self.config.userId}/agents/{agentId}/recording_views"
        super().invoke(payload=view_data)
        return self.response.json()


class GetCallRecordingViews(SupervisorRestMethod):
    """Gets the call recording views.
    GET /supervisors/{supervisorId}/agents/{agentId}/recording_views
    """

    def invoke(self, agentId):
        self.method = "GET"
        self.path = f"/supervisors/{self.config.userId}/agents/{agentId}/recording_views"
        super().invoke()
        return self.response.json()


class DeleteCallRecordingView(SupervisorRestMethod):
    """Deletes a call recording view.
    DELETE /supervisors/{supervisorId}/agents/{agentId}/recording_views/{viewId}
    """

    def invoke(self, agentId, viewId):
        self.method = "DELETE"
        self.path = f"/supervisors/{self.config.userId}/agents/{agentId}/recording_views/{viewId}"
        super().invoke()
        return self.response


class UpdateCallRecordingView(SupervisorRestMethod):
    """Updates a call recording view.
    PUT /supervisors/{supervisorId}/agents/{agentId}/recording_views/{viewId}
    """

    def invoke(self, agentId, viewId, view_data):
        self.method = "PUT"
        self.path = f"/supervisors/{self.config.userId}/agents/{agentId}/recording_views/{viewId}"
        super().invoke(payload=view_data)
        return self.response.json()


class IterateCallRecordingView(SupervisorRestMethod):
    """Iterates a call recording view (gets next page).
    PUT /supervisors/{supervisorId}/agents/{agentId}/recording_views/{viewId}/next
    """

    def invoke(self, agentId, viewId):
        self.method = "PUT"
        self.path = f"/supervisors/{self.config.userId}/agents/{agentId}/recording_views/{viewId}/next"
        super().invoke()
        return self.response.json()


class DownloadRecording(SupervisorRestMethod):
    """Downloads a call recording.
    PUT /supervisors/{supervisorId}/agents/{agentId}/recordings/{recordingId}/download
    """

    def invoke(self, agentId, recordingId):
        self.method = "PUT"
        self.path = f"/supervisors/{self.config.userId}/agents/{agentId}/recordings/{recordingId}/download"
        super().invoke()
        return self.response


#####################################################################
# Campaigns
#####################################################################


class GetCampaigns(SupervisorRestMethod):
    """Gets all campaigns.
    GET /orgs/{orgId}/campaigns
    """

    def invoke(self):
        self.method = "GET"
        self.path = f"/orgs/{self.config.orgId}/campaigns"
        super().invoke()
        return self.response.json()


class StartCampaign(SupervisorRestMethod):
    """Starts a campaign.
    PUT /orgs/{orgId}/campaigns/{campaignId}/start
    """

    def invoke(self, campaignId):
        self.method = "PUT"
        self.path = f"/orgs/{self.config.orgId}/campaigns/{campaignId}/start"
        super().invoke()
        return self.response


class StopCampaign(SupervisorRestMethod):
    """Stops a campaign.
    PUT /orgs/{orgId}/campaigns/{campaignId}/stop
    """

    def invoke(self, campaignId):
        self.method = "PUT"
        self.path = f"/orgs/{self.config.orgId}/campaigns/{campaignId}/stop"
        super().invoke()
        return self.response


class ResetCampaign(SupervisorRestMethod):
    """Resets a campaign.
    PUT /orgs/{orgId}/campaigns/{campaignId}/reset
    """

    def invoke(self, campaignId):
        self.method = "PUT"
        self.path = f"/orgs/{self.config.orgId}/campaigns/{campaignId}/reset"
        super().invoke()
        return self.response


class GetCampaignSystemMessage(SupervisorRestMethod):
    """Gets a campaign system message.
    GET /orgs/{orgId}/campaigns/{campaignId}/system_message
    """

    def invoke(self, campaignId):
        self.method = "GET"
        self.path = f"/orgs/{self.config.orgId}/campaigns/{campaignId}/system_message"
        super().invoke()
        return self.response.json()


class GetCampaignProfiles(SupervisorRestMethod):
    """Gets the campaign profiles.
    GET /orgs/{orgId}/campaign_profiles
    """

    def invoke(self):
        self.method = "GET"
        self.path = f"/orgs/{self.config.orgId}/campaign_profiles"
        super().invoke()
        return self.response.json()


class GetCampaignListDetails(SupervisorRestMethod):
    """Gets campaign list details.
    GET /orgs/{orgId}/campaigns/{campaignId}/lists/{listId}/details
    """

    def invoke(self, campaignId, listId):
        self.method = "GET"
        self.path = f"/orgs/{self.config.orgId}/campaigns/{campaignId}/lists/{listId}/details"
        super().invoke()
        return self.response.json()


class GetCampaignListStatistics(SupervisorRestMethod):
    """Gets the campaign list statistics.
    GET /orgs/{orgId}/campaigns/{campaignId}/lists/statistics
    """

    def invoke(self, campaignId):
        self.method = "GET"
        self.path = f"/orgs/{self.config.orgId}/campaigns/{campaignId}/lists/statistics"
        super().invoke()
        return self.response.json()


class RefreshCampaignStatistics(SupervisorRestMethod):
    """Updates the outbound campaign runtime statistics.
    PUT /orgs/{orgId}/campaigns/{campaignId}/statistics/refresh
    """

    def invoke(self, campaignId):
        self.method = "PUT"
        self.path = f"/orgs/{self.config.orgId}/campaigns/{campaignId}/statistics/refresh"
        super().invoke()
        return self.response


#####################################################################
# Domain
#####################################################################


class GetDomainTimeZones(SupervisorRestMethod):
    """Gets the time zones for the domain.
    GET /orgs/{orgId}/time_zones
    """

    def invoke(self):
        self.method = "GET"
        self.path = f"/orgs/{self.config.orgId}/time_zones"
        super().invoke()
        return self.response.json()


class GetAgentUserUid(SupervisorRestMethod):
    """Gets the user UID for an agent.
    GET /supervisors/{supervisorId}/agents/{agentId}/user_uid
    """

    def invoke(self, agentId):
        self.method = "GET"
        self.path = f"/supervisors/{self.config.userId}/agents/{agentId}/user_uid"
        super().invoke()
        return self.response.json()


class GetDomainSkills(SupervisorRestMethod):
    """Gets the queues in the domain.
    GET /orgs/{orgId}/skills
    """

    def invoke(self):
        self.method = "GET"
        self.path = f"/orgs/{self.config.orgId}/skills"
        super().invoke()
        return self.response.json()


class GetDomainTime(SupervisorRestMethod):
    """Gets the current time in the domain.
    GET /orgs/{orgId}/time
    """

    def invoke(self):
        self.method = "GET"
        self.path = f"/orgs/{self.config.orgId}/time"
        super().invoke()
        return self.response.json()


class GetDomainAgentGroups(SupervisorRestMethod):
    """Gets the agent groups in the domain.
    GET /orgs/{orgId}/agent_groups
    """

    def invoke(self):
        self.method = "GET"
        self.path = f"/orgs/{self.config.orgId}/agent_groups"
        super().invoke()
        return self.response.json()


class GetDomainUsers(SupervisorRestMethod):
    """Gets the users in the domain.
    GET /orgs/{orgId}/users
    """

    def invoke(self):
        self.method = "GET"
        self.path = f"/orgs/{self.config.orgId}/users"
        super().invoke()
        return self.response.json()


class GetReasonCodes(SupervisorRestMethod):
    """Gets the reason codes in the domain.
    GET /orgs/{orgId}/reason_codes
    """

    def invoke(self):
        self.method = "GET"
        self.path = f"/orgs/{self.config.orgId}/reason_codes"
        super().invoke()
        return self.response.json()


class GetDialingLists(SupervisorRestMethod):
    """Gets the dialing lists in the domain.
    GET /orgs/{orgId}/lists
    """

    def invoke(self):
        self.method = "GET"
        self.path = f"/orgs/{self.config.orgId}/lists"
        super().invoke()
        return self.response.json()


class LogoutUser(SupervisorRestMethod):
    """Logs out a user by session ID.
    PUT /orgs/{orgId}/user_sessions/{sessionId}/logout
    """

    def invoke(self, sessionId):
        self.method = "PUT"
        self.path = f"/orgs/{self.config.orgId}/user_sessions/{sessionId}/logout"
        super().invoke()
        return self.response


class GetDomainClusters(SupervisorRestMethod):
    """Gets the domain clusters.
    GET /orgs/{orgId}/clusters
    """

    def invoke(self):
        self.method = "GET"
        self.path = f"/orgs/{self.config.orgId}/clusters"
        super().invoke()
        return self.response.json()


class GetDomainAttributes(SupervisorRestMethod):
    """Gets the domain attributes.
    GET /orgs/{orgId}/attributes
    """

    def invoke(self):
        self.method = "GET"
        self.path = f"/orgs/{self.config.orgId}/attributes"
        super().invoke()
        return self.response.json()


#####################################################################
# Domain Users and Active User Sessions
#####################################################################


class GetUserProfiles(SupervisorRestMethod):
    """Gets the user profiles in the domain.
    GET /orgs/{orgId}/user_profiles
    """

    def invoke(self):
        self.method = "GET"
        self.path = f"/orgs/{self.config.orgId}/user_profiles"
        super().invoke()
        return self.response.json()


class GetAgentStates(SupervisorRestMethod):
    """Gets the agent states in the domain.
    GET /orgs/{orgId}/agent_states
    """

    def invoke(self):
        self.method = "GET"
        self.path = f"/orgs/{self.config.orgId}/agent_states"
        super().invoke()
        return self.response.json()


class GetUserSessions(SupervisorRestMethod):
    """Gets the active user sessions.
    GET /orgs/{orgId}/user_sessions
    """

    def invoke(self):
        self.method = "GET"
        self.path = f"/orgs/{self.config.orgId}/user_sessions"
        super().invoke()
        return self.response.json()


class UpdateAgentState(SupervisorRestMethod):
    """Updates the state of an agent.
    PUT /supervisors/{supervisorId}/agents/{agentId}/presence
    """

    def invoke(self, agentId, presence_data):
        self.method = "PUT"
        self.path = f"/supervisors/{self.config.userId}/agents/{agentId}/presence"
        super().invoke(payload=presence_data)
        return self.response


class MigrateSupervisor(SupervisorRestMethod):
    """Migrates a supervisor.
    PUT /supervisors/{supervisorId}/migrate
    """

    def invoke(self):
        self.method = "PUT"
        self.path = f"/supervisors/{self.config.userId}/migrate"
        super().invoke()
        return self.response


class GetSupervisorSwitchoverMetadata(SupervisorRestMethod):
    """Gets the maintenance state / switchover metadata of a supervisor.
    GET /supervisors/{supervisorId}/switchover_metadata
    """

    def invoke(self):
        self.method = "GET"
        self.path = f"/supervisors/{self.config.userId}/switchover_metadata"
        super().invoke()
        return self.response.json()


#####################################################################
# Messages
#####################################################################


class GetMessages(SupervisorRestMethod):
    """Gets a list of messages (shared message context).
    GET /messages/{userId}/messages
    """

    def invoke(self):
        self.method = "GET"
        self.path = f"/messages/{self.config.userId}/messages"
        super().invoke()
        return self.response.json()


class SendMessage(SupervisorRestMethod):
    """Sends a message (shared message context).
    POST /messages/{userId}/messages
    """

    def invoke(self, message_data):
        self.method = "POST"
        self.path = f"/messages/{self.config.userId}/messages"
        super().invoke(payload=message_data)
        return self.response.json()


class SendMessageWithId(SupervisorRestMethod):
    """Sends a message with an identifier (shared message context).
    POST /messages/{userId}/messages/{messageId}
    """

    def invoke(self, messageId, message_data):
        self.method = "POST"
        self.path = f"/messages/{self.config.userId}/messages/{messageId}"
        super().invoke(payload=message_data)
        return self.response.json()


class BroadcastMessage(SupervisorRestMethod):
    """Broadcasts a message to logged-in users.
    POST /users/{userId}/broadcast_messages
    """

    def invoke(self, message_data):
        self.method = "POST"
        self.path = f"/users/{self.config.userId}/broadcast_messages"
        super().invoke(payload=message_data)
        return self.response


class AcceptEmailMessage(SupervisorRestMethod):
    """Accepts an email message sent from an external source.
    POST /orgs/{orgId}/interactions/email
    """

    def invoke(self, email_data):
        self.method = "POST"
        self.path = f"/orgs/{self.config.orgId}/interactions/email"
        super().invoke(payload=email_data)
        return self.response.json()


#####################################################################
# Supervisor Messages
#####################################################################


class GetSupervisorMessages(SupervisorRestMethod):
    """Gets a list of messages for the supervisor.
    GET /supervisors/{supervisorId}/messages
    """

    def invoke(self):
        self.method = "GET"
        self.path = f"/supervisors/{self.config.userId}/messages"
        super().invoke()
        return self.response.json()


class SendSupervisorMessage(SupervisorRestMethod):
    """Sends a message as the supervisor.
    POST /supervisors/{supervisorId}/messages
    """

    def invoke(self, message_data):
        self.method = "POST"
        self.path = f"/supervisors/{self.config.userId}/messages"
        super().invoke(payload=message_data)
        return self.response.json()


class SendSupervisorMessageWithId(SupervisorRestMethod):
    """Sends a message with a message ID as the supervisor.
    POST /supervisors/{supervisorId}/messages/{messageId}
    """

    def invoke(self, messageId, message_data):
        self.method = "POST"
        self.path = f"/supervisors/{self.config.userId}/messages/{messageId}"
        super().invoke(payload=message_data)
        return self.response.json()


class GetMaintenanceNotice(SupervisorRestMethod):
    """Gets a specified maintenance notice.
    GET /supervisors/{supervisorId}/maintenance_notices/{noticeId}
    """

    def invoke(self, noticeId):
        self.method = "GET"
        self.path = f"/supervisors/{self.config.userId}/maintenance_notices/{noticeId}"
        super().invoke()
        return self.response.json()


#####################################################################
# Monitoring
#####################################################################


class MonitorAgent(SupervisorRestMethod):
    """Starts and stops agent monitoring.
    PUT /supervisors/{supervisorId}/agents/{agentId}/monitor
    """

    def invoke(self, agentId, monitor_data):
        self.method = "PUT"
        self.path = f"/supervisors/{self.config.userId}/agents/{agentId}/monitor"
        super().invoke(payload=monitor_data)
        return self.response


class GetAllAgents(SupervisorRestMethod):
    """Gets information about all agents.
    GET /supervisors/{supervisorId}/agents
    """

    def invoke(self):
        self.method = "GET"
        self.path = f"/supervisors/{self.config.userId}/agents"
        super().invoke()
        return self.response.json()


class GetAgentInfo(SupervisorRestMethod):
    """Gets information about a specific agent.
    GET /supervisors/{supervisorId}/agents/{agentId}
    """

    def invoke(self, agentId):
        self.method = "GET"
        self.path = f"/supervisors/{self.config.userId}/agents/{agentId}"
        super().invoke()
        return self.response.json()


class UpdateAgentInfo(SupervisorRestMethod):
    """Updates an agent's information.
    PUT /supervisors/{supervisorId}/agents/{agentId}
    """

    def invoke(self, agentId, agent_data):
        self.method = "PUT"
        self.path = f"/supervisors/{self.config.userId}/agents/{agentId}"
        super().invoke(payload=agent_data)
        return self.response


class GetAgentParkedCalls(SupervisorRestMethod):
    """Gets parked calls for an agent.
    GET /supervisors/{supervisorId}/agents/{agentId}/parked_calls
    """

    def invoke(self, agentId):
        self.method = "GET"
        self.path = f"/supervisors/{self.config.userId}/agents/{agentId}/parked_calls"
        super().invoke()
        return self.response.json()


class GetAgentSessionHistory(SupervisorRestMethod):
    """Gets the session history for an agent.
    GET /supervisors/{supervisorId}/agents/{agentId}/session_history
    """

    def invoke(self, agentId):
        self.method = "GET"
        self.path = f"/supervisors/{self.config.userId}/agents/{agentId}/session_history"
        super().invoke()
        return self.response.json()


class SetAgentRecordingState(SupervisorRestMethod):
    """Sets the recording state for an agent.
    PUT /supervisors/{supervisorId}/agents/{agentId}/recording_state
    """

    def invoke(self, agentId, recording_data):
        self.method = "PUT"
        self.path = f"/supervisors/{self.config.userId}/agents/{agentId}/recording_state"
        super().invoke(payload=recording_data)
        return self.response


class SetAgentVoicemailState(SupervisorRestMethod):
    """Sets the voicemail state for an agent.
    PUT /supervisors/{supervisorId}/agents/{agentId}/voicemail_state
    """

    def invoke(self, agentId, voicemail_data):
        self.method = "PUT"
        self.path = f"/supervisors/{self.config.userId}/agents/{agentId}/voicemail_state"
        super().invoke(payload=voicemail_data)
        return self.response


class SetMonitoredCampaigns(SupervisorRestMethod):
    """Sets the monitored campaigns.
    PUT /supervisors/{supervisorId}/monitor/campaigns
    """

    def invoke(self, campaign_data):
        self.method = "PUT"
        self.path = f"/supervisors/{self.config.userId}/monitor/campaigns"
        super().invoke(payload=campaign_data)
        return self.response


class GetMonitoredCampaigns(SupervisorRestMethod):
    """Gets the monitored campaigns.
    GET /supervisors/{supervisorId}/monitor/campaigns
    """

    def invoke(self):
        self.method = "GET"
        self.path = f"/supervisors/{self.config.userId}/monitor/campaigns"
        super().invoke()
        return self.response.json()


class GetSupervisorLocales(SupervisorRestMethod):
    """Gets the user locales for the supervisor.
    GET /supervisors/{supervisorId}/locales
    """

    def invoke(self):
        self.method = "GET"
        self.path = f"/supervisors/{self.config.userId}/locales"
        super().invoke()
        return self.response.json()


class GetLocaleDomainObjects(SupervisorRestMethod):
    """Gets locale-specific domain objects.
    GET /supervisors/{supervisorId}/locales/{localeId}/domain_objects
    """

    def invoke(self, localeId):
        self.method = "GET"
        self.path = f"/supervisors/{self.config.userId}/locales/{localeId}/domain_objects"
        super().invoke()
        return self.response.json()


class GetSupervisorSkills(SupervisorRestMethod):
    """Gets the supervisor's queues (skills).
    GET /supervisors/{supervisorId}/skills
    """

    def invoke(self):
        self.method = "GET"
        self.path = f"/supervisors/{self.config.userId}/skills"
        super().invoke()
        return self.response.json()


class GetSupervisorAgentGroups(SupervisorRestMethod):
    """Gets the supervisor's agent groups.
    GET /supervisors/{supervisorId}/agent_groups
    """

    def invoke(self):
        self.method = "GET"
        self.path = f"/supervisors/{self.config.userId}/agent_groups"
        super().invoke()
        return self.response.json()


class SetAgentActiveSkills(SupervisorRestMethod):
    """Sets the active skills for an agent.
    PUT /supervisors/{supervisorId}/agents/{agentId}/active_skills
    """

    def invoke(self, agentId, skills_data):
        self.method = "PUT"
        self.path = f"/supervisors/{self.config.userId}/agents/{agentId}/active_skills"
        super().invoke(payload=skills_data)
        return self.response


#####################################################################
# Statistics
#####################################################################


class GetStatsFilterSettings(SupervisorRestMethod):
    """Gets the statistics filter settings.
    GET /supervisors/{supervisorId}/stats_filter_settings
    """

    def invoke(self):
        self.method = "GET"
        self.path = f"/supervisors/{self.config.userId}/stats_filter_settings"
        super().invoke()
        return self.response.json()


class SetStatsFilterSettings(SupervisorRestMethod):
    """Sets the statistics filter settings.
    PUT /supervisors/{supervisorId}/stats_filter_settings
    """

    def invoke(self, filter_data):
        self.method = "PUT"
        self.path = f"/supervisors/{self.config.userId}/stats_filter_settings"
        super().invoke(payload=filter_data)
        return self.response


class GetStatsMetadata(SupervisorRestMethod):
    """Gets the statistics metadata.
    GET /supervisors/{supervisorId}/stats_metadata
    """

    def invoke(self):
        self.method = "GET"
        self.path = f"/supervisors/{self.config.userId}/stats_metadata"
        super().invoke()
        return self.response.json()


class GetStatsMetadataByType(SupervisorRestMethod):
    """Gets the statistics metadata for a specific type.
    GET /supervisors/{supervisorId}/stats_metadata/{statisticType}
    """

    def invoke(self, statisticType):
        self.method = "GET"
        self.path = f"/supervisors/{self.config.userId}/stats_metadata/{statisticType}"
        super().invoke()
        return self.response.json()


class GetCustomerPortal(SupervisorRestMethod):
    """Gets the customer portal information.
    GET /supervisors/{supervisorId}/customer_portal
    """

    def invoke(self):
        self.method = "GET"
        self.path = f"/supervisors/{self.config.userId}/customer_portal"
        super().invoke()
        return self.response.json()


class GetAcdSnapshot(SupervisorRestMethod):
    """Gets a snapshot of the ACD for a skill.
    GET /supervisors/{supervisorId}/skills/{skillId}/snapshot
    """

    def invoke(self, skillId):
        self.method = "GET"
        self.path = f"/supervisors/{self.config.userId}/skills/{skillId}/snapshot"
        super().invoke()
        return self.response.json()


class GetAgentAuxiliaryStats(SupervisorRestMethod):
    """Gets the auxiliary statistics of an agent.
    GET /supervisors/{supervisorId}/agents/{agentId}/auxiliary_stats
    """

    def invoke(self, agentId):
        self.method = "GET"
        self.path = f"/supervisors/{self.config.userId}/agents/{agentId}/auxiliary_stats"
        super().invoke()
        return self.response.json()


#####################################################################
# Supervisor Sessions (additional)
#####################################################################


class SupervisorSessionStop(SupervisorRestMethod):
    """Stops the supervisor's session.
    PUT /supervisors/{supervisorId}/session_stop
    """

    def invoke(self):
        self.method = "PUT"
        self.path = f"/supervisors/{self.config.userId}/session_stop"
        super().invoke()
        return self.response


class SupervisorSessionRestart(SupervisorRestMethod):
    """Restarts the supervisor's session.
    PUT /supervisors/{supervisorId}/session_restart
    """

    def invoke(self):
        self.method = "PUT"
        self.path = f"/supervisors/{self.config.userId}/session_restart"
        super().invoke()
        return self.response


class SetClientTimezone(SupervisorRestMethod):
    """Sets the time zone for the supervisor.
    PUT /supervisors/{supervisorId}/client_timezone
    """

    def invoke(self, timezone_data):
        self.method = "PUT"
        self.path = f"/supervisors/{self.config.userId}/client_timezone"
        super().invoke(payload=timezone_data)
        return self.response


class RequestFullStatistics(SupervisorRestMethod):
    """Requests full statistics via WebSocket event.
    PUT /supervisors/{supervisorId}/request_full_statistics
    """

    def invoke(self):
        self.method = "PUT"
        self.path = f"/supervisors/{self.config.userId}/request_full_statistics"
        super().invoke()
        return self.response


class SupervisorPing(SupervisorRestMethod):
    """Indicates whether the supervisor is active (keep-alive).
    PUT /supervisors/{supervisorId}/ping
    """

    def invoke(self):
        self.method = "PUT"
        self.path = f"/supervisors/{self.config.userId}/ping"
        super().invoke()
        return self.response


class GetSupervisorStation(SupervisorRestMethod):
    """Gets the supervisor's station.
    GET /supervisors/{supervisorId}/station
    """

    def invoke(self):
        self.method = "GET"
        self.path = f"/supervisors/{self.config.userId}/station"
        super().invoke()
        return self.response.json()


class GetSupervisorStationState(SupervisorRestMethod):
    """Gets the supervisor's station state.
    GET /supervisors/{supervisorId}/station_state
    """

    def invoke(self):
        self.method = "GET"
        self.path = f"/supervisors/{self.config.userId}/station_state"
        super().invoke()
        return self.response.json()


class RestartSupervisorStation(SupervisorRestMethod):
    """Restarts the supervisor's station.
    PUT /supervisors/{supervisorId}/station/restart
    """

    def invoke(self):
        self.method = "PUT"
        self.path = f"/supervisors/{self.config.userId}/station/restart"
        super().invoke()
        return self.response


class GetSupervisorSoftphoneConfig(SupervisorRestMethod):
    """Gets the supervisor's softphone configuration.
    GET /supervisors/{supervisorId}/softphone_config
    """

    def invoke(self):
        self.method = "GET"
        self.path = f"/supervisors/{self.config.userId}/softphone_config"
        super().invoke()
        return self.response.json()


class ForceRestartSupervisorSoftphone(SupervisorRestMethod):
    """Forces the supervisor's softphone to restart.
    PUT /supervisors/{supervisorId}/station/softphone_force_restart
    """

    def invoke(self):
        self.method = "PUT"
        self.path = f"/supervisors/{self.config.userId}/station/softphone_force_restart"
        super().invoke()
        return self.response


#####################################################################
# Voicemails
#####################################################################


class CreateAgentVoicemailView(SupervisorRestMethod):
    """Creates a voicemail view for an agent.
    POST /supervisors/{supervisorId}/agents/{agentId}/voicemail_views
    """

    def invoke(self, agentId, view_data):
        self.method = "POST"
        self.path = f"/supervisors/{self.config.userId}/agents/{agentId}/voicemail_views"
        super().invoke(payload=view_data)
        return self.response.json()


class CreateSkillVoicemailView(SupervisorRestMethod):
    """Creates a voicemail view for a skill.
    POST /supervisors/{supervisorId}/skills/{skillId}/voicemail_views
    """

    def invoke(self, skillId, view_data):
        self.method = "POST"
        self.path = f"/supervisors/{self.config.userId}/skills/{skillId}/voicemail_views"
        super().invoke(payload=view_data)
        return self.response.json()


class GetAgentVoicemailViews(SupervisorRestMethod):
    """Gets voicemail views for an agent.
    GET /supervisors/{supervisorId}/agents/{agentId}/voicemail_views
    """

    def invoke(self, agentId):
        self.method = "GET"
        self.path = f"/supervisors/{self.config.userId}/agents/{agentId}/voicemail_views"
        super().invoke()
        return self.response.json()


class GetSkillVoicemailViews(SupervisorRestMethod):
    """Gets voicemail views for a skill.
    GET /supervisors/{supervisorId}/skills/{skillId}/voicemail_views
    """

    def invoke(self, skillId):
        self.method = "GET"
        self.path = f"/supervisors/{self.config.userId}/skills/{skillId}/voicemail_views"
        super().invoke()
        return self.response.json()


class DeleteAgentVoicemailView(SupervisorRestMethod):
    """Deletes a voicemail view for an agent.
    DELETE /supervisors/{supervisorId}/agents/{agentId}/voicemail_views/{viewId}
    """

    def invoke(self, agentId, viewId):
        self.method = "DELETE"
        self.path = f"/supervisors/{self.config.userId}/agents/{agentId}/voicemail_views/{viewId}"
        super().invoke()
        return self.response


class UpdateAgentVoicemailView(SupervisorRestMethod):
    """Updates a voicemail view for an agent.
    PUT /supervisors/{supervisorId}/agents/{agentId}/voicemail_views/{viewId}
    """

    def invoke(self, agentId, viewId, view_data):
        self.method = "PUT"
        self.path = f"/supervisors/{self.config.userId}/agents/{agentId}/voicemail_views/{viewId}"
        super().invoke(payload=view_data)
        return self.response.json()


class UpdateSkillVoicemailView(SupervisorRestMethod):
    """Updates a voicemail view for a skill.
    PUT /supervisors/{supervisorId}/skills/{skillId}/voicemail_views/{viewId}
    """

    def invoke(self, skillId, viewId, view_data):
        self.method = "PUT"
        self.path = f"/supervisors/{self.config.userId}/skills/{skillId}/voicemail_views/{viewId}"
        super().invoke(payload=view_data)
        return self.response.json()


class IterateAgentVoicemailView(SupervisorRestMethod):
    """Iterates a voicemail view for an agent (gets next page).
    PUT /supervisors/{supervisorId}/agents/{agentId}/voicemail_views/{viewId}/next
    """

    def invoke(self, agentId, viewId):
        self.method = "PUT"
        self.path = f"/supervisors/{self.config.userId}/agents/{agentId}/voicemail_views/{viewId}/next"
        super().invoke()
        return self.response.json()


class IterateSkillVoicemailView(SupervisorRestMethod):
    """Iterates a voicemail view for a skill (gets next page).
    PUT /supervisors/{supervisorId}/skills/{skillId}/voicemail_views/{viewId}/next
    """

    def invoke(self, skillId, viewId):
        self.method = "PUT"
        self.path = f"/supervisors/{self.config.userId}/skills/{skillId}/voicemail_views/{viewId}/next"
        super().invoke()
        return self.response.json()


class TransferAgentVoicemail(SupervisorRestMethod):
    """Transfers a voicemail for an agent.
    PUT /supervisors/{supervisorId}/agents/{agentId}/voicemails/{voicemailId}/transfer
    """

    def invoke(self, agentId, voicemailId, transfer_data):
        self.method = "PUT"
        self.path = f"/supervisors/{self.config.userId}/agents/{agentId}/voicemails/{voicemailId}/transfer"
        super().invoke(payload=transfer_data)
        return self.response


class TransferSkillVoicemail(SupervisorRestMethod):
    """Transfers a voicemail for a skill.
    PUT /supervisors/{supervisorId}/skills/{skillId}/voicemails/{voicemailId}/transfer
    """

    def invoke(self, skillId, voicemailId, transfer_data):
        self.method = "PUT"
        self.path = f"/supervisors/{self.config.userId}/skills/{skillId}/voicemails/{voicemailId}/transfer"
        super().invoke(payload=transfer_data)
        return self.response


class RejectSkillVoicemail(SupervisorRestMethod):
    """Rejects a skill voicemail.
    PUT /supervisors/{supervisorId}/skills/{skillId}/voicemails/{voicemailId}/reject
    """

    def invoke(self, skillId, voicemailId):
        self.method = "PUT"
        self.path = f"/supervisors/{self.config.userId}/skills/{skillId}/voicemails/{voicemailId}/reject"
        super().invoke()
        return self.response


class AcceptAgentVoicemail(SupervisorRestMethod):
    """Accepts a voicemail for an agent.
    PUT /supervisors/{supervisorId}/agents/{agentId}/voicemails/{voicemailId}/accept
    """

    def invoke(self, agentId, voicemailId):
        self.method = "PUT"
        self.path = f"/supervisors/{self.config.userId}/agents/{agentId}/voicemails/{voicemailId}/accept"
        super().invoke()
        return self.response


class GetSkillVoicemailRecording(SupervisorRestMethod):
    """Gets a voicemail recording for a skill.
    GET /skills/{skillId}/voicemails/{voicemailId}/recordings/{recordingId}
    """

    def invoke(self, skillId, voicemailId, recordingId):
        self.method = "GET"
        self.path = f"/skills/{skillId}/voicemails/{voicemailId}/recordings/{recordingId}"
        super().invoke()
        return self.response


#####################################################################
# Interaction Subscriptions
#####################################################################


class SubscribeInteraction(SupervisorRestMethod):
    """Subscribes to a specific interaction.
    PUT /supervisors/{supervisorId}/interactions/{interactionId}/subscribe
    """

    def invoke(self, interactionId):
        self.method = "PUT"
        self.path = f"/supervisors/{self.config.userId}/interactions/{interactionId}/subscribe"
        super().invoke()
        return self.response


class SubscribeInteractions(SupervisorRestMethod):
    """Subscribes to multiple interactions.
    PUT /supervisors/{supervisorId}/interactions/subscribe
    """

    def invoke(self, subscribe_data):
        self.method = "PUT"
        self.path = f"/supervisors/{self.config.userId}/interactions/subscribe"
        super().invoke(payload=subscribe_data)
        return self.response


class UnsubscribeInteraction(SupervisorRestMethod):
    """Unsubscribes from a specific interaction.
    PUT /supervisors/{supervisorId}/interactions/{interactionId}/unsubscribe
    """

    def invoke(self, interactionId):
        self.method = "PUT"
        self.path = f"/supervisors/{self.config.userId}/interactions/{interactionId}/unsubscribe"
        super().invoke()
        return self.response


class UnsubscribeSubscription(SupervisorRestMethod):
    """Unsubscribes from interactions by subscription ID.
    PUT /supervisors/{supervisorId}/interactions/unsubscribe/{subscriptionId}
    """

    def invoke(self, subscriptionId):
        self.method = "PUT"
        self.path = f"/supervisors/{self.config.userId}/interactions/unsubscribe/{subscriptionId}"
        super().invoke()
        return self.response


class SubscribeSkill(SupervisorRestMethod):
    """Subscribes to a skill's interactions.
    PUT /supervisors/{supervisorId}/interactions/skills/{skillId}/subscribe
    """

    def invoke(self, skillId):
        self.method = "PUT"
        self.path = f"/supervisors/{self.config.userId}/interactions/skills/{skillId}/subscribe"
        super().invoke()
        return self.response


class UnsubscribeSkill(SupervisorRestMethod):
    """Unsubscribes from a skill's interactions.
    PUT /supervisors/{supervisorId}/interactions/skills/{skillId}/unsubscribe
    """

    def invoke(self, skillId):
        self.method = "PUT"
        self.path = f"/supervisors/{self.config.userId}/interactions/skills/{skillId}/unsubscribe"
        super().invoke()
        return self.response


#####################################################################
# Transfers
#####################################################################


class GetTransferableAgents(SupervisorRestMethod):
    """Gets agents available for receiving transfers.
    GET /supervisors/{supervisorId}/transferable_agents
    """

    def invoke(self):
        self.method = "GET"
        self.path = f"/supervisors/{self.config.userId}/transferable_agents"
        super().invoke()
        return self.response.json()


class GetEmailTransferableSkills(SupervisorRestMethod):
    """Gets skills that can accept email transfers.
    GET /supervisors/{supervisorId}/email_transferable_skills
    """

    def invoke(self):
        self.method = "GET"
        self.path = f"/supervisors/{self.config.userId}/email_transferable_skills"
        super().invoke()
        return self.response.json()


class TransferInteractionToGroup(SupervisorRestMethod):
    """Transfers an interaction to a group.
    PUT /supervisors/{supervisorId}/interactions/{interactionId}/transfer_to_group
    """

    def invoke(self, interactionId, transfer_data):
        self.method = "PUT"
        self.path = f"/supervisors/{self.config.userId}/interactions/{interactionId}/transfer_to_group"
        super().invoke(payload=transfer_data)
        return self.response


class TransferInteractionsToGroup(SupervisorRestMethod):
    """Transfers multiple interactions to a group.
    PUT /supervisors/{supervisorId}/interactions/transfer_to_group
    """

    def invoke(self, transfer_data):
        self.method = "PUT"
        self.path = f"/supervisors/{self.config.userId}/interactions/transfer_to_group"
        super().invoke(payload=transfer_data)
        return self.response


class TransferInteractionToAgent(SupervisorRestMethod):
    """Transfers an interaction to an agent.
    PUT /supervisors/{supervisorId}/interactions/{interactionId}/transfer_to_agent
    """

    def invoke(self, interactionId, transfer_data):
        self.method = "PUT"
        self.path = f"/supervisors/{self.config.userId}/interactions/{interactionId}/transfer_to_agent"
        super().invoke(payload=transfer_data)
        return self.response


class TransferInteractionsToAgent(SupervisorRestMethod):
    """Transfers multiple interactions to an agent.
    PUT /supervisors/{supervisorId}/interactions/transfer_to_agent
    """

    def invoke(self, transfer_data):
        self.method = "PUT"
        self.path = f"/supervisors/{self.config.userId}/interactions/transfer_to_agent"
        super().invoke(payload=transfer_data)
        return self.response
