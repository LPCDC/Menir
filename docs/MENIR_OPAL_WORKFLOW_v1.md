# Menir x Google Opal: The "Liquid Interface" Workflow

## The Design Philosophy
**Menir is the Mountain (Immovable). Opal is the River (Fluid).**

- **Menir (Local "Headless" OS)**:
    - Holds the **Truth** (Neo4j Graph).
    - Holds the **Governance** (Scribe/Proposals).
    - Holds the **Compute** (Python Logic/Agents).
    - **Change**: Needs to expose a standardized **API** (Menir Server).

- **Google Opal (The "Liquid" UI)**:
    - You never "code" a UI for Menir anymore.
    - You **ask** for a UI.
    - Opposed to a monolithic "Menir Dashboard", you generate micro-apps for specific moments.

## The New Workflow

### 1. The Setup (One-Time)
- **Menir side**: Run `menir monitor --api` (starts FastAPI + Tunnel/Ngrok/Tailscale).
- **Opal side**: Configure a "Menir Connector" (Base URL + Auth Token).

### 2. The Development Loop (Daily)

**Scenario A: The "Viewer" (Read)**
> *User:* "Estou escrevendo uma cena no bar. Preciso ver quem estava lá na última vez e o que eles beberam."

**Old Way**:
- User abre Neo4j Browser -> Escreve Cypher.
- Ou: User pede ao chat para escrever script Python.

**New Opal Way**:
- User → Opal: "Crie um app rápido que mostre os últimos 5 personagens que visitaram o 'Bar do Zé' e seus estados."
- Opal: Gera a UI.
- App: Chama `GET /menir/query?q=MATCH...` (ou endpoint semântico).
- **Result**: Um card visual imediato no celular/browser. Terminou? Lixo.

**Scenario B: The "Creator" (Write via Logic)**
> *User:* "Tive uma ideia. A Débora vai brigar com o pai por causa do dinheiro."

**Old Way**:
- User edita arquivo de texto -> Roda script de ingestão.

**New Opal Way**:
- User → Opal: "Quero um form para registrar um Conflito Narrativo."
- Opal: Cria form com campos (Personagens, Motivo, Intensidade).
- User: Preenche e envia.
- App: Chama `POST /menir/scribe/proposal` com JSON.
- **Menir**:
    - Recebe o JSON.
    - Scribe valida (Privacy/Logic).
    - Gera um **Proposal** no sistema de arquivos.
    - Notifica o User: "Proposal #123 created. Run `menir apply` to confirm."

### 3. Architecture Changes Required

To enable this, Menir must evolve from "Scripts" to "Server":

1.  **Menir API Gateway (`scripts/menir_server.py`)**:
    - Endpoints:
        - `/health`: Status.
        - `/query/cypher` (Com proteção): Read-only queries.
        - `/scribe/ingest`: Receives raw text/JSON.
        - `/context/search`: RAG endpoint (Vector search).
2.  **Auth Strategy**:
    - Simples Token Bearer (compartilhado com o Opal).
3.  **Governance Layer**:
    - NENHUMA escrita direta via API. Tudo vira `Proposal` para ser auditado.

## Summary: How this Optimization helps YOU
1.  **Zero UI Debt**: Você não mantém frontends. O Google mantém.
2.  **Focus on Logic**: Você só codifica as regras do Universo (Ontologia, Scribe), não botões e CSS.
3.  **Mobile Ready**: Apps do Opal funcionam no celular nativamente. Você "conversa" com o Menir de qualquer lugar.
