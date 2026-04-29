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
BASE    = os.path.dirname(os.path.abspath(__file__))
ASSETS  = os.path.join(BASE, "assets")
DATA    = os.path.join(BASE, "output")
XLSX    = os.path.join(DATA, "Control_TP_Portafolio_PyP.xlsx")
CSVDIR  = os.path.join(DATA, "APPSHEET")
CFG     = os.path.join(BASE, "config_app.json")
LOGO    = os.path.join(ASSETS, "Orbit Tienda Perfecta.png")

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
    initial_sidebar_state="collapsed",
)

# ─── Logo b64 ──────────────────────────────────────────────────────────────────
@st.cache_data
def get_logo_b64():
    if os.path.exists(LOGO):
        with open(LOGO, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return ""

@st.cache_data
def get_company_logo_b64():
    if os.path.exists(COMPANY_LOGO):
        with open(COMPANY_LOGO, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return ""


# ─── CSS ───────────────────────────────────────────────────────────────────────
def inject_css():
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

    @keyframes glow-pulse {{
        0%, 100% {{ box-shadow: 0 0 8px rgba(110,197,49,0.15); }}
        50%       {{ box-shadow: 0 0 22px rgba(110,197,49,0.35); }}
    }}
    @keyframes border-glow {{
        0%, 100% {{ border-color: rgba(110,197,49,0.25); }}
        50%       {{ border-color: rgba(110,197,49,0.6); }}
    }}
    @keyframes fade-in {{
        from {{ opacity:0; transform:translateY(8px); }}
        to   {{ opacity:1; transform:translateY(0); }}
    }}
    @keyframes shimmer {{
        0%   {{ background-position: -400px 0; }}
        100% {{ background-position: 400px 0; }}
    }}

    html, body, [class*="css"] {{
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
        background-color: {BLACK} !important;
        color: {WHITE};
    }}
    .stApp {{ background-color: {BLACK}; animation: fade-in 0.4s ease; }}
    #MainMenu, footer, header {{ visibility: hidden; }}
    .block-container {{ padding-top: 0 !important; padding-bottom: 0; max-width: 1440px; }}

    /* ── Executive header bar ─────────────────────────────────────── */
    .orbit-header-bar {{
        background: linear-gradient(135deg, #0C1A02 0%, #131a08 40%, #101208 70%, #0A0A0A 100%);
        border-bottom: 1px solid rgba(110,197,49,0.28);
        padding: 0.85rem 1.6rem;
        margin: 0 -4rem 1.4rem -4rem;
        display: flex;
        align-items: center;
        gap: 1.2rem;
        position: relative;
        box-shadow: 0 4px 32px rgba(0,0,0,0.6), 0 1px 0 rgba(110,197,49,0.15);
    }}
    .orbit-header-bar::after {{
        content: '';
        position: absolute;
        bottom: 0; left: 0; right: 0;
        height: 1px;
        background: linear-gradient(90deg,
            transparent 0%, rgba(110,197,49,0.5) 30%,
            rgba(110,197,49,0.8) 50%, rgba(110,197,49,0.5) 70%,
            transparent 100%);
    }}
    .orbit-header-logo {{
        height: 58px;
        width: auto;
        filter: brightness(1.55) drop-shadow(0 0 10px rgba(110,197,49,0.55));
        transition: filter 0.3s ease;
        flex-shrink: 0;
    }}
    .orbit-header-logo:hover {{
        filter: brightness(1.8) drop-shadow(0 0 16px rgba(110,197,49,0.8));
    }}
    .orbit-clogo {{
        height: 48px;
        width: auto;
        flex-shrink: 0;
        opacity: 0.85;
        filter: drop-shadow(0 2px 6px rgba(0,0,0,0.4));
        transition: opacity 0.3s ease;
    }}
    .orbit-clogo:hover {{ opacity: 1; }}
    .orbit-header-subtitle {{
        font-size: 0.72rem;
        font-weight: 600;
        color: rgba(110,197,49,0.65);
        text-transform: uppercase;
        letter-spacing: 2.5px;
        flex: 1;
    }}

    /* ── Slim header action buttons ───────────────────────────────── */
    .orbit-action-row {{
        display: flex;
        align-items: center;
        gap: 0.5rem;
        flex-shrink: 0;
    }}
    .orbit-btn-slim {{
        background: transparent;
        border: 1px solid #2A2A2A;
        color: #666;
        border-radius: 20px;
        padding: 0.28rem 0.9rem;
        font-size: 0.75rem;
        font-weight: 500;
        cursor: pointer;
        transition: all 0.22s ease;
        font-family: 'Inter', sans-serif;
        letter-spacing: 0.3px;
        white-space: nowrap;
    }}
    .orbit-btn-slim:hover {{
        border-color: {GREEN};
        color: {GREEN};
        background: rgba(110,197,49,0.07);
        box-shadow: 0 0 12px rgba(110,197,49,0.2);
        transform: translateY(-1px);
    }}
    .orbit-btn-exit {{
        border-color: #2A2A2A;
        color: #555;
    }}
    .orbit-btn-exit:hover {{
        border-color: {RED};
        color: {RED};
        background: rgba(232,75,75,0.07);
        box-shadow: 0 0 12px rgba(232,75,75,0.2);
    }}

    /* ── Default buttons — slim/subtle (header actions, etc.) ───── */
    .stButton > button {{
        background: transparent;
        color: #777;
        border: 1px solid #2A2A2A;
        border-radius: 20px;
        padding: 0.28rem 0.85rem;
        font-size: 0.75rem;
        font-weight: 500;
        font-family: 'Inter', sans-serif;
        letter-spacing: 0.3px;
        transition: all 0.22s ease;
        white-space: nowrap;
    }}
    .stButton > button:hover {{
        border-color: {GREEN};
        color: {GREEN};
        background: rgba(110,197,49,0.07);
        box-shadow: 0 0 12px rgba(110,197,49,0.2);
        transform: translateY(-2px);
    }}
    .stButton > button:active {{ transform: translateY(0); }}

    /* ── INGRESAR button (login only) ────────────────────────────── */
    .login-btn .stButton > button {{
        background: linear-gradient(135deg, {GREEN} 0%, {DGREEN} 100%);
        color: {BLACK};
        font-weight: 800;
        font-size: 0.9rem;
        letter-spacing: 1.5px;
        border: none;
        border-radius: 10px;
        padding: 0.7rem 2rem;
        width: 100%;
        transition: all 0.25s cubic-bezier(.4,0,.2,1);
        text-transform: uppercase;
        position: relative;
        overflow: hidden;
    }}
    .login-btn .stButton > button::before {{
        content: '';
        position: absolute;
        top: 0; left: -100%;
        width: 100%; height: 100%;
        background: linear-gradient(90deg, transparent,
            rgba(255,255,255,0.12), transparent);
        transition: left 0.4s ease;
    }}
    .login-btn .stButton > button:hover::before {{ left: 100%; }}
    .login-btn .stButton > button:hover {{
        background: linear-gradient(135deg, #7ED348 0%, {GREEN} 100%);
        transform: translateY(-3px);
        box-shadow: 0 8px 28px rgba(110,197,49,0.4),
                    0 2px 8px rgba(110,197,49,0.2);
    }}
    .login-btn .stButton > button:active {{ transform: translateY(-1px); }}

    /* ── Inputs ───────────────────────────────────────────────────── */
    .stTextInput > div > div > input {{
        background-color: #141414 !important;
        color: {WHITE} !important;
        border: 1.5px solid #252525 !important;
        border-radius: 10px !important;
        font-size: 1rem !important;
        transition: border-color 0.2s, box-shadow 0.2s !important;
    }}
    .stTextInput > div > div > input:focus {{
        border-color: {GREEN} !important;
        box-shadow: 0 0 0 3px rgba(110,197,49,0.15) !important;
    }}
    .stSelectbox > div > div {{
        background-color: #141414 !important;
        color: {WHITE} !important;
        border: 1.5px solid #252525 !important;
        border-radius: 10px !important;
    }}
    .stSelectbox label, .stTextInput label {{
        color: {GRAY} !important;
        font-size: 0.75rem !important;
        text-transform: uppercase;
        letter-spacing: 1.2px;
        font-weight: 700;
    }}

    /* ── Metrics ──────────────────────────────────────────────────── */
    [data-testid="stMetricValue"] {{
        font-size: 2rem !important;
        font-weight: 800 !important;
        color: {WHITE} !important;
    }}
    [data-testid="stMetricLabel"] {{
        color: {GRAY} !important;
        font-size: 0.7rem !important;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-weight: 700;
    }}

    /* ── Tabs ─────────────────────────────────────────────────────── */
    .stTabs [data-baseweb="tab-list"] {{
        background-color: #111;
        border-radius: 12px;
        padding: 4px;
        gap: 3px;
        border: 1px solid {BORDER};
    }}
    .stTabs [data-baseweb="tab"] {{
        background-color: transparent;
        color: {GRAY};
        border-radius: 9px;
        font-weight: 600;
        font-size: 0.83rem;
        padding: 0.48rem 1.1rem;
        border: none;
        transition: color 0.2s;
    }}
    .stTabs [data-baseweb="tab"]:hover {{ color: {LGRAY}; }}
    .stTabs [aria-selected="true"] {{
        background: linear-gradient(135deg, {GREEN}, {DGREEN}) !important;
        color: {BLACK} !important;
        box-shadow: 0 2px 10px rgba(110,197,49,0.3);
    }}

    /* ── Expanders ────────────────────────────────────────────────── */
    details {{
        background: {CARD} !important;
        border: 1px solid {BORDER} !important;
        border-radius: 10px !important;
        margin-bottom: 0.4rem !important;
        transition: border-color 0.2s, box-shadow 0.2s !important;
    }}
    details:hover {{
        border-color: rgba(110,197,49,0.3) !important;
        box-shadow: 0 2px 16px rgba(110,197,49,0.06) !important;
    }}
    details summary {{
        color: {WHITE} !important;
        font-weight: 600 !important;
        padding: 0.7rem 1rem !important;
        cursor: pointer;
        transition: color 0.2s;
    }}
    details summary:hover {{ color: {GREEN} !important; }}
    details[open] summary {{ border-bottom: 1px solid {BORDER}; color: {GREEN} !important; }}
    details > div {{ padding: 0.8rem 1rem !important; }}

    /* ── Orbit cards ──────────────────────────────────────────────── */
    .ocard {{
        background: {CARD};
        border: 1px solid {BORDER};
        border-radius: 14px;
        padding: 1.2rem 1.4rem;
        margin-bottom: 0.7rem;
        transition: transform 0.22s ease, box-shadow 0.22s ease, border-color 0.22s ease;
        animation: fade-in 0.35s ease;
    }}
    .ocard:hover {{
        transform: translateY(-3px);
        box-shadow: 0 8px 28px rgba(110,197,49,0.1);
        border-color: rgba(110,197,49,0.25) !important;
    }}
    .ocard-green  {{ border-left: 4px solid {GREEN} !important; }}
    .ocard-yellow {{ border-left: 4px solid {YELLOW} !important; }}
    .ocard-orange {{ border-left: 4px solid {ORANGE} !important; }}
    .ocard-red    {{ border-left: 4px solid {RED} !important; }}

    /* ── Section label ────────────────────────────────────────────── */
    .section-label {{
        font-size: 0.68rem;
        font-weight: 700;
        color: rgba(110,197,49,0.55);
        text-transform: uppercase;
        letter-spacing: 2.5px;
        margin: 1.4rem 0 0.7rem 0;
        padding-bottom: 0.4rem;
        border-bottom: 1px solid {BORDER};
    }}

    /* ── Footer ───────────────────────────────────────────────────── */
    .orbit-footer {{
        text-align: center;
        color: #2E2E2E;
        font-size: 0.7rem;
        padding: 2rem 0 0.5rem 0;
        margin-top: 2rem;
        border-top: 1px solid {BORDER};
        letter-spacing: 1px;
    }}

    /* ── SKU pills ────────────────────────────────────────────────── */
    .sku-g {{
        display: inline-block; background: #0F1F00; color: {GREEN};
        border: 1px solid {GREEN}55; border-radius: 20px;
        padding: 0.2rem 0.65rem; font-size: 0.75rem; margin: 2px;
        transition: all 0.18s ease; cursor: default;
    }}
    .sku-g:hover {{ background: rgba(110,197,49,0.15); transform: scale(1.04);
                   box-shadow: 0 2px 8px rgba(110,197,49,0.2); }}
    .sku-o {{
        display: inline-block; background: #1F0F00; color: {ORANGE};
        border: 1px solid {ORANGE}55; border-radius: 20px;
        padding: 0.2rem 0.65rem; font-size: 0.75rem; margin: 2px;
        transition: all 0.18s ease; cursor: default;
    }}
    .sku-o:hover {{ background: rgba(232,122,0,0.15); transform: scale(1.04); }}
    .sku-d {{
        display: inline-block; background: #1A1A1A; color: {GRAY};
        border: 1px solid {BORDER}; border-radius: 20px;
        padding: 0.2rem 0.65rem; font-size: 0.75rem; margin: 2px;
        transition: all 0.18s ease; cursor: default;
    }}
    .sku-d:hover {{ background: #222; color: {LGRAY}; }}

    /* ── Badges ───────────────────────────────────────────────────── */
    .bdg-g {{ display:inline-block; background:rgba(110,197,49,0.12); color:{GREEN};
               border:1px solid {GREEN}44; border-radius:20px; padding:0.12rem 0.7rem;
               font-size:0.72rem; font-weight:700; }}
    .bdg-r {{ display:inline-block; background:rgba(232,75,75,0.12); color:{RED};
               border:1px solid {RED}44; border-radius:20px; padding:0.12rem 0.7rem;
               font-size:0.72rem; font-weight:700; }}
    .bdg-y {{ display:inline-block; background:rgba(240,192,0,0.12); color:{YELLOW};
               border:1px solid {YELLOW}44; border-radius:20px; padding:0.12rem 0.7rem;
               font-size:0.72rem; font-weight:700; }}
    .bdg-o {{ display:inline-block; background:rgba(232,122,0,0.12); color:{ORANGE};
               border:1px solid {ORANGE}44; border-radius:20px; padding:0.12rem 0.7rem;
               font-size:0.72rem; font-weight:700; }}

    /* ── Divider ──────────────────────────────────────────────────── */
    hr {{ border-color: {BORDER} !important; margin: 0.6rem 0 1rem 0 !important; }}

    /* ── Progress ─────────────────────────────────────────────────── */
    .stProgress > div > div > div > div {{
        background: linear-gradient(90deg, {GREEN}, {DGREEN});
    }}
    </style>
    """, unsafe_allow_html=True)


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
                        "FACTURACION_CLIENTE", "KILOS_CLIENTE"]),
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

def kpi_card_html(label, value, sub, color):
    return f"""
    <div class='ocard' style='text-align:center;border-color:{color}80;border-top:3px solid {color}'>
        <div style='color:{GRAY};font-size:0.65rem;text-transform:uppercase;letter-spacing:1.5px;margin-bottom:0.3rem'>{label}</div>
        <div style='font-size:2.4rem;font-weight:900;color:{color};line-height:1.1'>{value}</div>
        <div style='color:{GRAY};font-size:0.75rem;margin-top:0.2rem'>{sub}</div>
    </div>"""

def sku_pills(lst, css_class="sku-g"):
    if not lst: return ""
    return " ".join(f"<span class='{css_class}'>{s}</span>" for s in lst)

def section_label(text):
    st.markdown(f"<div class='section-label'>{text}</div>", unsafe_allow_html=True)

def orbit_footer():
    st.markdown("<div class='orbit-footer'>Orbit © 2026 · Propiedad de Torres Matías</div>",
                unsafe_allow_html=True)

def page_header(subtitle, show_logout=True, logout_key="logout"):
    logo_b64    = get_logo_b64()
    clogo_b64   = get_company_logo_b64()

    orbit_html = (
        f"<img src='data:image/png;base64,{logo_b64}' class='orbit-header-logo' />"
        if logo_b64 else
        "<span style='font-size:1.6rem;font-weight:900;color:#6EC531;letter-spacing:2px'>ORBIT</span>"
    )
    clogo_html = (
        f"<img src='data:image/png;base64,{clogo_b64}' class='orbit-clogo' />"
        if clogo_b64 else ""
    )

    st.markdown(f"""
    <div class="orbit-header-bar">
        {orbit_html}
        <div style='display:flex;flex-direction:column;flex:1;min-width:0'>
            <div style='font-size:1.05rem;font-weight:800;color:#FFFFFF;letter-spacing:1px'>
                ORBIT · TIENDA PERFECTA
            </div>
            <div class="orbit-header-subtitle">{subtitle}</div>
        </div>
        {clogo_html}
    </div>
    """, unsafe_allow_html=True)

    if show_logout:
        _, col_btns = st.columns([9, 1])
        with col_btns:
            bc1, bc2 = st.columns(2)
            with bc1:
                if st.button("🔄", key=f"refresh_{logout_key}", help="Actualizar datos"):
                    load_data.clear()
                    st.rerun()
            with bc2:
                if st.button("✕", key=logout_key, help="Cerrar sesión"):
                    for k in list(st.session_state.keys()):
                        del st.session_state[k]
                    st.rerun()


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
    st.markdown("<div style='height:4rem'></div>", unsafe_allow_html=True)

    _, cc, _ = st.columns([1, 1.1, 1])
    with cc:
        logo_b64 = get_logo_b64()
        if logo_b64:
            st.markdown(f"""
            <div style='text-align:center;margin-bottom:0.5rem'>
                <img src='data:image/png;base64,{logo_b64}'
                     style='max-width:260px;width:100%;
                            filter:brightness(1.55) drop-shadow(0 0 14px rgba(110,197,49,0.6));'/>
            </div>""", unsafe_allow_html=True)
        elif os.path.exists(LOGO):
            st.image(LOGO, use_container_width=True)

        st.markdown(f"""
        <div style='text-align:center;margin:1.2rem 0 1.8rem 0'>
            <div style='color:{GRAY};font-size:0.75rem;letter-spacing:4px;
                        text-transform:uppercase;font-weight:600'>Plataforma Comercial</div>
        </div>
        """, unsafe_allow_html=True)

        with st.container():
            st.markdown(f"<div class='ocard'>", unsafe_allow_html=True)

            vendor_options = ["— Seleccioná tu perfil —", "Gerencia"] + list(VENDOR_NAMES.values())
            perfil = st.selectbox("Perfil", vendor_options, key="login_perfil")
            pwd    = st.text_input("Contraseña", type="password", key="login_pwd",
                                   placeholder="••••••••")

            st.markdown("<div class='login-btn'>", unsafe_allow_html=True)
            if st.button("INGRESAR →", key="btn_login"):
                if perfil == "Gerencia" and pwd == MGMT_PASS:
                    st.session_state.update({"logged_in": True, "role": "gerencia",
                                             "vendor_id": None, "vendor_name": "Gerencia"})
                    st.rerun()
                elif perfil in VENDOR_NAMES.values() and pwd == VENDOR_PASS:
                    vid = next(k for k, v in VENDOR_NAMES.items() if v == perfil)
                    st.session_state.update({"logged_in": True, "role": "vendor",
                                             "vendor_id": vid, "vendor_name": perfil})
                    st.rerun()
                elif perfil == "— Seleccioná tu perfil —":
                    st.warning("Elegí tu perfil primero.")
                else:
                    st.error("Contraseña incorrecta. Volvé a intentarlo.")
            st.markdown("</div>", unsafe_allow_html=True)  # close login-btn

            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown(f"""
        <div style='text-align:center;color:#333;font-size:0.7rem;margin-top:2rem'>
            Orbit © 2026 · Propiedad de Torres Matías
        </div>""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# VENDOR PAGE
# ═══════════════════════════════════════════════════════════════════════════════
def vendor_page(vendor_id, vendor_name):
    inject_css()
    cli, obj_tax, obj_vend, oport, foco = load_data()

    vid     = str(vendor_id)
    mis     = cli[cli["Vendedor_ID"] == vid].copy()
    mi_op   = oport[oport["VendedorID"] == vid].copy()
    mi_fc   = foco[(foco["Scope"] == "vendedor") & (foco["VendedorID"] == vid)].copy()
    obj_row = obj_vend[obj_vend["_VID"] == vid]

    obj_val  = float(obj_row["OBJETIVO"].iloc[0])  if len(obj_row) else 0
    acum_val = float(obj_row["ACUMULADO"].iloc[0]) if len(obj_row) else 0
    cumpl    = float(obj_row["CUMPLIMIENTO_PCT"].iloc[0]) if len(obj_row) else 0

    pct_port   = mis["PORTAFOLIO_PCT"].mean() if len(mis) else 0
    tp_sistema = int((mis["TP_SISTEMA"] == True).sum())
    tp_eligible= int(mis["TP_ELIGIBLE"].sum())
    n_oport    = len(mi_op)

    # ── Header
    page_header(f"Zona {vendor_name}  ·  {datetime.now().strftime('%A %d/%m').capitalize()}",
                logout_key="vend_logout")

    # ── KPI strip
    c1, c2, c3, c4 = st.columns(4)
    pc = pct_color(pct_port)
    cc = pct_color(cumpl)

    c1.markdown(kpi_card_html("Portafolio promedio", f"{pct_port:.0f}%",
                              f"{len(mis)} clientes totales", pc), unsafe_allow_html=True)
    c2.markdown(kpi_card_html("Objetivo TP",f"{cumpl:.0f}%",
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

            for _, row in mi_op.sort_values("PortafolioPct", ascending=False).iterrows():
                pct   = float(row.get("PortafolioPct", 0))
                col   = pct_color(pct)
                f80   = int(row.get("Faltan80", 0)) if pd.notna(row.get("Faltan80")) else 0
                skus80_raw = str(row.get("SKUsFaltan80", ""))
                skus80 = [s.strip() for s in skus80_raw.split(" | ") if s.strip()] if pd.notna(row.get("SKUsFaltan80")) else []
                tp_a  = str(row.get("TP_Aplica", "")).upper() == "SI"
                loc   = str(row.get("Localidad", ""))
                icon  = "⚡" if pct >= 70 else "⚠️"

                with st.expander(f"{icon} {row['RazonSocial']}  ·  {pct:.0f}%  ·  {loc}"):
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

            max_cant = mi_fc["CantClientes"].max()
            medals = ["🥇", "🥈", "🥉"]

            for _, row in mi_fc.sort_values("Rank").iterrows():
                rank = int(row["Rank"])
                art  = row["Articulo"]
                cant = int(row["CantClientes"])
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


# ═══════════════════════════════════════════════════════════════════════════════
# MANAGEMENT PAGE
# ═══════════════════════════════════════════════════════════════════════════════
def management_page():
    inject_css()
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

    page_header(
        f"Panel Gerencial  ·  {dia_es()}  ·  {total} clientes",
        logout_key="mgmt_logout"
    )

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

    # ── Global KPIs + Ver buttons
    drill = st.session_state.get("mgmt_drill")
    c1, c2, c3, c4, c5 = st.columns(5)

    for col, dk, lbl, val, sub, color in [
        (c1, "port",  "Portafolio Global",  f"{pp_global:.0f}%", f"{total} clientes",               pct_color(pp_global)),
        (c2, "tp",    "TP Sistema",          f"{tp_ok}",           f"{pct_tp:.0f}% del padrón",       GREEN if pct_tp >= 50 else YELLOW),
        (c3, None,    "Objetivo TP Dist.",   f"{t_cum:.0f}%",      f"{t_acum:.0f} / {t_obj:.0f} TPs", pct_color(t_cum)),
        (c4, "oport", "⚡ Oportunidad",       f"{n_oport}",         "clientes 60–79%",                 YELLOW),
        (c5, "crit",  "🔴 Críticos < 30%",   f"{n_crit}",          "requieren atención",               RED),
    ]:
        col.markdown(kpi_card_html(lbl, val, sub, color), unsafe_allow_html=True)
        if dk:
            is_active = (drill == dk)
            btn_lbl = "✕ Ocultar" if is_active else "▶ Ver clientes"
            if col.button(btn_lbl, key=f"drill_{dk}"):
                st.session_state["mgmt_drill"] = None if is_active else dk
                st.rerun()

    # ── Drill-down panel (between KPIs and tabs)
    drill = st.session_state.get("mgmt_drill")
    if drill and drill in drill_df_map:
        drill_df = drill_df_map[drill]
        st.markdown(f"""
        <div style='background:#0D1A04;border:1px solid rgba(110,197,49,0.35);
                    border-radius:12px;padding:0.75rem 1.2rem;margin:0.9rem 0 0.5rem 0;
                    display:flex;align-items:center;gap:1rem'>
            <div style='flex:1'>
                <div style='color:rgba(110,197,49,0.6);font-size:0.63rem;text-transform:uppercase;
                            letter-spacing:2.5px;font-weight:700;margin-bottom:0.15rem'>Detalle activo</div>
                <div style='color:#FFFFFF;font-weight:600;font-size:0.9rem'>{drill_labels[drill]}</div>
            </div>
        </div>""", unsafe_allow_html=True)
        render_clientes(drill_df)
        st.markdown("<hr>", unsafe_allow_html=True)

    # ── Main tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊  Resumen",
        "👥  Por Vendedor",
        "🗺️  Por Zona",
        "🔍  Clientes",
    ])

    # ── TAB 1: RESUMEN ──────────────────────────────────────────────────────────
    with tab1:
        col_a, col_b = st.columns(2)
        with col_a:
            section_label("Cumplimiento objetivo por vendedor")
            st.plotly_chart(chart_vendor_cumplimiento(obj_vend),
                            use_container_width=True, config={"displayModeBar": False})
        with col_b:
            section_label("Distribución de portafolio")
            st.plotly_chart(chart_portafolio_pie(cli),
                            use_container_width=True, config={"displayModeBar": False})

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

    # ── TAB 2: POR VENDEDOR ─────────────────────────────────────────────────────
    with tab2:
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

    # ── TAB 3: POR ZONA ─────────────────────────────────────────────────────────
    with tab3:
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
                                     <div style='color:{GRAY};font-size:0.65rem'>TP</div></div>
                                <div><div style='color:{YELLOW};font-weight:800;font-size:1.2rem'>{int(zrow["Oport"])}</div>
                                     <div style='color:{GRAY};font-size:0.65rem'>Oport.</div></div>
                                <div><div style='color:{RED};font-weight:800;font-size:1.2rem'>{int(zrow["Criticos"])}</div>
                                     <div style='color:{GRAY};font-size:0.65rem'>Críticos</div></div>
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
            z2.metric("TP sistema", z_tp)
            z3.metric("Total clientes", len(z_cli))
            z4.metric("Oportunidades", z_op2)
            z5.metric("Críticos", z_crit)

            section_label(f"Clientes en {zona_sel}")
            render_clientes(z_cli)

    # ── TAB 4: CLIENTES ─────────────────────────────────────────────────────────
    with tab4:
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
