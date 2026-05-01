### README Status:
This Readme is somewhat under construction.  If you identify incorrect or missing information, please submit a pull request or open an issue.  Forked from [Andrew Willey](https://github.com/andrewawilley)

# Overview

The Five9 Agent-Sup REST API Python Pack provides an example interface for interacting with Agent and Supervisor sessions in the Five9 Virtual Contact Center (VCC). It simplifies the process of integrating Five9's REST APIs into your Python applications, enabling you to perform agent and supervisor REST API methods, as well as open websockets for real-time interaction and notifications.


# DISCLAIMER
This repository contains sample code which is **not an official Five9 resource**. It is intended solely for educational and illustrative purposes to demonstrate possible ways to interact with Five9 APIs.

Under the MIT License:

- This is **not** officially endorsed or supported software by Five9.
- Any customizations, modifications, or deployments made with this code are done at your **own risk** and **sole responsibility**.
- The code may not account for all use cases or meet specific requirements without further development.
- Five9 assumes **no liability** and provides **no support** for issues arising from the use of this code.

For production-ready tailored implementations, we strongly recommend working with Five9’s Professional Services and Technical Account Management teams.


# Features
* Session Management: Handle login sessions, manage session metadata, and ensure proper authentication for API calls.
* Agent Operations and Supervisor Operations: Implement documented REST methods and perform your custom business logic with the response data.
* WebSocket Support: Establish WebSocket connections for real-time interaction and events with event handling and message processing.

## API Coverage
All methods from the Five9 Agent and Supervisor REST API documentation have been implemented as wrapper classes in `methods/agent_methods.py` and `methods/supervisor_methods.py`. Note that only the methods used in the main login flows and the included examples have been fully tested. The remaining methods follow the same patterns and should work as expected, but have not been individually verified against live API calls. If you encounter issues with a specific method, please open an issue or submit a pull request.


# Getting Started
## Prerequisites
* Tested Python 3.12 or higher, though it should work with Python 3.11 as well
* Five9 Virtual Contact Center (VCC) account with the Agent or Supervisor Role as appropriate for your use case

## Installation
Clone the repository to your local machine, create a virtual environment, and install using pip.

### Windows
```powershell
git clone https://github.com/Five9DeveloperProgram/Five9-Agent-Sup-REST-API-Python-Pack.git
cd Five9-Agent-Sup-REST-API-Python-Pack
python -m venv venvs\main
.\venvs\main\Scripts\activate
pip install .
```
### Linux/MacOS
```bash
git clone https://github.com/Five9DeveloperProgram/Five9-Agent-Sup-REST-API-Python-Pack.git
cd Five9-Agent-Sup-REST-API-Python-Pack
python -m venv venvs/main
source venvs/main/bin/activate
pip install .
```

Note, if you need to customize the package, you can install it in editable mode by running `pip install -e .`

# Configuration

The client object handles the following arguments:
* `region`: The region of the Five9 system to connect to.  This is optional, and will default to `US` if not provided.  Valid values are `US`, `CA`, `LDN`, and `FRK`.
* `username`: The username of the agent or supervisor to log in as.
* `password`: The password of the agent or supervisor to log in as.
* `socket_app_key`: The app key to use for the WebSocket connection.  This is optional, and will default to `python_pack_socket` if not provided.  It is arbitrary and simply used to identify the connection in the Five9 system.
* `custom_supervisor_methods`  and `custom_agent_methods`: An array of custom supervisor methods to add to the client's `supervisor` namespace.  See the section on Implementing Supervisor and Agent REST Methods for more information.
* `custom_socket_handlers`: An array of custom socket handlers to add to the client's `supervisor_socket` and `agent_socket` namespaces.  See the section on Defining a Message Handler for more information. 


# REST Client Usage
## Initializing the Client
Import `Five9RestClient` from five9_agent_suprest.client, create a client instance with credentials, and start a session:

```python
from five9_agent_suprest.client import Five9RestClient

# if you have a credentials.py file in the private folder, you can import the credentials from there
from five9_agent_suprest.private.credentials import ACCOUNTS

username = ACCOUNTS["default_test_account"]["username"]
password = ACCOUNTS["default_test_account"]["password"]

client = Five9RestClient(username='your_username', password='your_password')
```

### Starting an Agent or Supervisor Session
Use `initialize_agent_session()` or `initialize_supervisor_session()` to start sessions on the client.

```python
client.initialize_supervisor_session()
```

## Implementing Supervisor and Agent REST Methods
A number of the documented REST methods are implemented in the `supervisor` and `agent` modules, respectively.  Add additional methods from the developers guide by creating a class in `methods.agent_methods` or `methods.supervisor_methods` as a subclass of the `methods.base.AgentRestMethod` or `methods.base.SupervisorRestMethod`. Implement the invoke() method. 

### Example - Implementing the DomainQueues Method
* This will be a subclass of the `SupervisorRestMethod` class
* Name the class after the method name or functionality, but with the first letter capitalized and the underscores removed.  For example, the `GET /orgs/{orgId}/skills` method could be named `DomainQueues`.
* Add a docstring to the class that contains the method description from the developers guide, as well as the method path.  This is not required, but it is helpful for documentation purposes.
* Implement the `invoke()` method.  This method should set the http `method` and `path` properties, and then call the `super().invoke()` method.  This will invoke the method and store the response in the `response` property.  The `invoke()` method should, at a minimum, return the `response` object, but for many of the REST methods, you will want to pass the json value of the response.
    
```python
from five9client.methods.base import SupervisorRestMethod

class DomainQueues(SupervisorRestMethod):
    """Returns an array of all queues in the domain.
    GET /orgs/{orgId}/skills

    """

    def invoke(self):
        self.method = "GET"
        self.path = f"/orgs/{self.config.orgId}/skills"
        super().invoke()
        # return the json value of the response if the method has a response body that needs
        # to be processed by the calling method.
        return self.response.json()

```

You may pass in an array of `custom_supervisor_methods` or `custom_agent_methods` when creating the client to add your custom methods to the client.  For example:

```python
custom_supervisor_methods = [DomainQueues,]

client = Five9RestClient(
    username='your_username',
    password='your_password',
    custom_supervisor_methods=custom_supervisor_methods
)
```

If you feel a method you have created would be useful to others, please submit a pull request to add it to the package in the `methods` folder.

## Invoking REST Methods
Once a session has been started, you can invoke REST methods by calling the `invoke()` method on the client method class instance.  Pass in the correct payload for the method you are calling as required by the Five9 API documentation.  



# Supervisor and Agent WebSocket Usage
## Starting the WebSocket
The Five9RestClient builds a `supervisor_socket` and `agent_socket` that can be used to connect to the Five9 WebSocket server.   When creating the client, you can pass in a list of custom socket handlers that will be used to handle incoming messages.  The handlers should be subclasses of the `SocketEventHandler` class.  See the section on Defining a Message Handler for more information.

Use the `connect()` method to connect to the WebSocket server.  The `connect()` method will start an asyncio event loop and run until the connection is closed or the user presses `Enter`.

```python

client = Five9RestClient(
    username=username,
    password=password,
    socket_app_key="queue_alert_demo", #optional, will default to "python_pack_socket"
)
client.initialize_supervisor_session()

client.supervisor_socket.connect()
```

## Event IDs
The `five9_agent_sup_rest.event_ids` module provides a complete catalog of known Five9 WebSocket event IDs, derived from the official API documentation. Each constant includes a docstring describing the event's purpose and expected behavior.

Using these constants is **optional** — the handler dispatch system accepts any string event ID — but they provide discoverability via IDE autocomplete, inline documentation, and typo protection.

```python
from five9_agent_sup_rest import event_ids

# Use in a custom handler
class MyCallHandler(SocketEventHandler):
    eventId = event_ids.EVENT_CALL_CREATED  # "3"
    ...
```

The constants are organized into the following categories:

| Category | Event IDs | Examples |
|----------|-----------|---------|
| Infrastructure / Connection | 1000–1202 | `SERVER_CONNECTED` (1010), `PONG` (1202), `DUPLICATE_CONNECTION` (1020) |
| Agent Events | 1–202 | `EVENT_CALL_CREATED` (3), `EVENT_PRESENCE_UPDATED` (12), `EVENT_LOGIN_STATE_UPDATED` (17) |
| Supervisor Events | 5000–6008 | `EVENT_STATS` (5000), `EVENT_INCREMENTAL_STATS_UPDATE` (5012), `EVENT_AGENTS_INVALIDATED` (6002) |
| Multi-channel | 10000–10001 | `INTERACTION_MESSAGES` (10000), `AGENT_EVENTS` (10001) |

## Default Event Handlers
The following events are handled automatically with built-in default handlers. Events not listed here fall through to a generic handler that logs at DEBUG level.

| Event ID | Constant | Behavior |
|----------|----------|----------|
| 1010 | `SERVER_CONNECTED` | Logs successful WebSocket connection |
| 1202 | `PONG` | Logs ping/pong response |
| 70 | `EVENT_MAINTENANCE_STARTED` | Logs maintenance start |
| 73 | `EVENT_MAINTENANCE_COMPLETED` | Logs maintenance completion |
| 1000 | `SERVER_UNAVAILABLE` | Logs at WARNING — VCC connection lost |
| 1001 | `SERVER_MAINTENANCE_SWITCHOVER_RELOGIN` | Logs at WARNING, updates session metadata, triggers reconnect if needed |
| 1002 | `SERVER_MAINTENANCE_SWITCHOVER_RELOGIN_FORCED` | Updates session metadata, triggers reconnect if needed |
| 1003 | `JMS_SERVER_UNAVAILABLE` | Logs at WARNING — event pipeline broken |
| 1020 | `DUPLICATE_CONNECTION` | Logs at WARNING — server will close this socket |

## Defining a Custom Message Handler
The `SocketEventHandler` base class in `default_socket_handlers.py` requires the implementation of an `async def handle(self, event)` method, which is called when an event matching the handler's `eventId` is received. Any custom handler should inherit from this class.

In the example below, we create a handler for event 5000 (the statistics snapshot event) that tracks queue data changes:

```python
from five9_agent_sup_rest.client import Five9RestClient, Five9Socket
from five9_agent_sup_rest.methods.default_socket_handlers import SocketEventHandler
from five9_agent_sup_rest import event_ids

class QueueStatistics:
    def __init__(self, *args, **kwargs):
        self.queue_id_map = {}
        self.queue_mapping_info = kwargs.get("queue_mapping_info", None)
        self.map_queue_ids()

        self.current_queue_snapshot = {
            "added": [],
            "updated": [],  
            "removed": [],
        }

    def map_queue_ids(self):
        for queue in self.queue_mapping_info:
            self.queue_id_map[queue["id"]] = queue["name"]

    def update_queue_info(self, queue_info):
        self.previous_queue_snapshot = self.current_queue_snapshot
        self.current_queue_snapshot = queue_info

class StatsEvent5000Handler(SocketEventHandler):
    """Handler for event 5000 - Statistics Snapshot"""

    eventId = event_ids.EVENT_STATS

    def __init__(self, *args, **kwargs):
        super().__init__(eventId=self.eventId, *args, **kwargs)
        if not hasattr(self.client, "queue_statistics"):
            self.client.queue_statistics = QueueStatistics(
                queue_mapping_info=self.client.supervisor.DomainQueues.invoke()
            )
            logging.info("Queue Statistics Handler Initialized")

    async def handle(self, event):
        logging.info(
            f"Stats Handler EVENT: {event['context']['eventId']} - {event['payLoad']}"
        )
        for updated_object in event["payLoad"]:
            if updated_object["dataSource"] == "ACD_STATUS":
                self.client.queue_statistics.update_queue_info(updated_object["data"])

        return
```
From here, you can add the handler to the client when you create it, or you can add it later using the `add_socket_handler()` method.

```python
custom_socket_handlers = [StatsEvent5000Handler,]

client = Five9RestClient(
    username=username,
    password=password,
    socket_app_key="queue_alert_demo", #optional, will default to "python_pack_socket"
    custom_socket_handlers=custom_socket_handlers
)
client.initialize_supervisor_session()

# queues = client.supervisor.DomainQueues.invoke()

client.supervisor_socket.connect()
```