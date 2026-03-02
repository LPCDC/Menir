import os
import pickle
import datetime
import io
import json
import warnings
# Silencia o aviso chato do Google
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import pypdf
from dotenv import load_dotenv
import src.menir_intel as intel

load_dotenv()

SCOPES = ['https://www.googleapis.com/auth/drive', 'https://www.googleapis.com/auth/spreadsheets']
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CREDS_FILE = os.path.join(BASE_DIR, 'user_data', 'credentials.json')
TOKEN_FILE = os.path.join(BASE_DIR, 'user_data', 'token.json')
INBOX_NAME = "Menir_Inbox"
ARCHIVE_NAME = "Menir_Archive" # Nova Pasta
TRIAGE_SHEET_NAME = "Menir_Triage_Master"

def auth():
    creds = None
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'rb') as token: creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token: creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, 'wb') as token: pickle.dump(creds, token)
    return build('drive', 'v3', credentials=creds), build('sheets', 'v4', credentials=creds)

def get_folder_id(service, folder_name):
    query = f"mimeType='application/vnd.google-apps.folder' and name='{folder_name}' and trashed=false"
    results = service.files().list(q=query, fields='files(id)').execute()
    items = results.get('files', [])
    if not items:
        meta = {'name': folder_name, 'mimeType': 'application/vnd.google-apps.folder'}
        return service.files().create(body=meta, fields='id').execute().get('id')
    return items[0]['id']

def get_or_create_triage_sheet(drive_service, sheets_service):
    query = f"mimeType='application/vnd.google-apps.spreadsheet' and name='{TRIAGE_SHEET_NAME}' and trashed=false"
    results = drive_service.files().list(q=query, fields='files(id)').execute()
    items = results.get('files', [])
    if items: return items[0]['id']
    spreadsheet = {'properties': {'title': TRIAGE_SHEET_NAME}}
    sid = sheets_service.spreadsheets().create(body=spreadsheet, fields='spreadsheetId').execute().get('spreadsheetId')
    headers = [['STATUS', 'TIMESTAMP', 'FILENAME', 'RAW_CONTENT (Preview)', 'MENIR_SUGGESTION (JSON)', 'GRAPH_ACTION']]
    sheets_service.spreadsheets().values().update(spreadsheetId=sid, range="A1", valueInputOption="RAW", body={'values': headers}).execute()
    return sid

def extract_content(service, file_id, mime):
    try:
        if "application/pdf" in mime:
            request = service.files().get_media(fileId=file_id)
            fh = io.BytesIO()
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while done is False: _, done = downloader.next_chunk()
            fh.seek(0)
            reader = pypdf.PdfReader(fh)
            return "\n".join([p.extract_text() for p in reader.pages])
        elif "text" in mime or "json" in mime:
            return service.files().get_media(fileId=file_id).execute().decode('utf-8')
        return f"[Binary/Unsupported: {mime}]"
    except Exception as e: return f"[Error: {str(e)}]"

def process_next_file():
    try:
        drv, sht = auth()
        inbox_id = get_folder_id(drv, INBOX_NAME)
        archive_id = get_folder_id(drv, ARCHIVE_NAME) # Busca o ID do Arquivo Morto
        triage_id = get_or_create_triage_sheet(drv, sht)
        
        # Pega arquivo
        res = drv.files().list(q=f"'{inbox_id}' in parents and trashed=false", fields="files(id, name, mimeType)", pageSize=1).execute()
        files = res.get('files', [])
        if not files: return "Empty"
        
        f = files[0]
        
        # Processa
        content = extract_content(drv, f['id'], f['mimeType'])
        print(f"🧠 [AGAM] Analisando {f['name']}...")
        json_analysis = intel.analyze_document_content(content, f['name'])
        
        # Salva na Planilha
        preview = content[:2000] + "... [TRUNCATED]"
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        row = [['PENDING', timestamp, f['name'], preview, json_analysis, 'WAIT']]
        sht.spreadsheets().values().append(spreadsheetId=triage_id, range="A2", valueInputOption="RAW", body={'values': row}).execute()
        
        # MOVER PARA ARQUIVO (A CORREÇÃO)
        # Remove da Inbox E Adiciona no Archive ao mesmo tempo
        drv.files().update(fileId=f['id'], addParents=archive_id, removeParents=inbox_id).execute()
        
        return f"✅ Processed & Archived: {f['name']}"
    except Exception as e: return f"Error: {e}"
