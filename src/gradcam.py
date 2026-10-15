"""
NeuroVision AI - Explainable AI (XAI) Grad-CAM Module
Computes Gradient-weighted Class Activation Mapping (Grad-CAM) for EfficientNetB0
to highlight exact anatomical regions of interest driving tumor predictions.
"""

import logging
import sys
import cv2
import numpy as np

try:
    import tensorflow as tf
    TF_AVAILABLE = True
except Exception:
    tf = None
    TF_AVAILABLE = False

import config

logger = logging.getLogger("NeuroVision.GradCAM")


def find_target_conv_layer(model, layer_name: Optional[str] = None):
    """
    Locate the target convolutional layer in the model hierarchy.
    EfficientNetB0's final convolutional layer is typically 'top_conv'.

    Returns:
        Tuple of (sub_or_main_model, target_layer)
    """
    if layer_name:
        try:
            return model, model.get_layer(layer_name)
        except ValueError:
            pass

    # Check if model has a nested EfficientNet base model
    for layer in model.layers:
        if "efficientnet" in layer.name.lower() and hasattr(layer, "layers"):
            base_model = layer
            # Search within nested base model
            for nested_layer in reversed(base_model.layers):
                if isinstance(nested_layer, tf.keras.layers.Conv2D) or nested_layer.name == "top_conv":
                    logger.info("Found Grad-CAM conv layer '%s' inside nested base model.", nested_layer.name)
                    return base_model, nested_layer

    # Search directly in the top-level model
    for layer in reversed(model.layers):
        if isinstance(layer, tf.keras.layers.Conv2D):
            logger.info("Found Grad-CAM conv layer '%s' in top-level model.", layer.name)
            return model, layer

    raise ValueError("Could not locate any Conv2D layer in the model for Grad-CAM.")


def compute_gradcam_heatmap(
    model,
    input_tensor: np.ndarray,
    target_class_idx: Optional[int] = None,
    layer_name: Optional[str] = config.GRADCAM_TARGET_LAYER
) -> Optional[np.ndarray]:
    """
    Generate a 2D normalized Grad-CAM activation heatmap for the given input tensor.

    Args:
        model: Trained tf.keras.Model.
        input_tensor: Numpy array of shape (1, 224, 224, 3) in float32.
        target_class_idx: Index of class to explain. If None, uses top predicted class.
        layer_name: Name of target convolutional layer.

    Returns:
        2D numpy array with values normalized to [0, 1].
    """
    if not TF_AVAILABLE or tf is None or model is None:
        return None
    tf_tensor = tf.convert_to_tensor(input_tensor, dtype=tf.float32)

    # Check if backbone is nested
    nested_backbone = None
    for layer in model.layers:
        if "efficientnet" in layer.name.lower() and hasattr(layer, "layers"):
            nested_backbone = layer
            break

    if nested_backbone is not None:
        # Construct intermediate model inside nested backbone
        target_conv = nested_backbone.get_layer(layer_name) if layer_name and layer_name in [l.name for l in nested_backbone.layers] else None
        if target_conv is None:
            for l in reversed(nested_backbone.layers):
                if isinstance(l, tf.keras.layers.Conv2D):
                    target_conv = l
                    break

        conv_feature_extractor = tf.keras.Model(
            inputs=[nested_backbone.inputs],
            outputs=[target_conv.output, nested_backbone.output]
        )

        with tf.GradientTape() as tape:
            # 1. Forward through feature extractor
            conv_outputs, backbone_features = conv_feature_extractor(tf_tensor)
            tape.watch(conv_outputs)

            # 2. Forward through classifier head
            x = backbone_features
            for layer in model.layers:
                if layer != nested_backbone and layer.name != "mri_input":
                    x = layer(x)
            predictions = x

            if target_class_idx is None:
                target_class_idx = tf.argmax(predictions[0])

            loss = predictions[:, target_class_idx]

        # 3. Compute gradients of class score w.r.t. feature map
        grads = tape.gradient(loss, conv_outputs)

    else:
        # Standard flat model hierarchy
        target_layer = model.get_layer(layer_name) if layer_name else None
        if target_layer is None:
            for l in reversed(model.layers):
                if isinstance(l, tf.keras.layers.Conv2D):
                    target_layer = l
                    break

        grad_model = tf.keras.models.Model(
            inputs=[model.inputs],
            outputs=[target_layer.output, model.output]
        )

        with tf.GradientTape() as tape:
            conv_outputs, predictions = grad_model(tf_tensor)
            tape.watch(conv_outputs)
            if target_class_idx is None:
                target_class_idx = tf.argmax(predictions[0])
            loss = predictions[:, target_class_idx]

        grads = tape.gradient(loss, conv_outputs)

    # 4. Global Average Pooling of gradients (weights alpha_k)
    pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2))

    # 5. Weighted combination of activation maps
    conv_outputs_val = conv_outputs[0]
    heatmap = tf.reduce_sum(tf.multiply(pooled_grads, conv_outputs_val), axis=-1)

    # 6. Apply ReLU to isolate features with positive contribution to class
    heatmap = tf.maximum(heatmap, 0.0)

    # Normalize heatmap between 0 and 1
    max_val = tf.math.reduce_max(heatmap)
    if max_val > 0:
        heatmap = heatmap / max_val
    else:
        heatmap = tf.zeros_like(heatmap)

    return heatmap.numpy()


def overlay_gradcam(
    original_rgb_image: np.ndarray,
    heatmap: np.ndarray,
    alpha: float = 0.45,
    colormap: int = cv2.COLORMAP_JET
) -> np.ndarray:
    """
    Superimpose Grad-CAM heatmap over the original MRI scan.

    Args:
        original_rgb_image: Numpy array of shape (H, W, 3) in uint8 RGB.
        heatmap: 2D numpy array [0, 1].
        alpha: Blending weight for heatmap overlay (0.0 to 1.0).
        colormap: OpenCV colormap constant.

    Returns:
        Blended RGB image of shape (H, W, 3) in uint8.
    """
    h, w = original_rgb_image.shape[:2]

    # Resize heatmap to match original image dimensions
    resized_heatmap = cv2.resize(heatmap, (w, h), interpolation=cv2.INTER_CUBIC)

    # Scale to 0-255 uint8
    heatmap_uint8 = np.uint8(255 * resized_heatmap)

    # Apply colormap (cv2 applies colormap in BGR format)
    heatmap_colored_bgr = cv2.applyColorMap(heatmap_uint8, colormap)
    heatmap_colored_rgb = cv2.cvtColor(heatmap_colored_bgr, cv2.COLOR_BGR2RGB)

    # Blend original and heatmap
    superimposed_rgb = cv2.addWeighted(
        original_rgb_image,
        1.0 - alpha,
        heatmap_colored_rgb,
        alpha,
        0
    )

    return superimposed_rgb


def generate_side_by_side_visualization(
    original_rgb_image: np.ndarray,
    superimposed_rgb_image: np.ndarray,
    title_left: str = "Original MRI Scan",
    title_right: str = "Grad-CAM Localization"
) -> np.ndarray:
    """
    Create a clean side-by-side comparative panel with medical annotations.

    Returns:
        RGB numpy image suitable for saving or display.
    """
    h, w, c = original_rgb_image.shape
    banner_height = 40
    panel = np.zeros((h + banner_height, (w * 2) + 20, 3), dtype=np.uint8)
    panel.fill(20)  # Dark slate background

    # Insert left image
    panel[banner_height:banner_height + h, 0:w] = original_rgb_image

    # Insert right image
    panel[banner_height:banner_height + h, w + 20:(w * 2) + 20] = superimposed_rgb_image

    # Add text banners
    cv2.putText(panel, title_left, (15, 26), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (240, 240, 240), 2, cv2.LINE_AA)
    cv2.putText(panel, title_right, (w + 35, 26), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (50, 220, 255), 2, cv2.LINE_AA)

    return panel


def save_gradcam_result(
    original_rgb: np.ndarray,
    heatmap: np.ndarray,
    output_filename: str,
    output_dir: Path = config.GRADCAM_DIR
) -> Tuple[str, str]:
    """
    Save both the superimposed overlay and the side-by-side diagnostic image.

    Returns:
        Tuple of (overlay_filepath, side_by_side_filepath)
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    overlay = overlay_gradcam(original_rgb, heatmap)
    side_by_side = generate_side_by_side_visualization(original_rgb, overlay)

    overlay_path = output_dir / f"overlay_{output_filename}"
    sbs_path = output_dir / f"sbs_{output_filename}"

    # Convert RGB to BGR for cv2.imwrite
    cv2.imwrite(str(overlay_path), cv2.cvtColor(overlay, cv2.COLOR_RGB2BGR))
    cv2.imwrite(str(sbs_path), cv2.cvtColor(side_by_side, cv2.COLOR_RGB2BGR))

    logger.info("Saved Grad-CAM overlay to %s and SBS to %s", overlay_path, sbs_path)
    return str(overlay_path), str(sbs_path)
