# Login and metadata endpoint URLs keyed by Five9 region.
# Pass the region key to Five9RestClientSessionConfig via the `region` kwarg.
SETTINGS = {
    "US": {  # United States (default)
        "FIVENINE_VCC_LOGIN_URL": "https://app.five9.com/appsvcs/rs/svc/auth/login",
        "FIVENINE_VCC_METADATA_URL": "https://app.five9.com/appsvcs/rs/svc/metadata",
    },
    "CA": {  # Canada
        "FIVENINE_VCC_LOGIN_URL": "https://app.ca.five9.com/appsvcs/rs/svc/auth/login",
        "FIVENINE_VCC_METADATA_URL": "https://app.ca.five9.com/appsvcs/rs/svc/metadata",
    },
    "LDN": {  # Europe (London)
        "FIVENINE_VCC_LOGIN_URL": "https://app.ca.five9.eu/appsvcs/rs/svc/auth/login",
        "FIVENINE_VCC_METADATA_URL": "https://app.ca.five9.eu/appsvcs/rs/svc/metadata",
    },
    "FRK": {  # Europe (Frankfurt)
        "FIVENINE_VCC_LOGIN_URL": "https://app.eu.five9.eu/appsvcs/rs/svc/auth/login",
        "FIVENINE_VCC_METADATA_URL": "https://app.eu.five9.eu/appsvcs/rs/svc/metadata",
    },
}

CONTEXT_PATHS = {
    # Agent REST API Services
    "agent_rest": "/appsvcs/rs/svc",
    # Agent call recordings and email message attachments"
    "agent_str": "/strsvcs/rs/svc",
    # Supervisor REST API Services
    "sup_rest": "/supsvcs/rs/svc",
    
    "websocket_agent": "/appsvcs/ws/{socket_app_key}_agent",
    "websocket_supervisor": "/supsvcs/sws/{socket_app_key}_super",
}
