import sys
import os
import pypdf
from menir_intel import analyze_document_content
from menir_bridge import execute_bridge

# Configuração de Path
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

def extract_text(filepath):
    """Extrai texto de PDF ou TXT."""
    ext = os.path.splitext(filepath)[1].lower()
    try:
        if ext == ".pdf":
            reader = pypdf.PdfReader(filepath)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text
        else:
            with open(filepath, "r", encoding="utf-8") as f:
                return f.read()
    except Exception as e:
        return f"Erro de Leitura: {e}"

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("❌ Uso: python ingest.py <arquivo>")
        sys.exit(1)
        
    filepath = sys.argv[1]
    filename = os.path.basename(filepath)
    
    print(f"📄 Lendo: {filename}...")
    text = extract_text(filepath)
    
    print("🧠 Analisando (Ontologia V5)...")
    json_proposal = analyze_document_content(text, filename)
    
    print("🌉 Executando no Neo4j...")
    log = execute_bridge(json_proposal)
    
    print("\nRELATÓRIO DE INGESTÃO:")
    print(log)
