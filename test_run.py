import traceback
import sys
import config
from src.predict import BrainTumorPredictor

print("Python version:", sys.version)
try:
    p = BrainTumorPredictor()
    sample = config.SAMPLES_DIR / "glioma_sample.jpg"
    print("Testing sample path:", sample, "exists:", sample.exists())
    res = p.predict(str(sample), filename_hint="glioma_sample.jpg", generate_cam=True)
    print("PREDICTION SUCCESSFUL!")
    print("Class:", res["predicted_class"])
    print("Confidence:", res["confidence_percentage"])
    print("GradCAM overlay:", res["gradcam_overlay_filename"])
except Exception as e:
    traceback.print_exc()
