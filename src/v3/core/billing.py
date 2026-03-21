import time
from enum import Enum
from datetime import datetime
from zoneinfo import ZoneInfo
from typing import Optional

from pydantic import BaseModel, Field, AwareDatetime, field_validator
from neo4j import AsyncDriver
from neo4j.exceptions import ClientError, Neo4jError

SWISS_TZ = ZoneInfo("Europe/Zurich")

class ContractStatus(str, Enum):
    ACTIVE = "ACTIVE"
    ARCHIVED = "ARCHIVED"           
    SUSPENDED_TOMBSTONE = "TOMBSTONE" 

class DomainException(Exception): pass
class TemporalOverlapError(DomainException): pass
class InvalidTombstoneTransition(DomainException): pass
class ConcurrentMutationError(DomainException): pass

APOC_ERROR_MAP = {
    "ERR-BI-01: Violação Bitemporal": TemporalOverlapError,
    "ERR-BI-02: Optimistic Lock Failure": ConcurrentMutationError,
}

def translate_apoc_error(error: ClientError):
    for err_code, exception_class in APOC_ERROR_MAP.items():
        if err_code in error.message:
            return exception_class(error.message)
    return error

# O Escudo de Starvation Inter-Processo (ASGI / Gunicorn)
import os
import time
import tempfile
from pathlib import Path

_MULTIPROCESS_LOCK_DIR = Path(tempfile.gettempdir()) / "menir_tenant_locks"
_MULTIPROCESS_LOCK_DIR.mkdir(parents=True, exist_ok=True)

class InterProcessTenantLock:
    """
    Trava multi-processo (Fast-Fail) nativa do Unix baseada em O_EXCL.
    Resolve a asfixia do pool em instâncias ASGI horizontais (Gunicorn) sem rede 
    e elimina o Memory Leak crônico evadindo o dicionário em estado global.
    """
    def __init__(self, client_uid: str):
        self.client_uid = client_uid
        self.lock_path = _MULTIPROCESS_LOCK_DIR / f"tenant_{client_uid}.lock"

    async def __aenter__(self):
        try:
            # Operação atômica do SO cruzando fronteiras de Forks no Python
            fd = os.open(str(self.lock_path), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.close(fd)
        except OSError as e:
            if e.errno == 17: # EEXIST / FileExistsError
                # Dead-worker Stale Lock Heuristics
                try:
                    mtime = os.path.getmtime(self.lock_path)
                    if time.time() - mtime > 15: # Timeout de abandono de corrotina
                        os.unlink(self.lock_path)
                        return await self.__aenter__() # Tail recursion para retomar
                except OSError:
                    pass
                raise ConcurrentMutationError(
                    f"Repulsão ASGI Inter-Processo: Mutação travada para {self.client_uid}. "
                    "Proteção Fast-Fail abortou o vazamento ao Pool Neo4j."
                )
            raise e
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        try:
            os.unlink(self.lock_path)
        except OSError:
            pass

class RuleMutationPayload(BaseModel):
    client_uid: str
    new_tariff: float = Field(ge=0.0)
    effective_date: AwareDatetime 
    expected_version: Optional[int] = None

    @field_validator('effective_date', mode='after')
    @classmethod
    def enforce_swiss_seasonality(cls, v: datetime) -> datetime:
        naive_dt = v.replace(tzinfo=None)
        expected_swiss_dt = naive_dt.replace(tzinfo=SWISS_TZ)
        expected_offset = expected_swiss_dt.utcoffset()
        provided_offset = v.utcoffset()
        
        if provided_offset != expected_offset:
            raise ValueError(
                f"[REJEIÇÃO GEOPOLÍTICA] Desalinhamento Sazonal. A jurisdição "
                f"Europe/Zurich exige um offset de {expected_offset} para a data {naive_dt.date()}, "
                f"mas a carga informou {provided_offset}. Verifique o Horário de Verão Europeu."
            )
        return v

    @property
    def normalized_effective_timestamp(self) -> int:
        return int(self.effective_date.timestamp())

class ForensicAuditPayload(BaseModel):
    client_uid: str
    target_date: AwareDatetime 

    @field_validator('target_date', mode='after')
    @classmethod
    def enforce_swiss_seasonality(cls, v: datetime) -> datetime:
        naive_dt = v.replace(tzinfo=None)
        expected_swiss_dt = naive_dt.replace(tzinfo=SWISS_TZ)
        expected_offset = expected_swiss_dt.utcoffset()
        provided_offset = v.utcoffset()
        
        if provided_offset != expected_offset:
            raise ValueError(
                f"[REJEIÇÃO GEOPOLÍTICA] Desalinhamento Sazonal na Auditoria Forense. "
                f"A Suíça exige offset {expected_offset} para {naive_dt.date()}, "
                f"mas a carga informou {provided_offset}."
            )
        return v

    @property
    def normalized_target_timestamp(self) -> int:
        return int(self.target_date.timestamp())

CYPHER_MUTATION_UNIFIED = """
MATCH (c:Client {uid: $client_uid})

CALL {
    WITH c
    OPTIONAL MATCH (c)-[old_edge:ACTIVE_RULE]->(old:BillingRule)
    RETURN old_edge, old
}

CALL apoc.util.validate(
    (old IS NOT NULL AND ($expected_version IS NULL OR old.version <> $expected_version)) OR 
    (old IS NULL AND $expected_version IS NOT NULL),
    "ERR-BI-02: Optimistic Lock Failure - Version mismatch.",
    []
)

CALL apoc.util.validate(
    old IS NOT NULL AND $effective_date < old.valid_from,
    "ERR-BI-01: Violação Bitemporal - Data retroativa (" + toString($effective_date) + ") anterior ao horizonte da regra atual (" + toString(old.valid_from) + ").",
    []
)

CREATE (new:BillingRule {
    uid: randomUUID(), 
    tariff_rate: $new_rate, 
    valid_from: $effective_date, 
    created_at: $now,
    version: CASE WHEN old IS NULL THEN 1 ELSE old.version + 1 END
})

WITH c, new, old_edge, old
FOREACH (ignore IN CASE WHEN old IS NOT NULL THEN [1] ELSE [] END |
    DELETE old_edge
    SET old.valid_to = new.valid_from
    CREATE (new)-[:PREVIOUS_VERSION]->(old)
)

CREATE (c)-[:ACTIVE_RULE]->(new)
RETURN new.uid, new.version
"""

class BillingManager:
    def __init__(self, driver: AsyncDriver):
        self.driver = driver

    async def mutate_contract(self, payload: RuleMutationPayload) -> str:
        # 1. Escudo em Camada Python multi-processo contra saturação do Neo4j
        async with InterProcessTenantLock(payload.client_uid):
            now = int(time.time())
            try:
                # 2. Só toma uma conexão do pool se o semáforo ASGI liberou
                async with self.driver.session() as session:
                    async def _work(tx):
                        res = await tx.run(
                            CYPHER_MUTATION_UNIFIED,
                            client_uid=payload.client_uid,
                            new_rate=payload.new_tariff,
                            effective_date=payload.normalized_effective_timestamp,
                            expected_version=payload.expected_version,
                            now=now
                        )
                        return await res.single()
                        
                    record = await session.execute_write(_work)
                    if not record:
                        raise Exception("Client não encontrado para Gênese/Mutação.")
                    return record["new.uid"]
            except Neo4jError as e:
                raise translate_apoc_error(e)

    async def resolve_active_rule_at(self, payload: ForensicAuditPayload) -> Optional[dict]:
        # Segurança geopolítica e tipagem forense já garantidas na borda Pydantic
        invoice_timestamp = payload.normalized_target_timestamp
        
        query = """
        MATCH (c:Client {uid: $client_uid})-[:ACTIVE_RULE]->(current_rule:BillingRule)
        MATCH (current_rule)-[:PREVIOUS_VERSION*0..]->(historical_rule:BillingRule)
        WHERE historical_rule.valid_from <= $invoice_date 
          AND (historical_rule.valid_to IS NULL OR historical_rule.valid_to > $invoice_date)
        RETURN historical_rule LIMIT 1
        """
        async with self.driver.session() as session:
            async def _work(tx):
                res = await tx.run(query, client_uid=payload.client_uid, invoice_date=invoice_timestamp)
                return await res.single()
                
            record = await session.execute_read(_work)
            
            if record:
                return dict(record["historical_rule"])
            return None
