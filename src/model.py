"""
NeuroVision AI - Deep Learning Model Architecture
Implements transfer learning and fine-tuning with TensorFlow EfficientNetB0
for multi-class brain tumor classification (Glioma, Meningioma, Pituitary, No Tumor).
"""

import logging
import sys
from pathlib import Path
from typing import Optional, Tuple

try:
    import tensorflow as tf
    from tensorflow.keras import layers, models, regularizers
    from tensorflow.keras.applications import EfficientNetB0
    TF_AVAILABLE = True
except Exception as e:
    tf = None
    layers = None
    models = None
    regularizers = None
    EfficientNetB0 = None
    TF_AVAILABLE = False

import config

logger = logging.getLogger("NeuroVision.Model")


def build_model(
    num_classes: int = config.NUM_CLASSES,
    input_shape: Tuple[int, int, int] = config.INPUT_SHAPE,
    learning_rate: float = config.LEARNING_RATE_PHASE_1,
    freeze_base: bool = True
):
    """
    Construct the EfficientNetB0 Transfer Learning Architecture.

    Structure:
    Input (224x224x3)
      -> EfficientNetB0 Backbone (pre-trained on ImageNet, top excluded)
      -> GlobalAveragePooling2D
      -> BatchNormalization
      -> Dense(256, ReLU, L2 Regularization)
      -> Dropout(0.4)
      -> Dense(num_classes, Softmax)

    Args:
        num_classes: Number of classification targets (4).
        input_shape: Input image dimensions (224, 224, 3).
        learning_rate: Initial Adam optimizer learning rate.
        freeze_base: If True, freezes all backbone weights for initial warm-up.

    Returns:
        Compiled tf.keras.Model ready for Phase 1 training.
    """
    logger.info("Initializing EfficientNetB0 backbone with ImageNet weights...")
    base_model = EfficientNetB0(
        include_top=False,
        weights="imagenet",
        input_shape=input_shape
    )

    # Freeze backbone if requested for initial transfer learning phase
    base_model.trainable = not freeze_base

    # Build model using Functional API
    inputs = layers.Input(shape=input_shape, name="mri_input")
    x = base_model(inputs, training=False)
    x = layers.GlobalAveragePooling2D(name="global_avg_pool")(x)
    x = layers.BatchNormalization(name="head_batch_norm_1")(x)
    x = layers.Dense(
        256,
        activation="relu",
        kernel_regularizer=regularizers.l2(config.WEIGHT_DECAY),
        name="dense_feature_projection"
    )(x)
    x = layers.Dropout(config.DROPOUT_RATE, name="head_dropout")(x)
    outputs = layers.Dense(
        num_classes,
        activation="softmax",
        name="predictions"
    )(x)

    model = models.Model(inputs=inputs, outputs=outputs, name="NeuroVision_EfficientNetB0")

    compile_model(model, learning_rate=learning_rate)
    logger.info("Model built successfully. Total params: %d | Trainable: %d",
                model.count_params(),
                sum([tf.size(w).numpy() for w in model.trainable_weights]))
    return model


def compile_model(model: tf.keras.Model, learning_rate: float = config.LEARNING_RATE_PHASE_1) -> None:
    """
    Compile the model with Adam optimizer, Categorical Crossentropy,
    and comprehensive classification metrics.
    """
    optimizer = tf.keras.optimizers.Adam(learning_rate=learning_rate)
    loss = tf.keras.losses.CategoricalCrossentropy(label_smoothing=0.05)

    model.compile(
        optimizer=optimizer,
        loss=loss,
        metrics=[
            "accuracy",
            tf.keras.metrics.Precision(name="precision"),
            tf.keras.metrics.Recall(name="recall"),
            tf.keras.metrics.AUC(name="auc", multi_label=False)
        ]
    )


def unfreeze_for_fine_tuning(
    model: tf.keras.Model,
    num_layers: int = config.FINE_TUNE_LAYERS,
    learning_rate: float = config.LEARNING_RATE_PHASE_2
) -> None:
    """
    Unfreeze the top N layers of the EfficientNetB0 backbone for fine-tuning.
    Crucial best practice: keep BatchNormalization layers frozen in inference mode
    to prevent destruction of statistical estimates.

    Args:
        model: Built model containing the EfficientNetB0 base layer.
        num_layers: Number of top layers to unfreeze.
        learning_rate: Reduced learning rate for gentle fine-tuning (e.g. 1e-4).
    """
    # Locate backbone layer
    base_model = None
    for layer in model.layers:
        if "efficientnet" in layer.name.lower():
            base_model = layer
            break

    if base_model is None:
        logger.warning("Could not locate EfficientNet backbone; unfreezing top layers of main model.")
        base_model = model

    base_model.trainable = True

    # Freeze all layers except the last `num_layers`
    total_layers = len(base_model.layers)
    freeze_until = max(0, total_layers - num_layers)

    for layer in base_model.layers[:freeze_until]:
        layer.trainable = False

    # Keep all BatchNormalization layers non-trainable during fine-tuning
    for layer in base_model.layers[freeze_until:]:
        if isinstance(layer, layers.BatchNormalization):
            layer.trainable = False

    compile_model(model, learning_rate=learning_rate)
    trainable_count = sum([tf.size(w).numpy() for w in model.trainable_weights])
    logger.info("Fine-tuning configured. Unfrozen top %d layers. Trainable params: %d",
                num_layers, trainable_count)


def load_trained_model(model_path: Optional[Path] = None) -> tf.keras.Model:
    """
    Load a pre-trained model from disk. If the saved file does not exist,
    construct and return a freshly built model with ImageNet weights.

    Args:
        model_path: Path to the .keras or .h5 file.

    Returns:
        Loaded or freshly initialized tf.keras.Model.
    """
    if not TF_AVAILABLE:
        logger.warning("TensorFlow runtime not available in this Python environment; running in resilient diagnostic mode.")
        return None

    target_path = Path(model_path) if model_path else config.DEFAULT_MODEL_PATH
    backup_path = config.BACKUP_MODEL_PATH

    for candidate in [target_path, backup_path]:
        if candidate.exists():
            try:
                logger.info("Loading pre-trained model from %s", candidate)
                loaded_model = tf.keras.models.load_model(str(candidate), compile=False)
                compile_model(loaded_model, learning_rate=config.LEARNING_RATE_PHASE_2)
                return loaded_model
            except Exception as e:
                logger.error("Failed to load weights from %s: %s", candidate, e)

    logger.warning("No pre-trained model file found at %s. Initializing fresh model with ImageNet backbone.", target_path)
    fresh_model = build_model(freeze_base=False)
    return fresh_model
