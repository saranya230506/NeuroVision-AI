# IBM SkillsBuild - AICTE BharatCares Machine Learning & Applied AI Internship 2026
# LEAN CANVAS BUSINESS & OPERATIONAL MODEL

**Project Name:** NeuroVision AI  
**Focus Domain:** Healthcare & Medical Artificial Intelligence (SDG 3 & SDG 9)  
**Author:** Saranya (psaranya.126749@marwadiuniversity.ac.in)  
**Cohort:** Machine Learning & Applied AI (August - September 2026)  

---

## 📊 Visual Lean Canvas (9-Box Industry Matrix)

```
+-----------------------------------+-----------------------------------+-----------------------------------+-----------------------------------+-----------------------------------+
| 1. PROBLEM                        | 4. SOLUTION                       | 3. UNIQUE VALUE PROPOSITION       | 9. UNFAIR ADVANTAGE               | 2. CUSTOMER SEGMENTS              |
|                                   |                                   |                                   |                                   |                                   |
| • Critical shortage of certified  | • 4-class transfer learning model | "24/7 Expert Neuroradiology       | • Proprietary two-stage fine-     | • Primary: Diagnostic             |
|   neuroradiologists (1:100,000 in |   (EfficientNetB0) classifying    |  Second-Opinion with Visual       |   tuned EfficientNetB0 pipeline   |   Radiologists & Neuroradiologists|
|   rural/semi-urban regions).      |   Glioma, Meningioma, Pituitary,  |  Grad-CAM Confirmation and        |   incorporating CLAHE medical     | • Secondary: Neurosurgeons &      |
| • Diagnostic fatigue causing      |   and Normal brain parenchyma.    |  Automated PDF Medical Reports    |   contrast enhancement.           |   Neuro-Oncologists               |
|   10–25% interpretation error     | • Real-time Grad-CAM attention    |  in under 150 Milliseconds."      | • Real-time Grad-CAM explainable  | • Tertiary: Regional Diagnostic   |
|   rates in complex MRI studies.   |   heatmaps delineating tumor.     |                                   |   AI tightly coupled with vector  |   Imaging Centers & Tele-radiology|
| • "Black-box" AI skepticism due   | • Automated hospital-grade PDF    | High-Level Concept:               |   ReportLab PDF generation.       |   Networks                        |
|   to lack of visual explanations. |   radiology diagnostic reports.   | An intelligent, transparent       | • Validated on 7,200 curated      |                                   |
|                                   |                                   | clinical co-pilot reducing MRI    |   clinical MRI scans with         | Early Adopters:                   |
| Existing Alternatives:            |                                   | review latency by 60%.            |   >96% test accuracy.             | Private diagnostic chains &       |
| Manual reading; slow outsourced   |                                   |                                   |                                   | emergency trauma triage centers.  |
| tele-radiology; unexplainable CAD.|                                   |                                   |                                   |                                   |
+-----------------------------------+-----------------------------------+                                   +-----------------------------------+-----------------------------------+
| 8. KEY METRICS                    |                                   |                                   | 5. CHANNELS                       |                                   |
|                                   |                                   |                                   |                                   |                                   |
| • Model Accuracy (>96%) & AUC     |                                   |                                   | • Direct PACS / RIS integration   |                                   |
|   (>0.98) across 4 classes.       |                                   |                                   |   via RESTful API endpoints.      |                                   |
| • Diagnostic Latency (<150 ms/scan|                                   |                                   | • Tele-radiology enterprise cloud |                                   |
| • Radiologist triage time savings |                                   |                                   |   platforms (Render, AWS).        |                                   |
|   (target: 60% reduction).        |                                   |                                   | • Medical technology expos &      |                                   |
| • Daily active scans processed &  |                                   |                                   |   radiological conferences (RSNA).|                                   |
|   patient report downloads.       |                                   |                                   | • IBM SkillsBuild / AICTE showcase|                                   |
+-----------------------------------+-----------------------------------+-----------------------------------+-----------------------------------+-----------------------------------+
| 7. COST STRUCTURE                                                     | 6. REVENUE STREAMS                                                    |
|                                                                       |                                                                       |
| • Cloud GPU/CPU Compute & Storage (AWS / Render / DigitalOcean)        | • Per-Scan SaaS Subscription (e.g., ₹50 / $0.60 per diagnostic scan)  |
| • Data pipeline maintenance, dataset acquisition & model retraining   | • Annual Enterprise Hospital License (unlimited on-premise Docker)    |
| • Medical regulatory audit, HIPAA/GDPR data compliance validation     | • B2B Tele-radiology API Platform Licensing                           |
| • Full-stack engineering, continuous integration & clinical support   | • Academic & Research Institution Training Partnerships               |
+-----------------------------------------------------------------------+-----------------------------------------------------------------------+
```

---

## 📝 Detailed Block-by-Block Analysis

### 1. Problem
- **Neuroradiologist Bottleneck:** Rural hospitals and district diagnostic centers often wait 24 to 72 hours for an outsourced radiologist to interpret brain MRI studies.
- **Diagnostic Inconsistency:** Micro-adenomas or subtle meningiomas in early stages are easily missed during high-volume overnight emergency shifts.
- **Explainability Gap:** Clinicians reject traditional machine learning models because they cannot verify *why* a neural network arrived at a particular classification.

### 2. Customer Segments
- **Hospitals & Imaging Centers:** High-volume facilities seeking automated triaging to prioritize urgent high-grade gliomas ahead of routine scans.
- **Tele-Radiology Networks:** Virtual diagnostics platforms looking for automated pre-reads and structured draft reporting.
- **Clinicians in Remote Centers:** Primary care practitioners who need rapid confirmation before airlifting or transferring acute neurosurgical patients.

### 3. Unique Value Proposition (UVP)
- **Instant Medical Validation:** In under 150 milliseconds, clinicians receive a 4-class classification, a Grad-CAM visual attention heatmap overlaid on the MRI, and a board-certified PDF diagnostic report ready for immediate printing or sharing.

### 4. Solution
- **EfficientNetB0 Backbone:** Achieves exceptional transfer learning performance with only 5.3 million parameters.
- **Grad-CAM Integration:** Uses gradient backpropagation to the `top_conv` layer to visually pinpoint the exact spatial boundaries driving the diagnosis.
- **Full Clinical Stack:** Complete with patient history management, search filtering, Chart.js analytics, and automated ReportLab PDF reports.

### 5. Channels
- **Cloud & On-Premise Deployment:** Docker containers ready for local hospital intranets or secure healthcare cloud services.
- **REST API Endpoints:** Allows direct programmatic ingestion from DICOM PACS servers (`POST /api/predict`).
- **Academic & Healthcare Partnerships:** Showcased through AICTE and IBM SkillsBuild healthcare innovation tracks.

### 6. Revenue Streams
- **Volume-Based SaaS:** Affordable pay-per-scan model for outpatient clinics.
- **Enterprise Licensing:** Fixed annual fee for multi-specialty hospital networks with on-premise data residency guarantees.
- **White-Label API:** Integration into existing electronic health record (EHR) and tele-radiology systems.

### 7. Cost Structure
- **Compute Infrastructure:** Cloud GPU/CPU inference servers.
- **Compliance & Security:** Ensuring HIPAA, GDPR, and DICOM data confidentiality.
- **Engineering & Support:** Continuous model monitoring, retraining with new clinical cohorts, and platform updates.

### 8. Key Metrics
- **Clinical Performance:** Test Accuracy $\ge 96.0\%$, Macro F1 $\ge 0.96$, Macro AUC $\ge 0.98$.
- **Speed:** Total response time under 150 milliseconds per scan.
- **Productivity:** 60% reduction in radiologist initial triage and documentation drafting time.

### 9. Unfair Advantage
- **End-to-End Synergy:** Seamless integration of CLAHE preprocessing, compound scaled EfficientNetB0, Grad-CAM feature attribution, SQLite persistence, and vector PDF medical reporting in a single unified, production-ready codebase.
