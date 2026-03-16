import pytest
import os
import json
from unittest.mock import patch, MagicMock

# Importaremos a logica isoladamente ou rodaremos via subprocess no test.
# Como e um script, testaremos importando as funcões principais se houver, ou via command line.
from scripts.bootstrap_beco_clients import process_clients

@pytest.fixture
def mock_driver():
    driver = MagicMock()
    session = MagicMock()
    tx = MagicMock()
    
    # with GraphDatabase.driver(...) as driver:
    driver.__enter__.return_value = driver
    
    # with driver.session() as session:
    driver.session.return_value.__enter__.return_value = session
    
    # with session.begin_transaction() as tx:
    session.begin_transaction.return_value.__enter__.return_value = tx
    
    return driver, session, tx

def test_process_clients_reads_and_filters_correctly(mock_driver):
    driver, session, tx = mock_driver
    csv_file = "tests/fixtures/beco_clients_sample.csv"
    
    with patch("scripts.bootstrap_beco_clients.GraphDatabase") as mock_neo4j:
        mock_neo4j.driver.return_value = driver
        
        from src.v3.core.schemas.identity import TenantContext
        TenantContext.set("BECO")
        
        total, valid, injected, discarded = process_clients(csv_file, neo4j_uri="bolt://mock", neo4j_user="neo4j", neo4j_pass="mock")
        
        print(f"DEBUG TEST: valid={valid}, injected={injected}, discarded={discarded}")
        
        assert total == 10
        assert valid == 8
        assert discarded == 2
        assert injected == 8
        
        tx.run.assert_called()
        
        # E verifica a presenca de gravacoes no output (opicional, pode testar direto o file).
