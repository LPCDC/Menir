# Menir OS

> **Um Sistema Operacional Cognitivo que materializa, conecta e amplifica a sua inteligência através de um Grafo de Conhecimento privado.**

O Menir não é apenas mais um aplicativo de produtividade orgânica — é um arquétipo digital. Ele não destrói os dados que você joga nele em caixas de chat esquecidas. Em vez disso, o Menir escuta, lê, conecta e desenha um ecossistema visual intransponível do que você e sua empresa sabem. 

Do pensamento complexo no chuveiro até a reconciliação fiduciária suíça de dezenas de faturas: o Menir roteia a informação para o lugar certo, transformando o silêncio dos seus arquivos numa malha viva de insights.

---

## Para quem o Menir é construído?

O sistema possui uma arquitetura _Multi-Tenant_ isolada, que permite que o motor cognitivo abrace realidades drasticamente diferentes debaixo do mesmo teto.

### 🏢 1. Fiduciárias, Gestão e Backoffice (ex: BECO)
Para empresas de contabilidade e operações financeiras de alta precisão. O Menir ingere caixas de entrada lotadas de faturas brutas, PDFs suíços complexos e extratos bancários CAMT.053. Ele valida as regras da máfia da matemática fiduciária (como módulos UID suíços e alíquotas de TVA enraizadas), perdoa a entropia gerada pelo mundo real (gorjetas ou descritivos manuais soltos) e converte o caos em um grafo auditável de Fornecedores, Faturas e Reconciliações, pronto para ingestões seguras em ERPs como o Crésus.
*Nunca mais perca uma fatura para a desorganização. Confiança matemática com velocidade de IA.*

### 🎙️ 2. Criadores de Conteúdo, Speakers e Visionários
Para os curiosos crônicos, arquitetos de ideias e executivos. Quando você grava um áudio capturando um lampejo de ideia ou rascunha um Insight em texto, o **Menir Capture** desce as entranhas da sua lógica. Ele identifica os atores, os temas, as teses e os projetos ocultos ali. Depois, cruza esses nós com pensamentos seus de dois anos atrás. O que era um áudio solto vira uma conexão imediata entre um Livro, um Conceito e a sua próxima Palestra Magna.
*Amplifique a sua retenção. O Menir é o curador silencioso da sua mente aberta.*

### 🚀 3. Profissionais Independentes e Arquitetos de Software
Para quem respira complexidade. O Menir integra seu banco de dados, repos de código e documentação local com a capacidade implacável dos Agentes Inteligentes. Você conta com um auditor e desenvolvedor (o *Antigravity*) operando lado a lado com a base de dados. Solidez total guiada unicamente pelas suas decisões como Arquiteto do projeto.
*Menos debbugging. Mais tempo construindo a visão.*

---

## Possibilidades Ilimitadas

* **Roteamento Inteligente:** Faça upload de qualquer coisa. Se for fatura, a lógica contábil domina. Se for texto filosófico, a ontologia pessoal conecta.
* **Vector Search Semântico Próprio:** Vá além de buscar palavras-chave cegas. Pergunte "Quais insights eu tive sobre resiliência perto de rios?" e o Menir recupera conexões abstratas no seu grafo visual, ligando pensamentos e intuições.
* **Isolamento Galvânico:** Seus insights de vida privada jamais cruzarão caminhos ou gerarão ruído cognitivo nos dados contábeis da sua fiduciária.
* **Interativo & Resiliente:** Você não conversa com um bot. Você aciona um Ecossistema que manipula, altera e salva contexto e memória durável em um banco OGM moderno (Neo4j). 

---

## Como Iniciar a Operação

O ecossistema é ativado através de um Launcher conversacional focado em terminal e em transições Web nativas. 

1. Tenha o **Docker** rodando seu banco grafo de preferência (Neo4j) e obtenha sua chave primária do **Google Gemini** (V3 API).
2. Configure seu cenário isolado de chaves e _Tenants_ no seu arquivo oculto blindado `.env`.
3. Dispare o Gatilho do Sistema pelo terminal usando `python launcher.py`.

A partir daí, você está no controle do Painel de Bordo do Córtex. 

*Experimente conectar dois mundos hoje mesmo.*

---
_Anotação Técnica para Desenvolvedores (V0):_
_O núcleo profundo assíncrono repousa na integração do Driver `Neo4j` OGM + Pydantic estrito + `google.genai` SDK V3._
_Toda iteração e extração é submetida a Schemas Rigorosos com limites exatos (Pydantic), blindada por `Tenacity` e guardada através das trilhas de `ContextVars` asyncs isoladas._
