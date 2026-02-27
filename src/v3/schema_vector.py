
"""
Vector Schema (Horizon 4)
Defines the `Chunk` node for Hybrid RAG.
"""
from typing import List, Optional, Any
from pydantic import Field
from src.v3.schema import BaseNode

class Chunk(BaseNode):
    """
    Represents a semantic chunk of text with a vector embedding.
    Linked to a Document via [:HAS_CHUNK].
    """
    labels: List[str] = ["Chunk"]
    uid: str = Field(..., description="Unique ID of the chunk (UUID)")
    
    # Core Data
    text: str = Field(..., description="The text content of the chunk")
    embedding: Optional[List[float]] = Field(None, description="Vector representation (e.g., 1536 dims)")
    
    # Metadata
    index: int = Field(0, description="Order of the chunk in the document")
    source_sha256: str = Field(..., description="SHA256 of the parent document")
    
    # Context
    project: str = Field("MenirVital", description="Project namespace")

    @property
    def properties(self) -> dict:
        """Returns properties for Neo4j."""
        return {
            "text": self.text,
            "index": self.index,
            "project": self.project,
            "source": self.source_sha256
            # Note: Embedding is stored as a vector property, usually handled specifically
        }
