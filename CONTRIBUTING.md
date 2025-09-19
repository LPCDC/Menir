# Como Contribuir para o Training U

Obrigado por se interessar! O Training U é um playground pra automatizar o Menir — foco em persistência, gatilhos e menos dor de cabeça manual. Contribuições são bem-vindas, mas vamos manter simples: teste local, documente, e automatize onde der.

## Fluxo de Trabalho

1. **Fork e Clone**  
   - Fork o repo no GitHub.  
   - Clone local: `git clone <seu-fork-url>`.  
   - Crie branch: `git checkout -b feat/nome-da-sua-feature` (ou `fix/bug-especifico`).

2. **Desenvolva e Teste**  
   - Faça suas mudanças — adicione um gatilho novo? Um workflow? Um seed Cypher?  
   - Teste local: Rode scripts como `scripts/test_triggers.sh` ou aplique Cypher no Aura.  
   - Verifique logs: Atualize `checkpoint.md` ou adicione linha no `menir_meta_log.jsonl` com o que rolou (ex:  
     ```json
     {"date":"YYYY-MM-DD", "evento":"Novo gatilho X", "impacto":"Testado OK"}
     ```  
   )  
   - Rode linters se aplicável (adicione um no futuro se quiser).

3. **Commit**  
   - Mensagens claras: Use prefixos como `feat:`, `fix:`, `docs:`, `refactor:`, `trigger:`.  
   - Exemplo: `feat: add auto-commitlog to schema`.  
   - Commit: `git add . && git commit -m "sua-mensagem"`.

4. **Push e Pull Request**  
   - Push: `git push origin feat/sua-feature`.  
   - Abra Pull Request no repo principal: descreva o que mudou, por quê, e como testar (link pro checkpoint ou log).  
   - Mencione issues se relacionado (ex: "Closes #5").

5. **Revisão e Merge**  
   - Revisor checa: Funciona? Idempotente? Não quebra Aura?  
   - Merge via GitHub — squash se commits bagunçados.  
   - Pós-merge: workflow roda auto (schema / ingest / test).

## Dicas Rápidas

- **Gatilhos Novos**: adicione em `seeds/gatilhos_seed.cypher` com `MERGE`. Teste com `scripts/trigger_test.sh "Gato Mia"`.  
- **Automação**: qualquer workflow novo vai em `.github/workflows/`. Teste com `act` local se tiver.  
- **Logs/Reflexões**: sempre toque `menir_meta_log.jsonl` — é o coração do projeto.  
- **Erros Comuns**: schema não idempotente? Use `MERGE`. Ingest com `file:///?`? Mude pra HTTPS/raw.  
- **Perguntas?** Abra issue ou ping no chat — mas teste primeiro.

---

Mantenha o espírito: automatize ou morre. 😼
