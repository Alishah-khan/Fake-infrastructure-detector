# InfraAudit

### National Verification Portal for Publicly Funded Infrastructure

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://fake-infrastructure-detector.streamlit.app)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## Purpose

Public money is sanctioned for roads, schools, hospitals and bridges that are certified complete on
paper long before — and sometimes without ever — being built. InfraAudit verifies those claims
independently: it compares temporal satellite imagery of the sanctioned site, measures the change in
built-up footprint with computer vision, and releases a verdict into a public ledger that citizens,
auditors and executing agencies all see.

Payment for a milestone is cleared only when three independent sources agree — the contractor's own
declaration, the satellite audit, and citizen oversight.

---

## Portals

The platform is not a single dashboard. Each stakeholder group enters through its own route.

| Portal | Access | Capabilities |
|--------|--------|--------------|
| **Government Vigilance Portal** | Protected sign-in (MoSPI / CAG / state vigilance) | Three-way payment gatekeeper, satellite verification engine, Contractor Credibility Index, investigation dossier export |
| **Contractor Execution Portal** | Protected sign-in (registered executing agencies) | Milestone claims with GST invoices, weekly geotagged progress, five-year defect liability bond registration |
| **Public Citizen Portal** | Open, no registration | Anonymous ghost-asset reporting, five-year defect liability claims, public surveillance ledger with satellite evidence |
| **MP Allocation Directory** | Open, no registration | Searchable register of MPLADS allocations for all 543 Lok Sabha constituencies |

Demonstration credentials for the two protected portals are shown on their sign-in screens. They are
prototype accounts defined in `app_auth.py` and must be replaced by the department's identity
provider before any real deployment.

---

## Data

**MPLADS allocation register** — `data/mplads_543_mps.json` holds all 543 Lok Sabha constituencies
with the sitting member, constituency, state and allocated amount, parsed from the official
allocated-limit publication (₹8,318.06 crore in total). One source row carries no published amount
and is stored as `null` rather than being estimated. Rebuild the file with:

```bash
python scripts/build_mplads_dataset.py "Allocated Limit for Honble MPs.pdf"
```

**Case studies** — a small set of publicly reported execution failures (Biju Setu Jajpur, Biju Setu
Ganjam, Kiratpur–Manali NH-21, Banjar hospital expansion, Brazloo bridge Kulgam) is seeded into the
ledger to illustrate the delay patterns the platform detects. Coordinates are district-level
approximations; every entry carries its published source.

---

## Project structure

```
Fake-infrastructure-detector/
├── src/
│   ├── member1_fetcher.py     # Geocoding and temporal satellite acquisition
│   ├── member2_detector.py    # Footprint detection, change metrics and verdicts
│   └── member3_dashboard.py   # Government design system and page components
├── scripts/
│   └── build_mplads_dataset.py  # Parses the official allocation PDF
├── data/
│   ├── mplads_543_mps.json    # Constituency allocation register
│   ├── samples/               # Demonstration satellite image pairs
│   └── projects.db            # SQLite ledger (generated)
├── app_integrated.py          # Portal application and navigation
├── app_auth.py                # Role authentication for protected portals
├── integration.py             # Ledger, allocation queries, claims, dossier exporter
└── test_integration.py        # Automated test suite
```

---

## Getting started

```bash
git clone https://github.com/Alishah-khan/Fake-infrastructure-detector.git
cd Fake-infrastructure-detector
python3 -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
streamlit run app_integrated.py
```

The portal opens at `http://localhost:8501`.

Optional Sentinel Hub credentials can be placed in a `.env` file:

```env
SENTINEL_CLIENT_ID=your-client-id
SENTINEL_CLIENT_SECRET=your-client-secret
```

---

## Testing

```bash
python test_integration.py
```

The suite covers sample generation, geocoding, the detection engine on verified and ghost assets,
the ledger and dossier exporter, the 543-constituency allocation register and its search, case study
seeding, role permissions, the payment gatekeeper and citizen submissions.

---

## Sample verification scenarios

| Sanction | Location | Outlay | Expected verdict |
|----------|----------|--------|------------------|
| Primary Model School | Varanasi, UP | ₹1.45 Cr | Confirmed — new building, +29.3% built-up area |
| Bitumen Link Road 12B | Jabalpur, MP | ₹3.20 Cr | Flagged — no change, unpaved track |
| Rural Health Center | Ratnagiri, MH | ₹2.80 Cr | Flagged — no change, vacant farmland |
| Brahmani River Bridge | Dhenkanal, OD | ₹5.20 Cr | Confirmed — concrete deck span |

---

## Technology

Streamlit, Streamlit-Folium and Plotly for the interface; OpenCV, NumPy and Pillow for the detection
engine; Esri World Imagery and Nominatim for earth observation and geocoding; SQLite for the ledger.

---

## Roadmap

- [x] Separate vigilance, contractor and citizen portals
- [x] Three-way payment gatekeeper
- [x] Constituency allocation register for all 543 seats
- [ ] Live Sentinel-2 alert pipeline
- [ ] Integration with PM Gati Shakti and state PWD portals
- [ ] Citizen mobile application for crowdsourced geotagging

---

## License

MIT — see [LICENSE](LICENSE).

This deployment is a demonstration prototype.
