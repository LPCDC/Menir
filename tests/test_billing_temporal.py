import pytest
import pytest_asyncio
from datetime import datetime, timezone
import time
from pydantic import ValidationError
from neo4j import GraphDatabase

# The interfaces we are going to build
from src.v3.core.billing import (
    BillingManager, 
    RuleMutationPayload, 
    ForensicAuditPayload,
    TemporalOverlapError,
    ContractStatus
)
from neo4j import AsyncGraphDatabase
import os
from dotenv import load_dotenv

load_dotenv(override=True)

@pytest_asyncio.fixture()
async def db_driver():
    uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    user = os.getenv("NEO4J_USER", "neo4j")
    pwd = os.getenv("NEO4J_PASSWORD") or os.getenv("NEO4J_PWD", "SANTOS_DB2024")
    driver = AsyncGraphDatabase.driver(uri, auth=(user, pwd))
    yield driver
    await driver.close()

@pytest_asyncio.fixture()
async def clear_billing_graph(db_driver):
    """Limpa o subgrafo de testes antes e depois de cada teste."""
    async with db_driver.session() as session:
        await session.execute_write(
            lambda tx: tx.run("MATCH (c:Client {uid: 'TEST_CLIENT_BILLING'})-[r*0..]-(n) DETACH DELETE c, n")
        )
    yield db_driver
    async with db_driver.session() as session:
        await session.execute_write(
            lambda tx: tx.run("MATCH (c:Client {uid: 'TEST_CLIENT_BILLING'})-[r*0..]-(n) DETACH DELETE c, n")
        )

@pytest.fixture
def client_uid():
    return "TEST_CLIENT_BILLING"

@pytest.mark.asyncio
async def test_geographic_mismatch_pydantic():
    """Teste 5: Geopolítica Suíça. Tenta enviar offset de inverno (+01:00) numa data de verão."""
    # 1 de Julho na Suíça está no CEST (+02:00). 
    # Se tentarmos forçar +01:00, o Pydantic DEVE abortar.
    with pytest.raises(ValidationError) as exc_info:
        RuleMutationPayload(
            client_uid="ANY",
            new_tariff=150.0,
            effective_date="2026-07-01T00:00:00+01:00" 
        )
    # Tem que falhar porque o offset correto no verão é +02:00
    assert "Desalinhamento Sazonal" in str(exc_info.value) or "timezone" in str(exc_info.value).lower()

    # O offset correto deve passar
    payload = RuleMutationPayload(
        client_uid="ANY",
        new_tariff=150.0,
        effective_date="2026-07-01T00:00:00+02:00" 
    )
    assert payload.new_tariff == 150.0

@pytest.mark.asyncio
async def test_genesis_rule(client_uid, clear_billing_graph):
    """Teste 1: A Gênese do Contrato (Criar primeira tarifa)."""
    driver = clear_billing_graph
    
    # Criar cliente órfão primeiro
    async with driver.session() as session:
        await session.execute_write(lambda tx: tx.run("CREATE (c:Client {uid: $uid})", uid=client_uid))
    
    manager = BillingManager(driver)
    
    payload = RuleMutationPayload(
        client_uid=client_uid,
        new_tariff=100.0,
        effective_date="2026-01-01T00:00:00+01:00" # Inverno CET
    )
    
    new_rule_uid = await manager.mutate_contract(payload)
    assert new_rule_uid is not None
    
    # Valida estrutura via Cypher
    async with driver.session() as session:
        async def _verify(tx):
            res = await tx.run("MATCH (c:Client {uid: $uid})-[:ACTIVE_RULE]->(br:BillingRule) RETURN br", uid=client_uid)
            return await res.single()
        record = await session.execute_read(_verify)
        assert record is not None
        br = record["br"]
        assert br["tariff_rate"] == 100.0
        assert br["valid_from"] == payload.normalized_effective_timestamp
        assert br["version"] == 1

@pytest.mark.asyncio
async def test_mutation_fork_o1(client_uid, clear_billing_graph):
    """Teste 2: Mutação de Contrato O(1) e Cadeia Retrospectiva."""
    driver = clear_billing_graph
    async with driver.session() as session:
        await session.execute_write(lambda tx: tx.run("CREATE (c:Client {uid: $uid})", uid=client_uid))
    
    manager = BillingManager(driver)
    
    # Regra Inicial
    p1 = RuleMutationPayload(client_uid=client_uid, new_tariff=100.0, effective_date="2026-01-01T00:00:00+01:00")
    uid1 = await manager.mutate_contract(p1)
    
    # Mutação (Fork)
    p2 = RuleMutationPayload(client_uid=client_uid, new_tariff=250.0, effective_date="2026-02-01T00:00:00+01:00", expected_version=1)
    uid2 = await manager.mutate_contract(p2)
    
    # Valida se a ACTIVE aponta pro 2, e 2 aponta pro 1 via PREVIOUS_VERSION
    async with driver.session() as session:
        async def _verify(tx):
            res = await tx.run("MATCH (c:Client {uid: $uid})-[:ACTIVE_RULE]->(br:BillingRule)-[:PREVIOUS_VERSION]->(old:BillingRule) RETURN br, old", uid=client_uid)
            return await res.single()
        record = await session.execute_read(_verify)
        assert record is not None
        assert record["br"]["uid"] == uid2
        assert record["br"]["version"] == 2
        assert record["old"]["uid"] == uid1
        assert record["old"]["valid_to"] == p2.normalized_effective_timestamp

@pytest.mark.asyncio
async def test_temporal_overlap_rejection(client_uid, clear_billing_graph):
    """Teste 4: Blindagem Geopolítica e APOC Shield."""
    driver = clear_billing_graph
    async with driver.session() as session:
        await session.execute_write(lambda tx: tx.run("CREATE (c:Client {uid: $uid})", uid=client_uid))
    
    manager = BillingManager(driver)
    
    # Regra Inicial em Fevereiro
    p1 = RuleMutationPayload(client_uid=client_uid, new_tariff=100.0, effective_date="2026-02-01T00:00:00+01:00")
    await manager.mutate_contract(p1)
    
    # Tenta Mutar Retroativamente em Janeiro (Antes da Gênese Atual)
    p_invalid = RuleMutationPayload(client_uid=client_uid, new_tariff=250.0, effective_date="2026-01-01T00:00:00+01:00", expected_version=1)
    
    with pytest.raises(TemporalOverlapError) as exc_info:
        await manager.mutate_contract(p_invalid)
        
    assert "retroativa" in str(exc_info.value).lower() or "overlapping" in str(exc_info.value).lower()

@pytest.mark.asyncio
async def test_optimistic_lock_failure(client_uid, clear_billing_graph):
    """Teste 7: Optimistic Locking APOC Rejecting stale mutation."""
    from src.v3.core.billing import ConcurrentMutationError
    driver = clear_billing_graph
    async with driver.session() as session:
        await session.execute_write(lambda tx: tx.run("CREATE (c:Client {uid: $uid})", uid=client_uid))
    
    manager = BillingManager(driver)
    
    # Regra Inicial em Janeiro
    p1 = RuleMutationPayload(client_uid=client_uid, new_tariff=100.0, effective_date="2026-01-01T00:00:00+01:00")
    await manager.mutate_contract(p1)
    
    # Tenta Mutar enviando expected_version=100, mas a real é 1
    p_invalid = RuleMutationPayload(client_uid=client_uid, new_tariff=250.0, effective_date="2026-02-01T00:00:00+01:00", expected_version=100)
    
    with pytest.raises(ConcurrentMutationError) as exc_info:
        await manager.mutate_contract(p_invalid)
        
    assert "ERR-BI-02" in str(exc_info.value) or "Optimistic" in str(exc_info.value)

@pytest.mark.asyncio
async def test_forensic_time_travel(client_uid, clear_billing_graph):
    """Teste 3: Viagem no Tempo Segura (Sem type impedance)."""
    driver = clear_billing_graph
    async with driver.session() as session:
        await session.execute_write(lambda tx: tx.run("CREATE (c:Client {uid: $uid})", uid=client_uid))
        
    manager = BillingManager(driver)
    
    # 1. Regra base: Jan a Fev (100 CHF)
    p_jan = RuleMutationPayload(client_uid=client_uid, new_tariff=100.0, effective_date="2026-01-01T00:00:00+01:00")
    uid_jan = await manager.mutate_contract(p_jan)
    
    # 2. Regra Fev em Diante: (200 CHF)
    p_fev = RuleMutationPayload(client_uid=client_uid, new_tariff=200.0, effective_date="2026-02-01T00:00:00+01:00", expected_version=1)
    uid_fev = await manager.mutate_contract(p_fev)
    
    # Busca forense de 15 de Janeiro. Deve retornar "Type Safe" a regra base (100)
    # Mandamos payload forense com fuso suíço explícito, garantindo cast pra int internamente.
    p_audit = ForensicAuditPayload(
        client_uid=client_uid,
        target_date="2026-01-15T12:00:00+01:00"
    )
    rule = await manager.resolve_active_rule_at(p_audit)
    assert rule is not None
    assert rule["uid"] == uid_jan
    assert rule["tariff_rate"] == 100.0

@pytest.mark.asyncio
async def test_python_local_starvation_shield(client_uid, clear_billing_graph):
    """Teste 6: O Semáforo Fast-Fail Python que impede starvation do pool."""
    from src.v3.core.billing import ConcurrentMutationError
    driver = clear_billing_graph
    async with driver.session() as session:
        await session.execute_write(lambda tx: tx.run("CREATE (c:Client {uid: $uid})", uid=client_uid))
        
    manager = BillingManager(driver)
    
    # Payload 1: Valida.
    p1 = RuleMutationPayload(client_uid=client_uid, new_tariff=100.0, effective_date="2026-01-01T00:00:00+01:00")
    # Payload 2: Identica/Concorrente
    p2 = RuleMutationPayload(client_uid=client_uid, new_tariff=200.0, effective_date="2026-02-01T00:00:00+01:00", expected_version=1)
    
    # Criamos uma barreira artificial para travar a Coroutine 1 tempo suficiente para a Coroutine 2 bater na porta
    import asyncio
    
    async def slow_mutate():
        # Vamos emular que o mutate_contract segurou a lock enquanto bate no cypher
        return await manager.mutate_contract(p1)
        
    async def attacker_mutate():
        # Atrasa 10ms só para garantir que a 1 pegue a trava primeiro
        await asyncio.sleep(0.01)
        return await manager.mutate_contract(p2)
        
    t1 = asyncio.create_task(slow_mutate())
    t2 = asyncio.create_task(attacker_mutate())
    
    results = await asyncio.gather(t1, t2, return_exceptions=True)
    
    # Um deles deve ter sucesso (t1) e o outro falhar com ConcurrentMutationError (t2)
    exceptions = [r for r in results if isinstance(r, Exception)]
    assert len(exceptions) == 1
    assert isinstance(exceptions[0], ConcurrentMutationError)
    assert "Repulsão ASGI Inter-Processo" in str(exceptions[0])
