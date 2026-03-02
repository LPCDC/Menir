import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.utils import check_neo4j_connection

print("\n🔍 [AUDIT] Infiltrando no Banco...")
driver = check_neo4j_connection()
if driver:
    with driver.session() as session:
        # Busca Ricardo e suas relações
        res = session.run("MATCH (n:Person {name: 'Ricardo'}) RETURN count(n) as qtd").single()
        qtd = res['qtd']
        print(f"📊 RESULTADO: Encontrados {qtd} nós com o nome 'Ricardo'.")
        if qtd > 0:
            print("⚠️ Sugestão: Execute a limpeza após validar o cenário da Ella.")
    driver.close()
else:
    print("❌ ERRO: Não foi possível conectar ao Neo4j. Verifique se o Docker está ligado.")
