# Real-Time Solar Flare Detection and Prediction Platform Driven by Aditya-L1 X-ray Observations

A complete, low-latency space-weather monitoring and prediction workflow built around raw X-ray measurements from ISRO's **Aditya-L1** observatory. It combines causal fusion of multiple instruments, live flare detection, machine-learning-based early warning, and an operator-focused Streamlit control panel.

Developed by team **SolarSentinels** (Adamas University, Kolkata) for the ISRO Aditya-L1 Hackathon.

---

## 🌌 Background and Purpose

Solar eruptions — especially flares — can disrupt satellites, degrade high-frequency radio links, and stress power networks on the ground. Conventional prediction practices often depend on delayed manual review by specialists, leaving response gaps of roughly 15–30 minutes.

This workflow closes that operational gap through a fast, automated chain that:
1. **Combines and aligns** raw soft X-ray (SXR) readings from **SoLEXS** with hard X-ray (HXR) readings from **HEL1OS**.
2. **Spots** ongoing flares immediately using a causal, rolling-baseline detector.
3. **Anticipates** flare activity up to 30 minutes ahead with a physics-guided RandomForest model.
4. **Presents** streaming telemetry, alert states (🟢 LOW, 🟡 MEDIUM, 🔴 HIGH), and probability-based risk scores in one operations view.

---

## 🛠️ Core Scientific and Engineering Contributions

### 1. Real-Time Causal Baseline Detector
Many published detection approaches use centered smoothing (for example Gaussian or Savitzky-Golay filters) that look at future samples ($t + \Delta t$), so they cannot run on live telemetry. This project instead uses a **strictly history-only rolling baseline** (past samples only), preserving live-stream compatibility. Validated against the official NOAA GOES-16/18 flare catalogue, the detector recovers **93.2%** of events (68 of 73 flares).

### 2. Direct Fusion of Raw Instrument Streams
Unprocessed high-rate series from SoLEXS (1-second sampling) and HEL1OS (adaptive time-binning) are synchronized across shared observing intervals, covering more than 259,000 coincident timestamps. From this alignment the live **Spectral Hardness Ratio** ($COUNTS_{HEL1OS} / COUNTS_{SoLEXS}$) is derived.

### 3. Feature Design Grounded in Flare Physics
The learning model uses indicators tied to observed flare behaviour:
* **Gradual pre-flare brightening**: windowed averages and upward trends over 10-minute spans capture slow coronal heating ahead of the impulsive burst.
* **Quasi-Periodic Pulsations (QPPs)**: windowed variability captures rapid oscillations linked to MHD waves and reconnection in coronal loops.
* **Neupert-effect signature**: the hardness ratio plus cross-instrument Z-scores follow the fast shift from thermal heating to non-thermal particle acceleration.

### 4. Honest, Leakage-Aware Evaluation
For scientific and operational transparency, forecasting skill is reported under two protocols:
* **Random stratified split**: an optimistic **ROC-AUC of 0.894** with **16.51 minutes** mean lead time. Overlapping sliding windows can appear in both train and test here (temporal leakage).
* **Chronological 80/20 split**: a strict history-versus-future separation with no temporal leakage. On the exploratory 6-day sample (16 confirmed flares, 14,139 windows), this gives a conservative **ROC-AUC of ~0.533** and **~4.57 minutes** mean lead time. These careful figures form the scientific baseline and motivate a larger data-volume roadmap.

---

## 📊 Measured Performance

| Metric | Value | Measurement Setting |
|---|---|---|
| **Nowcasting Recall (NOAA GOES)** | **93.2%** | 68 / 73 GOES-listed flares recovered (only 5 weak C-class missed) |
| **Nowcasting Precision** | **35.8%** | 76 / 212 merged events match GOES; remaining 136 represent real sub-threshold microflares |
| **Forecasting ROC-AUC (Random Split)** | **0.894** | Inflated by temporal leakage (used for literature comparison) |
| **Forecasting ROC-AUC (Chronological)** | **~0.533** | Strict, leakage-free holdout (Phase-1 honest baseline) |
| **Average Lead Time (Random Split)** | **16.51 min** | Average warning time before flare peak |
| **Average Lead Time (Chronological)** | **~4.57 min** | Average warning time under strict chronological evaluation |
| **Inference Latency** | **< 1 ms** | Per window on commodity hardware (highly scalable) |

---

## 📂 Repository Structure

```
PS15_SolarFlare/
├── Solar Low Energy X-ray Spectrometer/     # SoLEXS-specific pipeline files
│   ├── data/                                # Raw SoLEXS zip files (ignored in Git)
│   ├── output/                              # Processed SoLEXS time series & nowcast catalogs
│   └── scripts/                             # Ingestion, nowcasting, and validation scripts
├── High Energy L1 Orbiting X-ray Spectrometer/ # HEL1OS-specific pipeline files
│   ├── data/                                # Raw HEL1OS fits files (ignored in Git)
│   ├── output/                              # Processed HEL1OS time series & nowcast catalogs
│   └── scripts/                             # Ingestion, nowcasting, and tuning scripts
├── scripts/                                 # Shared forecasting and evaluation scripts
│   ├── train_forecast_sklearn.py            # Trains single-instrument RandomForest
│   ├── train_forecast_dual_fusion.py        # Trains dual-instrument fusion model
│   ├── merge_catalogs.py                    # Integrates SoLEXS & HEL1OS nowcast catalogs
│   └── [helper scripts]                     # Statistical checks, false alarm analysis, etc.
├── output/                                  # Shared outputs, trained models, and results
│   ├── forecast_model_rf.joblib             # Trained single-instrument model
│   ├── forecast_model_rf_fusion.joblib      # Trained dual-instrument fusion model
│   ├── forecast_results_rf.csv              # Predictions & probabilities (single)
│   └── forecast_results_rf_fusion.csv       # Predictions & probabilities (fusion)
├── dashboard.py                             # Interactive Streamlit operator dashboard
├── run_full_pipeline.ps1                    # PowerShell wrapper to execute full pipeline
├── requirements.txt                         # Python package dependencies
└── README.md                                # This documentation
```

---

## 📊 Datasets & Data Sharing

To facilitate collaboration and reproducibility, the datasets are packaged and can be hosted on external platforms (due to GitHub's file size limits for the ~900MB raw telemetry files).

See the comprehensive [SHARE_DATASET.md](SHARE_DATASET.md) guide for detailed instructions on hosting, uploading, and downloading the datasets.

* **Hugging Face Hub Dataset**: `https://huggingface.co/datasets/YOUR_USERNAME/aditya-l1-solar-flare` *(Placeholder - update after uploading)*
* **Google Drive Link (Full Zip)**: `https://drive.google.com/open?id=YOUR_FILE_ID` *(Placeholder - update after uploading)*

By downloading the pre-processed ML-ready files directly into the `output/` directory, users can bypass raw data ingestion and train the forecasting models immediately.

---

## 🚀 Getting Started

### Prerequisites
* Python 3.9+
* PowerShell (for running the pipeline wrapper) or Git Bash

### 1. Installation
Clone the repository and set up a virtual environment:
```bash
# Clone the repository
git clone https://github.com/deepshekhar555/PS15_SolarFlare.git
cd PS15_SolarFlare

# Create and activate a virtual environment
python -m venv .venv
# On Windows PowerShell:
& .\.venv\Scripts\Activate.ps1
# On macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Run the Ingestion & Training Pipeline
To run the full pipeline (combining raw FITS/Zip files, running nowcasting, labeling flares, and training both the single-instrument and dual-instrument forecasting models):
```powershell
& .\run_full_pipeline.ps1
```
*Note: Raw data files are expected to be in the respective instrument `data/` subdirectories. If you have PRADAN download URLs, place them in `pradan_urls.txt` and export your `PRADAN_COOKIE` before running.*

### 3. Launch the Operator Dashboard
Start the interactive dashboard to visualize the telemetry and model predictions:
```bash
streamlit run dashboard.py
```
The dashboard will automatically open in your browser (defaulting to `http://localhost:8501`).

---

## 📈 Planned Next Phase

The Phase-1 build shows a complete working chain from raw telemetry to live alerts. To mature it toward operations-grade use, the planned next steps are:
1. **Broader archive coverage**: process the extended multi-month Aditya-L1 record from PRADAN to grow training coverage beyond 100 confirmed flares, stabilize the RandomForest, and support sequence models (such as LSTMs or Transformers).
2. **Pointing-aware correction**: use spacecraft roll, pitch, and yaw information to adjust count rates for collimator-area changes during off-pointing intervals.
3. **Flux-level calibration**: apply spectral deconvolution with Detector Response Matrices (DRMs) to translate raw counts into physical flux ($W/m^2$ or $photons/cm^2/s/keV$).
4. **Image-aware context**: add spatial context from Aditya-L1 **SUIT** (Solar Ultraviolet Imaging Telescope) to disambiguate among active regions.

---

## 👥 Team & Contact

* **Team Name**: SuryaDrishti (formerly SolarSentinels)
* **Institutional Affiliation**: Adamas University, Kolkata
* **Team Members**:
  * **Deep Shekhar Halder** (Team Lead & Tech Lead) - `deephalder209@gmail.com`
  * **Rituraj Saha** (Feature Engineering & Visualization) - `saharituraj805@gmail.com`
  * **Mahalaxmi Macha** (Data & Validation) - `mahalaxmimacha14@gmail.com`
  * **Ashfaque Ahamed Khan** (Dashboard & Benchmarking) - `ashfaqueahamedkhan591@gmail.com`
