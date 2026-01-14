# Menir v1.2: Headless API + Opal-ready
**Date:** 2025-12-12
**Status:** RELEASED
**Phase:** 3 (Opal Integration Pilot)

## 🏆 Milestone Achieved
Menir has successfully transitioned from a local CLI-only OS to a **Headless Intelligence Engine**.
The new "Menir Server" exposes the logic and memory of the system via a secure, governed REST API, ready to be consumed by "Liquid UIs" (Google Opal).

## 📦 Released Components
1.  **Menir Server (`scripts/menir_server.py`)**:
    - **Status**: Stable (Passed 7/7 Tests).
    - **Tech**: FastAPI, HTTPBearer Auth.
    - **Key Feature**: Zero-Trust Write (All writes are Proposals).

2.  **API Design (`docs/MENIR_SERVER_API_v1.md`)**:
    - **Read**: `/v1/query/view` (Canonical Views).
    - **Write**: `/v1/scribe/proposals` (Scribe Engine).
    - **Compliance**: LGPD-ready Audit Logs.

3.  **Canonical Views**:
    - `views/last_bar_visits.cypher`: Context for the Viewer Pilot.
    - `views/conflicts_by_chapter.cypher`: Analytics.

## 🔮 Strategy: Menir x Opal
We strictly adhere to the **"Caller-Agnostic"** API design.
- **Menir** does not know it is talking to Opal. It speaks standard HTTP/REST.
- **Opal** is the "Client". If it cannot speak direct HTTP, we use a Bridge (Proxy), but we **never** degrade the API design to fit the tool.

## 🚀 Next Mission: Opal Pilots
1.  **Pilot 1 (Read)**: "Viewer - Last Bar Visits"
    - **Risk**: Low (Read-Only).
    - **Goal**: Prove Opal can fetch and display JSON data from Menir.
    
2.  **Pilot 2 (Write)**: "Creator - Narrative Conflict"
    - **Risk**: Medium (Scribe flow).
    - **Goal**: Prove functionality of the Governance Pipeline (App -> JSON Proposal -> CLI Apply).

---
*Signed, Antigravity Agent.*
