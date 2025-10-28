# menu_all_in_one.py
# Menu básico de inicialização Menir (All-in-One)

import geopandas
import shapely
import pandas
import matplotlib
import rich
from neo4j import GraphDatabase
from rich.console import Console

console = Console()

def check_stack():
    console.print("[bold cyan]>>> Verificando pacotes instalados...[/]")
    print("geopandas:", geopandas.__version__)
    print("shapely:", shapely.__version__)
    print("pandas:", pandas.__version__)
    print("matplotlib:", matplotlib.__version__)
    print("rich: import ok")
    print("neo4j:", GraphDatabase)

def test_neo4j():
    console.print("[bold yellow]>>> Testando conexão Neo4j...[/]")
    try:
        uri = "neo4j://localhost:7687"  # substitua se tiver outra URI
        user = "neo4j"
        password = "test"            # substitua se tiver senha diferente
        driver = GraphDatabase.driver(uri, auth=(user, password))
        with driver.session() as session:
            result = session.run("RETURN 'Neo4j online' AS msg")
            for r in result:
                console.print("Neo4j respondeu:", r["msg"])
        driver.close()
    except Exception as e:
        console.print("[bold red]Falha de conexão Neo4j:[/]", str(e))

def main():
    check_stack()
    test_neo4j()
    console.print("[bold green]Ambiente MENIR pronto com All-in-One![/]")

if __name__ == "__main__":
    main()
