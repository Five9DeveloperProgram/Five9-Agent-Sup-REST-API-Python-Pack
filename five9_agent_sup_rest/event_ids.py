"""Known Five9 WebSocket event IDs.

Reference catalog derived from the Five9 Agent & Supervisor REST API
documentation.  Using these constants is optional — the handler dispatch
system accepts any string event ID — but they provide discoverability,
inline documentation, and typo protection when writing custom handlers.
"""


# ── Infrastructure / Connection Events ────────────────────────────────

SERVER_UNAVAILABLE = "1000"
"""Communication to VCC server was lost. Client should restart the session."""

SERVER_MAINTENANCE_SWITCHOVER_RELOGIN = "1001"
"""Domain moved to another server (graceful). User may complete current task
before reconnecting. Client should obtain new metadata and reload."""

SERVER_MAINTENANCE_SWITCHOVER_RELOGIN_FORCED = "1002"
"""Domain moved to another VCC server (forced). A system disposition is set
for the agent's task and the agent is moved immediately."""

JMS_SERVER_UNAVAILABLE = "1003"
"""The server cannot receive events. Client should display a message and
try to restart the session."""

FARM_EVENT = "1004"
"""The domain was assigned to another farm."""

SERVER_CONNECTED = "1010"
"""Successful WebSocket connection."""

DUPLICATE_CONNECTION = "1020"
"""Duplicate WebSocket connection. The duplicate connection is immediately
closed by the server with reason code 3000."""

PONG = "1202"
"""Response to a Ping. If not received for two successive requests, the
client should reload the UI and reestablish the WebSocket connection."""


# ── Agent Events ──────────────────────────────────────────────────────

FIVE9_EXCEPTION_DETAILS = "1"
"""Item requested (e.g. settings) was not found."""

EVENT_INCOMING_PREVIEW = "2"
"""Duplicate of ID 8 (EVENT_PREVIEW_CREATED). Will be removed in the future."""

EVENT_CALL_CREATED = "3"
"""New outbound or inbound call created. Duplicate: ID 30."""

EVENT_CALL_UPDATED = "4"
"""Call state was updated or the call ended."""

EVENT_CALL_DELETED = "5"
"""Call ended and disposition selected. Duplicate: ID 31."""

EVENT_INTERACTION_SESSION_UPDATED = "6"
"""Updated interaction."""

EVENT_CONFIGURATION_UPDATED = "7"
"""VCC admin added/deleted/modified a configuration item. Deprecated — use
event 57 (EVENT_RESOURCE_INVALIDATED) instead."""

EVENT_PREVIEW_CREATED = "8"
"""Preview task created."""

EVENT_PREVIEW_DELETED = "9"
"""Preview deleted."""

EVENT_PREVIEW_UPDATED = "10"
"""Preview updated."""

EVENT_ACTIVE_SKILLS_UPDATED = "11"
"""List of active skills changed by user or administrator."""

EVENT_PRESENCE_UPDATED = "12"
"""Agent's presence information was updated."""

EVENT_OPTIONS_UPDATED = "13"
"""Agent options updated."""

EVENT_PERMISSIONS_UPDATED = "14"
"""User's permissions updated."""

EVENT_AGENTS_READY_PRESENCES_SUBSCRIPTION_UPDATE = "15"
"""List of ready agents was updated."""

EVENT_SUBSCRIPTION_UPDATED = "16"
"""User subscription was updated."""

EVENT_LOGIN_STATE_UPDATED = "17"
"""User's login state was updated."""

EVENT_STATION_UPDATED = "18"
"""Status of the station was updated."""

EVENT_AGENT_REMOVED_FROM_SKILL = "19"
"""Skill removed from user's list."""

EVENT_INCOMING_QUEUE_CALLBACK = "20"
"""Duplicate of ID 21 (EVENT_QUEUE_CALLBACK_CREATED). Will be removed."""

EVENT_QUEUE_CALLBACK_CREATED = "21"
"""Queue callback was created."""

EVENT_QUEUE_CALLBACK_UPDATED = "22"
"""Queue callback was updated."""

EVENT_QUEUE_CALLBACK_DELETED = "23"
"""Queue callback was deleted."""

EVENT_VOICEMAILS_CREATED = "24"
"""Agent notified about a new skill voicemail message. Duplicate: ID 27."""

EVENT_VOICEMAILS_UPDATED = "25"
"""User accepts skill voicemail."""

EVENT_VOICEMAILS_DELETED = "26"
"""Voicemail message deleted."""

EVENT_SKILL_STATS_SNAPSHOT_SUBSCRIPTION_UPDATE = "29"
"""User's skill statistics updated (ACD snapshot per skill)."""

EVENT_CALL_CREATED_DUPLICATE = "30"
"""Duplicate of ID 3 (EVENT_CALL_CREATED)."""

EVENT_CALL_DELETED_DUPLICATE = "31"
"""Duplicate of ID 5 (EVENT_CALL_DELETED)."""

EVENT_INTERACTION_SESSION_CREATED = "32"
"""New interaction triggered by disposition, conference end, transfer, etc."""

EVENT_PENDING_CONNECTOR_CREATED = "33"
"""Pending connector created."""

EVENT_PENDING_CONNECTOR_DELETED = "34"
"""Pending connector deleted."""

EVENT_ECHO_CALL_DELETED = "36"
"""Echo call deleted."""

EVENT_MAINTENANCE_ANNOUNCED = "37"
"""Maintenance was announced. Payload contains ms until maintenance begins."""

EVENT_AGENT_ADDED_TO_SKILL = "39"
"""Administrator added a skill to the user's configuration."""

EVENT_NO_ANSWER_ON_TRANSFERRED_CALL = "40"
"""Agent has not answered a call transferred by another agent."""

EVENT_AUDIO_PLAYER_UPDATED = "41"
"""State of the audio player was updated."""

EVENT_STATION_NEEDS_RESTART = "42"
"""Station needs to be restarted."""

EVENT_NOT_READY_REASON_CODES_UPDATED = "48"
"""List of Not Ready reason codes was updated."""

EVENT_NOT_READY_REASON_CODES_DELETED = "49"
"""List of Not Ready reason codes was deleted."""

EVENT_LOGOUT_REASON_CODES_UPDATED = "50"
"""List of logout reason codes updated."""

EVENT_LOGOUT_REASON_CODES_DELETED = "51"
"""Logout reason codes disabled."""

EVENT_CALL_QUALITY_UPDATED = "52"
"""Call quality changed (network issues, etc.)."""

EVENT_CALLBACK_CREATED = "53"
"""Callback created."""

EVENT_CALLBACK_UPDATED = "54"
"""Call returned or callback updated."""

EVENT_CALLBACK_DELETED = "55"
"""Callback deleted."""

EVENT_RESOURCE_INVALIDATED = "57"
"""One or more resources have been updated. Payload contains URLs of
updated resources."""

EVENT_TRANSFER_FAILED = "58"
"""Transfer failed."""

EVENT_CALL_LOGGING_SETTINGS_CHANGED = "60"
"""Call logging settings changed."""

EVENT_MANUAL_CALL_SETTINGS_CHANGED = "61"
"""Manual call settings changed."""

EVENT_DASHBOARD_SUBSCRIPTION_CREATED = "62"
"""Dashboard subscription has been created."""

EVENT_DASHBOARD_SUBSCRIPTION_DELETED = "63"
"""Dashboard subscription has been deleted."""

EVENT_DASHBOARD_SUBSCRIPTION_UPDATED = "64"
"""Dashboard subscription has been updated."""

EVENT_MAKE_CALL_FAILED = "65"
"""Call attempt failed."""

EVENT_CALL_VARIABLES_UPDATED = "66"
"""Call variables updated in VCC administrator application."""

EVENT_CALL_VARIABLES_DELETED = "67"
"""Call variables deleted in VCC administrator application."""

EVENT_SOFTPHONE_DEFAULT_FLAGS_CHANGED = "69"
"""Softphone default flags changed."""

EVENT_MAINTENANCE_STARTED = "70"
"""Maintenance started."""

EVENT_SWITCHED_TO_BACKUP_HOST = "71"
"""Switched to the backup host (geographic redundancy)."""

EVENT_SWITCHED_TO_PRIMARY_HOST = "72"
"""Switched back to the primary host (geographic redundancy)."""

EVENT_MAINTENANCE_COMPLETED = "73"
"""Maintenance completed."""

EVENT_CLICK_TO_DIAL_REQUEST = "74"
"""New click-to-dial request."""

EVENT_CLICK_TO_DIAL_REQUEST_FAILED = "75"
"""Click-to-dial request failed."""

EVENT_CONTACT_UPDATED = "77"
"""Contact was updated."""

EVENT_GRACEFUL_STATE_TRANSITION_SETTINGS_CHANGES = "79"
"""Graceful Agent State Transition settings were updated."""

EVENT_LOGGING_CONFIG_CHANGED = "81"
"""Force logging mode was updated."""

EVENT_DOMAIN_USERS_CAN_MIGRATE = "84"
"""Domain migration state changed to READY_FOR_MIGRATION."""

EVENT_GAMIFICATION_AGENT_STAT = "200"
"""Gamification: interaction statistic (CALL or VOICE_MAIL)."""

EVENT_GAMIFICATION_DISPOSITION_STAT = "201"
"""Gamification: disposition for the statistic."""

EVENT_GAMIFICATION_SKILL_STAT = "202"
"""Gamification: skill groups for the statistic."""


# ── Supervisor Events ─────────────────────────────────────────────────

EVENT_STATS = "5000"
"""Statistics data (full snapshot) has been received."""

EVENT_DISPOSITIONS_INVALIDATED = "5002"
"""Disposition removed/created or name changed."""

EVENT_SKILLS_INVALIDATED = "5003"
"""Skill removed/created or queue name changed."""

EVENT_AGENT_GROUPS_INVALIDATED = "5004"
"""Agent group removed/created or name changed."""

EVENT_CAMPAIGNS_INVALIDATED = "5005"
"""Campaign removed/created or name changed."""

EVENT_USERS_INVALIDATED = "5006"
"""User removed/created or full name changed."""

EVENT_REASON_CODES_INVALIDATED = "5007"
"""Reason code removed/created or name changed."""

EVENT_CAMPAIGN_PROFILES_INVALIDATED = "5008"
"""Campaign profile removed/created or name changed."""

EVENT_CAMPAIGN_OUT_OF_NUMBERS = "5009"
"""Campaign has no more numbers to call."""

EVENT_LISTS_INVALIDATED = "5010"
"""Dialing list removed/created or name changed."""

EVENT_CAMPAIGN_LISTS_CHANGED = "5011"
"""Dialing lists removed from or added to a campaign."""

EVENT_INCREMENTAL_STATS_UPDATE = "5012"
"""Statistics incremental update has been received."""

EVENT_INCREMENTAL_USER_PROFILES_UPDATE = "5013"
"""User profile incremental update has been received."""

EVENT_SKILL_INTERACTIONS_UPDATE = "5014"
"""Skill interactions update has been received."""

EVENT_FILTER_SETTINGS_UPDATED = "6001"
"""Statistics filter settings updated by admin actions."""

EVENT_AGENTS_INVALIDATED = "6002"
"""User removed/created or name/email changed."""

EVENT_SUP_PERMISSIONS_UPDATED = "6003"
"""User permissions were updated (supervisor context)."""

EVENT_RESET_CAMPAIGN_DISPOSITIONS_COMPLETED = "6004"
"""Reset operation for outbound campaign dispositions completed."""

EVENT_MONITORING_STATE_UPDATED = "6005"
"""User monitoring state was updated."""

EVENT_RANDOM_MONITORING_STARTED = "6006"
"""Agent monitoring was started."""

EVENT_FDS_REAL_TIME = "6007"
"""Real-time event from Five9 Data Services for ACD queue event."""

EVENT_INCREMENTAL_INTERACTIONS = "6008"
"""Real-time event from Five9 Data Services for ACD queue events."""


# ── Multi-channel / Interaction Events ────────────────────────────────

AGENT_EVENTS = "10001"
"""Composite agent events envelope."""

INTERACTION_MESSAGES = "10000"
"""Interaction messages envelope."""
