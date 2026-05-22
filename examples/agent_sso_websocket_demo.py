#!/usr/bin/env python3
"""
Agent SSO WebSocket Demo

Demonstrates programmatic SSO authentication to Five9 using OneLogin,
creating an agent session, and listening to real-time WebSocket events.

Prerequisites:
- OneLogin developer account with API credentials
- Five9 SAML app configured in OneLogin
- User provisioned in both OneLogin and Five9 (as Agent)

Configuration:
- Set environment variables or use a .env file in this directory

Required Environment Variables:
    ONELOGIN_SUBDOMAIN      - Your OneLogin subdomain (e.g., "mycompany")
    ONELOGIN_CLIENT_ID      - OneLogin API client ID
    ONELOGIN_CLIENT_SECRET  - OneLogin API client secret
    ONELOGIN_FIVE9_APP_ID   - Five9 app ID in OneLogin (numeric)
    ONELOGIN_TARGET_USER    - Username/email of the Five9 user
    
Optional:
    ONELOGIN_REGION         - "us" (default) or "eu"
    ONELOGIN_TARGET_PASSWORD - User's OneLogin password (prompts if not set)

Usage:
    python examples/agent_sso_websocket_demo.py
    
    # With debug logging
    python examples/agent_sso_websocket_demo.py -l DEBUG
"""

import argparse
import logging
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

# Try to load .env file
try:
    from dotenv import load_dotenv
    # Look for .env in examples folder or project root
    for env_path in [Path(__file__).parent / ".env", Path(__file__).parent.parent / ".env"]:
        if env_path.exists():
            load_dotenv(env_path)
            break
except ImportError:
    pass

import requests

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from five9_agent_sup_rest.client import Five9RestClient
from five9_agent_sup_rest.sso import authenticate_with_saml, SSOAuthError
from five9_agent_sup_rest.methods.default_socket_handlers import SocketEventHandler


# =============================================================================
# OneLogin Configuration
# =============================================================================

@dataclass
class OneLoginConfig:
    """OneLogin API configuration."""
    subdomain: str
    client_id: str
    client_secret: str
    app_id: str
    region: str = "us"
    
    @property
    def api_base_url(self) -> str:
        if self.region == "eu":
            return "https://api.eu.onelogin.com"
        return "https://api.us.onelogin.com"
    
    @classmethod
    def from_env(cls) -> "OneLoginConfig":
        return cls(
            subdomain=os.environ.get("ONELOGIN_SUBDOMAIN", ""),
            client_id=os.environ.get("ONELOGIN_CLIENT_ID", ""),
            client_secret=os.environ.get("ONELOGIN_CLIENT_SECRET", ""),
            app_id=os.environ.get("ONELOGIN_FIVE9_APP_ID", ""),
            region=os.environ.get("ONELOGIN_REGION", "us"),
        )
    
    def validate(self) -> list:
        """Return list of missing required fields."""
        missing = []
        if not self.subdomain:
            missing.append("ONELOGIN_SUBDOMAIN")
        if not self.client_id:
            missing.append("ONELOGIN_CLIENT_ID")
        if not self.client_secret:
            missing.append("ONELOGIN_CLIENT_SECRET")
        if not self.app_id:
            missing.append("ONELOGIN_FIVE9_APP_ID")
        return missing


# =============================================================================
# OneLogin API Functions
# =============================================================================

def get_onelogin_access_token(config: OneLoginConfig) -> str:
    """Get OneLogin API access token using client credentials."""
    url = f"{config.api_base_url}/auth/oauth2/v2/token"
    
    response = requests.post(
        url,
        auth=(config.client_id, config.client_secret),
        json={"grant_type": "client_credentials"},
        headers={"Content-Type": "application/json"},
    )
    
    if response.status_code != 200:
        raise SSOAuthError(f"OneLogin auth failed: {response.status_code} - {response.text}")
    
    return response.json()["access_token"]


def generate_saml_assertion(
    config: OneLoginConfig,
    access_token: str,
    username: str,
    password: Optional[str] = None,
) -> str:
    """Generate SAML assertion for a user via OneLogin API."""
    url = f"{config.api_base_url}/api/2/saml_assertion"
    
    payload = {
        "username_or_email": username,
        "app_id": config.app_id,
        "subdomain": config.subdomain,
    }
    if password:
        payload["password"] = password
    
    response = requests.post(
        url,
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        },
        json=payload,
    )
    
    if response.status_code == 200:
        data = response.json()
        return data.get("data", data.get("saml_response", ""))
    else:
        data = response.json()
        raise SSOAuthError(f"OneLogin SAML generation failed: {data.get('message', response.text)}")


# =============================================================================
# WebSocket Event Handler - Logs All Events
# =============================================================================

class LogAllEventsHandler(SocketEventHandler):
    """
    A simple event handler that logs all WebSocket events to the console.
    
    This handler catches ALL events by overriding the default behavior.
    """
    
    eventId = None  # Will be set dynamically
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    async def handle(self, event):
        """Log the event details."""
        event_id = event.get("context", {}).get("eventId", "unknown")
        payload = event.get("payLoad", {})
        
        # Format output based on event type
        print(f"\n{'='*60}")
        print(f"EVENT: {event_id}")
        print(f"{'='*60}")
        
        # Pretty print the payload
        import json
        if payload:
            print(json.dumps(payload, indent=2, default=str)[:2000])
        else:
            print("(no payload)")
        
        return None


# =============================================================================
# Main
# =============================================================================

def authenticate_via_onelogin() -> dict:
    """Authenticate to Five9 via OneLogin SSO."""
    config = OneLoginConfig.from_env()
    
    # Validate config
    missing = config.validate()
    if missing:
        print(f"❌ Missing environment variables: {', '.join(missing)}")
        print("\nSet these variables or create a .env file.")
        sys.exit(1)
    
    # Get target user
    target_user = os.environ.get("ONELOGIN_TARGET_USER")
    if not target_user:
        target_user = input("Enter OneLogin username/email: ").strip()
    
    # Get password
    target_password = os.environ.get("ONELOGIN_TARGET_PASSWORD")
    if not target_password:
        import getpass
        target_password = getpass.getpass("Enter OneLogin password: ")
    
    print("\n[1/4] Authenticating to OneLogin API...")
    access_token = get_onelogin_access_token(config)
    print("      ✅ Got access token")
    
    print("[2/4] Generating SAML assertion...")
    saml_assertion = generate_saml_assertion(
        config, access_token, target_user, password=target_password
    )
    print("      ✅ Got SAML assertion")
    
    print("[3/4] Authenticating to Five9...")
    session_metadata = authenticate_with_saml(saml_assertion)
    print("      ✅ Five9 session established")
    
    print(f"[4/4] User: {session_metadata.get('userId')}, Farm: {session_metadata['context']['farmId']}")
    
    return session_metadata


def main():
    parser = argparse.ArgumentParser(
        description="Agent SSO WebSocket Demo - Listen to Five9 real-time events"
    )
    parser.add_argument(
        "-l", "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging level"
    )
    parser.add_argument(
        "-s", "--socket-app-key",
        default="python_sso_demo",
        help="Socket application key identifier"
    )
    
    args = parser.parse_args()
    
    logging.basicConfig(
        level=args.log_level,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )
    
    print("=" * 60)
    print("Five9 Agent SSO WebSocket Demo")
    print("=" * 60)
    
    try:
        # Authenticate via OneLogin SSO
        session_metadata = authenticate_via_onelogin()
        
        # Create Five9 client
        print("\nInitializing Five9 client...")
        client = Five9RestClient(
            session_metadata=session_metadata,
            socket_app_key=args.socket_app_key,
            custom_socket_handlers=[LogAllEventsHandler],
        )
        
        # Check agent state
        login_state = client.agent.AgentLoginState.invoke()
        print(f"Agent login state: {login_state}")
        
        # Initialize agent session
        print("Starting agent session...")
        result = client.initialize_agent_session()
        
        if not result:
            print("❌ Failed to initialize agent session")
            sys.exit(1)
        
        print("✅ Agent session started")
        print("\n" + "=" * 60)
        print("WebSocket connected - listening for events...")
        print("Press Enter to disconnect and exit.")
        print("=" * 60)
        
        # Connect to websocket (blocks until user presses Enter)
        client.agent_socket.connect()
        
        # Cleanup
        print("\nLogging out...")
        client.agent.LogOut.invoke()
        print("Session closed.")
        
    except SSOAuthError as e:
        print(f"\n❌ SSO Error: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\nInterrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
