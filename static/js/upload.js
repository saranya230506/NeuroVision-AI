/**
 * NeuroVision AI - MRI Upload, Scanner Animation & Inference Controller
 */

document.addEventListener('DOMContentLoaded', () => {
  const dropzone = document.getElementById('dropzone');
  const fileInput = document.getElementById('file-input');
  const uploadForm = document.getElementById('mri-upload-form');
  const previewContainer = document.getElementById('preview-container');
  const previewImg = document.getElementById('mri-preview-img');
  const scanViewport = document.getElementById('scanner-viewport');
  const scanStatusText = document.getElementById('scan-status-text');
  const analyzeBtn = document.getElementById('analyze-btn');
  const resetBtn = document.getElementById('reset-btn');
  
  // Results Elements
  const resultsCard = document.getElementById('results-card');
  const resPrimaryBadge = document.getElementById('res-primary-badge');
  const resConfidenceText = document.getElementById('res-confidence-text');
  const resSeverityText = document.getElementById('res-severity-text');
  const resDescriptionText = document.getElementById('res-description-text');
  const resRecommendationsList = document.getElementById('res-recommendations-list');
  const resViewReportBtn = document.getElementById('res-view-report-btn');
  const resDownloadPdfBtn = document.getElementById('res-download-pdf-btn');
  
  // Visual Switchers
  const toggleOriginalBtn = document.getElementById('toggle-original-btn');
  const toggleGradcamBtn = document.getElementById('toggle-gradcam-btn');
  const resVisualImg = document.getElementById('res-visual-img');
  
  let currentOriginalUrl = null;
  let currentGradcamUrl = null;

  if (!dropzone || !fileInput) return;

  // Dropzone drag & drop events
  ['dragenter', 'dragover'].forEach(eventName => {
    dropzone.addEventListener(eventName, (e) => {
      e.preventDefault();
      e.stopPropagation();
      dropzone.classList.add('dragover');
    }, false);
  });

  ['dragleave', 'drop'].forEach(eventName => {
    dropzone.addEventListener(eventName, (e) => {
      e.preventDefault();
      e.stopPropagation();
      dropzone.classList.remove('dragover');
    }, false);
  });

  dropzone.addEventListener('drop', (e) => {
    const dt = e.dataTransfer;
    const files = dt.files;
    if (files && files.length > 0) {
      handleFileSelected(files[0]);
    }
  });

  dropzone.addEventListener('click', () => {
    fileInput.click();
  });

  fileInput.addEventListener('change', () => {
    if (fileInput.files && fileInput.files.length > 0) {
      handleFileSelected(fileInput.files[0]);
    }
  });

  function handleFileSelected(file) {
    if (!file.type.startsWith('image/')) {
      window.showToast('Please upload a valid image format (PNG, JPG, JPEG, WEBP)', 'error');
      return;
    }
    if (file.size > 16 * 1024 * 1024) {
      window.showToast('File size exceeds 16 MB limit', 'error');
      return;
    }

    const reader = new FileReader();
    reader.onload = (e) => {
      previewImg.src = e.target.result;
      previewContainer.classList.remove('d-none');
      dropzone.classList.add('d-none');
      analyzeBtn.disabled = false;
      scanStatusText.textContent = `Scan ready: ${file.name} (${(file.size / 1024).toFixed(1)} KB)`;
    };
    reader.readAsDataURL(file);
  }

  // Reset Scanner
  if (resetBtn) {
    resetBtn.addEventListener('click', () => {
      fileInput.value = '';
      previewImg.src = '';
      previewContainer.classList.add('d-none');
      dropzone.classList.remove('d-none');
      analyzeBtn.disabled = true;
      scanStatusText.textContent = 'Upload or drag an MRI scan to begin diagnosis.';
      if (resultsCard) resultsCard.classList.add('d-none');
      if (scanViewport) scanViewport.classList.remove('scanning');
    });
  }

  // Handle Form Submission
  if (uploadForm) {
    uploadForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      if (!fileInput.files || fileInput.files.length === 0) {
        window.showToast('Please select or drop an MRI scan first.', 'error');
        return;
      }

      const formData = new FormData(uploadForm);
      await executeInference('/api/predict', formData);
    });
  }

  // Handle 1-Click Sample Testing
  const sampleButtons = document.querySelectorAll('.sample-pill-btn');
  sampleButtons.forEach(btn => {
    btn.addEventListener('click', async () => {
      const sampleType = btn.getAttribute('data-sample');
      if (!sampleType) return;
      
      scanStatusText.textContent = `Loading reference scan for ${sampleType}...`;
      if (previewContainer) previewContainer.classList.remove('d-none');
      if (dropzone) dropzone.classList.add('d-none');
      
      await executeInference(`/api/sample/${sampleType}`, null, 'POST');
    });
  });

  // Execute Prediction API Call
  async function executeInference(url, bodyData = null, method = 'POST') {
    // Start radar animation
    if (scanViewport) scanViewport.classList.add('scanning');
    analyzeBtn.disabled = true;
    scanStatusText.innerHTML = '<span class="spinner-border spinner-border-sm me-2 text-info"></span> Analyzing neural activations and extracting Grad-CAM heatmap...';
    if (resultsCard) resultsCard.classList.add('d-none');

    try {
      const response = await fetch(url, {
        method: method,
        body: bodyData
      });

      const data = await response.json();

      if (!response.ok || !data.success) {
        throw new Error(data.error || 'Failed to process brain MRI image.');
      }

      displayResults(data);
      window.showToast(`Diagnostic Assessment Complete: ${data.predicted_class} (${data.confidence_percentage}%)`, 'success');

    } catch (err) {
      console.error(err);
      window.showToast(err.message, 'error');
      scanStatusText.textContent = 'Diagnostic error occurred. Please try again.';
    } finally {
      if (scanViewport) scanViewport.classList.remove('scanning');
      analyzeBtn.disabled = false;
    }
  }

  // Render Prediction Results into UI
  function displayResults(data) {
    scanStatusText.textContent = `Diagnosis Completed for Patient ID: ${data.patient_id}`;

    currentOriginalUrl = data.image_url;
    currentGradcamUrl = data.gradcam_overlay_url || data.image_url;

    // Set visualization image
    if (resVisualImg) {
      resVisualImg.src = currentGradcamUrl;
    }

    // Badge & Confidence
    const pClass = data.predicted_class;
    let badgeClass = 'badge-notumor';
    if (pClass === 'Glioma') badgeClass = 'badge-glioma';
    else if (pClass === 'Meningioma') badgeClass = 'badge-meningioma';
    else if (pClass === 'Pituitary') badgeClass = 'badge-pituitary';

    if (resPrimaryBadge) {
      resPrimaryBadge.className = `badge fs-6 px-3 py-2 ${badgeClass}`;
      resPrimaryBadge.textContent = pClass;
    }

    if (resConfidenceText) {
      resConfidenceText.textContent = `${data.confidence_percentage}% Confidence`;
    }

    // Metadata
    const meta = data.metadata || {};
    if (resSeverityText) {
      resSeverityText.textContent = meta.severity || 'Normal Clinical Finding';
    }
    if (resDescriptionText) {
      resDescriptionText.textContent = meta.description || '';
    }

    // Recommendations List
    if (resRecommendationsList && meta.recommended_actions) {
      resRecommendationsList.innerHTML = meta.recommended_actions
        .map(action => `<li class="mb-1"><i class="bi bi-arrow-right-circle text-primary me-2"></i>${action}</li>`)
        .join('');
    }

    // Probability Bars
    const probs = data.probabilities || {};
    ['Glioma', 'Meningioma', 'No Tumor', 'Pituitary'].forEach(cls => {
      const slug = cls.toLowerCase().replace(' ', '');
      const bar = document.getElementById(`prob-bar-${slug}`);
      const val = document.getElementById(`prob-val-${slug}`);
      const pct = probs[cls] || 0.0;
      if (bar) {
        bar.style.width = '0%';
        setTimeout(() => { bar.style.width = `${pct}%`; }, 100);
      }
      if (val) {
        val.textContent = `${pct}%`;
      }
    });

    // Action Buttons
    if (resViewReportBtn) {
      resViewReportBtn.href = data.report_url;
    }
    if (resDownloadPdfBtn) {
      resDownloadPdfBtn.href = data.pdf_url;
    }

    // Show Results Card
    if (resultsCard) {
      resultsCard.classList.remove('d-none');
      resultsCard.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  }

  // Toggle between Original MRI and Grad-CAM Overlay
  if (toggleOriginalBtn && toggleGradcamBtn && resVisualImg) {
    toggleOriginalBtn.addEventListener('click', () => {
      toggleOriginalBtn.classList.replace('btn-outline-primary', 'btn-primary');
      toggleGradcamBtn.classList.replace('btn-primary', 'btn-outline-primary');
      if (currentOriginalUrl) resVisualImg.src = currentOriginalUrl;
    });

    toggleGradcamBtn.addEventListener('click', () => {
      toggleGradcamBtn.classList.replace('btn-outline-primary', 'btn-primary');
      toggleOriginalBtn.classList.replace('btn-primary', 'btn-outline-primary');
      if (currentGradcamUrl) resVisualImg.src = currentGradcamUrl;
    });
  }

});
