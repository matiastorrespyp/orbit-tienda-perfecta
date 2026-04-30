#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Orbit · Tienda Perfecta — Plataforma de visualización comercial
Autor: Matías Torres | Orbit © 2026
"""

import ast
import base64
import json
import os
import re
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

# ─── Paths ─────────────────────────────────────────────────────────────────────
BASE     = os.path.dirname(os.path.abspath(__file__))
ASSETS   = os.path.join(BASE, "assets")
DATA     = os.path.join(BASE, "output")
XLSX     = os.path.join(DATA, "Control_TP_Portafolio_PyP.xlsx")
CSVDIR   = os.path.join(DATA, "APPSHEET")
CFG      = os.path.join(BASE, "config_app.json")
LOGO     = os.path.join(ASSETS, "Orbit Tienda Perfecta.png")
MARK     = os.path.join(ASSETS, "orbit-mark.png")
WORDMARK = os.path.join(ASSETS, "orbit-wordmark.png")
PYP_LOGO = os.path.join(ASSETS, "pyp-logo.png")
PYP_MARK = os.path.join(ASSETS, "pyp-mark.png")
CURSOR   = os.path.join(ASSETS, "cursor-dorito.png")
AUDIO_JS = os.path.join(ASSETS, "audio.js")

# ─── Spanish days ──────────────────────────────────────────────────────────────
_DIAS_ES = {
    "Monday":"Lunes","Tuesday":"Martes","Wednesday":"Miércoles",
    "Thursday":"Jueves","Friday":"Viernes","Saturday":"Sábado","Sunday":"Domingo"
}
def dia_es():
    n = datetime.now()
    return f"{_DIAS_ES.get(n.strftime('%A'), n.strftime('%A'))} {n.strftime('%d/%m/%Y')}"

# ─── Brand ─────────────────────────────────────────────────────────────────────
GREEN   = "#6EC531"
DGREEN  = "#4A8A1C"
BLACK   = "#0A0A0A"
CARD    = "#111111"
CARD2   = "#161616"
BORDER  = "#222222"
RED     = "#E84B4B"
YELLOW  = "#F0C000"
ORANGE  = "#E87A00"
WHITE   = "#FFFFFF"
GRAY    = "#888888"
LGRAY   = "#BBBBBB"

# ─── Config load ───────────────────────────────────────────────────────────────
def load_config():
    if os.path.exists(CFG):
        with open(CFG, encoding="utf-8") as f:
            return json.load(f)
    return {
        "mgmt_password": "orbit2026",
        "vendor_password": "tp2026",
        "vendor_names": {"2": "Juliana", "3": "Nadia", "4": "Ángel", "5": "Majo", "6": "Andrea"}
    }

CFG_DATA      = load_config()
MGMT_PASS     = CFG_DATA.get("mgmt_password", "orbit2026")
VENDOR_PASS   = CFG_DATA.get("vendor_password", "tp2026")
VENDOR_NAMES  = CFG_DATA.get("vendor_names", {})
_clogo_rel    = CFG_DATA.get("company_logo", "assets/empresa.png")
COMPANY_LOGO  = os.path.join(BASE, _clogo_rel)

# ─── Page setup ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Orbit · Tienda Perfecta",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="auto",
)

# ─── Logo / asset b64 helpers ──────────────────────────────────────────────────
def _b64(path):
    if os.path.exists(path):
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return ""

@st.cache_data
def get_logo_b64():         return _b64(LOGO)
@st.cache_data
def get_company_logo_b64(): return _b64(COMPANY_LOGO)
@st.cache_data
def get_mark_b64():         return _b64(MARK)
@st.cache_data
def get_wordmark_b64():     return _b64(WORDMARK)
@st.cache_data
def get_pyp_logo_b64():     return _b64(PYP_LOGO)
@st.cache_data
def get_pyp_mark_b64():     return _b64(PYP_MARK)
@st.cache_data
def get_cursor_b64():       return _b64(CURSOR)
@st.cache_data
def get_audio_js():
    if os.path.exists(AUDIO_JS):
        with open(AUDIO_JS, encoding="utf-8") as f:
            return f.read()
    return ""


# ─── Audio crunch injection ────────────────────────────────────────────────────
def inject_audio():
    """Inyecta el sistema de sonido WebAudio en la página principal."""
    import streamlit.components.v1 as components
    js = get_audio_js()
    if not js:
        return
    components.html(f"""
    <script>
    (function() {{
        // Ocultar este iframe para que no aparezca como espacio vacío
        try {{
            var el = window.frameElement;
            if (el) {{
                el.style.cssText = 'display:none!important;height:0!important;';
                var p = el.closest('.element-container') || el.parentElement;
                if (p) p.style.cssText = 'height:0!important;overflow:hidden!important;margin:0!important;padding:0!important;';
            }}
        }} catch(e) {{}}
        if (window.parent.__orbitAudioInstalled) return;
        window.parent.__orbitAudioInstalled = true;
        var s = window.parent.document.createElement('script');
        s.textContent = {repr(js)};
        window.parent.document.head.appendChild(s);
    }})();
    </script>
    """, height=0, scrolling=False)


# ─── CSS ───────────────────────────────────────────────────────────────────────
def inject_css():
    """Inyecta CSS en window.parent.document via JS (bypasa sanitización de Streamlit)."""
    import streamlit.components.v1 as components

    cursor_b64 = get_cursor_b64()
    if cursor_b64:
        cur_auto = f"url('data:image/png;base64,{cursor_b64}') 16 4, auto"
        cur_ptr  = f"url('data:image/png;base64,{cursor_b64}') 16 4, pointer"
        cur_txt  = f"url('data:image/png;base64,{cursor_b64}') 16 4, text"
    else:
        cur_auto, cur_ptr, cur_txt = "auto", "pointer", "text"

    # Construimos el CSS como string Python (las llaves CSS son literales aquí)
    css = f"""
    :root {{
        --bg:         #0A0B0A;
        --bg-1:       #0E100E;
        --surface:    #121412;
        --surface-2:  #181B18;
        --surface-3:  #1F231F;
        --line:       #232723;
        --line-2:     #2F342F;
        --text:       #F4F6F4;
        --text-2:     #A8AEA8;
        --text-3:     #6B716B;
        --text-4:     #494E49;
        --green:      #6EC531;
        --green-2:    #8AD94E;
        --green-dim:  #4A8A1C;
        --green-soft: rgba(110,197,49,0.10);
        --green-line: rgba(110,197,49,0.28);
        --red:        #E84B4B;
        --yellow:     #F0C000;
        --orange:     #E87A00;
    }}
    /* Cursor Dorito */
    *, *::before, *::after {{ cursor: {cur_auto} !important; }}
    a, button, [role="button"], .clickable, label[for], summary {{ cursor: {cur_ptr} !important; }}
    input[type="text"], input[type="password"], input[type="search"], textarea {{ cursor: {cur_txt} !important; }}
    /* Base */
    html, body, [class*="css"] {{
        font-family: 'Geist', -apple-system, BlinkMacSystemFont, system-ui, sans-serif !important;
        background-color: var(--bg) !important;
        color: var(--text) !important;
        -webkit-font-smoothing: antialiased !important;
        font-feature-settings: "ss01", "cv11";
    }}
    .stApp {{ background-color: var(--bg); }}
    #MainMenu, footer, header {{ visibility: hidden; }}
    .block-container {{ padding-top: 0 !important; padding-bottom: 0 !important; max-width: 1400px; }}
    /* Ambient grid */
    .stApp::before {{
        content: '';
        position: fixed; inset: 0; pointer-events: none; z-index: 0;
        background-image:
            linear-gradient(rgba(110,197,49,0.022) 1px, transparent 1px),
            linear-gradient(90deg, rgba(110,197,49,0.022) 1px, transparent 1px);
        background-size: 64px 64px;
        mask-image: radial-gradient(ellipse 80% 60% at 30% 20%, #000 30%, transparent 80%);
    }}
    /* Scrollbar */
    ::-webkit-scrollbar {{ width: 10px; height: 10px; }}
    ::-webkit-scrollbar-track {{ background: transparent; }}
    ::-webkit-scrollbar-thumb {{ background: var(--surface-3); border-radius: 8px; border: 2px solid var(--bg); }}
    ::-webkit-scrollbar-thumb:hover {{ background: var(--line-2); }}
    /* Animations */
    @keyframes floaty {{
        0%, 100% {{ transform: translateY(0) rotate(0deg); }}
        50%       {{ transform: translateY(-8px) rotate(6deg); }}
    }}
    @keyframes launch {{
        0%   {{ transform: rotate(0) scale(1); filter: drop-shadow(0 0 28px rgba(110,197,49,0.55)); }}
        35%  {{ transform: rotate(-30deg) scale(0.9); }}
        70%  {{ transform: rotate(720deg) scale(1.4); filter: drop-shadow(0 0 60px rgba(110,197,49,1)); }}
        100% {{ transform: rotate(1080deg) scale(0.4); opacity: 0; filter: drop-shadow(0 0 80px rgba(110,197,49,0.9)); }}
    }}
    @keyframes shake {{
        10%, 90% {{ transform: translateX(-2px); }}
        20%, 80% {{ transform: translateX(4px); }}
        30%, 50%, 70% {{ transform: translateX(-7px); }}
        40%, 60% {{ transform: translateX(7px); }}
    }}
    @keyframes fade-in {{
        from {{ opacity: 0; transform: translateY(6px); }}
        to   {{ opacity: 1; transform: translateY(0); }}
    }}
    @keyframes liveDot {{
        0%, 100% {{ box-shadow: 0 0 6px rgba(110,197,49,0.7); }}
        50%       {{ box-shadow: 0 0 14px rgba(110,197,49,1), 0 0 22px rgba(110,197,49,0.45); }}
    }}
    .live-dot {{ animation: liveDot 2.4s ease-in-out infinite; }}
    .orbit-mark-spin {{ animation: floaty 5.5s ease-in-out infinite; }}
    .orbit-mark-launch {{ animation: launch 1.1s cubic-bezier(.4,0,.2,1) forwards !important; }}
    /* Sidebar */
    [data-testid="stSidebar"] {{
        background: var(--bg-1) !important;
        border-right: 1px solid var(--line) !important;
        min-width: 236px !important;
        max-width: 236px !important;
    }}
    [data-testid="stSidebar"] > div {{
        padding: 0 !important; gap: 0 !important; overflow-x: hidden !important;
    }}
    /* Collapse button: oculto en desktop, visible en mobile */
    @media (min-width: 769px) {{
        [data-testid="stSidebarCollapseButton"],
        button[data-testid="collapsedControl"] {{ display: none !important; }}
    }}
    /* Iframes de inyección (height=0) — no ocupan espacio visible */
    iframe[height="0"] {{ position: absolute !important; width: 0 !important; }}
    .element-container:has(> div > iframe[height="0"]) {{
        height: 0 !important; margin: 0 !important; padding: 0 !important;
        overflow: hidden !important;
    }}
    [data-testid="stSidebar"] .stButton > button {{
        background: transparent !important; color: var(--text-2) !important;
        border: none !important; border-radius: 7px !important;
        padding: 8px 10px !important; font-size: 13px !important;
        font-weight: 500 !important; width: 100% !important;
        text-align: left !important; justify-content: flex-start !important;
        box-shadow: none !important; transform: none !important;
        letter-spacing: 0.1px !important;
        transition: background .18s, color .18s, transform .22s cubic-bezier(.2,.8,.2,1) !important;
    }}
    [data-testid="stSidebar"] .stButton > button:hover {{
        background: rgba(255,255,255,0.025) !important; color: var(--text) !important;
        transform: translateX(2px) !important; box-shadow: none !important;
    }}
    [data-testid="stSidebar"] .stButton > button[kind="primary"] {{
        background: var(--surface-2) !important; color: var(--text) !important;
        border-left: 2px solid var(--green) !important;
        border-radius: 7px !important; padding-left: 8px !important;
    }}
    [data-testid="stSidebar"] .sidebar-icon-btn .stButton > button {{
        width: 30px !important; height: 30px !important; padding: 0 !important;
        border: 1px solid var(--line) !important; border-radius: 7px !important;
        font-size: 13px !important; display: grid !important;
        place-items: center !important; justify-content: center !important;
    }}
    [data-testid="stSidebar"] .sidebar-icon-btn .stButton > button:hover {{
        border-color: var(--green-line) !important; color: var(--green) !important;
        background: var(--green-soft) !important; transform: translateY(-2px) !important;
        box-shadow: 0 4px 12px rgba(110,197,49,0.18) !important;
    }}
    /* Top bar */
    .orbit-topbar {{
        display: flex; align-items: center; gap: 16px;
        padding: 18px 32px; margin: 0 -4rem 1.4rem -4rem;
        border-bottom: 1px solid var(--line);
        background: rgba(10,11,10,0.9); backdrop-filter: blur(10px);
        position: sticky; top: 0; z-index: 4; animation: fade-in 0.3s ease;
    }}
    .period-chip {{
        display: flex; align-items: center; gap: 8px;
        padding: 6px 11px 6px 8px; border: 1px solid var(--line);
        border-radius: 99px; font-size: 12px; cursor: default;
        transition: border-color .22s;
    }}
    .period-chip:hover {{ border-color: var(--green-line); }}
    /* KPI cards */
    .kpi-card {{
        position: relative; overflow: hidden;
        border: 1px solid var(--line); border-radius: 12px;
        background: var(--surface); padding: 20px; cursor: pointer;
        transition: transform .35s cubic-bezier(.2,.8,.2,1), border-color .25s, box-shadow .35s !important;
    }}
    .kpi-card:hover {{
        transform: translateY(-3px) !important;
        border-color: var(--green-line) !important;
        box-shadow: 0 10px 32px rgba(0,0,0,0.45), 0 0 0 1px rgba(110,197,49,0.08) !important;
    }}
    .kpi-card::before {{
        content: ''; position: absolute; inset: 0;
        background: radial-gradient(120% 100% at 50% 0%, rgba(110,197,49,0.08), transparent 60%);
        opacity: 0; transition: opacity .35s; pointer-events: none;
    }}
    .kpi-card:hover::before {{ opacity: 1; }}
    .kpi-card.active {{
        border-color: rgba(110,197,49,0.5) !important;
        box-shadow: 0 0 0 1px rgba(110,197,49,0.2) !important;
    }}
    /* Invisible overlay buttons on KPI cards */
    .element-container:has(.kpi-port) + .element-container .stButton > button,
    .element-container:has(.kpi-tp)   + .element-container .stButton > button,
    .element-container:has(.kpi-oport)+ .element-container .stButton > button,
    .element-container:has(.kpi-crit) + .element-container .stButton > button {{
        background: transparent !important; border: none !important;
        box-shadow: none !important; outline: none !important;
        width: 100% !important; min-height: 120px !important;
        margin-top: -124px !important; opacity: 0 !important;
        cursor: pointer !important; position: relative !important;
        z-index: 100 !important; padding: 0 !important;
    }}
    /* Buttons */
    .stButton > button {{
        background: transparent !important; color: var(--text-3) !important;
        border: 1px solid var(--line) !important; border-radius: 7px !important;
        padding: 0.3rem 0.9rem !important; font-size: 13px !important;
        font-weight: 500 !important; font-family: 'Geist', sans-serif !important;
        letter-spacing: 0.2px !important; transition: all 0.22s ease !important;
        white-space: nowrap !important;
    }}
    .stButton > button:hover {{
        border-color: var(--green-line) !important; color: var(--green) !important;
        background: var(--green-soft) !important;
        box-shadow: 0 0 12px rgba(110,197,49,0.18) !important;
        transform: translateY(-1px) !important;
    }}
    .stButton > button:active {{ transform: translateY(0) !important; }}
    /* Login button */
    .login-btn .stButton > button {{
        background: linear-gradient(135deg, var(--green) 0%, var(--green-dim) 100%) !important;
        color: #0A0B0A !important; font-weight: 700 !important; font-size: 13px !important;
        letter-spacing: 1.5px !important; text-transform: uppercase !important;
        border: none !important; border-radius: 10px !important; padding: 14px !important;
        width: 100% !important; box-shadow: 0 6px 20px rgba(110,197,49,0.28) !important;
        transition: all .25s cubic-bezier(.2,.8,.2,1) !important;
    }}
    .login-btn .stButton > button:hover {{
        transform: translateY(-2px) !important; filter: brightness(1.08) !important;
        box-shadow: 0 12px 32px rgba(110,197,49,0.45) !important;
    }}
    .login-btn .stButton > button:active {{ transform: translateY(0) scale(0.98) !important; }}
    /* Inputs */
    .stTextInput > div > div > input {{
        background-color: #101210 !important; color: var(--text) !important;
        border: 1.5px solid var(--line) !important; border-radius: 9px !important;
        font-size: 14px !important; font-family: inherit !important;
        transition: border-color .2s, box-shadow .2s !important;
    }}
    .stTextInput > div > div > input:focus {{
        border-color: var(--green-line) !important;
        box-shadow: 0 0 0 3px rgba(110,197,49,0.10) !important;
    }}
    .stSelectbox > div > div {{
        background-color: #101210 !important; color: var(--text) !important;
        border: 1.5px solid var(--line) !important; border-radius: 9px !important;
    }}
    .stSelectbox label, .stTextInput label {{
        color: var(--text-3) !important; font-size: 10.5px !important;
        text-transform: uppercase !important; letter-spacing: 1.4px !important;
        font-weight: 600 !important;
    }}
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {{
        background-color: var(--surface); border-radius: 9px; padding: 3px; gap: 2px;
        border: 1px solid var(--line);
    }}
    .stTabs [data-baseweb="tab"] {{
        background-color: transparent; color: var(--text-3); border-radius: 7px;
        font-weight: 500; font-size: 13px; padding: 0.45rem 1rem;
        border: none; transition: color 0.2s;
    }}
    .stTabs [data-baseweb="tab"]:hover {{ color: var(--text); }}
    .stTabs [aria-selected="true"] {{
        background: linear-gradient(135deg, var(--green), var(--green-dim)) !important;
        color: #0A0B0A !important; box-shadow: 0 2px 10px rgba(110,197,49,0.3) !important;
    }}
    /* Expanders */
    details {{
        background: var(--surface) !important; border: 1px solid var(--line) !important;
        border-radius: 10px !important; margin-bottom: 0.4rem !important;
        transition: border-color 0.2s !important;
    }}
    details:hover {{ border-color: var(--green-line) !important; }}
    details summary {{
        color: var(--text) !important; font-weight: 600 !important;
        padding: 0.7rem 1rem !important; cursor: pointer; transition: color 0.2s;
    }}
    details summary:hover {{ color: var(--green) !important; }}
    details[open] summary {{ border-bottom: 1px solid var(--line); color: var(--green) !important; }}
    details > div {{ padding: 0.8rem 1rem !important; }}
    /* Orbit cards */
    .ocard {{
        background: var(--surface); border: 1px solid var(--line);
        border-radius: 12px; padding: 1.2rem 1.4rem; margin-bottom: 0.7rem;
        transition: transform 0.22s ease, box-shadow 0.22s ease, border-color 0.22s ease;
        animation: fade-in 0.35s ease;
    }}
    .ocard:hover {{ transform: translateY(-2px); box-shadow: 0 8px 28px rgba(0,0,0,0.35); border-color: var(--green-line) !important; }}
    .ocard-green  {{ border-left: 3px solid var(--green) !important; }}
    .ocard-yellow {{ border-left: 3px solid var(--yellow) !important; }}
    .ocard-orange {{ border-left: 3px solid var(--orange) !important; }}
    .ocard-red    {{ border-left: 3px solid var(--red) !important; }}
    /* Row hover */
    .row-hover {{ transition: background .18s, transform .22s cubic-bezier(.2,.8,.2,1) !important; }}
    .row-hover:hover {{ background: rgba(110,197,49,0.04) !important; transform: translateX(2px) !important; }}
    /* Section label */
    .section-label {{
        font-size: 10.5px; font-weight: 600; color: var(--text-3);
        text-transform: uppercase; letter-spacing: 1.5px;
        margin: 1.4rem 0 0.7rem 0; padding-bottom: 0.4rem;
        border-bottom: 1px solid var(--line);
    }}
    /* Mono numbers */
    .num {{ font-family: 'JetBrains Mono', monospace !important; font-feature-settings: "tnum" !important; }}
    /* Metrics */
    [data-testid="stMetricValue"] {{
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 2rem !important; font-weight: 600 !important; color: var(--text) !important;
    }}
    [data-testid="stMetricLabel"] {{
        color: var(--text-3) !important; font-size: 10.5px !important;
        text-transform: uppercase !important; letter-spacing: 1.2px !important; font-weight: 600 !important;
    }}
    /* Footer */
    .orbit-footer {{
        text-align: center; color: var(--text-4); font-size: 10px;
        padding: 2rem 0 0.5rem 0; margin-top: 2rem;
        border-top: 1px solid var(--line); letter-spacing: 1px;
    }}
    /* SKU pills */
    .sku-g {{ display:inline-block; background:#0F1F00; color:var(--green); border:1px solid rgba(110,197,49,0.33); border-radius:20px; padding:0.2rem 0.65rem; font-size:12px; margin:2px; transition:all 0.18s ease; cursor:default; }}
    .sku-g:hover {{ background:rgba(110,197,49,0.15); transform:scale(1.04); }}
    .sku-o {{ display:inline-block; background:#1F0F00; color:var(--orange); border:1px solid rgba(232,122,0,0.33); border-radius:20px; padding:0.2rem 0.65rem; font-size:12px; margin:2px; cursor:default; }}
    .sku-d {{ display:inline-block; background:var(--surface-3); color:var(--text-3); border:1px solid var(--line); border-radius:20px; padding:0.2rem 0.65rem; font-size:12px; margin:2px; cursor:default; }}
    /* Badges */
    .bdg-g {{ display:inline-block; background:rgba(110,197,49,0.12); color:var(--green); border:1px solid rgba(110,197,49,0.27); border-radius:20px; padding:0.12rem 0.7rem; font-size:11px; font-weight:700; }}
    .bdg-r {{ display:inline-block; background:rgba(232,75,75,0.12); color:var(--red); border:1px solid rgba(232,75,75,0.27); border-radius:20px; padding:0.12rem 0.7rem; font-size:11px; font-weight:700; }}
    .bdg-y {{ display:inline-block; background:rgba(240,192,0,0.12); color:var(--yellow); border:1px solid rgba(240,192,0,0.27); border-radius:20px; padding:0.12rem 0.7rem; font-size:11px; font-weight:700; }}
    .bdg-o {{ display:inline-block; background:rgba(232,122,0,0.12); color:var(--orange); border:1px solid rgba(232,122,0,0.27); border-radius:20px; padding:0.12rem 0.7rem; font-size:11px; font-weight:700; }}
    /* HR */
    hr {{ border-color: var(--line) !important; margin: 0.6rem 0 1rem 0 !important; }}
    /* Progress */
    .stProgress > div > div > div > div {{ background: linear-gradient(90deg, var(--green), var(--green-dim)); }}
    /* Desktop: ocultar botón colapso sidebar (fija siempre abierta) */
    @media (min-width: 769px) {{
        [data-testid="stSidebarCollapseButton"],
        button[data-testid="collapsedControl"] {{ display: none !important; }}
    }}
    /* Mobile */
    @media (max-width: 768px) {{
        /* Sidebar como overlay al abrirla */
        [data-testid="stSidebar"] {{
            min-width: 260px !important; max-width: 82vw !important;
            box-shadow: 4px 0 24px rgba(0,0,0,0.55) !important;
        }}
        /* Tab lateral verde — flecha para abrir sidebar */
        button[data-testid="collapsedControl"] {{
            display: flex !important;
            position: fixed !important;
            left: 0 !important; top: 50% !important;
            transform: translateY(-50%) !important;
            z-index: 9999 !important;
            background: var(--surface-2) !important;
            border: 1px solid var(--green-line) !important;
            border-left: none !important;
            border-radius: 0 10px 10px 0 !important;
            width: 22px !important; height: 60px !important;
            padding: 0 !important; margin: 0 !important;
            align-items: center !important; justify-content: center !important;
            color: var(--green) !important; font-size: 13px !important;
            box-shadow: 3px 0 14px rgba(110,197,49,0.22) !important;
            transition: width .2s, background .2s !important;
        }}
        button[data-testid="collapsedControl"]:hover,
        button[data-testid="collapsedControl"]:active {{
            width: 28px !important;
            background: rgba(110,197,49,0.15) !important;
        }}
        /* X para cerrar sidebar cuando está abierta */
        [data-testid="stSidebarCollapseButton"] {{
            display: flex !important; z-index: 9999 !important;
            background: var(--surface-3) !important;
            border: 1px solid var(--line) !important;
            color: var(--text-2) !important; border-radius: 7px !important;
        }}
        .orbit-topbar {{ padding: 12px 16px !important; margin: 0 -1rem 1rem -1rem !important; flex-wrap: wrap !important; gap: 8px !important; }}
        .orbit-topbar h1 {{ font-size: 17px !important; }}
        .period-chip {{ font-size: 10px !important; padding: 4px 8px !important; }}
        .kpi-card {{ padding: 14px !important; }}
        .block-container {{ padding-left: 0.8rem !important; padding-right: 0.8rem !important; max-width: 100% !important; }}
        [data-testid="stMetricValue"] {{ font-size: 1.4rem !important; }}
        .stApp::before {{ display: none !important; }}
        .stTabs [data-baseweb="tab-list"] {{ overflow-x: auto !important; flex-wrap: nowrap !important; }}
        .stTabs [data-baseweb="tab"] {{ white-space: nowrap !important; font-size: 12px !important; padding: 0.35rem 0.7rem !important; }}
    }}
    """

    # Inyectamos via JS al documento padre (bypasa el sanitizador de Streamlit)
    fonts_url = ("https://fonts.googleapis.com/css2?family=Geist:wght@300;400;500;600;700"
                 ";800;900&family=JetBrains+Mono:wght@400;500;600&display=swap")
    components.html(f"""
    <script>
    (function() {{
        // Ocultar este iframe (evita espacio vacío visible)
        try {{
            var el = window.frameElement;
            if (el) {{
                el.style.cssText = 'display:none!important;height:0!important;';
                var p = el.closest('.element-container') || el.parentElement;
                if (p) p.style.cssText = 'height:0!important;overflow:hidden!important;margin:0!important;padding:0!important;';
            }}
        }} catch(e) {{}}

        var doc = window.parent.document;

        // Eliminar CSS de login si quedó del paso anterior (fix pantalla negra en mobile)
        var loginCss = doc.getElementById('orbit-login-css');
        if (loginCss) loginCss.remove();

        if (doc.getElementById('orbit-tp-css')) return;

        // Google Fonts
        ['https://fonts.googleapis.com','https://fonts.gstatic.com'].forEach(function(h) {{
            var l = doc.createElement('link'); l.rel='preconnect'; l.href=h;
            if (h.includes('gstatic')) l.crossOrigin='';
            doc.head.appendChild(l);
        }});
        var lf = doc.createElement('link');
        lf.rel = 'stylesheet';
        lf.href = '{fonts_url}';
        doc.head.appendChild(lf);

        // Orbit CSS
        var s = doc.createElement('style');
        s.id = 'orbit-tp-css';
        s.textContent = {repr(css)};
        doc.head.appendChild(s);

        // Login: animación + sonido al hacer clic en INGRESAR
        function hookLoginBtn() {{
            var btn = doc.querySelector('.login-btn button');
            if (!btn) {{ setTimeout(hookLoginBtn, 400); return; }}
            btn.addEventListener('click', function() {{
                var mark = doc.querySelector('.orbit-mark-spin');
                if (mark) {{
                    mark.classList.remove('orbit-mark-launch');
                    void mark.offsetWidth; // reflow para reiniciar animación
                    mark.classList.add('orbit-mark-launch');
                }}
                if (window.playEnter) window.playEnter();
            }});
        }}
        hookLoginBtn();
    }})();
    </script>
    """, height=0, scrolling=False)


# ─── Data ──────────────────────────────────────────────────────────────────────
def _is_cloud() -> bool:
    """True cuando corre en Streamlit Cloud (sin archivos locales)."""
    return not os.path.exists(XLSX)


def _gsheets_client():
    """Retorna gspread client autenticado usando credenciales en st.secrets."""
    import gspread
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request as GRequest
    s = st.secrets["google"]
    creds = Credentials(
        token=None,
        refresh_token=s["refresh_token"],
        token_uri=s.get("token_uri", "https://oauth2.googleapis.com/token"),
        client_id=s["client_id"],
        client_secret=s["client_secret"],
        scopes=["https://www.googleapis.com/auth/spreadsheets"],
    )
    creds.refresh(GRequest())
    return gspread.authorize(creds), s["spreadsheet_id"]


def _gsheet_to_df(spreadsheet, tab_name: str) -> pd.DataFrame:
    """Lee una pestaña de Google Sheets y devuelve DataFrame."""
    ws   = spreadsheet.worksheet(tab_name)
    data = ws.get_all_values()
    if len(data) < 2:
        return pd.DataFrame()
    return pd.DataFrame(data[1:], columns=data[0])


@st.cache_data(ttl=300)
def load_data():
    _valid_vids = set(VENDOR_NAMES.keys())

    if _is_cloud():
        # ── Modo nube: leer de Google Sheets ───────────────────────────
        gc, sid = _gsheets_client()
        sheet   = gc.open_by_key(sid)
        cli      = _gsheet_to_df(sheet, "STATUS_CLIENTE")
        obj_tax  = _gsheet_to_df(sheet, "OBJ_TAXONOMIA")
        obj_vend = _gsheet_to_df(sheet, "OBJ_VENDEDOR")
        oport    = _gsheet_to_df(sheet, "clientes_oportunidad")
        foco     = _gsheet_to_df(sheet, "foco_productos")
        # Convertir columnas numéricas que vienen como string desde GSheets
        for df, cols in [
            (cli,      ["PORTAFOLIO_PCT", "FALTAN_80_N", "FALTAN_100_N",
                        "FACTURACION_CLIENTE", "KILOS_CLIENTE", "TP_ELIGIBLE"]),
            (obj_vend, ["OBJETIVO", "ACUMULADO", "REAL_DIA", "FALTANTE",
                        "CUMPLIMIENTO_PCT", "_VEND_ID_TXT"]),
            (obj_tax,  ["OBJETIVO", "ACUMULADO", "CUMPLIMIENTO_PCT", "REAL_DIA"]),
            (oport,    []),
            (foco,     ["Rank", "CantClientes"]),
        ]:
            for c in cols:
                if c in df.columns:
                    df[c] = pd.to_numeric(df[c], errors="coerce")
        # TP_SISTEMA viene como "True"/"False" string
        if "TP_SISTEMA" in cli.columns:
            cli["TP_SISTEMA"] = cli["TP_SISTEMA"].map(
                lambda x: str(x).strip().lower() in ("true", "1", "yes"))
    else:
        # ── Modo local: leer del Excel ─────────────────────────────────
        xl       = pd.ExcelFile(XLSX)
        cli      = xl.parse("STATUS_CLIENTE")
        obj_tax  = xl.parse("OBJ_TAXONOMIA")
        obj_vend = xl.parse("OBJ_VENDEDOR")
        oport    = pd.read_csv(os.path.join(CSVDIR, "clientes_oportunidad.csv"))
        foco     = pd.read_csv(os.path.join(CSVDIR, "foco_productos.csv"))

    # ── Transformaciones comunes ────────────────────────────────────────
    for col in ["SKUs_faltan_para_80_ENT", "SKUs_faltan_para_100_ENT"]:
        if col in cli.columns:
            cli[col] = cli[col].apply(_parse_list)

    cli["Vendedor_ID"] = cli["Vendedor_ID"].astype(str).str.replace(r"\.0$", "", regex=True)
    cli = cli[cli["Vendedor_ID"].isin(_valid_vids)].copy()
    cli["VendedorNombre"] = cli["Vendedor_ID"].map(lambda x: VENDOR_NAMES.get(x, f"Vendedor {x}"))
    cli["Localidad"]      = cli["Localidad"].fillna("Sin datos").str.strip().str.title()
    cli["PORTAFOLIO_PCT"] = pd.to_numeric(cli["PORTAFOLIO_PCT"], errors="coerce").fillna(0)

    obj_vend = obj_vend[obj_vend["_VEND_ID_TXT"].notna()].copy()
    obj_vend["_VID"] = obj_vend["_VEND_ID_TXT"].astype(float).astype(int).astype(str)
    obj_vend = obj_vend[obj_vend["_VID"].isin(_valid_vids)].copy()
    if "REAL_DIA" not in obj_vend.columns:
        obj_vend["REAL_DIA"] = 0

    oport["VendedorID"] = oport["VendedorID"].astype(str).str.replace(r"\.0$", "", regex=True)
    foco["VendedorID"]  = foco["VendedorID"].fillna("").astype(str).str.replace(r"\.0$", "", regex=True)

    return cli, obj_tax, obj_vend, oport, foco


def _parse_list(val):
    if pd.isna(val) or str(val).strip() in ("", "[]", "nan"):
        return []
    try:
        lst = ast.literal_eval(str(val))
        return [re.sub(r"Lay[\W_]s", "Lay's", s) for s in lst] if isinstance(lst, list) else []
    except Exception:
        return []


# ─── Helpers ───────────────────────────────────────────────────────────────────
def pct_color(p):
    if p >= 80:  return GREEN
    if p >= 60:  return YELLOW
    if p >= 30:  return ORANGE
    return RED

def pct_icon(p):
    if p >= 80:  return "✅"
    if p >= 60:  return "⚡"
    if p >= 30:  return "⚠️"
    return "🔴"

def pct_label(p):
    if p >= 80:  return "TP alcanzado"
    if p >= 60:  return "Oportunidad"
    if p >= 30:  return "Recuperar"
    return "Crítico"

def pct_band_css(p):
    if p >= 80:  return "ocard ocard-green"
    if p >= 60:  return "ocard ocard-yellow"
    if p >= 30:  return "ocard ocard-orange"
    return "ocard ocard-red"

def fmt_ars(val):
    try:
        return f"$ {float(val):,.0f}".replace(",", ".")
    except Exception:
        return "—"

def progress_bar_html(pct, color, height="8px"):
    w = min(max(float(pct), 0), 100)
    return f"""
    <div style='background:#1A1A1A;border-radius:20px;height:{height};overflow:hidden'>
        <div style='width:{w:.0f}%;background:linear-gradient(90deg,{color},{color}CC);
                    height:100%;border-radius:20px;transition:width 0.8s ease'></div>
    </div>"""

def kpi_card_html(label, value, sub, color, card_class="", is_active=False):
    """KPI hero card — estilo referencia con top accent bar y mono numbers."""
    active_style = f"border-color:rgba(110,197,49,0.5);box-shadow:0 0 0 1px rgba(110,197,49,0.2);" if is_active else ""
    return f"""
    <div class='kpi-card {card_class}'
         style='border-top:2px solid {color};{active_style}'>
        <div style='font-size:11px;color:var(--text-3);letter-spacing:1.2px;
                    text-transform:uppercase;font-weight:500;margin-bottom:12px'>{label}</div>
        <div class='num' style='font-size:30px;font-weight:600;letter-spacing:-0.5px;
                                 line-height:1;margin-bottom:8px;color:{color}'>{value}</div>
        <div style='color:var(--text-3);font-size:12px'>{sub}</div>
    </div>"""

def sku_pills(lst, css_class="sku-g"):
    if not lst: return ""
    return " ".join(f"<span class='{css_class}'>{s}</span>" for s in lst)

def section_label(text):
    st.markdown(f"<div class='section-label'>{text}</div>", unsafe_allow_html=True)

def orbit_footer():
    st.markdown("<div class='orbit-footer'>Orbit © 2026 · Propiedad de Torres Matías</div>",
                unsafe_allow_html=True)

def render_sidebar(role="gerencia", vendor_name="Matías Torres"):
    """Sidebar fija estilo referencia — branding + nav + footer."""
    mark_b64     = get_mark_b64()
    wordmark_b64 = get_wordmark_b64()
    pyp_mark_b64 = get_pyp_mark_b64()
    nav_page     = st.session_state.get("nav_page", "resumen")

    with st.sidebar:
        # ── Brand block ──────────────────────────────────────────────
        mark_img = (f"<img src='data:image/png;base64,{mark_b64}'"
                    f" class='orbit-mark-spin'"
                    f" style='width:40px;height:40px;filter:drop-shadow(0 0 12px rgba(110,197,49,0.4))'/>"
                    if mark_b64 else "🎯")
        wm_img   = (f"<img src='data:image/png;base64,{wordmark_b64}'"
                    f" style='height:26px;width:auto;filter:brightness(1.1);flex-shrink:0'/>"
                    if wordmark_b64 else "<span style='font-size:13px;font-weight:700;color:var(--text)'>ORBIT · TP</span>")
        pyp_img  = (f"<img src='data:image/png;base64,{pyp_mark_b64}'"
                    f" style='height:24px;width:auto;filter:drop-shadow(0 0 8px rgba(56,110,255,0.5)) brightness(1.15)'/>"
                    if pyp_mark_b64 else "")

        st.markdown(f"""
        <div style='padding:18px 16px 14px;display:flex;align-items:center;gap:10px;
                    border-bottom:1px solid var(--line)'>
            {mark_img}
            {wm_img}
            <div style='width:1px;height:24px;background:var(--line);margin:0 2px'></div>
            {pyp_img}
        </div>
        """, unsafe_allow_html=True)

        # ── User card ────────────────────────────────────────────────
        initials   = vendor_name[:2].upper() if vendor_name else "MT"
        role_label = "Gerencia comercial" if role == "gerencia" else "Vendedor/a"
        st.markdown(f"""
        <div style='margin:6px 12px 12px;padding:10px 11px;border:1px solid var(--line);
                    border-radius:9px;background:var(--surface);
                    display:flex;align-items:center;gap:9px'>
            <div style='width:28px;height:28px;border-radius:6px;background:#1E2A14;
                        display:grid;place-items:center;color:var(--green);
                        font-weight:600;font-size:12px;flex-shrink:0'>{initials}</div>
            <div style='flex:1;min-width:0;overflow:hidden'>
                <div style='font-size:12px;font-weight:500;color:var(--text);
                            white-space:nowrap;overflow:hidden;text-overflow:ellipsis'>{vendor_name}</div>
                <div style='font-size:10px;color:var(--text-3)'>{role_label}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ── Nav items ────────────────────────────────────────────────
        st.markdown("""<div style='font-size:10px;color:var(--text-4);letter-spacing:1.6px;
                        text-transform:uppercase;padding:6px 16px 4px'>Operación</div>""",
                    unsafe_allow_html=True)

        if role == "gerencia":
            nav_items = [
                ("resumen",    "📊  Resumen"),
                ("vendedores", "👥  Vendedores"),
                ("por_zona",   "🗺️  Por Zona"),
                ("clientes",   "🔍  Clientes"),
            ]
        else:
            nav_items = [("resumen", "📊  Mi Panel")]

        for key, label in nav_items:
            is_active = (nav_page == key)
            btn_type  = "primary" if is_active else "secondary"
            if st.button(label, key=f"nav_{key}", use_container_width=True, type=btn_type):
                st.session_state["nav_page"] = key
                st.rerun()

        # ── Sync status block ────────────────────────────────────────
        st.markdown("""
        <div style='margin:14px 12px 0;padding:12px;border:1px solid var(--line);
                    border-radius:9px;
                    background:linear-gradient(140deg,rgba(110,197,49,0.07),transparent 60%)'>
            <div style='font-size:10px;color:var(--green);letter-spacing:1.4px;
                        text-transform:uppercase;font-weight:600;margin-bottom:4px;
                        display:flex;align-items:center;gap:6px'>
                <span class="live-dot" style='display:inline-block;width:5px;height:5px;
                    border-radius:99px;background:var(--green)'></span>
                Sync activo
            </div>
            <div style='font-size:11px;color:var(--text-2);line-height:1.4'>
                Excel → Google Sheets.<br>Datos del último proceso.
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ── Footer spacer + icon buttons ─────────────────────────────
        st.markdown("<div style='flex:1;min-height:20px'></div>", unsafe_allow_html=True)
        st.markdown("<div style='padding:10px 12px 14px;border-top:1px solid var(--line);margin-top:14px'></div>",
                    unsafe_allow_html=True)

        fc1, fc2, fc3 = st.columns(3)
        for col, icon, key, tip, action in [
            (fc1, "⚙", "sb_cfg",    "Configuración", None),
            (fc2, "🔄", "sb_ref",   "Actualizar datos", "refresh"),
            (fc3, "✕", "sb_logout", "Cerrar sesión",   "logout"),
        ]:
            with col:
                st.markdown('<div class="sidebar-icon-btn">', unsafe_allow_html=True)
                if st.button(icon, key=key, help=tip):
                    if action == "refresh":
                        load_data.clear()
                        st.rerun()
                    elif action == "logout":
                        for k in list(st.session_state.keys()):
                            del st.session_state[k]
                        st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)


def render_topbar(title, subtitle):
    """Top bar con breadcrumb, título, live dot y período."""
    st.markdown(f"""
    <div class="orbit-topbar">
        <div>
            <div style='font-size:11px;color:var(--text-3);letter-spacing:0.6px;margin-bottom:3px'>
                Orbit &nbsp;›&nbsp; {subtitle}
            </div>
            <h1 style='margin:0;font-size:22px;font-weight:600;letter-spacing:-0.3px;color:var(--text)'>{title}</h1>
        </div>
        <div style='flex:1'></div>
        <div class="period-chip">
            <span class="live-dot" style='width:6px;height:6px;border-radius:99px;
                background:var(--green);display:inline-block'></span>
            <span style='color:var(--text-2);font-size:12px'>Período</span>
            <span class='num' style='font-size:12px;font-weight:500'>{dia_es()}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


def page_header(subtitle, show_logout=True, logout_key="logout"):
    """Compatibilidad legacy — usa render_topbar internamente."""
    render_topbar(subtitle.split("·")[0].strip(), subtitle)


# ─── Charts ────────────────────────────────────────────────────────────────────
def chart_vendor_cumplimiento(obj_vend):
    df = obj_vend.copy()
    df["Nombre"] = df["_VID"].map(lambda x: VENDOR_NAMES.get(str(x), f"V{x}"))
    df["Color"]  = df["CUMPLIMIENTO_PCT"].apply(pct_color)
    df = df.sort_values("CUMPLIMIENTO_PCT")

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df["CUMPLIMIENTO_PCT"], y=df["Nombre"],
        orientation="h",
        marker=dict(color=df["Color"], line=dict(width=0)),
        text=[f"  {v:.1f}%" for v in df["CUMPLIMIENTO_PCT"]],
        textposition="outside",
        textfont=dict(color=WHITE, size=13, family="Inter"),
        hovertemplate="<b>%{y}</b><br>Cumplimiento: %{x:.1f}%<extra></extra>",
        width=0.55,
    ))
    fig.add_vline(x=80, line_dash="dot", line_color=GREEN, line_width=1.5)
    fig.add_annotation(x=80, y=-0.5, text="Meta", font=dict(color=GREEN, size=10), showarrow=False)
    fig.update_layout(
        paper_bgcolor=CARD2, plot_bgcolor=CARD2,
        font=dict(color=WHITE, family="Inter"),
        height=260, margin=dict(l=5, r=60, t=10, b=10),
        xaxis=dict(range=[0, 130], color=GRAY, gridcolor=BORDER, showgrid=True),
        yaxis=dict(color=WHITE, tickfont=dict(size=13)),
        showlegend=False,
    )
    return fig


def chart_portafolio_pie(cli_df):
    labels = ["≥ 80% TP", "60–79% Oport.", "30–59% Recup.", "< 30% Crítico"]
    values = [
        len(cli_df[cli_df["PORTAFOLIO_PCT"] >= 80]),
        len(cli_df[(cli_df["PORTAFOLIO_PCT"] >= 60) & (cli_df["PORTAFOLIO_PCT"] < 80)]),
        len(cli_df[(cli_df["PORTAFOLIO_PCT"] >= 30) & (cli_df["PORTAFOLIO_PCT"] < 60)]),
        len(cli_df[cli_df["PORTAFOLIO_PCT"] < 30]),
    ]
    fig = go.Figure(go.Pie(
        labels=labels, values=values,
        marker_colors=[GREEN, YELLOW, ORANGE, RED],
        hole=0.55,
        textfont=dict(size=12, color=WHITE, family="Inter"),
        hovertemplate="<b>%{label}</b><br>%{value} clientes  (%{percent})<extra></extra>",
    ))
    fig.add_annotation(text=f"{sum(values)}<br><span style='font-size:10px'>clientes</span>",
                       x=0.5, y=0.5, font=dict(size=22, color=WHITE, family="Inter"),
                       showarrow=False)
    fig.update_layout(
        paper_bgcolor=CARD2, plot_bgcolor=CARD2,
        font=dict(color=WHITE, family="Inter"),
        height=280, margin=dict(l=5, r=5, t=5, b=5),
        legend=dict(font=dict(color=LGRAY, size=11), bgcolor="rgba(0,0,0,0)"),
        showlegend=True,
    )
    return fig


def chart_foco_bar(foco_df, max_rank=10):
    df = foco_df[foco_df["Rank"] <= max_rank].sort_values("Rank")
    if df.empty:
        return None
    max_cant = df["CantClientes"].max()
    colors = [GREEN if i < 3 else DGREEN for i in range(len(df))]
    fig = go.Figure(go.Bar(
        x=df["CantClientes"], y=df["Articulo"],
        orientation="h",
        marker=dict(color=colors, line=dict(width=0)),
        text=[f"  {v}" for v in df["CantClientes"]],
        textposition="outside",
        textfont=dict(color=WHITE, size=12),
        hovertemplate="<b>%{y}</b><br>%{x} clientes<extra></extra>",
        width=0.6,
    ))
    fig.update_layout(
        paper_bgcolor=CARD2, plot_bgcolor=CARD2,
        font=dict(color=WHITE, family="Inter"),
        height=max(220, len(df) * 32),
        margin=dict(l=5, r=50, t=5, b=10),
        xaxis=dict(range=[0, max_cant * 1.25], color=GRAY, gridcolor=BORDER),
        yaxis=dict(color=WHITE, tickfont=dict(size=11), autorange="reversed"),
        showlegend=False,
    )
    return fig


# ─── Render clientes (shared) ──────────────────────────────────────────────────
SEG_COLOR = {"P": "#B57BFF", "A": "#F0C000", "B": "#888888", "C": "#6EC531"}
SEG_BG    = {"P": "rgba(181,123,255,0.12)", "A": "rgba(240,192,0,0.12)",
             "B": "rgba(136,136,136,0.10)", "C": "rgba(110,197,49,0.10)"}


def render_clientes(df, context=""):
    if df.empty:
        st.info("Sin clientes para mostrar.")
        return
    for _, row in df.sort_values("PORTAFOLIO_PCT", ascending=False).iterrows():
        pct  = float(row.get("PORTAFOLIO_PCT", 0))
        col  = pct_color(pct)
        icon = pct_icon(pct)
        skus80  = row.get("SKUs_faltan_para_80_ENT", []) or []
        skus100 = row.get("SKUs_faltan_para_100_ENT", []) or []
        extras  = [s for s in skus100 if s not in skus80]
        vname   = VENDOR_NAMES.get(str(row.get("Vendedor_ID", "")), "")
        _f80_raw  = int(row.get("FALTAN_80_N",  0)) if pd.notna(row.get("FALTAN_80_N"))  else 0
        _f100_raw = int(row.get("FALTAN_100_N", 0)) if pd.notna(row.get("FALTAN_100_N")) else 0
        # Si ya superó el umbral, faltantes en ese nivel = 0
        f80  = 0 if pct >= 80  else _f80_raw
        f100 = 0 if pct >= 100 else _f100_raw
        tp_s = row.get("TP_SISTEMA", False)
        loc  = row.get("Localidad", "")
        freq = row.get("frecuencia", "")
        fact = fmt_ars(row.get("FACTURACION_CLIENTE"))
        seg  = str(row.get("Segmento", "")).strip().upper()
        if seg not in SEG_COLOR: seg = ""

        title = f"{icon} {row.get('Razon_Social','—')}  ·  {pct:.0f}%"
        if seg:   title += f"  ·  [{seg}]"
        if vname: title += f"  ·  {vname}"
        if loc:   title += f"  ·  {loc}"

        with st.expander(title):
            c1, c2, c3, c4, c5, c6 = st.columns(6)
            c1.metric("Portafolio", f"{pct:.0f}%")
            c2.metric("Faltan 80%", f80)
            c3.metric("Faltan 100%", f100)
            c4.metric("Facturación", fact)
            tp_badge = "<span class='bdg-g'>TP ✓</span>" if tp_s else "<span class='bdg-r'>Sin TP</span>"
            c5.markdown(f"<div style='padding-top:1.8rem'>{tp_badge}</div>", unsafe_allow_html=True)
            if seg:
                sc = SEG_COLOR[seg]
                sb = SEG_BG[seg]
                seg_labels = {"P": "Platino", "A": "Categoría A", "B": "Categoría B", "C": "Categoría C"}
                c6.markdown(
                    f"<div style='padding-top:1.8rem'>"
                    f"<span style='background:{sb};color:{sc};border:1px solid {sc}55;"
                    f"border-radius:20px;padding:0.12rem 0.7rem;font-size:0.72rem;font-weight:700'>"
                    f"Seg {seg}</span></div>",
                    unsafe_allow_html=True)

            st.markdown(progress_bar_html(pct, col, "6px"), unsafe_allow_html=True)
            st.markdown(f"""
            <div style='color:{GRAY};font-size:0.78rem;margin-top:0.5rem'>
                📍 {row.get("Direccion","")} &nbsp;·&nbsp;
                🗓️ {freq} &nbsp;·&nbsp;
                🏪 {row.get("SubCanal","—")}
            </div>""", unsafe_allow_html=True)

            if pct >= 100:
                st.markdown(f"<div style='color:{GREEN};font-size:0.78rem;font-weight:700;"
                            f"margin:0.6rem 0 0.2rem 0'>✅ Portafolio completo</div>",
                            unsafe_allow_html=True)
            elif pct >= 80:
                if extras:
                    st.markdown(f"<div style='color:{GRAY};font-size:0.73rem;font-weight:700;"
                                f"margin:0.6rem 0 0.25rem 0;text-transform:uppercase;letter-spacing:1px'>"
                                f"Hasta el 100% (faltan {len(extras)})</div>", unsafe_allow_html=True)
                    st.markdown(sku_pills(extras, "sku-d"), unsafe_allow_html=True)
            else:
                if skus80:
                    st.markdown(f"<div style='color:{ORANGE};font-size:0.73rem;font-weight:700;"
                                f"margin:0.6rem 0 0.25rem 0;text-transform:uppercase;letter-spacing:1px'>"
                                f"Para llegar al 80% (faltan {f80})</div>", unsafe_allow_html=True)
                    st.markdown(sku_pills(skus80, "sku-o"), unsafe_allow_html=True)
                if extras:
                    st.markdown(f"<div style='color:{GRAY};font-size:0.73rem;font-weight:700;"
                                f"margin:0.5rem 0 0.25rem 0;text-transform:uppercase;letter-spacing:1px'>"
                                f"Hasta el 100% (faltan {_f100_raw - f80})</div>", unsafe_allow_html=True)
                    st.markdown(sku_pills(extras, "sku-d"), unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# LOGIN
# ═══════════════════════════════════════════════════════════════════════════════
def login_page():
    inject_css()
    inject_audio()

    mark_b64     = get_mark_b64()
    wordmark_b64 = get_wordmark_b64()
    pyp_logo_b64 = get_pyp_logo_b64()

    # CSS login-específico (sidebar oculto, glow ambiental) via JS
    import streamlit.components.v1 as components
    components.html("""
    <script>
    (function() {
        try {
            var el = window.frameElement;
            if (el) {
                el.style.cssText = 'display:none!important;height:0!important;';
                var p = el.closest('.element-container') || el.parentElement;
                if (p) p.style.cssText = 'height:0!important;overflow:hidden!important;margin:0!important;padding:0!important;';
            }
        } catch(e) {}
        var doc = window.parent.document;
        if (doc.getElementById('orbit-login-css')) return;
        var s = doc.createElement('style');
        s.id = 'orbit-login-css';
        s.textContent = `
            .stApp { background: radial-gradient(60% 50% at 50% 25%, rgba(110,197,49,0.07), transparent 70%) !important; }
            [data-testid="stSidebar"] { display: none !important; }
            [data-testid="stSidebarCollapseButton"] { display: none !important; }
            .block-container { padding-top: 2rem !important; }
        `;
        doc.head.appendChild(s);
    })();
    </script>
    """, height=0, scrolling=False)

    _, cc, _ = st.columns([1, 1.15, 1])
    with cc:
        # ── Logo flotante ────────────────────────────────────────────
        if mark_b64:
            wm_html = (f"<img src='data:image/png;base64,{wordmark_b64}'"
                       f" style='height:34px;width:auto;margin-top:12px;filter:brightness(1.1)'/>"
                       if wordmark_b64 else "")
            st.markdown(f"""
            <div style='display:flex;flex-direction:column;align-items:center;margin-bottom:22px'>
                <img src='data:image/png;base64,{mark_b64}'
                     class='orbit-mark-spin'
                     style='width:112px;height:112px;
                            filter:drop-shadow(0 0 28px rgba(110,197,49,0.55));'/>
                {wm_html}
                <div style='font-size:10px;color:var(--text-3);letter-spacing:2.5px;
                            text-transform:uppercase;margin-top:10px;font-weight:500'>
                    Plataforma comercial
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            logo_b64 = get_logo_b64()
            if logo_b64:
                st.markdown(f"""
                <div style='text-align:center;margin-bottom:1rem'>
                    <img src='data:image/png;base64,{logo_b64}'
                         style='max-width:240px;filter:drop-shadow(0 0 18px rgba(110,197,49,0.6))'/>
                </div>""", unsafe_allow_html=True)

        # ── Login card ───────────────────────────────────────────────
        all_perfiles = ["— Seleccioná tu perfil —", "Gerencia"] + list(VENDOR_NAMES.values())
        perfil = st.selectbox("Perfil", all_perfiles, key="login_perfil", label_visibility="collapsed")

        # Profile mini card
        if perfil and perfil != "— Seleccioná tu perfil —":
            tag = perfil[:2].upper()
            rol_txt = "Gerencia comercial · Acceso completo" if perfil == "Gerencia" else "Vendedor/a"
            st.markdown(f"""
            <div style='padding:8px 11px;background:rgba(110,197,49,0.06);
                        border:1px solid var(--green-line);border-radius:8px;
                        display:flex;align-items:center;gap:9px;font-size:12px;
                        margin:6px 0 10px'>
                <div style='width:26px;height:26px;border-radius:6px;
                            background:rgba(110,197,49,0.15);color:var(--green);
                            display:grid;place-items:center;font-weight:600;font-size:10px;
                            flex-shrink:0'>{tag}</div>
                <div>
                    <div style='font-weight:500;color:var(--text)'>{perfil}</div>
                    <div style='color:var(--text-3);font-size:10px'>{rol_txt}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        pwd = st.text_input("Contraseña", type="password", key="login_pwd",
                            placeholder="••••••••", label_visibility="collapsed")

        st.markdown('<div class="login-btn">', unsafe_allow_html=True)
        if st.button("INGRESAR →", key="btn_login", use_container_width=True):
            if perfil == "— Seleccioná tu perfil —":
                st.warning("Elegí un perfil primero.")
            elif perfil == "Gerencia" and pwd == MGMT_PASS:
                st.session_state.update({"logged_in": True, "role": "gerencia",
                                         "vendor_id": None, "vendor_name": "Matías Torres",
                                         "nav_page": "resumen"})
                st.rerun()
            elif perfil in VENDOR_NAMES.values() and pwd == VENDOR_PASS:
                vid = next(k for k, v in VENDOR_NAMES.items() if v == perfil)
                st.session_state.update({"logged_in": True, "role": "vendor",
                                         "vendor_id": vid, "vendor_name": perfil,
                                         "nav_page": "resumen"})
                st.rerun()
            else:
                st.error("Contraseña incorrecta.")
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("""
        <div style='display:flex;justify-content:space-between;font-size:11px;
                    color:var(--text-4);margin-top:12px'>
            <span>Orbit · Tienda Perfecta</span>
            <span style='display:inline-flex;align-items:center;gap:5px'>
                <span class='live-dot' style='width:5px;height:5px;border-radius:99px;
                    background:var(--green);display:inline-block'></span>
                Conectado
            </span>
        </div>
        """, unsafe_allow_html=True)

        # ── P&P logo ─────────────────────────────────────────────────
        if pyp_logo_b64:
            st.markdown(f"""
            <div style='margin-top:22px;padding-top:18px;border-top:1px solid var(--line);
                        display:flex;flex-direction:column;align-items:center;gap:7px'>
                <div style='font-size:9px;color:var(--text-4);letter-spacing:2.2px;
                            text-transform:uppercase;font-weight:600'>Operado por</div>
                <img src='data:image/png;base64,{pyp_logo_b64}'
                     style='max-width:160px;height:auto;max-height:70px;
                            filter:drop-shadow(0 4px 16px rgba(56,110,255,0.3)) brightness(1.15) saturate(1.15)'/>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("""
    <div style='text-align:center;color:var(--text-4);font-size:10px;
                letter-spacing:1.5px;margin-top:1.5rem'>
        Orbit © 2026 · Propiedad de Torres Matías
    </div>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# VENDOR PAGE
# ═══════════════════════════════════════════════════════════════════════════════
def vendor_page(vendor_id, vendor_name):
    import traceback as _tb
    inject_css()
    inject_audio()

    try:
        # ── Carga de datos ───────────────────────────────────────────────────────
        cli, obj_tax, obj_vend, oport, foco = load_data()

        vid     = str(vendor_id)

        # Filtros por vendedor — columna puede llamarse Vendedor_ID o VendedorID
        _vcol = "Vendedor_ID" if "Vendedor_ID" in cli.columns else (
                "VendedorID"  if "VendedorID"  in cli.columns else None)
        mis = cli[cli[_vcol] == vid].copy() if _vcol else pd.DataFrame()

        mi_op   = oport[oport["VendedorID"] == vid].copy() if "VendedorID" in oport.columns else pd.DataFrame()
        mi_fc   = (foco[(foco["Scope"] == "vendedor") & (foco["VendedorID"] == vid)].copy()
                   if "Scope" in foco.columns and "VendedorID" in foco.columns else pd.DataFrame())
        obj_row = obj_vend[obj_vend["_VID"] == vid] if "_VID" in obj_vend.columns else pd.DataFrame()

        def _safe_float(df, col, idx=0, default=0.0):
            try: return float(df[col].iloc[idx])
            except Exception: return default

        obj_val  = _safe_float(obj_row, "OBJETIVO")
        acum_val = _safe_float(obj_row, "ACUMULADO")
        cumpl    = _safe_float(obj_row, "CUMPLIMIENTO_PCT")

        pct_port    = float(mis["PORTAFOLIO_PCT"].mean()) if len(mis) else 0.0
        tp_sistema  = int((mis["TP_SISTEMA"] == True).sum()) if "TP_SISTEMA" in mis.columns else 0
        _te_series  = pd.to_numeric(mis["TP_ELIGIBLE"], errors="coerce").fillna(0) if "TP_ELIGIBLE" in mis.columns else None
        tp_eligible = int(_te_series.sum()) if _te_series is not None else len(mis)
        n_oport     = len(mi_op)

        # ── Sidebar + Topbar
        render_sidebar(role="vendor", vendor_name=vendor_name)
        render_topbar(f"Mi Panel — {vendor_name}", f"Zona {vendor_name}")

        # ── KPI strip
        c1, c2, c3, c4 = st.columns(4)
        pc = pct_color(pct_port)
        cc = pct_color(cumpl)

        c1.markdown(kpi_card_html("Portafolio promedio", f"{pct_port:.0f}%",
                                  f"{len(mis)} clientes totales", pc), unsafe_allow_html=True)
        c2.markdown(kpi_card_html("Objetivo TP", f"{cumpl:.0f}%",
                                  f"{acum_val:.0f} de {obj_val:.0f} TPs", cc), unsafe_allow_html=True)
        c3.markdown(kpi_card_html("⚡ Oportunidad hoy", str(n_oport),
                                  "clientes en 60–79%", YELLOW), unsafe_allow_html=True)
        c4.markdown(kpi_card_html("TP Sistema", str(tp_sistema),
                                  f"de {tp_eligible} elegibles", GREEN), unsafe_allow_html=True)

        # ── Objetivo progress bar
        st.markdown(f"""
        <div style='margin:0.2rem 0 0.8rem 0'>
            <div style='display:flex;justify-content:space-between;color:{GRAY};
                        font-size:0.72rem;margin-bottom:0.3rem'>
                <span>Progreso objetivo mensual</span>
                <span style='color:{cc};font-weight:700'>{cumpl:.1f}% alcanzado</span>
            </div>
            {progress_bar_html(cumpl, cc, "10px")}
            <div style='display:flex;justify-content:space-between;color:{GRAY};
                        font-size:0.68rem;margin-top:0.2rem'>
                <span>0</span><span style='color:{GREEN}'>Meta: 80%</span><span>100%</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ── Tabs
        tab1, tab2, tab3 = st.tabs(["⚡  Mis oportunidades", "📋  Todos mis clientes", "🎯  Foco del día"])

        # TAB 1 – Oportunidades 60-79%
        with tab1:
            if mi_op.empty:
                st.info("Sin clientes en zona de oportunidad para la zona activa.")
            else:
                st.markdown(f"""
                <div style='color:{GRAY};font-size:0.85rem;margin:0.8rem 0'>
                    <b style='color:{YELLOW}'>{n_oport} clientes</b> a un paso del TP —
                    priorizalos hoy para maximizar tu resultado
                </div>""", unsafe_allow_html=True)

                _sort_col = "PortafolioPct" if "PortafolioPct" in mi_op.columns else (
                            mi_op.columns[0] if len(mi_op.columns) else "PortafolioPct")
                for _, row in mi_op.sort_values(_sort_col, ascending=False).iterrows():
                    pct   = float(row.get("PortafolioPct", 0))
                    col   = pct_color(pct)
                    f80   = int(row.get("Faltan80", 0)) if pd.notna(row.get("Faltan80")) else 0
                    skus80_raw = str(row.get("SKUsFaltan80", ""))
                    skus80 = [s.strip() for s in skus80_raw.split(" | ") if s.strip()] if pd.notna(row.get("SKUsFaltan80")) else []
                    tp_a  = str(row.get("TP_Aplica", "")).upper() == "SI"
                    loc   = str(row.get("Localidad", ""))
                    icon  = "⚡" if pct >= 70 else "⚠️"

                    with st.expander(f"{icon} {row.get('RazonSocial', '—')}  ·  {pct:.0f}%  ·  {loc}"):
                        d1, d2, d3 = st.columns([1, 1, 2])
                        d1.metric("Portafolio", f"{pct:.0f}%")
                        d2.metric("SKUs para 80%", f80)
                        with d3:
                            badge = "<span class='bdg-g'>TP Aplica ✓</span>" if tp_a else "<span class='bdg-r'>No aplica TP</span>"
                            st.markdown(f"""
                            <div style='padding-top:1.8rem'>
                                {badge}
                                <div style='color:{GRAY};font-size:0.75rem;margin-top:0.3rem'>
                                    📍 {row.get("Direccion","")}
                                </div>
                            </div>""", unsafe_allow_html=True)

                        st.markdown(progress_bar_html(pct, col, "7px"), unsafe_allow_html=True)

                        if skus80:
                            st.markdown(f"<div style='color:{ORANGE};font-size:0.73rem;font-weight:700;"
                                        f"margin:0.6rem 0 0.3rem;text-transform:uppercase;letter-spacing:1px'>"
                                        f"Vendé esto para llegar al 80%</div>", unsafe_allow_html=True)
                            st.markdown(sku_pills(skus80, "sku-o"), unsafe_allow_html=True)

        # TAB 2 – Todos los clientes por banda
        with tab2:
            def render_band(label, color, df_band, icon):
                if df_band.empty: return
                st.markdown(f"""
                <div style='display:flex;align-items:center;gap:0.6rem;margin:1.2rem 0 0.5rem'>
                    <div style='width:5px;height:1.2rem;background:{color};border-radius:3px'></div>
                    <span style='color:{color};font-weight:800;font-size:0.9rem'>{icon} {label}</span>
                    <span style='color:{GRAY};font-size:0.8rem'>({len(df_band)} clientes)</span>
                </div>""", unsafe_allow_html=True)
                render_clientes(df_band)

            render_band("TP alcanzado (≥ 80%)",  GREEN,  mis[mis["PORTAFOLIO_PCT"] >= 80], "✅")
            render_band("Oportunidad (60–79%)",   YELLOW, mis[(mis["PORTAFOLIO_PCT"] >= 60) & (mis["PORTAFOLIO_PCT"] < 80)], "⚡")
            render_band("Recuperar (30–59%)",     ORANGE, mis[(mis["PORTAFOLIO_PCT"] >= 30) & (mis["PORTAFOLIO_PCT"] < 60)], "⚠️")
            render_band("Crítico (< 30%)",        RED,    mis[mis["PORTAFOLIO_PCT"] < 30], "🔴")

        # TAB 3 – Foco del día
        with tab3:
            if mi_fc.empty:
                st.info("Sin datos de foco de productos disponibles.")
            else:
                st.markdown(f"""
                <div style='color:{GRAY};font-size:0.85rem;margin-bottom:1rem'>
                    Los productos que más veces faltan en tus clientes de oportunidad —
                    <b style='color:{GREEN}'>llevá stock de estos hoy</b>
                </div>""", unsafe_allow_html=True)

                _cant_s  = pd.to_numeric(mi_fc["CantClientes"], errors="coerce").fillna(1)
                max_cant = _cant_s.max() or 1
                medals   = ["🥇", "🥈", "🥉"]

                for _, row in mi_fc.sort_values("Rank").iterrows():
                    rank = int(pd.to_numeric(row.get("Rank", 99), errors="coerce") or 99)
                    art  = str(row.get("Articulo", "—"))
                    cant = int(pd.to_numeric(row.get("CantClientes", 0), errors="coerce") or 0)
                    bw   = max(8, int(cant / max_cant * 100))
                    med  = medals[rank - 1] if rank <= 3 else f"#{rank}"
                    col  = GREEN if rank <= 3 else DGREEN

                    st.markdown(f"""
                    <div class='ocard' style='padding:0.8rem 1.2rem;margin-bottom:0.4rem'>
                        <div style='display:flex;align-items:center;gap:1rem'>
                            <div style='font-size:1.6rem;min-width:2.4rem;text-align:center'>{med}</div>
                            <div style='flex:1'>
                                <div style='font-weight:700;font-size:0.95rem;color:{WHITE}'>{art}</div>
                                {progress_bar_html(bw, col, "5px")}
                            </div>
                            <div style='text-align:right;min-width:3rem'>
                                <div style='font-size:1.5rem;font-weight:900;color:{col}'>{cant}</div>
                                <div style='color:{GRAY};font-size:0.65rem;text-transform:uppercase'>clientes</div>
                            </div>
                        </div>
                    </div>""", unsafe_allow_html=True)

        orbit_footer()

    except Exception as _e:
        render_sidebar(role="vendor", vendor_name=vendor_name)
        render_topbar(f"Mi Panel — {vendor_name}", "Error")
        st.error(f"⚠️ Error inesperado en el panel: {_e}")
        with st.expander("🔍 Detalle técnico (enviáselo a Matías)"):
            st.code(_tb.format_exc())
        st.info("Intentá recargar la página o cerrá sesión y volvé a ingresar.")
        orbit_footer()


# ═══════════════════════════════════════════════════════════════════════════════
# MANAGEMENT PAGE
# ═══════════════════════════════════════════════════════════════════════════════
def management_page():
    inject_css()
    inject_audio()
    cli, obj_tax, obj_vend, oport, foco = load_data()

    total     = len(cli)
    tp_ok     = int((cli["TP_SISTEMA"] == True).sum())
    pct_tp    = tp_ok / total * 100 if total else 0
    pp_global = cli["PORTAFOLIO_PCT"].mean()
    n_oport   = len(oport)
    n_crit    = len(cli[cli["PORTAFOLIO_PCT"] < 30])

    t_obj  = obj_vend["OBJETIVO"].sum()
    t_acum = obj_vend["ACUMULADO"].sum()
    t_cum  = t_acum / t_obj * 100 if t_obj else 0

    # ── Sidebar + Topbar ────────────────────────────────────────────────────────
    render_sidebar(role="gerencia", vendor_name=st.session_state.get("vendor_name", "Matías Torres"))
    nav_page = st.session_state.get("nav_page", "resumen")
    render_topbar("Resumen ejecutivo", f"Panel · {total} clientes")

    # ── Drill-down data maps
    drill_df_map = {
        "port":  cli.sort_values("PORTAFOLIO_PCT"),
        "tp":    cli[cli["TP_SISTEMA"] == True].sort_values("PORTAFOLIO_PCT", ascending=False),
        "oport": cli[(cli["PORTAFOLIO_PCT"] >= 60) & (cli["PORTAFOLIO_PCT"] < 80)]
                    .sort_values("PORTAFOLIO_PCT", ascending=False),
        "crit":  cli[cli["PORTAFOLIO_PCT"] < 30].sort_values("PORTAFOLIO_PCT"),
    }
    drill_labels = {
        "port":  f"Todos los clientes ({total}) — portafolio ascendente (peores primero)",
        "tp":    f"Tienda Perfecta confirmada — {tp_ok} clientes",
        "oport": f"Zona de oportunidad 60–79% — {n_oport} clientes",
        "crit":  f"Clientes críticos < 30% — {n_crit} clientes",
    }

    # ── Hero KPI cards (clickables — siempre visibles) ──────────────────────────
    drill = st.session_state.get("mgmt_drill")
    c1, c2, c3, c4, c5 = st.columns(5)

    kpi_data = [
        (c1, "port",  "Portafolio Global",  f"{pp_global:.0f}%", f"{total} clientes",                pct_color(pp_global)),
        (c2, "tp",    "TP Confirmados",       f"{tp_ok}",           f"{pct_tp:.0f}% del padrón",        GREEN if pct_tp >= 50 else YELLOW),
        (c3, None,    "Objetivo TP Dist.",   f"{t_cum:.0f}%",      f"{t_acum:.0f}/{t_obj:.0f} TPs",    pct_color(t_cum)),
        (c4, "oport", "Oportunidad 60-79%", f"{n_oport}",         "clientes en zona",                  YELLOW),
        (c5, "crit",  "Críticos < 30%",     f"{n_crit}",          "requieren atención",                RED),
    ]

    for col, dk, lbl, val, sub, color in kpi_data:
        is_active = (drill == dk) if dk else False
        card_class = f"kpi-{dk}" if dk else ""
        col.markdown(kpi_card_html(lbl, val, sub, color, card_class, is_active), unsafe_allow_html=True)
        if dk:
            # Botón invisible sobre la card (ver CSS :has selector)
            if col.button("", key=f"drill_{dk}", use_container_width=True):
                st.session_state["mgmt_drill"] = None if is_active else dk
                st.rerun()

    # ── Drill-down panel ────────────────────────────────────────────────────────
    drill = st.session_state.get("mgmt_drill")
    if drill and drill in drill_df_map:
        drill_df = drill_df_map[drill]
        close_col, _ = st.columns([6, 1])
        st.markdown(f"""
        <div style='background:rgba(110,197,49,0.06);border:1px solid rgba(110,197,49,0.32);
                    border-radius:12px;padding:12px 18px;margin:12px 0 6px;
                    display:flex;align-items:center;gap:12px;animation:fade-in .3s ease'>
            <span style='width:6px;height:6px;border-radius:99px;background:var(--green);
                         display:inline-block;flex-shrink:0'></span>
            <div style='flex:1'>
                <div style='color:rgba(110,197,49,0.65);font-size:10px;text-transform:uppercase;
                            letter-spacing:2px;font-weight:600;margin-bottom:2px'>Detalle activo</div>
                <div style='color:var(--text);font-weight:500;font-size:14px'>{drill_labels[drill]}</div>
            </div>
        </div>""", unsafe_allow_html=True)
        render_clientes(drill_df)
        st.markdown("<hr>", unsafe_allow_html=True)

    # ── Contenido según nav del sidebar ────────────────────────────────────────
    if nav_page in ("resumen", "", None):
        # ── RESUMEN ────────────────────────────────────────────────────────────
        col_a, col_b = st.columns(2)
        with col_a:
            section_label("Cumplimiento objetivo por vendedor")
            st.plotly_chart(chart_vendor_cumplimiento(obj_vend),
                            use_container_width=True, config={"displayModeBar": False})
        with col_b:
            section_label("Distribución de portafolio")
            st.plotly_chart(chart_portafolio_pie(cli),
                            use_container_width=True, config={"displayModeBar": False})

        # ── Facturación TP vs No TP ────────────────────────────────────────────
        has_fact = "FACTURACION_CLIENTE" in cli.columns
        has_kg   = "KILOS_CLIENTE" in cli.columns
        if has_fact:
            cli_tp    = cli[cli["TP_SISTEMA"] == True]
            cli_notp  = cli[cli["TP_SISTEMA"] != True]
            fact_tp   = pd.to_numeric(cli_tp["FACTURACION_CLIENTE"],   errors="coerce").dropna()
            fact_notp = pd.to_numeric(cli_notp["FACTURACION_CLIENTE"], errors="coerce").dropna()
            avg_tp   = fact_tp.mean()   if len(fact_tp)   else 0
            avg_notp = fact_notp.mean() if len(fact_notp) else 0
            diff_pct = (avg_tp / avg_notp - 1) * 100 if avg_notp else 0

            kg_tp_avg = kg_notp_avg = diff_kg_pct = None
            if has_kg:
                kg_tp   = pd.to_numeric(cli_tp["KILOS_CLIENTE"],   errors="coerce").dropna()
                kg_notp = pd.to_numeric(cli_notp["KILOS_CLIENTE"], errors="coerce").dropna()
                kg_tp_avg   = kg_tp.mean()   if len(kg_tp)   else 0
                kg_notp_avg = kg_notp.mean() if len(kg_notp) else 0
                diff_kg_pct = (kg_tp_avg / kg_notp_avg - 1) * 100 if kg_notp_avg else 0

            def _kg_row(val, color):
                if val is None:
                    return ""
                return f"""<div style='margin-top:8px;padding-top:8px;border-top:1px solid var(--line)'>
                    <div style='font-size:9px;color:var(--text-3);text-transform:uppercase;
                                letter-spacing:1.2px;margin-bottom:3px'>Promedio kg</div>
                    <div class='num' style='font-size:18px;font-weight:600;color:{color}'>
                        {val:,.1f} <span style='font-size:12px;font-weight:400'>kg</span>
                    </div></div>"""

            section_label("Facturación promedio mensual — TP vs No TP")
            fa, fb = st.columns(2)
            with fa:
                st.markdown(f"""
                <div class='ocard ocard-green' style='padding:1rem 1.2rem'>
                    <div style='font-size:10px;color:var(--text-3);text-transform:uppercase;
                                letter-spacing:1.4px;font-weight:600;margin-bottom:10px'>
                        Cliente con TP &nbsp;<span style='opacity:.5'>({len(cli_tp)} clientes)</span>
                    </div>
                    <div style='font-size:9px;color:var(--text-3);text-transform:uppercase;
                                letter-spacing:1.2px;margin-bottom:3px'>Promedio $</div>
                    <div class='num' style='font-size:26px;font-weight:700;color:var(--green)'>
                        {fmt_ars(avg_tp)}
                    </div>
                    {_kg_row(kg_tp_avg, "var(--green)")}
                </div>""", unsafe_allow_html=True)
            with fb:
                st.markdown(f"""
                <div class='ocard ocard-yellow' style='padding:1rem 1.2rem'>
                    <div style='font-size:10px;color:var(--text-3);text-transform:uppercase;
                                letter-spacing:1.4px;font-weight:600;margin-bottom:10px'>
                        Cliente sin TP &nbsp;<span style='opacity:.5'>({len(cli_notp)} clientes)</span>
                    </div>
                    <div style='font-size:9px;color:var(--text-3);text-transform:uppercase;
                                letter-spacing:1.2px;margin-bottom:3px'>Promedio $</div>
                    <div class='num' style='font-size:26px;font-weight:700;color:var(--yellow)'>
                        {fmt_ars(avg_notp)}
                    </div>
                    {_kg_row(kg_notp_avg, "var(--yellow)")}
                </div>""", unsafe_allow_html=True)

            # Brecha TP vs No TP
            diff_kg_str = f" &nbsp;·&nbsp; <span class='num' style='color:var(--green);font-weight:700'>+{diff_kg_pct:.0f}%</span> más en kg" if diff_kg_pct is not None else ""
            st.markdown(f"""
            <div style='background:linear-gradient(135deg,rgba(110,197,49,0.08),rgba(110,197,49,0.03));
                        border:1px solid var(--green-line);border-radius:10px;
                        padding:10px 16px;margin-top:6px;
                        display:flex;align-items:center;gap:14px;flex-wrap:wrap'>
                <span style='font-size:18px'>📈</span>
                <div>
                    <div style='font-size:10px;color:var(--text-3);text-transform:uppercase;
                                letter-spacing:1.3px;font-weight:600;margin-bottom:2px'>Brecha TP vs No TP · mes en curso</div>
                    <div style='font-size:13px;color:var(--text)'>
                        Un cliente TP compra
                        <span class='num' style='color:var(--green);font-weight:700;font-size:15px'>
                            +{diff_pct:.0f}%
                        </span> más en ${diff_kg_str}
                    </div>
                </div>
            </div>""", unsafe_allow_html=True)

        section_label("Objetivos por taxonomía")
        t_cols = st.columns(len(obj_tax))
        for col, (_, row) in zip(t_cols, obj_tax.iterrows()):
            c  = pct_color(float(row.get("CUMPLIMIENTO_PCT", 0)))
            cm = float(row.get("CUMPLIMIENTO_PCT", 0))
            ob = float(row.get("OBJETIVO", 0))
            ac = float(row.get("ACUMULADO", 0))
            rd = float(row.get("REAL_DIA", 0))
            col.markdown(f"""
            <div class='ocard' style='text-align:center;border-top:3px solid {c}'>
                <div style='color:{GRAY};font-size:0.65rem;text-transform:uppercase;
                            letter-spacing:1.5px;margin-bottom:0.3rem'>
                    Taxonomía {row["TAXONOMIA"]}</div>
                <div style='font-size:2.5rem;font-weight:900;color:{c}'>{cm:.0f}%</div>
                <div style='color:{GRAY};font-size:0.75rem'>{ac:.0f} / {ob:.0f} TPs</div>
                {progress_bar_html(cm, c, "6px")}
                <div style='color:{GRAY};font-size:0.7rem;margin-top:0.3rem'>
                    Real hoy: {rd:.0f}</div>
            </div>""", unsafe_allow_html=True)

        section_label("Top 10 productos foco — distribuidora")
        foco_gral = foco[foco["Scope"] == "general"].head(10)
        if not foco_gral.empty:
            fig = chart_foco_bar(foco_gral)
            if fig:
                st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    elif nav_page == "vendedores":
        # ── POR VENDEDOR ───────────────────────────────────────────────────────
        # Handle navigation from vendor row buttons (must set key BEFORE widget renders)
        if "mgmt_vend_pending" in st.session_state:
            pv = st.session_state.pop("mgmt_vend_pending")
            vend_opts = ["— Todos —"] + list(VENDOR_NAMES.values())
            if pv in vend_opts:
                st.session_state["mgmt_vend"] = pv

        vend_sel = st.selectbox("Vendedor", ["— Todos —"] + list(VENDOR_NAMES.values()),
                                key="mgmt_vend")

        # KPI real del día — total distribuidora
        t_real = int(obj_vend["REAL_DIA"].sum())
        _vend_real_html = ""
        for _, _vr in obj_vend.sort_values("_VID").iterrows():
            _rval  = int(_vr["REAL_DIA"])
            _vnom  = VENDOR_NAMES.get(str(_vr["_VID"]), str(_vr["_VID"]))
            _rcol  = GREEN if _rval > 0 else GRAY
            _vend_real_html += (
                f"<div style='text-align:center'>"
                f"<div style='color:{GRAY};font-size:0.65rem;text-transform:uppercase;"
                f"letter-spacing:1px'>{_vnom}</div>"
                f"<div style='font-size:1.6rem;font-weight:900;color:{_rcol}'>{_rval}</div>"
                f"<div style='color:{GRAY};font-size:0.62rem'>TPs hoy</div></div>"
            )
        st.markdown(f"""
        <div style='background:linear-gradient(135deg,#0D1A04,#111);
                    border:1px solid rgba(110,197,49,0.3);border-radius:12px;
                    padding:0.7rem 1.4rem;margin-bottom:0.9rem;
                    display:flex;align-items:center;gap:2rem;flex-wrap:wrap'>
            <div>
                <div style='color:rgba(110,197,49,0.6);font-size:0.62rem;text-transform:uppercase;
                            letter-spacing:2px;font-weight:700'>TPs LOGRADOS HOY — DISTRIBUIDORA</div>
                <div style='font-size:2.2rem;font-weight:900;color:{GREEN};line-height:1.1'>{t_real}</div>
            </div>
            {_vend_real_html}
        </div>""", unsafe_allow_html=True)

        if vend_sel == "— Todos —":
            section_label("Comparativa de vendedores")
            for _, vrow in obj_vend.sort_values("CUMPLIMIENTO_PCT", ascending=False).iterrows():
                vid_s  = str(vrow["_VID"])
                vname  = VENDOR_NAMES.get(vid_s, vrow.get("_VEND_LABEL", vid_s))
                cm     = float(vrow.get("CUMPLIMIENTO_PCT", 0))
                ob     = float(vrow.get("OBJETIVO", 0))
                ac     = float(vrow.get("ACUMULADO", 0))
                real_h = int(vrow.get("REAL_DIA", 0))
                c      = pct_color(cm)
                v_cli  = cli[cli["Vendedor_ID"] == vid_s]
                v_pp   = v_cli["PORTAFOLIO_PCT"].mean() if len(v_cli) else 0
                v_op   = len(oport[oport["VendedorID"] == vid_s])
                v_tp   = int((v_cli["TP_SISTEMA"] == True).sum())
                real_color = GREEN if real_h > 0 else GRAY

                rc1, rc2 = st.columns([8, 1])
                with rc1:
                    st.markdown(f"""
                    <div class='ocard' style='margin-bottom:0.5rem'>
                        <div style='display:flex;align-items:center;gap:1.2rem;flex-wrap:wrap'>
                            <div style='min-width:8rem'>
                                <div style='font-weight:800;font-size:1.05rem'>{vname}</div>
                                <div style='color:{GRAY};font-size:0.73rem'>{len(v_cli)} clientes</div>
                            </div>
                            <div style='flex:1;min-width:180px'>
                                <div style='display:flex;justify-content:space-between;
                                            color:{GRAY};font-size:0.7rem;margin-bottom:0.25rem'>
                                    <span>Objetivo TP</span>
                                    <span style='color:{c};font-weight:700'>{cm:.1f}%</span>
                                </div>
                                {progress_bar_html(cm, c, "8px")}
                                <div style='display:flex;justify-content:space-between;
                                            color:{GRAY};font-size:0.68rem;margin-top:0.2rem'>
                                    <span>Portafolio prom: <b style='color:{pct_color(v_pp)}'>{v_pp:.0f}%</b></span>
                                    <span>TP sistema: <b style='color:{GREEN}'>{v_tp}</b></span>
                                    <span>Oport: <b style='color:{YELLOW}'>{v_op}</b></span>
                                </div>
                            </div>
                            <div style='text-align:center;min-width:5rem'>
                                <div style='font-size:2rem;font-weight:900;color:{c}'>{ac:.0f}</div>
                                <div style='color:{GRAY};font-size:0.7rem'>/ {ob:.0f} TPs</div>
                            </div>
                            <div style='text-align:center;min-width:4rem;
                                        border-left:1px solid #222;padding-left:1rem'>
                                <div style='font-size:1.8rem;font-weight:900;color:{real_color}'>{real_h}</div>
                                <div style='color:{GRAY};font-size:0.62rem;text-transform:uppercase;
                                            letter-spacing:0.8px'>TPs hoy</div>
                            </div>
                        </div>
                    </div>""", unsafe_allow_html=True)
                with rc2:
                    st.markdown("<div style='padding-top:1.1rem'>", unsafe_allow_html=True)
                    if st.button("▶ Ver", key=f"vend_btn_{vid_s}",
                                 help=f"Ver clientes de {vname}"):
                        st.session_state["mgmt_vend_pending"] = vname
                        st.rerun()
                    st.markdown("</div>", unsafe_allow_html=True)
        else:
            vid    = next(k for k, v in VENDOR_NAMES.items() if v == vend_sel)
            v_cli  = cli[cli["Vendedor_ID"] == vid].copy()
            v_op   = oport[oport["VendedorID"] == vid]
            v_fc   = foco[(foco["Scope"] == "vendedor") & (foco["VendedorID"] == vid)]
            v_obj  = obj_vend[obj_vend["_VID"] == vid]
            cm     = float(v_obj["CUMPLIMIENTO_PCT"].iloc[0]) if len(v_obj) else 0
            ob     = float(v_obj["OBJETIVO"].iloc[0]) if len(v_obj) else 0
            ac     = float(v_obj["ACUMULADO"].iloc[0]) if len(v_obj) else 0
            c      = pct_color(cm)

            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Cumplimiento TP", f"{cm:.1f}%", f"{ac:.0f}/{ob:.0f}")
            m2.metric("Portafolio promedio", f"{v_cli['PORTAFOLIO_PCT'].mean():.0f}%")
            m3.metric("Oportunidades", len(v_op))
            m4.metric("TP sistema", int((v_cli["TP_SISTEMA"] == True).sum()))

            if not v_fc.empty:
                section_label(f"Foco de productos — {vend_sel}")
                fig = chart_foco_bar(v_fc)
                if fig:
                    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

            section_label(f"Clientes de {vend_sel}")
            render_clientes(v_cli)

    elif nav_page == "por_zona":
        # ── POR ZONA ───────────────────────────────────────────────────────────
        zonas = sorted(cli["Localidad"].dropna().unique())
        zona_opts = ["— Todas las zonas —"] + list(zonas)

        # Handle navigation from zone row buttons (must set key BEFORE widget renders)
        if "mgmt_zona_pending" in st.session_state:
            pz = st.session_state.pop("mgmt_zona_pending")
            if pz in zona_opts:
                st.session_state["mgmt_zona"] = pz

        zona_sel = st.selectbox("Zona / Localidad", zona_opts, key="mgmt_zona")

        if zona_sel == "— Todas las zonas —":
            section_label("Resumen por localidad — clic en ▶ Ver para ver el detalle de clientes")
            st.markdown(f"""
            <div style='font-size:11px;color:var(--text-3);margin-bottom:10px;
                        padding:7px 11px;border-left:2px solid var(--line);background:var(--surface)'>
                ⓘ &nbsp;<b>TP confirmados</b>: clientes con TP registrado en el sistema (flag ERP,
                independiente del % de portafolio del día). &nbsp;
                <b>60–79%</b>: clientes en zona de oportunidad.&nbsp;
                Un cliente puede ser TP confirmado <i>y</i> estar en 60–79% simultáneamente —
                por eso la suma puede superar el total.
            </div>""", unsafe_allow_html=True)
            zsumm = cli.groupby("Localidad").agg(
                Clientes=("Cliente", "count"),
                PP=("PORTAFOLIO_PCT", "mean"),
                TP=("TP_SISTEMA", lambda x: (x == True).sum()),
                Oport=("PORTAFOLIO_PCT", lambda x: ((x >= 60) & (x < 80)).sum()),
                Criticos=("PORTAFOLIO_PCT", lambda x: (x < 30).sum()),
            ).reset_index().sort_values("PP", ascending=False)

            for _, zrow in zsumm.iterrows():
                pp = float(zrow["PP"])
                c  = pct_color(pp)
                rc1, rc2 = st.columns([8, 1])
                with rc1:
                    st.markdown(f"""
                    <div class='ocard' style='margin-bottom:0.35rem'>
                        <div style='display:flex;align-items:center;gap:1.2rem;flex-wrap:wrap'>
                            <div style='min-width:9rem'>
                                <div style='font-weight:700;font-size:1rem'>{zrow["Localidad"]}</div>
                                <div style='color:{GRAY};font-size:0.73rem'>{int(zrow["Clientes"])} clientes</div>
                            </div>
                            <div style='flex:1;min-width:180px'>
                                <div style='display:flex;justify-content:space-between;
                                            color:{GRAY};font-size:0.7rem;margin-bottom:0.2rem'>
                                    <span>Portafolio promedio</span>
                                    <span style='color:{c};font-weight:700'>{pp:.0f}%</span>
                                </div>
                                {progress_bar_html(pp, c, "6px")}
                            </div>
                            <div style='display:flex;gap:1.8rem;font-size:0.8rem;text-align:center'>
                                <div><div style='color:{GREEN};font-weight:800;font-size:1.2rem'>{int(zrow["TP"])}</div>
                                     <div style='color:{GRAY};font-size:0.65rem'>TP sistem.</div></div>
                                <div><div style='color:{YELLOW};font-weight:800;font-size:1.2rem'>{int(zrow["Oport"])}</div>
                                     <div style='color:{GRAY};font-size:0.65rem'>60–79%</div></div>
                                <div><div style='color:{RED};font-weight:800;font-size:1.2rem'>{int(zrow["Criticos"])}</div>
                                     <div style='color:{GRAY};font-size:0.65rem'>&lt;30%</div></div>
                            </div>
                        </div>
                    </div>""", unsafe_allow_html=True)
                with rc2:
                    st.markdown("<div style='padding-top:1.1rem'>", unsafe_allow_html=True)
                    if st.button("▶ Ver", key=f"zona_btn_{zrow['Localidad']}",
                                 help=f"Ver clientes de {zrow['Localidad']}"):
                        st.session_state["mgmt_zona_pending"] = zrow["Localidad"]
                        st.rerun()
                    st.markdown("</div>", unsafe_allow_html=True)
        else:
            z_cli = cli[cli["Localidad"] == zona_sel].copy()
            z_pp  = z_cli["PORTAFOLIO_PCT"].mean()
            z_tp  = int((z_cli["TP_SISTEMA"] == True).sum())
            z_op  = len(oport[oport["Localidad"] == zona_sel]) if "Localidad" in oport.columns else "—"
            z_crit = len(z_cli[z_cli["PORTAFOLIO_PCT"] < 30])
            z_op2  = len(z_cli[(z_cli["PORTAFOLIO_PCT"] >= 60) & (z_cli["PORTAFOLIO_PCT"] < 80)])

            z1, z2, z3, z4, z5 = st.columns(5)
            z1.metric("Portafolio promedio", f"{z_pp:.0f}%")
            z2.metric("TP confirmados", z_tp,
                      help="Clientes con TP_SISTEMA=True en el ERP (flag independiente del % de portafolio)")
            z3.metric("Total clientes", len(z_cli))
            z4.metric("En zona 60–79%", z_op2,
                      help="Clientes con portafolio entre 60 y 79% — a un paso del TP")
            z5.metric("Críticos <30%", z_crit)

            section_label(f"Clientes en {zona_sel}")
            render_clientes(z_cli)

    elif nav_page == "clientes":
        # ── CLIENTES ───────────────────────────────────────────────────────────
        search = st.text_input("🔍 Buscar por nombre o código",
                               placeholder="Escribí el nombre o ID del cliente...",
                               key="mgmt_search")

        if search and len(search) >= 2:
            hits = cli[
                cli["Razon_Social"].str.contains(search, case=False, na=False) |
                cli["Cliente"].astype(str).str.contains(search, na=False)
            ]
            st.markdown(f"<div style='color:{GRAY};font-size:0.8rem;margin-bottom:0.5rem'>"
                        f"{len(hits)} resultado(s) para «{search}»</div>", unsafe_allow_html=True)
            render_clientes(hits)
        else:
            section_label("Clientes más críticos (portafolio < 30%) — Top 20")
            criticos = cli[cli["PORTAFOLIO_PCT"] < 30].sort_values("PORTAFOLIO_PCT").head(20)
            render_clientes(criticos)

            section_label("Clientes en zona de oportunidad (60–79%) — Top 20")
            opport_top = cli[(cli["PORTAFOLIO_PCT"] >= 60) & (cli["PORTAFOLIO_PCT"] < 80)]\
                .sort_values("PORTAFOLIO_PCT", ascending=False).head(20)
            render_clientes(opport_top)

    orbit_footer()


# ═══════════════════════════════════════════════════════════════════════════════
# ROUTER
# ═══════════════════════════════════════════════════════════════════════════════
def main():
    if not st.session_state.get("logged_in"):
        login_page()
    elif st.session_state.get("role") == "gerencia":
        management_page()
    elif st.session_state.get("role") == "vendor":
        vendor_page(st.session_state["vendor_id"], st.session_state["vendor_name"])
    else:
        login_page()


if __name__ == "__main__":
    main()
