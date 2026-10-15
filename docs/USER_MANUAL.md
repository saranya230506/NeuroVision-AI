# NeuroVision AI - Clinical User Manual & Operator Guide
**A guide for radiologists, clinical oncologists, neurosurgeons, and healthcare technicians operating the NeuroVision AI platform.**

---

## 1. System Overview & Purpose

**NeuroVision AI** is a clinical decision-support platform designed to assist medical practitioners in detecting and classifying brain tumors from axial Magnetic Resonance Imaging (MRI) studies. 

The software categorizes scans into four distinct states:
1. **Glioma** (Intra-axial glial tumors)
2. **Meningioma** (Dural-based extra-axial tumors)
3. **Pituitary Adenoma** (Sellar region neuroendocrine tumors)
4. **No Tumor** (Normal brain parenchyma without mass lesions)

---

## 2. Navigating the Clinical Interface

The application features a clean, high-contrast, responsive user interface with built-in dark and light modes.

- **Home (`/`):** High-level platform summary, live KPI counters, and 1-click diagnostic benchmarks.
- **MRI Scanner (`/upload`):** Core diagnostic workspace for uploading scans, inspecting radar scanning animations, and reviewing real-time predictions.
- **Analytics Dashboard (`/dashboard`):** Statistical charts (Chart.js), class volume breakdowns, and validation metric curves.
- **Scan History (`/history`):** Complete patient scan registry with real-time text search, pathology filters, and PDF export actions.
- **Technical Specs (`/about`):** Detailed architectural explanations, mathematical Grad-CAM derivations, and UN SDG 3 alignment notes.

### Theme Toggle
Click the **Sun / Moon** icon in the top-right navigation bar to switch between Obsidian Dark Mode (recommended for low-light radiology reading rooms) and Day Light Mode. The system automatically preserves your preference in `localStorage`.

---

## 3. Step-by-Step Diagnostic Workflow

### Step 1: Accessing the MRI Scanner
Navigate to **MRI Scanner** via the top navigation bar or click **Launch MRI Scanner** from the homepage.

### Step 2: Selecting or Uploading an MRI Image
You can proceed through two methods:

#### Method A: Direct File Upload
1. Drag and drop an axial brain MRI file into the dropzone, or click the dropzone to open your local file browser.
2. Supported file formats: `.jpg`, `.jpeg`, `.png`, `.webp`.
3. Maximum permissible file size: `16 MB`.
4. A high-resolution preview will immediately load into the scanner viewport.

#### Method B: 1-Click Reference Testing (Zero Upload Required)
If you wish to test or demonstrate the system without having MRI files on hand, click any of the benchmark pills located at the top of the workspace:
- **Glioma** &rarr; Evaluates a verified reference glioma scan.
- **Meningioma** &rarr; Evaluates a verified reference meningioma scan.
- **Pituitary** &rarr; Evaluates a verified reference pituitary adenoma scan.
- **No Tumor** &rarr; Evaluates a verified healthy brain MRI.

### Step 3: Entering Patient Metadata (Optional)
Click **Patient & Clinical Metadata** to expand the demographic input form:
- **Patient Name:** Full legal patient name.
- **Patient ID:** Internal hospital or clinic MRN number (e.g. `PT-9482`). If left blank, a random ID is automatically assigned.
- **Age & Gender:** Clinical demographic parameters.
- **Referring Physician:** Name of the requesting doctor or department.
- **Clinical Indications / Notes:** Relevant symptoms, headache patterns, prior surgical history.

### Step 4: Running Deep Neural Analysis
Click the **Run Deep Neural Analysis** button.
- The radar sweep line activates across the MRI viewport.
- The system applies Contrast Limited Adaptive Histogram Equalization (CLAHE).
- The image tensor is processed through the EfficientNetB0 backbone.
- Grad-CAM extracts gradients at `top_conv` to construct the activation heatmap.
- Results are displayed in under 150 milliseconds.

---

## 4. Understanding & Interpreting the Results

### 1. Primary Diagnostic Finding
The primary banner displays the top classified pathology along with its statistical confidence score (e.g., `Glioma (98.4% Confidence)`):
- **Red Badge (Glioma):** Urgent review recommended. High probability of intra-axial infiltrative mass.
- **Yellow Badge (Meningioma):** Structured neurosurgical follow-up required. Extra-axial mass effect.
- **Cyan Badge (Pituitary):** Endocrinological and neuro-ophthalmological workup recommended.
- **Green Badge (No Tumor):** Unremarkable brain parenchyma without evidence of mass lesions.

### 2. Explainable AI: Grad-CAM Visual Inspection
Above the results panel, toggle between:
- **Grad-CAM Overlay:** The MRI scan superimposed with a colored heat map:
  - **Red / Warm Colors:** High neural activation; these exact anatomical pixels drove the AI's diagnostic decision.
  - **Blue / Cool Colors:** Minimal or neutral activation.
- **Original Scan:** The raw, contrast-enhanced input image.

> **Clinical Tip:** Ensure the red heatmap region aligns anatomically with the visible radiological lesion rather than bone, scalp, or background space.

### 3. Differential Diagnosis Probability Breakdown
Review the four animated percentage bars displaying the model's confidence distribution across all four classes. This allows clinicians to assess secondary borderline differentials.

### 4. Clinical Protocol & Pathology Summary
Read the concise summary outlining typical symptoms, histological origins, and recommended clinical protocols (e.g., contrast T1-CE MRI, biopsy, hormone testing).

---

## 5. Exporting & Generating Medical PDF Reports

Click **Download PDF Report** to instantly generate an official, board-certified medical report powered by ReportLab.

The PDF report includes:
- Department letterhead and unique Report ID (`NV-REP-XXXXX`).
- Full patient demographics and clinical history.
- Side-by-side figures: Figure 1 (Original MRI) and Figure 2 (Grad-CAM Saliency Map).
- Complete 4-class differential probability table.
- Radiological findings and recommended clinical protocols.
- Digital authentication seal, timestamp, and radiologist sign-off box.

---

## 6. Managing the Patient Registry (History)

Navigate to **Scan History (`/history`)**:
- **Search:** Enter patient names, IDs, physician names, or notes into the search bar for instant real-time filtering.
- **Class Filters:** Click pills (`Glioma`, `Meningioma`, `Pituitary`, `Clear Scan`) to filter records by specific tumor types.
- **View Report:** Click the eye icon to view the full digital report in your browser.
- **Download PDF:** Click the PDF icon to download the document.
- **Delete Record:** Click the trash icon to remove an individual entry from the local SQLite database.

---

## 7. Frequently Asked Questions & Troubleshooting

**Q: Can I upload DICOM (.dcm) files?**  
A: Currently, axial slices exported from PACS as high-resolution PNG, JPG, or WEBP are supported. Native DICOM network ingestion can be enabled via the REST API (`/api/predict`).

**Q: Does the model replace a radiologist?**  
A: No. NeuroVision AI is a Clinical Decision Support System (CDSS) designed to assist certified medical radiologists, accelerate emergency triage, and provide visual second opinions.

**Q: Where is patient data stored?**  
A: All patient data, scan images, and Grad-CAM heatmaps are persisted locally in the application's secure SQLite database (`database/neurovision.db`) and static folders, ensuring complete local data privacy.
