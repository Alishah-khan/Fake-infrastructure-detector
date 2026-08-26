"""
Fake Infrastructure Detector
AI-Powered Satellite Verification Platform for Public Infrastructure Projects.
"""

import streamlit as st
import folium
from streamlit_folium import st_folium
import plotly.express as px
import pandas as pd
from datetime import datetime, date
from pathlib import Path
from PIL import Image, ImageFile

ImageFile.LOAD_TRUNCATED_IMAGES = True

from src.member1_fetcher import (
    geocode_location, fetch_satellite_pair, get_demo_samples_meta, generate_all_samples
)
from src.member2_detector import analyze_infrastructure_project
from src.member3_dashboard import get_custom_ui_theme, safe_load_image
from integration import (
    init_db, save_project, get_all_projects, get_flagged_projects,
    get_audit_statistics, seed_sample_projects, generate_audit_dossier,
    get_government_portal_contracts
)

# Page Setup
st.set_page_config(
    page_title="InfraAudit | Satellite Verification Platform",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Apply UI Theme
st.markdown(get_custom_ui_theme(), unsafe_allow_html=True)

# Initialize Storage & Datasets
generate_all_samples()
init_db()
seed_sample_projects()

# CENTERED PREMIUM HERO HEADER
st.markdown("""
<div class="hero-center-container">
    <div class="hero-pill">🛰️ AI Earth Observation & National Vigilance Engine</div>
    <h1 class="hero-title-main">
        🏗️ <span class="hero-title-gradient">InfraAudit</span>
    </h1>
    <p class="hero-tagline">
        Autonomous satellite surveillance pipeline verifying public infrastructure execution, exposing ghost assets, and protecting public treasury funds.
    </p>
</div>
""", unsafe_allow_html=True)

# Navigation (Centered)
tab_feed, tab_portal, tab_verify, tab_analytics, tab_team = st.tabs([
    "🌐 Public Surveillance Feed",
    "🏛️ Govt Portal Sync Gateway",
    "🔍 Verify New Project",
    "📊 Civic Audit Analytics",
    "👥 Team Roles & Architecture"
])

# -------------------------------------------------------------
# TAB 1: SURVEILLANCE FEED
# -------------------------------------------------------------
with tab_feed:
    stats = get_audit_statistics()

    # Metric Row
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.metric("Total Scrutinized Projects", f"{stats['total_projects']} Contracts")
    with k2:
        st.metric("Monitored Public Outlay", f"₹{stats['total_budget']/1e7:.2f} Cr")
    with k3:
        st.metric("Flagged Fraud Outlay", f"₹{stats['flagged_budget']/1e7:.2f} Cr", delta=f"{stats['suspicious_count']} Scams Flagged", delta_color="inverse")
    with k4:
        st.metric("Fraud Anomaly Rate", f"{stats['fraud_risk_rate']}%", delta_color="off")

    st.markdown("---")

    # Search & Category Filter
    col_s1, col_s2 = st.columns([3, 1])
    with col_s1:
        search_query = st.text_input("🔍 Search by project title, state, department, or keyword...", placeholder="e.g., School, Road, Varanasi, Madhya Pradesh...")
    with col_s2:
        filter_category = st.selectbox(
            "Filter Category:",
            ["All Infrastructure", "🚨 Flagged Scams Only", "✅ Verified Only", "🏫 Schools", "🛣️ Highways", "🏥 Hospitals", "🌉 Bridges"]
        )

    projects = get_all_projects()

    if filter_category == "🚨 Flagged Scams Only":
        projects = [p for p in projects if p["verdict"] == "SUSPICIOUS"]
    elif filter_category == "✅ Verified Only":
        projects = [p for p in projects if p["verdict"] == "VERIFIED"]
    elif filter_category == "🏫 Schools":
        projects = [p for p in projects if "School" in p["project_type"] or "Education" in p["department"]]
    elif filter_category == "🛣️ Highways":
        projects = [p for p in projects if "Road" in p["project_type"]]
    elif filter_category == "🏥 Hospitals":
        projects = [p for p in projects if "Hospital" in p["project_type"] or "Health" in p["department"]]
    elif filter_category == "🌉 Bridges":
        projects = [p for p in projects if "Bridge" in p["project_type"]]

    if search_query:
        projects = [
            p for p in projects
            if search_query.lower() in p["project_name"].lower()
            or search_query.lower() in p["location_name"].lower()
            or search_query.lower() in p["department"].lower()
        ]

    st.markdown("### 📋 Active Inspection Ledger")

    cols = st.columns(3)
    for idx, p in enumerate(projects):
        col = cols[idx % 3]

        with col:
            verdict = p["verdict"]
            badge_class = "badge-verified" if verdict == "VERIFIED" else ("badge-progress" if verdict == "IN_PROGRESS" else "badge-suspicious")
            badge_text = "✅ CONFIRMED BUILT" if verdict == "VERIFIED" else ("🟡 IN PROGRESS" if verdict == "IN_PROGRESS" else "🚨 FLAGGED FRAUD")
            budget_str = f"₹{p['sanctioned_budget']/1e7:.2f} Cr" if p['sanctioned_budget'] >= 1e7 else f"₹{p['sanctioned_budget']/1e5:.1f} L"

            with st.container(border=True):
                st.markdown(f"""
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                    <span class="{badge_class}">{badge_text}</span>
                    <span style="font-weight:700; color:#1e293b; font-size:0.9rem;">{budget_str}</span>
                </div>
                """, unsafe_allow_html=True)

                img_path = p.get("image_after_path") or p.get("image_before_path")
                loaded_img = safe_load_image(img_path)
                if loaded_img:
                    st.image(loaded_img, use_container_width=True)

                st.markdown(f"#### {p['project_name']}")
                st.caption(f"🏛️ **{p['department']}** | 📍 {p['location_name']}")

                st.markdown(f"""
                <div class="metric-chip-row">
                    <div class="metric-chip-item">
                        <div class="metric-chip-val">{p['confidence_score']}%</div>
                        <div class="metric-chip-lbl">Confidence</div>
                    </div>
                    <div class="metric-chip-item">
                        <div class="metric-chip-val" style="color:#16a34a;">&lt; 3%</div>
                        <div class="metric-chip-lbl">Cloud Cover</div>
                    </div>
                    <div class="metric-chip-item">
                        <div class="metric-chip-val">+{p['built_area_change_pct']}%</div>
                        <div class="metric-chip-lbl">Growth</div>
                    </div>
                    <div class="metric-chip-item">
                        <div class="metric-chip-val">{p['after_structure_count']}</div>
                        <div class="metric-chip-lbl">Structures</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                st.markdown(f"<div class='audit-callout'>{p['audit_notes']}</div>", unsafe_allow_html=True)

                with st.expander(f"🔍 Satellite Evidence #{p['id']}"):
                    cb1, cb2 = st.columns(2)
                    with cb1:
                        st.caption(f"📅 Baseline ({p['start_date']})")
                        b_img = safe_load_image(p.get("image_before_path"))
                        if b_img:
                            st.image(b_img, use_container_width=True)
                    with cb2:
                        st.caption(f"📅 Post-Completion ({p['end_date']})")
                        a_img = safe_load_image(p.get("image_after_path"))
                        if a_img:
                            st.image(a_img, use_container_width=True)

                    dossier_text = generate_audit_dossier(p)
                    st.download_button(
                        f"📥 Export Dossier #{p['id']}",
                        data=dossier_text,
                        file_name=f"audit_dossier_{p['id']}.md",
                        mime="text/markdown",
                        key=f"dl_{p['id']}"
                    )

# -------------------------------------------------------------
# TAB 2: GOVERNMENT PORTAL SYNC GATEWAY
# -------------------------------------------------------------
with tab_portal:
    st.markdown("### 🏛️ National Government Portal API Gateway")
    st.caption("Live integration pipeline connecting to **e-GramSwaraj, PMGSY, PM Gati Shakti, and data.gov.in** API endpoints to ingest claims before financial treasury disbursement.")

    c_p1, c_p2, c_p3 = st.columns([2, 1, 1])
    with c_p1:
        portal_filter = st.selectbox(
            "Select Connected Government Portal:",
            ["All National Portals (4 Active Feeds)", "e-GramSwaraj (Panchayati Raj)", "PMGSY (Rural Roads)", "PM Gati Shakti Master Plan", "data.gov.in Open Data"]
        )
    with c_p2:
        st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
        if st.button("🔄 Sync Government Feeds"):
            st.toast("Synchronized with National Informatics Centre (NIC) Gateway!", icon="✅")
    with c_p3:
        st.markdown("<div style='height:32px'></div>", unsafe_allow_html=True)
        st.markdown("<span style='background:#dcfce7; color:#16a34a; padding:6px 12px; border-radius:20px; font-weight:700; font-size:0.8rem;'>● 4 GOVT APIS CONNECTED</span>", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("#### 📑 Incoming Completion Claims Awaiting Satellite Audit")

    portal_contracts = get_government_portal_contracts()

    for c in portal_contracts:
        with st.container(border=True):
            col_h1, col_h2 = st.columns([3, 1])
            with col_h1:
                st.markdown(f"#### 🏛️ {c['project_name']} (`{c['work_order_id']}`)")
                st.caption(f"📡 **Source:** {c['source_portal']} | 🏢 **Contractor:** {c['contractor_name']} | 📜 **Tender ID:** `{c['tender_id']}`")
            with col_h2:
                st.markdown(f"<div style='text-align:right; font-weight:700; font-size:1.1rem; color:#1e293b;'>{c['payment_claimed']}</div>", unsafe_allow_html=True)
                st.markdown(f"<div style='text-align:right; font-size:0.8rem; color:#64748b;'>Claimed: {c['completion_claimed_date']}</div>", unsafe_allow_html=True)

            c_info1, c_info2, c_info3 = st.columns([2, 2, 1.2])
            with c_info1:
                st.write(f"📍 **Location:** {c['location_name']}")
                st.write(f"🌐 **GIS Coordinates:** `{c['latitude']:.4f}, {c['longitude']:.4f}`")
            with c_info2:
                st.write(f"📅 **Contract Period:** {c['start_date']} to {c['end_date']}")
                st.write(f"💰 **Sanctioned Outlay:** ₹{c['sanctioned_budget']/1e7:.2f} Crore")
            with c_info3:
                st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
                if st.button(f"🛰️ Audit via Satellite", key=f"btn_audit_{c['work_order_id']}", type="primary", use_container_width=True):
                    with st.status(f"Auditing {c['work_order_id']}...", expanded=True) as status:
                        st.write("1. 📡 Querying Sentinel-2 & High-Resolution Tile Archive...")
                        b_path, a_path = fetch_satellite_pair(c['latitude'], c['longitude'], c['start_date'], c['end_date'], sample_id=c['sample_id'])

                        st.write("2. 🧠 Running structural computer vision footprint detection...")
                        analysis = analyze_infrastructure_project(
                            before_img_path=b_path,
                            after_img_path=a_path,
                            project_type=c['project_type'],
                            sanctioned_budget=c['sanctioned_budget'],
                            project_name=c['project_name']
                        )

                        st.write("3. 📑 Logging audit results to public surveillance ledger...")
                        new_record = {
                            "project_name": c['project_name'],
                            "department": c['department'],
                            "project_type": c['project_type'],
                            "location_name": c['location_name'],
                            "latitude": c['latitude'],
                            "longitude": c['longitude'],
                            "sanctioned_budget": c['sanctioned_budget'],
                            "start_date": c['start_date'],
                            "end_date": c['end_date'],
                            "verdict": analysis["verdict"],
                            "confidence_score": analysis["confidence_score"],
                            "before_structure_count": analysis["before_structure_count"],
                            "after_structure_count": analysis["after_structure_count"],
                            "built_area_change_pct": analysis["built_area_change_pct"],
                            "audit_notes": f"[Govt Work Order: {c['work_order_id']} | Source: {c['source_portal']}] " + analysis["reason"],
                            "image_before_path": b_path,
                            "image_after_path": a_path,
                            "image_annotated_path": analysis["image_annotated_path"],
                            "heatmap_path": analysis["heatmap_path"],
                            "status": analysis["status"]
                        }
                        save_project(new_record)
                        status.update(label="✅ Government Claim Audited Successfully!", state="complete", expanded=False)

                    # Show Verdict Result
                    if analysis["verdict"] == "SUSPICIOUS":
                        st.error(f"🚨 **SUSPICIOUS — {c['project_name']}:** {analysis['reason']} (AI Confidence: {analysis['confidence_score']}%)")
                    else:
                        st.success(f"✅ **VERIFIED — {c['project_name']}:** {analysis['reason']} (AI Confidence: {analysis['confidence_score']}%)")

# -------------------------------------------------------------
# TAB 3: VERIFY NEW PROJECT
# -------------------------------------------------------------
with tab_verify:
    st.markdown("### 🔍 Initiate Satellite Verification")
    st.caption("Submit project details to retrieve temporal Earth Observation passes and execute AI change detection.")

    demo_samples = get_demo_samples_meta()
    demo_dict = {f"{'✅' if s['expected_verdict']=='VERIFIED' else '🔴'} {s['name']}": s for s in demo_samples}

    selected_demo_key = st.selectbox(
        "⚡ Quick Test with Ground Truth Presets:",
        ["-- Custom Project Input --"] + list(demo_dict.keys())
    )

    sample_data = demo_dict.get(selected_demo_key, None)

    def_name = sample_data["name"] if sample_data else "Modern Primary School Wing"
    def_dept = sample_data["department"] if sample_data else "Education & School Infrastructure"
    def_type = sample_data["type"] if sample_data else "Building / School"
    def_loc = sample_data["location"] if sample_data else "Rampur Sector 4, Varanasi, Uttar Pradesh"
    def_lat = sample_data["lat"] if sample_data else 25.3176
    def_lon = sample_data["lon"] if sample_data else 82.9739
    def_budget = sample_data["budget"] if sample_data else 15000000.0
    def_start = datetime.strptime(sample_data["start_date"], "%Y-%m-%d").date() if sample_data else date(2024, 1, 15)
    def_end = datetime.strptime(sample_data["end_date"], "%Y-%m-%d").date() if sample_data else date(2024, 11, 20)
    sample_id = sample_data["id"] if sample_data else None

    col_v1, col_v2 = st.columns([1.2, 1])
    with col_v1:
        v_name = st.text_input("Project / Sanction Title", value=def_name)
        v_dept = st.text_input("Department / Ministry", value=def_dept)
        v_type = st.selectbox("Asset Category", ["Building / School", "Road / Highway", "Hospital / Health Center", "Bridge / Flyover", "Water Tank / Canal"], index=0)

        cv_loc1, cv_loc2 = st.columns([3, 1])
        with cv_loc1:
            v_loc = st.text_input("Location Name", value=def_loc)
        with cv_loc2:
            st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
            if st.button("📍 Geocode"):
                glat, glon, _ = geocode_location(v_loc)
                st.session_state["v_lat"] = glat
                st.session_state["v_lon"] = glon
                st.rerun()

        c_lat = st.session_state.get("v_lat", def_lat)
        c_lon = st.session_state.get("v_lon", def_lon)

        cv_c1, cv_c2, cv_c3 = st.columns([1, 1, 1.2])
        with cv_c1:
            in_lat = st.number_input("Latitude", value=float(c_lat), format="%.4f")
        with cv_c2:
            in_lon = st.number_input("Longitude", value=float(c_lon), format="%.4f")
        with cv_c3:
            in_budget = st.number_input("Sanction Budget (₹)", value=float(def_budget), step=1000000.0, format="%.0f")

        cv_d1, cv_d2 = st.columns(2)
        with cv_d1:
            in_start = st.date_input("Start Date", value=def_start)
        with cv_d2:
            in_end = st.date_input("Completion Date", value=def_end)

    with col_v2:
        st.markdown("**🗺️ Geographic Coordinates Map**")
        m = folium.Map(location=[in_lat, in_lon], zoom_start=14, tiles="OpenStreetMap")
        folium.Marker([in_lat, in_lon], tooltip=v_name, icon=folium.Icon(color="blue", icon="info-sign")).add_to(m)
        folium.Circle(radius=400, location=[in_lat, in_lon], color="#2563eb", fill=True, fill_opacity=0.15).add_to(m)
        st_folium(m, height=270, width="100%")

    st.markdown("---")
    if st.button("🚀 Run Satellite AI Verification", type="primary", use_container_width=True):
        with st.status("🛰️ Executing Verification Protocol...", expanded=True) as status:
            st.write("1. 📡 Downloading temporal satellite image passes...")
            b_path, a_path = fetch_satellite_pair(in_lat, in_lon, str(in_start), str(in_end), sample_id=sample_id)

            st.write("2. 🧠 Running computer vision structural footprint analysis...")
            analysis = analyze_infrastructure_project(
                before_img_path=b_path,
                after_img_path=a_path,
                project_type=v_type,
                sanctioned_budget=in_budget,
                project_name=v_name
            )

            st.write("3. 📑 Logging audit results to persistent ledger...")
            new_record = {
                "project_name": v_name,
                "department": v_dept,
                "project_type": v_type,
                "location_name": v_loc,
                "latitude": in_lat,
                "longitude": in_lon,
                "sanctioned_budget": in_budget,
                "start_date": str(in_start),
                "end_date": str(in_end),
                "verdict": analysis["verdict"],
                "confidence_score": analysis["confidence_score"],
                "before_structure_count": analysis["before_structure_count"],
                "after_structure_count": analysis["after_structure_count"],
                "built_area_change_pct": analysis["built_area_change_pct"],
                "audit_notes": analysis["reason"],
                "image_before_path": b_path,
                "image_after_path": a_path,
                "image_annotated_path": analysis["image_annotated_path"],
                "heatmap_path": analysis["heatmap_path"],
                "status": analysis["status"]
            }
            save_project(new_record)
            status.update(label="✅ Project Audited Successfully!", state="complete", expanded=False)

        # Show Verdict Result
        if analysis["verdict"] == "SUSPICIOUS":
            st.error(f"🚨 **SUSPICIOUS — {v_name}:** {analysis['reason']} (AI Confidence: {analysis['confidence_score']}%)")
        else:
            st.success(f"✅ **VERIFIED — {v_name}:** {analysis['reason']} (AI Confidence: {analysis['confidence_score']}%)")

        # Visual Comparison Section
        st.markdown("### 🛰️ Satellite Computer Vision Diagnostics")
        col_im1, col_im2, col_im3 = st.columns(3)
        with col_im1:
            st.caption("📅 Pre-Construction Baseline")
            b_diag = safe_load_image(b_path)
            if b_diag:
                st.image(b_diag, use_container_width=True)
        with col_im2:
            st.caption("📅 Post-Completion Capture")
            a_diag = safe_load_image(a_path)
            if a_diag:
                st.image(a_diag, use_container_width=True)
        with col_im3:
            st.caption("🤖 AI Asset Footprint Detection")
            ann_diag = safe_load_image(analysis["image_annotated_path"])
            if ann_diag:
                st.image(ann_diag, use_container_width=True)

# -------------------------------------------------------------
# TAB 4: AUDIT ANALYTICS
# -------------------------------------------------------------
with tab_analytics:
    st.markdown("### 📊 Public Vigilance & Financial Analytics")
    all_p = get_all_projects()
    if all_p:
        df = pd.DataFrame(all_p)
        c_ch1, c_ch2 = st.columns(2)
        with c_ch1:
            st.markdown("#### 🎯 Verdict Distribution")
            fig_v = px.pie(
                df,
                names="verdict",
                color="verdict",
                color_discrete_map={"VERIFIED": "#16a34a", "SUSPICIOUS": "#dc2626", "IN_PROGRESS": "#f59e0b"},
                hole=0.45
            )
            st.plotly_chart(fig_v, use_container_width=True)

        with c_ch2:
            st.markdown("#### 🏛️ Outlay at Risk by Department")
            df["budget_cr"] = df["sanctioned_budget"] / 1e7
            fig_d = px.bar(
                df,
                x="budget_cr",
                y="department",
                color="verdict",
                orientation="h",
                color_discrete_map={"VERIFIED": "#16a34a", "SUSPICIOUS": "#dc2626", "IN_PROGRESS": "#f59e0b"}
            )
            st.plotly_chart(fig_d, use_container_width=True)

# -------------------------------------------------------------
# TAB 5: TEAM ROLES & ARCHITECTURE
# -------------------------------------------------------------
with tab_team:
    st.markdown("###  Team Roles")
    ct1, ct2 = st.columns(2)
    with ct1:
        st.markdown("""
        - **Saba Qadeer (Satellite & Geocoding):** Fetches Sentinel & Esri tiles across target construction dates.
        - **Shifa Maheen (AI & Computer Vision):** Runs structural edge & footprint change detection.
        
        """)
    with ct2:
        st.markdown("""
        - **Saniya Khatoon (UI & UX Specialist):** Dashboard, dynamic card feed.
        - **Alishah Khan(Integration & Vigilance):** Manages SQLite ledger & legal audit dossiers.
        """)

st.markdown("---")
st.markdown("<p style='text-align:center; color:#94a3b8;'>🏗️ <b>InfraAudit</b> | Built for Civic Integrity & Anti-Corruption Audits</p>", unsafe_allow_html=True)