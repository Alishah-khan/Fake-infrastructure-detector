"""
Module: User Interface & Visual Layout Engine
Author: Member 3 (UI/UX & Frontend Lead)

Provides custom styling, centered hero branding, centered navigation tabs,
and cinematic animations (screen cracks for suspicious fraud, and green laser for verified).
"""

from PIL import Image, ImageFile
from pathlib import Path

ImageFile.LOAD_TRUNCATED_IMAGES = True


def get_custom_ui_theme():
    """Returns CSS theme with centered hero design, centered tabs, and cinematic animations."""
    return """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800;900&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* CENTERED HERO CONTAINER */
    .hero-center-container {
        text-align: center;
        padding: 32px 24px 28px 24px;
        background: linear-gradient(180deg, #f8fafc 0%, #ffffff 100%);
        border-radius: 24px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.05);
        margin: 0 auto 28px auto;
        max-width: 1000px;
        position: relative;
    }
    .hero-center-container::before {
        content: '';
        position: absolute;
        top: 0;
        left: 50%;
        transform: translateX(-50%);
        width: 320px;
        height: 4px;
        background: linear-gradient(90deg, #3b82f6, #10b981, #3b82f6);
        border-radius: 0 0 10px 10px;
    }
    .hero-pill {
        display: inline-block;
        background: #eff6ff;
        color: #2563eb;
        border: 1px solid #dbeafe;
        padding: 6px 18px;
        border-radius: 30px;
        font-size: 0.82rem;
        font-weight: 700;
        letter-spacing: 0.5px;
        text-transform: uppercase;
        margin-bottom: 12px;
    }
    .hero-title-main {
        font-size: 3rem;
        font-weight: 900;
        color: #0f172a;
        letter-spacing: -1px;
        margin: 0 0 10px 0;
        line-height: 1.15;
        text-align: center;
    }
    .hero-title-gradient {
        background: linear-gradient(135deg, #1e40af 0%, #3b82f6 50%, #059669 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .hero-tagline {
        font-size: 1.05rem;
        color: #64748b;
        max-width: 720px;
        margin: 0 auto;
        line-height: 1.6;
        font-weight: 500;
        text-align: center;
    }

    /* CENTER ALIGN STREAMLIT TABS BAR */
    .stTabs [data-baseweb="tab-list"] {
        display: flex;
        justify-content: center;
        width: 100%;
        gap: 12px;
        border-bottom: 2px solid #e2e8f0;
        margin-bottom: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        font-size: 0.95rem;
        font-weight: 600;
        padding: 10px 20px;
        border-radius: 10px 10px 0 0;
    }

    /* ------------------------------------------------------------- */
    /* 🚨 CINEMATIC CRACKS & RED EMERGENCY SIREN (FOR SUSPICIOUS)   */
    /* ------------------------------------------------------------- */
    @keyframes screenShake {
        0%, 100% { transform: translate(0, 0) rotate(0deg); }
        10% { transform: translate(-6px, 6px) rotate(-0.8deg); }
        20% { transform: translate(6px, -5px) rotate(0.8deg); }
        30% { transform: translate(-5px, 4px) rotate(-0.5deg); }
        40% { transform: translate(5px, -4px) rotate(0.5deg); }
        50% { transform: translate(-4px, 3px) rotate(-0.3deg); }
        60% { transform: translate(3px, -2px) rotate(0.3deg); }
    }

    @keyframes crackLineDraw {
        0% { stroke-dashoffset: 1200; opacity: 0; }
        10% { opacity: 1; }
        100% { stroke-dashoffset: 0; opacity: 0.95; }
    }

    @keyframes redPulseAlert {
        0%, 100% {
            box-shadow: 0 0 40px rgba(220, 38, 38, 0.6), inset 0 0 30px rgba(220, 38, 38, 0.3);
            border-color: #ef4444;
        }
        50% {
            box-shadow: 0 0 90px rgba(239, 68, 68, 0.95), inset 0 0 50px rgba(239, 68, 68, 0.5);
            border-color: #dc2626;
        }
    }

    .suspicious-screen-takeover {
        animation: screenShake 0.7s cubic-bezier(0.36, 0.07, 0.19, 0.97) both;
        position: relative;
        background: linear-gradient(145deg, #450a0a 0%, #1f0202 100%);
        border: 3px solid #ef4444;
        border-radius: 24px;
        padding: 36px 28px;
        margin: 20px 0;
        color: #ffffff;
        text-align: center;
        animation: redPulseAlert 1.6s infinite ease-in-out;
        overflow: hidden;
    }

    .crack-overlay-svg {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        pointer-events: none;
        z-index: 1;
    }
    .crack-path {
        stroke: rgba(254, 202, 202, 0.85);
        stroke-width: 3;
        stroke-linecap: round;
        stroke-linejoin: round;
        stroke-dasharray: 1200;
        animation: crackLineDraw 0.8s ease-out forwards;
        filter: drop-shadow(0 0 8px rgba(239, 68, 68, 0.9));
    }

    .suspicious-alert-badge {
        display: inline-block;
        background: #dc2626;
        color: #ffffff;
        font-weight: 900;
        font-size: 1rem;
        padding: 8px 24px;
        border-radius: 30px;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        box-shadow: 0 0 25px rgba(220, 38, 38, 0.8);
        margin-bottom: 14px;
        position: relative;
        z-index: 2;
    }
    .suspicious-main-heading {
        font-size: 2.3rem;
        font-weight: 900;
        color: #fee2e2;
        margin: 8px 0 12px 0;
        letter-spacing: -0.5px;
        position: relative;
        z-index: 2;
        text-shadow: 0 0 20px rgba(239, 68, 68, 0.8);
    }
    .suspicious-desc {
        font-size: 1.15rem;
        color: #fca5a5;
        max-width: 760px;
        margin: 0 auto 20px auto;
        line-height: 1.5;
        position: relative;
        z-index: 2;
    }

    /* ------------------------------------------------------------- */
    /* ✅ CELEBRATORY GREEN HOLOGRAPHIC SHIELD (FOR VERIFIED)       */
    /* ------------------------------------------------------------- */
    @keyframes greenHoloGlow {
        0%, 100% {
            box-shadow: 0 0 45px rgba(22, 163, 74, 0.5), inset 0 0 25px rgba(22, 163, 74, 0.2);
            border-color: #22c55e;
        }
        50% {
            box-shadow: 0 0 85px rgba(34, 197, 94, 0.85), inset 0 0 45px rgba(34, 197, 94, 0.4);
            border-color: #16a34a;
        }
    }

    @keyframes laserScan {
        0% { transform: translateY(-100%); opacity: 0; }
        50% { opacity: 0.8; }
        100% { transform: translateY(100%); opacity: 0; }
    }

    .verified-screen-takeover {
        position: relative;
        background: linear-gradient(145deg, #052e16 0%, #022c22 100%);
        border: 3px solid #22c55e;
        border-radius: 24px;
        padding: 36px 28px;
        margin: 20px 0;
        color: #ffffff;
        text-align: center;
        animation: greenHoloGlow 2s infinite ease-in-out;
        overflow: hidden;
    }
    .verified-laser-line {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 6px;
        background: linear-gradient(90deg, transparent, #4ade80, transparent);
        animation: laserScan 2.2s infinite linear;
        box-shadow: 0 0 20px #22c55e;
    }
    .verified-alert-badge {
        display: inline-block;
        background: #16a34a;
        color: #ffffff;
        font-weight: 900;
        font-size: 1rem;
        padding: 8px 24px;
        border-radius: 30px;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        box-shadow: 0 0 25px rgba(22, 163, 74, 0.8);
        margin-bottom: 14px;
    }
    .verified-main-heading {
        font-size: 2.3rem;
        font-weight: 900;
        color: #dcfce7;
        margin: 8px 0 12px 0;
        letter-spacing: -0.5px;
        text-shadow: 0 0 20px rgba(34, 197, 94, 0.8);
    }
    .verified-desc {
        font-size: 1.15rem;
        color: #86efac;
        max-width: 760px;
        margin: 0 auto 20px auto;
        line-height: 1.5;
    }

    /* Common Card Badges */
    .badge-verified {
        background: #16a34a;
        color: #ffffff;
        padding: 5px 12px;
        border-radius: 20px;
        font-size: 0.76rem;
        font-weight: 700;
        display: inline-block;
    }
    .badge-suspicious {
        background: #dc2626;
        color: #ffffff;
        padding: 5px 12px;
        border-radius: 20px;
        font-size: 0.76rem;
        font-weight: 700;
        display: inline-block;
    }
    .badge-progress {
        background: #d97706;
        color: #ffffff;
        padding: 5px 12px;
        border-radius: 20px;
        font-size: 0.76rem;
        font-weight: 700;
        display: inline-block;
    }

    .metric-chip-row {
        display: flex;
        justify-content: space-between;
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 8px 12px;
        margin: 12px 0;
    }
    .metric-chip-item {
        text-align: center;
    }
    .metric-chip-val {
        font-size: 0.95rem;
        font-weight: 700;
        color: #1e293b;
    }
    .metric-chip-lbl {
        font-size: 0.7rem;
        color: #64748b;
        text-transform: uppercase;
    }

    .audit-callout {
        font-size: 0.82rem;
        color: #334155;
        background: #f1f5f9;
        border-left: 3px solid #64748b;
        border-radius: 6px;
        padding: 8px 12px;
        margin-bottom: 12px;
        line-height: 1.4;
    }
    </style>
    """


def render_suspicious_cracks_alert(project_name: str, reason: str, confidence: float, budget: float):
    """Renders the dramatic screen crack animation with glowing red siren takeover."""
    budget_str = f"₹{budget/1e7:.2f} Crore" if budget >= 1e7 else f"₹{budget/1e5:.1f} Lakh"
    return f"""
    <div class="suspicious-screen-takeover">
        <svg class="crack-overlay-svg" viewBox="0 0 800 350" preserveAspectRatio="none">
            <circle cx="400" cy="175" r="8" fill="#ef4444" filter="drop-shadow(0 0 10px #ff0000)" />
            <path class="crack-path" d="M400,175 L280,60 L140,20 L0,0" />
            <path class="crack-path" d="M400,175 L520,70 L670,30 L800,10" />
            <path class="crack-path" d="M400,175 L310,240 L180,310 L20,350" />
            <path class="crack-path" d="M400,175 L500,260 L690,320 L800,350" />
            <path class="crack-path" d="M400,175 L390,30 L380,0" />
            <path class="crack-path" d="M400,175 L415,310 L430,350" />
            <path class="crack-path" d="M280,60 L240,120 L160,150 L0,160" />
            <path class="crack-path" d="M520,70 L580,130 L720,160 L800,180" />
            <path class="crack-path" d="M310,240 L250,220 L120,240" />
            <path class="crack-path" d="M500,260 L570,230 L710,260" />
        </svg>

        <span class="suspicious-alert-badge">🚨 CRITICAL FRAUD DETECTED • PHANTOM ASSET FLAGGED</span>
        <h2 class="suspicious-main-heading">⚠️ ZERO PHYSICAL INFRASTRUCTURE DETECTED</h2>
        <p class="suspicious-desc"><b>{project_name}:</b> {reason}</p>
        
        <div style="display:flex; justify-content:center; gap:16px; flex-wrap:wrap; position:relative; z-index:2;">
            <span style="background:rgba(220,38,38,0.3); border:1px solid #ef4444; color:#fee2e2; padding:8px 18px; border-radius:20px; font-weight:700; font-size:0.9rem;">
                🎯 AI CONFIDENCE: {confidence}%
            </span>
            <span style="background:rgba(220,38,38,0.3); border:1px solid #ef4444; color:#fee2e2; padding:8px 18px; border-radius:20px; font-weight:700; font-size:0.9rem;">
                💰 CAPITAL AT RISK: {budget_str}
            </span>
            <span style="background:#dc2626; color:#ffffff; padding:8px 18px; border-radius:20px; font-weight:700; font-size:0.9rem; box-shadow:0 0 15px rgba(220,38,38,0.6);">
                🔒 TREASURY PAYMENT FROZEN
            </span>
        </div>
    </div>
    """


def render_verified_hologram_alert(project_name: str, reason: str, confidence: float, growth: float):
    """Renders the grand green holographic laser celebration for confirmed built projects."""
    return f"""
    <div class="verified-screen-takeover">
        <div class="verified-laser-line"></div>
        <span class="verified-alert-badge">✅ GROUND TRUTH VERIFIED • ASSET CONFIRMED BUILT</span>
        <h2 class="verified-main-heading">🌟 100% PHYSICAL CONSTRUCTION CONFIRMED</h2>
        <p class="verified-desc"><b>{project_name}:</b> {reason}</p>
        
        <div style="display:flex; justify-content:center; gap:16px; flex-wrap:wrap;">
            <span style="background:rgba(22,163,74,0.3); border:1px solid #4ade80; color:#dcfce7; padding:8px 18px; border-radius:20px; font-weight:700; font-size:0.9rem;">
                🎯 AI CONFIDENCE: {confidence}%
            </span>
            <span style="background:rgba(22,163,74,0.3); border:1px solid #4ade80; color:#dcfce7; padding:8px 18px; border-radius:20px; font-weight:700; font-size:0.9rem;">
                📈 BUILT-UP EXPANSION: +{growth}%
            </span>
            <span style="background:#16a34a; color:#ffffff; padding:8px 18px; border-radius:20px; font-weight:700; font-size:0.9rem; box-shadow:0 0 15px rgba(22,163,74,0.6);">
                🏛️ APPROVED FOR FINAL SETTLEMENT
            </span>
        </div>
    </div>
    """


def safe_load_image(img_path: str):
    """Safely loads image with truncated file protection."""
    try:
        if img_path and Path(img_path).exists():
            img = Image.open(img_path)
            img.load()
            return img
    except Exception:
        pass
    return None

