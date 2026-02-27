import sys
import os

# TRUQUE SÊNIOR: Adiciona a pasta 'src' ao caminho do Python antes de importar
# Isso impede o erro "ModuleNotFoundError" independente de onde vc roda
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, "src")
sys.path.append(src_dir)

print(f"🔧 Configurando ambiente... (Source: {src_dir})")

try:
    from menir_intel import analyze_document_content
    from menir_bridge import execute_bridge
    print("✅ Módulos carregados.")
except ImportError as e:
    print(f"❌ Erro fatal de importação: {e}")
    sys.exit(1)

# O TESTE REAL
briefing = "Oi Luiz, aqui é a Ella. Preciso contratar a LibLabs para o álbum True Stories. Sou sua amiga!"

print("\n🧠 1. SOLICITANDO INTELIGÊNCIA (Gemini 1.5)...")
proposal = analyze_document_content(briefing, "test.txt")
print(f"   📋 Resposta da IA: {proposal[:100]}...")

print("\n🌉 2. EXECUTANDO PONTE (Neo4j)...")
log = execute_bridge(proposal)
print("\n" + "="*30)
print("RELATÓRIO FINAL:")
print(log)
print("="*30)
