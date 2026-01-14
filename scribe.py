import httpx
import sys

def send_thought(text):
    try:
        r = httpx.post("http://127.0.0.1:8000/ingest/", 
                       json={"raw_text": text, "source": "AG-Direct"})
        res = r.json()
        print(f"✅ [ID: {res['id']}] Arquivado. Análise: {res['analysis']['context']}")
    except Exception as e:
        print(f"❌ Falha na conexão: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        send_thought(" ".join(sys.argv[1:]))
    else:
        print("Uso: python scribe.py 'Sua ideia brilhante aqui'")
