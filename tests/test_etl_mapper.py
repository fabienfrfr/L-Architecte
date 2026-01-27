import pytest
import os
from apps.architect.ingestion.etl_mapper import ETLMapper

# We assume a test database is running or mocked
@pytest.fixture
def mapper():
    return ETLMapper(db_auth={"user": "root", "password": "password"})

def test_extract_returns_content(mapper):
    """Test the [E]xtract phase"""
    # Use a small sample pdf for testing
    path = "tests/data/sample.pdf"
    if not os.path.exists(path):
        pytest.skip("Sample PDF not found")
        
    pages = mapper._extract(path)
    assert len(pages) > 0
    assert "content" in pages[0]
    assert isinstance(pages[0]["page_num"], int)

def test_transform_detects_entities(mapper):
    """Test the [T]ransform phase with French and English entities"""
    raw_data = [
        {"page_num": 1, "content": "Le système LMS doit être déployé sur Kubernetes."},
        {"page_num": 2, "content": "The project uses Python and ArangoDB for data storage."}
    ]
    
    transformed = mapper._transform(raw_data)
    
    assert len(transformed) == 2
    # Verify entity detection (checking for common tech terms)
    all_entities = [ent["text"].upper() for page in transformed for ent in page["entities"]]
    assert any("LMS" in e for e in all_entities)
    assert any("KUBERNETES" in e for e in all_entities)
    assert any("PYTHON" in e for e in all_entities)

def test_load_to_arangodb(mapper, mocker):
    """Test the [L]oad phase (Mocking ArangoDB calls)"""
    mock_import = mocker.patch.object(mapper.db.collection('Chunks'), 'import_bulk')
    mock_has_ent = mocker.patch.object(mapper.db.collection('Entities'), 'has', return_value=False)
    mock_insert_ent = mocker.patch.object(mapper.db.collection('Entities'), 'insert')

    test_data = [{
        "text": "Sample text",
        "metadata": {"page": 1},
        "entities": [{"text": "LMS", "label": "PRODUCT"}]
    }]

    mapper._load(test_data, "test.pdf")

    assert mock_import.called
    assert mock_insert_ent.called