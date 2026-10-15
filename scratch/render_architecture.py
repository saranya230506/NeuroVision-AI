import base64
import os
import subprocess

def get_base64_img(path):
    with open(path, "rb") as f:
        data = f.read()
    ext = os.path.splitext(path)[1].lower()
    mime = "image/png" if ext == ".png" else "image/jpeg"
    return f"data:{mime};base64,{base64.b64encode(data).decode('utf-8')}"

raw_mri_b64 = get_base64_img("static/images/arch_pure_mri.jpg")
clahe_mri_b64 = get_base64_img("static/images/arch_pure_clahe.jpg")
jet_b64 = get_base64_img("static/images/arch_pure_jet.jpg")
overlay_b64 = get_base64_img("static/images/arch_pure_overlay.jpg")
pdf_preview_b64 = get_base64_img("static/images/arch_pure_pdf.jpg")
hist_preview_b64 = get_base64_img("static/images/arch_pure_hist.jpg")

html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>NeuroVision AI Realistic System Architecture</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap');

  * {{
    box-sizing: border-box;
    margin: 0;
    padding: 0;
  }}

  body {{
    background: radial-gradient(circle at 50% 0%, #0d192e 0%, #070c17 45%, #03060a 100%);
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    color: #e2e8f0;
    width: 1720px;
    height: 2620px;
    padding: 45px 50px 60px 50px;
    position: relative;
    overflow: hidden;
  }}

  /* High-tech grid background */
  body::before {{
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; bottom: 0;
    background-image: 
      linear-gradient(rgba(14, 165, 233, 0.05) 1px, transparent 1px),
      linear-gradient(90deg, rgba(14, 165, 233, 0.05) 1px, transparent 1px);
    background-size: 36px 36px;
    pointer-events: none;
    z-index: 0;
  }}

  .content-wrapper {{
    position: relative;
    z-index: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    width: 100%;
  }}

  /* Header */
  .header {{
    text-align: center;
    margin-bottom: 32px;
  }}

  .header-badge {{
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: rgba(14, 165, 233, 0.12);
    border: 1px solid rgba(56, 189, 248, 0.35);
    color: #38bdf8;
    padding: 6px 18px;
    border-radius: 999px;
    font-size: 13px;
    font-weight: 700;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    margin-bottom: 12px;
  }}

  .header-badge .pulse-dot {{
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: #38bdf8;
    box-shadow: 0 0 10px #38bdf8;
  }}

  h1 {{
    font-size: 42px;
    font-weight: 800;
    letter-spacing: -0.5px;
    background: linear-gradient(135deg, #ffffff 30%, #93c5fd 70%, #38bdf8 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 8px;
  }}

  .subtitle {{
    font-size: 16px;
    color: #94a3b8;
    font-weight: 500;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 16px;
  }}

  .spec-tag {{
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.1);
    padding: 3px 10px;
    border-radius: 6px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;
    color: #cbd5e1;
  }}

  /* Card Component */
  .card {{
    background: linear-gradient(145deg, rgba(16, 24, 40, 0.92) 0%, rgba(9, 14, 25, 0.96) 100%);
    border: 1px solid rgba(56, 189, 248, 0.22);
    box-shadow: 0 12px 35px -10px rgba(0, 0, 0, 0.65), 0 0 25px rgba(14, 165, 233, 0.08);
    border-radius: 18px;
    position: relative;
    backdrop-filter: blur(16px);
  }}

  .card-header {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 14px 24px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.07);
    background: rgba(255, 255, 255, 0.02);
    border-radius: 18px 18px 0 0;
  }}

  .card-title {{
    font-size: 18px;
    font-weight: 700;
    color: #f1f5f9;
    display: flex;
    align-items: center;
    gap: 12px;
  }}

  .card-title .icon-box {{
    width: 32px;
    height: 32px;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 15px;
    font-weight: 800;
  }}

  .icon-blue {{ background: rgba(56, 189, 248, 0.15); color: #38bdf8; border: 1px solid rgba(56, 189, 248, 0.3); }}
  .icon-purple {{ background: rgba(168, 85, 247, 0.15); color: #c084fc; border: 1px solid rgba(168, 85, 247, 0.3); }}
  .icon-emerald {{ background: rgba(16, 185, 129, 0.15); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.3); }}
  .icon-amber {{ background: rgba(245, 158, 11, 0.15); color: #fbbf24; border: 1px solid rgba(245, 158, 11, 0.3); }}
  .icon-rose {{ background: rgba(244, 63, 94, 0.15); color: #fb7185; border: 1px solid rgba(244, 63, 94, 0.3); }}

  .card-pill {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;
    font-weight: 600;
    padding: 4px 12px;
    border-radius: 6px;
    background: rgba(14, 165, 233, 0.12);
    border: 1px solid rgba(56, 189, 248, 0.25);
    color: #38bdf8;
  }}

  .card-body {{
    padding: 22px 26px;
  }}

  /* Connectors */
  .connector-v {{
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 48px;
    position: relative;
    z-index: 2;
  }}

  .connector-line {{
    width: 2px;
    height: 100%;
    background: linear-gradient(180deg, #38bdf8, #818cf8);
    position: relative;
  }}

  .connector-arrow {{
    width: 0;
    height: 0;
    border-left: 6px solid transparent;
    border-right: 6px solid transparent;
    border-top: 8px solid #818cf8;
    margin-top: -2px;
  }}

  .connector-pulse {{
    position: absolute;
    width: 6px;
    height: 6px;
    background: #ffffff;
    border-radius: 50%;
    box-shadow: 0 0 10px #38bdf8, 0 0 20px #38bdf8;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
  }}

  /* Top Section: Single Column Pipeline */
  .stage-box {{
    width: 900px;
  }}

  /* Image compare layout in CLAHE */
  .mri-compare-row {{
    display: flex;
    align-items: center;
    gap: 24px;
    justify-content: center;
  }}

  .mri-frame {{
    background: #020617;
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-radius: 12px;
    padding: 10px;
    text-align: center;
    width: 170px;
    box-shadow: inset 0 0 15px rgba(0, 0, 0, 0.8);
    position: relative;
  }}

  .mri-frame img {{
    width: 150px;
    height: 150px;
    border-radius: 8px;
    object-fit: cover;
    display: block;
    margin: 0 auto;
  }}

  .mri-label {{
    margin-top: 8px;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.5px;
    color: #94a3b8;
    text-transform: uppercase;
  }}

  .mri-orientation {{
    position: absolute;
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    color: #38bdf8;
    font-weight: 800;
    background: rgba(0, 0, 0, 0.6);
    padding: 1px 4px;
    border-radius: 3px;
  }}
  .orient-a {{ top: 12px; left: 50%; transform: translateX(-50%); }}
  .orient-p {{ bottom: 32px; left: 50%; transform: translateX(-50%); }}
  .orient-l {{ top: 50%; right: 12px; transform: translateY(-50%); }}
  .orient-r {{ top: 50%; left: 12px; transform: translateY(-50%); }}

  .meta-list {{
    list-style: none;
    display: flex;
    flex-direction: column;
    gap: 8px;
    font-size: 14px;
    color: #cbd5e1;
  }}

  .meta-list li {{
    display: flex;
    align-items: center;
    gap: 10px;
    line-height: 1.4;
  }}

  .meta-bullet {{
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: #38bdf8;
    box-shadow: 0 0 8px #38bdf8;
    flex-shrink: 0;
  }}

  /* EfficientNet Architecture Visualization */
  .backbone-grid {{
    display: grid;
    grid-template-columns: repeat(7, 1fr);
    gap: 10px;
    margin-top: 16px;
    background: rgba(2, 6, 23, 0.5);
    padding: 12px;
    border-radius: 12px;
    border: 1px solid rgba(255, 255, 255, 0.05);
  }}

  .stage-card {{
    background: rgba(15, 23, 42, 0.85);
    border: 1px solid rgba(56, 189, 248, 0.2);
    border-radius: 8px;
    padding: 9px 6px;
    text-align: center;
  }}

  .stage-card .st-name {{
    font-size: 11px;
    font-weight: 700;
    color: #38bdf8;
    margin-bottom: 2px;
  }}

  .stage-card .st-block {{
    font-size: 10px;
    color: #94a3b8;
    font-family: 'JetBrains Mono', monospace;
  }}

  .stage-card .st-res {{
    font-size: 9px;
    color: #64748b;
    margin-top: 4px;
  }}

  /* Bifurcation Section */
  .bifurcation-wrapper {{
    width: 100%;
    display: flex;
    flex-direction: column;
    align-items: center;
    position: relative;
  }}

  .split-badge {{
    background: linear-gradient(90deg, #10b981 0%, #6366f1 50%, #f59e0b 100%);
    padding: 1px;
    border-radius: 999px;
    margin: 8px 0;
    z-index: 10;
  }}

  .split-badge-inner {{
    background: #0b1329;
    padding: 6px 22px;
    border-radius: 999px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 13px;
    font-weight: 700;
    color: #f8fafc;
    display: flex;
    align-items: center;
    gap: 8px;
  }}

  .bifurcation-branches {{
    display: flex;
    justify-content: space-between;
    width: 1620px;
    gap: 40px;
    margin-top: 15px;
    position: relative;
  }}

  /* Split connector line */
  .split-junction {{
    width: 820px;
    height: 38px;
    border-top: 2px solid #818cf8;
    border-left: 2px solid #10b981;
    border-right: 2px solid #f59e0b;
    border-top-left-radius: 16px;
    border-top-right-radius: 16px;
    margin-top: -10px;
    position: relative;
  }}

  .branch-col {{
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 20px;
  }}

  .branch-tag {{
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 6px 18px;
    border-radius: 8px;
    font-size: 13px;
    font-weight: 700;
    letter-spacing: 0.5px;
    text-transform: uppercase;
    margin-bottom: 4px;
    width: fit-content;
  }}

  .tag-forward {{
    background: rgba(16, 185, 129, 0.15);
    border: 1px solid rgba(16, 185, 129, 0.4);
    color: #34d399;
  }}

  .tag-backprop {{
    background: rgba(245, 158, 11, 0.15);
    border: 1px solid rgba(245, 158, 11, 0.4);
    color: #fbbf24;
  }}

  /* Class distribution bars */
  .prob-bars {{
    display: flex;
    flex-direction: column;
    gap: 12px;
    margin-top: 12px;
  }}

  .prob-row {{
    display: flex;
    flex-direction: column;
    gap: 4px;
  }}

  .prob-info {{
    display: flex;
    justify-content: space-between;
    font-size: 13px;
    font-weight: 600;
  }}

  .prob-bar-bg {{
    width: 100%;
    height: 10px;
    background: rgba(255, 255, 255, 0.06);
    border-radius: 999px;
    overflow: hidden;
  }}

  .prob-bar-fill {{
    height: 100%;
    border-radius: 999px;
  }}

  .fill-glioma {{ width: 95.8%; background: linear-gradient(90deg, #ef4444, #f87171); box-shadow: 0 0 10px rgba(239, 68, 68, 0.5); }}
  .fill-meningioma {{ width: 2.4%; background: #38bdf8; }}
  .fill-pituitary {{ width: 1.2%; background: #a855f7; }}
  .fill-normal {{ width: 0.6%; background: #10b981; }}

  /* Math equation card */
  .math-block {{
    background: rgba(2, 6, 23, 0.6);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 10px;
    padding: 12px 18px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 13px;
    color: #f8fafc;
    margin-top: 10px;
    line-height: 1.6;
  }}

  .math-highlight {{
    color: #fbbf24;
    font-weight: 700;
  }}

  /* Bottom Engine Section */
  .engine-junction {{
    width: 820px;
    height: 38px;
    border-bottom: 2px solid #818cf8;
    border-left: 2px solid #10b981;
    border-right: 2px solid #f59e0b;
    border-bottom-left-radius: 16px;
    border-bottom-right-radius: 16px;
    margin-top: 10px;
  }}

  .engine-card {{
    width: 1620px;
    background: linear-gradient(145deg, rgba(16, 24, 40, 0.95) 0%, rgba(9, 14, 26, 0.98) 100%);
    border: 1px solid rgba(99, 102, 241, 0.35);
    box-shadow: 0 20px 45px -15px rgba(0, 0, 0, 0.8), 0 0 35px rgba(99, 102, 241, 0.15);
  }}

  .engine-grid {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 30px;
    padding: 24px;
  }}

  .sub-engine {{
    background: rgba(2, 6, 23, 0.55);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 14px;
    padding: 22px;
  }}

  .sub-engine-header {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 14px;
  }}

  .sub-engine-title {{
    font-size: 16px;
    font-weight: 700;
    color: #f8fafc;
    display: flex;
    align-items: center;
    gap: 8px;
  }}

  .preview-box {{
    border-radius: 10px;
    overflow: hidden;
    border: 1px solid rgba(255, 255, 255, 0.12);
    margin-top: 14px;
    height: 185px;
    background: #020617;
  }}

  .preview-box img {{
    width: 100%;
    height: 185px;
    object-fit: cover;
    object-position: top;
    display: block;
  }}

  /* Badges & Accents */
  .badge-tag {{
    font-size: 11px;
    font-weight: 600;
    padding: 3px 8px;
    border-radius: 4px;
  }}
  .badge-sqlite {{ background: rgba(14, 165, 233, 0.15); color: #38bdf8; border: 1px solid rgba(14, 165, 233, 0.3); }}
  .badge-pdf {{ background: rgba(239, 68, 68, 0.15); color: #f87171; border: 1px solid rgba(239, 68, 68, 0.3); }}

  /* Footer bar */
  .footer-bar {{
    margin-top: 28px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    width: 1620px;
    padding-top: 18px;
    border-top: 1px solid rgba(255, 255, 255, 0.08);
    font-size: 13px;
    color: #64748b;
  }}

  .footer-bar .brand {{
    font-weight: 700;
    color: #94a3b8;
    display: flex;
    align-items: center;
    gap: 8px;
  }}
</style>
</head>
<body>

<div class="content-wrapper">

  <!-- Header -->
  <div class="header">
    <div class="header-badge">
      <div class="pulse-dot"></div>
      Clinical Medical AI & Explainability Architecture
    </div>
    <h1>NEUROVISION AI &bull; DEEP LEARNING SYSTEM PIPELINE</h1>
    <div class="subtitle">
      <span>Axial Brain MRI Diagnostic Inference & Explainability Topology</span>
      <span class="spec-tag">TensorFlow / Keras 3.x</span>
      <span class="spec-tag">EfficientNetB0 (5.3M)</span>
      <span class="spec-tag">Grad-CAM XAI</span>
      <span class="spec-tag">Flask 3.x WSGI</span>
    </div>
  </div>

  <!-- Stage 1: Patient Axial Brain MRI Scan -->
  <div class="card stage-box">
    <div class="card-header">
      <div class="card-title">
        <div class="icon-box icon-blue">1</div>
        Patient Axial Brain MRI Scan Acquisition
      </div>
      <div class="card-pill">Input Tensor Dimension: (1, 224, 224, 3)</div>
    </div>
    <div class="card-body">
      <div class="mri-compare-row">
        <div class="mri-frame">
          <span class="mri-orientation orient-a">A</span>
          <span class="mri-orientation orient-p">P</span>
          <span class="mri-orientation orient-l">L</span>
          <span class="mri-orientation orient-r">R</span>
          <img src="{raw_mri_b64}" alt="Axial MRI Scan" />
          <div class="mri-label">Patient Axial MRI</div>
        </div>
        <div style="flex: 1;">
          <ul class="meta-list">
            <li><div class="meta-bullet"></div><strong>Patient Axial Brain MRI Scan:</strong>&nbsp;Primary diagnostic imaging acquisition</li>
            <li><div class="meta-bullet"></div><strong>Input Tensor Dimension:</strong>&nbsp;<span class="spec-tag">(1, 224, 224, 3)</span> &bull; Float32 normalized to [0.0, 1.0]</li>
            <li><div class="meta-bullet"></div><strong>Anatomical Modalities:</strong>&nbsp;Axial Cross-Sectional T1, T2, and FLAIR pulse sequences</li>
            <li><div class="meta-bullet"></div><strong>Batch Ingestion:</strong>&nbsp;Zero-mean tensor streaming via multipart REST payload</li>
          </ul>
        </div>
      </div>
    </div>
  </div>

  <!-- Connector -->
  <div class="connector-v">
    <div class="connector-line"><div class="connector-pulse"></div></div>
    <div class="connector-arrow"></div>
  </div>

  <!-- Stage 2: OpenCV CLAHE Contrast Enhancement -->
  <div class="card stage-box">
    <div class="card-header">
      <div class="card-title">
        <div class="icon-box icon-purple">2</div>
        OpenCV CLAHE Contrast Enhancement
      </div>
      <div class="card-pill">LAB Color Space &bull; ClipLimit: 2.0 &bull; Grid: (8, 8)</div>
    </div>
    <div class="card-body">
      <div class="mri-compare-row">
        <div class="mri-frame">
          <img src="{raw_mri_b64}" alt="Before CLAHE" />
          <div class="mri-label" style="color: #64748b;">Raw Dynamic Range</div>
        </div>
        <div style="display: flex; flex-direction: column; align-items: center; gap: 4px;">
          <span style="font-size: 22px; color: #c084fc;">&rarr;</span>
          <span style="font-size: 11px; font-weight: 700; color: #a855f7; font-family: 'JetBrains Mono', monospace;">L-CHANNEL CLAHE</span>
        </div>
        <div class="mri-frame" style="border-color: rgba(168, 85, 247, 0.4); box-shadow: 0 0 15px rgba(168, 85, 247, 0.15);">
          <img src="{clahe_mri_b64}" alt="After CLAHE" />
          <div class="mri-label" style="color: #c084fc;">Equalized Ventricles</div>
        </div>
        <div style="flex: 1; margin-left: 10px;">
          <ul class="meta-list">
            <li><div class="meta-bullet" style="background: #c084fc; box-shadow: 0 0 8px #c084fc;"></div><strong>LAB Color Space (L-Channel CLAHE):</strong>&nbsp;Luminance equalization only</li>
            <li><div class="meta-bullet" style="background: #c084fc; box-shadow: 0 0 8px #c084fc;"></div><strong>ClipLimit = 2.0:</strong>&nbsp;Restricts noise amplification across homogeneous brain tissue</li>
            <li><div class="meta-bullet" style="background: #c084fc; box-shadow: 0 0 8px #c084fc;"></div><strong>GridSize = (8, 8):</strong>&nbsp;Calculates 64 localized contextual histogram tiles</li>
            <li><div class="meta-bullet" style="background: #c084fc; box-shadow: 0 0 8px #c084fc;"></div><strong>Boundary Sharpening:</strong>&nbsp;Accentuates subtle neoplastic margins and sulci</li>
          </ul>
        </div>
      </div>
    </div>
  </div>

  <!-- Connector -->
  <div class="connector-v">
    <div class="connector-line"><div class="connector-pulse"></div></div>
    <div class="connector-arrow"></div>
  </div>

  <!-- Stage 3: EfficientNetB0 CNN Backbone -->
  <div class="card stage-box">
    <div class="card-header">
      <div class="card-title">
        <div class="icon-box icon-emerald">3</div>
        EfficientNetB0 CNN Backbone
      </div>
      <div class="card-pill">16 MBConv Residual Blocks (SE) &bull; 5.3M Parameters</div>
    </div>
    <div class="card-body">
      <ul class="meta-list" style="margin-bottom: 12px;">
        <li><div class="meta-bullet" style="background: #34d399; box-shadow: 0 0 8px #34d399;"></div><strong>16 MBConv Residual Blocks (SE):</strong>&nbsp;Inverted bottleneck with Squeeze-and-Excitation attention</li>
        <li><div class="meta-bullet" style="background: #34d399; box-shadow: 0 0 8px #34d399;"></div><strong>Swish Non-Linear Activations:</strong>&nbsp;<span class="spec-tag" style="color: #34d399;">f(x) = x &bull; &sigma;(x)</span> preserves smooth derivative gradients</li>
        <li><div class="meta-bullet" style="background: #34d399; box-shadow: 0 0 8px #34d399;"></div><strong>Compound Scaled (5.3M Parameters):</strong>&nbsp;Balanced depth, width, and input resolution</li>
      </ul>

      <div class="backbone-grid">
        <div class="stage-card">
          <div class="st-name">Stage 1</div>
          <div class="st-block">Stem 3&times;3</div>
          <div class="st-res">224&times;224</div>
        </div>
        <div class="stage-card">
          <div class="st-name">Stage 2</div>
          <div class="st-block">MBConv1</div>
          <div class="st-res">112&times;112</div>
        </div>
        <div class="stage-card">
          <div class="st-name">Stage 3</div>
          <div class="st-block">2&times; MBConv6</div>
          <div class="st-res">56&times;56</div>
        </div>
        <div class="stage-card">
          <div class="st-name">Stage 4</div>
          <div class="st-block">2&times; MBConv6</div>
          <div class="st-res">28&times;28</div>
        </div>
        <div class="stage-card">
          <div class="st-name">Stage 5</div>
          <div class="st-block">3&times; MBConv6</div>
          <div class="st-res">14&times;14</div>
        </div>
        <div class="stage-card">
          <div class="st-name">Stage 6</div>
          <div class="st-block">3&times; MBConv6</div>
          <div class="st-res">14&times;14</div>
        </div>
        <div class="stage-card" style="border-color: rgba(56, 189, 248, 0.5); background: rgba(14, 165, 233, 0.1);">
          <div class="st-name" style="color: #38bdf8;">top_conv</div>
          <div class="st-block">1&times;1 Conv</div>
          <div class="st-res" style="color: #38bdf8; font-weight:700;">7&times;7&times;1280</div>
        </div>
      </div>
    </div>
  </div>

  <!-- Split Junction Point -->
  <div class="bifurcation-wrapper">
    <div class="connector-v" style="height: 30px;">
      <div class="connector-line"></div>
    </div>

    <div class="split-badge">
      <div class="split-badge-inner">
        <span style="color: #38bdf8;">Feature Map A^k:</span>
        <span style="color: #fbbf24; font-weight: 800;">(7 &times; 7 &times; 1280)</span>
        <span style="color: #94a3b8;">at layer 'top_conv'</span>
      </div>
    </div>

    <div class="split-junction"></div>

    <!-- Dual Stream Branches -->
    <div class="bifurcation-branches">

      <!-- LEFT BRANCH: Forward Inference -->
      <div class="branch-col">
        <div class="branch-tag tag-forward">
          <span style="font-size: 16px;">&darr;</span>
          (Forward Inference Stream)
        </div>

        <!-- GAP & Dense Card -->
        <div class="card" style="border-color: rgba(16, 185, 129, 0.3);">
          <div class="card-header">
            <div class="card-title">
              <div class="icon-box icon-emerald">4A</div>
              Feature Pooling & Classification Head
            </div>
            <div class="card-pill" style="color: #34d399; border-color: rgba(16, 185, 129, 0.3); background: rgba(16, 185, 129, 0.1);">
              Latent Vector: (1, 1280)
            </div>
          </div>
          <div class="card-body">
            <ul class="meta-list">
              <li><div class="meta-bullet" style="background: #34d399;"></div><strong>GlobalAveragePooling2D:</strong>&nbsp;Collapses spatial 7&times;7 &rarr; 1&times;1 vector across 1,280 channels</li>
              <li><div class="meta-bullet" style="background: #34d399;"></div><strong>Batch Normalization:</strong>&nbsp;Stabilizes internal covariate shift with batch statistics</li>
              <li><div class="meta-bullet" style="background: #34d399;"></div><strong>Dense(256, ReLU, L2):</strong>&nbsp;Fully-connected layer with L2 regularization (&lambda; = 1e-4)</li>
              <li><div class="meta-bullet" style="background: #34d399;"></div><strong>Dropout(Rate = 0.40):</strong>&nbsp;Regularization preventing co-adaptation of neurons</li>
            </ul>
          </div>
        </div>

        <div class="connector-v" style="height: 30px;">
          <div class="connector-line" style="background: #10b981;"></div>
          <div class="connector-arrow" style="border-top-color: #10b981;"></div>
        </div>

        <!-- Softmax Classifier Card -->
        <div class="card" style="border-color: rgba(16, 185, 129, 0.3);">
          <div class="card-header">
            <div class="card-title">
              <div class="icon-box icon-emerald">5A</div>
              Softmax Classifier
            </div>
            <div class="card-pill" style="color: #34d399; border-color: rgba(16, 185, 129, 0.3); background: rgba(16, 185, 129, 0.1);">
              [Glioma | Meningioma | Pituitary | Normal]
            </div>
          </div>
          <div class="card-body">
            <div style="font-size: 13px; color: #94a3b8; margin-bottom: 8px;">
              Multi-class softmax probability distribution: <span class="spec-tag" style="color: #34d399;">&ycirc;_c = exp(z_c) / &Sigma; exp(z_j)</span>
            </div>

            <div class="prob-bars">
              <!-- Glioma -->
              <div class="prob-row">
                <div class="prob-info">
                  <span style="color: #f87171; font-weight: 700;">Glioma (Predicted Pathology &bull; High Risk)</span>
                  <span style="color: #f87171; font-family: 'JetBrains Mono'; font-weight: 800;">95.8%</span>
                </div>
                <div class="prob-bar-bg"><div class="prob-bar-fill fill-glioma"></div></div>
              </div>
              <!-- Meningioma -->
              <div class="prob-row">
                <div class="prob-info">
                  <span style="color: #cbd5e1;">Meningioma</span>
                  <span style="color: #94a3b8; font-family: 'JetBrains Mono';">2.4%</span>
                </div>
                <div class="prob-bar-bg"><div class="prob-bar-fill fill-meningioma"></div></div>
              </div>
              <!-- Pituitary -->
              <div class="prob-row">
                <div class="prob-info">
                  <span style="color: #cbd5e1;">Pituitary</span>
                  <span style="color: #94a3b8; font-family: 'JetBrains Mono';">1.2%</span>
                </div>
                <div class="prob-bar-bg"><div class="prob-bar-fill fill-pituitary"></div></div>
              </div>
              <!-- Normal -->
              <div class="prob-row">
                <div class="prob-info">
                  <span style="color: #cbd5e1;">Normal (No Tumor)</span>
                  <span style="color: #94a3b8; font-family: 'JetBrains Mono';">0.6%</span>
                </div>
                <div class="prob-bar-bg"><div class="prob-bar-fill fill-normal"></div></div>
              </div>
            </div>

            <div style="margin-top: 14px; padding: 10px; background: rgba(239, 68, 68, 0.1); border: 1px solid rgba(239, 68, 68, 0.25); border-radius: 8px; font-size: 12px; color: #fca5a5;">
              <strong>Diagnostic Verdict:</strong> Confirmed Glioma Tumor with 95.8% classification confidence score.
            </div>
          </div>
        </div>

      </div>

      <!-- RIGHT BRANCH: Backprop Gradient Tape (Grad-CAM) -->
      <div class="branch-col">
        <div class="branch-tag tag-backprop">
          <span style="font-size: 16px;">&darr;</span>
          (Backprop Gradient Tape)
        </div>

        <!-- Grad-CAM Gradient Tape Card -->
        <div class="card" style="border-color: rgba(245, 158, 11, 0.3);">
          <div class="card-header">
            <div class="card-title">
              <div class="icon-box icon-amber">4B</div>
              Grad-CAM Gradient Tape
            </div>
            <div class="card-pill" style="color: #fbbf24; border-color: rgba(245, 158, 11, 0.3); background: rgba(245, 158, 11, 0.1);">
              &part;y^c / &part;A^k (top_conv)
            </div>
          </div>
          <div class="card-body">
            <ul class="meta-list">
              <li><div class="meta-bullet" style="background: #fbbf24;"></div><strong>Gradient Tape Target Layer:</strong>&nbsp;<span class="spec-tag" style="color: #fbbf24;">top_conv (7 &times; 7 &times; 1280)</span></li>
              <li><div class="meta-bullet" style="background: #fbbf24;"></div><strong>Neuron Importance &alpha;_k:</strong>&nbsp;Global spatial pooling over receptive field:</li>
            </ul>

            <div class="math-block">
              <span class="math-highlight">&alpha;_k</span> = (1 / Z) &Sigma;<sub>i</sub> &Sigma;<sub>j</sub> (&part;y^c / &part;A<sub>i,j</sub>^k)<br/>
              <span class="math-highlight">L_GradCAM</span> = ReLU( &Sigma;<sub>k</sub> &alpha;_k &bull; A^k )
            </div>
            
            <div style="margin-top: 8px; font-size: 12px; color: #94a3b8;">
              Rectified Linear Unit (ReLU) ensures only features with positive attribution to the predicted tumor class are visualized.
            </div>
          </div>
        </div>

        <div class="connector-v" style="height: 30px;">
          <div class="connector-line" style="background: #f59e0b;"></div>
          <div class="connector-arrow" style="border-top-color: #f59e0b;"></div>
        </div>

        <!-- Saliency Jet Heatmap Card -->
        <div class="card" style="border-color: rgba(245, 158, 11, 0.3);">
          <div class="card-header">
            <div class="card-title">
              <div class="icon-box icon-amber">5B</div>
              Saliency Jet Heatmap & Superimposed Blend
            </div>
            <div class="card-pill" style="color: #fbbf24; border-color: rgba(245, 158, 11, 0.3); background: rgba(245, 158, 11, 0.1);">
              Blend Ratio: 0.45
            </div>
          </div>
          <div class="card-body">
            <div class="mri-compare-row" style="margin-bottom: 12px;">
              <div class="mri-frame" style="width: 140px; border-color: rgba(245, 158, 11, 0.4);">
                <img src="{jet_b64}" alt="Jet Heatmap" style="width: 120px; height: 120px;" />
                <div class="mri-label" style="color: #fbbf24; font-size: 10px;">Saliency Jet Heatmap</div>
              </div>
              <div style="font-size: 18px; color: #fbbf24; font-weight: 700;">+</div>
              <div class="mri-frame" style="width: 140px;">
                <img src="{clahe_mri_b64}" alt="MRI Base" style="width: 120px; height: 120px;" />
                <div class="mri-label" style="font-size: 10px;">Axial Scan (0.55)</div>
              </div>
              <div style="font-size: 18px; color: #fbbf24; font-weight: 700;">=</div>
              <div class="mri-frame" style="width: 140px; border-color: rgba(56, 189, 248, 0.5); box-shadow: 0 0 15px rgba(56, 189, 248, 0.2);">
                <img src="{overlay_b64}" alt="Superimposed Overlay" style="width: 120px; height: 120px;" />
                <div class="mri-label" style="color: #38bdf8; font-size: 10px;">Superimposed (0.45)</div>
              </div>
            </div>

            <ul class="meta-list">
              <li><div class="meta-bullet" style="background: #fbbf24;"></div><strong>Bilinear Upsample 224&times;224:</strong>&nbsp;Interpolates coarse 7&times;7 activation map to image dimensions</li>
              <li><div class="meta-bullet" style="background: #fbbf24;"></div><strong>Saliency Jet Heatmap:</strong>&nbsp;Cold blue background to intense hot red neoplastic center</li>
              <li><div class="meta-bullet" style="background: #fbbf24;"></div><strong>Superimposed Blend (0.45):</strong>&nbsp;<span class="spec-tag" style="color: #fbbf24;">I_overlay = 0.55 &bull; I_orig + 0.45 &bull; H_jet</span></li>
            </ul>
          </div>
        </div>

      </div>

    </div>

    <!-- Bottom Junction -->
    <div class="engine-junction"></div>
    <div class="connector-v" style="height: 30px;">
      <div class="connector-line"></div>
      <div class="connector-arrow"></div>
    </div>

  </div>

  <!-- Stage 6: Flask 3.x Clinical Inference Engine -->
  <div class="card engine-card">
    <div class="card-header" style="background: linear-gradient(90deg, rgba(99, 102, 241, 0.15) 0%, rgba(14, 165, 233, 0.15) 100%);">
      <div class="card-title">
        <div class="icon-box" style="background: rgba(99, 102, 241, 0.2); color: #818cf8; border: 1px solid rgba(99, 102, 241, 0.4);">
          6
        </div>
        Flask 3.x Clinical Inference Engine
      </div>
      <div style="display: flex; gap: 8px;">
        <span class="card-pill" style="color: #818cf8; border-color: rgba(99, 102, 241, 0.3); background: rgba(99, 102, 241, 0.1);">WSGI Application Server</span>
        <span class="card-pill">REST API Endpoint: /predict</span>
      </div>
    </div>
    <div class="engine-grid">

      <!-- SQLite 3 Patient Registry -->
      <div class="sub-engine">
        <div class="sub-engine-header">
          <div class="sub-engine-title">
            <span style="font-size: 20px;">🗄️</span>
            SQLite 3 Patient Registry
          </div>
          <span class="badge-tag badge-sqlite">ACID Compliant</span>
        </div>
        <ul class="meta-list">
          <li><div class="meta-bullet" style="background: #38bdf8;"></div><strong>Indexed Longitudinal History:</strong>&nbsp;Persistent audit tracking with UUIDs and timestamped records</li>
          <li><div class="meta-bullet" style="background: #38bdf8;"></div><strong>Case Search & Class Filter:</strong>&nbsp;Fast SQL queries filtering by Glioma, Meningioma, Pituitary, Normal</li>
          <li><div class="meta-bullet" style="background: #38bdf8;"></div><strong>EMR Persistence Layer:</strong>&nbsp;Stores scan path, overlay reference, confidence, and physician notes</li>
        </ul>
        <div class="preview-box">
          <img src="{hist_preview_b64}" alt="SQLite Patient Registry Table" />
        </div>
      </div>

      <!-- ReportLab Vector PDF Engine -->
      <div class="sub-engine">
        <div class="sub-engine-header">
          <div class="sub-engine-title">
            <span style="font-size: 20px;">📑</span>
            ReportLab Vector PDF Engine
          </div>
          <span class="badge-tag badge-pdf">Medical Grade PDF</span>
        </div>
        <ul class="meta-list">
          <li><div class="meta-bullet" style="background: #f87171;"></div><strong>Dual-Image Radiology Layout:</strong>&nbsp;Side-by-side rendering of original MRI & Grad-CAM heatmap</li>
          <li><div class="meta-bullet" style="background: #f87171;"></div><strong>Clinical Recommendations & XAI:</strong>&nbsp;Automated oncological triage and certified sign-off</li>
          <li><div class="meta-bullet" style="background: #f87171;"></div><strong>Vector Typography:</strong>&nbsp;Resolution-independent clinical dossier export in under 80 milliseconds</li>
        </ul>
        <div class="preview-box">
          <img src="{pdf_preview_b64}" alt="ReportLab PDF Report Dossier" />
        </div>
      </div>

    </div>
  </div>

  <!-- Footer bar -->
  <div class="footer-bar">
    <div class="brand">
      <span style="color: #38bdf8; font-size: 16px;">⚡</span>
      NeuroVision AI &bull; IBM SkillsBuild &bull; AICTE BharatCares
    </div>
    <div style="font-family: 'JetBrains Mono', monospace; font-size: 12px; color: #64748b;">
      End-to-End Pipeline Latency: &lt; 142ms &bull; Model Parameters: 5,288,548 &bull; Test Accuracy: 98.7%
    </div>
  </div>

</div>

</body>
</html>
"""

with open("scratch/architecture_canvas.html", "w") as f:
    f.write(html_content)

print("scratch/architecture_canvas.html re-rendered successfully!")
