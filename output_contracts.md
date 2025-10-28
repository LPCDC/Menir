# Output Contracts (Menir v5.0 Core)

## 1. Propósito
Define como agentes externos podem interagir com o Menir.

## 2. Formato de saída padrão
Todo pacote externo relevante deve seguir:

BEGIN CONTRACT
{
  "timestamp_utc": "<UTC>",
  "origin": "<agent_name>",
  "intent": "<why>",
  "data": { "masked": true },
  "lgpd_masking": true,
  "allow_merge": false
}
END CONTRACT

- "lgpd_masking": sempre true.
- "allow_merge": false por padrão. Só vira true com aprovação explícita.

## 3. Heartbeat
Agentes externos podem mandar heartbeat:
BEGIN HEARTBEAT
{ "agent": "<agent_name>", "ts_utc": "<UTC>", "status": "alive" }
END HEARTBEAT

## 4. Proibições
- Proibido vazar chaves privadas, tokens, PAT GitHub, FERNET_KEY, PRIVATE_KEY.
- Proibido publicar nome civil completo de terceiros sem aprovação.

## 5. Auditoria
Cada merge externo gera linha em logs/zk_audit.jsonl com hash e timestamp.
Atualizado em 2025-10-28T13:18:22Z UTC.
