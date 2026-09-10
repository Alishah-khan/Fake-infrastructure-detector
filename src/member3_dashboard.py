"""
Module: Interface Design System

Government portal design system: colour tokens, typography, navigation bar,
publication-style cards and verification result banners.
"""

from pathlib import Path

from PIL import Image, ImageFile

ImageFile.LOAD_TRUNCATED_IMAGES = True

NAVY = "#0A192F"
SLATE = "#1E293B"
GOLD = "#D97706"
EMERALD = "#059669"
CRIMSON = "#DC2626"
CANVAS = "#FAF8F4"


def get_custom_ui_theme():
    """Returns the portal stylesheet."""
    return f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Source+Serif+4:wght@600;700&family=Inter:wght@400;500;600;700&display=swap');

    :root {{
        --navy: {NAVY};
        --slate: {SLATE};
        --gold: {GOLD};
        --emerald: {EMERALD};
        --crimson: {CRIMSON};
        --canvas: {CANVAS};
        --line: #DDD6CA;
    }}

    html, body, [class*="css"] {{
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }}
    .stApp {{
        background: var(--canvas);
    }}
    .block-container {{
        padding-top: 1.6rem;
        max-width: 1280px;
    }}
    h1, h2, h3, h4 {{
        font-family: 'Source Serif 4', Georgia, serif;
        color: var(--navy);
        letter-spacing: -0.01em;
    }}

    /* Masthead */
    .gov-masthead {{
        background: var(--navy);
        border-bottom: 4px solid var(--gold);
        border-radius: 4px 4px 0 0;
        padding: 22px 30px 20px 30px;
        color: #F8FAFC;
    }}
    .gov-masthead .emblem {{
        font-size: 0.72rem;
        letter-spacing: 0.18em;
        text-transform: uppercase;
        color: #94A3B8;
        margin-bottom: 6px;
    }}
    .gov-masthead h1 {{
        color: #FFFFFF;
        font-size: 2rem;
        margin: 0 0 6px 0;
    }}
    .gov-masthead .strapline {{
        color: #CBD5E1;
        font-size: 0.95rem;
        max-width: 780px;
        line-height: 1.55;
        margin: 0;
    }}

    /* Navigation bar */
    div[role="radiogroup"] {{
        background: var(--slate);
        border-radius: 0 0 4px 4px;
        padding: 4px 10px;
        margin-bottom: 24px;
        gap: 4px;
    }}
    div[role="radiogroup"] > label {{
        padding: 10px 18px;
        margin: 0;
        border-bottom: 3px solid transparent;
    }}
    div[role="radiogroup"] > label > div:first-child {{ display: none; }}
    div[role="radiogroup"] > label p {{
        color: #CBD5E1;
        font-weight: 600;
        font-size: 0.88rem;
        letter-spacing: 0.01em;
    }}
    div[role="radiogroup"] > label:hover p {{ color: #FFFFFF; }}
    div[role="radiogroup"] > label:has(input:checked) {{
        border-bottom-color: var(--gold);
        background: rgba(255, 255, 255, 0.06);
    }}
    div[role="radiogroup"] > label:has(input:checked) p {{ color: #FFFFFF; }}

    /* Section headings */
    .section-rule {{
        border-left: 4px solid var(--gold);
        padding-left: 14px;
        margin: 6px 0 18px 0;
    }}
    .section-rule h3 {{
        margin: 0;
        font-size: 1.35rem;
    }}
    .section-rule p {{
        margin: 4px 0 0 0;
        color: #64748B;
        font-size: 0.9rem;
    }}

    /* Publication-style cards */
    .gov-card {{
        background: #FFFFFF;
        border: 1px solid var(--line);
        border-top: 3px solid var(--navy);
        border-radius: 4px;
        padding: 18px 20px;
        margin-bottom: 16px;
    }}
    .gov-card h4 {{
        margin: 0 0 6px 0;
        font-size: 1.05rem;
    }}
    .gov-card .meta {{
        color: #64748B;
        font-size: 0.82rem;
        margin-bottom: 10px;
    }}
    .gov-card.is-flagged {{ border-top-color: var(--crimson); }}
    .gov-card.is-clear {{ border-top-color: var(--emerald); }}

    .stat-tile {{
        background: #FFFFFF;
        border: 1px solid var(--line);
        border-radius: 4px;
        padding: 16px 18px;
        height: 100%;
    }}
    .stat-tile .label {{
        font-size: 0.72rem;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        color: #64748B;
    }}
    .stat-tile .value {{
        font-family: 'Source Serif 4', Georgia, serif;
        font-size: 1.75rem;
        font-weight: 700;
        color: var(--navy);
        line-height: 1.2;
        margin-top: 4px;
    }}
    .stat-tile .note {{
        font-size: 0.8rem;
        color: #64748B;
    }}

    /* Status badges */
    .badge-verified, .badge-suspicious, .badge-progress, .badge-neutral {{
        display: inline-block;
        padding: 3px 10px;
        border-radius: 3px;
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.06em;
        text-transform: uppercase;
    }}
    .badge-verified {{ background: #ECFDF5; color: var(--emerald); border: 1px solid #A7F3D0; }}
    .badge-suspicious {{ background: #FEF2F2; color: var(--crimson); border: 1px solid #FECACA; }}
    .badge-progress {{ background: #FFFBEB; color: var(--gold); border: 1px solid #FDE68A; }}
    .badge-neutral {{ background: #F1F5F9; color: var(--slate); border: 1px solid #E2E8F0; }}

    .metric-chip-row {{
        display: flex;
        justify-content: space-between;
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 4px;
        padding: 8px 12px;
        margin: 12px 0;
    }}
    .metric-chip-item {{ text-align: center; }}
    .metric-chip-val {{ font-size: 0.95rem; font-weight: 700; color: var(--slate); }}
    .metric-chip-lbl {{ font-size: 0.68rem; color: #64748B; text-transform: uppercase; letter-spacing: 0.06em; }}

    .audit-callout {{
        font-size: 0.84rem;
        color: #334155;
        background: #F8FAFC;
        border-left: 3px solid var(--gold);
        padding: 9px 12px;
        margin-bottom: 12px;
        line-height: 1.45;
    }}

    /* Verification result banners */
    .verdict-banner {{
        border-radius: 4px;
        padding: 22px 26px;
        margin: 18px 0;
        color: #F8FAFC;
        background: var(--navy);
        border-left: 6px solid var(--gold);
    }}
    .verdict-banner.is-flagged {{ border-left-color: var(--crimson); }}
    .verdict-banner.is-clear {{ border-left-color: var(--emerald); }}
    .verdict-banner .kicker {{
        font-size: 0.72rem;
        letter-spacing: 0.16em;
        text-transform: uppercase;
        color: #94A3B8;
    }}
    .verdict-banner h2 {{
        color: #FFFFFF;
        font-size: 1.5rem;
        margin: 6px 0 8px 0;
    }}
    .verdict-banner p {{
        color: #CBD5E1;
        margin: 0 0 14px 0;
        line-height: 1.55;
    }}
    .verdict-facts {{ display: flex; gap: 10px; flex-wrap: wrap; }}
    .verdict-facts span {{
        background: rgba(255, 255, 255, 0.08);
        border: 1px solid rgba(255, 255, 255, 0.18);
        color: #E2E8F0;
        padding: 6px 14px;
        border-radius: 3px;
        font-size: 0.82rem;
        font-weight: 600;
    }}

    /* Login panel */
    .login-panel {{
        background: #FFFFFF;
        border: 1px solid var(--line);
        border-top: 3px solid var(--gold);
        border-radius: 4px;
        padding: 8px 26px 4px 26px;
    }}
    .login-panel .crest {{
        font-size: 0.72rem;
        letter-spacing: 0.16em;
        text-transform: uppercase;
        color: var(--gold);
        font-weight: 700;
    }}

    .gov-footer {{
        text-align: center;
        color: #94A3B8;
        font-size: 0.82rem;
        padding: 22px 0 8px 0;
        border-top: 1px solid var(--line);
        margin-top: 30px;
    }}
    </style>
    """


def render_masthead(title: str, strapline: str, kicker: str) -> str:
    """Returns the portal masthead markup."""
    return f"""
    <div class="gov-masthead">
        <div class="emblem">{kicker}</div>
        <h1>{title}</h1>
        <p class="strapline">{strapline}</p>
    </div>
    """


def render_section(title: str, description: str = "") -> str:
    """Returns a gold-ruled section heading."""
    note = f"<p>{description}</p>" if description else ""
    return f'<div class="section-rule"><h3>{title}</h3>{note}</div>'


def render_stat_tile(label: str, value: str, note: str = "") -> str:
    """Returns a key-figure tile."""
    return f"""
    <div class="stat-tile">
        <div class="label">{label}</div>
        <div class="value">{value}</div>
        <div class="note">{note}</div>
    </div>
    """


def render_verdict_banner(verdict: str, project_name: str, reason: str, facts: list) -> str:
    """Returns the verification outcome banner for a completed audit."""
    if verdict == "VERIFIED":
        modifier, kicker, heading = "is-clear", "Independent verification complete", "Asset confirmed on the ground"
    elif verdict == "IN_PROGRESS":
        modifier, kicker, heading = "", "Independent verification complete", "Partial execution detected"
    else:
        modifier, kicker, heading = "is-flagged", "Vigilance alert raised", "No qualifying construction detected"

    fact_html = "".join(f"<span>{fact}</span>" for fact in facts)
    return f"""
    <div class="verdict-banner {modifier}">
        <div class="kicker">{kicker}</div>
        <h2>{heading}</h2>
        <p><b>{project_name}</b> — {reason}</p>
        <div class="verdict-facts">{fact_html}</div>
    </div>
    """


def safe_load_image(img_path: str):
    """Loads an image, tolerating missing or truncated files."""
    try:
        if img_path and Path(img_path).exists():
            image = Image.open(img_path)
            image.load()
            return image
    except Exception:
        pass
    return None
