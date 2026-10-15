"""
Automated unit tests for SQLite database operations.
"""

import tempfile
from pathlib import Path
import pytest

from database.db import (
    clear_history,
    delete_prediction,
    get_all_predictions,
    get_prediction_by_id,
    get_statistics,
    init_db,
    insert_prediction
)


@pytest.fixture
def temp_db():
    """Create a temporary test database file."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        temp_path = Path(f.name)
    init_db(temp_path)
    yield temp_path
    if temp_path.exists():
        temp_path.unlink()


def test_insert_and_get_prediction(temp_db):
    """Test inserting a record and retrieving it by ID."""
    rec_id = insert_prediction(
        patient_id="PT-TEST-001",
        patient_name="Jane Doe",
        patient_age=34,
        patient_gender="Female",
        physician_name="Dr. Smith",
        filename="test_scan.jpg",
        gradcam_filename="cam_test_scan.jpg",
        predicted_class="Glioma",
        confidence=0.965,
        probabilities={"Glioma": 96.5, "Meningioma": 2.1, "No Tumor": 0.4, "Pituitary": 1.0},
        notes="Suspected low-grade lesion.",
        db_path=temp_db
    )

    assert rec_id > 0

    record = get_prediction_by_id(rec_id, db_path=temp_db)
    assert record is not None
    assert record["patient_name"] == "Jane Doe"
    assert record["predicted_class"] == "Glioma"
    assert record["confidence"] == 0.965
    assert record["probabilities"]["Glioma"] == 96.5


def test_filter_and_search_predictions(temp_db):
    """Test search query and class filtering."""
    insert_prediction(
        patient_id="PT-101",
        patient_name="Arthur Pendelton",
        patient_age=50,
        patient_gender="Male",
        physician_name="Dr. House",
        filename="scan1.jpg",
        gradcam_filename="cam1.jpg",
        predicted_class="Meningioma",
        confidence=0.91,
        probabilities={"Meningioma": 91.0},
        notes="Frontal lobe mass",
        db_path=temp_db
    )

    results = get_all_predictions(search_query="Pendelton", db_path=temp_db)
    assert len(results) == 1
    assert results[0]["patient_name"] == "Arthur Pendelton"

    filtered = get_all_predictions(class_filter="Meningioma", db_path=temp_db)
    assert len(filtered) == 1

    empty_filter = get_all_predictions(class_filter="Pituitary", db_path=temp_db)
    assert len(empty_filter) == 0


def test_delete_and_clear_predictions(temp_db):
    """Test single record deletion and clearing all history."""
    r1 = insert_prediction(
        patient_id="PT-1", patient_name="P1", patient_age=25, patient_gender="M",
        physician_name="Dr. A", filename="s1.jpg", gradcam_filename="c1.jpg",
        predicted_class="No Tumor", confidence=0.99, probabilities={}, db_path=temp_db
    )

    deleted = delete_prediction(r1, db_path=temp_db)
    assert deleted is True
    assert get_prediction_by_id(r1, db_path=temp_db) is None

    # Insert two more and clear
    insert_prediction(patient_id="PT-2", patient_name="P2", patient_age=30, patient_gender="F", physician_name="Dr. B", filename="s2.jpg", gradcam_filename="c2.jpg", predicted_class="Glioma", confidence=0.95, probabilities={}, db_path=temp_db)
    insert_prediction(patient_id="PT-3", patient_name="P3", patient_age=40, patient_gender="M", physician_name="Dr. C", filename="s3.jpg", gradcam_filename="c3.jpg", predicted_class="Pituitary", confidence=0.97, probabilities={}, db_path=temp_db)

    count = clear_history(db_path=temp_db)
    assert count == 2
    assert len(get_all_predictions(db_path=temp_db)) == 0
