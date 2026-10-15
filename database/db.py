"""
NeuroVision AI - SQLite Database Access & Persistence Module
Manages patient scan histories, prediction classifications, confidence metrics,
and statistical aggregation for clinical dashboards.
"""

import json
import logging
import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Generator, List, Optional

import config

logger = logging.getLogger("NeuroVision.Database")


@contextmanager
def get_db_connection(db_path: Path = config.DATABASE_PATH) -> Generator[sqlite3.Connection, None, None]:
    """Context manager for thread-safe SQLite database connections."""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path), timeout=15.0)
    conn.row_factory = sqlite3.Row
    # Auto-ensure schema exists
    conn.execute("""
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id TEXT NOT NULL,
            patient_name TEXT NOT NULL,
            patient_age INTEGER,
            patient_gender TEXT,
            physician_name TEXT,
            filename TEXT NOT NULL,
            gradcam_filename TEXT,
            predicted_class TEXT NOT NULL,
            confidence REAL NOT NULL,
            probabilities TEXT NOT NULL,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_predictions_class ON predictions(predicted_class)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_predictions_patient ON predictions(patient_name)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_predictions_created ON predictions(created_at)")
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        logger.error("Database transaction rolled back due to error: %s", e)
        raise e
    finally:
        conn.close()


def init_db(db_path: Path = config.DATABASE_PATH) -> None:
    """Initialize the SQLite database schema and indices."""
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id TEXT NOT NULL,
                patient_name TEXT NOT NULL,
                patient_age INTEGER,
                patient_gender TEXT,
                physician_name TEXT,
                filename TEXT NOT NULL,
                gradcam_filename TEXT,
                predicted_class TEXT NOT NULL,
                confidence REAL NOT NULL,
                probabilities TEXT NOT NULL,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Performance indices for search and filtering
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_predictions_class ON predictions(predicted_class)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_predictions_patient ON predictions(patient_name)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_predictions_created ON predictions(created_at)")
        logger.info("Database initialized successfully at %s", db_path)


def insert_prediction(
    patient_id: str,
    patient_name: str,
    patient_age: Optional[int],
    patient_gender: Optional[str],
    physician_name: Optional[str],
    filename: str,
    gradcam_filename: Optional[str],
    predicted_class: str,
    confidence: float,
    probabilities: Dict[str, float],
    notes: Optional[str] = "",
    db_path: Path = config.DATABASE_PATH
) -> int:
    """
    Persist a newly analyzed MRI scan and its AI diagnostic outcome.

    Returns:
        The integer ID of the newly inserted record.
    """
    prob_json = json.dumps(probabilities)
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO predictions (
                patient_id, patient_name, patient_age, patient_gender,
                physician_name, filename, gradcam_filename,
                predicted_class, confidence, probabilities, notes, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            patient_id,
            patient_name.strip() if patient_name else "Anonymous Patient",
            int(patient_age) if patient_age is not None and str(patient_age).isdigit() else None,
            patient_gender.strip() if patient_gender else "Not Specified",
            physician_name.strip() if physician_name else "Dr. AI Diagnostic System",
            filename,
            gradcam_filename,
            predicted_class,
            float(confidence),
            prob_json,
            notes.strip() if notes else "",
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))
        new_id = cursor.lastrowid
        logger.info("Recorded diagnosis ID #%d for patient '%s' (%s: %.2f%%)",
                    new_id, patient_name, predicted_class, confidence * 100)
        return new_id


def get_all_predictions(
    search_query: Optional[str] = None,
    class_filter: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    db_path: Path = config.DATABASE_PATH
) -> List[Dict[str, Any]]:
    """
    Query records with optional search query and class filtering.
    """
    query = "SELECT * FROM predictions WHERE 1=1"
    params: List[Any] = []

    if class_filter and class_filter.strip() and class_filter.lower() != "all":
        query += " AND LOWER(predicted_class) = LOWER(?)"
        params.append(class_filter.strip())

    if search_query and search_query.strip():
        search_term = f"%{search_query.strip()}%"
        query += " AND (patient_name LIKE ? OR patient_id LIKE ? OR notes LIKE ? OR physician_name LIKE ?)"
        params.extend([search_term, search_term, search_term, search_term])

    query += " ORDER BY id DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])

    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        results = []
        for row in rows:
            record = dict(row)
            try:
                record["probabilities"] = json.loads(record["probabilities"])
            except Exception:
                record["probabilities"] = {}
            results.append(record)
        return results


def get_prediction_by_id(prediction_id: int, db_path: Path = config.DATABASE_PATH) -> Optional[Dict[str, Any]]:
    """Retrieve a single patient record by database ID."""
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM predictions WHERE id = ?", (prediction_id,))
        row = cursor.fetchone()
        if row is None:
            return None
        record = dict(row)
        try:
            record["probabilities"] = json.loads(record["probabilities"])
        except Exception:
            record["probabilities"] = {}
        return record


def delete_prediction(prediction_id: int, db_path: Path = config.DATABASE_PATH) -> bool:
    """Delete a single prediction record by ID."""
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM predictions WHERE id = ?", (prediction_id,))
        deleted = cursor.rowcount > 0
        if deleted:
            logger.info("Deleted prediction record #%d", prediction_id)
        return deleted


def clear_history(db_path: Path = config.DATABASE_PATH) -> int:
    """Purge all prediction records from history table."""
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM predictions")
        count = cursor.rowcount
        logger.info("Purged %d records from predictions database.", count)
        return count


def get_statistics(db_path: Path = config.DATABASE_PATH) -> Dict[str, Any]:
    """
    Compute aggregate statistics for clinical dashboard:
    - Total scans processed
    - Breakdown by class (Glioma, Meningioma, Pituitary, No Tumor)
    - Average diagnostic confidence
    - Recent scans timeline
    """
    stats: Dict[str, Any] = {
        "total_scans": 0,
        "class_counts": {"Glioma": 0, "Meningioma": 0, "No Tumor": 0, "Pituitary": 0},
        "avg_confidence": 0.0,
        "recent_predictions": []
    }

    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()

        # Total scans
        cursor.execute("SELECT COUNT(*), AVG(confidence) FROM predictions")
        total_row = cursor.fetchone()
        if total_row and total_row[0] > 0:
            stats["total_scans"] = total_row[0]
            stats["avg_confidence"] = round(float(total_row[1] or 0.0) * 100, 2)

        # Class counts
        cursor.execute("SELECT predicted_class, COUNT(*) FROM predictions GROUP BY predicted_class")
        for row in cursor.fetchall():
            c_name, count = row[0], row[1]
            if c_name in stats["class_counts"]:
                stats["class_counts"][c_name] = count

        # Recent 5 scans
        cursor.execute("SELECT * FROM predictions ORDER BY id DESC LIMIT 5")
        for row in cursor.fetchall():
            rec = dict(row)
            try:
                rec["probabilities"] = json.loads(rec["probabilities"])
            except Exception:
                rec["probabilities"] = {}
            stats["recent_predictions"].append(rec)

    return stats
