
from src.v3.menir_bridge import MenirBridge

def nuke():
    bridge = MenirBridge()
    msg = "⚠️ NUKING DATABASE... ⚠️"
    print(msg)
    
    with bridge.driver.session() as session:
        # Delete relationships first
        session.run("MATCH ()-[r]->() DELETE r")
        # Delete nodes
        session.run("MATCH (n) DELETE n")
        
    print("✅ DATABASE WIPED (Clean Slate).")
    bridge.close()

if __name__ == "__main__":
    nuke()
