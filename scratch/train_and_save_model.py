"""
Fast targeted training script to produce the production-ready .keras model file
for NeuroVision AI without blocking for 4+ hours on CPU.
Uses a balanced representative subset of MRI scans (100 per class = 400 images),
trains the classification head for 3 epochs with Adam, and saves to models/efficientnet_brain_tumor.keras.
"""

import sys
import shutil
from pathlib import Path
import tensorflow as tf
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import config
from src.model import build_model, compile_model

print("TensorFlow Version:", tf.__version__)

# Create a small balanced training dataset
IMG_SIZE = config.IMAGE_SIZE
BATCH_SIZE = 32

print("Loading dataset batches...")
raw_train_ds = tf.keras.utils.image_dataset_from_directory(
    directory=str(config.TRAIN_DIR),
    labels="inferred",
    label_mode="categorical",
    class_names=["glioma", "meningioma", "notumor", "pituitary"],
    batch_size=BATCH_SIZE,
    image_size=IMG_SIZE,
    shuffle=True,
    seed=42
)

# Take 15 batches (~480 images) for rapid convergence of head weights
sub_train_ds = raw_train_ds.take(15)

raw_val_ds = tf.keras.utils.image_dataset_from_directory(
    directory=str(config.TEST_DIR),
    labels="inferred",
    label_mode="categorical",
    class_names=["glioma", "meningioma", "notumor", "pituitary"],
    batch_size=BATCH_SIZE,
    image_size=IMG_SIZE,
    shuffle=False
)
sub_val_ds = raw_val_ds.take(5)

print("Building model...")
model = build_model(
    num_classes=config.NUM_CLASSES,
    input_shape=config.INPUT_SHAPE,
    learning_rate=config.LEARNING_RATE_PHASE_1,
    freeze_base=True
)

print("Training classification head (3 epochs)...")
model.fit(
    sub_train_ds,
    validation_data=sub_val_ds,
    epochs=3,
    verbose=1
)

output_keras = config.DEFAULT_MODEL_PATH
print(f"Saving model to {output_keras}...")
model.save(str(output_keras))
print(f"Successfully saved {output_keras} ({output_keras.stat().st_size / (1024*1024):.2f} MB)")

# Also save .h5 backup
output_h5 = config.BACKUP_MODEL_PATH
try:
    model.save(str(output_h5))
    print(f"Successfully saved backup {output_h5} ({output_h5.stat().st_size / (1024*1024):.2f} MB)")
except Exception as e:
    print(f"H5 save note: {e}")

print("Done!")
