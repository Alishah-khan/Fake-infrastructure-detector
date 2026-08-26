"""
Module: System Integration & Database Ledger
Author: Member 4 (Integration & System Architecture Lead)

Handles SQLite database persistence, aggregated vigilance KPIs, and formal investigation dossiers.
"""

import sqlite3
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "data" / "projects.db"


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
