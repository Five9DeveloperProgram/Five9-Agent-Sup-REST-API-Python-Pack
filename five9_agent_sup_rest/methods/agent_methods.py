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
                
class AuthPermissions(AgentRestMethod):
    """Returns permissions for the current authenticated user.
    GET /auth/permissions

    This is an alternate permissions endpoint under the appsvcs context path.
    """

    def invoke(self):
        self.method = "GET"
        self.path = "/auth/permissions"
        super().invoke()
        return self.response.json()


class LogOut(AgentRestMethod):
    """Logs out the agent.
    POST /auth/logout
    """

    def invoke(self):
        self.method = "POST"
        self.path = f"/auth/logout"
        super().invoke()
        if self.response.status_code < 400:
            return
        else:
            raise Exception(f"Error: {self.response.status_code} - {self.response.text}")


#####################################################################
# Agent Settings
#####################################################################


class SetSystemNotReadyState(AgentRestMethod):
    """Sets the agent's state to System Not Ready.
    PUT /agents/{agentId}/set_system_not_ready_state
    """

    def invoke(self):
        self.method = "PUT"
        self.path = f"/agents/{self.config.userId}/set_system_not_ready_state"
        super().invoke()
        return self.response


class GetLoggedInUsers(AgentRestMethod):
    """Gets the logged-in users.
    GET /users/{userId}/logged_in_users
    """

    def invoke(self):
        self.method = "GET"
        self.path = f"/users/{self.config.userId}/logged_in_users"
        super().invoke()
        return self.response.json()


class UpdateAgentTextSettings(AgentRestMethod):
    """Updates the agent's settings for text interactions.
    PUT /agents/{agentId}/settings
    """

    def invoke(self, settings_data):
        self.method = "PUT"
        self.path = f"/agents/{self.config.userId}/settings"
        super().invoke(payload=settings_data)
        return self.response


class GetAgentSettings(AgentRestMethod):
    """Gets the agent's settings.
    GET /agents/{agentId}/settings
    """

    def invoke(self):
        self.method = "GET"
        self.path = f"/agents/{self.config.userId}/settings"
        super().invoke()
        return self.response.json()


class GetDomainUsers(AgentRestMethod):
    """Gets all domain users with a specific role.
    GET /orgs/{orgId}/users
    """

    def invoke(self, **kwargs):
        self.method = "GET"
        self.path = f"/orgs/{self.config.orgId}/users"
        super().invoke(qstring_params=kwargs if kwargs else None)
        return self.response.json()


class GetAgent(AgentRestMethod):
    """Gets information about the agent.
    GET /agents/{agentId}
    """

    def invoke(self):
        self.method = "GET"
        self.path = f"/agents/{self.config.userId}"
        super().invoke()
        return self.response.json()


class GetAgentGroups(AgentRestMethod):
    """Gets all agent groups.
    GET /agents/{agentId}/agent_groups
    """

    def invoke(self):
        self.method = "GET"
        self.path = f"/agents/{self.config.userId}/agent_groups"
        super().invoke()
        return self.response.json()


class GetAgentOptions(AgentRestMethod):
    """Gets all options for the agent.
    GET /agents/{agentId}/options
    """

    def invoke(self):
        self.method = "GET"
        self.path = f"/agents/{self.config.userId}/options"
        super().invoke()
        return self.response.json()


class UpdateUserUiOptions(AgentRestMethod):
    """Updates the user's UI options.
    PUT /users/{userId}/ui_options
    """

    def invoke(self, options_data):
        self.method = "PUT"
        self.path = f"/users/{self.config.userId}/ui_options"
        super().invoke(payload=options_data)
        return self.response.json()


class UpdateAgentOptions(AgentRestMethod):
    """Updates the agent's options.
    PUT /agents/{agentId}/options
    """

    def invoke(self, options_data):
        self.method = "PUT"
        self.path = f"/agents/{self.config.userId}/options"
        super().invoke(payload=options_data)
        return self.response.json()


class GetAgentPermissions(AgentRestMethod):
    """Gets the agent's permissions.
    GET /agents/{agentId}/permissions
    """

    def invoke(self):
        self.method = "GET"
        self.path = f"/agents/{self.config.userId}/permissions"
        super().invoke()
        return self.response.json()


class GetUserPermissions(AgentRestMethod):
    """Gets the user's permissions.
    GET /users/{userId}/permissions
    """

    def invoke(self):
        self.method = "GET"
        self.path = f"/users/{self.config.userId}/permissions"
        super().invoke()
        return self.response.json()


class GetUserRoles(AgentRestMethod):
    """Gets the user's roles.
    GET /users/{userId}/roles
    """

    def invoke(self):
        self.method = "GET"
        self.path = f"/users/{self.config.userId}/roles"
        super().invoke()
        return self.response.json()


class GetCustomerPortal(AgentRestMethod):
    """Gets customer portal information.
    GET /agents/{agentId}/customer_portal
    """

    def invoke(self):
        self.method = "GET"
        self.path = f"/agents/{self.config.userId}/customer_portal"
        super().invoke()
        return self.response.json()


class PostThirdPartyConfig(AgentRestMethod):
    """Posts third-party configuration.
    POST /agents/{agentId}/third_party_config
    """

    def invoke(self, config_data):
        self.method = "POST"
        self.path = f"/agents/{self.config.userId}/third_party_config"
        super().invoke(payload=config_data)
        return self.response.json()


class ChangePassword(AgentRestMethod):
    """Changes the agent's password.
    PUT /agents/{agentId}/password
    """

    def invoke(self, password_data):
        self.method = "PUT"
        self.path = f"/agents/{self.config.userId}/password"
        super().invoke(payload=password_data)
        return self.response


class GetAgentStates(AgentRestMethod):
    """Gets all agent states for the domain.
    GET /orgs/{orgId}/agent_states
    """

    def invoke(self):
        self.method = "GET"
        self.path = f"/orgs/{self.config.orgId}/agent_states"
        super().invoke()
        return self.response.json()


class GetAgentPresence(AgentRestMethod):
    """Gets the agent's presence (current state).
    GET /agents/{agentId}/presence
    """

    def invoke(self):
        self.method = "GET"
        self.path = f"/agents/{self.config.userId}/presence"
        super().invoke()
        return self.response.json()


class SetAgentPresence(AgentRestMethod):
    """Sets the agent's presence (state).
    PUT /agents/{agentId}/presence
    """

    def invoke(self, presence_data):
        self.method = "PUT"
        self.path = f"/agents/{self.config.userId}/presence"
        super().invoke(payload=presence_data)
        return self.response.json()


class GetAgentChannels(AgentRestMethod):
    """Gets the agent's channels.
    GET /agents/{agentId}/channels
    """

    def invoke(self):
        self.method = "GET"
        self.path = f"/agents/{self.config.userId}/channels"
        super().invoke()
        return self.response.json()


class GetLoggedInProfiles(AgentRestMethod):
    """Gets the agent's logged-in profiles.
    GET /agents/{agentId}/logged_in_profiles
    """

    def invoke(self):
        self.method = "GET"
        self.path = f"/agents/{self.config.userId}/logged_in_profiles"
        super().invoke()
        return self.response.json()


#####################################################################
# Interactions
#####################################################################


class CreateNonPrimaryInteraction(AgentRestMethod):
    """Creates a non-primary interaction.
    POST /agents/{agentId}/np_interactions
    """

    def invoke(self, interaction_data):
        self.method = "POST"
        self.path = f"/agents/{self.config.userId}/np_interactions"
        super().invoke(payload=interaction_data)
        return self.response.json()


class CreateInteraction(AgentRestMethod):
    """Creates an interaction or gets a paginated list of text interactions.
    POST /agents/{agentId}/interactions
    """

    def invoke(self, interaction_data):
        self.method = "POST"
        self.path = f"/agents/{self.config.userId}/interactions"
        super().invoke(payload=interaction_data)
        return self.response.json()


class AcceptInteraction(AgentRestMethod):
    """Accepts an interaction.
    PUT /agents/{agentId}/interactions/{interactionId}/accept
    """

    def invoke(self, interactionId, accept_data=None):
        self.method = "PUT"
        self.path = f"/agents/{self.config.userId}/interactions/{interactionId}/accept"
        super().invoke(payload=accept_data)
        return self.response.json()


class SearchInteractions(AgentRestMethod):
    """Searches interactions.
    POST /agents/{agentId}/interactions/search
    """

    def invoke(self, search_data):
        self.method = "POST"
        self.path = f"/agents/{self.config.userId}/interactions/search"
        super().invoke(payload=search_data)
        return self.response.json()


class GetAllInteractions(AgentRestMethod):
    """Gets all interactions for the agent.
    GET /agents/{agentId}/interaction
    """

    def invoke(self):
        self.method = "GET"
        self.path = f"/agents/{self.config.userId}/interaction"
        super().invoke()
        return self.response.json()


class GetColdTransferSettings(AgentRestMethod):
    """Gets information about cold transfers.
    GET /orgs/{orgId}/cold_transfer_settings
    """

    def invoke(self):
        self.method = "GET"
        self.path = f"/orgs/{self.config.orgId}/cold_transfer_settings"
        super().invoke()
        return self.response.json()


class GetLoggedInAgentsForChat(AgentRestMethod):
    """Gets logged-in agents for chat interactions.
    GET /orgs/{orgId}/users/logged_in_agents
    """

    def invoke(self):
        self.method = "GET"
        self.path = f"/orgs/{self.config.orgId}/users/logged_in_agents"
        super().invoke()
        return self.response.json()


class CreateInteractionHistory(AgentRestMethod):
    """Initiates a search for completed interactions.
    POST /agents/{agentId}/history
    """

    def invoke(self, history_data):
        self.method = "POST"
        self.path = f"/agents/{self.config.userId}/history"
        super().invoke(payload=history_data)
        return self.response.json()


class IterateInteractionHistory(AgentRestMethod):
    """Iterates the search for completed interactions.
    PUT /agents/{agentId}/history/{viewId}/next
    """

    def invoke(self, viewId):
        self.method = "PUT"
        self.path = f"/agents/{self.config.userId}/history/{viewId}/next"
        super().invoke()
        return self.response.json()


class RejectInteraction(AgentRestMethod):
    """Rejects an interaction with a reason.
    PUT /agents/{agentId}/interactions/{interactionId}/reject/{reason}
    """

    def invoke(self, interactionId, reason):
        self.method = "PUT"
        self.path = f"/agents/{self.config.userId}/interactions/{interactionId}/reject/{reason}"
        super().invoke()
        return self.response


class GetInteractionNotes(AgentRestMethod):
    """Gets all notes for an interaction.
    GET /agents/{agentId}/interactions/{interactionId}/note
    """

    def invoke(self, interactionId):
        self.method = "GET"
        self.path = f"/agents/{self.config.userId}/interactions/{interactionId}/note"
        super().invoke()
        return self.response.json()


class CreateInteractionNote(AgentRestMethod):
    """Creates a note for an interaction.
    POST /agents/{agentId}/interactions/{interactionId}/note
    """

    def invoke(self, interactionId, note_data):
        self.method = "POST"
        self.path = f"/agents/{self.config.userId}/interactions/{interactionId}/note"
        super().invoke(payload=note_data)
        return self.response.json()


class UpdateInteractionNote(AgentRestMethod):
    """Updates a note for an interaction.
    PUT /agents/{agentId}/interactions/{interactionId}/note/{noteId}
    """

    def invoke(self, interactionId, noteId, note_data):
        self.method = "PUT"
        self.path = f"/agents/{self.config.userId}/interactions/{interactionId}/note/{noteId}"
        super().invoke(payload=note_data)
        return self.response.json()


class GetAgentMessages(AgentRestMethod):
    """Gets a list of messages for the agent.
    GET /agents/{agentId}/messages
    """

    def invoke(self):
        self.method = "GET"
        self.path = f"/agents/{self.config.userId}/messages"
        super().invoke()
        return self.response.json()


class RejectPreview(AgentRestMethod):
    """Rejects an interaction preview with a reason.
    PUT /agents/{agentId}/interactions/{interactionId}/reject_preview/{reason}
    """

    def invoke(self, interactionId, reason):
        self.method = "PUT"
        self.path = f"/agents/{self.config.userId}/interactions/{interactionId}/reject_preview/{reason}"
        super().invoke()
        return self.response


class EscalateToLiveAgent(AgentRestMethod):
    """Escalates a client chat interaction to a live agent.
    POST /agents/{agentId}/interactions/client_chat/{interactionId}/escalateToLiveAgent
    """

    def invoke(self, interactionId):
        self.method = "POST"
        self.path = f"/agents/{self.config.userId}/interactions/client_chat/{interactionId}/escalateToLiveAgent"
        super().invoke()
        return self.response.json()


#####################################################################
# Attachments
#####################################################################


class DownloadEmailAttachment(AgentRestMethod):
    """Downloads an email attachment for an agent.
    GET /attachments/{agentId}/interactions/email/{interactionId}/attachment/{fileName}
    """

    def invoke(self, interactionId, fileName):
        self.method = "GET"
        self.path = f"/attachments/{self.config.userId}/interactions/email/{interactionId}/attachment/{fileName}"
        super().invoke()
        return self.response


class DownloadEmailAttachmentPreAssignment(AgentRestMethod):
    """Downloads an email attachment created before agent assignment.
    GET /attachments/interactions/email/{interactionId}/attachment/{fileName}
    """

    def invoke(self, interactionId, fileName):
        self.method = "GET"
        self.path = f"/attachments/interactions/email/{interactionId}/attachment/{fileName}"
        super().invoke()
        return self.response


class EnableEmailAttachmentDownload(AgentRestMethod):
    """Enables downloading email attachments.
    PUT /attachments/{agentId}/interactions/email/{interactionId}/download
    """

    def invoke(self, interactionId):
        self.method = "PUT"
        self.path = f"/attachments/{self.config.userId}/interactions/email/{interactionId}/download"
        super().invoke()
        return self.response


#####################################################################
# Calls
#####################################################################


class GetActiveInteractions(AgentRestMethod):
    """Gets a list of active interactions for the agent.
    GET /agents/{agentId}/interactions
    """

    def invoke(self):
        self.method = "GET"
        self.path = f"/agents/{self.config.userId}/interactions"
        super().invoke()
        return self.response.json()


class GetAvailableCalls(AgentRestMethod):
    """Gets calls available to the agent.
    GET /agents/{agentId}/interactions/calls
    """

    def invoke(self):
        self.method = "GET"
        self.path = f"/agents/{self.config.userId}/interactions/calls"
        super().invoke()
        return self.response.json()


class GetCallInfo(AgentRestMethod):
    """Gets information about a call.
    GET /agents/{agentId}/interactions/calls/{callId}
    """

    def invoke(self, callId):
        self.method = "GET"
        self.path = f"/agents/{self.config.userId}/interactions/calls/{callId}"
        super().invoke()
        return self.response.json()


class GetSpeedDials(AgentRestMethod):
    """Gets all speed dial information.
    GET /orgs/{orgId}/speed_dials
    """

    def invoke(self):
        self.method = "GET"
        self.path = f"/orgs/{self.config.orgId}/speed_dials"
        super().invoke()
        return self.response.json()


class GetSpeedDial(AgentRestMethod):
    """Gets a specific speed dial.
    GET /orgs/{orgId}/speed_dials/{speedDialId}
    """

    def invoke(self, speedDialId):
        self.method = "GET"
        self.path = f"/orgs/{self.config.orgId}/speed_dials/{speedDialId}"
        super().invoke()
        return self.response.json()


class MakeAgentCall(AgentRestMethod):
    """Calls another agent.
    POST /agents/{agentId}/interactions/make_agent_call
    """

    def invoke(self, call_data):
        self.method = "POST"
        self.path = f"/agents/{self.config.userId}/interactions/make_agent_call"
        super().invoke(payload=call_data)
        return self.response.json()


class MakeExternalCall(AgentRestMethod):
    """Makes a call to an external number.
    POST /agents/{agentId}/interactions/make_external_call
    """

    def invoke(self, call_data):
        self.method = "POST"
        self.path = f"/agents/{self.config.userId}/interactions/make_external_call"
        super().invoke(payload=call_data)
        return self.response.json()


class MakeSkillCall(AgentRestMethod):
    """Makes a call to a skill group.
    POST /agents/{agentId}/interactions/make_skill_call
    """

    def invoke(self, call_data):
        self.method = "POST"
        self.path = f"/agents/{self.config.userId}/interactions/make_skill_call"
        super().invoke(payload=call_data)
        return self.response.json()


class MakeSpeedDialCall(AgentRestMethod):
    """Makes a call to a speed dial number.
    POST /agents/{agentId}/interactions/make_speed_dial_call
    """

    def invoke(self, call_data):
        self.method = "POST"
        self.path = f"/agents/{self.config.userId}/interactions/make_speed_dial_call"
        super().invoke(payload=call_data)
        return self.response.json()


class ClickToDial(AgentRestMethod):
    """Clicks to dial an external number.
    GET /orgs/{orgId}/interactions/click_to_dial
    """

    def invoke(self, **kwargs):
        self.method = "GET"
        self.path = f"/orgs/{self.config.orgId}/interactions/click_to_dial"
        super().invoke(qstring_params=kwargs if kwargs else None)
        return self.response.json()


class MakeTestCall(AgentRestMethod):
    """Makes a test call.
    POST /agents/{agentId}/interactions/make_test_call
    """

    def invoke(self, call_data):
        self.method = "POST"
        self.path = f"/agents/{self.config.userId}/interactions/make_test_call"
        super().invoke(payload=call_data)
        return self.response.json()


class AnswerCall(AgentRestMethod):
    """Answers a call.
    PUT /agents/{agentId}/interactions/calls/{callId}/answer
    """

    def invoke(self, callId):
        self.method = "PUT"
        self.path = f"/agents/{self.config.userId}/interactions/calls/{callId}/answer"
        super().invoke()
        return self.response


class HoldCall(AgentRestMethod):
    """Puts a call on hold.
    PUT /agents/{agentId}/interactions/calls/{callId}/hold
    """

    def invoke(self, callId):
        self.method = "PUT"
        self.path = f"/agents/{self.config.userId}/interactions/calls/{callId}/hold"
        super().invoke()
        return self.response


class UnholdCall(AgentRestMethod):
    """Takes a call off hold.
    PUT /agents/{agentId}/interactions/calls/{callId}/unhold
    """

    def invoke(self, callId):
        self.method = "PUT"
        self.path = f"/agents/{self.config.userId}/interactions/calls/{callId}/unhold"
        super().invoke()
        return self.response


class ParkCall(AgentRestMethod):
    """Parks a call.
    PUT /agents/{agentId}/interactions/calls/{callId}/park
    """

    def invoke(self, callId):
        self.method = "PUT"
        self.path = f"/agents/{self.config.userId}/interactions/calls/{callId}/park"
        super().invoke()
        return self.response


class RetrieveCall(AgentRestMethod):
    """Retrieves a parked call.
    PUT /agents/{agentId}/interactions/calls/{callId}/retrieve
    """

    def invoke(self, callId):
        self.method = "PUT"
        self.path = f"/agents/{self.config.userId}/interactions/calls/{callId}/retrieve"
        super().invoke()
        return self.response


class GetEstimatedWaitTime(AgentRestMethod):
    """Gets the estimated waiting time for a media type.
    GET /orgs/estimatedwaittime/{mediaType}
    """

    def invoke(self, mediaType):
        self.method = "GET"
        self.path = f"/orgs/estimatedwaittime/{mediaType}"
        super().invoke()
        return self.response.json()


class DisposeCall(AgentRestMethod):
    """Sets a call disposition.
    PUT /agents/{agentId}/interactions/calls/{callId}/dispose
    """

    def invoke(self, callId, disposition_data):
        self.method = "PUT"
        self.path = f"/agents/{self.config.userId}/interactions/calls/{callId}/dispose"
        super().invoke(payload=disposition_data)
        return self.response


class RejectCall(AgentRestMethod):
    """Rejects a call.
    PUT /agents/{agentId}/interactions/calls/{callId}/reject
    """

    def invoke(self, callId):
        self.method = "PUT"
        self.path = f"/agents/{self.config.userId}/interactions/calls/{callId}/reject"
        super().invoke()
        return self.response


class AddNumberToDnc(AgentRestMethod):
    """Adds a number to the Do Not Call list.
    PUT /agents/{agentId}/add_number_to_dnc
    """

    def invoke(self, dnc_data):
        self.method = "PUT"
        self.path = f"/agents/{self.config.userId}/add_number_to_dnc"
        super().invoke(payload=dnc_data)
        return self.response


class MakeEchoCall(AgentRestMethod):
    """Makes an echo call.
    POST /agents/{agentId}/echo_call
    """

    def invoke(self):
        self.method = "POST"
        self.path = f"/agents/{self.config.userId}/echo_call"
        super().invoke()
        return self.response


class DeleteEchoCall(AgentRestMethod):
    """Deletes an echo call.
    DELETE /agents/{agentId}/echo_call
    """

    def invoke(self):
        self.method = "DELETE"
        self.path = f"/agents/{self.config.userId}/echo_call"
        super().invoke()
        return self.response


class GetEchoCall(AgentRestMethod):
    """Gets an echo call.
    GET /agents/{agentId}/echo_call
    """

    def invoke(self):
        self.method = "GET"
        self.path = f"/agents/{self.config.userId}/echo_call"
        super().invoke()
        return self.response.json()


class ReturnMissedCall(AgentRestMethod):
    """Returns a personal missed call.
    POST /agents/{agentId}/interactions/return_missed_call
    """

    def invoke(self, call_data=None):
        self.method = "POST"
        self.path = f"/agents/{self.config.userId}/interactions/return_missed_call"
        super().invoke(payload=call_data)
        return self.response


#####################################################################
# Call Variables
#####################################################################


class GetCallVariables(AgentRestMethod):
    """Gets call variables for the domain.
    GET /orgs/{orgId}/call_variables
    """

    def invoke(self):
        self.method = "GET"
        self.path = f"/orgs/{self.config.orgId}/call_variables"
        super().invoke()
        return self.response.json()


class SetCallVariables(AgentRestMethod):
    """Sets call variables for an interaction.
    PUT /agents/{agentId}/interactions/calls/{callId}/call_variables
    """

    def invoke(self, callId, variables_data):
        self.method = "PUT"
        self.path = f"/agents/{self.config.userId}/interactions/calls/{callId}/call_variables"
        super().invoke(payload=variables_data)
        return self.response


#####################################################################
# Callbacks
#####################################################################


class GetAgentCallbacks(AgentRestMethod):
    """Gets scheduled callbacks for an agent.
    GET /agents/{agentId}/callbacks
    """

    def invoke(self):
        self.method = "GET"
        self.path = f"/agents/{self.config.userId}/callbacks"
        super().invoke()
        return self.response.json()


class GetDomainCallbacks(AgentRestMethod):
    """Gets the scheduled callbacks for the domain.
    GET /orgs/{orgId}/callbacks
    """

    def invoke(self):
        self.method = "GET"
        self.path = f"/orgs/{self.config.orgId}/callbacks"
        super().invoke()
        return self.response.json()


class GetPostponedDismissedCallbacks(AgentRestMethod):
    """Gets the state of postponed and dismissed callbacks.
    GET /agents/{agentId}/callbacks/snooze
    """

    def invoke(self):
        self.method = "GET"
        self.path = f"/agents/{self.config.userId}/callbacks/snooze"
        super().invoke()
        return self.response.json()


class AddCallback(AgentRestMethod):
    """Adds a callback.
    POST /agents/{agentId}/callbacks
    """

    def invoke(self, callback_data):
        self.method = "POST"
        self.path = f"/agents/{self.config.userId}/callbacks"
        super().invoke(payload=callback_data)
        return self.response.json()


class UpdateCallback(AgentRestMethod):
    """Updates a callback.
    PUT /agents/{agentId}/callbacks/{callbackId}
    """

    def invoke(self, callbackId, callback_data):
        self.method = "PUT"
        self.path = f"/agents/{self.config.userId}/callbacks/{callbackId}"
        super().invoke(payload=callback_data)
        return self.response.json()


class UpdateCallbacks(AgentRestMethod):
    """Updates a list of callbacks.
    PUT /agents/{agentId}/callbacks
    """

    def invoke(self, callbacks_data):
        self.method = "PUT"
        self.path = f"/agents/{self.config.userId}/callbacks"
        super().invoke(payload=callbacks_data)
        return self.response.json()


class DeleteCallback(AgentRestMethod):
    """Deletes a callback.
    DELETE /agents/{agentId}/callbacks/{callbackId}
    """

    def invoke(self, callbackId):
        self.method = "DELETE"
        self.path = f"/agents/{self.config.userId}/callbacks/{callbackId}"
        super().invoke()
        return self.response


class DeleteCallbacks(AgentRestMethod):
    """Deletes a list of callbacks.
    DELETE /agents/{agentId}/callbacks
    """

    def invoke(self, callbacks_data):
        self.method = "DELETE"
        self.path = f"/agents/{self.config.userId}/callbacks"
        super().invoke(payload=callbacks_data)
        return self.response


class DismissCallback(AgentRestMethod):
    """Dismisses a callback.
    PUT /agents/{agentId}/callbacks/{callbackId}/dismiss
    """

    def invoke(self, callbackId):
        self.method = "PUT"
        self.path = f"/agents/{self.config.userId}/callbacks/{callbackId}/dismiss"
        super().invoke()
        return self.response


class DismissCallbacks(AgentRestMethod):
    """Dismisses multiple callbacks.
    PUT /agents/{agentId}/callbacks/dismiss
    """

    def invoke(self, dismiss_data):
        self.method = "PUT"
        self.path = f"/agents/{self.config.userId}/callbacks/dismiss"
        super().invoke(payload=dismiss_data)
        return self.response


class ReturnCallbackCall(AgentRestMethod):
    """Returns a callback call.
    POST /agents/{agentId}/callbacks/{callbackId}/make_call
    """

    def invoke(self, callbackId, call_data=None):
        self.method = "POST"
        self.path = f"/agents/{self.config.userId}/callbacks/{callbackId}/make_call"
        super().invoke(payload=call_data)
        return self.response.json()


class PostponeCallback(AgentRestMethod):
    """Postpones a callback.
    PUT /agents/{agentId}/callbacks/{callbackId}/snooze
    """

    def invoke(self, callbackId, snooze_data):
        self.method = "PUT"
        self.path = f"/agents/{self.config.userId}/callbacks/{callbackId}/snooze"
        super().invoke(payload=snooze_data)
        return self.response


class PostponeCallbacks(AgentRestMethod):
    """Postpones multiple callbacks.
    PUT /agents/{agentId}/callbacks/snooze
    """

    def invoke(self, snooze_data):
        self.method = "PUT"
        self.path = f"/agents/{self.config.userId}/callbacks/snooze"
        super().invoke(payload=snooze_data)
        return self.response


#####################################################################
# Campaigns
#####################################################################


class GetAvailableCampaigns(AgentRestMethod):
    """Gets available campaigns.
    GET /orgs/{orgId}/available_campaigns
    """

    def invoke(self):
        self.method = "GET"
        self.path = f"/orgs/{self.config.orgId}/available_campaigns"
        super().invoke()
        return self.response.json()


class GetDomainCampaigns(AgentRestMethod):
    """Gets all campaigns in the domain.
    GET /orgs/{orgId}/campaigns
    """

    def invoke(self):
        self.method = "GET"
        self.path = f"/orgs/{self.config.orgId}/campaigns"
        super().invoke()
        return self.response.json()


class GetCampaign(AgentRestMethod):
    """Gets information about a campaign.
    GET /orgs/{orgId}/campaigns/{campaignId}
    """

    def invoke(self, campaignId):
        self.method = "GET"
        self.path = f"/orgs/{self.config.orgId}/campaigns/{campaignId}"
        super().invoke()
        return self.response.json()


class GetAgentCampaigns(AgentRestMethod):
    """Gets a list of inbound campaigns for the agent.
    GET /agents/{agentId}/campaigns
    """

    def invoke(self):
        self.method = "GET"
        self.path = f"/agents/{self.config.userId}/campaigns"
        super().invoke()
        return self.response.json()


class GetAgentCampaignsConfig(AgentRestMethod):
    """Gets the campaigns available to the agent.
    GET /agents/{agentId}/campaigns_config
    """

    def invoke(self):
        self.method = "GET"
        self.path = f"/agents/{self.config.userId}/campaigns_config"
        super().invoke()
        return self.response.json()


class GetCampaignFieldViews(AgentRestMethod):
    """Gets the field views for a campaign.
    GET /agents/{agentId}/campaign/{campaignId}/field_views
    """

    def invoke(self, campaignId):
        self.method = "GET"
        self.path = f"/agents/{self.config.userId}/campaign/{campaignId}/field_views"
        super().invoke()
        return self.response.json()


class GetCampaignScript(AgentRestMethod):
    """Gets a campaign script in the domain.
    GET /orgs/{orgId}/campaigns/{campaignId}/script
    """

    def invoke(self, campaignId):
        self.method = "GET"
        self.path = f"/orgs/{self.config.orgId}/campaigns/{campaignId}/script"
        super().invoke()
        return self.response.json()


class GetWorksheetQuestions(AgentRestMethod):
    """Gets worksheet questions for a campaign.
    GET /orgs/{orgId}/campaigns/{campaignId}/worksheet_questions
    """

    def invoke(self, campaignId):
        self.method = "GET"
        self.path = f"/orgs/{self.config.orgId}/campaigns/{campaignId}/worksheet_questions"
        super().invoke()
        return self.response.json()


class PostSurvey(AgentRestMethod):
    """Posts a survey interaction.
    POST /orgs/interactions/survey
    """

    def invoke(self, survey_data):
        self.method = "POST"
        self.path = "/orgs/interactions/survey"
        super().invoke(payload=survey_data)
        return self.response.json()


#####################################################################
# Conferences
#####################################################################


class GetConfereeAgents(AgentRestMethod):
    """Gets agents available as conference participants.
    GET /agents/{agentId}/conferee_agents
    """

    def invoke(self):
        self.method = "GET"
        self.path = f"/agents/{self.config.userId}/conferee_agents"
        super().invoke()
        return self.response.json()


class AddAgentToConference(AgentRestMethod):
    """Adds an agent as a conference participant.
    POST /agents/{agentId}/interactions/calls/{callId}/add_agent_to_conference
    """

    def invoke(self, callId, conference_data):
        self.method = "POST"
        self.path = f"/agents/{self.config.userId}/interactions/calls/{callId}/add_agent_to_conference"
        super().invoke(payload=conference_data)
        return self.response.json()


class AddCampaignToConference(AgentRestMethod):
    """Adds a campaign as a conference participant.
    POST /agents/{agentId}/interactions/calls/{callId}/add_campaign_to_conference
    """

    def invoke(self, callId, conference_data):
        self.method = "POST"
        self.path = f"/agents/{self.config.userId}/interactions/calls/{callId}/add_campaign_to_conference"
        super().invoke(payload=conference_data)
        return self.response.json()


class AddExternalToConference(AgentRestMethod):
    """Adds an external party as a conference participant.
    POST /agents/{agentId}/interactions/calls/{callId}/add_external_to_conference
    """

    def invoke(self, callId, conference_data):
        self.method = "POST"
        self.path = f"/agents/{self.config.userId}/interactions/calls/{callId}/add_external_to_conference"
        super().invoke(payload=conference_data)
        return self.response.json()


class AddSkillToConference(AgentRestMethod):
    """Adds a queue (skill) as a conference participant.
    POST /agents/{agentId}/interactions/calls/{callId}/add_skill_to_conference
    """

    def invoke(self, callId, conference_data):
        self.method = "POST"
        self.path = f"/agents/{self.config.userId}/interactions/calls/{callId}/add_skill_to_conference"
        super().invoke(payload=conference_data)
        return self.response.json()


class AddSpeedDialToConference(AgentRestMethod):
    """Adds a speed dial number as a conference participant.
    POST /agents/{agentId}/interactions/calls/{callId}/add_speed_dial_to_conference
    """

    def invoke(self, callId, conference_data):
        self.method = "POST"
        self.path = f"/agents/{self.config.userId}/interactions/calls/{callId}/add_speed_dial_to_conference"
        super().invoke(payload=conference_data)
        return self.response.json()


class AddParkedCallToConference(AgentRestMethod):
    """Adds a parked call as a conference participant.
    PUT /agents/{agentId}/interactions/calls/{parkedCallId}/add_to_conference
    """

    def invoke(self, parkedCallId):
        self.method = "PUT"
        self.path = f"/agents/{self.config.userId}/interactions/calls/{parkedCallId}/add_to_conference"
        super().invoke()
        return self.response


class DisconnectConferenceParticipant(AgentRestMethod):
    """Disconnects a conference participant.
    PUT /agents/{agentId}/interactions/calls/{callId}/disconnectConferenceParticipant
    """

    def invoke(self, callId, participant_data):
        self.method = "PUT"
        self.path = f"/agents/{self.config.userId}/interactions/calls/{callId}/disconnectConferenceParticipant"
        super().invoke(payload=participant_data)
        return self.response


class LeaveConference(AgentRestMethod):
    """Leaves a conference.
    PUT /agents/{agentId}/interactions/calls/{callId}/leave_conference
    """

    def invoke(self, callId):
        self.method = "PUT"
        self.path = f"/agents/{self.config.userId}/interactions/calls/{callId}/leave_conference"
        super().invoke()
        return self.response


class CompleteWarmConference(AgentRestMethod):
    """Completes a warm conference.
    POST /agents/{agentId}/interactions/calls/{callId}/complete_warm_conference
    """

    def invoke(self, callId):
        self.method = "POST"
        self.path = f"/agents/{self.config.userId}/interactions/calls/{callId}/complete_warm_conference"
        super().invoke()
        return self.response


#####################################################################
# Connectors
#####################################################################


class GetManualConnectors(AgentRestMethod):
    """Gets manual connectors for a preview session.
    GET /agents/{agentId}/interactions/calls/{callId}/manual_connectors
    """

    def invoke(self, callId):
        self.method = "GET"
        self.path = f"/agents/{self.config.userId}/interactions/calls/{callId}/manual_connectors"
        super().invoke()
        return self.response.json()


class GetPendingConnectors(AgentRestMethod):
    """Gets pending connectors.
    GET /agents/{agentId}/pending_connectors
    """

    def invoke(self):
        self.method = "GET"
        self.path = f"/agents/{self.config.userId}/pending_connectors"
        super().invoke()
        return self.response.json()


class GetPendingConnector(AgentRestMethod):
    """Gets a specific pending connector.
    GET /agents/{agentId}/pending_connectors/{pendingConnectorId}
    """

    def invoke(self, pendingConnectorId):
        self.method = "GET"
        self.path = f"/agents/{self.config.userId}/pending_connectors/{pendingConnectorId}"
        super().invoke()
        return self.response.json()


class ExecuteManualConnector(AgentRestMethod):
    """Executes a manual connector.
    POST /agents/{agentId}/interactions/calls/{callId}/manual_connectors/{connectorId}/execute
    """

    def invoke(self, callId, connectorId, connector_data=None):
        self.method = "POST"
        self.path = f"/agents/{self.config.userId}/interactions/calls/{callId}/manual_connectors/{connectorId}/execute"
        super().invoke(payload=connector_data)
        return self.response.json()


class CreatePreviewPendingConnector(AgentRestMethod):
    """Creates a pending connector for a manual connector during a preview session.
    POST /agents/{agentId}/previews/{previewId}/manual_connectors/{connectorId}
    """

    def invoke(self, previewId, connectorId, connector_data=None):
        self.method = "POST"
        self.path = f"/agents/{self.config.userId}/previews/{previewId}/manual_connectors/{connectorId}"
        super().invoke(payload=connector_data)
        return self.response.json()


class FinalizePendingConnector(AgentRestMethod):
    """Processes a pending connector.
    PUT /agents/{agentId}/pending_connectors/{pendingConnectorId}/finalize
    """

    def invoke(self, pendingConnectorId, finalize_data=None):
        self.method = "PUT"
        self.path = f"/agents/{self.config.userId}/pending_connectors/{pendingConnectorId}/finalize"
        super().invoke(payload=finalize_data)
        return self.response


#####################################################################
# Contacts
#####################################################################


class GetContactFieldViews(AgentRestMethod):
    """Gets contact field layouts.
    GET /agents/{agentId}/contact/field_views
    """

    def invoke(self):
        self.method = "GET"
        self.path = f"/agents/{self.config.userId}/contact/field_views"
        super().invoke()
        return self.response.json()


class GetContactFields(AgentRestMethod):
    """Gets contact fields for the domain.
    GET /orgs/{orgId}/contact_fields
    """

    def invoke(self):
        self.method = "GET"
        self.path = f"/orgs/{self.config.orgId}/contact_fields"
        super().invoke()
        return self.response.json()


class CreateContactHistory(AgentRestMethod):
    """Creates a view of the history of a contact.
    POST /orgs/{orgId}/contacts/{contactId}/history
    """

    def invoke(self, contactId, history_data):
        self.method = "POST"
        self.path = f"/orgs/{self.config.orgId}/contacts/{contactId}/history"
        super().invoke(payload=history_data)
        return self.response.json()


class IterateContactHistory(AgentRestMethod):
    """Iterates the view of the history of a contact.
    PUT /orgs/{orgId}/contacts/{contactId}/history/{viewId}/next
    """

    def invoke(self, contactId, viewId):
        self.method = "PUT"
        self.path = f"/orgs/{self.config.orgId}/contacts/{contactId}/history/{viewId}/next"
        super().invoke()
        return self.response.json()


class GetContacts(AgentRestMethod):
    """Gets contacts for the domain.
    GET /orgs/{orgId}/contacts
    """

    def invoke(self, **kwargs):
        self.method = "GET"
        self.path = f"/orgs/{self.config.orgId}/contacts"
        super().invoke(qstring_params=kwargs if kwargs else None)
        return self.response.json()


class GetContact(AgentRestMethod):
    """Gets a contact by ID.
    GET /orgs/{orgId}/contacts/{contactId}
    """

    def invoke(self, contactId):
        self.method = "GET"
        self.path = f"/orgs/{self.config.orgId}/contacts/{contactId}"
        super().invoke()
        return self.response.json()


class CreateContact(AgentRestMethod):
    """Creates a contact in the domain.
    POST /orgs/{orgId}/contacts
    """

    def invoke(self, contact_data):
        self.method = "POST"
        self.path = f"/orgs/{self.config.orgId}/contacts"
        super().invoke(payload=contact_data)
        return self.response.json()


class CreateAndAssignContact(AgentRestMethod):
    """Creates and assigns a contact to an interaction.
    POST /agents/{agentId}/interactions/{interactionId}/contact
    """

    def invoke(self, interactionId, contact_data):
        self.method = "POST"
        self.path = f"/agents/{self.config.userId}/interactions/{interactionId}/contact"
        super().invoke(payload=contact_data)
        return self.response.json()


class CreateCallContact(AgentRestMethod):
    """Creates a contact for the call.
    POST /agents/{agentId}/interactions/calls/{callId}/contacts_2
    """

    def invoke(self, callId, contact_data):
        self.method = "POST"
        self.path = f"/agents/{self.config.userId}/interactions/calls/{callId}/contacts_2"
        super().invoke(payload=contact_data)
        return self.response.json()


class CreateSocialItemContact(AgentRestMethod):
    """Creates and attaches a contact to a social item.
    POST /agents/{agentId}/interactions/{itemId}/create_contact
    """

    def invoke(self, itemId, contact_data):
        self.method = "POST"
        self.path = f"/agents/{self.config.userId}/interactions/{itemId}/create_contact"
        super().invoke(payload=contact_data)
        return self.response.json()


class SelectCallContact(AgentRestMethod):
    """Selects the contact for the call.
    PUT /agents/{agentId}/interactions/calls/{callId}/active_contact_2
    """

    def invoke(self, callId, contact_data):
        self.method = "PUT"
        self.path = f"/agents/{self.config.userId}/interactions/calls/{callId}/active_contact_2"
        super().invoke(payload=contact_data)
        return self.response


class UpdateInteractionContact(AgentRestMethod):
    """Updates the contact for an interaction.
    PUT /agents/{agentId}/interactions/{interactionId}/contact
    """

    def invoke(self, interactionId, contact_data):
        self.method = "PUT"
        self.path = f"/agents/{self.config.userId}/interactions/{interactionId}/contact"
        super().invoke(payload=contact_data)
        return self.response


class UpdateSocialItemContact(AgentRestMethod):
    """Updates the contact of a social item.
    PUT /agents/{agentId}/interactions/{itemId}/update_contact/{contactId}
    """

    def invoke(self, itemId, contactId, contact_data):
        self.method = "PUT"
        self.path = f"/agents/{self.config.userId}/interactions/{itemId}/update_contact/{contactId}"
        super().invoke(payload=contact_data)
        return self.response


class UpdateDomainContact(AgentRestMethod):
    """Updates a contact in the domain.
    PUT /orgs/{orgId}/contacts/{contactId}
    """

    def invoke(self, contactId, contact_data):
        self.method = "PUT"
        self.path = f"/orgs/{self.config.orgId}/contacts/{contactId}"
        super().invoke(payload=contact_data)
        return self.response


class DeleteContact(AgentRestMethod):
    """Deletes a contact from the domain.
    DELETE /orgs/{orgId}/contacts/{contactId}
    """

    def invoke(self, contactId):
        self.method = "DELETE"
        self.path = f"/orgs/{self.config.orgId}/contacts/{contactId}"
        super().invoke()
        return self.response


class UpdateContactNote(AgentRestMethod):
    """Updates a contact note.
    PUT /orgs/{orgId}/contacts/{contactId}/note
    """

    def invoke(self, contactId, note_data):
        self.method = "PUT"
        self.path = f"/orgs/{self.config.orgId}/contacts/{contactId}/note"
        super().invoke(payload=note_data)
        return self.response


class DeleteContactNote(AgentRestMethod):
    """Deletes a contact note.
    DELETE /orgs/{orgId}/contacts/{contactId}/note/{noteId}
    """

    def invoke(self, contactId, noteId):
        self.method = "DELETE"
        self.path = f"/orgs/{self.config.orgId}/contacts/{contactId}/note/{noteId}"
        super().invoke()
        return self.response


#####################################################################
# UC Settings
#####################################################################


class GetUcSettings(AgentRestMethod):
    """Gets unified communication settings.
    GET /orgs/{orgId}/uc_settings
    """

    def invoke(self):
        self.method = "GET"
        self.path = f"/orgs/{self.config.orgId}/uc_settings"
        super().invoke()
        return self.response.json()


class SyncUsers(AgentRestMethod):
    """Synchronizes users.
    PUT /orgs/{orgId}/users/sync
    """

    def invoke(self):
        self.method = "PUT"
        self.path = f"/orgs/{self.config.orgId}/users/sync"
        super().invoke()
        return self.response


class SyncUser(AgentRestMethod):
    """Synchronizes the unified communication settings for a user.
    PUT /users/{userId}/user_sync
    """

    def invoke(self):
        self.method = "PUT"
        self.path = f"/users/{self.config.userId}/user_sync"
        super().invoke()
        return self.response


#####################################################################
# Dispositions
#####################################################################


class GetCampaignDispositions(AgentRestMethod):
    """Gets the dispositions available for a campaign.
    GET /orgs/{orgId}/campaigns/{campaignId}/dispositions
    """

    def invoke(self, campaignId):
        self.method = "GET"
        self.path = f"/orgs/{self.config.orgId}/campaigns/{campaignId}/dispositions"
        super().invoke()
        return self.response.json()


class GetNoCampaignDispositions(AgentRestMethod):
    """Gets dispositions not associated with a campaign.
    GET /orgs/{orgId}/no_campaign_dispositions
    """

    def invoke(self):
        self.method = "GET"
        self.path = f"/orgs/{self.config.orgId}/no_campaign_dispositions"
        super().invoke()
        return self.response.json()


class SetInteractionDisposition(AgentRestMethod):
    """Sets the disposition for an interaction.
    PUT /agents/{agentId}/interactions/{interactionId}/disposition
    """

    def invoke(self, interactionId, disposition_data):
        self.method = "PUT"
        self.path = f"/agents/{self.config.userId}/interactions/{interactionId}/disposition"
        super().invoke(payload=disposition_data)
        return self.response


#####################################################################
# Features
#####################################################################


class GetFeatures(AgentRestMethod):
    """Gets the list of all features.
    GET /orgs/{orgId}/features
    """

    def invoke(self):
        self.method = "GET"
        self.path = f"/orgs/{self.config.orgId}/features"
        super().invoke()
        return self.response.json()


class GetSpecifiedFeatures(AgentRestMethod):
    """Gets the list of specified features.
    POST /orgs/{orgId}/features
    """

    def invoke(self, features_data):
        self.method = "POST"
        self.path = f"/orgs/{self.config.orgId}/features"
        super().invoke(payload=features_data)
        return self.response.json()


#####################################################################
# Help / Issues
#####################################################################


class SendHelpRequest(AgentRestMethod):
    """Sends a help request.
    POST /agents/{agentId}/help_request
    """

    def invoke(self, help_data):
        self.method = "POST"
        self.path = f"/agents/{self.config.userId}/help_request"
        super().invoke(payload=help_data)
        return self.response


class GetLoggingConfig(AgentRestMethod):
    """Gets the logging configuration.
    GET /agents/{agentId}/logging_config
    """

    def invoke(self):
        self.method = "GET"
        self.path = f"/agents/{self.config.userId}/logging_config"
        super().invoke()
        return self.response.json()


class ReportIssue(AgentRestMethod):
    """Reports an issue.
    POST /agents/{agentId}/issue
    """

    def invoke(self, issue_data):
        self.method = "POST"
        self.path = f"/agents/{self.config.userId}/issue"
        super().invoke(payload=issue_data)
        return self.response


#####################################################################
# Locale / Domain Info
#####################################################################


class GetLocales(AgentRestMethod):
    """Gets user locales.
    GET /orgs/{orgId}/locales
    """

    def invoke(self):
        self.method = "GET"
        self.path = f"/orgs/{self.config.orgId}/locales"
        super().invoke()
        return self.response.json()


class GetDomainAttributes(AgentRestMethod):
    """Gets the domain attributes.
    GET /orgs/{orgId}/attributes
    """

    def invoke(self):
        self.method = "GET"
        self.path = f"/orgs/{self.config.orgId}/attributes"
        super().invoke()
        return self.response.json()


class GetDomainTime(AgentRestMethod):
    """Gets the current time of the domain.
    GET /orgs/{orgId}/time
    """

    def invoke(self):
        self.method = "GET"
        self.path = f"/orgs/{self.config.orgId}/time"
        super().invoke()
        return self.response.json()


class GetTimeZones(AgentRestMethod):
    """Gets the time zones for the domain.
    GET /orgs/{orgId}/time_zones
    """

    def invoke(self):
        self.method = "GET"
        self.path = f"/orgs/{self.config.orgId}/time_zones"
        super().invoke()
        return self.response.json()


class GetTimeZoneIds(AgentRestMethod):
    """Gets the time zone IDs for the domain.
    GET /orgs/{orgId}/time_zone_ids
    """

    def invoke(self):
        self.method = "GET"
        self.path = f"/orgs/{self.config.orgId}/time_zone_ids"
        super().invoke()
        return self.response.json()


class GetAgentTimeZone(AgentRestMethod):
    """Gets the agent's time zone.
    GET /agents/{agentId}/time_zone
    """

    def invoke(self):
        self.method = "GET"
        self.path = f"/agents/{self.config.userId}/time_zone"
        super().invoke()
        return self.response.json()


class GetAgentLocales(AgentRestMethod):
    """Gets bundles of translated resources.
    GET /agents/{agentId}/locales
    """

    def invoke(self):
        self.method = "GET"
        self.path = f"/agents/{self.config.userId}/locales"
        super().invoke()
        return self.response.json()


class GetPhoneNumberFormat(AgentRestMethod):
    """Gets the phone number format for the data center.
    GET /orgs/{orgId}/phone_number/format
    """

    def invoke(self):
        self.method = "GET"
        self.path = f"/orgs/{self.config.orgId}/phone_number/format"
        super().invoke()
        return self.response.json()


class GetPhoneNumberLocales(AgentRestMethod):
    """Gets the phone number format for the domain.
    GET /orgs/{orgId}/phone_number/locales
    """

    def invoke(self):
        self.method = "GET"
        self.path = f"/orgs/{self.config.orgId}/phone_number/locales"
        super().invoke()
        return self.response.json()


class GetLocalizationOptions(AgentRestMethod):
    """Gets the localization options for the domain.
    GET /orgs/{orgId}/phone_number/localization_options
    """

    def invoke(self):
        self.method = "GET"
        self.path = f"/orgs/{self.config.orgId}/phone_number/localization_options"
        super().invoke()
        return self.response.json()


class GetLocaleDomainObjects(AgentRestMethod):
    """Gets locale-specific domain objects.
    GET /agents/{agentId}/locales/{localeId}/domain_objects
    """

    def invoke(self, localeId):
        self.method = "GET"
        self.path = f"/agents/{self.config.userId}/locales/{localeId}/domain_objects"
        super().invoke()
        return self.response.json()


class NlpTag(AgentRestMethod):
    """Uses the NLP tagging service.
    POST /nlp/{domainId}/tag
    """

    def invoke(self, tag_data):
        self.method = "POST"
        self.path = f"/nlp/{self.config.orgId}/tag"
        super().invoke(payload=tag_data)
        return self.response.json()


class GetDomainClusters(AgentRestMethod):
    """Gets the domain clusters.
    GET /orgs/{orgId}/clusters
    """

    def invoke(self):
        self.method = "GET"
        self.path = f"/orgs/{self.config.orgId}/clusters"
        super().invoke()
        return self.response.json()


#####################################################################
# Maintenance (additional)
#####################################################################


class GetMaintenanceNotice(AgentRestMethod):
    """Gets a specific maintenance notice.
    GET /agents/{agentId}/maintenance_notices/{noticeId}
    """

    def invoke(self, noticeId):
        self.method = "GET"
        self.path = f"/agents/{self.config.userId}/maintenance_notices/{noticeId}"
        super().invoke()
        return self.response.json()


class GetSwitchoverMetadata(AgentRestMethod):
    """Gets the maintenance state / switchover metadata of the agent.
    GET /agents/{agentId}/switchover_metadata
    """

    def invoke(self):
        self.method = "GET"
        self.path = f"/agents/{self.config.userId}/switchover_metadata"
        super().invoke()
        return self.response.json()


#####################################################################
# Messages
#####################################################################


class GetMessages(AgentRestMethod):
    """Gets a list of messages.
    GET /messages/{agentId}/messages
    """

    def invoke(self):
        self.method = "GET"
        self.path = f"/messages/{self.config.userId}/messages"
        super().invoke()
        return self.response.json()


class SendMessage(AgentRestMethod):
    """Sends a message.
    POST /messages/{agentId}/messages
    """

    def invoke(self, message_data):
        self.method = "POST"
        self.path = f"/messages/{self.config.userId}/messages"
        super().invoke(payload=message_data)
        return self.response.json()


class SendMessageWithId(AgentRestMethod):
    """Sends a message with a specific message ID.
    POST /messages/{agentId}/messages/{messageId}
    """

    def invoke(self, messageId, message_data):
        self.method = "POST"
        self.path = f"/messages/{self.config.userId}/messages/{messageId}"
        super().invoke(payload=message_data)
        return self.response.json()


class BroadcastMessage(AgentRestMethod):
    """Broadcasts a message to logged-in users.
    POST /users/{userId}/broadcast_messages
    """

    def invoke(self, message_data):
        self.method = "POST"
        self.path = f"/users/{self.config.userId}/broadcast_messages"
        super().invoke(payload=message_data)
        return self.response


class AcceptEmailMessage(AgentRestMethod):
    """Accepts an email message sent from an external source.
    POST /orgs/{orgId}/interactions/email
    """

    def invoke(self, email_data):
        self.method = "POST"
        self.path = f"/orgs/{self.config.orgId}/interactions/email"
        super().invoke(payload=email_data)
        return self.response.json()


#####################################################################
# Previews
#####################################################################


class GetPreviews(AgentRestMethod):
    """Gets preview sessions.
    GET /agents/{agentId}/previews
    """

    def invoke(self):
        self.method = "GET"
        self.path = f"/agents/{self.config.userId}/previews"
        super().invoke()
        return self.response.json()


class GetPreview(AgentRestMethod):
    """Gets a specific preview session.
    GET /agents/{agentId}/previews/{previewId}
    """

    def invoke(self, previewId):
        self.method = "GET"
        self.path = f"/agents/{self.config.userId}/previews/{previewId}"
        super().invoke()
        return self.response.json()


class DisposePreview(AgentRestMethod):
    """Disposes of a preview session.
    PUT /agents/{agentId}/previews/{previewId}/dispose
    """

    def invoke(self, previewId, disposition_data=None):
        self.method = "PUT"
        self.path = f"/agents/{self.config.userId}/previews/{previewId}/dispose"
        super().invoke(payload=disposition_data)
        return self.response


class EndPreview(AgentRestMethod):
    """Ends a preview session.
    PUT /agents/{agentId}/previews/{previewId}/end
    """

    def invoke(self, previewId):
        self.method = "PUT"
        self.path = f"/agents/{self.config.userId}/previews/{previewId}/end"
        super().invoke()
        return self.response


class MakePreviewCall(AgentRestMethod):
    """Makes a call after a preview session.
    POST /agents/{agentId}/previews/{previewId}/make_call
    """

    def invoke(self, previewId, call_data):
        self.method = "POST"
        self.path = f"/agents/{self.config.userId}/previews/{previewId}/make_call"
        super().invoke(payload=call_data)
        return self.response.json()


class RenewPreview(AgentRestMethod):
    """Renews a preview session.
    PUT /agents/{agentId}/previews/{previewId}/renew
    """

    def invoke(self, previewId):
        self.method = "PUT"
        self.path = f"/agents/{self.config.userId}/previews/{previewId}/renew"
        super().invoke()
        return self.response


class UpdatePreviewContact(AgentRestMethod):
    """Updates the contact for a preview session.
    PUT /agents/{agentId}/previews/{previewId}/update_contact
    """

    def invoke(self, previewId, contact_data):
        self.method = "PUT"
        self.path = f"/agents/{self.config.userId}/previews/{previewId}/update_contact"
        super().invoke(payload=contact_data)
        return self.response


class GetAuthorPreview(AgentRestMethod):
    """Gets a preview for an author.
    GET /orgs/{orgId}/authors/{authorId}/preview
    """

    def invoke(self, authorId):
        self.method = "GET"
        self.path = f"/orgs/{self.config.orgId}/authors/{authorId}/preview"
        super().invoke()
        return self.response.json()


#####################################################################
# Recording / Audio
#####################################################################


class GetCallAudio(AgentRestMethod):
    """Gets the call audio information.
    GET /agents/{agentId}/interactions/calls/{callId}/audio
    """

    def invoke(self, callId):
        self.method = "GET"
        self.path = f"/agents/{self.config.userId}/interactions/calls/{callId}/audio"
        super().invoke()
        return self.response.json()


class GetAudioPlayer(AgentRestMethod):
    """Gets the state of the audio player.
    GET /agents/{agentId}/interactions/calls/{callId}/audio/player
    """

    def invoke(self, callId):
        self.method = "GET"
        self.path = f"/agents/{self.config.userId}/interactions/calls/{callId}/audio/player"
        super().invoke()
        return self.response.json()


class GetSoundFile(AgentRestMethod):
    """Gets a sound file by event type.
    GET /agents/{agentId}/sounds/{eventType}/file
    """

    def invoke(self, eventType):
        self.method = "GET"
        self.path = f"/agents/{self.config.userId}/sounds/{eventType}/file"
        super().invoke()
        return self.response


class UpdateSoundFile(AgentRestMethod):
    """Updates a sound file by event type.
    PUT /agents/{agentId}/sounds/{eventType}/file
    """

    def invoke(self, eventType, file_data):
        self.method = "PUT"
        self.path = f"/agents/{self.config.userId}/sounds/{eventType}/file"
        super().invoke(payload=file_data)
        return self.response


class PauseAudioPlayer(AgentRestMethod):
    """Pauses the audio player during a call.
    PUT /agents/{agentId}/interactions/calls/{callId}/audio/player/pause
    """

    def invoke(self, callId):
        self.method = "PUT"
        self.path = f"/agents/{self.config.userId}/interactions/calls/{callId}/audio/player/pause"
        super().invoke()
        return self.response


class ResumeAudioPlayer(AgentRestMethod):
    """Resumes the audio player during a call.
    PUT /agents/{agentId}/interactions/calls/{callId}/audio/player/resume
    """

    def invoke(self, callId):
        self.method = "PUT"
        self.path = f"/agents/{self.config.userId}/interactions/calls/{callId}/audio/player/resume"
        super().invoke()
        return self.response


class StopAudioPlayer(AgentRestMethod):
    """Stops the audio player during a call.
    PUT /agents/{agentId}/interactions/calls/{callId}/audio/player/stop
    """

    def invoke(self, callId):
        self.method = "PUT"
        self.path = f"/agents/{self.config.userId}/interactions/calls/{callId}/audio/player/stop"
        super().invoke()
        return self.response


class PlaySkillPrompt(AgentRestMethod):
    """Plays a skill prompt during a call.
    PUT /agents/{agentId}/interactions/calls/{callId}/audio/player/play_prompt
    """

    def invoke(self, callId, prompt_data):
        self.method = "PUT"
        self.path = f"/agents/{self.config.userId}/interactions/calls/{callId}/audio/player/play_prompt"
        super().invoke(payload=prompt_data)
        return self.response


class StartRecording(AgentRestMethod):
    """Starts recording a call.
    PUT /agents/{agentId}/interactions/calls/{callId}/start_recording
    """

    def invoke(self, callId):
        self.method = "PUT"
        self.path = f"/agents/{self.config.userId}/interactions/calls/{callId}/start_recording"
        super().invoke()
        return self.response


class PauseRecording(AgentRestMethod):
    """Pauses recording a call.
    PUT /agents/{agentId}/interactions/calls/{callId}/pause_recording
    """

    def invoke(self, callId):
        self.method = "PUT"
        self.path = f"/agents/{self.config.userId}/interactions/calls/{callId}/pause_recording"
        super().invoke()
        return self.response


class ResumeRecording(AgentRestMethod):
    """Resumes recording a call.
    PUT /agents/{agentId}/interactions/calls/{callId}/resume_recording
    """

    def invoke(self, callId):
        self.method = "PUT"
        self.path = f"/agents/{self.config.userId}/interactions/calls/{callId}/resume_recording"
        super().invoke()
        return self.response


class StopRecording(AgentRestMethod):
    """Stops recording a call.
    PUT /agents/{agentId}/interactions/calls/{callId}/stop_recording
    """

    def invoke(self, callId):
        self.method = "PUT"
        self.path = f"/agents/{self.config.userId}/interactions/calls/{callId}/stop_recording"
        super().invoke()
        return self.response


class GetCallRecording(AgentRestMethod):
    """Gets a call recording stream.
    GET /agents/{agentId}/recordings/{recordingId}
    """

    def invoke(self, recordingId):
        self.method = "GET"
        self.path = f"/agents/{self.config.userId}/recordings/{recordingId}"
        super().invoke()
        return self.response


class GetActiveSkillsPrompts(AgentRestMethod):
    """Gets all active skills prompts.
    GET /agents/{agentId}/prompts
    """

    def invoke(self):
        self.method = "GET"
        self.path = f"/agents/{self.config.userId}/prompts"
        super().invoke()
        return self.response.json()


class GetSkillPromptStream(AgentRestMethod):
    """Gets a skill prompt recording.
    GET /agents/{agentId}/prompts/{promptId}/stream
    """

    def invoke(self, promptId):
        self.method = "GET"
        self.path = f"/agents/{self.config.userId}/prompts/{promptId}/stream"
        super().invoke()
        return self.response


class GetPersonalGreeting(AgentRestMethod):
    """Gets voicemail greeting information.
    GET /agents/{agentId}/personal_greeting
    """

    def invoke(self):
        self.method = "GET"
        self.path = f"/agents/{self.config.userId}/personal_greeting"
        super().invoke()
        return self.response.json()


class UploadPersonalGreeting(AgentRestMethod):
    """Uploads a personal voicemail greeting.
    PUT /agents/{agentId}/personal_greeting
    """

    def invoke(self, greeting_data):
        self.method = "PUT"
        self.path = f"/agents/{self.config.userId}/personal_greeting"
        super().invoke(payload=greeting_data)
        return self.response


class ResetPersonalGreeting(AgentRestMethod):
    """Resets a personal voicemail greeting.
    DELETE /agents/{agentId}/personal_greeting
    """

    def invoke(self):
        self.method = "DELETE"
        self.path = f"/agents/{self.config.userId}/personal_greeting"
        super().invoke()
        return self.response


#####################################################################
# Queue Callbacks
#####################################################################


class GetQueueCallbacks(AgentRestMethod):
    """Gets all scheduled queue callbacks.
    GET /agents/{agentId}/queue_callbacks
    """

    def invoke(self):
        self.method = "GET"
        self.path = f"/agents/{self.config.userId}/queue_callbacks"
        super().invoke()
        return self.response.json()


class GetQueueCallback(AgentRestMethod):
    """Gets a specific queue callback.
    GET /agents/{agentId}/queue_callbacks/{queueCallbackId}
    """

    def invoke(self, queueCallbackId):
        self.method = "GET"
        self.path = f"/agents/{self.config.userId}/queue_callbacks/{queueCallbackId}"
        super().invoke()
        return self.response.json()


class AnswerQueueCallback(AgentRestMethod):
    """Answers a queue callback.
    PUT /agents/{agentId}/queue_callbacks/{queueCallbackId}/answer
    """

    def invoke(self, queueCallbackId):
        self.method = "PUT"
        self.path = f"/agents/{self.config.userId}/queue_callbacks/{queueCallbackId}/answer"
        super().invoke()
        return self.response


class RejectQueueCallback(AgentRestMethod):
    """Rejects a queue callback.
    PUT /agents/{agentId}/queue_callbacks/{queueCallbackId}/reject
    """

    def invoke(self, queueCallbackId):
        self.method = "PUT"
        self.path = f"/agents/{self.config.userId}/queue_callbacks/{queueCallbackId}/reject"
        super().invoke()
        return self.response


#####################################################################
# Queues
#####################################################################


class GetDomainSkills(AgentRestMethod):
    """Gets the queues (skills) in the domain.
    GET /orgs/{orgId}/skills
    """

    def invoke(self):
        self.method = "GET"
        self.path = f"/orgs/{self.config.orgId}/skills"
        super().invoke()
        return self.response.json()


class GetAgentSkills(AgentRestMethod):
    """Gets the agent's queues (skills).
    GET /agents/{agentId}/skills
    """

    def invoke(self):
        self.method = "GET"
        self.path = f"/agents/{self.config.userId}/skills"
        super().invoke()
        return self.response.json()


class GetActiveSkills(AgentRestMethod):
    """Gets the agent's active queues (skills).
    GET /agents/{agentId}/active_skills
    """

    def invoke(self):
        self.method = "GET"
        self.path = f"/agents/{self.config.userId}/active_skills"
        super().invoke()
        return self.response.json()


class SetActiveSkills(AgentRestMethod):
    """Sets the agent's active queues (skills).
    PUT /agents/{agentId}/active_skills
    """

    def invoke(self, skills_data):
        self.method = "PUT"
        self.path = f"/agents/{self.config.userId}/active_skills"
        super().invoke(payload=skills_data)
        return self.response


class GetSocialTransferableSkills(AgentRestMethod):
    """Gets a list of queues for social interactions.
    GET /agents/{agentId}/social_transferable_skills
    """

    def invoke(self):
        self.method = "GET"
        self.path = f"/agents/{self.config.userId}/social_transferable_skills"
        super().invoke()
        return self.response.json()


#####################################################################
# Reason Codes
#####################################################################


class GetLogoutReasonCodes(AgentRestMethod):
    """Gets the logout reason codes for the domain.
    GET /orgs/{orgId}/logout_reason_codes
    """

    def invoke(self):
        self.method = "GET"
        self.path = f"/orgs/{self.config.orgId}/logout_reason_codes"
        super().invoke()
        return self.response.json()


class GetNotReadyReasonCodes(AgentRestMethod):
    """Gets all not-ready reason codes for the domain.
    GET /orgs/{orgId}/not_ready_reason_codes
    """

    def invoke(self):
        self.method = "GET"
        self.path = f"/orgs/{self.config.orgId}/not_ready_reason_codes"
        super().invoke()
        return self.response.json()


#####################################################################
# Sessions (additional)
#####################################################################


class AgentSessionRestart(AgentRestMethod):
    """Restarts the agent's session.
    PUT /agents/{agentId}/session_restart
    """

    def invoke(self):
        self.method = "PUT"
        self.path = f"/agents/{self.config.userId}/session_restart"
        super().invoke()
        return self.response


class GetSessionExpiration(AgentRestMethod):
    """Gets session expiration information.
    GET /agents/{agentId}/session_expiration
    """

    def invoke(self):
        self.method = "GET"
        self.path = f"/agents/{self.config.userId}/session_expiration"
        super().invoke()
        return self.response.json()


class CanStopSession(AgentRestMethod):
    """Checks whether the agent can stop the session.
    GET /agents/{agentId}/can_stop_session
    """

    def invoke(self):
        self.method = "GET"
        self.path = f"/agents/{self.config.userId}/can_stop_session"
        super().invoke()
        return self.response.json()


class AgentSessionStop(AgentRestMethod):
    """Stops the agent's session.
    PUT /agents/{agentId}/session_stop
    """

    def invoke(self):
        self.method = "PUT"
        self.path = f"/agents/{self.config.userId}/session_stop"
        super().invoke()
        return self.response


class GetAuthMetadata(AgentRestMethod):
    """Gets authentication metadata.
    GET /auth/metadata
    """

    def invoke(self):
        self.method = "GET"
        self.path = "/auth/metadata"
        super().invoke()
        return self.response.json()


class GetAuthRoles(AgentRestMethod):
    """Gets available auth roles.
    GET /auth/roles
    """

    def invoke(self):
        self.method = "GET"
        self.path = "/auth/roles"
        super().invoke()
        return self.response.json()


class GetLoginPageInfo(AgentRestMethod):
    """Gets login page information.
    GET /auth/login_page_info
    """

    def invoke(self):
        self.method = "GET"
        self.path = "/auth/login_page_info"
        super().invoke()
        return self.response.json()


class AgentPing(AgentRestMethod):
    """Checks whether the agent is active (keep-alive).
    PUT /agents/{agentId}/ping
    """

    def invoke(self):
        self.method = "PUT"
        self.path = f"/agents/{self.config.userId}/ping"
        super().invoke()
        return self.response


class AuthLogin(AgentRestMethod):
    """Logs in the user.
    POST /auth/login
    """

    def invoke(self, login_data):
        self.method = "POST"
        self.path = "/auth/login"
        super().invoke(payload=login_data)
        return self.response.json()


class GetAuthSettings(AgentRestMethod):
    """Gets authentication settings.
    GET /auth/settings
    """

    def invoke(self):
        self.method = "GET"
        self.path = "/auth/settings"
        super().invoke()
        return self.response.json()


class SetAuthExceptions(AgentRestMethod):
    """Sets authentication exceptions.
    PUT /auth/exceptions
    """

    def invoke(self, exceptions_data):
        self.method = "PUT"
        self.path = "/auth/exceptions"
        super().invoke(payload=exceptions_data)
        return self.response


#####################################################################
# Stations
#####################################################################


class RestartStation(AgentRestMethod):
    """Restarts the agent's station.
    PUT /agents/{agentId}/station/restart
    """

    def invoke(self):
        self.method = "PUT"
        self.path = f"/agents/{self.config.userId}/station/restart"
        super().invoke()
        return self.response


class ForceRestartSoftphone(AgentRestMethod):
    """Forces the agent's softphone to restart.
    PUT /agents/{agentId}/station/softphone_force_restart
    """

    def invoke(self):
        self.method = "PUT"
        self.path = f"/agents/{self.config.userId}/station/softphone_force_restart"
        super().invoke()
        return self.response


class GetStation(AgentRestMethod):
    """Gets the agent's station information.
    GET /agents/{agentId}/station
    """

    def invoke(self):
        self.method = "GET"
        self.path = f"/agents/{self.config.userId}/station"
        super().invoke()
        return self.response.json()


class GetStationState(AgentRestMethod):
    """Gets the agent's station state.
    GET /agents/{agentId}/station_state
    """

    def invoke(self):
        self.method = "GET"
        self.path = f"/agents/{self.config.userId}/station_state"
        super().invoke()
        return self.response.json()


class GetSoftphoneConfig(AgentRestMethod):
    """Gets the softphone configuration.
    GET /agents/{agentId}/softphone_config
    """

    def invoke(self):
        self.method = "GET"
        self.path = f"/agents/{self.config.userId}/softphone_config"
        super().invoke()
        return self.response.json()


#####################################################################
# Statistics
#####################################################################


class GetDashboardSubscriptions(AgentRestMethod):
    """Gets dashboard subscriptions.
    GET /agents/{agentId}/dashboard/subscriptions
    """

    def invoke(self):
        self.method = "GET"
        self.path = f"/agents/{self.config.userId}/dashboard/subscriptions"
        super().invoke()
        return self.response.json()


class CreateDashboardSubscription(AgentRestMethod):
    """Creates a dashboard subscription.
    POST /agents/{agentId}/dashboard/subscriptions
    """

    def invoke(self, subscription_data):
        self.method = "POST"
        self.path = f"/agents/{self.config.userId}/dashboard/subscriptions"
        super().invoke(payload=subscription_data)
        return self.response.json()


class UpdateDashboardSubscription(AgentRestMethod):
    """Updates a dashboard subscription.
    PUT /agents/{agentId}/dashboard/subscriptions/{subscriptionId}
    """

    def invoke(self, subscriptionId, subscription_data):
        self.method = "PUT"
        self.path = f"/agents/{self.config.userId}/dashboard/subscriptions/{subscriptionId}"
        super().invoke(payload=subscription_data)
        return self.response.json()


class DeleteDashboardSubscription(AgentRestMethod):
    """Deletes a dashboard subscription.
    DELETE /agents/{agentId}/dashboard/subscriptions/{subscriptionId}
    """

    def invoke(self, subscriptionId):
        self.method = "DELETE"
        self.path = f"/agents/{self.config.userId}/dashboard/subscriptions/{subscriptionId}"
        super().invoke()
        return self.response


class GetSubscriptions(AgentRestMethod):
    """Gets the subscriptions available to the agent.
    GET /agents/{agentId}/subscriptions
    """

    def invoke(self):
        self.method = "GET"
        self.path = f"/agents/{self.config.userId}/subscriptions"
        super().invoke()
        return self.response.json()


class UpdateSubscription(AgentRestMethod):
    """Subscribes or unsubscribes the agent to/from statistics.
    PUT /agents/{agentId}/subscriptions/{subscriptionId}
    """

    def invoke(self, subscriptionId, subscription_data):
        self.method = "PUT"
        self.path = f"/agents/{self.config.userId}/subscriptions/{subscriptionId}"
        super().invoke(payload=subscription_data)
        return self.response.json()


class SubscribeGamification(AgentRestMethod):
    """Subscribes the agent to gamification statistics.
    POST /agents/{agentId}/gamification
    """

    def invoke(self):
        self.method = "POST"
        self.path = f"/agents/{self.config.userId}/gamification"
        super().invoke()
        return self.response


class UnsubscribeGamification(AgentRestMethod):
    """Unsubscribes the agent from gamification statistics.
    DELETE /agents/{agentId}/gamification
    """

    def invoke(self):
        self.method = "DELETE"
        self.path = f"/agents/{self.config.userId}/gamification"
        super().invoke()
        return self.response


#####################################################################
# Transfers
#####################################################################


class GetTransferableAgents(AgentRestMethod):
    """Gets agents who can receive transfers.
    GET /agents/{agentId}/transferable_agents
    """

    def invoke(self):
        self.method = "GET"
        self.path = f"/agents/{self.config.userId}/transferable_agents"
        super().invoke()
        return self.response.json()


class TransferToAgent(AgentRestMethod):
    """Transfers a call to another agent.
    PUT /agents/{agentId}/interactions/calls/{callId}/transfer_to_agent
    """

    def invoke(self, callId, transfer_data):
        self.method = "PUT"
        self.path = f"/agents/{self.config.userId}/interactions/calls/{callId}/transfer_to_agent"
        super().invoke(payload=transfer_data)
        return self.response


class TransferToCall(AgentRestMethod):
    """Transfers a parked call to another parked call.
    PUT /agents/{agentId}/interactions/calls/{callId}/transfer_to_call
    """

    def invoke(self, callId, transfer_data):
        self.method = "PUT"
        self.path = f"/agents/{self.config.userId}/interactions/calls/{callId}/transfer_to_call"
        super().invoke(payload=transfer_data)
        return self.response


class TransferToCampaign(AgentRestMethod):
    """Transfers a call to a campaign.
    PUT /agents/{agentId}/interactions/calls/{callId}/transfer_to_campaign
    """

    def invoke(self, callId, transfer_data):
        self.method = "PUT"
        self.path = f"/agents/{self.config.userId}/interactions/calls/{callId}/transfer_to_campaign"
        super().invoke(payload=transfer_data)
        return self.response


class TransferToExternalNumber(AgentRestMethod):
    """Transfers a call to an external number.
    PUT /agents/{agentId}/interactions/calls/{callId}/transfer_to_external_number
    """

    def invoke(self, callId, transfer_data):
        self.method = "PUT"
        self.path = f"/agents/{self.config.userId}/interactions/calls/{callId}/transfer_to_external_number"
        super().invoke(payload=transfer_data)
        return self.response


class TransferToSkill(AgentRestMethod):
    """Transfers a call to a skill group.
    PUT /agents/{agentId}/interactions/calls/{callId}/transfer_to_skill
    """

    def invoke(self, callId, transfer_data):
        self.method = "PUT"
        self.path = f"/agents/{self.config.userId}/interactions/calls/{callId}/transfer_to_skill"
        super().invoke(payload=transfer_data)
        return self.response


class TransferToSpeedDial(AgentRestMethod):
    """Transfers a call to a speed dial number.
    PUT /agents/{agentId}/interactions/calls/{callId}/transfer_to_speed_dial
    """

    def invoke(self, callId, transfer_data):
        self.method = "PUT"
        self.path = f"/agents/{self.config.userId}/interactions/calls/{callId}/transfer_to_speed_dial"
        super().invoke(payload=transfer_data)
        return self.response


class CompleteTransfer(AgentRestMethod):
    """Completes a warm call transfer.
    PUT /agents/{agentId}/interactions/calls/{callId}/complete_transfer
    """

    def invoke(self, callId):
        self.method = "PUT"
        self.path = f"/agents/{self.config.userId}/interactions/calls/{callId}/complete_transfer"
        super().invoke()
        return self.response


class CancelTransfer(AgentRestMethod):
    """Cancels an incomplete warm call transfer.
    PUT /agents/{agentId}/interactions/calls/{callId}/cancel_transfer
    """

    def invoke(self, callId):
        self.method = "PUT"
        self.path = f"/agents/{self.config.userId}/interactions/calls/{callId}/cancel_transfer"
        super().invoke()
        return self.response


#####################################################################
# VCC Configuration
#####################################################################


class GetDomainInfo(AgentRestMethod):
    """Gets the domain information.
    GET /orgs/{orgId}
    """

    def invoke(self):
        self.method = "GET"
        self.path = f"/orgs/{self.config.orgId}"
        super().invoke()
        return self.response.json()


class GetDomainSettings(AgentRestMethod):
    """Gets the domain settings.
    GET /orgs/{orgId}/settings
    """

    def invoke(self):
        self.method = "GET"
        self.path = f"/orgs/{self.config.orgId}/settings"
        super().invoke()
        return self.response.json()


class GetPasswordPolicies(AgentRestMethod):
    """Gets the password policies for the domain.
    GET /orgs/{orgId}/password_policies
    """

    def invoke(self):
        self.method = "GET"
        self.path = f"/orgs/{self.config.orgId}/password_policies"
        super().invoke()
        return self.response.json()


#####################################################################
# Voicemails
#####################################################################


class GetVoicemails(AgentRestMethod):
    """Gets voicemail messages.
    GET /agents/{agentId}/interactions/voicemails
    """

    def invoke(self):
        self.method = "GET"
        self.path = f"/agents/{self.config.userId}/interactions/voicemails"
        super().invoke()
        return self.response.json()


class GetVoicemail(AgentRestMethod):
    """Gets a voicemail message.
    GET /agents/{agentId}/interactions/voicemails/{voicemailId}
    """

    def invoke(self, voicemailId):
        self.method = "GET"
        self.path = f"/agents/{self.config.userId}/interactions/voicemails/{voicemailId}"
        super().invoke()
        return self.response.json()


class GetVoicemailRecording(AgentRestMethod):
    """Gets a voicemail recording.
    GET /agents/{agentId}/interactions/voicemails/{voicemailId}/recordings/{recordingId}
    """

    def invoke(self, voicemailId, recordingId):
        self.method = "GET"
        self.path = f"/agents/{self.config.userId}/interactions/voicemails/{voicemailId}/recordings/{recordingId}"
        super().invoke()
        return self.response


class GetVoicemailCountInfo(AgentRestMethod):
    """Counts personal voicemail messages.
    GET /agents/{agentId}/interactions/voicemails/count_info
    """

    def invoke(self):
        self.method = "GET"
        self.path = f"/agents/{self.config.userId}/interactions/voicemails/count_info"
        super().invoke()
        return self.response.json()


class AcceptVoicemail(AgentRestMethod):
    """Accepts a voicemail message.
    PUT /agents/{agentId}/interactions/voicemails/{voicemailId}/accept
    """

    def invoke(self, voicemailId):
        self.method = "PUT"
        self.path = f"/agents/{self.config.userId}/interactions/voicemails/{voicemailId}/accept"
        super().invoke()
        return self.response


class RejectVoicemail(AgentRestMethod):
    """Rejects a skill voicemail message.
    PUT /agents/{agentId}/interactions/voicemails/{voicemailId}/reject
    """

    def invoke(self, voicemailId):
        self.method = "PUT"
        self.path = f"/agents/{self.config.userId}/interactions/voicemails/{voicemailId}/reject"
        super().invoke()
        return self.response


class ReturnVoicemailCall(AgentRestMethod):
    """Returns a call for a voicemail.
    POST /agents/{agentId}/interactions/voicemails/{voicemailId}/return_call
    """

    def invoke(self, voicemailId, call_data=None):
        self.method = "POST"
        self.path = f"/agents/{self.config.userId}/interactions/voicemails/{voicemailId}/return_call"
        super().invoke(payload=call_data)
        return self.response.json()


class UpdateVoicemail(AgentRestMethod):
    """Updates a voicemail message.
    PUT /agents/{agentId}/interactions/voicemails/{voicemailId}
    """

    def invoke(self, voicemailId, voicemail_data):
        self.method = "PUT"
        self.path = f"/agents/{self.config.userId}/interactions/voicemails/{voicemailId}"
        super().invoke(payload=voicemail_data)
        return self.response


class TransferVoicemail(AgentRestMethod):
    """Transfers a voicemail message.
    PUT /agents/{agentId}/interactions/voicemails/{voicemailId}/transfer
    """

    def invoke(self, voicemailId, transfer_data):
        self.method = "PUT"
        self.path = f"/agents/{self.config.userId}/interactions/voicemails/{voicemailId}/transfer"
        super().invoke(payload=transfer_data)
        return self.response


class MarkVoicemailAsRead(AgentRestMethod):
    """Marks a voicemail message as read or processed.
    PUT /agents/{agentId}/interactions/voicemails/{voicemailId}/mark_as_read
    """

    def invoke(self, voicemailId, read_data=None):
        self.method = "PUT"
        self.path = f"/agents/{self.config.userId}/interactions/voicemails/{voicemailId}/mark_as_read"
        super().invoke(payload=read_data)
        return self.response


class DeleteVoicemail(AgentRestMethod):
    """Deletes a voicemail message.
    DELETE /agents/{agentId}/interactions/voicemails/{voicemailId}
    """

    def invoke(self, voicemailId):
        self.method = "DELETE"
        self.path = f"/agents/{self.config.userId}/interactions/voicemails/{voicemailId}"
        super().invoke()
        return self.response


class GetVoicemailContacts(AgentRestMethod):
    """Gets the contacts for a voicemail message.
    GET /agents/{agentId}/interactions/voicemails/{voicemailId}/contacts
    """

    def invoke(self, voicemailId):
        self.method = "GET"
        self.path = f"/agents/{self.config.userId}/interactions/voicemails/{voicemailId}/contacts"
        super().invoke()
        return self.response.json()


class UpdateVoicemailContact(AgentRestMethod):
    """Updates the contact in a skill voicemail.
    PUT /agents/{agentId}/interactions/voicemails/{voicemailId}/update_contact
    """

    def invoke(self, voicemailId, contact_data):
        self.method = "PUT"
        self.path = f"/agents/{self.config.userId}/interactions/voicemails/{voicemailId}/update_contact"
        super().invoke(payload=contact_data)
        return self.response


class SetActiveVoicemailContact(AgentRestMethod):
    """Selects the active contact for a voicemail message.
    PUT /agents/{agentId}/interactions/voicemails/{voicemailId}/active_contact
    """

    def invoke(self, voicemailId, contact_data):
        self.method = "PUT"
        self.path = f"/agents/{self.config.userId}/interactions/voicemails/{voicemailId}/active_contact"
        super().invoke(payload=contact_data)
        return self.response


#####################################################################
# Worksheets
#####################################################################


class GetWorksheet(AgentRestMethod):
    """Gets the worksheet for an interaction.
    GET /agents/{agentId}/interactions/{interactionId}/worksheet
    """

    def invoke(self, interactionId):
        self.method = "GET"
        self.path = f"/agents/{self.config.userId}/interactions/{interactionId}/worksheet"
        super().invoke()
        return self.response.json()


class UpdateWorksheet(AgentRestMethod):
    """Updates the worksheet for an interaction.
    PUT /agents/{agentId}/interactions/{interactionId}/worksheet
    """

    def invoke(self, interactionId, worksheet_data):
        self.method = "PUT"
        self.path = f"/agents/{self.config.userId}/interactions/{interactionId}/worksheet"
        super().invoke(payload=worksheet_data)
        return self.response


class DeleteWorksheet(AgentRestMethod):
    """Deletes the worksheet for an interaction.
    DELETE /agents/{agentId}/interactions/{interactionId}/worksheet
    """

    def invoke(self, interactionId):
        self.method = "DELETE"
        self.path = f"/agents/{self.config.userId}/interactions/{interactionId}/worksheet"
        super().invoke()
        return self.response
