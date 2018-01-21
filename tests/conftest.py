from lib.models.classifications import Classifications
from panoptes_client import Classification
import json
import pytest

@pytest.fixture
def pages_raw_subject_ids():
    return [14813280, 14813281, 12992773, 12993513, 12993899, 5823821, 5823822, 12992657,
        12992851, 12993844, 12996372, 14813279]

@pytest.fixture
def panoptes_classification_models():
    fixtures_fpath = 'tests/fixtures/classifications/railroad_workflow_classifications_raw.json'
    with open(fixtures_fpath, 'r') as content_file:
        classifications_json = content_file.read()
    classifications_raw = json.JSONDecoder().decode(classifications_json)
    classifications_objects = []
    for c_raw in classifications_raw:
        classifications_objects.append(Classification(raw=c_raw))
    return classifications_objects
