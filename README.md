# Menir – Boot v5.0
Repositório: LPCDC/Menir · Branch: release/menir-aio-v5.0-boot

## Propósito
Este branch mantém o **núcleo de inicialização padrão** do Menir (sem dependência local).  
Serve para ativar o sistema em ambiente remoto, testar integração com Neo4j/Aura e sincronizar logs via GitHub Actions.

## Estrutura
- `boot.py` / `bootnow.ps1` — inicializadores principais  
- `logs/` — trilhas de auditoria (`zk_audit.jsonl`)  
- `tools/` — scripts de suporte (verificação, ingest, push)  
- `config/` — arquivos `.env` e políticas LGPD  

## Como usar
```bash
git clone https://github.com/LPCDC/Menir.git
cd Menir
git checkout release/menir-aio-v5.0-boot
conda activate menir
python boot.py --mode remote