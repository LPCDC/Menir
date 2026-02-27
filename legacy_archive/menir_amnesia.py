import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/drive', 'https://www.googleapis.com/auth/spreadsheets']

def get_creds():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    return creds

def wipe_tivoli_memory():
    print("🧠 MENIR AMNESIA V3: Alvo -> 'Menir_Triage_Master'...")
    
    creds = get_creds()
    if not creds: return

    try:
        service = build('drive', 'v3', credentials=creds)
        sheets_service = build('sheets', 'v4', credentials=creds)

        # 1. Busca Exata pelo nome correto
        query = "name = 'Menir_Triage_Master' and mimeType = 'application/vnd.google-apps.spreadsheet' and trashed = false"
        results = service.files().list(q=query, pageSize=1, fields="files(id, name)").execute()
        items = results.get('files', [])

        if not items:
            print("❌ Erro: Planilha 'Menir_Triage_Master' não encontrada! Verifique o Drive.")
            return
        
        spreadsheet_id = items[0]['id']
        print(f"🎯 Alvo Travado: {items[0]['name']} (ID: {spreadsheet_id})")

        # 2. Pega dados da primeira aba
        sheet_metadata = sheets_service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
        sheets = sheet_metadata.get('sheets', '')
        sheet_id = sheets[0]['properties']['sheetId'] 
        sheet_title = sheets[0]['properties']['title']

        # 3. Lê o conteúdo
        result = sheets_service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=sheet_title).execute()
        rows = result.get('values', [])

        # 4. Identifica linhas com "TIVOLI" (Registro 5 da sua lista)
        rows_to_delete = []
        for index, row in enumerate(rows):
            # Converte linha para texto e busca a chave
            if "TIVOLI" in str(row).upper():
                rows_to_delete.append(index)

        if not rows_to_delete:
            print("✅ Limpo. Nenhuma linha com 'TIVOLI' encontrada.")
            return

        rows_to_delete.sort(reverse=True)
        print(f"⚠️ Apagando {len(rows_to_delete)} registro(s) antigos do Tivoli...")

        # 5. Executa Deleção
        requests = []
        for row_index in rows_to_delete:
            requests.append({
                "deleteDimension": {
                    "range": {
                        "sheetId": sheet_id,
                        "dimension": "ROWS",
                        "startIndex": row_index,
                        "endIndex": row_index + 1
                    }
                }
            })

        body = {'requests': requests}
        sheets_service.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id, body=body).execute()
        print("✨ MEMÓRIA APAGADA. Pode reprocessar.")

    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    wipe_tivoli_memory()
