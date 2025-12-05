# menir_allinone.py
import typer, rich, os
from pathlib import Path

app = typer.Typer()

@app.command()
def healthcheck():
    rich.print("[green]✔ Ambiente Menir pronto[/green]")

@app.command()
def neo4j_info():
    from neo4j import GraphDatabase
    uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    user = os.getenv("NEO4J_USER", "neo4j")
    pwd  = os.getenv("NEO4J_PASSWORD", "test")
    driver = GraphDatabase.driver(uri, auth=(user, pwd))
    with driver.session() as session:
        result = session.run("RETURN 1 AS ok")
        rich.print(f"[blue]Neo4j conectado[/blue]: {result.single()['ok']}")

@app.command()
def shapefile_info():
    import geopandas as gpd
    data_dir = Path("data_shapefiles")
    if not data_dir.exists():
        rich.print("[red]Nenhum shapefile encontrado[/red]")
    else:
        for f in data_dir.glob("*.shp"):
            gdf = gpd.read_file(f)
            rich.print(f"[cyan]{f.name}[/cyan]: {len(gdf)} features")

if __name__ == "__main__":
    app()
