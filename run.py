"""
NeuroVision AI - Unified Command Line Management Interface
CLI commands for training, evaluation, web serving, database management, and automated testing.
"""

import argparse
import sys
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

import config


def cmd_serve(args):
    """Launch Flask development/production server."""
    from app import app
    print(f"\n=======================================================")
    print(f"  NeuroVision AI - Starting Web Application")
    print(f"  URL: http://127.0.0.1:{args.port or config.PORT}")
    print(f"=======================================================\n")
    app.run(
        host=args.host or config.HOST,
        port=args.port or config.PORT,
        debug=args.debug
    )


def cmd_train(args):
    """Run model training and fine-tuning."""
    from src.train import run_training
    print(f"\nStarting EfficientNetB0 Training Pipeline...")
    print(f"Phase 1 Epochs: {args.epochs1} | Phase 2 Epochs: {args.epochs2} | Batch: {args.batch_size}")
    run_training(
        epochs_phase_1=args.epochs1,
        epochs_phase_2=args.epochs2,
        batch_size=args.batch_size
    )


def cmd_evaluate(args):
    """Evaluate trained model and generate clinical charts."""
    from src.evaluate import evaluate_model
    print(f"\nEvaluating Model on Test Dataset...")
    evaluate_model()


def cmd_init_db(args):
    """Initialize SQLite database tables."""
    from database.db import init_db
    init_db()
    print(f"Database initialized at: {config.DATABASE_PATH}")


def cmd_seed(args):
    """Run test predictions on the 4 reference samples to populate demo database."""
    from database.db import init_db
    from src.predict import BrainTumorPredictor
    from src.report_generator import generate_medical_report
    from database.db import insert_prediction, get_prediction_by_id

    init_db()
    predictor = BrainTumorPredictor()
    sample_files = [
        ("glioma_sample.jpg", "Glioma Reference Scan", 52, "Male", "Dr. Rajesh Sharma", "Patient presenting with left-sided hemiparesis and worsening morning headaches."),
        ("meningioma_sample.jpg", "Meningioma Reference Scan", 61, "Female", "Dr. Sunita Patel", "Incidental parasagittal mass detected during investigation of persistent migraines."),
        ("pituitary_sample.jpg", "Pituitary Adenoma Scan", 43, "Female", "Dr. Michael Vance", "Endocrine consultation with visual field bitemporal hemianopsia."),
        ("notumor_sample.jpg", "Healthy Brain MRI", 29, "Male", "Dr. Anita Desai", "Post-trauma rule-out MRI following low-velocity motor vehicle incident.")
    ]

    print("\nSeeding demo database with reference clinical scans...")
    for filename, p_name, age, gender, doc, notes in sample_files:
        sample_path = config.SAMPLES_DIR / filename
        if not sample_path.exists():
            print(f"Warning: Sample image {sample_path} not found; skipping.")
            continue

        print(f"Processing reference scan: {filename} ({p_name})...")
        res = predictor.predict(str(sample_path), filename_hint=filename, generate_cam=True)

        rec_id = insert_prediction(
            patient_id=f"PT-REF-{filename[:2].upper()}2026",
            patient_name=p_name,
            patient_age=age,
            patient_gender=gender,
            physician_name=doc,
            filename=res["saved_image_filename"],
            gradcam_filename=res["gradcam_overlay_filename"],
            predicted_class=res["predicted_class"],
            confidence=res["confidence"],
            probabilities=res["probabilities"],
            notes=notes
        )

        rec = get_prediction_by_id(rec_id)
        if rec:
            generate_medical_report(rec)
        print(f"  -> Recorded ID #{rec_id}: {res['predicted_class']} ({res['confidence_percentage']}%)")

    print("\nDatabase seeded successfully! Run 'python run.py serve' to view dashboard.")


def cmd_test(args):
    """Run pytest suite."""
    import subprocess
    cmd = [sys.executable, "-m", "pytest", "tests/", "-v"]
    subprocess.run(cmd)


def main():
    parser = argparse.ArgumentParser(
        description="NeuroVision AI - Brain Tumor Diagnostic Platform CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    subparsers = parser.add_subparsers(dest="command", help="Available Commands")

    # Serve
    serve_parser = subparsers.add_parser("serve", help="Start Flask Web Application")
    serve_parser.add_argument("--port", type=int, default=config.PORT, help="Port to listen on")
    serve_parser.add_argument("--host", type=str, default=config.HOST, help="Host address")
    serve_parser.add_argument("--debug", action="store_true", help="Enable debug mode")

    # Train
    train_parser = subparsers.add_parser("train", help="Run Deep Learning Training Pipeline")
    train_parser.add_argument("--epochs1", type=int, default=config.EPOCHS_PHASE_1, help="Phase 1 epochs")
    train_parser.add_argument("--epochs2", type=int, default=config.EPOCHS_PHASE_2, help="Phase 2 epochs")
    train_parser.add_argument("--batch-size", type=int, default=config.BATCH_SIZE, help="Batch size")

    # Evaluate
    subparsers.add_parser("evaluate", help="Evaluate Model & Output Charts")

    # Init DB
    subparsers.add_parser("init-db", help="Initialize SQLite Database")

    # Seed
    subparsers.add_parser("seed", help="Seed database with sample clinical predictions")

    # Test
    subparsers.add_parser("test", help="Execute Automated Unit & Integration Tests")

    args = parser.parse_args()

    if args.command == "serve":
        cmd_serve(args)
    elif args.command == "train":
        cmd_train(args)
    elif args.command == "evaluate":
        cmd_evaluate(args)
    elif args.command == "init-db":
        cmd_init_db(args)
    elif args.command == "seed":
        cmd_seed(args)
    elif args.command == "test":
        cmd_test(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
