import os
import sys
import asyncio
import logging

# Adiciona o diretório raiz ao sys.path para importações v3
sys.path.append(os.getcwd())

from src.v3.menir_bridge import get_bridge
from src.v3.core.neo4j_pool import Neo4jPoolManager

logging.basicConfig(level=logging.INFO)

async def test_singleton():
    print("--- Testando Singleton MenirBridge ---")
    
    # 1. Testar Guarda (deve falhar pois Neo4jPoolManager não foi criado)
    print("1. Testando guarda de inicialização (esperado: RuntimeError)...")
    try:
        get_bridge()
        print("FAIL: get_bridge() retornou instância antes do pool ser inicializado!")
    except RuntimeError as e:
        print(f"PASS: Capturado erro esperado: {e}")
    except Exception as e:
        print(f"FAIL: Capturado erro inesperado: {type(e).__name__}: {e}")

    # 2. Inicializar Pool e Testar Singleton
    print("\n2. Inicializando Neo4jPoolManager e testando Singleton...")
    # Mock de environment para o pool
    os.environ["NEO4J_URI"] = "bolt://localhost:7687"
    os.environ["NEO4J_USER"] = "neo4j"
    os.environ["NEO4J_PASSWORD"] = "test" # Não vai conectar, mas deve inicializar o manager
    
    # Forçamos a inicialização do Manager (Singleton de módulo)
    pool = Neo4jPoolManager()
    
    try:
        b1 = get_bridge()
        b2 = get_bridge()
        
        if b1 is b2:
            print("PASS: get_bridge() retornou a mesma instância (Singleton OK).")
        else:
            print("FAIL: get_bridge() retornou instâncias diferentes!")
            
    except Exception as e:
        print(f"FAIL: Erro ao obter bridge: {e}")

if __name__ == "__main__":
    asyncio.run(test_singleton())
