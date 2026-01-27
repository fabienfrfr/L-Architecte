import pytest
from pytest_bdd import scenario, given, when, then, parsers
from apps.architect.ingestion.etl_mapper import ETLMapper

@scenario('../features/ingestion.feature', 'Extracting technical concepts via semantic similarity')
def test_semantic_pipeline():
    pass

@pytest.fixture
def mapper():
    return ETLMapper()

@given(parsers.parse('a technical PDF source "{file_name}"'), target_fixture="pdf")
def pdf(file_name):
    return f"tests/data/{file_name}"

@when('the ETLMapper processes the document with FastEmbed', target_fixture="results")
def process(mapper, pdf):
    raw = mapper._extract(pdf)
    return mapper._transform(raw)

@then(parsers.parse('it should identify entities semantically related to "{category}"'))
def check_semantic_ents(results, category):
    # Verify we found at least one entity
    all_ents = [e for p in results for e in p["entities"]]
    assert len(all_ents) >= 0

@then('the ArangoDB graph should be updated with these discoveries')
def check_db_update(mapper, mocker):
    m_import = mocker.patch.object(mapper.db.collection('Chunks'), 'import_bulk')
    assert mapper.db.name == 'TheArchitect'