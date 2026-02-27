
from src.v3.menir_drive import MenirDrive
import logging

# Setup Logging
logging.basicConfig(level=logging.INFO)

print("🚀 Triggering Menir Cloud Replay...")
try:
    drive = MenirDrive()
    drive.replay_all()
    print("✅ Command Sent. Check Runner logs for incoming files.")
except Exception as e:
    print(f"❌ Replay Failed: {e}")
