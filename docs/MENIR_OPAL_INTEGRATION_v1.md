# Menir x Opal: Integration Guide (v1)

## Overview
This document guides the integration of **Google Opal** (No-Code App Builder) with **Menir Server** (Graph API).
Since Opal apps function as "Liquid UIs", they interact with Menir to:
1.  **Read**: Fetch context via Views/Queries.
2.  **Write**: Submit Proposals via Scribe.

## Integration Patterns

### Scenario A: Direct API (Ideal)
If Opal supports direct HTTP/CURL blocks or "Checkpoints" that can auth via Bearer Token.

**Config:**
- **Endpoint**: `https://<your-tunnel-url>/v1/`
- **Auth**: Header `Authorization: Bearer <sk-menir-...>`

**Flow:**
1.  Opal Step 1: User Input (Form).
2.  Opal Step 2: HTTP Request Block.
    - URL: `/v1/query/view`
    - Method: POST
    - Body: `{"view_id": "last_bar_visits"}`
3.  Opal Step 3: Display JSON Result.

### Scenario B: Bridge / Gateway (Likely for V1)
If Opal restricts calls to Google Workspace or specific integrations, use a bridge.

**Bridge Options:**
1.  **n8n / Zapier**:
    - Webhook Trigger (from Opal).
    - HTTP Request (to Menir).
    - Return Data.
2.  **Google Cloud Function (Proxy)**:
    - Receive call from Opal (authorized via Google Identity).
    - Call Menir Server (with protected Token).
    - Return sanitized JSON.

## Suggested Micro-Apps

### 1. The "Bar Scene" Viewer
**Goal**: Show last context before writing a new scene.
- **Endpoint**: `POST /v1/query/view`
- **Payload**: `{"view_id": "last_bar_visits", "params": {"limit": 3}}`
- **Opal Prompt**: "Build a tool that fetches the last 3 bar visits from the API and displays them as cards."

### 2. The "Conflict" Creator
**Goal**: Register a new conflict idea.
- **Endpoint**: `POST /v1/scribe/proposals`
- **Payload**:
```json
{
  "project_id": "livro_debora",
  "type": "conflict_idea",
  "payload": {
    "characters": ["Débora", "Pai"],
    "intensity": "High",
    "description": "User input from form..."
  },
  "source_metadata": {"channel": "opal_app", "app_id": "conflict_v1"}
}
```
- **Opal Prompt**: "Create a form asking for Characters and Description, then send it to the Proposal API."
