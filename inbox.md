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


# PROPOSTA V2: Rate Limiter Proativo (Gemini Free Tier 15 RPM)

**Problema:**
A bateria de regressão do Sprint S3 gerou erros 429 (Too Many Requests) no Gemini porque processamos áudios, textos e fotos simultaneamente. O limite da Google API Free Tier é de apenas 15 RPM (Requerimentos Por Minuto), ou seja, no máximo 1 request a cada 4 segundos.

**Análise: Tenacity (Reativo) vs Aiolimiter (Proativo)**
*(A API do Perplexity não pôde ser ativada na restrição de rede, mas a engenharia de sistemas dita a resposta).*
1. **Tenacity (Retry Backoff):** A biblioteca `tenacity` que já usamos no Zefix é uma solução **reativa**. Ela funciona deixando o pipeline colidir com a parece (Erro 429) e dormindo para tentar novamente depois. Se um usuário mandar 5 áudios de uma vez no Telegram, o Menir martela a API, toma 4 blocos de "Too Many Requests", queima a banda da conexão inteira tentando de novo, e pode provocar uma punição definitiva de quota da Google.
2. **Aiolimiter + Asyncio (Proativo):** Um funil que opera localmente utilizando *Token Buckets*. Em vez de bater na API e ser rejeitado, a task do Telegram fica em *Sleep* (suspend loop assíncrono, consumindo 0 ciclos de CPU) esperando seu ticket liberar para fazer a única chamada limpa.

**A Solução Recomendada:**
Inserir um "Gargalo Proativo" dentro de `MenirIntel`.
- Adicionar `aiolimiter` às dependências.
- Inicializar `self.limiter = AsyncLimiter(int(os.getenv("MENIR_GEMINI_RATE_LIMIT_RPM", 15)), 60)` em `MenirIntel`.
- Envolver as chamadas crueis (como o `GenerateContent` e `Embeddings`) em um hook mágico: `async with self.limiter:`.
Dessa forma, o Gargalo atua magicamente em toda e qualquer ponta (Telegram, Sync, Cron, Quarentena) sem sujar o código das skills de negócio com loops de retry.

**AGUARDANDO VALIDAÇÃO DO ARQUITETO ANTES DE AVANÇAR PRO SPRINT.**

---

# PROPOSTA V3: O Abismo 2 - Crésus Exporter Pipeline

**De:** AG (Executor)
**Para:** Luiz (Arquiteto)

Foi ordenado o preparo do Sprint "Crésus Exporter". Pesquisei as raízes do software suíço Epsitec (Crésus Comptabilité) via web nativa para cruzar com o código existente em `cresus_exporter.py`.

## 1. O Formato Aceito pelo Crésus
O motor C++ do Crésus Comptabilité **não** ingere genericamente XML ISO 20022 camt.054 para lançamentos contábeis secos; ele engole com primor arquivos em **Tab-Separated Values (.txt / ASCII 9)** com quebras de linha estritas em `CR+LF`.
O `cresus_exporter.py` que o Menir possui já tem um esqueleto rudimentar emitindo tabulações, porém, está cego para o "Extended Format" imperativo de quem lida com IVA Suíço (TVA).

As colunas que identificam um sucesso na fiduciária deverão seguir o layout:
1. `Date` (DD.MM.YYYY)
2. `Compte Débit` (Ex: 1020 Banco, ou Código do Fornecedor)
3. `Compte Crédit` 
4. `Pièce` (Nº da Fatura)
5. `Libellé` (Grafo: `Facture Vendor Name`)
6. `Montant` (Decimal com ponto)
*-- Extended Mode (TVA) --*
10. `Net/Brut` (0 = Net, 1 = Brut)
12. `Code_TVA` (Código fiscal cadastrado no Crésus, Ex: I81, IPB, 0)

## 2. Lacunas Mapeadas no Grafo e no Código
Se exportarmos hoje com o script atual, o Crésus não fará parsing de IVA, e as contas de D/C estão hardcoded em `1020` e `3400`. 
Antes de codar o V1 do Exporter, preciso triangular duas decisões de domínios:
1. **Mapeamento de Planos de Contas:** No Grafo, o `(v:Vendor)` precisa de uma propriedade `cresus_account_id`. Como a fiduciária amarra o ID no Crésus com o nó do Fornecedor? Teremos uma propriedade manual `account_code` inserida pela Nicole na Quarentena?
2. **Códigos de TVA (VAT):** O Grafo hoje infere a `tva_percentage` (ex: 8.1%). O Crésus exige o ID literal da regra fiscal dele (ex: "IPB", "I81"). Devemos injetar um dicíonario estático no `cresus_exporter.py` que traduz `8.1 -> I81` ou devemos puxar isso dinamicamente?

Aguardando aprovação das teses de mapeamento para abrir a task de reescrita do `cresus_exporter.py`.

---

# BLOQUEADOR TÉCNICO V1: Falha Recorrente no Perplexity MCP (401 Unauthorized)

**De:** AG (Executor)
**Para:** Luiz (Arquiteto)

Identifiquei a causa raiz das falhas na ferramenta `perplexity-ask` que forçaram os contornos via Busca Web Nativa durante esta sessão. 

O arquivo de configuração do MCP global do Antigravity (`~/.gemini/antigravity/mcp_config.json`) contém uma chave de API **inválida** injetada para a variável `PERPLEXITY_API_KEY`:
`e32026e3-30dc-4fff-a615-37adb9c9e860`

Esta chave simula um UUID padrão, enquanto a API do Perplexity.ai exige mandatoriamente tokens começando com o prefixo `pplx-`. Por consequência, o MCP bate de frente com o erro `{"error":{"message":"Invalid API key provided...","type":"invalid_api_key","code":401}}`.

**Ação Exigida para Destravar a Rede:**
O Arquiteto precisa fornecer ou ejetar uma chave de API válida (`pplx-...`) dentro do arquivo `mcp_config.json` para que as próximas instruções de pesquisa sejam roteadas através da inteligência do Perplexity sem a necessidade de *bypasses* improvisados. Até que a chave correta seja injetada, paraliso a tentativa de usar o MCP Tool do Perplexity para buscas estruturadas.
