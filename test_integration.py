"""
Automated Test Suite for Fake Infrastructure Detector.
"""

import sys
from pathlib import Path

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.member1_fetcher import geocode_location, fetch_satellite_pair, generate_all_samples
from src.member2_detector import analyze_infrastructure_project
from integration import init_db, seed_sample_projects, get_audit_statistics, get_all_projects, generate_audit_dossier


def run_tests():
    print("==================================================")
    print("RUNNING FAKE INFRASTRUCTURE DETECTOR TEST SUITE")
    print("==================================================")

    print("\n[1/4] Generating Sample Datasets...")
    generate_all_samples()
    print("  [+] Sample satellite pairs generated.")

    print("\n[2/4] Testing Geocoding...")
    lat, lon, addr = geocode_location("Varanasi")
    print(f"  [+] Resolved Varanasi -> ({lat:.4f}, {lon:.4f})")

    print("\n[3/4] Testing AI Detection Engine...")
    b_path, a_path = fetch_satellite_pair(25.0, 80.0, "2024-01-01", "2024-12-01", sample_id="verified_school")
    res = analyze_infrastructure_project(b_path, a_path, "Building / School", 15000000.0, "Test School")
    print(f"  [+] School Verdict: {res['verdict']} (Confidence: {res['confidence_score']}%)")
    assert res['verdict'] == "VERIFIED"

    b_path, a_path = fetch_satellite_pair(23.0, 79.0, "2024-01-01", "2024-12-01", sample_id="suspicious_road")
    res_road = analyze_infrastructure_project(b_path, a_path, "Road / Highway", 32000000.0, "Test Road")
    print(f"  [+] Ghost Road Verdict: {res_road['verdict']} (Confidence: {res_road['confidence_score']}%)")
    assert res_road['verdict'] == "SUSPICIOUS"

    print("\n[4/4] Testing Database & Dossier Exporter...")
    init_db()
    seed_sample_projects()
    stats = get_audit_statistics()
    print(f"  [+] Total Projects: {stats['total_projects']}, Flagged: {stats['suspicious_count']}")
    assert stats['total_projects'] >= 4

    sample_proj = get_all_projects()[0]
    dossier = generate_audit_dossier(sample_proj)
    assert "GOVERNMENT INFRASTRUCTURE AUDIT DOSSIER" in dossier
    print("  [+] Audit dossier generated.")

    print("\n==================================================")
    print("ALL TESTS PASSED SUCCESSFULLY!")
    print("==================================================")


if __name__ == "__main__":
    run_tests()
