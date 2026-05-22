# Five9 SSO Authentication Guide

This document explains how to programmatically authenticate to Five9 using SAML SSO from an enterprise Identity Provider (IdP) like OneLogin, Okta, or Azure AD.

## Overview

Five9 uses **Okta** as an identity broker. When authenticating via SSO, the flow is:

```
┌──────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────┐
│   IdP    │ ──► │ Five9/Okta  │ ──► │ Okta OAuth  │ ──► │  Five9  │
│(OneLogin)│     │   ACS       │     │   Server    │     │   API   │
└──────────┘     └─────────────┘     └─────────────┘     └─────────┘
   SAML           Session +           Access            Session
  Assertion       Cookies             Token             Metadata
```

**Key Insight**: The SAML assertion must be **IdP-initiated** (not SP-initiated) to work programmatically. SP-initiated assertions contain an `InResponseTo` attribute that binds them to a specific browser session.

---

## Prerequisites

### 1. Configure Your IdP (OneLogin/Okta/Azure AD)

Create a SAML application in your IdP with these settings:

| Setting | Value |
|---------|-------|
| **ACS URL / Recipient** | `https://auth.five9.com/sso/saml2/{okta_app_id}` |
| **Audience / Entity ID** | `https://www.okta.com/saml2/service-provider/{sp_id}` |
| **SAML Initiator** | **IdP-initiated** (critical!) |
| **Name ID Format** | Email |
| **Signature** | Sign Response |

The `{okta_app_id}` comes from Five9's SSO configuration.

### 2. Ensure User Exists in Both Systems

The user must:
- Exist in your IdP with the Five9 app assigned
- Exist in Five9 with a matching email address
- Have the appropriate role (Agent, Supervisor, Admin)

### 3. For Programmatic Access (IdP API)

If your IdP supports generating SAML assertions via API (like OneLogin), you'll need:
- API credentials with "Generate SAML tokens" permission
- The Five9 app ID in your IdP

---

## Authentication Flow

### Step 1: Generate SAML Assertion

Obtain a SAML assertion from your IdP. This can be done via:

**Option A: IdP API** (preferred for automation)
```
POST https://{idp-domain}/api/2/saml_assertion
{
  "username_or_email": "user@company.com",
  "password": "user_password",
  "app_id": "12345",
  "subdomain": "your-subdomain"
}

Response: Base64-encoded SAML Response
```

**Option B: IdP-Initiated SSO URL**

Navigate to the IdP's app launch URL to trigger an unsolicited SAML response.

**Critical**: Verify the assertion does NOT contain `InResponseTo` attribute:
```xml
<!-- ❌ SP-initiated (will fail) -->
<samlp:Response InResponseTo="id123456789">

<!-- ✅ IdP-initiated (will work) -->
<samlp:Response ID="_abc123">
```

---

### Step 2: POST SAML to Five9/Okta ACS

Post the SAML assertion to Five9's Okta Assertion Consumer Service endpoint.

**Request:**
```http
POST https://auth.five9.com/sso/saml2/{okta_app_id}
Content-Type: application/x-www-form-urlencoded

SAMLResponse={base64_encoded_saml_assertion}&RelayState=
```

**Response:** 
- Status: `302 Found`
- `Location` header: Redirect URL (ignore this)
- **Capture cookies**: `sid`, `JSESSIONID`, `DT`, `xids`

These cookies establish the Okta session and are required for the next step.

---

### Step 3: OAuth Authorization Code Request

Using the cookies from Step 2, request an OAuth authorization code.

**Request:**
```http
GET https://auth.five9.com/oauth2/default/v1/authorize
  ?client_id=0oa8i5mpqhuilseOq5d7
  &response_type=code
  &scope=openid email profile offline_access
  &redirect_uri=https://app.five9.com/clients/integrations/adt.main.html
  &state=f9idplogin
  &nonce={random_string}
  &code_challenge={sha256_base64url(code_verifier)}
  &code_challenge_method=S256

Cookie: {cookies_from_step_2}
```

**PKCE Parameters:**
- `code_verifier`: Random string (43-128 chars)
- `code_challenge`: `BASE64URL(SHA256(code_verifier))`

**Response:**
- Status: `302 Found`
- `Location` header contains: `...?code={authorization_code}&state=f9idplogin`
- Extract the `code` parameter

---

### Step 4: Exchange Code for Tokens

Exchange the authorization code for OAuth tokens.

**Request:**
```http
POST https://auth.five9.com/oauth2/default/v1/token
Content-Type: application/x-www-form-urlencoded

client_id=0oa8i5mpqhuilseOq5d7
&grant_type=authorization_code
&code={authorization_code}
&code_verifier={code_verifier_from_step_3}
&redirect_uri=https://app.five9.com/clients/integrations/adt.main.html
```

**Response:**
```json
{
  "token_type": "Bearer",
  "expires_in": 600,
  "access_token": "eyJraWQi...",
  "refresh_token": "...",
  "id_token": "..."
}
```

---

### Step 5: Login by Token to Five9

Exchange the Okta access token for a Five9 session.

**Request:**
```http
POST https://app.five9.com/appsvcs/rs/svc/auth/login_by_token
Content-Type: application/json
Authorization: Bearer {access_token_from_step_4}

{
  "policy": "AttachExisting"
}
```

**Response:**
```json
{
  "tokenId": "abc123-def456-...",
  "sessionId": "...",
  "orgId": "131792",
  "userId": "3799884",
  "context": {
    "farmId": "252",
    "cloudClientUrl": "https://api.us.five9.net/"
  },
  "metadata": {
    "dataCenters": [{
      "name": "Atlanta Data Center",
      "apiUrls": [{"host": "app-atl.five9.com", "port": "443"}]
    }]
  }
}
```

**Capture the response cookies** — they're required for subsequent API calls:
- `apiRouteKey`
- `farmId`
- `Authorization`
- `f9-sessionId`

---

## Step 6: Create Agent/Supervisor Session

Now you can use the Five9 REST API to create a session.

### Check Login State

```http
GET https://{api_host}/agentsvcs/rs/svc/agents/login_state
Authorization: Bearer-{tokenId}
farmId: {farmId}
Cookie: {cookies_from_step_5}
```

Response: `"SELECT_STATION"`, `"ACCEPT_NOTICE"`, or `"WORKING"`

### Start Agent Session

```http
PUT https://{api_host}/agentsvcs/rs/svc/agents/session_start
  ?stationId=
  &stationType=EMPTY
  &stationState=DISCONNECTED
Authorization: Bearer-{tokenId}
farmId: {farmId}
Cookie: {cookies_from_step_5}
```

### Accept Maintenance Notices (if required)

```http
GET https://{api_host}/agentsvcs/rs/svc/agents/maintenance_notices
PUT https://{api_host}/agentsvcs/rs/svc/agents/maintenance_notices/{notice_id}/accept
```

---

## WebSocket Connection

Once the session is established, connect to the WebSocket for real-time events:

```
wss://{api_host}/agentsws/{app_key}
```

**Headers:**
```
Authorization: Bearer-{tokenId}
Cookie: {cookies_from_step_5}
```

Send periodic `ping` messages (every 15 seconds) to keep the connection alive.

---

## Summary: Required Values

| Value | Source | Used In |
|-------|--------|---------|
| `okta_app_id` | Five9 SSO config | Step 2 URL |
| `client_id` | Five9 Okta | Steps 3 & 4 |
| `redirect_uri` | Fixed | Steps 3 & 4 |
| `code_verifier` | Generated (random) | Steps 3 & 4 |
| `access_token` | Step 4 response | Step 5 |
| `tokenId` | Step 5 response | All API calls |
| `farmId` | Step 5 response | All API calls |
| `cookies` | Steps 2 & 5 | All API calls |
| `api_host` | Step 5 `metadata.dataCenters` | All API calls |

---

## Troubleshooting

### "400 Bad Request" at ACS (Step 2)

- **InResponseTo present**: The assertion is SP-initiated. Use IdP-initiated flow.
- **Assertion expired**: SAML assertions typically expire in 5 minutes.
- **Wrong ACS URL**: Verify the `Destination` in the assertion matches the POST URL.

### "403 Forbidden" on API calls

- **Missing cookies**: Ensure cookies from `login_by_token` are included.
- **Wrong role**: User doesn't have Agent/Supervisor permissions in Five9.

### "401 Unauthorized"

- **Token expired**: The `access_token` expires in 600 seconds (10 minutes).
- **Missing Authorization header**: Must be `Bearer-{tokenId}` (note the hyphen).

---

## Security Considerations

1. **Never expose credentials**: Store IdP API credentials securely.
2. **Use HTTPS**: All endpoints require TLS.
3. **Token lifetime**: Implement token refresh for long-running sessions.
4. **Audit logging**: Log authentication events for compliance.
