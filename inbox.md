# PROPOSTA V2: Dashboard Quarantine Loop (HITL)

**De:** AG (Executor)
**Para:** Claude / Luiz (Arquiteto)
**Fase:** 46 - Step 2

---

## 1. PESQUISA: Padrões HITL em Document Pipelines (React + FastAPI)
*Nota: A API do Perplexity e o Web Search retornaram erros de autorização/conexão durante a consulta, portanto esta síntese baseia-se em padrões robustos da indústria e arquiteturas state-of-the-art para HITL (Human-In-The-Loop).*

**Painpoints da Indústria e Soluções (Best Practices):**
1. **Fadiga Visual (Cognitive Load):** 
   - *Erro comum:* Mostrar campos não relacionados ao PDF de forma dispersa.
   - *Padrão:* **Split-Screen UI** (PDF viewer à esquerda, formulário vertical alinhado à direita). Sincronia de scroll/destaque (bounding boxes no PDF atreladas ao campo em foco no input).
2. **Contexto de Retenção (Provenance):**
   - *Padrão:* Todo campo editado deve rastrear o valor original do LLM vs. o valor humano. O endpoint FastAPI (`PATCH /documents/{uid}/correct`) recebe os campos corrigidos e marca `is_human_corrected = True`.
3. **Ações Decisivas (Aprovar, Rejeitar, Reinjetar):**
   - *Padrão:* Diferenciar claramente "Save Draft" vs "Aprovar e Enviar para Pipeline (Reinjetar)". Ações de reinjeção devem ser destrutivas/transacionais na UI para evitar double-submission.
4. **Resiliência Backend (FastAPI):**
   - *Padrão arquitetural:* O FastAPI expõe `/quarantine/pending` (polling ou WebSocket) e `/quarantine/resolve/{doc_id}`. O corpo da resolução dita se o nó do Grafo no Neo4j deve ser atualizado (`MERGE/SET`) e despachado adiante ou abortado.

---

## 2. MOCKUP VISUAL ESTRUTURAL (Dashboard Quarentena)

O dashboard focará na **fiduciária (BECO/Nicole)**, com uma linguagem visual séria, clean, e densa.

### Layout Geral (Viewport 1920x1080)
```mermaid
graph TD
    subgraph UI_Header [Top Navbar - Fiduciário Escuro]
        L[Logo Menir] --- T[Quarentena de Documentos] --- B[🔴 3 Aguardando Revisão]
    end
    
    subgraph Dashboard_Core [Main Split-Screen View]
         subgraph Left_Panel [65% Width: Document Viewer]
             PDF(PDF Viewer Nativo / Imagem com Zoom)
             PDF --- Alert[Motivo da Quarentena: 'Total Mismatch', 'Missing TVA']
         end
         
         subgraph Right_Panel [35% Width: Extraction & Editing]
             H[Dados Extraídos]
             H --- I1[Fornecedor: Swisscom ⚠️ 'Não encontrado no Zefix']
             H --- I2[Data Emissão: 12.10.2025]
             H --- I3[Moeda: CHF]
             H --- I4[TVA: 8.1%]
             H --- I5[Total Bruto: 110.50 (Editável)]
             
             I5 --- Actions[Ações de Resolução]
             Actions --- Btn1("[ CORRIGIR E REINJETAR ] (Primário, Verde Escuro)")
             Actions --- Btn2("[ REJEITAR DOCUMENTO ] (Secundário, Vermelho Tênue)")
         end
    end
```

### Componentização em React (Proposta)
- **`<QuarantineDashboard />`**: View principal.
- **`<PdfSplitViewer file={doc.url} quarantineReason={doc.reason} />`**: Lado esquerdo. Trava o scroll vertical independentemente do formulário.
- **`<CorrectionForm initialData={doc.extracted} />`**: Formulário à direita, utilizando `react-hook-form` e `zod` para schema matching idêntico ao backend. Inputs de erro têm bordas laranjas (warning), inputs corrigidos ficam com borda azul para indicar edição humana.

### Contrato Backend (FastAPI)
- `GET /api/v3/quarantine/queue`: Retorna lista de `{uid, filename, reason, inferred_data}`.
- `POST /api/v3/quarantine/resolve/{uid}`: Redireciona de volta para a máquina de estados.
  Payload:
  ```json
  {
      "action": "reinject", // ou "reject"
      "corrected_fields": {
          "total_amount": 120.00
      }
  }
  ```

---
**AGUARDANDO VALIDAÇÃO DO ARQUITETO:**
1. O split-screen clássico (65/35) está de acordo com a sobriedade esperada?
2. Posso prosseguir com a implementação do componente React (`QuarantineView.tsx`) e os dois endpoints no FastAPI em `src/v3/core/synapse.py`?
