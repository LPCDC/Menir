# src/v3/setup_audit_sheet.py
import os
import logging
import gspread
from .menir_audit import MenirAudit

# Reuse the Auth logic from the class we just patched
# We instantiate MenirAudit with dummy ID just to get the client
def get_audit_sheet_id():
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("SetupAudit")
    
    # Dummy config
    audit = MenirAudit("credentials.json", "dummy", "Audit_V3")
    creds = audit._get_credentials()
    
    if not creds:
        # Fallback to local gspread default 
        client = gspread.oauth(
            credentials_filename='credentials.json',
            authorized_user_filename='token.json'
        )
    else:
        client = gspread.authorize(creds)
        
    SHEET_TITLE = "Menir_Audit_V3_Master"
    
    try:
        # Try to open by title
        sheet = client.open(SHEET_TITLE)
        logger.info(f"Found existing sheet: {sheet.id}")
        return sheet.id
    except gspread.SpreadsheetNotFound:
        logger.info(f"Sheet '{SHEET_TITLE}' not found. Creating...")
        sheet = client.create(SHEET_TITLE)
        sheet.share('menir-bot@menir-vital-link.iam.gserviceaccount.com', perm_type='user', role='writer') # Optional sharing if we knew the email
        # Or just rely on user ownership
        logger.info(f"Created new sheet: {sheet.id}")
        
        # Init Header
        ws = sheet.get_worksheet(0)
        ws.update_title("Audit_V3")
        ws.append_row([
            "timestamp", "project", "filename", "sha256", 
            "status", "reason", "duration_s", "model"
        ])
        return sheet.id

if __name__ == "__main__":
    print(f"SHEET_ID={get_audit_sheet_id()}")
