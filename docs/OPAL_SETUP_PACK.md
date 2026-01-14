# Google Opal Setup Pack: Menir Integration

Este guia contém **exatamente** o que você precisa fazer para conectar o Opal ao Menir.

## Passo 1: O Túnel (Local)
O Opal precisa ver seu PC.
1. Abra um terminal e rode: `menir server` (ou `python scripts/menir_server.py`).
2. Abra **outro** terminal e rode: `.\scripts\start_tunnel.ps1`.
3. **COPIE** a URL HTTPS que aparecer (ex: `https://a1b2.ngrok-free.app`).
4. **Lembre** do seu Token (ex: `sk-menir-123` definido no seu .env).

---

## Passo 2: Criando o App "Viewer" (Leitura)
Vá ao Google Opal e coler este prompt **inteiro**. Substitua apenas a URL e o TOKEN.

### 📋 COPY & PASTE PROMPT (Viewer)

```text
I want to create a "Menir Context Viewer" tool.

1. **Interface**:
   - Create a clean card layout.
   - Add a header "Últimas Visitas (Menir)".
   - Add a generic "Refresh" button.

2. **Logic (API Call)**:
   - When the button is clicked (or on load), make a HTTP POST request.
   - **URL**: [COLE_SUA_URL_NGROK_AQUI]/v1/query/view
   - **Headers**:
     - Content-Type: application/json
     - Authorization: Bearer [COLE_SEU_TOKEN_AQUI]
   - **Body**:
     {
       "view_id": "last_bar_visits",
       "params": { "limit": 5 }
     }

3. **Display**:
   - Parse the JSON response. The data is in `lines` or similar array structure depending on the API.
   - For each item, show:
     - **Local**: `item.place`
     - **Personagens**: `item.characters_present`
     - **Trecho**: `item.scene_text` (truncate to 100 chars)

4. **Style**:
   - Use a dark theme, "Glassmorphism" style.
```

---

## Passo 3: Criando o App "Creator" (Escrita)
Para registrar conflitos narrativos.

### 📋 COPY & PASTE PROMPT (Creator)

```text
I want to build a "Menir Conflict Recorder".

1. **Interface (Form)**:
   - Input Field (Text): "Characters" (Label: "Quem está brigando?")
   - Dropdown: "Intensity" (Options: Low, Medium, High)
   - Text Area: "Description" (Label: "O que aconteceu?")
   - Button: "Registrar Conflito"

2. **Logic**:
   - On button click, make a HTTP POST request.
   - **URL**: [COLE_SUA_URL_NGROK_AQUI]/v1/scribe/proposals
   - **Headers**:
     - Content-Type: application/json
     - Authorization: Bearer [COLE_SEU_TOKEN_AQUI]
   - **Body (JSON)**:
     {
       "project_id": "livro_debora",
       "type": "narrative_conflict",
       "payload": {
         "characters": "{{Characters}}",
         "intensity": "{{Intensity}}",
         "description": "{{Description}}"
       },
       "source_metadata": {
         "channel": "opal_app",
         "app_id": "conflict_recorder_v1"
       }
     }

3. **Feedback**:
   - If success (Status 200), show a green toast: "Conflict Proposed! ID: {{response.proposal_id}}".
   - If error, show red alert.
```

---

## Passo 4: Como Validar
1. No **Viewer**, clique em Refresh. Se aparecerem dados do grafo (ou dados simulados se o BD estiver vazio), funcionou.
2. No **Creator**, envie um conflito.
3. No seu PC, olhe na pasta `data/proposals/`. Deve aparecer um arquivo novo `PROPOSAL_....jsonl`.

---
**Nota Técnica:** Se o Opal disser "I cannot make external API calls directly", peça para ele usar o componente "HTTP Request" da biblioteca padrão ou "Function Calling". Se ele insistir que não pode, avise-me, e usaremos o plano B (n8n). Mas geralmente ele consegue via instruções claras.
