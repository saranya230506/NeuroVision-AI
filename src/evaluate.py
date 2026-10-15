"""
NeuroVision AI - Model Evaluation & Clinical Metrics Suite
Computes multi-class Confusion Matrix, ROC curves, AUC scores, and
per-class precision/recall/F1-scores on the independent Brain Tumor MRI Test set.
"""

import json
import logging
import os
import sys
from pathlib import Path
from typing import Dict, Tuple

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import tensorflow as tf
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    roc_auc_score,
    roc_curve
)

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import config
from src.model import load_trained_model

logger = logging.getLogger("NeuroVision.Evaluate")


def evaluate_model(
    model: tf.keras.Model = None,
    test_dir: Path = config.TEST_DIR,
    image_size: Tuple[int, int] = config.IMAGE_SIZE,
    batch_size: int = config.BATCH_SIZE
) -> Dict:
    """
    Run comprehensive evaluation on the brain tumor test dataset.

    Returns:
        Dictionary containing overall accuracy, macro metrics, per-class metrics,
        and AUC values.
    """
    if model is None:
        model = load_trained_model()

    logger.info("Loading test dataset from %s...", test_dir)
    test_ds = tf.keras.utils.image_dataset_from_directory(
        directory=str(test_dir),
        labels="categorical",
        label_mode="categorical",
        class_names=["glioma", "meningioma", "notumor", "pituitary"],
        batch_size=batch_size,
        image_size=image_size,
        shuffle=False
    )

    # Collect true labels and predictions
    y_true_list = []
    y_pred_probs_list = []

    for images_batch, labels_batch in test_ds:
        preds = model.predict(images_batch, verbose=0)
        y_true_list.append(labels_batch.numpy())
        y_pred_probs_list.append(preds)

    y_true = np.concatenate(y_true_list, axis=0)
    y_pred_probs = np.concatenate(y_pred_probs_list, axis=0)

    y_true_classes = np.argmax(y_true, axis=1)
    y_pred_classes = np.argmax(y_pred_probs, axis=1)

    display_class_names = ["Glioma", "Meningioma", "No Tumor", "Pituitary"]

    # 1. Confusion Matrix
    cm = confusion_matrix(y_true_classes, y_pred_classes)
    cm_norm = cm.astype("float") / cm.sum(axis=1)[:, np.newaxis]

    plt.figure(figsize=(9, 7))
    sns.heatmap(
        cm,
        annot=True,
        fmt="d",
        cmap="Blues",
        xticklabels=display_class_names,
        yticklabels=display_class_names,
        cbar=True,
        annot_kws={"size": 13, "weight": "bold"}
    )
    plt.title("NeuroVision AI - Brain Tumor MRI Confusion Matrix", fontsize=14, fontweight="bold", pad=15)
    plt.xlabel("Predicted Class", fontsize=12, fontweight="bold")
    plt.ylabel("Ground Truth Class", fontsize=12, fontweight="bold")
    plt.tight_layout()
    cm_path = config.STATIC_DIR / "confusion_matrix.png"
    plt.savefig(str(cm_path), dpi=300)
    plt.close()
    logger.info("Saved Confusion Matrix plot to %s", cm_path)

    # 2. Multi-Class ROC Curves & AUC (One-vs-Rest)
    plt.figure(figsize=(10, 8))
    roc_auc_dict = {}

    colors = ["#dc3545", "#fd7e14", "#198754", "#0d6efd"]
    for i, class_name in enumerate(display_class_names):
        fpr, tpr, _ = roc_curve(y_true[:, i], y_pred_probs[:, i])
        auc_val = roc_auc_score(y_true[:, i], y_pred_probs[:, i])
        roc_auc_dict[class_name] = float(auc_val)
        plt.plot(fpr, tpr, color=colors[i], lw=2.5,
                 label=f"{class_name} (AUC = {auc_val:.3f})")

    # Macro AUC
    macro_auc = roc_auc_score(y_true, y_pred_probs, multi_class="ovr", average="macro")
    roc_auc_dict["macro_average"] = float(macro_auc)

    plt.plot([0, 1], [0, 1], "k--", lw=1.5, alpha=0.7)
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel("False Positive Rate (1 - Specificity)", fontsize=12, fontweight="bold")
    plt.ylabel("True Positive Rate (Sensitivity)", fontsize=12, fontweight="bold")
    plt.title("NeuroVision AI - Multi-Class ROC Curves (One-vs-Rest)", fontsize=14, fontweight="bold", pad=15)
    plt.legend(loc="lower right", fontsize=11, frameon=True)
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.tight_layout()
    roc_path = config.STATIC_DIR / "roc_curve.png"
    plt.savefig(str(roc_path), dpi=300)
    plt.close()
    logger.info("Saved ROC Curves plot to %s", roc_path)

    # 3. Classification Report
    clf_report = classification_report(
        y_true_classes,
        y_pred_classes,
        target_names=display_class_names,
        output_dict=True,
        zero_division=0
    )

    accuracy = float(clf_report["accuracy"])
    macro_f1 = float(clf_report["macro avg"]["f1-score"])
    weighted_f1 = float(clf_report["weighted avg"]["f1-score"])

    logger.info("==========================================")
    logger.info("         EVALUATION RESULTS SUMMARY       ")
    logger.info("==========================================")
    logger.info(" Overall Test Accuracy : %.2f%%", accuracy * 100)
    logger.info(" Macro Average F1-Score: %.4f", macro_f1)
    logger.info(" Weighted F1-Score     : %.4f", weighted_f1)
    logger.info(" Macro Average AUC     : %.4f", macro_auc)
    logger.info("==========================================")

    metrics_summary = {
        "accuracy": accuracy,
        "macro_f1": macro_f1,
        "weighted_f1": weighted_f1,
        "macro_auc": macro_auc,
        "roc_auc_per_class": roc_auc_dict,
        "classification_report": clf_report,
        "confusion_matrix": cm.tolist()
    }

    with open(config.METRICS_PATH, "w", encoding="utf-8") as f:
        json.dump(metrics_summary, f, indent=4)
    logger.info("Saved evaluation metrics to %s", config.METRICS_PATH)

    return metrics_summary


if __name__ == "__main__":
    evaluate_model()
