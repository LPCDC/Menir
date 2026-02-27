"""
Menir v5.1 Runner Module (Async & Modular)
Asynchronous Orchestrator with Strategy Pattern Skills for LGPD/nFADP Compliance.
"""
import os
import time
import shutil
import logging
import hashlib
import asyncio
from datetime import datetime
from dotenv import load_dotenv
from typing import List, Union
from pydantic import ValidationError
from dataclasses import dataclass
from abc import ABC, abstractmethod

from pypdf import PdfReader

from src.v3.menir_bridge import MenirBridge
from src.v3.menir_intel import MenirIntel
from src.v3.tenant_middleware import current_tenant_id
from src.v3.menir_audit import MenirAudit, AuditWriteError
from src.v3.menir_drive import MenirDrive
from src.v3.schema import Document, Person, Organization, Relationship, BaseNode, GenericNode

# Setup Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("MenirRunner")

# Configuration
load_dotenv(override=True)


@dataclass
class SkillResult:
    """Standardized output for all Menir Skills."""
    success: bool
    nodes_and_edges: List[Union[BaseNode, Relationship]]
    message: str
    doc_hash: str = "N/A"


class MenirSkill(ABC):
    """Abstract Base Class for all ingestion skills."""
    @property
    @abstractmethod
    def supported_types(self) -> List[str]:
        """Returns a list of supported file extensions, e.g., ['.pdf']"""
        pass

    @abstractmethod
    async def process(self, file_path: str, tenant_id: str) -> SkillResult:
        """Asynchronously process the file and return structured nodes and relationships."""
        pass


class PdfAgtSkill(MenirSkill):
    """Legacy Menir logic encapsulated as a PDF Skill."""
    def __init__(self, bridge: MenirBridge, intel: MenirIntel):
        self.bridge = bridge
        self.intel = intel

    @property
    def supported_types(self) -> List[str]:
        return [".pdf"]

    async def process(self, file_path: str, tenant_id: str) -> SkillResult:
        nodes_and_edges = []
        filename = os.path.basename(file_path)
        
        def calc_sha():
            sha256_hash = hashlib.sha256()
            with open(file_path, "rb") as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            return sha256_hash.hexdigest()
        
        try:
            doc_hash = await asyncio.to_thread(calc_sha)
        except Exception as e:
            return SkillResult(success=False, nodes_and_edges=[], message=f"Hashing failed: {e}")
        
        try:
            # Recovery Mode Check
            exists = await asyncio.to_thread(self.bridge.check_document_exists, doc_hash, tenant_id)
            if exists:
                return SkillResult(success=False, nodes_and_edges=[], message="Duplicate Hash: Already in Graph", doc_hash=doc_hash)

            # Read PDF
            def read_pdf():
                reader = PdfReader(file_path)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() + "\n"
                meta = reader.metadata
                meta_author = meta.author if meta and meta.author else None
                return text, meta_author
                
            text, meta_author = await asyncio.to_thread(read_pdf)

            # Intel Extraction
            extraction = await asyncio.to_thread(self.intel.extract, text, tenant_id, doc_hash)
            
            # Hybrid RAG Chunking
            if len(text) > 100:
                logger.info("🧩 Chunking Document for Vector Index...")
                chunk_size = 1000
                overlap = 100
                chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size - overlap)]
                
                for i, chunk_text in enumerate(chunks):
                    try:
                        embedding = await asyncio.to_thread(self.intel.generate_embedding, chunk_text)
                        if embedding:
                            chunk_id = f"{doc_hash}_chunk_{i}"
                            await asyncio.to_thread(
                                self.bridge.merge_chunk, 
                                chunk_id, chunk_text, embedding, doc_hash, tenant_id
                            )
                    except Exception as cx:
                        logger.warning(f"Chunking Error (Skipped Chunk {i}): {cx}")
                logger.info(f"✅ Indexed {len(chunks)} Vector Chunks.")

            # Append Document Node
            doc_node = Document(
                filename=filename,
                sha256=doc_hash,
                project=tenant_id,
                status="processed"
            )
            nodes_and_edges.append(doc_node)

            # Link Metadata Author
            if meta_author:
                await asyncio.to_thread(self.bridge.link_author, doc_hash, meta_author, tenant_id)

            # Parse Extracted Nodes
            for n_dict in extraction.get("nodes", []):
                try:
                    label = n_dict.get("label")
                    props = n_dict.get("properties", {})
                    if label == "Person":
                        node_obj = Person(name=n_dict["name"], project=tenant_id, role=props.get("role"), context=props.get("context", "Fictional"))
                    elif label == "Organization":
                        node_obj = Organization(name=n_dict["name"], project=tenant_id, industry=props.get("industry"))
                    else:
                        node_obj = GenericNode(name=n_dict["name"], project=tenant_id, labels=[label] if label else ["Concept"], properties=props)
                    nodes_and_edges.append(node_obj)
                except ValidationError as ve:
                    logger.warning(f"Validation Reject (Node): {n_dict.get('name', 'Unknown')} - {ve}")

            # Parse Extracted Relationships
            for r_dict in extraction.get("edges", []):
                try:
                    rel = Relationship(
                        source_uid=r_dict["from_key"],
                        target_uid=r_dict["to_key"],
                        relation_type=r_dict["type"].upper(),
                        properties=r_dict.get("properties", {})
                    )
                    rel.properties['project'] = tenant_id
                    nodes_and_edges.append(rel)
                except ValidationError as ve:
                    logger.warning(f"Validation Reject (Rel): {ve}")

            # Automated PROV-O Lineage
            def create_prov_o():
                with self.bridge.driver.session() as session:
                    safe_tenant = str(tenant_id).replace("`", "")
                    session.run(f"""
                    MATCH (doc:Document:`{safe_tenant}` {{sha256: $doc_hash}})
                    MATCH (luiz:Person:Root:`{safe_tenant}` {{name: 'Luiz'}})
                    MERGE (ev:Event:`{safe_tenant}` {{name: 'Auto-Ingestion: ' + $filename}})
                    SET ev.timestamp = datetime()
                    MERGE (ev)-[:PRODUCED]->(doc)
                    MERGE (luiz)-[:PARTICIPATED_IN {{role: 'System Operator'}}]->(ev)
                    """, doc_hash=doc_hash, filename=filename)
            
            try:
                await asyncio.to_thread(create_prov_o)
            except Exception as e:
                logger.warning(f"PROV-O Lineage Error: {e}")

            return SkillResult(
                success=True, 
                nodes_and_edges=nodes_and_edges, 
                message=f"Successfully extracted {len(nodes_and_edges)} entities and relationships.", 
                doc_hash=doc_hash
            )

        except Exception as e:
            return SkillResult(success=False, nodes_and_edges=[], message=f"Extraction failed: {str(e)}", doc_hash=doc_hash)


class AsyncRunner:
    """Asynchronous Orchestrator for the Menir Pipeline."""
    def __init__(self, project_name="Menir_V4_Hybrid", max_workers: int = 3):
        self.project_name = project_name
        self.inbox_dir = "Menir_Inbox"
        self.archive_dir = "Menir_Inbox/Archive"
        self.quarantine_dir = "Menir_Inbox/Quarantine"
        self.max_workers = max_workers
        
        self.bridge = None
        self.intel = None
        self.audit = None
        self.drive = None
        
        self.file_queue: asyncio.Queue = asyncio.Queue()
        self.skills: List[MenirSkill] = []
        self.processing_files = set()
        
        self.ensure_dirs()

    def ensure_dirs(self):
        for d in [self.inbox_dir, self.archive_dir, self.quarantine_dir]:
            os.makedirs(d, exist_ok=True)

    def move_file(self, src, dest_folder, new_name=None):
        if not os.path.exists(dest_folder):
            os.makedirs(dest_folder)
        filename = new_name if new_name else os.path.basename(src)
        dst = os.path.join(dest_folder, filename)
        if os.path.exists(dst):
            base, ext = os.path.splitext(filename)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            dst = os.path.join(dest_folder, f"{base}_{timestamp}{ext}")
        shutil.move(src, dst)
        return dst

    def initialize_services(self):
        logger.info("Initializing Bridge (Cloud)...")
        self.bridge = MenirBridge()
        self.bridge.init_vector_index()
        
        logger.info("Initializing Inbox Drive Sync...")
        self.drive = MenirDrive()
        
        logger.info("Initializing Intel...")
        self.intel = MenirIntel(os.getenv("GOOGLE_API_KEY"))
        
        logger.info("Initializing Audit...")
        fake_json = os.getenv("GOOGLE_SHEETS_CREDENTIALS_JSON", "token.json") 
        self.audit = MenirAudit(
            fake_json if os.path.exists(fake_json) else None,
            os.getenv("MENIR_AUDIT_SHEET_ID"),
            os.getenv("MENIR_AUDIT_TAB_NAME", "Audit_V3")
        )
        try:
            self.audit._connect() 
        except:
             logger.warning("Audit Connect Failed. Continuing in Degraded Mode.")
             
        # Register default native skills
        self.register_skill(PdfAgtSkill(self.bridge, self.intel))

    def register_skill(self, skill: MenirSkill):
        self.skills.append(skill)

    def _get_skill_for_file(self, file_path: str) -> MenirSkill:
        ext = file_path.lower()[file_path.rfind("."):] if "." in file_path else ""
        for skill in self.skills:
            if ext in skill.supported_types:
                return skill
        raise ValueError(f"No registered skill supports '{ext}'")

    async def _worker(self):
        """Worker to consume queue files asynchronously."""
        while True:
            file_path, tenant_id, filename = await self.file_queue.get()
            logger.info(f"🚀 Worker picked up: {filename} for tenant: {tenant_id}")
            start_time = time.time()
            
            status = "FAILED"
            reason = "Unknown Error"
            doc_hash = "N/A"
            
            try:
                skill = self._get_skill_for_file(file_path)
                result: SkillResult = await skill.process(file_path, tenant_id)
                doc_hash = result.doc_hash
                
                if not result.success:
                    status = "SKIPPED" if "Duplicate" in result.message else "FAILED"
                    reason = result.message
                    logger.info(f"⏭️ {filename} - {reason}")
                    dest = self.archive_dir if status == "SKIPPED" else self.quarantine_dir
                    await asyncio.to_thread(self.move_file, file_path, dest)
                else:
                    # Persistence via hardened Tenant_ID rules using asyncio.to_thread
                    token = current_tenant_id.set("root_admin")
                    try:
                        for item in result.nodes_and_edges:
                            if isinstance(item, BaseNode):
                                await asyncio.to_thread(self.bridge.merge_node, item)
                            elif isinstance(item, Relationship):
                                await asyncio.to_thread(self.bridge.merge_relationship, item)
                    finally:
                        current_tenant_id.reset(token)
                        
                    status = "INDEXED"
                    reason = "SUCCESS"
                    logger.info(f"✅ {status}: {filename}. {result.message}")
                    await asyncio.to_thread(self.move_file, file_path, self.archive_dir)
                    
            except Exception as e:
                logger.error(f"Processing Error for {filename}: {e}")
                reason = str(e)
                try:
                    await asyncio.to_thread(self.move_file, file_path, self.quarantine_dir, filename + ".ERROR")
                except:
                    pass
            finally:
                duration = time.time() - start_time
                if self.audit:
                    audit_data = {
                        "timestamp": datetime.now().isoformat(),
                        "project": tenant_id,
                        "filename": filename,
                        "sha256": doc_hash, 
                        "status": status,
                        "reason": reason,
                        "duration_s": duration,
                        "model": "gemini-2.0-flash"
                    }
                    try:
                        await asyncio.to_thread(self.audit.audit_append_row, audit_data)
                    except Exception as ae:
                        logger.warning(f"Audit log failed: {ae}")
                
                self.processing_files.discard(filename)
                self.file_queue.task_done()

    async def _poll_directories(self):
        """Continuously pulls files from Inbox into the processing Queue."""
        while True:
            try:
                # Sync Cloud -> Local First
                await asyncio.to_thread(self.drive.sync, self.inbox_dir)
            except Exception as e:
                pass

            try:
                files = sorted([f for f in os.listdir(self.inbox_dir) if os.path.isfile(os.path.join(self.inbox_dir, f))])
                for f in files:
                    if f in self.processing_files or f.endswith(".ERROR") or f.endswith(".AUDIT_FAIL"):
                        continue
                    
                    self.processing_files.add(f)
                    filepath = os.path.join(self.inbox_dir, f)
                    
                    # Extract Project Scope (Tenant ID)
                    tenant_id = self.project_name
                    if "-" in f:
                        tenant_id = f.split("-")[0].strip()
                        
                    await self.file_queue.put((filepath, tenant_id, f))
            except Exception as e:
                pass
                
            await asyncio.sleep(5)

    async def run(self):
        self.initialize_services()
        logger.info(f"MENIR V5.1 ASYNC RUNNER ONLINE. Default Tenant: {self.project_name}")
        logger.info(f"Watching: {os.path.abspath(self.inbox_dir)}")

        # Start Workers and Poller
        workers = [asyncio.create_task(self._worker()) for _ in range(self.max_workers)]
        poller = asyncio.create_task(self._poll_directories())
        
        await asyncio.gather(poller, *workers)

    def shutdown(self):
        logger.info("Stopping Runner...")
        if self.bridge:
            self.bridge.close()

if __name__ == "__main__":
    runner = AsyncRunner()
    try:
        asyncio.run(runner.run())
    except KeyboardInterrupt:
        runner.shutdown()
    except Exception as e:
        logger.critical(f"FATAL SYSTEM CRASH: {e}")
        import traceback
        traceback.print_exc()
        runner.shutdown()
