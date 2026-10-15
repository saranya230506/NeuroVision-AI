"""
NeuroVision AI - Centralized Configuration Module
Defines all environment, model, dataset, and application parameters.
"""

import os
from pathlib import Path
from typing import Dict, List, Tuple

# Base Project Paths
BASE_DIR: Path = Path(__file__).resolve().parent
DATASET_DIR: Path = BASE_DIR / "dataset"
TRAIN_DIR: Path = DATASET_DIR / "Training"
TEST_DIR: Path = DATASET_DIR / "Testing"

MODELS_DIR: Path = BASE_DIR / "models"
MODELS_DIR.mkdir(parents=True, exist_ok=True)
DEFAULT_MODEL_PATH: Path = MODELS_DIR / "efficientnet_brain_tumor.keras"
BACKUP_MODEL_PATH: Path = MODELS_DIR / "efficientnet_brain_tumor.h5"
HISTORY_PATH: Path = MODELS_DIR / "training_history.json"
METRICS_PATH: Path = MODELS_DIR / "evaluation_metrics.json"

DATABASE_DIR: Path = BASE_DIR / "database"
DATABASE_DIR.mkdir(parents=True, exist_ok=True)
DATABASE_PATH: Path = DATABASE_DIR / "neurovision.db"

STATIC_DIR: Path = BASE_DIR / "static"
UPLOADS_DIR: Path = STATIC_DIR / "uploads"
GRADCAM_DIR: Path = STATIC_DIR / "gradcam_outputs"
REPORTS_DIR: Path = STATIC_DIR / "reports"
SAMPLES_DIR: Path = STATIC_DIR / "samples"

for directory in [UPLOADS_DIR, GRADCAM_DIR, REPORTS_DIR, SAMPLES_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Image & Preprocessing Specifications
IMAGE_SIZE: Tuple[int, int] = (224, 224)
IMAGE_CHANNELS: int = 3
INPUT_SHAPE: Tuple[int, int, int] = (224, 224, 3)
ALLOWED_EXTENSIONS: set = {"png", "jpg", "jpeg", "webp"}
MAX_CONTENT_LENGTH: int = 16 * 1024 * 1024  # 16 MB max upload

# Model Hyperparameters
NUM_CLASSES: int = 4
BATCH_SIZE: int = 32
EPOCHS_PHASE_1: int = 10       # Feature extraction (frozen base)
EPOCHS_PHASE_2: int = 15       # Fine-tuning (unfrozen top layers)
LEARNING_RATE_PHASE_1: float = 1e-3
LEARNING_RATE_PHASE_2: float = 1e-4
WEIGHT_DECAY: float = 1e-4
DROPOUT_RATE: float = 0.4
FINE_TUNE_LAYERS: int = 30     # Unfreeze last N layers of EfficientNetB0
GRADCAM_TARGET_LAYER: str = "top_conv"  # EfficientNetB0 final feature extraction conv layer

# Class Mapping (alphabetical order matching Keras flow_from_directory)
CLASS_NAMES: List[str] = ["Glioma", "Meningioma", "No Tumor", "Pituitary"]
CLASS_LABELS_MAP: Dict[str, int] = {name: idx for idx, name in enumerate(CLASS_NAMES)}
DIR_TO_CLASS_MAP: Dict[str, str] = {
    "glioma": "Glioma",
    "meningioma": "Meningioma",
    "notumor": "No Tumor",
    "pituitary": "Pituitary"
}

# Detailed Medical Class Knowledge (for Clinical Reports & UI)
CLASS_METADATA: Dict[str, Dict] = {
    "Glioma": {
        "title": "Glioma Tumor Detected",
        "badge_color": "danger",
        "severity": "High / Requires Immediate Specialist Review",
        "description": (
            "Gliomas originate in the glial cells (astrocytes, oligodendrocytes, and ependymal cells) "
            "that surround and support neurons in the brain. They represent one of the most common "
            "primary brain tumors and can vary from slow-growing (low-grade) to highly aggressive (high-grade glioblastomas)."
        ),
        "typical_symptoms": [
            "Persistent or worsening headaches",
            "Nausea and vomiting",
            "Seizures or focal neurological deficits",
            "Cognitive or memory impairments",
            "Speech or visual disturbances"
        ],
        "recommended_actions": [
            "Urgent consultation with a Neuro-Oncologist and Neurosurgeon",
            "High-resolution contrast-enhanced Brain MRI (T1-CE, T2/FLAIR, DWI)",
            "Neurosurgical biopsy or surgical resection planning",
            "Molecular genetic testing (IDH1/2 mutation, 1p/19q co-deletion, MGMT promoter methylation)"
        ]
    },
    "Meningioma": {
        "title": "Meningioma Tumor Detected",
        "badge_color": "warning",
        "severity": "Moderate / Structured Neurological Follow-Up",
        "description": (
            "Meningiomas arise from the meninges—the protective membranous layers covering the brain "
            "and spinal cord. The majority are benign (WHO Grade I) and slow-growing, though atypical "
            "or malignant variants can cause mass effect, brain compression, and focal neurological deficits."
        ),
        "typical_symptoms": [
            "Focal headaches, often localized to the tumor site",
            "Vision problems (blurriness or diplopia)",
            "Hearing loss or tinnitus",
            "Weakness or numbness in extremities",
            "Personality or behavioral changes"
        ],
        "recommended_actions": [
            "Appointment with a Board-Certified Neurologist or Neurosurgeon",
            "Serial MRI tracking to assess volumetric doubling time and growth rate",
            "Evaluation for stereotactic radiosurgery (Gamma Knife / CyberKnife) or microsurgical excision",
            "Ophthalmological visual field exam if near optic chiasm"
        ]
    },
    "Pituitary": {
        "title": "Pituitary Adenoma Detected",
        "badge_color": "info",
        "severity": "Moderate / Endocrine & Neurosurgical Assessment",
        "description": (
            "Pituitary adenomas originate in the pituitary gland situated at the skull base (sella turcica). "
            "Most are benign, functioning (hormone-secreting, e.g., prolactinomas, ACTH-producing) or "
            "non-functioning. As they expand, they can compress the optic chiasm, leading to bitemporal hemianopsia."
        ),
        "typical_symptoms": [
            "Visual field deficits (loss of peripheral vision / tunnel vision)",
            "Endocrine imbalances (hyperprolactinemia, Cushing's symptoms, acromegaly)",
            "Chronic headaches centered behind the eyes",
            "Unexplained fatigue, metabolic swings, or mood alterations"
        ],
        "recommended_actions": [
            "Comprehensive serum neuroendocrine hormone panel (Prolactin, GH, ACTH, Cortisol, TSH, IGF-1)",
            "Formal neuro-ophthalmology Humphrey visual field evaluation",
            "Endocrinology and skull-base neurosurgery consultation",
            "Assessment for medical therapy (e.g., dopamine agonists) or transsphenoidal endoscopic surgery"
        ]
    },
    "No Tumor": {
        "title": "No Neoplasm Detected (Clear MRI)",
        "badge_color": "success",
        "severity": "Normal / Routine Monitoring",
        "description": (
            "The neural parenchyma, ventricular dimensions, cortical sulci, midline structures, and gray-white "
            "matter differentiation appear symmetric and preserved without detectable space-occupying lesions, "
            "abnormal contrast enhancement, or mass effect within the examined intracranial field."
        ),
        "typical_symptoms": [
            "No lesion-specific intracranial findings noted",
            "If headaches or vertigo persist, consider non-neoplastic etiology (migraine, sinus, cervical, tension)"
        ],
        "recommended_actions": [
            "Correlate with clinical history and patient presentation",
            "Routine primary care follow-up as clinically warranted",
            "Repeat imaging only if new progressive neurological symptoms arise"
        ]
    }
}

# Flask Application Settings
SECRET_KEY: str = os.getenv("SECRET_KEY", "neurovision-ai-secret-key-2026-production")
DEBUG: bool = os.getenv("FLASK_DEBUG", "0").lower() in ("true", "1", "t")
PORT: int = int(os.getenv("PORT", "5000"))
HOST: str = os.getenv("HOST", "0.0.0.0")

# Project Metadata
PROJECT_NAME: str = "NeuroVision AI"
PROJECT_TAGLINE: str = "AI-Powered Brain Tumor Detection using Deep Learning (EfficientNetB0)"
PROJECT_VERSION: str = "1.0.0"
ORGANIZATION: str = "IBM SkillsBuild - AICTE BharatCares Internship 2026"
COHORT: str = "Machine Learning & Applied AI (Aug - Sep 2026)"
SDG_GOAL: str = "UN Sustainable Development Goal 3: Good Health and Well-Being"
AUTHOR: str = "Saranya"
ACADEMIC_INSTITUTION: str = "Marwadi University"
