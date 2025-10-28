Set-Content -Path ".\reports\risk_report.md" -Encoding UTF8 -Value @"
# Risk Report - Menir v5.0

## vermelho (Critical)
- **Banking Risk (Itaú)**: Early termination (Cl. 10) - 53% by 13/11/2025. Action: Escalate N3 if no protocol in 48h.
- **Credential Leak**: Drive/Gmail placeholders - 80% exposure. Action: Rotate secrets.

## amarelo (Attention)
- **Condo Assembly (Tivoli/Iberê)**: Stage2 delay - 40% rework. Action: Auto-ping Bia.
- **Performance (GPU)**: RTX 4070 Ti >86°C - 25% throttle. Action: Alert on bootnow.

## verde (In Progress)
- **Neo4j Indexing**: 47 nodes - 90% stable. Action: Incremental sync.
- **GitHub Sync**: Push OK - 100% audit. Action: Hourly `run_all.sh`.

**Last Update**: 2025-10-27T17:30:00-03:00

<!-- requires_push_agent: true -->
"@
