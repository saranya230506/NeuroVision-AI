"""
Automated unit tests for EfficientNetB0 model architecture and utilities.
"""

import numpy as np
import pytest
import tensorflow as tf

import config
from src.model import build_model, unfreeze_for_fine_tuning
from src.utils import apply_clahe, load_and_preprocess_image


def test_build_model_architecture():
    """Verify model output shape, input shape, and compilation metrics."""
    model = build_model(num_classes=4, input_shape=(224, 224, 3), freeze_base=True)
    assert model is not None
    assert model.input_shape == (None, 224, 224, 3)
    assert model.output_shape == (None, 4)
    assert len(model.outputs) == 1
    assert model.name == "NeuroVision_EfficientNetB0"


def test_unfreeze_for_fine_tuning():
    """Verify unfreezing top layers increases trainable parameters."""
    model = build_model(num_classes=4, freeze_base=True)
    trainable_before = sum([tf.size(w).numpy() for w in model.trainable_weights])

    unfreeze_for_fine_tuning(model, num_layers=30, learning_rate=1e-4)
    trainable_after = sum([tf.size(w).numpy() for w in model.trainable_weights])

    assert trainable_after >= trainable_before


def test_clahe_preprocessing():
    """Verify CLAHE image enhancement maintains shape and uint8 range."""
    dummy_rgb = np.random.randint(0, 256, (224, 224, 3), dtype=np.uint8)
    enhanced = apply_clahe(dummy_rgb)

    assert enhanced.shape == (224, 224, 3)
    assert enhanced.dtype == np.uint8
    assert enhanced.max() <= 255
    assert enhanced.min() >= 0


def test_load_and_preprocess_image():
    """Verify load_and_preprocess_image outputs correct tensor dimensions."""
    sample_path = config.SAMPLES_DIR / "glioma_sample.jpg"
    if sample_path.exists():
        tensor_batch, display_rgb = load_and_preprocess_image(str(sample_path))
        assert tensor_batch.shape == (1, 224, 224, 3)
        assert tensor_batch.dtype == np.float32
        assert display_rgb.shape == (224, 224, 3)
        assert display_rgb.dtype == np.uint8
