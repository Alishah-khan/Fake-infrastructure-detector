# 🏗️ Fake Infrastructure Detector

### *AI-Powered Satellite Verification for Government Projects*

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://fake-infrastructure-detector.streamlit.app)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![SIH 2026](https://img.shields.io/badge/SIH-2026-orange.svg)](https://www.sih.gov.in/)

---

## 📌 Problem Statement

**The Challenge:** Government spends billions on infrastructure projects (roads, schools, hospitals, wells) in rural areas. However, many projects are shown as "completed" on paper but are never actually built. Citizens have no easy way to verify if these projects exist.

**Our Solution:** A web-based tool that uses satellite imagery and Artificial Intelligence to automatically verify infrastructure projects by comparing before/after satellite images and flagging suspicious projects for investigation.

**Impact:** Saves taxpayer money, enables citizen oversight, helps audit teams work efficiently, and promotes transparent governance.

---

## 🎯 Key Features

| Feature | Description |
|---------|-------------|
| 🔍 **Project Verification** | Enter project details and get AI-powered verification |
| 🛰️ **Satellite Image Analysis** | Fetches real satellite images from Sentinel Hub & Esri Earth Observation |
| 🤖 **AI Infrastructure Detection** | Detects buildings, roads, bridges using computer vision & footprint segmentation |
| 📊 **Audit Dashboard** | View statistics, flagged projects, and financial analysis charts |
| 📥 **Report Generation** | Export detailed audit reports in JSON/Markdown |
| 🗺️ **Interactive Maps** | Visualize project locations on Folium satellite maps |
| ⚡ **Demo Mode** | Quick test with pre-loaded verified and suspicious projects |
| 🌐 **Dynamic Surveillance Grid** | Responsive visual feed for live civic audits |

---

## 🏗️ System Architecture

```
┌────────────────────────────────────────────────────────┐
│               Streamlit Web Interface                  │
│  - Project Input & Geocoding Search                   │
│  - Interactive Folium Map                              │
│  - Before vs. After Visual Comparison                  │
│  - AI Detection Overlays & Metrics Dashboard          │
│  - Audit Dossier & Flagged Projects Registry          │
└──────────────────────────┬─────────────────────────────┘
                           │
         ┌─────────────────┴─────────────────┐
         ▼                                   ▼
┌──────────────────────────┐       ┌──────────────────────────┐
│ Satellite Fetcher Service│       │ AI & Vision Detection    │
│ - Sentinel-2 / Map tiles │       │ - Structural detection   │
│ - Geocoding (Nominatim)  │       │ - Building footprint AI  │
│ - Curated Demo Cache     │       │ - Change index & verdict │
└────────┬─────────────────┘       └────────┬─────────────────┘
         │                                   │
         └─────────────────┬─────────────────┘
                           ▼
┌────────────────────────────────────────────────────────┐
│                Database & Audit Store                  │
│ - SQLite/JSON Project Records                          │
│ - Flagged Projects Tracker & Exportable Reports        │
└────────────────────────────────────────────────────────┘
```

---

## 📁 Project Structure

```
Fake-infrastructure-detector/
│
├── 📁 src/
│   ├── member1_fetcher.py     # Satellite image fetcher & geocoding
│   ├── member2_detector.py    # AI detection & change analysis engine
│   └── member3_dashboard.py   # Modern UI components & styling
│
├── 📁 data/
│   ├── cache/                 # Local image cache
│   ├── samples/               # Pre-loaded demo satellite image pairs
│   └── projects.db            # SQLite audit database
│
├── 📄 app_integrated.py       # Main Streamlit dashboard (Surveillance Feed)
├── 📄 integration.py          # Database operations & dossier exporter
├── 📄 test_integration.py     # Automated testing pipeline
├── 📄 requirements.txt        # Python dependencies
├── 📄 README.md               # Complete Project Documentation
└── 📄 LICENSE                 # MIT License
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- Git (for cloning)
- VS Code (recommended) or any Python IDE

### Installation

**1. Clone the repository**
```bash
git clone https://github.com/Alishah-khan/Fake-infrastructure-detector.git
cd Fake-infrastructure-detector
```

**2. Create virtual environment**
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Set up API keys** (Optional - for custom Sentinel Hub access)

Create a `.env` file in the root directory:
```env
SENTINEL_CLIENT_ID=your-client-id
SENTINEL_CLIENT_SECRET=your-client-secret
ROBOFLOW_API_KEY=your-roboflow-key
```

### Running the Application

```bash
streamlit run app_integrated.py
```

The application will open in your browser at `http://localhost:8501`

---

## 🧪 Testing

### Run Integration Tests
```bash
python test_integration.py
```

### Manual Testing Checklist
- [x] Dashboard opens successfully
- [x] Can enter project details & geocode locations
- [x] Satellite images fetch (or use demo samples)
- [x] AI detection runs & generates change heatmaps
- [x] Verdict displays correctly (Verified / Suspicious / In Progress)
- [x] Downloadable official audit dossier (.md)
- [x] Audit dashboard shows statistics & risk charts

---

## 🖥️ Demo Walkthrough

### 1. Verify a Project
1. Open the app: `streamlit run app_integrated.py`
2. Go to **"🔍 Verify New Project"** tab
3. Select a preset (e.g. **Verified School** or **Ghost Road**)
4. Click **"Run Satellite AI Verification"**
5. View before/after satellite images & AI bounding box overlays
6. See the verdict badge & download the investigation dossier

### 2. Sample Scenarios

| Scenario | Location | Budget | Expected Result |
|----------|----------|--------|-----------------|
| **Primary Model School** | Varanasi, UP | ₹1.45 Cr | ✅ VERIFIED - New building (+29.3% built area) |
| **Bitumen Link Road 12B** | Jabalpur, MP | ₹3.20 Cr | 🔴 SUSPICIOUS - 0% change, unpaved dirt path |
| **Rural Health Center** | Ratnagiri, MH | ₹2.80 Cr | 🔴 SUSPICIOUS - 0% change, vacant farmland |
| **Brahmani River Bridge** | Dhenkanal, OD | ₹5.20 Cr | ✅ VERIFIED - Concrete deck span (+5.7% built area) |

### 3. Audit Analytics Dashboard
- View total projects audited
- Track flagged ghost fraud funds (₹6.00+ Crore)
- Analyze department-level expenditure vs. fraud risk

---

## 👥 Team Members

| Member | Role | Responsibilities | Module |
|--------|------|------------------|--------|
| **Saba Qadeer** | Satellite Image Fetcher | Sentinel API integration, geocoding & tile caching | `src/member1_fetcher.py` |
| **Shifa Maheen** | AI Detection Engineer | Computer vision, structural footprint & change heatmaps | `src/member2_detector.py` |
| **Saniya Khatoon** | UI/UX Developer | Dynamic surveillance dashboard, maps & visualizations | `src/member3_dashboard.py` |
| **Alishah Khan** | Integration Lead | SQLite database ledger, dossier generator & presentation | `integration.py` |

---

## 🔧 Technologies Used

| Component | Technology |
|-----------|------------|
| **Frontend** | Streamlit, Streamlit-Folium, Plotly, HTML5/CSS3 |
| **Backend** | Python 3.8+ |
| **Satellite Imagery** | Esri World Imagery, OpenStreetMap (Nominatim), Sentinel Hub |
| **Computer Vision / AI** | OpenCV, NumPy, Pillow, Scikit-Image |
| **Database** | SQLite3 |
| **Testing** | Python Test Suite |
| **Version Control** | Git, GitHub |
| **Deployment** | Streamlit Community Cloud |

---

## 📊 Sample Outputs

### Verified Project ✅
```
📊 Analysis Results
┌─────────────────────────┬──────────────┐
│ Metric                  │ Value        │
├─────────────────────────┼──────────────┤
│ Pre-Construction Assets │ 0 structures │
│ Post-Completion Assets  │ 1 structure  │
│ Built-Up Footprint Delta│ +29.3%       │
│ AI Confidence           │ 96.8%        │
│ Final Status            │ VERIFIED ✅  │
└─────────────────────────┴──────────────┘
```

### Suspicious Project (Ghost Asset) 🔴
```
📊 Analysis Results
┌─────────────────────────┬──────────────┐
│ Metric                  │ Value        │
├─────────────────────────┼──────────────┤
│ Pre-Construction Assets │ 0 structures │
│ Post-Completion Assets  │ 0 structures │
│ Built-Up Footprint Delta│ +0.0%        │
│ AI Confidence           │ 97.0%        │
│ Capital at Risk         │ ₹3.20 Crore  │
│ Final Status            │ SUSPICIOUS 🔴│
└─────────────────────────┴──────────────┘
```

---

## 🚧 Roadmap

- [x] Streamlit dashboard with dynamic surveillance feed
- [x] Satellite image fetching & geocoding
- [x] AI infrastructure detection & change heatmaps
- [x] SQLite audit ledger & official dossier exporter
- [x] Automated test suite
- [ ] Real-time Sentinel-2 alert pipeline
- [ ] Integration with PM Gati Shakti & State PWD portals
- [ ] Citizen mobile app for crowdsourced geotagging

---

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch: `git checkout -b feature/AmazingFeature`
3. Commit your changes: `git commit -m 'Add some AmazingFeature'`
4. Push to the branch: `git push origin feature/AmazingFeature`
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Copernicus Sentinel Hub & Esri** - Satellite earth observation data
- **Streamlit & OpenCV Community** - Open-source tools
- **All team members** - For their dedication and hard work

---

## ⭐ Star us on GitHub!

If you find this project helpful, please give us a star ⭐ on GitHub: [Alishah-khan/Fake-infrastructure-detector](https://github.com/Alishah-khan/Fake-infrastructure-detector)!
Note: This is only for DEMO purpose.
---


