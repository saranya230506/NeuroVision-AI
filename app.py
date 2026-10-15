"""
NeuroVision AI - Main Flask Web Application & REST API
Integrates Deep Learning, Explainable AI (Grad-CAM), SQLite Persistence,
and Automated Clinical Medical Report Generation.
"""

import json
import logging
import os
from pathlib import Path
from typing import Any, Dict

from flask import (
    Flask,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    send_file,
    url_for
)
from werkzeug.utils import secure_filename

import config
from database.db import (
    clear_history,
    delete_prediction,
    get_all_predictions,
    get_prediction_by_id,
    get_statistics,
    init_db,
    insert_prediction
)
from src.predict import BrainTumorPredictor
from src.report_generator import generate_medical_report
from src.utils import allowed_file, generate_unique_filename

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("NeuroVision.App")

# Initialize Flask App
app = Flask(
    __name__,
    static_folder="static",
    template_folder="templates"
)
app.config["SECRET_KEY"] = config.SECRET_KEY
app.config["MAX_CONTENT_LENGTH"] = config.MAX_CONTENT_LENGTH
app.config["UPLOAD_FOLDER"] = str(config.UPLOADS_DIR)

# Initialize Database Schema
init_db()


# ==========================================
# Frontend Page Routes
# ==========================================

@app.route("/")
def index():
    """Home / Landing Page showcasing system capabilities, live stats & tech stack."""
    stats = get_statistics()
    return render_template("index.html", stats=stats, config=config)


@app.route("/upload")
def upload_page():
    """MRI Scanner & Diagnostic Upload workspace."""
    return render_template("upload.html", config=config)


@app.route("/dashboard")
def dashboard_page():
    """Clinical Analytics Dashboard displaying model performance & scan metrics."""
    stats = get_statistics()
    return render_template("dashboard.html", stats=stats, config=config)


@app.route("/history")
def history_page():
    """Patient Scan History Table with search, class filtering, and report downloads."""
    query = request.args.get("q", "")
    class_filter = request.args.get("class", "all")
    records = get_all_predictions(search_query=query, class_filter=class_filter, limit=200)
    return render_template(
        "history.html",
        records=records,
        current_query=query,
        current_filter=class_filter,
        config=config
    )


@app.route("/report/<int:prediction_id>")
def report_page(prediction_id: int):
    """Interactive in-browser medical diagnostic report view."""
    record = get_prediction_by_id(prediction_id)
    if not record:
        flash("Medical diagnostic record not found.", "warning")
        return redirect(url_for("history_page"))

    meta = config.CLASS_METADATA.get(record["predicted_class"], {})
    return render_template("report_view.html", record=record, meta=meta, config=config)


@app.route("/download-report/<int:prediction_id>")
def download_report(prediction_id: int):
    """Generate or retrieve and stream clinical PDF report."""
    record = get_prediction_by_id(prediction_id)
    if not record:
        return jsonify({"error": "Diagnostic record not found"}), 404

    pdf_filename = f"report_{prediction_id}.pdf"
    pdf_path = config.REPORTS_DIR / pdf_filename

    if not pdf_path.exists():
        try:
            generate_medical_report(record, output_dir=config.REPORTS_DIR)
        except Exception as e:
            logger.error("Failed to generate PDF report: %s", e)
            return jsonify({"error": f"Failed to generate PDF: {str(e)}"}), 500

    return send_file(
        str(pdf_path),
        mimetype="application/pdf",
        as_attachment=True,
        download_name=f"NeuroVision_Report_Patient_{record.get('patient_id', prediction_id)}.pdf"
    )


@app.route("/about")
def about_page():
    """Technical architecture, AI explainability, and IBM SkillsBuild internship details."""
    metrics_data = {}
    if config.METRICS_PATH.exists():
        try:
            with open(config.METRICS_PATH, "r", encoding="utf-8") as f:
                metrics_data = json.load(f)
        except Exception:
            pass
    return render_template("about.html", metrics=metrics_data, config=config)


# ==========================================
# REST API Endpoints
# ==========================================

@app.route("/api/predict", methods=["POST"])
def api_predict():
    """
    Primary inference endpoint:
    Accepts multipart/form-data:
      - 'image': File
      - 'patient_name': Optional[str]
      - 'patient_id': Optional[str]
      - 'patient_age': Optional[int]
      - 'patient_gender': Optional[str]
      - 'physician_name': Optional[str]
      - 'notes': Optional[str]
    Returns comprehensive diagnostic prediction & Grad-CAM visual output.
    """
    if "image" not in request.files:
        return jsonify({"success": False, "error": "No image file provided in request."}), 400

    file = request.files["image"]
    if file.filename == "":
        return jsonify({"success": False, "error": "Empty filename submitted."}), 400

    if not allowed_file(file.filename):
        return jsonify({
            "success": False,
            "error": f"Unsupported file type. Allowed extensions: {', '.join(config.ALLOWED_EXTENSIONS)}"
        }), 400

    try:
        # Extract patient metadata
        patient_name = request.form.get("patient_name", "Anonymous Patient").strip()
        patient_id = request.form.get("patient_id", "").strip()
        patient_age = request.form.get("patient_age")
        patient_gender = request.form.get("patient_gender", "Not Specified").strip()
        physician_name = request.form.get("physician_name", "Dr. AI Diagnostic System").strip()
        notes = request.form.get("notes", "").strip()

        # Generate default patient ID if omitted
        if not patient_id:
            import random
            patient_id = f"PT-{random.randint(10000, 99999)}"

        # Run Prediction & Grad-CAM
        predictor = BrainTumorPredictor()
        file_bytes = file.read()
        prediction_result = predictor.predict(
            image_source=file_bytes,
            filename_hint=file.filename,
            generate_cam=True
        )

        # Store in SQLite Database
        record_id = insert_prediction(
            patient_id=patient_id,
            patient_name=patient_name,
            patient_age=int(patient_age) if patient_age and str(patient_age).isdigit() else None,
            patient_gender=patient_gender,
            physician_name=physician_name,
            filename=prediction_result["saved_image_filename"],
            gradcam_filename=prediction_result["gradcam_overlay_filename"],
            predicted_class=prediction_result["predicted_class"],
            confidence=prediction_result["confidence"],
            probabilities=prediction_result["probabilities"],
            notes=notes
        )

        # Pre-generate PDF report
        try:
            full_record = get_prediction_by_id(record_id)
            if full_record:
                generate_medical_report(full_record)
        except Exception as rep_err:
            logger.warning("Background PDF generation deferred: %s", rep_err)

        return jsonify({
            "success": True,
            "prediction_id": record_id,
            "patient_id": patient_id,
            "patient_name": patient_name,
            "predicted_class": prediction_result["predicted_class"],
            "confidence": prediction_result["confidence"],
            "confidence_percentage": prediction_result["confidence_percentage"],
            "probabilities": prediction_result["probabilities"],
            "metadata": prediction_result["metadata"],
            "image_url": url_for("static", filename=f"uploads/{prediction_result['saved_image_filename']}"),
            "gradcam_overlay_url": url_for("static", filename=f"gradcam_outputs/{prediction_result['gradcam_overlay_filename']}") if prediction_result['gradcam_overlay_filename'] else None,
            "gradcam_sbs_url": url_for("static", filename=f"gradcam_outputs/{prediction_result['gradcam_sbs_filename']}") if prediction_result['gradcam_sbs_filename'] else None,
            "report_url": url_for("report_page", prediction_id=record_id),
            "pdf_url": url_for("download_report", prediction_id=record_id)
        }), 200

    except Exception as e:
        logger.error("Error processing MRI prediction: %s", e, exc_info=True)
        return jsonify({"success": False, "error": f"Internal inference error: {str(e)}"}), 500


@app.route("/api/sample/<sample_type>", methods=["POST", "GET"])
def api_sample_prediction(sample_type: str):
    """
    Run prediction on one of the pre-bundled reference MRI scans
    (glioma, meningioma, notumor, pituitary) for 1-click zero-upload demonstration.
    """
    sample_type = sample_type.lower().strip()
    valid_samples = {
        "glioma": "glioma_sample.jpg",
        "meningioma": "meningioma_sample.jpg",
        "notumor": "notumor_sample.jpg",
        "pituitary": "pituitary_sample.jpg"
    }

    if sample_type not in valid_samples:
        return jsonify({"success": False, "error": f"Invalid sample type '{sample_type}'."}), 400

    sample_filename = valid_samples[sample_type]
    sample_path = config.SAMPLES_DIR / sample_filename

    if not sample_path.exists():
        return jsonify({"success": False, "error": f"Sample image file not found on disk."}), 404

    try:
        import random
        predictor = BrainTumorPredictor()
        prediction_result = predictor.predict(
            image_source=str(sample_path),
            filename_hint=sample_filename,
            generate_cam=True
        )

        patient_id = f"REF-{sample_type.upper()}-{random.randint(100, 999)}"
        record_id = insert_prediction(
            patient_id=patient_id,
            patient_name=f"Sample Reference ({sample_type.capitalize()})",
            patient_age=48,
            patient_gender="Female" if sample_type in ("meningioma", "pituitary") else "Male",
            physician_name="Dr. Automated Reference Protocol",
            filename=prediction_result["saved_image_filename"],
            gradcam_filename=prediction_result["gradcam_overlay_filename"],
            predicted_class=prediction_result["predicted_class"],
            confidence=prediction_result["confidence"],
            probabilities=prediction_result["probabilities"],
            notes=f"Automated benchmark test using verified reference {sample_type} brain MRI scan."
        )

        full_record = get_prediction_by_id(record_id)
        if full_record:
            generate_medical_report(full_record)

        return jsonify({
            "success": True,
            "prediction_id": record_id,
            "patient_id": patient_id,
            "patient_name": f"Sample Reference ({sample_type.capitalize()})",
            "predicted_class": prediction_result["predicted_class"],
            "confidence": prediction_result["confidence"],
            "confidence_percentage": prediction_result["confidence_percentage"],
            "probabilities": prediction_result["probabilities"],
            "metadata": prediction_result["metadata"],
            "image_url": url_for("static", filename=f"uploads/{prediction_result['saved_image_filename']}"),
            "gradcam_overlay_url": url_for("static", filename=f"gradcam_outputs/{prediction_result['gradcam_overlay_filename']}"),
            "gradcam_sbs_url": url_for("static", filename=f"gradcam_outputs/{prediction_result['gradcam_sbs_filename']}"),
            "report_url": url_for("report_page", prediction_id=record_id),
            "pdf_url": url_for("download_report", prediction_id=record_id)
        }), 200

    except Exception as e:
        logger.error("Failed sample analysis: %s", e)
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/history", methods=["GET"])
def api_get_history():
    """Retrieve filtered list of past scan records."""
    query = request.args.get("q", "")
    class_filter = request.args.get("class", "all")
    limit = int(request.args.get("limit", 100))
    offset = int(request.args.get("offset", 0))

    records = get_all_predictions(search_query=query, class_filter=class_filter, limit=limit, offset=offset)
    return jsonify({"success": True, "count": len(records), "records": records}), 200


@app.route("/api/history/<int:record_id>", methods=["DELETE"])
def api_delete_history_item(record_id: int):
    """Delete a single diagnostic record."""
    success = delete_prediction(record_id)
    if success:
        return jsonify({"success": True, "message": f"Record #{record_id} deleted successfully."}), 200
    return jsonify({"success": False, "error": "Record not found or already deleted."}), 404


@app.route("/api/history/clear", methods=["POST"])
def api_clear_history():
    """Purge all records from database."""
    count = clear_history()
    return jsonify({"success": True, "message": f"Cleared {count} records."}), 200


@app.route("/api/stats", methods=["GET"])
def api_get_stats():
    """Retrieve statistical aggregation for charts and KPI cards."""
    stats = get_statistics()
    return jsonify({"success": True, "stats": stats}), 200


@app.route("/api/health", methods=["GET"])
def healthcheck():
    """Container & service health check endpoint."""
    return jsonify({
        "status": "healthy",
        "service": config.PROJECT_NAME,
        "version": config.PROJECT_VERSION,
        "model_loaded": BrainTumorPredictor._instance is not None
    }), 200


# ==========================================
# Error Handlers
# ==========================================

@app.errorhandler(413)
def request_entity_too_large(error):
    return jsonify({
        "success": False,
        "error": "The uploaded file exceeds the 16 MB limit. Please upload a standard brain MRI image."
    }), 413


@app.errorhandler(404)
def not_found_error(error):
    if request.path.startswith("/api/"):
        return jsonify({"success": False, "error": "API endpoint not found."}), 404
    return render_template("index.html", error_message="Page not found"), 404


@app.errorhandler(500)
def internal_error(error):
    if request.path.startswith("/api/"):
        return jsonify({"success": False, "error": "Internal server error occurred."}), 500
    return render_template("index.html", error_message="An internal server error occurred"), 500


if __name__ == "__main__":
    logger.info("Starting %s on %s:%d (Debug=%s)", config.PROJECT_NAME, config.HOST, config.PORT, config.DEBUG)
    app.run(host=config.HOST, port=config.PORT, debug=config.DEBUG)
