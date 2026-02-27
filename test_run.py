import sys
import os
sys.path.append(os.path.join(os.getcwd(), "src"))
from menir_intel import analyze_document_content
from menir_bridge import execute_bridge

print("📄 Lendo briefing_ella.txt...")
with open("briefing_ella.txt", "r", encoding="utf-8") as f:
    text = f.read()

print("🧠 Analisando com Gemini (Intel V3)...")
json_proposal = analyze_document_content(text, "briefing_ella.txt")
print(f"   Proposta Gerada: {json_proposal[:100]}...")

print("🌉 Executando na Ponte (Bridge V3)...")
result = execute_bridge(json_proposal)
print(result)
