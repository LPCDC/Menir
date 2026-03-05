<div align="center">
  <h1>🏔️ Menir OS v5.2</h1>
  <p><strong>The Sovereign, Metacognitive Graph Intelligence & Personal Zero-Trust Engine.</strong></p>
  
  [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
  [![Platform: Neo4j](https://img.shields.io/badge/Graph_Engine-Neo4j-008cc1?logo=neo4j)](https://neo4j.com/)
  [![Language: Python 3.12](https://img.shields.io/badge/Language-Python_3.12-blue?logo=python)](https://python.org)
  [![Frontend: React TS](https://img.shields.io/badge/Tier_2-Vite_React_TS-61DAFB?logo=react)](https://reactjs.org)
</div>

<br>

> *"Data acts as a vector; logic acts as a scalar. Only the Graph Remembers."* — **The Menir Manifesto**

## 📖 O que é o Menir?

**Menir** não é um mero wrapper de LLM ou um script de automação. É uma **Inteligência em Grafo Soberana** hospedada localmente (`Neo4j`), desenhada sob arquitetura *Zero-Trust* e *Zero-Bloat*. Ele age como um "Segundo Cérebro" estrutural, forçando a fluidez da Inteligência Artificial (Google Gemini) a operar sob as regras estritas da matemática de grafos e validação rigorosa (Pydantic V2).

Ele nunca esquece, nunca alucina em dados críticos e impõe barreiras absolutas de isolamento de contexto (Galvanic Isolation). O Menir transforma o ruído da vida diária e acadêmica em uma ontologia roteável e persistente.

---

## ⚡ Potencial Real & Casos de Uso (Estudante & Pesquisador)

O ecossistema do Menir foi forjado para combater a amnésia digital, servindo perfeitamente para a **Vida Pessoal (Metacognição)**, pesquisas acadêmicas e gestão de vida fluida.

### 1. O "Segundo Cérebro" Metacognitivo (Gestão Acadêmica)
Ao invés de depender de bancos vetoriais voláteis ou blocos de notas perdidos, o Menir plota a sua vida acadêmica numa Ontologia Estruturada Neo4j.
- **Rápida Ingestão Epistêmica:** Você envia um paper PDF denso, anotações de aulas ou transcrições de áudio. O Menir extrai os conceitos e conecta matematicamente as ideias: `(:Concept {name: "Machine Learning"})-[:IS_FOUNDATIONAL_TO]->(:ResearchTopic {title: "Neural Networks"})`.
- **Rastreabilidade Não-Linear:** Meses depois, se você perguntar *"Quais autores eu li que discordam da teoria que estudei no semestre passado sobre redes convolucionais?"*, o Menir fará uma travessia no Grafo. O banco injetará toda a árvore bibliográfica histórica na janela de contexto do LLM. Ele tem empatia sintática e memória estrutural.

### 2. A Esteira de Absorção e Roteamento de Tarefas
O motor resolve o problema do "esquecimento de prazos" e caos de informações:
- **Exemplo de Uso:** Você insere um syllabus de curso ou um cronograma de TCC confuso.
- **Barreira de Alucinação (Pydantic):** O LLM nunca vai inventar uma data de entrega. Se a data extraída não cruzar matematicamente com a lógica de tempo do sistema, a barreira do `Pydantic` no Tier 1 destrói o payload. Apenas a verdade absoluta entra no Grafo temporal (`[:DUE_BY]`).

### 3. Tier 2: Painel Zero-Bloat (React + TypeScript)
Painel derivado diretamente das especificações matemáticas do Backend, garantindo total sinergia de ponta a ponta sem o "inchaço" comum de web apps modernos.
- Visualização pura dos prazos de estudos e do mapa de conhecimentos adquiridos.
- Render-blocking Security alimentado pela autenticação JWT, garantindo que suas notas pessoais e intelectuais permaneçam inacessíveis a terceiros.

---

## ⚙️ Paradigma Técnico

Menir preenche o abismo entre o abstrato (AI) e o concreto (Matemática de Grafos).

* **Graph Source of Truth:** `Neo4j` dita a realidade. Se a IA tenta inventar um autor já registrado com um nome ligeiramente diferente (ex: "J. Doe" vs "John Doe"), a camada Cypher a força de volta para o UUID conhecido via semântica de RAG vetorial (768-dimensões).
* **A.I. Engine:** Google `gemini-3.1-pro-preview` operando primariamente em `JSON_OBJECT` mode via MenirIntel. Geração assíncrona blindada (`asyncio.to_thread`).
* **Typing Rigoroso:** MyPy Static Typing e validação Pydantic estrita (`extra="forbid"`).
* **Segurança & Isolamento:** *Privacy by Design*. Capacidade de segregar completamente diferentes "Modos de Vida" (Estudos, Finanças Pessoais, Trabalho) através de "Tenants" estanques gerenciados por tenacidade no Contexto local do Python (`ContextVars`), sem vazamento cruzado de grafos.

---

## 📦 Inicialização do Nó (Quickstart)

Requerimentos: **Neo4j AuraDB** (ou local 5.x) e **Google Gemini API Key**. Node.js `v20+` para a Camada Cliente.

1. **Clone & Ambiente:**
   ```bash
   git clone https://github.com/LPCDC/Menir.git
   cd Menir
   # Defina NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD, GOOGLE_API_KEY no seu .env
   ```

2. **Gênese do Grafo (Bootstrap):**
   ```bash
   python -c "from src.v3.meta_cognition import MenirOntologyManager; import os; MenirOntologyManager(os.getenv('NEO4J_URI'), (os.getenv('NEO4J_USER'), os.getenv('NEO4J_PASSWORD') or '')).bootstrap_system_graph()"
   ```

3. **Ignite Tier 1 (Synapse & Control Plane):**
   ```bash
   python src/v3/core/menir_runner.py
   ```

4. **Ignite Tier 2 (Client SPA):**
   ```bash
   cd menir_web
   npm run dev
   ```

<BR>
<div align="center">
  <i>"No Menir, nada se perde. O Grafo a tudo assiste e a tudo lembra."</i>
</div>
