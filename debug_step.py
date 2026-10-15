import sys
print("Step 1: start", flush=True)

import os
print("Step 2: os", flush=True)

import cv2
print("Step 3: cv2", flush=True)

import numpy as np
print("Step 4: numpy", flush=True)

import tensorflow as tf
print("Step 5: tf version:", tf.__version__, flush=True)

import keras
print("Step 6: keras version:", keras.__version__, flush=True)

from tensorflow.keras.applications import EfficientNetB0
print("Step 7: imported EfficientNetB0", flush=True)

model = EfficientNetB0(include_top=False, weights=None, input_shape=(224, 224, 3))
print("Step 8: constructed model with weights=None", flush=True)
