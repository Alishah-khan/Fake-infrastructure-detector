"""
Automated test suite for the InfraAudit verification portal.
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
from integration import (
    evaluate_payment_gate, generate_audit_dossier, get_all_projects, get_audit_statistics,
    get_case_studies, get_mplads_summary, get_state_allocation_totals, get_whistleblower_reports,
    init_db, search_mp_allocations, seed_case_studies, seed_sample_projects,
    submit_whistleblower_report,
)
from app_auth import authenticate


def run_tests():
    print("==================================================")
    print("RUNNING INFRAAUDIT PORTAL TEST SUITE")
    print("==================================================")

    print("\n[1/7] Generating Sample Datasets...")
    generate_all_samples()
    print("  [+] Sample satellite pairs generated.")

    print("\n[2/7] Testing Geocoding...")
    lat, lon, addr = geocode_location("Varanasi")
    print(f"  [+] Resolved Varanasi -> ({lat:.4f}, {lon:.4f})")

    print("\n[3/7] Testing AI Detection Engine...")
    b_path, a_path = fetch_satellite_pair(25.0, 80.0, "2024-01-01", "2024-12-01", sample_id="verified_school")
    res = analyze_infrastructure_project(b_path, a_path, "Building / School", 15000000.0, "Test School")
    print(f"  [+] School Verdict: {res['verdict']} (Confidence: {res['confidence_score']}%)")
    assert res['verdict'] == "VERIFIED"

    b_path, a_path = fetch_satellite_pair(23.0, 79.0, "2024-01-01", "2024-12-01", sample_id="suspicious_road")
    res_road = analyze_infrastructure_project(b_path, a_path, "Road / Highway", 32000000.0, "Test Road")
    print(f"  [+] Ghost Road Verdict: {res_road['verdict']} (Confidence: {res_road['confidence_score']}%)")
    assert res_road['verdict'] == "SUSPICIOUS"

    print("\n[4/7] Testing Database & Dossier Exporter...")
    init_db()
    seed_sample_projects()
    stats = get_audit_statistics()
    print(f"  [+] Total Projects: {stats['total_projects']}, Flagged: {stats['suspicious_count']}")
    assert stats['total_projects'] >= 4

    sample_proj = get_all_projects()[0]
    dossier = generate_audit_dossier(sample_proj)
    assert "GOVERNMENT INFRASTRUCTURE AUDIT DOSSIER" in dossier
    print("  [+] Audit dossier generated.")

    print("\n[5/7] Testing MPLADS Allocation Register...")
    summary = get_mplads_summary()
    print(f"  [+] Constituencies on record: {summary['member_count']}, "
          f"total ₹{summary['total_allocated_crore']:,.2f} Cr")
    assert summary['member_count'] == 543
    assert len(search_mp_allocations()) == 543

    for needle in ["Modi", "Varanasi", "Rahul Gandhi", "Tharoor", "Owaisi"]:
        hits = search_mp_allocations(needle)
        print(f"  [+] Search '{needle}' -> {len(hits)} record(s): "
              f"{', '.join(h['mp_name'] for h in hits[:3])}")
        assert hits, f"no allocation record matched '{needle}'"

    kerala = search_mp_allocations(state="Kerala")
    assert kerala and all(m['state'] == "Kerala" for m in kerala)
    state_totals = get_state_allocation_totals()
    assert sum(s['members'] for s in state_totals) == 543
    print(f"  [+] State filtering works across {len(state_totals)} states/UTs.")

    print("\n[6/7] Testing Empirical Case Studies...")
    seed_case_studies()
    studies = get_case_studies()
    print(f"  [+] Case studies seeded: {len(studies)}")
    assert len(studies) == 5
    assert any("Jajpur" in s['location_name'] for s in studies)
    seed_case_studies()
    assert len(get_case_studies()) == 5, "case study seeding must be idempotent"

    print("\n[7/7] Testing Role Authentication & Payment Gatekeeper...")
    assert authenticate("government", "admin", "mospi2026")
    assert authenticate("contractor", "contractor", "pass123")
    assert not authenticate("government", "contractor", "pass123")
    assert not authenticate("contractor", "admin", "mospi2026")
    assert not authenticate("government", "admin", "wrong-password")
    print("  [+] Role permissions enforced across both protected portals.")

    claim = {"work_order_id": "WO/TEST/1", "milestone": "Completion",
             "claim_amount": 5200000.0, "progress_pct": 100.0}
    verified_project = next(p for p in get_all_projects() if p['verdict'] == "VERIFIED")
    flagged_project = next(p for p in get_all_projects() if p['verdict'] == "SUSPICIOUS")
    assert evaluate_payment_gate(claim, verified_project, 0)['cleared']
    assert not evaluate_payment_gate(claim, flagged_project, 0)['cleared']
    assert not evaluate_payment_gate(claim, verified_project, 1)['cleared']
    assert not evaluate_payment_gate({**claim, "progress_pct": 40.0}, verified_project, 0)['cleared']
    print("  [+] Three-way payment gatekeeper withholds on any failed check.")

    reference = submit_whistleblower_report({
        "project_reference": "WO/TEST/1", "location_name": "Test Village",
        "category": "Asset does not exist", "description": "No structure at the site.",
    })
    assert reference.startswith("WB-")
    assert any(r['reference_code'] == reference for r in get_whistleblower_reports())
    print(f"  [+] Citizen report lodged with reference {reference}.")

    print("\n==================================================")
    print("ALL TESTS PASSED SUCCESSFULLY!")
    print("==================================================")


if __name__ == "__main__":
    run_tests()
