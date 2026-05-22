"""
Five9 SSO Authentication Module

Handles programmatic authentication using SAML assertions from enterprise IdPs
(Azure AD, OneLogin, Okta, etc.). This module implements the full five-step flow:

  1. [IdP] SAML Assertion is prepared by customer's app/IdP
  2. POST SAML to the ACS URL from the assertion (or config override) → get Okta session cookies
  3. OAuth2 /authorize with PKCE → get authorization code
  4. Exchange code for Okta tokens
  5. POST to Five9 login_by_token → get session metadata

The session metadata is then compatible with Five9RestClientSessionConfig.
"""

import base64
import hashlib
import json
import logging
import os
import secrets
import urllib.parse
from dataclasses import dataclass
from typing import Optional, Dict, Tuple
import xml.etree.ElementTree as ET

import requests

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class Five9SSOConfig:
    """Domain-specific SSO settings for a Five9 environment."""

    saml_acs_url: str
    okta_client_id: str
    okta_authorize_url: str
    okta_token_url: str
    okta_redirect_uri: str
    login_by_token_url: str

    @classmethod
    def from_env(cls) -> "Five9SSOConfig":
        """Build config from env vars, falling back to current domain defaults."""
        return cls(
            saml_acs_url=os.getenv("FIVE9_SAML_ACS_URL", ""),
            okta_client_id=os.getenv("FIVE9_OKTA_CLIENT_ID", "0oa8i5mpqhuilseOq5d7"),
            okta_authorize_url=os.getenv(
                "FIVE9_OKTA_AUTHORIZE_URL",
                "https://auth.five9.com/oauth2/default/v1/authorize",
            ),
            okta_token_url=os.getenv(
                "FIVE9_OKTA_TOKEN_URL",
                "https://auth.five9.com/oauth2/default/v1/token",
            ),
            okta_redirect_uri=os.getenv(
                "FIVE9_OKTA_REDIRECT_URI",
                "https://app.five9.com/clients/integrations/adt.main.html",
            ),
            login_by_token_url=os.getenv(
                "FIVE9_LOGIN_BY_TOKEN_URL",
                "https://app.five9.com/appsvcs/rs/svc/auth/login_by_token",
            ),
        )


DEFAULT_SSO_CONFIG = Five9SSOConfig.from_env()


class SSOAuthError(Exception):
    """Base exception for SSO authentication failures."""
    pass


class SSOACSError(SSOAuthError):
    """Failed to establish Okta session via SAML ACS."""
    pass


class SSOAuthorizationError(SSOAuthError):
    """Failed to obtain OAuth2 authorization code."""
    pass


class SSOTokenError(SSOAuthError):
    """Failed to exchange authorization code for tokens."""
    pass


class SSOLoginError(SSOAuthError):
    """Failed to obtain Five9 session metadata."""
    pass


def normalize_saml_assertion(saml_input: str) -> str:
    """
    Normalize a SAML assertion to plain base64.
    
    Accepts:
      - Raw base64 string (no padding needed, padding added if required)
      - URL-encoded SAML response
      - XML-formatted SAML (not yet base64 encoded)
    
    Returns:
      Base64-encoded SAML assertion ready to POST to ACS.
    """
    if not saml_input or not isinstance(saml_input, str):
        raise ValueError("SAML assertion must be a non-empty string")
    
    saml_input = saml_input.strip()
    
    # Try to decode as XML first (detect if it's already XML)
    if saml_input.startswith("<"):
        logger.debug("SAML input detected as XML, encoding to base64")
        return base64.b64encode(saml_input.encode("utf-8")).decode("ascii")
    
    # Try URL decoding (in case it came from a form POST)
    try:
        decoded = urllib.parse.unquote(saml_input)
        if decoded != saml_input:
            logger.debug("SAML input was URL-encoded, decoded and using")
            saml_input = decoded
    except Exception:
        pass
    
    # Assume it's base64. Add padding if needed.
    # Base64 strings should have length % 4 == 0
    padding_needed = len(saml_input) % 4
    if padding_needed:
        saml_input += "=" * (4 - padding_needed)
    
    # Validate it's valid base64 by attempting decode
    try:
        base64.b64decode(saml_input, validate=True)
    except Exception as e:
        raise ValueError(f"Invalid base64 in SAML assertion: {e}")
    
    return saml_input


def extract_saml_acs_url(saml_input: str) -> str:
    """Extract the ACS URL from a SAML Response's Destination or Recipient."""
    saml_b64 = normalize_saml_assertion(saml_input)
    saml_xml = base64.b64decode(saml_b64).decode("utf-8")

    try:
        root = ET.fromstring(saml_xml)
    except ET.ParseError as exc:
        raise ValueError(f"Could not parse SAML XML: {exc}")

    destination = root.attrib.get("Destination")
    if destination:
        return destination

    namespaces = {
        "samlp": "urn:oasis:names:tc:SAML:2.0:protocol",
        "saml": "urn:oasis:names:tc:SAML:2.0:assertion",
    }
    recipient = root.find(".//saml:SubjectConfirmationData", namespaces)
    if recipient is not None:
        recipient_url = recipient.attrib.get("Recipient")
        if recipient_url:
            return recipient_url

    raise ValueError("Could not find ACS URL in SAML assertion")


def _generate_pkce() -> Tuple[str, str]:
    """Generate PKCE code_verifier and code_challenge."""
    code_verifier = secrets.token_hex(25)  # 50 hex chars
    digest = hashlib.sha256(code_verifier.encode("ascii")).digest()
    code_challenge = base64.urlsafe_b64encode(digest).decode("ascii").rstrip("=")
    return code_verifier, code_challenge


def _resolve_saml_acs_url(saml_assertion: str, config: Five9SSOConfig) -> str:
    """Return the configured ACS URL or derive it from the assertion."""
    if config.saml_acs_url:
        return config.saml_acs_url
    return extract_saml_acs_url(saml_assertion)


def _post_saml_to_acs(saml_assertion_b64: str, acs_url: str) -> requests.Session:
    """
    POST SAML assertion to Five9's Okta ACS.
    
    Returns a requests.Session with Okta cookies (sid, xids, JSESSIONID).
    Raises SSOACSError on failure.
    """
    logger.info("Step 2: Posting SAML assertion to Five9 Okta ACS")
    
    session = requests.Session()
    
    payload = {
        "SAMLResponse": saml_assertion_b64,
        "RelayState": "https://app.five9.com/clients/integrations/adt.main.html?f9idplogin=true",
    }
    
    logger.debug(f"SAML assertion length: {len(saml_assertion_b64)} chars")
    logger.debug(f"Assertion starts with: {saml_assertion_b64[:50]}...")
    
    try:
        resp = session.post(
            acs_url,
            data=payload,
            allow_redirects=False,
            timeout=10,
        )
    except requests.RequestException as e:
        raise SSOACSError(f"Failed to reach Okta ACS: {e}")
    
    if resp.status_code not in (200, 302):
        error_detail = resp.text[:1000]
        logger.debug(f"ACS error response: {error_detail}")
        raise SSOACSError(
            f"Okta ACS returned {resp.status_code}: {error_detail}"
        )
    
    # Verify Okta session was established
    cookie_names = [c.name for c in session.cookies]
    if "sid" not in cookie_names:
        raise SSOACSError(
            f"No 'sid' cookie in ACS response. Got: {cookie_names}. "
            f"SAML assertion may be expired or invalid."
        )
    
    logger.debug(f"Okta session established. Cookies: {cookie_names}")
    return session


def _get_oauth_authorization_code(
    okta_session: requests.Session,
    config: Five9SSOConfig,
) -> Tuple[str, str]:
    """
    Use Okta session to get OAuth2 authorization code via PKCE.
    
    Returns (authorization_code, code_verifier).
    Raises SSOAuthorizationError on failure.
    """
    logger.info("Step 3: Requesting OAuth2 authorization code")
    
    code_verifier, code_challenge = _generate_pkce()
    nonce = secrets.token_urlsafe(48)
    
    params = {
        "client_id": config.okta_client_id,
        "code_challenge": code_challenge,
        "code_challenge_method": "S256",
        "nonce": nonce,
        "redirect_uri": config.okta_redirect_uri,
        "response_type": "code",
        "state": "f9idplogin",
        "scope": "openid email profile offline_access",
    }
    
    try:
        resp = okta_session.get(
            config.okta_authorize_url,
            params=params,
            allow_redirects=False,
            timeout=10,
        )
    except requests.RequestException as e:
        raise SSOAuthorizationError(f"Failed to reach OAuth authorize endpoint: {e}")
    
    if resp.status_code != 302:
        raise SSOAuthorizationError(
            f"Expected 302 redirect, got {resp.status_code}: {resp.text[:500]}"
        )
    
    location = resp.headers.get("Location", "")
    parsed = urllib.parse.urlparse(location)
    query_params = urllib.parse.parse_qs(parsed.query)
    
    if "code" not in query_params:
        error = query_params.get("error", ["unknown"])[0]
        description = query_params.get("error_description", [""])[0]
        raise SSOAuthorizationError(
            f"OAuth /authorize failed: {error} - {description}"
        )
    
    authorization_code = query_params["code"][0]
    logger.debug(f"Authorization code obtained: {authorization_code[:20]}...")
    
    return authorization_code, code_verifier


def _exchange_code_for_tokens(
    authorization_code: str,
    code_verifier: str,
    config: Five9SSOConfig,
) -> Dict:
    """
    Exchange OAuth authorization code for tokens.
    
    Returns dict with access_token, refresh_token, id_token, etc.
    Raises SSOTokenError on failure.
    """
    logger.info("Step 4: Exchanging authorization code for tokens")
    
    payload = {
        "client_id": config.okta_client_id,
        "redirect_uri": config.okta_redirect_uri,
        "grant_type": "authorization_code",
        "code_verifier": code_verifier,
        "code": authorization_code,
    }
    
    try:
        resp = requests.post(
            config.okta_token_url,
            data=payload,
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept": "application/json",
            },
            timeout=10,
        )
    except requests.RequestException as e:
        raise SSOTokenError(f"Failed to reach token endpoint: {e}")
    
    if resp.status_code != 200:
        try:
            error_data = resp.json()
        except Exception:
            error_data = {"error": resp.text[:200]}
        raise SSOTokenError(
            f"Token exchange failed ({resp.status_code}): {error_data}"
        )
    
    tokens = resp.json()
    logger.debug(f"Tokens obtained. Expires in: {tokens.get('expires_in')}s")
    
    return tokens


def _login_by_token(
    access_token: str,
    policy: str = "AttachExisting",
    config: Five9SSOConfig = DEFAULT_SSO_CONFIG,
) -> Dict:
    """
    Exchange Okta access token for Five9 session metadata.
    
    Returns session metadata dict with tokenId, orgId, userId, farmId, etc.
    Also includes '_cookies' key with cookie string for subsequent API calls.
    Raises SSOLoginError on failure.
    """
    logger.info("Step 5: Obtaining Five9 session metadata")
    
    try:
        resp = requests.post(
            config.login_by_token_url,
            json={"policy": policy},
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            timeout=10,
        )
    except requests.RequestException as e:
        raise SSOLoginError(f"Failed to reach Five9 login endpoint: {e}")
    
    if resp.status_code != 200:
        raise SSOLoginError(
            f"Five9 login_by_token failed ({resp.status_code}): {resp.text[:500]}"
        )
    
    metadata = resp.json()
    
    # Capture cookies from the response - these are required for supervisor/agent API calls
    cookies_header = "; ".join(
        [f"{cookie.name}={cookie.value}" for cookie in resp.cookies]
    )
    metadata["_cookies"] = cookies_header
    logger.debug(f"Captured {len(resp.cookies)} cookies from login_by_token response")
    
    logger.info(
        f"Session established. User: {metadata.get('userId')}, "
        f"Org: {metadata.get('orgId')}"
    )
    
    return metadata


def authenticate_with_saml(
    saml_assertion: str,
    policy: str = "AttachExisting",
    normalize: bool = True,
    config: Optional[Five9SSOConfig] = None,
) -> Dict:
    """
    Authenticate to Five9 using a SAML assertion.
    
    Executes the complete five-step SSO flow and returns session metadata
    compatible with Five9RestClientSessionConfig.
    
    Args:
        saml_assertion (str): SAML assertion in any format:
            - Base64-encoded (plain or with padding)
            - URL-encoded form data
            - Raw XML (will be base64-encoded)
        policy (str): Session policy. "AttachExisting" or "ForceIn".
            Defaults to "AttachExisting".
        normalize (bool): Whether to normalize the SAML assertion format.
            Defaults to True. Set to False only if you've pre-normalized it.
    
    Returns:
        dict: Session metadata containing:
            - tokenId: Bearer token for subsequent API calls
            - orgId: Organization ID
            - userId: User ID
            - context: Contains farmId and other context
            - metadata: Contains dataCenters with API URLs
    
    Raises:
        SSOAuthError: Base exception for any authentication failure.
        SSOACSError: SAML ACS validation failed.
        SSOAuthorizationError: OAuth authorization failed.
        SSOTokenError: Token exchange failed.
        SSOLoginError: Five9 login failed.
    """
    logger.info("Starting SSO authentication with SAML assertion")
    
    try:
        config = config or DEFAULT_SSO_CONFIG

        # Normalize the SAML assertion
        if normalize:
            saml_assertion = normalize_saml_assertion(saml_assertion)
            logger.debug("SAML assertion normalized")
        
        acs_url = _resolve_saml_acs_url(saml_assertion, config)
        logger.debug(f"Using SAML ACS URL: {acs_url}")

        # Step 2: POST SAML to ACS
        okta_session = _post_saml_to_acs(saml_assertion, acs_url)
        
        # Step 3: Get authorization code
        auth_code, code_verifier = _get_oauth_authorization_code(okta_session, config)
        
        # Step 4: Exchange code for tokens
        tokens = _exchange_code_for_tokens(auth_code, code_verifier, config)
        
        # Step 5: Get Five9 session metadata
        session_metadata = _login_by_token(tokens["access_token"], policy=policy, config=config)
        
        logger.info("SSO authentication successful")
        return session_metadata
    
    except SSOAuthError:
        raise
    except Exception as e:
        logger.exception("Unexpected error during SSO authentication")
        raise SSOAuthError(f"Unexpected error: {e}")
