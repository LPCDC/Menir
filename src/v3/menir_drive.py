"""
Menir v3.0 Drive Module
Handles Google Drive Polling and Downloading.
"""
import os
import io
import logging
import pickle
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

logger = logging.getLogger("MenirDrive")

class MenirDrive:
    SCOPES = ['https://www.googleapis.com/auth/drive']
    
    def __init__(self, token_path='token.json', creds_path='credentials.json'):
        self.creds = self._get_credentials(token_path, creds_path)
        self.service = build('drive', 'v3', credentials=self.creds)
        self.folders = self._init_folders()
        
    def _get_credentials(self, token_path, creds_path):
        creds = None
        if os.path.exists(token_path):
            with open(token_path, 'rb') as token:
                # Handle both pickle (legacy) and JSON
                try:
                    creds = Credentials.from_authorized_user_file(token_path, self.SCOPES)
                except ValueError:
                    # Maybe it's pickle?
                    try:
                        with open(token_path, 'rb') as ptoken:
                             creds = pickle.load(ptoken)
                    except:
                        pass

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except Exception as e:
                    logger.warning(f"Token refresh failed ({e}). Re-authenticating via browser...")
                    if os.path.exists(creds_path):
                        flow = InstalledAppFlow.from_client_secrets_file(creds_path, self.SCOPES)
                        creds = flow.run_local_server(port=0)
            else:
                 # We assume token exists from previous steps, but if not:
                 if os.path.exists(creds_path):
                     flow = InstalledAppFlow.from_client_secrets_file(creds_path, self.SCOPES)
                     creds = flow.run_local_server(port=0)
            
            # Save updated token
            with open(token_path, 'w') as token:
                token.write(creds.to_json())
                
        return creds

    def _init_folders(self):
        """Finds or creates necessary Drive folders."""
        names = ["Menir_Inbox", "Menir_Cloud_Archive"]
        folders = {}
        
        for name in names:
            query = f"mimeType='application/vnd.google-apps.folder' and name='{name}' and trashed=false"
            results = self.service.files().list(q=query, fields="files(id)").execute()
            items = results.get('files', [])
            
            if not items:
                logger.info(f"Drive: Creating folder {name}...")
                meta = {'name': name, 'mimeType': 'application/vnd.google-apps.folder'}
                created = self.service.files().create(body=meta, fields='id').execute()
                folders[name] = created['id']
            else:
                folders[name] = items[0]['id']
                
        logger.info(f"Drive Linked: Inbox={folders['Menir_Inbox']}, Archive={folders['Menir_Cloud_Archive']}")
        return folders

    def sync(self, local_inbox):
        """
        Polls Drive Inbox, Downloads to Local Inbox, Moves to Cloud Archive.
        """
        inbox_id = self.folders["Menir_Inbox"]
        archive_id = self.folders["Menir_Cloud_Archive"]
        
        query = f"'{inbox_id}' in parents and trashed=false and mimeType != 'application/vnd.google-apps.folder'"
        results = self.service.files().list(q=query, fields="files(id, name)").execute()
        items = results.get('files', [])
        
        downloaded_count = 0
        
        for item in items:
            file_id = item['id']
            name = item['name']
            
            logger.info(f"Drive: Downloading {name}...")
            
            request = self.service.files().get_media(fileId=file_id)
            fh = io.BytesIO()
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while done is False:
                status, done = downloader.next_chunk()

            local_path = os.path.join(local_inbox, name)
            with open(local_path, "wb") as f:
                f.write(fh.getbuffer())
                
            # Move to Cloud Archive to prevent re-download
            # We add Archive parent, remove Inbox parent
            self.service.files().update(
                fileId=file_id,
                addParents=archive_id,
                removeParents=inbox_id
            ).execute()
            
            downloaded_count += 1
            
        if downloaded_count > 0:
            logger.info(f"Drive Sync: {downloaded_count} files downloaded.")

    def replay_all(self):
        """
        MOVES all files from Menir_Cloud_Archive back to Menir_Inbox.
        This triggers a full re-ingestion by the Runner.
        """
        inbox_id = self.folders["Menir_Inbox"]
        archive_id = self.folders["Menir_Cloud_Archive"]
        
        query = f"'{archive_id}' in parents and trashed=false"
        results = self.service.files().list(q=query, fields="files(id, name)").execute()
        items = results.get('files', [])
        
        if not items:
            logger.info("Drive Replay: No files found in Archive.")
            return

        logger.info(f"Drive Replay: Moving {len(items)} files back to Inbox...")
        
        for item in items:
            try:
                self.service.files().update(
                    fileId=item['id'],
                    addParents=inbox_id,
                    removeParents=archive_id
                ).execute()
                logger.info(f"   Requeued: {item['name']}")
            except Exception as e:
                logger.error(f"   Failed to requeue {item['name']}: {e}")
        
        logger.info("✅ Drive Replay Complete. Runner should detect files shortly.")

