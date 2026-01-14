import os
import zipfile
import glob
import json
import logging
from datetime import datetime, timezone

# Configuração de Log de Console
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def perform_backup():
    # Caminhos
    script_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.dirname(script_dir)
    log_path = os.path.join(base_dir, 'logs', 'operations.jsonl')
    
    folders_to_backup = ["data/system", "logs"]
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    target_dir = os.path.join(base_dir, "backups")
    archive_name = f"menir_backup_{timestamp}.zip"
    archive_path = os.path.join(target_dir, archive_name)
    
    os.makedirs(target_dir, exist_ok=True)
    
    logging.info(f"📦 Starting backup to: {archive_path}")
    
    try:
        count_files = 0
        with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for folder in folders_to_backup:
                abs_folder_path = os.path.join(base_dir, folder)
                if not os.path.exists(abs_folder_path):
                    logging.warning(f"⚠️ Folder not found: {folder}")
                    continue
                    
                for root, dirs, files in os.walk(abs_folder_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, base_dir)
                        # Evita loop infinito: não incluir backups passados
                        if "backups" in arcname: 
                            continue
                        zipf.write(file_path, arcname)
                        count_files += 1
                        
        logging.info(f"✅ Backup created successfully! ({count_files} files)")
        
        # Log Oficial
        append_log(log_path, "backup_success", {"file": archive_name, "count": count_files})
        
        # Rotação
        rotate_backups(target_dir, limit=30)
        
    except Exception as e:
        logging.error(f"❌ Backup failed: {e}")
        append_log(log_path, "backup_failure", {"error": str(e)}, level="ERROR")
        raise e

def append_log(log_path: str, action: str, payload: dict, level: str = "INFO"):
    """Escreve no log oficial operations.jsonl"""
    entry = {
        "ts": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "action": action,
        "level": level,
        **payload
    }
    try:
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(entry) + '\n')
    except Exception as e:
        logging.error(f"Failed to write to operations.jsonl: {e}")

def rotate_backups(target_dir, limit=30):
    archives = sorted(glob.glob(os.path.join(target_dir, "menir_backup_*.zip")))
    
    if len(archives) > limit:
        logging.info(f"🧹 Rotation needed: Found {len(archives)} backups (Limit: {limit})")
        to_remove = len(archives) - limit
        for i in range(to_remove):
            file_to_del = archives[i]
            try:
                os.remove(file_to_del)
                logging.info(f"🗑️ Deleted old backup: {os.path.basename(file_to_del)}")
            except OSError as e:
                logging.error(f"Failed to delete {file_to_del}: {e}")
    else:
        logging.info("✨ Backup rotation clean.")

if __name__ == "__main__":
    perform_backup()
