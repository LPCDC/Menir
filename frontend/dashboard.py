import streamlit as st
import requests
from streamlit_agraph import agraph, Node, Edge, Config
from neo4j import GraphDatabase

st.set_page_config(page_title="Menir v1.8", layout="wide")
st.title(" Menir: Seu Segundo Cérebro")

# Função Robusta para buscar o Grafo
def get_graph_refined():
    nodes, edges = [], []
    try:
        driver = GraphDatabase.driver("bolt://menir-db:7687", auth=("neo4j", "menir123"))
        with driver.session() as session:
            # Query Pente-Fino: Pega nós e relações (se existirem)
            result = session.run("MATCH (n) OPTIONAL MATCH (n)-[r]->(m) RETURN n, r, m LIMIT 100")
            for record in result:
                for node in [record['n'], record['m']]:
                    if node:
                        # No Neo4j 5.x usamos element_id
                        nid = node.element_id 
                        if not any(x.id == nid for x in nodes):
                            label = list(node.labels)[0] if node.labels else "Entity"
                            # Cores: Ciano para Documento, Azul para Entidade
                            color = "#56b4e9" if label == "Document" else "#0072b2"
                            name = node.get('name', node.get('filename', 'Item'))
                            nodes.append(Node(id=nid, label=name, color=color, size=20))
                
                if record['r'] and record['m']:
                    edges.append(Edge(source=record['n'].element_id, target=record['m'].element_id))
        driver.close()
    except Exception as e:
        st.error(f"Erro de Conexão com o Banco: {e}")
    return nodes, edges

col1, col2 = st.columns([1.5, 1])

with col1:
    st.header(" Mapa de Conhecimento")
    if st.button(" Recarregar Mapa"):
        st.rerun()
    
    nodes, edges = get_graph_refined()
    if nodes:
        config = Config(width=700, height=600, directed=True, nodeHighlightBehavior=True, highlightColor="#F7A7A6")
        agraph(nodes=nodes, edges=edges, config=config)
    else:
        st.info("O Banco de Dados parece vazio ou inacessível.")

with col2:
    st.header(" Entrada")
    up = st.file_uploader("Upload PDF/Imagem", type=['pdf', 'jpg', 'png'])
    if up and st.button("Processar no Cérebro"):
        with st.spinner("Analisando..."):
            files = {"file": (up.name, up.getvalue())}
            r = requests.post("http://menir-scribe:8000/process", files=files)
            if r.status_code == 200:
                st.success("Processado! Clique em 'Recarregar Mapa'.")
                st.json(r.json())

st.sidebar.title("Chat")
if prompt := st.sidebar.text_input("Pergunte algo..."):
    st.sidebar.write(f"Menir pensando sobre: {prompt}")
