import json
from neo4j import GraphDatabase
# Importação relativa removida para evitar erro, conexão será injetada ou local
from dotenv import load_dotenv
import os

load_dotenv()

def execute_bridge(json_str):
    # Conexão direta e simples para o teste local
    uri = "neo4j://localhost:7687"
    auth = ("neo4j", "menir123")
    
    try:
        data = json.loads(json_str)
        if "error" in data: return f"❌ Abortado: {data['error']}"
        
        driver = GraphDatabase.driver(uri, auth=auth)
        driver.verify_connectivity()
        
        summary = []
        with driver.session() as session:
            # Inserção Atômica de Nós
            for node in data.get("nodes", []):
                q = f"MERGE (n:{node['label']} {{name: $name}}) SET n += $props"
                session.run(q, name=node["name"], props=node.get("props", {}))
                summary.append(f"✅ Nó Criado/Atualizado: {node['name']} ({node['label']})")
                
            # Inserção Atômica de Arestas
            for edge in data.get("edges", []):
                q = f"""
                MATCH (a {{name: $src}}), (b {{name: $tgt}})
                MERGE (a)-[r:{edge['type']}]->(b)
                """
                session.run(q, src=edge["source"], tgt=edge["target"])
                summary.append(f"🔗 Conexão: {edge['source']} -> {edge['type']} -> {edge['target']}")
                
        driver.close()
        return "\n".join(summary)
    except Exception as e:
        return f"❌ Falha Crítica na Ponte: {e}"
