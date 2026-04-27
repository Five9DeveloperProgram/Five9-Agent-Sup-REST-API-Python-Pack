import argparse
from getpass import getpass
import json
import logging
import os

from five9_agent_sup_rest.client import Five9RestClient

# You can create a directory called "private" and create a file called "credentials.py" in it
# with a dictionary called "ACCOUNTS" that contains your Five9 account credentials
# ACCOUNTS = {
#     'default_test_account': {
#       'username': 'your_username@your_domain',
#       'password': 'superSecretPassword',
#     }
try:
    from private.credentials import ACCOUNTS
except ImportError:
    ACCOUNTS = {}


if __name__ == "__main__":
    """
    Demo for the undocumented GET /orgs/{orgId}/application_seats endpoint.

    Requires a user with Supervisor role and the CAN_VIEW_ACTIVE_SESSIONS
    permission (cloud permission: agentsession.active-sessions.view).

    Prints the raw JSON response from the endpoint so it can be inspected
    and shared with the customer.
    """
    parser = argparse.ArgumentParser(
        description="Fetch application seat data from the Five9 supervisor API."
    )
    parser.add_argument(
        "-u",
        "--username",
        default=os.environ.get("FIVE9_USERNAME", None),
        help="Username for authentication",
    )
    parser.add_argument(
        "-p",
        "--password",
        default=os.environ.get("FIVE9_PASSWORD", None),
        help="Password for authentication",
    )
    parser.add_argument(
        "-a",
        "--account-alias",
        default=None,
        help="Account alias to use for looking up credentials in ACCOUNTS dictionary",
    )
    parser.add_argument("-r", "--region", default="US", help="US, CA, LDN, FRK")
    parser.add_argument(
        "-l", "--logging-level", default="DEBUG", help="Logging level to use"
    )

    args = parser.parse_args()

    logging.basicConfig(
        level=args.logging_level.upper(),
        format="%(asctime)s - %(levelname)s - %(message)s",
    )

    if args.account_alias:
        account_info = ACCOUNTS.get(args.account_alias)
        if not account_info:
            raise ValueError(f"No account found for alias: {args.account_alias}")
        username = account_info["username"]
        password = account_info["password"]
    else:
        username = args.username or input("Enter username: ")
        password = args.password or getpass("Enter password: ")

    client = Five9RestClient(
        username=username,
        password=password,
        region=args.region,
    )
    client.initialize_supervisor_session()

    logging.info("Fetching user permissions via supervisor endpoint...")
    sup_permissions = client.supervisor.GetPermissions.invoke()
    print("\n--- GET /supsvcs/rs/svc/users/{userId}/permissions response ---")
    print(json.dumps(sup_permissions, indent=2))
    print("--------------------------------------------------\n")

    logging.info("Fetching user permissions via auth endpoint...")
    auth_permissions = client.agent.AuthPermissions.invoke()
    print("\n--- GET /appsvcs/rs/svc/auth/permissions response ---")
    print(json.dumps(auth_permissions, indent=2))
    print("--------------------------------------------------\n")

    logging.info("Exchanging VCC token for cloud JWT...")
    token_result = client.supervisor.ExchangeFdmToken.invoke()
    print("\n--- POST {cloudTokenUrl}/cloudauthsvcs/v1/domains/{orgId}/exchangefdmtoken response ---")
    print(json.dumps({k: v if k != "access_token" else v[:50] + "..." for k, v in token_result.items()}, indent=2))
    print("--------------------------------------------------\n")

    logging.info("Fetching cloud UI permissions...")
    cloud_permissions = client.supervisor.GetCloudUiPermissions.invoke()
    print("\n--- GET {cloudClientUrl}/acl/v1/domains/{orgId}/my-ui-permissions response ---")
    print(json.dumps(cloud_permissions, indent=2))
    print("--------------------------------------------------\n")

    logging.info("Fetching application seats...")
    result = client.supervisor.GetApplicationSeats.invoke()

    print("\n--- GET /orgs/{orgId}/application_seats response ---")
    print(json.dumps(result, indent=2))
    print("----------------------------------------------------\n")

    client.supervisor.LogOut.invoke()
    logging.info("Logged out.")
