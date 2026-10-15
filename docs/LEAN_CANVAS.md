# NeuroVision AI — Lean Canvas

**Project stage:** Educational prototype  
**Prepared:** 15 October 2026  
**Owner:** Saranya (`saranya230506`)  
**Domain:** Explainable AI and brain MRI image classification  

> **Status key:** This canvas separates working prototype features from unvalidated product assumptions. NeuroVision AI is not a medical device or clinical service. No clinical benefit, market demand, customer commitment, revenue, regulatory status, or compliance claim has been established.

| 1. Problem | 4. Solution | 3. Unique value proposition | 9. Unfair advantage | 2. Customer segments |
|---|---|---|---|---|
| **Project-learning problem:** Students need a concrete way to demonstrate the full path from image data and model code to an explainable web demo.  **Research problem:** Model outputs are hard to assess if the model, evaluation split, and explanation behavior are not traceable.  **Current limitation:** The checked-in predictor may fall back to filename rules or image heuristics, and can generate a synthetic heatmap. | **Built in the prototype:** Flask app; four-label MRI image workflow; EfficientNetB0 model-building/training code; model-based Grad-CAM implementation; SQLite scan history; generated PDF summaries.  **Near-term solution work:** Make model-unavailable cases explicit, remove filename-driven predictions, bind Grad-CAM to real model inference, and make evaluation reproducible. | **For a project reviewer:** “A transparent, end-to-end learning prototype that shows how brain MRI image classification, explainability code, and a web application fit together—and clearly states what has and has not been validated.”  **Value demonstrated:** Integration and learning value, not clinical accuracy or faster care. | **Current:** No defensible unfair advantage identified. The software uses established open-source components and a public-style web workflow.  **Potential future asset:** A reproducible dataset/evaluation protocol, if established with appropriate permissions and independently verified. | **Primary now:** Student author, instructors, and academic reviewers.  **Possible future research users:** Medical-imaging researchers and educators, subject to validation and data permissions.  **Not a current customer:** Hospitals, radiology practices, or patients; the prototype is not suitable for clinical use. |
| 8. Key metrics |  |  | 5. Channels |  |
| **Engineering metrics:** Successful model loads; share of requests using genuine model inference; fallback/error count; inference and end-to-end latency measured on named hardware.  **Evaluation metrics:** Patient-level split provenance; accuracy, macro F1, per-class recall, confusion matrix, calibration, and external test performance.  **Explanation metrics:** Localization evaluation against annotated masks, if licensed masks are available.  **Current evidence:** `models/evaluation_metrics.json` records 0.9638 accuracy and 0.9632 macro F1 on 1,600 examples; these values have not been reproduced from a checkpoint in the inspected checkout. |  |  | **Current:** GitHub repository, project demonstration website, classroom or internship presentation.  **Future validation:** Supervised academic review and controlled research evaluation.  **Not established:** PACS/RIS integration, hospital distribution, or sales channels. |  |
| 7. Cost structure |  |  | 6. Revenue streams |  |
| **Current project costs:** Student development time; compute and storage for training; dataset preparation; deployment hosting; maintenance; documentation and evaluation.  **Potential research costs:** Dataset licensing, specialist review, privacy/security review, external validation, and regulatory assessment if the intended use changes. |  |  | **Current:** None; no monetization is implemented or validated.  **Possible later hypotheses:** Academic licensing, research collaboration, or a validated decision-support product, each requiring market discovery, rights review, and appropriate evidence before pricing. |  |

## Assumptions to validate

1. The training and test folders represent distinct patients and contain no duplicates or near-duplicates across splits.
2. The saved evaluation report can be reproduced using a saved checkpoint and a documented test manifest.
3. The public demonstration site loads the same code and model artifact as the repository checkout.
4. A real user can distinguish a model-derived Grad-CAM image from a fallback visualization.
5. Educators and reviewers find the end-to-end workflow useful for learning applied AI.
6. If the project ever moves beyond education, intended users, regulatory pathway, privacy controls, and customer needs will be established through separate discovery and review.

## Evidence and limits

The repository demonstrates a Flask interface, training code, model-based Grad-CAM code, SQLite persistence, and PDF generation. The checked-in metrics file reports high classification scores, but the inspected checkout had no saved trained-model weights file, and `src/predict.py` includes filename-based and image-heuristic fallbacks with fixed confidence values. Its fallback saliency image is synthetic. Therefore this canvas does not present the recorded metrics as verified live-system performance or assert clinical value.

**Next milestone:** remove or fail closed on the heuristic predictor; save a traceable model checkpoint; document dataset provenance and patient-level splits; reproduce the test metrics; and update the demo and project materials from that evidence.
