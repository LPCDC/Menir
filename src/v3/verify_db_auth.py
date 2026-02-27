from neo4j import GraphDatabase
import logging

# Candidate passwords provided by user
PASSWORDS = [
    "bvPp561reYBKtaNPwgPG4250tI9RFKcjNKkhoXG5dGc",
    "I7Dbf7wQEE3wsHQ1o3UB33I8vewoRrAWdtMcN0bVkY0",
    "menir123",  # Current, likely wrong
    "neo4j"      # Default
]

URI = "neo4j://localhost:7687"
USER = "neo4j"

def test_auth():
    print(f"Testing connection to {URI}...")
    
    for pwd in PASSWORDS:
        print(f"Trying password: {pwd[:5]}...{pwd[-3:]}")
        try:
            driver = GraphDatabase.driver(URI, auth=(USER, pwd))
            driver.verify_connectivity()
            print(f"✅ SUCCESS! Correct Password is: {pwd}")
            return pwd
        except Exception as e:
            print(f"❌ Failed: {e}")
            driver.close()
            
    print("❌ All passwords failed.")
    return None

if __name__ == "__main__":
    test_auth()
