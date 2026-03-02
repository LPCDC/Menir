
import os
import sys
from neo4j import GraphDatabase
from dotenv import load_dotenv

# Force load from .env in current directory, OVERRIDING system env
load_dotenv(override=True)

uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
user = os.getenv("NEO4J_USER", "neo4j")
password = os.getenv("NEO4J_PASSWORD", "menir123")

print(f"🔍 EXTRACTED CONFIG:")
print(f"   URI: {uri}")
print(f"   USER: {user}")
print(f"   PASSWORD (First 5): {password[:5] if password else 'None'}")
print(f"   PASSWORD (Last 5):  {password[-5:] if password else 'None'}")
print(f"   PASSWORD LEN:       {len(password) if password else 0}")
print(f"   PASSWORD REPR:      {repr(password)}")


print("\n🔌 ATTEMPTING CONNECTION WITH MULTIPLE CANDIDATES...")

candidates = [
    (password, "User Provided (.env)"),
    ("neo4j", "Default (neo4j)"),
    ("menir123", "Previous Dev Default"),
    ("admin", "Admin Default"),
    ("password", "Common Default")
]

success = False

for pwd, label in candidates:
    if not pwd: continue
    print(f"   👉 Trying {label}: '{pwd[:5]}...'")
    try:
        driver = GraphDatabase.driver(uri, auth=(user, pwd))
        driver.verify_connectivity()
        print(f"      ✅ SUCCESS! The correct password is: {label}")
        success = True
        driver.close()
        break
    except Exception as e:
        msg = str(e)
        if "Unauthorized" in msg:
            print(f"      ❌ Unauthorized")
        else:
            print(f"      ❌ Error: {msg}")

if success:
    print("\n✅ AUTHENTICATION RESOLVED.")
    sys.exit(0)
else:
    print("\n❌ ALL CANDIDATES FAILED.")
    sys.exit(1)
