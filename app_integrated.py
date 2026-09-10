"""
InfraAudit — National Infrastructure Verification Portal.

Satellite earth observation and computer vision verification of publicly funded
infrastructure, with separate access routes for vigilance officers, executing
contractors and citizens.
"""

from datetime import date, datetime

import folium
import pandas as pd
import plotly.express as px
import streamlit as st
from PIL import ImageFile
from streamlit_folium import st_folium

ImageFile.LOAD_TRUNCATED_IMAGES = True

from app_auth import authenticate
from integration import (
    evaluate_payment_gate, generate_audit_dossier, get_all_projects, get_audit_statistics,
    get_case_studies, get_contractor_credibility_index, get_government_portal_contracts,
    get_milestone_claims, get_mplads_summary, get_state_allocation_totals, get_warranty_claims,
    get_whistleblower_reports, init_db, save_project, search_mp_allocations, seed_case_studies,
    seed_sample_projects, submit_milestone_claim, submit_warranty_claim,
    submit_whistleblower_report,
)
from src.member1_fetcher import (
    fetch_satellite_pair, generate_all_samples, geocode_location, get_demo_samples_meta,
)
from src.member2_detector import analyze_infrastructure_project
from src.member3_dashboard import (
    get_custom_ui_theme, render_masthead, render_section, render_stat_tile,
    render_verdict_banner, safe_load_image,
)

PAGES = [
    "Home & Overview",
    "Government Portal",
    "Contractor Portal",
    "Public Citizen Portal",
    "MP Allocation Directory",
]

st.set_page_config(
    page_title="InfraAudit | National Infrastructure Verification Portal",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(get_custom_ui_theme(), unsafe_allow_html=True)

generate_all_samples()
init_db()
seed_sample_projects()
seed_case_studies()

st.markdown(render_masthead(
    title="InfraAudit",
    strapline=(
        "National verification portal for publicly funded infrastructure. Independent satellite "
        "earth observation, computer vision progress audits and constituency-level fund transparency."
    ),
    kicker="Public Infrastructure Vigilance · Earth Observation Verification",
), unsafe_allow_html=True)

page = st.radio("Portal navigation", PAGES, key="nav", horizontal=True, label_visibility="collapsed")


def go_to(destination: str):
    """Switches the active portal page."""
    st.session_state["nav"] = destination
    st.rerun()


def budget_label(amount) -> str:
    """Formats rupee amounts in crore or lakh."""
    if amount is None:
        return "Not published"
    if amount >= 1e7:
        return f"₹{amount / 1e7:.2f} Cr"
    return f"₹{amount / 1e5:.2f} L"


def render_login(title: str, description: str, role: str, session_key: str, hint: str):
    """Renders a portal login form and returns True once authenticated."""
    if st.session_state.get(session_key):
        header, action = st.columns([4, 1])
        with header:
            st.markdown(
                f'<span class="badge-verified">Signed in</span> &nbsp; '
                f'<b>{st.session_state[session_key]}</b>',
                unsafe_allow_html=True,
            )
        with action:
            if st.button("Sign out", key=f"logout_{session_key}", use_container_width=True):
                st.session_state[session_key] = ""
                st.rerun()
        st.markdown("---")
        return True

    _, panel, _ = st.columns([1, 2, 1])
    with panel:
        st.markdown('<div class="login-panel">', unsafe_allow_html=True)
        st.markdown('<div class="crest">Restricted access</div>', unsafe_allow_html=True)
        st.markdown(f"#### {title}")
        st.caption(description)
        with st.form(f"form_{session_key}"):
            username = st.text_input("User ID")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Sign in", type="primary", use_container_width=True)
        if submitted:
            if authenticate(role, username, password):
                st.session_state[session_key] = username
                st.rerun()
            else:
                st.error("Access denied. The credentials provided are not recognised.")
        st.caption(hint)
        st.markdown("</div>", unsafe_allow_html=True)
    return False


def run_satellite_audit(record: dict, sample_id: str = None, work_order_id: str = "", source_portal: str = ""):
    """Runs the earth observation audit pipeline and writes the result to the ledger."""
    with st.status(f"Auditing {record['project_name']}...", expanded=True) as status:
        st.write("Retrieving temporal satellite passes...")
        before_path, after_path = fetch_satellite_pair(
            record["latitude"], record["longitude"], record["start_date"], record["end_date"],
            sample_id=sample_id,
        )

        st.write("Running structural footprint change detection...")
        analysis = analyze_infrastructure_project(
            before_img_path=before_path,
            after_img_path=after_path,
            project_type=record["project_type"],
            sanctioned_budget=record["sanctioned_budget"],
            project_name=record["project_name"],
        )

        st.write("Writing the outcome to the public surveillance ledger...")
        notes = analysis["reason"]
        if work_order_id:
            notes = f"[Work order {work_order_id} | Source: {source_portal}] {notes}"
        save_project({
            **record,
            "verdict": analysis["verdict"],
            "confidence_score": analysis["confidence_score"],
            "before_structure_count": analysis["before_structure_count"],
            "after_structure_count": analysis["after_structure_count"],
            "built_area_change_pct": analysis["built_area_change_pct"],
            "audit_notes": notes,
            "image_before_path": before_path,
            "image_after_path": after_path,
            "image_annotated_path": analysis["image_annotated_path"],
            "heatmap_path": analysis["heatmap_path"],
            "status": analysis["status"],
        })
        status.update(label="Audit complete", state="complete", expanded=False)

    st.markdown(render_verdict_banner(
        analysis["verdict"],
        record["project_name"],
        analysis["reason"],
        [
            f"Confidence {analysis['confidence_score']}%",
            f"Built-up change +{analysis['built_area_change_pct']}%",
            f"Sanctioned outlay {budget_label(record['sanctioned_budget'])}",
        ],
    ), unsafe_allow_html=True)
    return analysis, before_path, after_path


# -------------------------------------------------------------------------
# Home & overview
# -------------------------------------------------------------------------
if page == "Home & Overview":
    stats = get_audit_statistics()
    mplads = get_mplads_summary()

    tiles = st.columns(4)
    figures = [
        ("Works scrutinised", f"{stats['total_projects']}", "Contracts in the audit ledger"),
        ("Public outlay monitored", f"₹{stats['total_budget'] / 1e7:.2f} Cr", "Sanctioned value under review"),
        ("Capital at risk", f"₹{stats['flagged_budget'] / 1e7:.2f} Cr", f"{stats['suspicious_count']} works flagged"),
        ("Constituency funds tracked", f"₹{mplads['total_allocated_crore']:,.2f} Cr",
         f"{mplads['member_count']} constituencies"),
    ]
    for column, (label, value, note) in zip(tiles, figures):
        with column:
            st.markdown(render_stat_tile(label, value, note), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(render_section(
        "Access routes",
        "Each stakeholder group enters the platform through its own portal.",
    ), unsafe_allow_html=True)

    route_columns = st.columns(3)
    routes = [
        ("Government Vigilance Portal", "Protected access for MoSPI, CAG and vigilance officers. "
                                        "Payment gatekeeping, satellite audits, contractor credibility and dossiers.",
         "Government Portal"),
        ("Contractor Execution Portal", "Protected access for executing agencies. Milestone claims, GST invoices, "
                                        "geotagged weekly progress and defect liability bonds.", "Contractor Portal"),
        ("Public Citizen Portal", "Open access for citizens. Anonymous reporting, defect liability claims and the "
                                  "public surveillance ledger.", "Public Citizen Portal"),
    ]
    for column, (title, description, destination) in zip(route_columns, routes):
        with column:
            st.markdown(
                f'<div class="gov-card"><h4>{title}</h4><div class="meta">{description}</div></div>',
                unsafe_allow_html=True,
            )
            if st.button(f"Enter {title.split()[0].lower()} portal", key=f"route_{destination}",
                         use_container_width=True):
                go_to(destination)

    st.markdown(render_section(
        "Documented execution failures",
        "Case studies of publicly reported infrastructure delays that motivated this platform.",
    ), unsafe_allow_html=True)

    for study in get_case_studies():
        with st.container(border=True):
            heading, marker = st.columns([4, 1])
            with heading:
                st.markdown(f"#### {study['title']}")
                st.caption(f"{study['location_name']} · {study['asset_type']} · {study['source']}")
            with marker:
                st.markdown(
                    f'<div style="text-align:right"><span class="badge-suspicious">'
                    f'{study["delay_summary"]}</span></div>',
                    unsafe_allow_html=True,
                )
            st.write(f"**Promise and delay:** {study['promise_and_delay']}")
            st.write(f"**Human impact:** {study['human_impact']}")
            if study["sanctioned_budget"]:
                st.caption(f"Recorded expenditure: {budget_label(study['sanctioned_budget'])}")

# -------------------------------------------------------------------------
# Government vigilance portal
# -------------------------------------------------------------------------
elif page == "Government Portal":
    st.markdown(render_section(
        "Government Vigilance Portal",
        "Ministry of Statistics & Programme Implementation · Comptroller and Auditor General · State vigilance.",
    ), unsafe_allow_html=True)

    if render_login(
        title="Vigilance officer sign in",
        description="Authorised officers of MoSPI, CAG and state vigilance directorates only.",
        role="government",
        session_key="gov_user",
        hint="Demonstration credentials: admin / mospi2026",
    ):
        gate_tab, engine_tab, credibility_tab, dossier_tab = st.tabs([
            "Payment gatekeeper", "Satellite verification engine", "Contractor credibility", "Audit dossiers",
        ])

        with gate_tab:
            st.markdown(render_section(
                "Three-way payment gatekeeper",
                "A claim is released only when the contractor declaration, the satellite audit and citizen "
                "oversight agree.",
            ), unsafe_allow_html=True)

            claims = get_milestone_claims()
            if not claims:
                st.info("No contractor milestone claims have been submitted yet.")
            else:
                audited = {p["project_name"]: p for p in get_all_projects()}
                contracts = {c["work_order_id"]: c for c in get_government_portal_contracts()}
                open_flags = get_whistleblower_reports()

                for claim in claims:
                    contract = contracts.get(claim["work_order_id"])
                    project = audited.get(contract["project_name"]) if contract else None
                    flags = sum(
                        1 for report in open_flags
                        if claim["work_order_id"].lower() in report["project_reference"].lower()
                        and report["status"] == "UNDER_REVIEW"
                    )
                    gate = evaluate_payment_gate(claim, project, flags)

                    with st.container(border=True):
                        heading, decision = st.columns([3, 1])
                        with heading:
                            st.markdown(f"#### {claim['work_order_id']} — {claim['milestone']}")
                            st.caption(
                                f"{claim['contractor_name']} · GST invoice {claim['gst_invoice_no']} · "
                                f"claim {budget_label(claim['claim_amount'])}"
                            )
                        with decision:
                            badge = "badge-verified" if gate["cleared"] else "badge-suspicious"
                            st.markdown(
                                f'<div style="text-align:right"><span class="{badge}">{gate["decision"]}</span></div>',
                                unsafe_allow_html=True,
                            )
                        for check in gate["checks"]:
                            mark = "PASS" if check["passed"] else "FAIL"
                            st.markdown(
                                f'<div class="audit-callout"><b>{mark} · {check["name"]}</b><br>{check["detail"]}</div>',
                                unsafe_allow_html=True,
                            )

        with engine_tab:
            st.markdown(render_section(
                "Satellite verification engine",
                "Audit an incoming completion claim or submit a new work for verification.",
            ), unsafe_allow_html=True)

            st.markdown("##### Completion claims awaiting audit")
            for contract in get_government_portal_contracts():
                with st.container(border=True):
                    heading, amount = st.columns([3, 1])
                    with heading:
                        st.markdown(f"#### {contract['project_name']}")
                        st.caption(
                            f"{contract['work_order_id']} · {contract['source_portal']} · "
                            f"{contract['contractor_name']} · {contract['location_name']}"
                        )
                    with amount:
                        st.markdown(
                            f'<div style="text-align:right"><b>{contract["payment_claimed"]}</b><br>'
                            f'<span style="color:#64748B;font-size:0.8rem">Claimed '
                            f'{contract["completion_claimed_date"]}</span></div>',
                            unsafe_allow_html=True,
                        )
                    if st.button("Run satellite audit", key=f"audit_{contract['work_order_id']}", type="primary"):
                        run_satellite_audit(
                            {
                                "project_name": contract["project_name"],
                                "department": contract["department"],
                                "project_type": contract["project_type"],
                                "location_name": contract["location_name"],
                                "latitude": contract["latitude"],
                                "longitude": contract["longitude"],
                                "sanctioned_budget": contract["sanctioned_budget"],
                                "start_date": contract["start_date"],
                                "end_date": contract["end_date"],
                            },
                            sample_id=contract["sample_id"],
                            work_order_id=contract["work_order_id"],
                            source_portal=contract["source_portal"],
                        )

            st.markdown("---")
            st.markdown("##### Verify a new work")

            samples = {f"{s['name']}": s for s in get_demo_samples_meta()}
            selected = st.selectbox("Ground-truth preset", ["Custom entry"] + list(samples))
            preset = samples.get(selected)

            details, map_column = st.columns([1.2, 1])
            with details:
                name = st.text_input("Sanction title", value=preset["name"] if preset else "Primary school wing")
                department = st.text_input(
                    "Department or ministry",
                    value=preset["department"] if preset else "Education & School Infrastructure",
                )
                asset_type = st.selectbox("Asset category", [
                    "Building / School", "Road / Highway", "Hospital / Health Center",
                    "Bridge / Flyover", "Water Tank / Canal",
                ])

                location_input, geocode_button = st.columns([3, 1])
                with location_input:
                    location = st.text_input(
                        "Location",
                        value=preset["location"] if preset else "Rampur Sector 4, Varanasi, Uttar Pradesh",
                    )
                with geocode_button:
                    st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
                    if st.button("Geocode"):
                        found_lat, found_lon, _ = geocode_location(location)
                        st.session_state["v_lat"] = found_lat
                        st.session_state["v_lon"] = found_lon
                        st.rerun()

                default_lat = st.session_state.get("v_lat", preset["lat"] if preset else 25.3176)
                default_lon = st.session_state.get("v_lon", preset["lon"] if preset else 82.9739)

                coord_a, coord_b, coord_c = st.columns([1, 1, 1.2])
                with coord_a:
                    latitude = st.number_input("Latitude", value=float(default_lat), format="%.4f")
                with coord_b:
                    longitude = st.number_input("Longitude", value=float(default_lon), format="%.4f")
                with coord_c:
                    sanctioned = st.number_input(
                        "Sanctioned budget (₹)",
                        value=float(preset["budget"] if preset else 15000000.0),
                        step=1000000.0, format="%.0f",
                    )

                date_a, date_b = st.columns(2)
                with date_a:
                    start = st.date_input(
                        "Start date",
                        value=datetime.strptime(preset["start_date"], "%Y-%m-%d").date() if preset else date(2024, 1, 15),
                    )
                with date_b:
                    end = st.date_input(
                        "Completion date",
                        value=datetime.strptime(preset["end_date"], "%Y-%m-%d").date() if preset else date(2024, 11, 20),
                    )

            with map_column:
                st.markdown("**Site location**")
                site_map = folium.Map(location=[latitude, longitude], zoom_start=14, tiles="OpenStreetMap")
                folium.Marker([latitude, longitude], tooltip=name).add_to(site_map)
                folium.Circle(radius=400, location=[latitude, longitude], color="#0A192F",
                              fill=True, fill_opacity=0.12).add_to(site_map)
                st_folium(site_map, height=270, width="100%")

            if st.button("Run verification", type="primary", use_container_width=True):
                analysis, before_path, after_path = run_satellite_audit(
                    {
                        "project_name": name,
                        "department": department,
                        "project_type": asset_type,
                        "location_name": location,
                        "latitude": latitude,
                        "longitude": longitude,
                        "sanctioned_budget": sanctioned,
                        "start_date": str(start),
                        "end_date": str(end),
                    },
                    sample_id=preset["id"] if preset else None,
                )

                evidence = st.columns(3)
                captions = [
                    ("Pre-construction baseline", before_path),
                    ("Post-completion capture", after_path),
                    ("Detected asset footprint", analysis["image_annotated_path"]),
                ]
                for column, (caption, path) in zip(evidence, captions):
                    with column:
                        st.caption(caption)
                        image = safe_load_image(path)
                        if image:
                            st.image(image, use_container_width=True)

        with credibility_tab:
            st.markdown(render_section(
                "Contractor Credibility Index",
                "Share of each executing agency's audited works that were confirmed on the ground.",
            ), unsafe_allow_html=True)

            index = get_contractor_credibility_index()
            frame = pd.DataFrame(index)
            frame["Capital at risk (₹ Cr)"] = (frame["capital_at_risk"] / 1e7).round(2)
            st.dataframe(
                frame[["contractor_name", "works", "verified", "flagged", "cci_score", "rating",
                       "Capital at risk (₹ Cr)"]].rename(columns={
                           "contractor_name": "Executing agency",
                           "works": "Works audited",
                           "verified": "Confirmed",
                           "flagged": "Flagged",
                           "cci_score": "CCI score",
                           "rating": "Rating",
                       }),
                use_container_width=True, hide_index=True,
            )

        with dossier_tab:
            st.markdown(render_section(
                "Investigation dossiers",
                "Export the formal audit record for any work in the ledger.",
            ), unsafe_allow_html=True)

            for project in get_all_projects():
                with st.container(border=True):
                    heading, download = st.columns([3, 1])
                    with heading:
                        st.markdown(f"**{project['project_name']}**")
                        st.caption(
                            f"{project['department']} · {project['location_name']} · "
                            f"verdict {project['verdict']}"
                        )
                    with download:
                        st.download_button(
                            "Download dossier",
                            data=generate_audit_dossier(project),
                            file_name=f"audit_dossier_{project['id']}.md",
                            mime="text/markdown",
                            key=f"dossier_{project['id']}",
                            use_container_width=True,
                        )

# -------------------------------------------------------------------------
# Contractor execution portal
# -------------------------------------------------------------------------
elif page == "Contractor Portal":
    st.markdown(render_section(
        "Contractor Execution Portal",
        "Milestone claims, tax invoices, geotagged weekly progress and defect liability bonds.",
    ), unsafe_allow_html=True)

    if render_login(
        title="Contractor sign in",
        description="Registered executing agencies holding an active government work order.",
        role="contractor",
        session_key="contractor_user",
        hint="Demonstration credentials: contractor / pass123",
    ):
        claim_tab, progress_tab, bond_tab, history_tab = st.tabs([
            "Milestone claim", "Weekly geotagged progress", "Defect liability bond", "My claims",
        ])

        contracts = {c["work_order_id"]: c for c in get_government_portal_contracts()}

        with claim_tab:
            st.markdown(render_section(
                "Submit a milestone claim",
                "Every claim is held until an independent satellite audit confirms physical execution.",
            ), unsafe_allow_html=True)

            with st.form("milestone_claim"):
                work_order = st.selectbox("Work order", list(contracts))
                contract = contracts[work_order]
                st.caption(f"{contract['project_name']} · {contract['location_name']}")

                field_a, field_b = st.columns(2)
                with field_a:
                    milestone = st.selectbox("Milestone", [
                        "Stage 1 — Site mobilisation", "Stage 2 — Substructure",
                        "Stage 3 — Superstructure", "Stage 4 — Completion & handover",
                    ])
                    claim_amount = st.number_input("Claim amount (₹)", value=1000000.0, step=100000.0, format="%.0f")
                with field_b:
                    gst_invoice = st.text_input("GST invoice number", value="GST/2026/0001")
                    progress = st.slider("Declared execution (%)", 0, 100, 100)

                geo_a, geo_b = st.columns(2)
                with geo_a:
                    claim_lat = st.number_input("Site latitude", value=float(contract["latitude"]), format="%.4f")
                with geo_b:
                    claim_lon = st.number_input("Site longitude", value=float(contract["longitude"]), format="%.4f")

                remarks = st.text_area("Remarks")
                if st.form_submit_button("Submit claim", type="primary"):
                    submit_milestone_claim({
                        "work_order_id": work_order,
                        "contractor_name": contract["contractor_name"],
                        "milestone": milestone,
                        "claim_amount": claim_amount,
                        "gst_invoice_no": gst_invoice,
                        "progress_pct": float(progress),
                        "geotag_latitude": claim_lat,
                        "geotag_longitude": claim_lon,
                        "remarks": remarks,
                    })
                    st.success("Claim submitted and queued for independent satellite verification.")

        with progress_tab:
            st.markdown(render_section(
                "Weekly geotagged progress",
                "Log the current execution position for the running week.",
            ), unsafe_allow_html=True)

            with st.form("weekly_progress"):
                work_order = st.selectbox("Work order", list(contracts), key="progress_work_order")
                contract = contracts[work_order]
                progress = st.slider("Execution this week (%)", 0, 100, 40, key="weekly_pct")
                note = st.text_area("Site note", placeholder="Earthwork completed on the northern approach.")
                if st.form_submit_button("Log progress", type="primary"):
                    submit_milestone_claim({
                        "work_order_id": work_order,
                        "contractor_name": contract["contractor_name"],
                        "milestone": f"Weekly progress update — {date.today().isoformat()}",
                        "claim_amount": 0.0,
                        "gst_invoice_no": "NOT APPLICABLE",
                        "progress_pct": float(progress),
                        "geotag_latitude": contract["latitude"],
                        "geotag_longitude": contract["longitude"],
                        "remarks": note,
                        "status": "PROGRESS_LOGGED",
                    })
                    st.success("Weekly geotagged progress recorded.")

        with bond_tab:
            st.markdown(render_section(
                "Five-year defect liability bond",
                "Upload the warranty bond covering the defect liability period of a completed asset.",
            ), unsafe_allow_html=True)

            with st.form("dlp_bond"):
                work_order = st.selectbox("Work order", list(contracts), key="bond_work_order")
                contract = contracts[work_order]
                bond_reference = st.text_input("Bond reference", value="DLP/BOND/2026/001")
                bond_file = st.file_uploader("Bond document (PDF)", type=["pdf"])
                if st.form_submit_button("Register bond", type="primary"):
                    if bond_file is None:
                        st.error("Attach the signed bond document before registering.")
                    else:
                        submit_milestone_claim({
                            "work_order_id": work_order,
                            "contractor_name": contract["contractor_name"],
                            "milestone": "Defect liability bond registration",
                            "claim_amount": 0.0,
                            "gst_invoice_no": "NOT APPLICABLE",
                            "progress_pct": 100.0,
                            "geotag_latitude": contract["latitude"],
                            "geotag_longitude": contract["longitude"],
                            "dlp_bond_reference": bond_reference,
                            "remarks": f"Bond document {bond_file.name} registered for a five-year liability period.",
                            "status": "BOND_REGISTERED",
                        })
                        st.success(f"Bond {bond_reference} registered for a five-year defect liability period.")

        with history_tab:
            submissions = get_milestone_claims()
            if not submissions:
                st.info("No submissions recorded yet.")
            else:
                frame = pd.DataFrame(submissions)
                frame["Claim (₹ Cr)"] = (frame["claim_amount"] / 1e7).round(3)
                st.dataframe(
                    frame[["created_at", "work_order_id", "milestone", "gst_invoice_no",
                           "progress_pct", "Claim (₹ Cr)", "status"]].rename(columns={
                               "created_at": "Submitted",
                               "work_order_id": "Work order",
                               "milestone": "Milestone",
                               "gst_invoice_no": "GST invoice",
                               "progress_pct": "Declared %",
                               "status": "Status",
                           }),
                    use_container_width=True, hide_index=True,
                )

# -------------------------------------------------------------------------
# Public citizen portal
# -------------------------------------------------------------------------
elif page == "Public Citizen Portal":
    st.markdown(render_section(
        "Public Citizen Portal",
        "Open to every citizen. No registration is required to report a ghost asset or a defect.",
    ), unsafe_allow_html=True)

    report_tab, warranty_tab, ledger_tab = st.tabs([
        "Anonymous report", "Defect liability claim", "Public surveillance ledger",
    ])

    with report_tab:
        st.markdown(render_section(
            "Report a suspected ghost asset",
            "Reports are recorded anonymously and block payment release on the referenced work order.",
        ), unsafe_allow_html=True)

        with st.form("whistleblower"):
            project_reference = st.text_input("Project or work order reference", placeholder="PMGSY/MP/2024/RD-4102")
            location = st.text_input("Location", placeholder="Village, district, state")
            category = st.selectbox("Nature of the complaint", [
                "Asset does not exist", "Substandard construction", "Work abandoned midway",
                "Completion falsely certified", "Other irregularity",
            ])
            description = st.text_area("What did you observe?")
            if st.form_submit_button("Lodge report", type="primary"):
                if not (project_reference and location and description):
                    st.error("Provide the work reference, the location and a description.")
                else:
                    reference = submit_whistleblower_report({
                        "project_reference": project_reference,
                        "location_name": location,
                        "category": category,
                        "description": description,
                    })
                    st.success(f"Report lodged anonymously. Tracking reference: {reference}")

    with warranty_tab:
        st.markdown(render_section(
            "Five-year defect liability claim",
            "Public assets carry a five-year contractor warranty. Report defects within that window.",
        ), unsafe_allow_html=True)

        with st.form("warranty"):
            asset_name = st.text_input("Asset", placeholder="Bitumen Highway Link Road 12B")
            location = st.text_input("Location", placeholder="Village, district, state", key="dlp_location")
            defect_type = st.selectbox("Defect", [
                "Potholes and surface failure", "Structural cracking", "Drainage failure",
                "Collapsed or missing railing", "Other defect",
            ])
            commissioned_on = st.date_input("Asset commissioned on", value=date(2024, 10, 15))
            description = st.text_area("Describe the defect", key="dlp_description")
            if st.form_submit_button("Lodge claim", type="primary"):
                if not (asset_name and location and description):
                    st.error("Provide the asset, the location and a description of the defect.")
                else:
                    within_dlp = (date.today() - commissioned_on).days <= 5 * 365
                    reference = submit_warranty_claim({
                        "asset_name": asset_name,
                        "location_name": location,
                        "defect_type": defect_type,
                        "commissioned_on": str(commissioned_on),
                        "within_dlp": within_dlp,
                        "description": description,
                    })
                    if within_dlp:
                        st.success(
                            f"Claim lodged within the defect liability period. Tracking reference: {reference}"
                        )
                    else:
                        st.warning(
                            f"Recorded as reference {reference}, but the asset is beyond its five-year "
                            "defect liability period."
                        )

    with ledger_tab:
        st.markdown(render_section(
            "Public surveillance ledger",
            "Every audited work, with its satellite evidence and verdict.",
        ), unsafe_allow_html=True)

        search_column, filter_column = st.columns([3, 1])
        with search_column:
            query = st.text_input("Search by work, location or department", placeholder="School, Varanasi, PWD")
        with filter_column:
            verdict_filter = st.selectbox("Verdict", ["All", "Flagged", "Confirmed", "In progress"])

        projects = get_all_projects()
        verdict_map = {"Flagged": "SUSPICIOUS", "Confirmed": "VERIFIED", "In progress": "IN_PROGRESS"}
        if verdict_filter in verdict_map:
            projects = [p for p in projects if p["verdict"] == verdict_map[verdict_filter]]
        if query:
            needle = query.lower()
            projects = [
                p for p in projects
                if needle in p["project_name"].lower()
                or needle in p["location_name"].lower()
                or needle in p["department"].lower()
            ]

        columns = st.columns(3)
        for index, project in enumerate(projects):
            with columns[index % 3]:
                with st.container(border=True):
                    badge = {
                        "VERIFIED": ("badge-verified", "Confirmed built"),
                        "IN_PROGRESS": ("badge-progress", "In progress"),
                    }.get(project["verdict"], ("badge-suspicious", "Flagged"))
                    st.markdown(
                        f'<div style="display:flex;justify-content:space-between;align-items:center;">'
                        f'<span class="{badge[0]}">{badge[1]}</span>'
                        f'<b>{budget_label(project["sanctioned_budget"])}</b></div>',
                        unsafe_allow_html=True,
                    )
                    image = safe_load_image(project.get("image_after_path") or project.get("image_before_path"))
                    if image:
                        st.image(image, use_container_width=True)
                    st.markdown(f"#### {project['project_name']}")
                    st.caption(f"{project['department']} · {project['location_name']}")
                    st.markdown(f"""
                    <div class="metric-chip-row">
                        <div class="metric-chip-item">
                            <div class="metric-chip-val">{project['confidence_score']}%</div>
                            <div class="metric-chip-lbl">Confidence</div>
                        </div>
                        <div class="metric-chip-item">
                            <div class="metric-chip-val">+{project['built_area_change_pct']}%</div>
                            <div class="metric-chip-lbl">Built-up change</div>
                        </div>
                        <div class="metric-chip-item">
                            <div class="metric-chip-val">{project['after_structure_count']}</div>
                            <div class="metric-chip-lbl">Structures</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    st.markdown(f"<div class='audit-callout'>{project['audit_notes']}</div>", unsafe_allow_html=True)

                    with st.expander("Satellite evidence"):
                        before_column, after_column = st.columns(2)
                        with before_column:
                            st.caption(f"Baseline {project['start_date']}")
                            before_image = safe_load_image(project.get("image_before_path"))
                            if before_image:
                                st.image(before_image, use_container_width=True)
                        with after_column:
                            st.caption(f"Post-completion {project['end_date']}")
                            after_image = safe_load_image(project.get("image_after_path"))
                            if after_image:
                                st.image(after_image, use_container_width=True)

        st.markdown("---")
        st.markdown("##### Citizen submissions on record")
        submission_a, submission_b = st.columns(2)
        with submission_a:
            reports = get_whistleblower_reports()
            st.caption(f"Anonymous reports: {len(reports)}")
            if reports:
                st.dataframe(
                    pd.DataFrame(reports)[["reference_code", "project_reference", "category", "status"]],
                    use_container_width=True, hide_index=True,
                )
        with submission_b:
            claims = get_warranty_claims()
            st.caption(f"Defect liability claims: {len(claims)}")
            if claims:
                st.dataframe(
                    pd.DataFrame(claims)[["reference_code", "asset_name", "defect_type", "status"]],
                    use_container_width=True, hide_index=True,
                )

# -------------------------------------------------------------------------
# MP allocation directory
# -------------------------------------------------------------------------
elif page == "MP Allocation Directory":
    summary = get_mplads_summary()
    st.markdown(render_section(
        "Members of Parliament Local Area Development allocation register",
        summary["source"],
    ), unsafe_allow_html=True)

    tiles = st.columns(3)
    figures = [
        ("Constituencies on record", f"{summary['member_count']}", "Lok Sabha seats"),
        ("Total allocated", f"₹{summary['total_allocated_crore']:,.2f} Cr", "Across all constituencies"),
        ("States and union territories", f"{summary['state_count']}", "Covered by the register"),
    ]
    for column, (label, value, note) in zip(tiles, figures):
        with column:
            st.markdown(render_stat_tile(label, value, note), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    search_column, state_column = st.columns([3, 1.4])
    with search_column:
        query = st.text_input("Search by member, constituency or state",
                              placeholder="Narendra Modi, Varanasi, Kerala")
    with state_column:
        state = st.selectbox("State or union territory", ["All"] + summary["states"])

    members = search_mp_allocations(query, "" if state == "All" else state)
    frame = pd.DataFrame(members)
    frame["Allocated (₹ Cr)"] = (frame["allocated_amount"] / 1e7).round(4)
    st.caption(f"{len(members)} of {summary['member_count']} constituencies shown.")
    st.dataframe(
        frame[["sr_no", "mp_name", "constituency", "state", "Allocated (₹ Cr)"]].rename(columns={
            "sr_no": "Sr. no.",
            "mp_name": "Member of Parliament",
            "constituency": "Constituency",
            "state": "State / UT",
        }),
        use_container_width=True, hide_index=True, height=430,
    )

    st.markdown(render_section("Allocation by state", "Total constituency development funds per state."),
                unsafe_allow_html=True)
    totals = pd.DataFrame(get_state_allocation_totals())
    totals["allocated_crore"] = (totals["allocated_amount"] / 1e7).round(2)
    chart = px.bar(
        totals.sort_values("allocated_crore"),
        x="allocated_crore", y="state", orientation="h",
        labels={"allocated_crore": "Allocated (₹ Cr)", "state": ""},
        color_discrete_sequence=["#0A192F"],
    )
    chart.update_layout(height=760, plot_bgcolor="#FFFFFF", paper_bgcolor="#FFFFFF", margin=dict(l=0, r=0, t=10, b=0))
    st.plotly_chart(chart, use_container_width=True)

st.markdown(
    '<div class="gov-footer">InfraAudit · Independent verification of publicly funded infrastructure</div>',
    unsafe_allow_html=True,
)
