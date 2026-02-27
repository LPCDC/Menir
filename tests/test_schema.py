
import pytest
from pydantic import ValidationError
from src.v3.schema import Person, Document, Organization

def test_person_capitalization():
    """Person names must start with a capital letter."""
    # Valid
    p = Person(name="Luiz", project="Test")
    assert p.name == "Luiz"
    
    # Invalid (lowercase)
    with pytest.raises(ValidationError) as excinfo:
        Person(name="luiz", project="Test")
    assert "start with a capital letter" in str(excinfo.value)

def test_document_validation():
    """Documents must have valid SHA256 and status."""
    # Valid
    valid_sha = "a" * 64
    d = Document(filename="test.pdf", sha256=valid_sha, project="Test", status="processed")
    assert d.status == "processed"

    # Invalid Hash
    with pytest.raises(ValidationError):
        Document(filename="test.pdf", sha256="bad_hash", project="Test")
    
    # Invalid Status
    with pytest.raises(ValidationError):
        Document(filename="test.pdf", sha256=valid_sha, project="Test", status="Exploded")

def test_organization_defaults():
    """Organization label should be auto-appended."""
    org = Organization(name="LibLabs", project="Test")
    assert "Organization" in org.labels
