import sys
import os

# --- FIX: ADICIONAR PASTA 'SRC' AO PATH ---
# Isso ensina o Runner a encontrar menir_intel e menir_bridge dentro de src/
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

import time
import io
import hashlib
import re
import random
import shutil
from datetime import datetime
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# Agora os imports funcionam:
from menir_intel import analyze_document_content
from menir_bridge import execute_bridge
from ingest import extract_text

# --- CONFIGURAÇÃO ---
SCOPES = [
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/spreadsheets'
]
INBOX_NAME = "Menir_Inbox"
ARCHIVE_NAME = "Menir_Archive"
QUARANTINE_NAME = "Menir_Quarantine"
SHEET_NAME = "Menir_Triage_Master"
TEMP_DIR = "tmp_processing"

# --- UTILITÁRIOS ---
def calculate_local_md5(filepath):
    """Calcula MD5 localmente se a API falhar em entregar."""
    hash_md5 = hashlib.md5()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def sanitize_text_lgpd(text):
    """LGPD GATE: Mascara PII básico antes de enviar para a IA."""
    if not text: return ""
    text = re.sub(r'\b\d{3}\.\d{3}\.\d{3}-\d{2}\b', '[CPF_MASKED]', text)
    text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL_MASKED]', text)
    text = re.sub(r'\(\d{2}\)\s\d{4,5}-\d{4}', '[PHONE_MASKED]', text)
    return text

def exponential_backoff(attempt):
    """Dorme progressivamente em caso de erro de API."""
    sleep_time = min(300, (2 ** attempt) + random.uniform(0, 1))
    print(f"⚠️ API Limit/Erro (Tentativa {attempt}). Dormindo {sleep_time:.1f}s...")
    time.sleep(sleep_time)

# --- AUTH & SETUP ---
def get_services():
    creds = None
    if os.path.exists('token.json'):
        try:
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        except:
            print("⚠️ Token inválido. Recriando...")
            creds = None

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except:
                creds = None 
        
        if not creds:
            if os.path.exists('token.json'): os.remove('token.json')
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
            
    return (build('drive', 'v3', credentials=creds), 
            build('sheets', 'v4', credentials=creds))

def setup_structure(drive, sheet):
    folders = {}
    for name in [INBOX_NAME, ARCHIVE_NAME, QUARANTINE_NAME]:
        q = f"mimeType='application/vnd.google-apps.folder' and name='{name}' and trashed=false"
        res = drive.files().list(q=q, fields="files(id)").execute()
        items = res.get('files', [])
        if not items:
            print(f"📂 Criando pasta: {name}")
            meta = {'name': name, 'mimeType': 'application/vnd.google-apps.folder'}
            created = drive.files().create(body=meta, fields='id').execute()
            folders[name] = created['id']
        else:
            folders[name] = items[0]['id']
            
    sheet_id = None
    res = drive.files().list(q=f"name='{SHEET_NAME}' and mimeType='application/vnd.google-apps.spreadsheet'", fields="files(id)").execute()
    items = res.get('files', [])
    if not items:
        print(f"📊 Criando Planilha Mestra: {SHEET_NAME}")
        meta = {'properties': {'title': SHEET_NAME}}
        ss = sheet.spreadsheets().create(body=meta).execute()
        sheet_id = ss['spreadsheetId']
        header = [['TIMESTAMP', 'FILE_NAME', 'FILE_ID', 'MD5_HASH', 'STATUS', 'NEO4J_LOG']]
        sheet.spreadsheets().values().update(
            spreadsheetId=sheet_id, range="A1", 
            valueInputOption="RAW", body={'values': header}
        ).execute()
    else:
        sheet_id = items[0]['id']
        
    return folders, sheet_id

# --- CORE LOGIC ---
def get_processed_hashes(sheet, sheet_id):
    """Carrega cache de hashes processados."""
    try:
        result = sheet.spreadsheets().values().get(
            spreadsheetId=sheet_id, range="D:D").execute()
        return set([row[0] for row in result.get('values', []) if row])
    except Exception:
        return set()

def log_audit(sheet, sheet_id, data):
    row = [[
        datetime.now().isoformat(),
        data['name'],
        data['id'],
        data['hash'],
        data['status'],
        data['log'][:4000] 
    ]]
    try:
        sheet.spreadsheets().values().append(
            spreadsheetId=sheet_id, range="A:A",
            valueInputOption="USER_ENTERED", body={'values': row}
        ).execute()
    except HttpError as e:
        print(f"⚠️ Erro ao auditar na planilha: {e}")

def safe_download(drive, file_id):
    if not os.path.exists(TEMP_DIR): os.makedirs(TEMP_DIR)
    local_path = os.path.join(TEMP_DIR, f"{file_id}.pdf")
    
    request = drive.files().get_media(fileId=file_id)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
    
    with open(local_path, "wb") as f:
        f.write(fh.getbuffer())
    return local_path

def main_loop():
    print("🛡️ MENIR RUNNER V2.2 (COM SRC PATH FIX) - INICIANDO...")
    
    # 1. Autenticação & Setup
    drive_service, sheet_service = get_services()
    folders, sheet_id = setup_structure(drive_service, sheet_service)
    inbox_id = folders[INBOX_NAME]
    archive_id = folders[ARCHIVE_NAME]
    quarantine_id = folders[QUARANTINE_NAME]
    
    print(f"🔭 Inbox: ...{inbox_id[-5:]}")
    print(f"📊 Sheet: ...{sheet_id[-5:]}")
    print("🚀 SISTEMA PRONTO. Aguardando arquivos na Inbox do Drive...")
    
    errors_consecutive = 0
    processed_hashes = get_processed_hashes(sheet_service, sheet_id)

    while True:
        try:
            # 2. Busca PDFs
            q = f"'{inbox_id}' in parents and trashed=false and mimeType='application/pdf'"
            results = drive_service.files().list(q=q, fields="files(id, name, md5Checksum)").execute()
            items = results.get('files', [])
            
            errors_consecutive = 0 

            if not items:
                time.sleep(10)
                continue

            for item in items:
                f_id, f_name = item['id'], item['name']
                drive_hash = item.get('md5Checksum')
                local_path = None
                
                print(f"\n🔎 Arquivo Detectado: {f_name}")

                try:
                    # 3. Download & Hash Local (Fallback)
                    local_path = safe_download(drive_service, f_id)
                    
                    if drive_hash:
                        final_hash = drive_hash
                    else:
                        print("   ⚠️ Hash API ausente. Calculando localmente...")
                        final_hash = calculate_local_md5(local_path)
                    
                    # 4. Check Idempotência (Memória)
                    if final_hash in processed_hashes:
                        print("   ⏭️ DUPLICATA (Hash Match). Arquivando sem processar...")
                        drive_service.files().update(fileId=f_id, addParents=archive_id, removeParents=inbox_id).execute()
                        continue

                    # 5. Processamento (LGPD -> IA -> Neo4j)
                    print("   🧠 Extraindo & Sanitizando (LGPD)...")
                    raw_text = extract_text(local_path)
                    safe_text = sanitize_text_lgpd(raw_text)
                    
                    print("   🤖 IA Analysis...")
                    json_proposal = analyze_document_content(safe_text, f_name)

                    if not json_proposal:
                        msg = "IA falhou (retornou vazio/None). Abortando e movendo para Quarentena."
                        print(f"   ❌ {msg}")
                        log_audit(sheet_service, sheet_id, {
                            'name': f_name, 'id': f_id, 'hash': final_hash,
                            'status': 'QUARANTINED_AI_ERROR', 'log': msg
                        })
                        drive_service.files().update(
                            fileId=f_id,
                            addParents=quarantine_id,
                            removeParents=inbox_id,
                        ).execute()
                        print("   ☣️ Movido para Quarentena.")
                        continue
                    
                    print("   🌉 Neo4j Injection...")
                    log = execute_bridge(json_proposal)
                    
                    # 6. Sucesso: Audita, Cacheia, Arquiva
                    log_audit(sheet_service, sheet_id, {
                        'name': f_name, 'id': f_id, 'hash': final_hash,
                        'status': 'INDEXED', 'log': log
                    })
                    processed_hashes.add(final_hash)
                    
                    drive_service.files().update(fileId=f_id, addParents=archive_id, removeParents=inbox_id).execute()
                    print("   ✅ SUCESSO. Arquivado.")

                except Exception as e:
                    print(f"   ❌ FALHA: {e}")
                    log_audit(sheet_service, sheet_id, {
                        'name': f_name, 'id': f_id, 'hash': 'error',
                        'status': 'ERROR', 'log': str(e)
                    })
                    drive_service.files().update(fileId=f_id, addParents=quarantine_id, removeParents=inbox_id).execute()
                    print("   ☣️ Movido para Quarentena.")
                
                finally:
                    if local_path and os.path.exists(local_path): 
                        try: os.remove(local_path)
                        except: pass
                    
        except HttpError as e:
            # Tratamento de Quota/Rate Limit
            if e.resp.status in [403, 429, 500, 503]:
                errors_consecutive += 1
                exponential_backoff(errors_consecutive)
            else:
                print(f"⚠️ Erro HTTP Crítico: {e}")
                time.sleep(30)
        except Exception as e:
            print(f"⚠️ Erro Genérico: {e}")
            time.sleep(30)

if __name__ == "__main__":
    main_loop()

