# NeuroVision AI — Final Presentation Content

**Deck purpose:** Academic project review  
**Audience:** Internship faculty and project reviewers  
**Recommended length:** 12 slides  
**Prepared:** 15 October 2026  

> This is the corrected slide manuscript for the project. It replaces unsupported clinical, speed, compliance, and deployment claims in the existing deck. The PPTX still needs to be rebuilt from this manuscript before formal presentation.

## Slide 1 — NeuroVision AI

**Explainable Brain MRI Image Classification Prototype**  
Saranya · Marwadi University  
Machine Learning and Applied AI project

**Visual:** Project interface screenshot or a neutral MRI illustration. Do not use patient-identifiable data.

## Slide 2 — Project question

**How can an AI image-classification workflow be made understandable in a web demonstration?**

- Input: a single brain MRI image
- Output labels: Glioma, Meningioma, Pituitary, or No Tumor
- Focus: model workflow, explainability code, and application integration

**Footer:** Educational prototype; not for diagnosis or clinical decisions.

## Slide 3 — What the project contains

- EfficientNetB0 model construction and training code
- Image preprocessing and four-label prediction flow
- Grad-CAM implementation for model-derived predictions
- Flask interface, SQLite history, and PDF summary generation

**Visual:** A simple flow: MRI image → preprocessing → classifier → result and explanation → web interface.

## Slide 4 — System architecture

**User interface:** HTML, CSS, and JavaScript templates  
**Application:** Flask routes and upload handling  
**ML path:** TensorFlow/Keras EfficientNetB0, if a trained checkpoint loads  
**Persistence and output:** SQLite record, optional Grad-CAM output, generated PDF summary

**Implementation note:** The current predictor also contains a heuristic fallback. A result from that path is not an EfficientNet prediction.

## Slide 5 — Model approach

- EfficientNetB0 initialized with ImageNet weights
- 224 × 224 RGB input
- Custom head: global average pooling, batch normalization, dense layer, dropout, four-class softmax
- Training configuration: 10 feature-extraction epochs followed by 15 fine-tuning epochs

**Caption:** These are repository settings and architecture choices; they do not independently establish performance.

## Slide 6 — Explainability approach

- The Grad-CAM code uses gradients at a convolutional feature layer to form a class-specific activation map.
- A heatmap can help inspect which image regions influenced a model output.
- A heatmap is not a segmentation mask, causal explanation, or proof that a prediction is correct.
- If the model is unavailable, the current code can create a heuristic heatmap; that is not Grad-CAM.

**Visual:** Use a real-model Grad-CAM example only if its model checkpoint and source image are traceable. Otherwise, show a labeled code/workflow schematic without implying a measured result.

## Slide 7 — Web application

- Upload page for supported image files
- Prediction result with class scores
- History and dashboard pages backed by SQLite
- Generated PDF summary
- Public demonstration URL: `https://neurovision-ai-m0t6.onrender.com`

**Safety note:** Do not upload identifiable health information to the public demonstration site.

## Slide 8 — Evaluation evidence

**Values stored in `models/evaluation_metrics.json` (not reproduced from the current deployment):**

- Accuracy: 96.38%
- Macro F1: 0.9632
- Weighted F1: 0.9639
- Macro ROC-AUC: 0.9880
- Reported test size: 1,600 images

**Required caveat on slide:** The inspected checkout contains no saved trained-model checkpoint, and the prediction code has a heuristic fallback. These stored values are not verified live-system performance.

**Visual:** Simple metric table with “reported artifact values” label. Do not call them clinical accuracy or independently validated results.

## Slide 9 — Current limitation discovered

- Model weights were not present in the inspected checkout.
- Predictor may use filename words or an image heuristic to select a class.
- Some fallback confidence values are fixed in code.
- Fallback heatmaps are generated heuristically, not from model gradients.
- Dataset provenance and patient-level split evidence need to be documented.

**Takeaway:** Fixing the prediction path and reproducing evaluation are the next engineering priorities.

## Slide 10 — Responsible-use boundary

- Educational and demonstration use only
- Not validated for diagnosis, triage, or treatment
- “No Tumor” is only one dataset label; it does not rule out other conditions
- Local SQLite storage is not proof of privacy or regulatory compliance
- Use only non-identifiable demonstration images cleared for this purpose

## Slide 11 — Roadmap

1. Remove filename-based and heuristic class predictions; fail clearly when the model cannot load.
2. Save the model checkpoint and pin its configuration and hash.
3. Document data source, license, patient-level split, and duplicate checks.
4. Re-run evaluation and save predictions and metrics from the exact checkpoint.
5. Verify Grad-CAM and separate inference time from full request time.
6. Consider external validation only under an appropriate supervised research protocol.

## Slide 12 — Summary

**NeuroVision AI brings together** a brain MRI image-classification workflow, explainability code, and a web application in an educational prototype.

**Next proof point:** reproducible model evaluation with a traceable checkpoint and no heuristic predictions.

Saranya · NeuroVision AI · GitHub: `saranya230506/NeuroVision-AI`

## Speaker notes: sources and claim provenance

- Project-specific architecture, routes, and fallback behavior: repository files `src/model.py`, `src/predict.py`, `src/gradcam.py`, `app.py`, `config.py`.
- Recorded metrics: `models/evaluation_metrics.json`; label every value as stored/reported until the exact checkpoint and test procedure are reproduced.
- Project link and deployment URL: supplied by the author; live deployment content was not independently verified in the available browser session.
- No external medical-performance or market-size claims are used in this slide manuscript.
