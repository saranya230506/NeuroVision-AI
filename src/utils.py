"""
NeuroVision AI - Utility Functions Module
Provides image preprocessing, medical contrast enhancement (CLAHE),
seed reproducibility, logging configuration, and filename sanitation.
"""

import io
import logging
import os
import random
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple, Union

import cv2
import numpy as np

import config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("NeuroVision")


def set_seed(seed: int = 42) -> None:
    """Set random seeds across libraries to ensure reproducible results."""
    random.seed(seed)
    np.random.seed(seed)
    os.environ["PYTHONHASHSEED"] = str(seed)
    try:
        import tensorflow as tf
        tf.random.set_seed(seed)
        logger.info("Deterministic seed set to %d", seed)
    except ImportError:
        pass


def apply_clahe(image: np.ndarray, clip_limit: float = 2.0, tile_grid_size: Tuple[int, int] = (8, 8)) -> np.ndarray:
    """
    Apply Contrast Limited Adaptive Histogram Equalization (CLAHE) to an MRI image.
    This enhances local contrast and accentuates subtle boundaries in brain tissue.

    Args:
        image: RGB or grayscale image as numpy array.
        clip_limit: Threshold for contrast limiting.
        tile_grid_size: Size of grid for histogram equalization.

    Returns:
        Enhanced RGB image as numpy array (uint8).
    """
    if len(image.shape) == 2:
        clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_grid_size)
        return clahe.apply(image)

    # Convert RGB to LAB color space to equalize only the L (luminance) channel
    lab = cv2.cvtColor(image, cv2.COLOR_RGB2LAB)
    l_channel, a_channel, b_channel = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_grid_size)
    cl = clahe.apply(l_channel)
    merged_lab = cv2.merge((cl, a_channel, b_channel))
    enhanced_rgb = cv2.cvtColor(merged_lab, cv2.COLOR_LAB2RGB)
    return enhanced_rgb


def load_and_preprocess_image(
    image_source: Union[str, Path, bytes, io.BytesIO],
    target_size: Tuple[int, int] = config.IMAGE_SIZE,
    enhance_contrast: bool = True
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Load an MRI image from path or bytes, apply CLAHE enhancement, resize,
    and prepare both display-ready RGB image and batch-ready model tensor.

    Args:
        image_source: File path (str/Path) or raw byte data.
        target_size: Tuple of (height, width).
        enhance_contrast: Whether to apply CLAHE medical enhancement.

    Returns:
        Tuple of (model_input_tensor [1, 224, 224, 3] float32, display_image [224, 224, 3] uint8 RGB)
    """
    if isinstance(image_source, (str, Path)):
        if not os.path.exists(image_source):
            raise FileNotFoundError(f"Image not found at path: {image_source}")
        bgr_image = cv2.imread(str(image_source))
        if bgr_image is None:
            raise ValueError(f"Failed to decode image from path: {image_source}")
        rgb_image = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2RGB)
    elif isinstance(image_source, (bytes, io.BytesIO)):
        byte_data = image_source.getvalue() if isinstance(image_source, io.BytesIO) else image_source
        file_bytes = np.frombuffer(byte_data, dtype=np.uint8)
        bgr_image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
        if bgr_image is None:
            raise ValueError("Failed to decode image from provided byte stream")
        rgb_image = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2RGB)
    elif isinstance(image_source, np.ndarray):
        rgb_image = image_source.copy()
        if len(rgb_image.shape) == 2:
            rgb_image = cv2.cvtColor(rgb_image, cv2.COLOR_GRAY2RGB)
    else:
        raise TypeError(f"Unsupported image source type: {type(image_source)}")

    # Apply CLAHE contrast enhancement for medical MRI
    if enhance_contrast:
        processed_rgb = apply_clahe(rgb_image)
    else:
        processed_rgb = rgb_image

    # Resize to model input dimension
    resized_display = cv2.resize(processed_rgb, target_size, interpolation=cv2.INTER_AREA)

    # Note: TensorFlow EfficientNetB0 includes its own internal normalization layer
    # when fed standard uint8/float32 (0-255). We provide float32 in range [0, 255] or [0, 1].
    # Feeding float32 in [0, 255] matches standard keras.applications.efficientnet.preprocess_input.
    tensor_input = resized_display.astype(np.float32)
    tensor_batch = np.expand_dims(tensor_input, axis=0)

    return tensor_batch, resized_display


def allowed_file(filename: str) -> bool:
    """Check if the uploaded file has a valid permitted image extension."""
    if "." not in filename:
        return False
    ext = filename.rsplit(".", 1)[1].lower()
    return ext in config.ALLOWED_EXTENSIONS


def generate_unique_filename(original_filename: str, prefix: str = "scan") -> str:
    """Generate a collision-free secure filename with timestamp and UUID."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    ext = original_filename.rsplit(".", 1)[1].lower() if "." in original_filename else "jpg"
    short_uuid = uuid.uuid4().hex[:8]
    return f"{prefix}_{timestamp}_{short_uuid}.{ext}"


def get_formatted_timestamp() -> str:
    """Return ISO standard formatted timestamp."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
