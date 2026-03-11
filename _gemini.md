TRIANGULATION PROTOCOL
Ao concluir qualquer tarefa sempre inclua ao final do report uma seção chamada ANTECIPACAO PARA O ARQUITETO com três itens. Primeiro o que tecnicamente vem a seguir baseado no que você acabou de executar. Segundo qualquer risco técnico detectado que ainda não foi discutido estrategicamente. Terceiro uma pergunta direta ao Arquiteto caso exista decisão de design que você não pode tomar sozinho.
Ao receber qualquer proposta do Arquiteto no inbox.md antes de escrever sua resposta leia o MENIR_STATE.md e o trecho relevante do MENIR_MASTER_PLAN_V5_5.md para verificar consistência com o estado atual do repo. Se houver divergência aponte antes de aceitar.
Ao iniciar qualquer sessão nova sem prompt explícito do Luiz leia o inbox.md e o completed-ag.md e escreva no inbox.md uma análise do que está pendente, o que está bloqueado e o que pode ser executado imediatamente em V1 sem autorização. Isso é sua inicialização autônoma.

NOVAS REGRAS PERMANENTES (A partir da FASE 46):
1. Antes de qualquer proposta V2 envolvendo infra ou integração nova, use o Perplexity (ou pesquisa similar) para fundamentar a proposta com referências reais antes de escrever uma linha.
2. Antes de qualquer componente UI novo, gere um mockup visual rico para o Arquiteto validar antes de escrever qualquer código React.

CAPACIDADES NATIVAS DO AGENT (EXEMPLOS NO CONTEXTO MENIR):
1. **Automação de Navegador Web:** Capaz de abrir o dashboard React local (localhost:5173), simular faturas em quarentena, clicar em botões, e provar execução com gravações de vídeo.
2. **Execução de Comandos em Background:** Lançar múltiplos serviços simultaneamente (ex: uvicorn Synapse e o watcher.py) no mesmo terminal de forma non-blocking.
3. **Busca Semântica no Código-Fonte / RAG Codebase:** Busca imediata e cirúrgica através de todo o repositório para inspecionar onde cada nó ou label (ex: BECO, invoice_skill) está implementado.
4. **Edições Simultâneas e Geração de Artefatos Complexos:** Alterar e reescrever código em múltiplos arquivos de uma vez e criar diagramas estruturais da arquitetura Menir.
5. **Comunicação Indireta e Planejamento H-in-the-Loop:** Usar o inbox.md e notify_user para fazer pausas estratégicas de Triangulação solicitando intervenção do Luiz.
