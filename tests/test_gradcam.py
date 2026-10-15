"""
Automated unit tests for Grad-CAM explainable AI module.
"""

import numpy as np
import pytest
import tensorflow as tf

from src.gradcam import compute_gradcam_heatmap, overlay_gradcam
from src.model import build_model


def test_gradcam_heatmap_generation():
    """Verify Grad-CAM produces a 2D normalized heatmap between 0 and 1."""
    model = build_model(num_classes=4, freeze_base=False)
    dummy_input = np.random.uniform(0.0, 255.0, (1, 224, 224, 3)).astype(np.float32)

    heatmap = compute_gradcam_heatmap(
        model=model,
        input_tensor=dummy_input,
        target_class_idx=0
    )

    assert heatmap is not None
    assert len(heatmap.shape) == 2
    assert heatmap.max() <= 1.0 + 1e-5
    assert heatmap.min() >= 0.0


def test_gradcam_overlay():
    """Verify superimposing heatmap onto original image produces uint8 RGB output."""
    dummy_original = np.random.randint(0, 256, (224, 224, 3), dtype=np.uint8)
    dummy_heatmap = np.random.uniform(0.0, 1.0, (7, 7)).astype(np.float32)

    overlay = overlay_gradcam(dummy_original, dummy_heatmap, alpha=0.45)

    assert overlay.shape == (224, 224, 3)
    assert overlay.dtype == np.uint8
