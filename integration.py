"""
Module: System Integration & Database Ledger

Handles SQLite persistence for the audit ledger, contractor milestone claims,
citizen submissions, the MPLADS constituency allocation register, and the
formal investigation dossiers exported by the vigilance portal.
"""

import json
import sqlite3
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "data" / "projects.db"
MPLADS_PATH = BASE_DIR / "data" / "mplads_543_mps.json"


def get_connection():
    """Returns thread-safe SQLite connection."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initializes the database schema."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS projects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        project_name TEXT NOT NULL,
        department TEXT NOT NULL,
        project_type TEXT NOT NULL,
        location_name TEXT NOT NULL,
        latitude REAL NOT NULL,
        longitude REAL NOT NULL,
        sanctioned_budget REAL NOT NULL,
        start_date TEXT NOT NULL,
        end_date TEXT NOT NULL,
        verdict TEXT NOT NULL,
        confidence_score REAL NOT NULL,
        before_structure_count INTEGER DEFAULT 0,
        after_structure_count INTEGER DEFAULT 0,
        built_area_change_pct REAL DEFAULT 0.0,
        audit_notes TEXT,
        image_before_path TEXT,
        image_after_path TEXT,
        image_annotated_path TEXT,
        heatmap_path TEXT,
        status TEXT DEFAULT 'AUDITED',
        created_at TEXT NOT NULL
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS milestone_claims (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        work_order_id TEXT NOT NULL,
        contractor_name TEXT NOT NULL,
        milestone TEXT NOT NULL,
        claim_amount REAL NOT NULL,
        gst_invoice_no TEXT NOT NULL,
        progress_pct REAL NOT NULL,
        geotag_latitude REAL,
        geotag_longitude REAL,
        dlp_bond_reference TEXT,
        remarks TEXT,
        status TEXT NOT NULL DEFAULT 'PENDING_SATELLITE_AUDIT',
        created_at TEXT NOT NULL
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS whistleblower_reports (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        reference_code TEXT NOT NULL,
        project_reference TEXT NOT NULL,
        location_name TEXT NOT NULL,
        category TEXT NOT NULL,
        description TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'UNDER_REVIEW',
        created_at TEXT NOT NULL
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS warranty_claims (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        reference_code TEXT NOT NULL,
        asset_name TEXT NOT NULL,
        location_name TEXT NOT NULL,
        defect_type TEXT NOT NULL,
        commissioned_on TEXT NOT NULL,
        within_dlp INTEGER NOT NULL,
        description TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'LODGED',
        created_at TEXT NOT NULL
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS case_studies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        location_name TEXT NOT NULL,
        state TEXT NOT NULL,
        asset_type TEXT NOT NULL,
        sanctioned_budget REAL,
        delay_summary TEXT NOT NULL,
        promise_and_delay TEXT NOT NULL,
        human_impact TEXT NOT NULL,
        latitude REAL,
        longitude REAL,
        source TEXT NOT NULL
    )
    """)
    conn.commit()
    conn.close()


def save_project(project_data: dict) -> int:
    """Inserts a verified project record into the audit ledger."""
    conn = get_connection()
    cursor = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
    INSERT INTO projects (
        project_name, department, project_type, location_name,
        latitude, longitude, sanctioned_budget, start_date, end_date,
        verdict, confidence_score, before_structure_count, after_structure_count,
        built_area_change_pct, audit_notes, image_before_path, image_after_path,
        image_annotated_path, heatmap_path, status, created_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        project_data.get("project_name", "Untitled Project"),
        project_data.get("department", "PWD"),
        project_data.get("project_type", "Building"),
        project_data.get("location_name", "Unknown"),
        project_data.get("latitude", 0.0),
        project_data.get("longitude", 0.0),
        project_data.get("sanctioned_budget", 0.0),
        project_data.get("start_date", ""),
        project_data.get("end_date", ""),
        project_data.get("verdict", "SUSPICIOUS"),
        project_data.get("confidence_score", 0.0),
        project_data.get("before_structure_count", 0),
        project_data.get("after_structure_count", 0),
        project_data.get("built_area_change_pct", 0.0),
        project_data.get("audit_notes", ""),
        project_data.get("image_before_path", ""),
        project_data.get("image_after_path", ""),
        project_data.get("image_annotated_path", ""),
        project_data.get("heatmap_path", ""),
        project_data.get("status", "AUDITED"),
        now
    ))
    pid = cursor.lastrowid
    conn.commit()
    conn.close()
    return pid


def get_all_projects():
    """Retrieves all project records."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM projects ORDER BY id DESC")
    rows = cursor.fetchall()
    projects = [dict(row) for row in rows]
    conn.close()
    return projects


def get_flagged_projects():
    """Retrieves projects flagged as suspicious."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM projects WHERE verdict = 'SUSPICIOUS' ORDER BY id DESC")
    rows = cursor.fetchall()
    projects = [dict(row) for row in rows]
    conn.close()
    return projects


def get_audit_statistics():
    """Calculates summary KPIs across all audited projects."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) as total FROM projects")
    total_projects = cursor.fetchone()["total"]

    cursor.execute("SELECT SUM(sanctioned_budget) as total_budget FROM projects")
    total_budget = cursor.fetchone()["total_budget"] or 0.0

    cursor.execute("SELECT COUNT(*) as verified FROM projects WHERE verdict = 'VERIFIED'")
    verified_count = cursor.fetchone()["verified"]

    cursor.execute("SELECT COUNT(*) as suspicious FROM projects WHERE verdict = 'SUSPICIOUS'")
    suspicious_count = cursor.fetchone()["suspicious"]

    cursor.execute("SELECT COUNT(*) as in_progress FROM projects WHERE verdict = 'IN_PROGRESS'")
    in_progress_count = cursor.fetchone()["in_progress"]

    cursor.execute("SELECT SUM(sanctioned_budget) as flagged_budget FROM projects WHERE verdict = 'SUSPICIOUS'")
    flagged_budget = cursor.fetchone()["flagged_budget"] or 0.0

    conn.close()
    fraud_rate = (suspicious_count / total_projects * 100) if total_projects > 0 else 0

    return {
        "total_projects": total_projects,
        "total_budget": total_budget,
        "verified_count": verified_count,
        "suspicious_count": suspicious_count,
        "in_progress_count": in_progress_count,
        "flagged_budget": flagged_budget,
        "fraud_risk_rate": round(fraud_rate, 1)
    }


def seed_sample_projects():
    """Seeds initial demonstration data."""
    init_db()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as cnt FROM projects")
    cnt = cursor.fetchone()["cnt"]

    if cnt == 0:
        samples_dir = BASE_DIR / "data" / "samples"
        samples = [
            {
                "project_name": "Primary Model School Complex",
                "department": "Education & School Infrastructure",
                "project_type": "Building / School",
                "location_name": "Rampur Sector 4, Varanasi, Uttar Pradesh",
                "latitude": 25.3176,
                "longitude": 82.9739,
                "sanctioned_budget": 14500000.0,
                "start_date": "2024-01-10",
                "end_date": "2024-11-20",
                "verdict": "VERIFIED",
                "confidence_score": 96.8,
                "before_structure_count": 0,
                "after_structure_count": 1,
                "built_area_change_pct": 29.3,
                "audit_notes": "Ground truth verified. Multi-story school blocks and paved assembly court identified.",
                "image_before_path": str(samples_dir / "verified_school" / "before.png"),
                "image_after_path": str(samples_dir / "verified_school" / "after.png"),
                "image_annotated_path": str(samples_dir / "verified_school" / "after.png"),
                "heatmap_path": "",
                "status": "APPROVED",
                "created_at": "2024-11-25 14:30:00"
            },
            {
                "project_name": "Bitumen Highway Link Road 12B",
                "department": "Public Works Department (PWD)",
                "project_type": "Road / Highway",
                "location_name": "Kishanpur to Bhedaghat Link, Madhya Pradesh",
                "latitude": 23.1298,
                "longitude": 79.8007,
                "sanctioned_budget": 32000000.0,
                "start_date": "2024-02-01",
                "end_date": "2024-10-15",
                "verdict": "SUSPICIOUS",
                "confidence_score": 97.0,
                "before_structure_count": 2,
                "after_structure_count": 2,
                "built_area_change_pct": 0.0,
                "audit_notes": "CRITICAL FRAUD: Project marked 100% completed, but satellite shows unpaved dirt path unchanged.",
                "image_before_path": str(samples_dir / "suspicious_road" / "before.png"),
                "image_after_path": str(samples_dir / "suspicious_road" / "after.png"),
                "image_annotated_path": str(samples_dir / "suspicious_road" / "after.png"),
                "heatmap_path": "",
                "status": "FLAGGED_FOR_VIGILANCE",
                "created_at": "2024-10-20 11:15:00"
            },
            {
                "project_name": "Community Health & Trauma Center",
                "department": "Health & Family Welfare",
                "project_type": "Hospital / Health Center",
                "location_name": "Devbagh Block, Ratnagiri, Maharashtra",
                "latitude": 16.9902,
                "longitude": 73.3120,
                "sanctioned_budget": 28000000.0,
                "start_date": "2024-03-01",
                "end_date": "2024-12-05",
                "verdict": "SUSPICIOUS",
                "confidence_score": 97.0,
                "before_structure_count": 0,
                "after_structure_count": 0,
                "built_area_change_pct": 0.0,
                "audit_notes": "NO PHYSICAL ASSET FOUND. Plot remains vacant agricultural land with zero civil works.",
                "image_before_path": str(samples_dir / "suspicious_hospital" / "before.png"),
                "image_after_path": str(samples_dir / "suspicious_hospital" / "after.png"),
                "image_annotated_path": str(samples_dir / "suspicious_hospital" / "after.png"),
                "heatmap_path": "",
                "status": "FLAGGED_FOR_VIGILANCE",
                "created_at": "2024-12-10 16:45:00"
            },
            {
                "project_name": "Brahmani River Elevated Bypass Bridge",
                "department": "National Highways Authority",
                "project_type": "Bridge / Flyover",
                "location_name": "Bypass Bridge, Dhenkanal, Odisha",
                "latitude": 20.6586,
                "longitude": 85.5956,
                "sanctioned_budget": 52000000.0,
                "start_date": "2023-11-01",
                "end_date": "2024-11-30",
                "verdict": "VERIFIED",
                "confidence_score": 89.7,
                "before_structure_count": 0,
                "after_structure_count": 1,
                "built_area_change_pct": 5.7,
                "audit_notes": "River span structure and concrete approach embankments clearly visible.",
                "image_before_path": str(samples_dir / "verified_bridge" / "before.png"),
                "image_after_path": str(samples_dir / "verified_bridge" / "after.png"),
                "image_annotated_path": str(samples_dir / "verified_bridge" / "after.png"),
                "heatmap_path": "",
                "status": "APPROVED",
                "created_at": "2024-12-01 09:20:00"
            }
        ]
        for s in samples:
            cursor.execute("""
            INSERT INTO projects (
                project_name, department, project_type, location_name,
                latitude, longitude, sanctioned_budget, start_date, end_date,
                verdict, confidence_score, before_structure_count, after_structure_count,
                built_area_change_pct, audit_notes, image_before_path, image_after_path,
                image_annotated_path, heatmap_path, status, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                s["project_name"], s["department"], s["project_type"],
                s["location_name"], s["latitude"], s["longitude"],
                s["sanctioned_budget"], s["start_date"], s["end_date"],
                s["verdict"], s["confidence_score"], s["before_structure_count"],
                s["after_structure_count"], s["built_area_change_pct"], s["audit_notes"],
                s["image_before_path"], s["image_after_path"], s["image_annotated_path"],
                s["heatmap_path"], s["status"], s["created_at"]
            ))
        conn.commit()
    conn.close()


def generate_audit_dossier(project: dict) -> str:
    """Generates official investigation dossier."""
    now_str = datetime.now().strftime("%d-%B-%Y %H:%M:%S")
    budget_formatted = f"₹{project.get('sanctioned_budget', 0):,.2f}"
    if project.get('sanctioned_budget', 0) >= 10000000:
        budget_formatted += f" (₹{project.get('sanctioned_budget', 0)/1e7:.2f} Crore)"

    verdict = project.get("verdict", "SUSPICIOUS")
    verdict_emoji = "✅" if verdict == "VERIFIED" else ("🟡" if verdict == "IN_PROGRESS" else "🚨")

    return f"""# 🏛️ GOVERNMENT INFRASTRUCTURE AUDIT DOSSIER
**Automated Satellite Imagery & Computer Vision Verification System**
*Generated on: {now_str}*

---

## 📌 1. Project Identification
- **Project Name:** {project.get('project_name', 'N/A')}
- **Department:** {project.get('department', 'N/A')}
- **Asset Type:** {project.get('project_type', 'N/A')}
- **Location:** {project.get('location_name', 'N/A')}
- **Geographic Coordinates:** Lat {project.get('latitude', 0.0):.5f}, Lon {project.get('longitude', 0.0):.5f}
- **Sanctioned Public Budget:** {budget_formatted}
- **Target Construction Window:** {project.get('start_date', 'N/A')} to {project.get('end_date', 'N/A')}

---

## {verdict_emoji} 2. Audit Findings & Verification Verdict

### **VERDICT: {verdict}**
- **AI Verification Confidence:** **{project.get('confidence_score', 0.0)}%**
- **Audit Status:** `{project.get('status', 'AUDITED')}`

### **🔍 Summary Finding:**
> {project.get('audit_notes') or 'Verification completed.'}

---

## 📊 3. Satellite Computer Vision Evidence Matrix

| Metric Parameter | Pre-Construction | Post-Completion | Change Delta |
|:---|:---:|:---:|:---:|
| **Detected Physical Structures** | {project.get('before_structure_count', 0)} | {project.get('after_structure_count', 0)} | **{project.get('after_structure_count', 0) - project.get('before_structure_count', 0):+d} structures** |
| **Built-up Surface Footprint** | - | - | **+{project.get('built_area_change_pct', 0.0)}% growth** |

---
*Disclaimer: Generated autonomously by the Fake Infrastructure Detector AI engine.*
"""


def get_government_portal_contracts():
    """
    Simulates live API ingestion from National Informatics Centre (NIC) 
    government portals: e-GramSwaraj, PMGSY, PM Gati Shakti, and CPPP e-Procure.
    """
    return [
        {
            "work_order_id": "NIC/EGS/2024/SCH-9941",
            "source_portal": "e-GramSwaraj (Ministry of Panchayati Raj)",
            "project_name": "Primary Model School Complex",
            "department": "Education & School Infrastructure",
            "project_type": "Building / School",
            "location_name": "Rampur Sector 4, Varanasi, Uttar Pradesh",
            "latitude": 25.3176,
            "longitude": 82.9739,
            "sanctioned_budget": 14500000.0,
            "contractor_name": "Apex Civil Infrastructure Ltd.",
            "tender_id": "CPP/2023/PWD/88219",
            "start_date": "2024-01-15",
            "end_date": "2024-11-20",
            "completion_claimed_date": "2024-11-22",
            "payment_claimed": "₹1.45 Crore (100% Stage 4)",
            "sample_id": "verified_school"
        },
        {
            "work_order_id": "PMGSY/MP/2024/RD-4102",
            "source_portal": "PMGSY (Pradhan Mantri Gram Sadak Yojana)",
            "project_name": "Bitumen Highway Link Road 12B",
            "department": "Public Works Department (PWD)",
            "project_type": "Road / Highway",
            "location_name": "Kishanpur to Bhedaghat Link, Madhya Pradesh",
            "latitude": 23.1298,
            "longitude": 79.8007,
            "sanctioned_budget": 32000000.0,
            "contractor_name": "Shree Ram Infra & Bitumen Works",
            "tender_id": "CPP/2023/PMGSY/1149",
            "start_date": "2024-02-01",
            "end_date": "2024-10-15",
            "completion_claimed_date": "2024-10-18",
            "payment_claimed": "₹3.20 Crore (Final Settlement)",
            "sample_id": "suspicious_road"
        },
        {
            "work_order_id": "NRHM/MH/2024/HOSP-882",
            "source_portal": "data.gov.in (National Health Mission)",
            "project_name": "Community Health & Trauma Center",
            "department": "Health & Family Welfare",
            "project_type": "Hospital / Health Center",
            "location_name": "Devbagh Block, Ratnagiri, Maharashtra",
            "latitude": 16.9902,
            "longitude": 73.3120,
            "sanctioned_budget": 28000000.0,
            "contractor_name": "Universal Medicare Builders",
            "tender_id": "CPP/2024/HFW/3392",
            "start_date": "2024-03-01",
            "end_date": "2024-12-05",
            "completion_claimed_date": "2024-12-08",
            "payment_claimed": "₹2.80 Crore (Final Bill)",
            "sample_id": "suspicious_hospital"
        },
        {
            "work_order_id": "NHAI/GATI/2024/BRG-005",
            "source_portal": "PM Gati Shakti Master Plan (BISAG-N)",
            "project_name": "Brahmani River Elevated Bypass Bridge",
            "department": "National Highways Authority",
            "project_type": "Bridge / Flyover",
            "location_name": "Bypass Bridge, Dhenkanal, Odisha",
            "latitude": 20.6586,
            "longitude": 85.5956,
            "sanctioned_budget": 52000000.0,
            "contractor_name": "L&B Engineering Infra Corp",
            "tender_id": "CPP/2023/NHAI/7721",
            "start_date": "2023-11-01",
            "end_date": "2024-11-30",
            "completion_claimed_date": "2024-12-01",
            "payment_claimed": "₹5.20 Crore (Milestone 3)",
            "sample_id": "verified_bridge"
        }
    ]


# -------------------------------------------------------------------------
# MPLADS constituency allocation register
# -------------------------------------------------------------------------

_MPLADS_CACHE = None


def load_mp_allocations() -> dict:
    """Loads the official MPLADS allocation register for all Lok Sabha constituencies."""
    global _MPLADS_CACHE
    if _MPLADS_CACHE is None:
        with open(MPLADS_PATH, encoding="utf-8") as handle:
            _MPLADS_CACHE = json.load(handle)
    return _MPLADS_CACHE


def get_mplads_summary() -> dict:
    """Returns headline figures for the allocation register."""
    register = load_mp_allocations()
    members = register["members"]
    states = sorted({m["state"] for m in members})
    return {
        "member_count": register["member_count"],
        "total_allocated_amount": register["total_allocated_amount"],
        "total_allocated_crore": register["total_allocated_crore"],
        "state_count": len(states),
        "states": states,
        "source": register["source"],
    }


def search_mp_allocations(query: str = "", state: str = "") -> list:
    """Filters the allocation register by member name, constituency or state."""
    members = load_mp_allocations()["members"]
    if state:
        members = [m for m in members if m["state"] == state]
    if query:
        needle = query.strip().lower()
        members = [
            m for m in members
            if needle in m["mp_name"].lower()
            or needle in m["constituency"].lower()
            or needle in m["state"].lower()
        ]
    return members


def get_state_allocation_totals() -> list:
    """Aggregates allocated funds per state, highest first."""
    totals = {}
    for member in load_mp_allocations()["members"]:
        entry = totals.setdefault(member["state"], {"state": member["state"], "members": 0, "allocated_amount": 0.0})
        entry["members"] += 1
        entry["allocated_amount"] += member["allocated_amount"] or 0.0
    return sorted(totals.values(), key=lambda e: e["allocated_amount"], reverse=True)


# -------------------------------------------------------------------------
# Documented infrastructure failure case studies
# -------------------------------------------------------------------------

CASE_STUDIES = [
    {
        "title": "Defunct Biju Setu Bridge Project",
        "location_name": "Jajpur District, Odisha",
        "state": "Odisha",
        "asset_type": "Bridge",
        "sanctioned_budget": 110000000.0,
        "delay_summary": "₹11 crore sunk cost, structure abandoned",
        "promise_and_delay": (
            "Constructed at an expense of ₹11 crore under the Biju Setu scheme, the bridge structure "
            "stands abruptly abandoned without functional approach roads or structural continuity."
        ),
        "human_impact": (
            "Villagers are forced into a 15 km detour to cover a straight-line distance of 100 metres, "
            "disrupting daily commerce and emergency transit."
        ),
        "latitude": 20.8410,
        "longitude": 86.3340,
        "source": "OdishaTV report, 04 August 2026",
    },
    {
        "title": "Biju Setu Bridge Execution Delay",
        "location_name": "Ganjam District, Odisha",
        "state": "Odisha",
        "asset_type": "Bridge",
        "sanctioned_budget": None,
        "delay_summary": "Four years past completion deadline",
        "promise_and_delay": (
            "Meant to deliver essential river crossing connectivity, the project has stalled four years "
            "past its completion deadline due to uncoordinated execution."
        ),
        "human_impact": (
            "Schoolchildren and daily workers wade through hazardous riverbeds and muddy tracks on "
            "two-wheelers, risking their lives to meet basic needs."
        ),
        "latitude": 19.3860,
        "longitude": 84.8800,
        "source": "OdishaTV report, 01 September 2026",
    },
    {
        "title": "Kiratpur-Manali National Highway (NH-21)",
        "location_name": "Mandi & Kullu Districts, Himachal Pradesh",
        "state": "Himachal Pradesh",
        "asset_type": "Highway",
        "sanctioned_budget": None,
        "delay_summary": "Over five years behind target",
        "promise_and_delay": (
            "Signed in August 2017 with an original completion target of September 2021. The prolonged "
            "delay forced the Himachal Pradesh High Court to summon the concessionaire's managing director."
        ),
        "human_impact": (
            "Damaged, incomplete stretches have subjected travellers and tourists to extreme hardship for "
            "over five years, hampering the regional tourism economy."
        ),
        "latitude": 31.7080,
        "longitude": 76.9310,
        "source": "Himachal Pradesh High Court proceedings, May 2026",
    },
    {
        "title": "Banjar Hospital Expansion Project",
        "location_name": "Banjar, Kullu District, Himachal Pradesh",
        "state": "Himachal Pradesh",
        "asset_type": "Hospital",
        "sanctioned_budget": None,
        "delay_summary": "Delayed for five years and counting",
        "promise_and_delay": (
            "Intended to expand local healthcare capacity from 50 to 100 beds. Although 85% of structural "
            "framing is up, roofing and interior finishing remain completely incomplete."
        ),
        "human_impact": (
            "Patients rely on an overcrowded, cracked facility or travel 50-60 km to regional medical "
            "centres in Kullu or Shimla for critical care."
        ),
        "latitude": 31.6360,
        "longitude": 77.3390,
        "source": "Press report, March 2026",
    },
    {
        "title": "Brazloo Bridge Bypass (NH-444)",
        "location_name": "Kulgam District, Jammu & Kashmir",
        "state": "Jammu And Kashmir",
        "asset_type": "Bridge",
        "sanctioned_budget": None,
        "delay_summary": "Missed the April 2026 completion target",
        "promise_and_delay": (
            "Originally sanctioned in 2017 and retendered in 2022 with an April 2026 completion target. "
            "Official claims of 95% completion contrast with ongoing real-world bottlenecks."
        ),
        "human_impact": (
            "Commuters face daily gridlock on the narrow existing bridge, delaying transit and "
            "compromising emergency patient transport."
        ),
        "latitude": 33.6400,
        "longitude": 75.0190,
        "source": "Daily Excelsior report, May 2026",
    },
]


def seed_case_studies():
    """Seeds the documented infrastructure failure case studies."""
    init_db()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as cnt FROM case_studies")
    if cursor.fetchone()["cnt"] == 0:
        for study in CASE_STUDIES:
            cursor.execute("""
            INSERT INTO case_studies (
                title, location_name, state, asset_type, sanctioned_budget,
                delay_summary, promise_and_delay, human_impact, latitude, longitude, source
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                study["title"], study["location_name"], study["state"], study["asset_type"],
                study["sanctioned_budget"], study["delay_summary"], study["promise_and_delay"],
                study["human_impact"], study["latitude"], study["longitude"], study["source"]
            ))
        conn.commit()
    conn.close()


def get_case_studies() -> list:
    """Retrieves the seeded infrastructure failure case studies."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM case_studies ORDER BY id")
    studies = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return studies


# -------------------------------------------------------------------------
# Contractor execution portal
# -------------------------------------------------------------------------

def submit_milestone_claim(claim: dict) -> int:
    """Records a contractor milestone claim awaiting independent satellite audit."""
    init_db()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO milestone_claims (
        work_order_id, contractor_name, milestone, claim_amount, gst_invoice_no,
        progress_pct, geotag_latitude, geotag_longitude, dlp_bond_reference,
        remarks, status, created_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        claim["work_order_id"], claim["contractor_name"], claim["milestone"],
        claim["claim_amount"], claim["gst_invoice_no"], claim["progress_pct"],
        claim.get("geotag_latitude"), claim.get("geotag_longitude"),
        claim.get("dlp_bond_reference", ""), claim.get("remarks", ""),
        claim.get("status", "PENDING_SATELLITE_AUDIT"),
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))
    claim_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return claim_id


def get_milestone_claims(contractor_name: str = "") -> list:
    """Retrieves milestone claims, optionally scoped to one contractor."""
    conn = get_connection()
    cursor = conn.cursor()
    if contractor_name:
        cursor.execute("SELECT * FROM milestone_claims WHERE contractor_name = ? ORDER BY id DESC", (contractor_name,))
    else:
        cursor.execute("SELECT * FROM milestone_claims ORDER BY id DESC")
    claims = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return claims


def get_contractor_credibility_index() -> list:
    """Scores contractors on the share of their audited works confirmed on the ground."""
    scores = {}
    for contract in get_government_portal_contracts():
        scores[contract["contractor_name"]] = {
            "contractor_name": contract["contractor_name"],
            "works": 0,
            "verified": 0,
            "flagged": 0,
            "capital_at_risk": 0.0,
        }

    audited = {p["project_name"]: p for p in get_all_projects()}
    for contract in get_government_portal_contracts():
        entry = scores[contract["contractor_name"]]
        project = audited.get(contract["project_name"])
        if project is None:
            continue
        entry["works"] += 1
        if project["verdict"] == "VERIFIED":
            entry["verified"] += 1
        elif project["verdict"] == "SUSPICIOUS":
            entry["flagged"] += 1
            entry["capital_at_risk"] += project["sanctioned_budget"]

    for entry in scores.values():
        entry["cci_score"] = round(entry["verified"] / entry["works"] * 100, 1) if entry["works"] else None
        if entry["cci_score"] is None:
            entry["rating"] = "NOT RATED"
        elif entry["cci_score"] >= 80:
            entry["rating"] = "RELIABLE"
        elif entry["cci_score"] >= 50:
            entry["rating"] = "WATCHLIST"
        else:
            entry["rating"] = "HIGH RISK"

    return sorted(scores.values(), key=lambda e: (e["cci_score"] is None, -(e["cci_score"] or 0)))


# -------------------------------------------------------------------------
# Public citizen portal
# -------------------------------------------------------------------------

def _reference_code(prefix: str) -> str:
    return f"{prefix}-{datetime.now().strftime('%Y%m%d%H%M%S')}"


def submit_whistleblower_report(report: dict) -> str:
    """Lodges an anonymous citizen report and returns its tracking reference."""
    init_db()
    reference = _reference_code("WB")
    conn = get_connection()
    conn.execute("""
    INSERT INTO whistleblower_reports (
        reference_code, project_reference, location_name, category, description, status, created_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        reference, report["project_reference"], report["location_name"], report["category"],
        report["description"], "UNDER_REVIEW", datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))
    conn.commit()
    conn.close()
    return reference


def get_whistleblower_reports() -> list:
    """Retrieves lodged citizen reports."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM whistleblower_reports ORDER BY id DESC")
    reports = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return reports


def submit_warranty_claim(claim: dict) -> str:
    """Lodges a defect liability period claim and returns its tracking reference."""
    init_db()
    reference = _reference_code("DLP")
    conn = get_connection()
    conn.execute("""
    INSERT INTO warranty_claims (
        reference_code, asset_name, location_name, defect_type, commissioned_on,
        within_dlp, description, status, created_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        reference, claim["asset_name"], claim["location_name"], claim["defect_type"],
        claim["commissioned_on"], int(claim["within_dlp"]), claim["description"],
        "LODGED" if claim["within_dlp"] else "OUTSIDE_WARRANTY",
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))
    conn.commit()
    conn.close()
    return reference


def get_warranty_claims() -> list:
    """Retrieves lodged defect liability claims."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM warranty_claims ORDER BY id DESC")
    claims = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return claims


# -------------------------------------------------------------------------
# Three-way payment gatekeeper
# -------------------------------------------------------------------------

def evaluate_payment_gate(claim: dict, project: dict = None, citizen_flags: int = 0) -> dict:
    """
    Clears a contractor payment only when the contractor claim, the satellite audit
    verdict and citizen oversight all agree that the asset exists.
    """
    checks = []

    claimed_complete = claim.get("progress_pct", 0) >= 100
    checks.append({
        "name": "Contractor milestone declaration",
        "passed": claimed_complete,
        "detail": f"Contractor reports {claim.get('progress_pct', 0):.0f}% execution against milestone "
                  f"'{claim.get('milestone', 'N/A')}'.",
    })

    verdict = (project or {}).get("verdict")
    checks.append({
        "name": "Independent satellite verification",
        "passed": verdict == "VERIFIED",
        "detail": f"Earth observation audit verdict: {verdict or 'NOT YET AUDITED'}.",
    })

    checks.append({
        "name": "Citizen oversight clearance",
        "passed": citizen_flags == 0,
        "detail": f"{citizen_flags} open citizen report(s) against this work order.",
    })

    cleared = all(check["passed"] for check in checks)
    return {
        "cleared": cleared,
        "decision": "RELEASE PAYMENT" if cleared else "PAYMENT WITHHELD",
        "checks": checks,
        "amount": claim.get("claim_amount", 0.0),
    }
