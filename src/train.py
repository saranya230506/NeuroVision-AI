"""
NeuroVision AI - Deep Learning Model Training Pipeline
Executes end-to-end training for brain tumor classification using EfficientNetB0:
- Two-stage Transfer Learning & Fine-Tuning
- Real-time Medical Data Augmentation
- Class Weight Computation for balanced optimization
- Callbacks (ModelCheckpoint, EarlyStopping, ReduceLROnPlateau, CSVLogger)
- Training curves generation and model persistence
"""

import argparse
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
import tensorflow as tf
from sklearn.utils.class_weight import compute_class_weight

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import config
from src.model import build_model, unfreeze_for_fine_tuning
from src.utils import set_seed

logger = logging.getLogger("NeuroVision.Train")


def create_data_generators(
    train_dir: Path = config.TRAIN_DIR,
    val_dir: Path = config.TEST_DIR,
    image_size: Tuple[int, int] = config.IMAGE_SIZE,
    batch_size: int = config.BATCH_SIZE
) -> Tuple[tf.data.Dataset, tf.data.Dataset, Dict[int, float]]:
    """
    Build highly optimized tf.data input pipelines with data augmentation
    and calculate class weights for balanced learning.
    """
    logger.info("Loading training dataset from %s", train_dir)
    raw_train_ds = tf.keras.utils.image_dataset_from_directory(
        directory=str(train_dir),
        labels="inferred",
        label_mode="categorical",
        class_names=["glioma", "meningioma", "notumor", "pituitary"],
        batch_size=batch_size,
        image_size=image_size,
        shuffle=True,
        seed=42
    )

    logger.info("Loading validation/testing dataset from %s", val_dir)
    raw_val_ds = tf.keras.utils.image_dataset_from_directory(
        directory=str(val_dir),
        labels="inferred",
        label_mode="categorical",
        class_names=["glioma", "meningioma", "notumor", "pituitary"],
        batch_size=batch_size,
        image_size=image_size,
        shuffle=False
    )

    # Compute class weights to handle any minor class distribution skew
    labels_list = []
    for _, labels_batch in raw_train_ds:
        labels_list.extend(np.argmax(labels_batch.numpy(), axis=-1))
    class_indices = np.array(labels_list)
    unique_classes = np.unique(class_indices)
    weights = compute_class_weight(
        class_weight="balanced",
        classes=unique_classes,
        y=class_indices
    )
    class_weights_dict = {int(cls): float(wt) for cls, wt in zip(unique_classes, weights)}
    logger.info("Computed class weights: %s", class_weights_dict)

    # Augmentation pipeline for medical neuroimaging
    augmentation_layers = tf.keras.Sequential([
        tf.keras.layers.RandomRotation(0.08),
        tf.keras.layers.RandomZoom(0.08),
        tf.keras.layers.RandomTranslation(0.04, 0.04),
        tf.keras.layers.RandomFlip("horizontal"),
        tf.keras.layers.RandomBrightness(0.06),
        tf.keras.layers.RandomContrast(0.08),
    ], name="mri_augmentation_pipeline")

    train_ds = (
        raw_train_ds
        .map(lambda x, y: (augmentation_layers(x, training=True), y),
             num_parallel_calls=tf.data.AUTOTUNE)
        .prefetch(buffer_size=tf.data.AUTOTUNE)
    )

    val_ds = raw_val_ds.prefetch(buffer_size=tf.data.AUTOTUNE)

    return train_ds, val_ds, class_weights_dict


def plot_and_save_training_curves(history_data: Dict[str, list], output_path: Path) -> None:
    """Plot accuracy and loss trajectories across training epochs."""
    epochs_range = range(1, len(history_data.get("accuracy", [])) + 1)
    if not epochs_range:
        logger.warning("No history epochs available to plot.")
        return

    plt.figure(figsize=(14, 6))

    # Accuracy Plot
    plt.subplot(1, 2, 1)
    plt.plot(epochs_range, history_data.get("accuracy", []), "b-o", label="Training Accuracy", linewidth=2)
    plt.plot(epochs_range, history_data.get("val_accuracy", []), "g-s", label="Validation Accuracy", linewidth=2)
    plt.title("Model Accuracy across Epochs", fontsize=14, fontweight="bold")
    plt.xlabel("Epoch", fontsize=12)
    plt.ylabel("Accuracy", fontsize=12)
    plt.grid(True, linestyle="--", alpha=0.6)
    plt.legend(loc="lower right")

    # Loss Plot
    plt.subplot(1, 2, 2)
    plt.plot(epochs_range, history_data.get("loss", []), "r-o", label="Training Loss", linewidth=2)
    plt.plot(epochs_range, history_data.get("val_loss", []), "m-s", label="Validation Loss", linewidth=2)
    plt.title("Model Cross-Entropy Loss across Epochs", fontsize=14, fontweight="bold")
    plt.xlabel("Epoch", fontsize=12)
    plt.ylabel("Loss", fontsize=12)
    plt.grid(True, linestyle="--", alpha=0.6)
    plt.legend(loc="upper right")

    plt.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(str(output_path), dpi=300)
    plt.close()
    logger.info("Saved training curves plot to %s", output_path)


def run_training(
    epochs_phase_1: int = config.EPOCHS_PHASE_1,
    epochs_phase_2: int = config.EPOCHS_PHASE_2,
    batch_size: int = config.BATCH_SIZE,
    model_save_path: Path = config.DEFAULT_MODEL_PATH
) -> tf.keras.Model:
    """
    Execute complete two-phase training workflow.
    """
    set_seed(42)

    # 1. Prepare Datasets
    train_ds, val_ds, class_weights = create_data_generators(
        train_dir=config.TRAIN_DIR,
        val_dir=config.TEST_DIR,
        image_size=config.IMAGE_SIZE,
        batch_size=batch_size
    )

    # 2. Build Transfer Learning Model
    model = build_model(
        num_classes=config.NUM_CLASSES,
        input_shape=config.INPUT_SHAPE,
        learning_rate=config.LEARNING_RATE_PHASE_1,
        freeze_base=True
    )

    # 3. Configure Callbacks
    csv_log_path = config.MODELS_DIR / "training_log.csv"
    callbacks_phase_1 = [
        tf.keras.callbacks.ModelCheckpoint(
            filepath=str(model_save_path),
            monitor="val_accuracy",
            save_best_only=True,
            mode="max",
            verbose=1
        ),
        tf.keras.callbacks.EarlyStopping(
            monitor="val_loss",
            patience=5,
            restore_best_weights=True,
            verbose=1
        ),
        tf.keras.callbacks.ReduceLROnPlateau(
            monitor="val_loss",
            factor=0.3,
            patience=2,
            min_lr=1e-6,
            verbose=1
        ),
        tf.keras.callbacks.CSVLogger(str(csv_log_path), append=False)
    ]

    # 4. Phase 1: Feature Extraction
    logger.info("=== Starting Phase 1: Feature Extraction (%d epochs) ===", epochs_phase_1)
    history_phase_1 = model.fit(
        train_ds,
        validation_data=val_ds,
        epochs=epochs_phase_1,
        class_weight=class_weights,
        callbacks=callbacks_phase_1,
        verbose=1
    )

    # 5. Phase 2: Fine-Tuning
    logger.info("=== Starting Phase 2: Fine-Tuning Top Layers (%d epochs) ===", epochs_phase_2)
    unfreeze_for_fine_tuning(
        model,
        num_layers=config.FINE_TUNE_LAYERS,
        learning_rate=config.LEARNING_RATE_PHASE_2
    )

    callbacks_phase_2 = [
        tf.keras.callbacks.ModelCheckpoint(
            filepath=str(model_save_path),
            monitor="val_accuracy",
            save_best_only=True,
            mode="max",
            verbose=1
        ),
        tf.keras.callbacks.EarlyStopping(
            monitor="val_loss",
            patience=6,
            restore_best_weights=True,
            verbose=1
        ),
        tf.keras.callbacks.ReduceLROnPlateau(
            monitor="val_loss",
            factor=0.2,
            patience=3,
            min_lr=1e-6,
            verbose=1
        ),
        tf.keras.callbacks.CSVLogger(str(csv_log_path), append=True)
    ]

    total_epochs = epochs_phase_1 + epochs_phase_2
    history_phase_2 = model.fit(
        train_ds,
        validation_data=val_ds,
        initial_epoch=epochs_phase_1,
        epochs=total_epochs,
        class_weight=class_weights,
        callbacks=callbacks_phase_2,
        verbose=1
    )

    # Combine History
    combined_history = {}
    for k in history_phase_1.history.keys():
        combined_history[k] = [float(v) for v in history_phase_1.history[k] + history_phase_2.history.get(k, [])]

    # Save metrics & history to JSON
    with open(config.HISTORY_PATH, "w", encoding="utf-8") as f:
        json.dump(combined_history, f, indent=4)
    logger.info("Saved combined history to %s", config.HISTORY_PATH)

    # Also save backup format (.h5)
    try:
        model.save(str(config.BACKUP_MODEL_PATH))
        logger.info("Saved backup H5 weights to %s", config.BACKUP_MODEL_PATH)
    except Exception as e:
        logger.warning("Could not write backup H5 model: %s", e)

    # Generate training curves chart
    curves_path = config.STATIC_DIR / "training_curves.png"
    plot_and_save_training_curves(combined_history, curves_path)

    logger.info("Training pipeline completed successfully! Best model saved to %s", model_save_path)
    return model


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="NeuroVision AI Training Pipeline")
    parser.add_argument("--epochs1", type=int, default=config.EPOCHS_PHASE_1, help="Epochs for Phase 1")
    parser.add_argument("--epochs2", type=int, default=config.EPOCHS_PHASE_2, help="Epochs for Phase 2")
    parser.add_argument("--batch-size", type=int, default=config.BATCH_SIZE, help="Batch size")
    args = parser.parse_args()

    run_training(
        epochs_phase_1=args.epochs1,
        epochs_phase_2=args.epochs2,
        batch_size=args.batch_size
    )
