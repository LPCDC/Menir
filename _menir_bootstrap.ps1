# gera arquivos canônicos do Menir e auditoria inicial
$tsUtc = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
$stateJson = @"
{
  "meta": {
    "boot_version": "v5.0",
    "branch_canonico": "release/menir-aio-v5.0-boot-local",
    "repo": "LPCDC/Menir",
    "timestamp_utc": "$tsUtc",
    "next_deadline": "2025-10-29T19:30:00-03:00"
  },
  "tasks": [
    "gerar Cypher incremental para novas Transacao Ita\u00FA",
    "gerar timeline Ita\u00FA limpa para assembleia sem sobrenomes completos"
  ],
  "schema": {
    "neo4j_labels_added": ["EventoBanco","Transacao"],
    "neo4j_rels_added": ["REFERE_A","ENVOLVENDO"],
    "evento_banco_anchor_id": "REG-2025-10-001",
    "conta_anchor_id": "15220012",
    "projeto_anchor_slug": "Itau"
  },
  "slowdown_guard": {
    "gpu_temp_c_max": 87,
    "latency_ms_max": 5000,
    "char_count_max": 90000
  },
  "push_policy": "manual_approval_required",
  "risk_notes": {
    "itau": "risco de rescis\u00E3o antecipada contratual ~53 antes de 2025-11-13 se n\u00E3o houver protocolo formal em 48h",
    "condominio": "assembleia Tivoli retrofit t\u00E9rreo e s\u00EDndico profissional. risco de retrabalho ~40%",
    "gpu": "RTX 4070 Ti aproximando 87 C. risco de throttle ~25%",
    "credencial": "exposi\u00E7\u00E3o de credencial \u00E9 risco alto. girar token se vazar"
  },
  "itau_context": "Linha do tempo banc\u00E1ria e efeito patrimonial ap\u00F3s assinatura 2025-09-29. Banco interno ainda n\u00E3o liberou cr\u00E9dito. Pedido formal de protocolo/registro, planilha CET, previs\u00E3o libera\u00E7\u00E3o p\u00F3s-registro.",
  "assembly_context": "Condom\u00EDnio Tivoli. Pauta retrofit t\u00E9rreo e s\u00EDndico profissional. Prazo interno Stage2.",
  "zk_log_digest": [
    {
      "hash": "SHA256:PLACEHOLDER",
      "action": "timeline_itau_generated",
      "ts_brt": "2025-10-27T20:40:00-03:00
