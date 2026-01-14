# Menir Tools Directory

This directory contains data normalization and transformation tools for the Menir pipeline.

## TODO: Tools to Implement

### Email Processing
- **`itau_email_to_jsonl.py`**
  - Input: Raw .mbox or .eml files from `data/itau/email/raw/`
  - Output: Normalized JSONL to `data/itau/email/normalized/itau_emails.jsonl`
  - Schema: `{id, from, to, cc, subject, body, date, attachments[]}`

### Extrato (Bank Statement) Processing
- **`itau_extrato_to_jsonl.py`**
  - Input: Raw PDF statements from `data/itau/extratos/raw/`
  - Output: Normalized JSONL to `data/itau/extratos/normalized/extratos.jsonl`
  - Schema: `{id, account, date, transactions[{date, description, amount, balance}]}`

### WhatsApp Processing
- **`whatsapp_txt_to_jsonl.py`**
  - Input: Raw WhatsApp export text from `data/itau/whatsapp/raw/`
  - Output: Normalized JSONL to `data/itau/whatsapp/normalized/whatsapp_messages.jsonl`
  - Schema: `{id, timestamp, sender, message, media[]}`

### Document Manifest Generation
- **`docs_to_manifest.py`**
  - Input: Various documents from `data/itau/docs/`
  - Output: Manifest JSON to `data/itau/docs/itau_docs_manifest.json`
  - Schema: `{documents: [{id, path, type, size, hash, metadata}]}`

## Implementation Priority

1. Email processing (highest value for legal cases)
2. Extrato processing (financial transaction tracking)
3. Document manifest (baseline for all document types)
4. WhatsApp processing (messaging context)

## Dependencies

Common dependencies for all tools:
- `python3.12+`
- `jsonlines` (for JSONL output)
- `hashlib` (for content hashing)
- `pathlib` (for file handling)

Tool-specific:
- Email: `email`, `mailbox` (stdlib)
- PDF: `pdfplumber` or `PyPDF2`
- WhatsApp: regex parsing (stdlib)
