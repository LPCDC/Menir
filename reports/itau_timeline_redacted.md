New-Item -ItemType Directory -Force -Path ".\reports" | Out-Null
Set-Content -Path ".\reports\itau_timeline_redacted.md" -Encoding UTF8 -Value @"
# Itaú Timeline - Redacted (LGPD Compliant)

## Key Events (Initials Only)

- **T0**: Commercial origination (T/J) - CET variations.
- **T1**: Contract migration (M/V) - Proposal reopen/close.
- **T2**: Vias sent to e-Notariado.
- **T3**: Client signature (2025-09-29). Bank signatures pending.
- **T4**: Post-signature email - Request protocol/registration, CET, credit forecast.
- **T5**: Expected: SRI prenotation, resource release (D+3 electronic / D+10 physical).
- **T6**: Dossiê preparation - CET, logs, recordings, "tied sale" case (E).

## Risks
- **Registration Limit**: 45 days (Cl. 1.1) - Monitor.
- **Release SLA**: 3/10 business days post-registration.
- **CET Compliance**: Spreadsheet mandatory (Res. CMN 4.197/2013).

**Last Update**: 2025-10-27T17:30:00-03:00

<!-- requires_push_agent: true -->
"@
