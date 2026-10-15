"""
Automated unit tests for ReportLab clinical PDF report generation.
"""

import tempfile
from pathlib import Path
import pytest

from src.report_generator import generate_medical_report


def test_generate_medical_report():
    """Verify PDF medical report is generated on disk with valid file size."""
    with tempfile.TemporaryDirectory() as temp_dir:
        output_dir = Path(temp_dir)
        dummy_record = {
            "id": 999,
            "patient_id": "PT-TEST-999",
            "patient_name": "Alexander Hayes",
            "patient_age": 42,
            "patient_gender": "Male",
            "physician_name": "Dr. Sarah Lin",
            "filename": "sample_scan.jpg",
            "gradcam_filename": "sample_cam.jpg",
            "predicted_class": "Glioma",
            "confidence": 0.985,
            "probabilities": {
                "Glioma": 98.5,
                "Meningioma": 1.0,
                "No Tumor": 0.2,
                "Pituitary": 0.3
            },
            "notes": "Patient presents with persistent severe headaches and localized dizziness.",
            "created_at": "2026-10-15 10:30:00"
        }

        pdf_path = generate_medical_report(dummy_record, output_dir=output_dir)

        assert pdf_path is not None
        assert Path(pdf_path).exists()
        assert Path(pdf_path).suffix == ".pdf"
        assert Path(pdf_path).stat().st_size > 1000  # Non-trivial PDF output
