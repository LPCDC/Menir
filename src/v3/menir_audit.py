# src/v3/menir_audit.py
import os
import json
import time
import logging
import gspread
from google.oauth2.credentials import Credentials
from google.oauth2 import service_account
from google.auth.transport.requests import Request
from tenacity import retry, stop_after_delay, wait_exponential, retry_if_exception_type

logger = logging.getLogger(__name__)

class AuditWriteError(Exception):
    """Erro fatal de escrita que deve acionar Quarentena."""
    pass

class MenirAudit:
    REQUIRED_SCOPES = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]

    def __init__(self, creds_json, sheet_id, tab_name):
        self.creds_json = creds_json
        self.sheet_id = sheet_id
        self.tab_name = tab_name
        self.client = None
        self.sheet = None

    def _get_credentials(self):
        """
        Hybrid Auth: Tries Service Account first, then generic 'token.json' User Auth.
        """
        # 1. Try Service Account (Strict)
        if self.creds_json and os.path.exists(self.creds_json):
            try:
                with open(self.creds_json, 'r') as f:
                    creds_data = json.load(f)
                
                if creds_data.get('type') == 'service_account':
                    logger.info("Auth: Detected Service Account.")
                    return service_account.Credentials.from_service_account_info(
                        creds_data, scopes=self.REQUIRED_SCOPES
                    )
            except Exception as e:
                logger.warning(f"Auth: Failed to load Service Account: {e}")
        
        # 2. Try User Token (token.json) - Specific to this environment
        token_path = "token.json" 
        if os.path.exists(token_path):
            try:
                logger.info(f"Auth: Loading {token_path}...")
                creds = Credentials.from_authorized_user_file(token_path, self.REQUIRED_SCOPES)
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                return creds
            except Exception as e:
                logger.error(f"Auth: User Token failed: {e}")
        
        # 3. Last Resort: return None (gspread factory might handle default env vars)
        return None

    def _connect(self):
        """Conecta e valida a existência da aba."""
        try:
            creds = self._get_credentials()
            
            if creds:
                self.client = gspread.authorize(creds)
            else:
                # Fallback: passing None explicitly allows gspread to try default locations
                # or crash if nothing found, but caught by loop below
                self.client = gspread.oauth(
                    credentials_filename=self.creds_json if self.creds_json else 'credentials.json',
                    authorized_user_filename='token.json'
                )

            logger.info(f"Connecting to Sheet ID: {self.sheet_id}")
            spreadsheet = self.client.open_by_key(self.sheet_id)
            
            try:
                self.sheet = spreadsheet.worksheet(self.tab_name)
            except gspread.WorksheetNotFound:
                logger.info(f"Tab {self.tab_name} not found. Creating...")
                self.sheet = spreadsheet.add_worksheet(title=self.tab_name, rows=1000, cols=10)
                self.sheet.append_row([
                    "timestamp", "project", "filename", "sha256", 
                    "status", "reason", "duration_s", "model"
                ])
            
            logger.info(f"Audit System Online: {self.sheet.title}")
            
        except Exception as e:
            # Mask sensitive parts of error
            msg = str(e).replace(self.sheet_id, "***") if self.sheet_id else str(e)
            raise AuditWriteError(f"Audit Boot Failed: {msg}")

    @retry(
        stop=stop_after_delay(600),
        wait=wait_exponential(multiplier=1, min=2, max=60),
        retry=retry_if_exception_type(gspread.exceptions.APIError),
        reraise=True
    )
    def _safe_append(self, row):
        if self.client is None: # or self.client.auth.expired: # gspread handles Auth refresh logic usually?
            self._connect()
            
        try:
            self.sheet.append_row(row, value_input_option='USER_ENTERED')
        except gspread.exceptions.APIError as e:
            if e.response.status_code == 403 and "quota" not in str(e).lower():
                raise AuditWriteError(f"FATAL PERMISSION ERROR: {e}")
            raise e

    def audit_append_row(self, audit_data: dict):
        """
        Grava linha com Hard-Stop.
        Schema: timestamp, project, filename, sha256, status, reason, duration_s, model
        """
        reason = str(audit_data.get('reason', ''))[:500].replace('\n', ' ')
        
        row = [
            audit_data.get('timestamp'),
            audit_data.get('project'),
            audit_data.get('filename'),
            audit_data.get('sha256'),
            audit_data.get('status'),
            reason,
            str(audit_data.get('duration_s', 0)),
            audit_data.get('model', 'gemini-1.5-flash')
        ]
        
        try:
            self._safe_append(row)
            logger.info(f"Audit Logged: {audit_data.get('status')} - {audit_data.get('filename')}")
        except Exception as e:
            logger.critical(f"AUDIT HARD-STOP: {e}")
            raise AuditWriteError(f"Audit Failed: {e}")
