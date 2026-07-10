"""
🌸 Katsearose's Dreamscape 🌸
"""

import streamlit as st
import streamlit.components.v1 as components
import sqlite3
import base64
import json
import datetime
import requests
from pathlib import Path

# ============================================================
# CONFIG GENERAL
# ============================================================
st.set_page_config(
    page_title="Katsearose's Dreamscape",
    page_icon="🌸",
    layout="wide",
    initial_sidebar_state="expanded",
)

DB_PATH = "otaku_bitacora.db"

SECTIONS = {
    "BL": {"label": "⋆. ̊ BL", "emoji": "💗", "link_label": "🔗 Enlace donde lo leo"},
    "BOOKS": {"label": "⋆. ̊ BOOKS", "emoji": "📚", "link_label": "🔗 Enlace donde lo leo"},
    "STUDY": {"label": "⋆. ̊ STUDY", "emoji": "📝", "link_label": "☁️ Enlace de Drive / Notion"},
}

DEFAULT_COLORS = ["#F7B8D2", "#F5D6E0", "#E7C9E9", "#D9C6EE", "#C9D6F0", "#F6E3C5", "#E4D4C0"]

# ============================================================
# CSS — estética blanco + rosa, archivadores, plaid banner, dashboard
# ============================================================
def inject_css():
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Jost:wght@400;500;600;700&family=Pinyon+Script&family=Dancing+Script:wght@600;700&family=Inter:wght@300;400;500;600;700;800&display=swap');

        html, body, [class*="css"] { font-family: 'Inter', sans-serif; font-weight: 300; }

        h1, h2, h3 {
            font-family: 'Inter', sans-serif !important;
            font-weight: 700 !important;
            letter-spacing: -0.5px;
            color: #7a3b52 !important;
        }
        h2 { font-size: 1.8em !important; }
        h3 { font-size: 1.3em !important; }
        .stTabs [data-baseweb="tab-list"] button p {
            font-family: 'Inter', sans-serif !important;
            font-size: 1.15em !important;
            font-weight: 700 !important;
        }

        .stApp {
            background:
                radial-gradient(circle, #f9d6e3 1px, transparent 1px) 0 0/26px 26px,
                #ffffff;
        }

        section[data-testid="stSidebar"] {
            background: #fff6fa;
            border: 2px dashed #f3b8d2;
            border-radius: 0 32px 32px 0;
            margin: 14px 0 14px 0;
            box-shadow: 6px 0 22px rgba(230,170,190,0.18);
        }
        section[data-testid="stSidebar"] .profile-card img {
            filter: grayscale(1);
            border-radius: 50%;
        }

        div.stButton > button {
            border-radius: 14px;
            font-weight: 600;
            border: 1px solid #f6c9dc;
            transition: transform .12s ease-in-out, box-shadow .12s ease-in-out;
        }
        div.stButton > button:hover {
            transform: translateY(-2px) scale(1.02);
            box-shadow: 0 6px 14px rgba(244,150,190,0.35);
        }
        div.stButton > button:active { transform: scale(0.90) !important; box-shadow: none !important; }

        /* ---- Perfil (sidebar) ---- */
        .profile-card {
            text-align: center;
            background: #ffffff;
            border: 2px dashed #f3b8d2;
            border-radius: 20px;
            padding: 16px 10px 12px 10px;
            margin-bottom: 14px;
        }
        .profile-name {
            font-family: 'Pinyon Script', cursive;
            font-size: 34px;
            color: #C2185B;
            font-weight: 400;
            margin-top: 2px;
        }

        /* ---- Banner tipo plaid decorativo (home) ---- */
        .plaid-banner {
            border-radius: 26px;
            padding: 34px 26px;
            margin-bottom: 22px;
            text-align: center;
            background:
                repeating-linear-gradient(45deg, rgba(255,255,255,0.55) 0 6px, transparent 6px 14px),
                repeating-linear-gradient(-45deg, rgba(198,164,150,0.35) 0 3px, transparent 3px 22px),
                linear-gradient(135deg, #f7c9dc 0%, #f6e6d8 50%, #e9d3c4 100%);
            border: 3px solid #e9c6d6;
            box-shadow: 0 10px 26px rgba(230,170,190,0.35);
        }
        .plaid-title {
            font-family: 'Dancing Script', cursive;
            font-weight: 700;
            font-size: 78px;
            color: #7a3b52;
            margin: 0;
            text-shadow: 0 2px 0 rgba(255,255,255,0.65), 0 0 18px rgba(255,255,255,0.45);
        }
        .plaid-sep { color: #a9647f; letter-spacing: 2px; margin: 4px 0; }
        .plaid-kaomoji { color: #a9647f; font-size: 15px; }

        /* ---- Hero grande del inicio (estilo Lunar Bloom) ---- */
        .hero-banner {
            border-radius: 32px 32px 0 0;
            padding: 44px 40px 24px 40px;
            margin-bottom: 0;
            text-align: center;
            position: relative;
            overflow: hidden;
            background:
                radial-gradient(circle, rgba(255,255,255,0.55) 1.5px, transparent 1.5px) 0 0/20px 20px,
                linear-gradient(135deg, #ffd6e6 0%, #ffe3ee 40%, #fff0f5 100%);
            border: 3px solid #f6c9dc;
            border-bottom: none;
            box-shadow: 0 14px 34px rgba(230,150,180,0.35);
        }
        .hero-banner::before, .hero-banner::after {
            content: "✿";
            position: absolute;
            color: rgba(255,255,255,0.6);
            font-size: 90px;
        }
        .hero-banner::before { top: -20px; left: -10px; }
        .hero-banner::after { bottom: -30px; right: -10px; }
        .hero-title {
            font-family: 'Inter', sans-serif;
            font-weight: 700;
            letter-spacing: 1px;
            font-size: 46px !important;
            color: #7a3b52;
            margin: 0;
            position: relative;
            z-index: 1;
        }
        .hero-sep { color: #a9647f; letter-spacing: 3px; margin: 6px 0; position: relative; z-index: 1; }
        .hero-kaomoji { color: #a9647f; font-size: 17px; position: relative; z-index: 1; margin-bottom: 24px; }
        .hero-tagline { color: #9b4468; font-size: 15px; margin-top: 6px; position: relative; z-index: 1; }
        .hero-clock-wrap {
            font-family: 'Inter', sans-serif;
            text-align: center;
            background: linear-gradient(135deg, #ffe3ee 0%, #fff0f5 100%);
            border-left: 3px solid #f6c9dc;
            border-right: 3px solid #f6c9dc;
            border-bottom: 3px solid #f6c9dc;
            border-radius: 0 0 32px 32px;
            box-shadow: 0 14px 34px rgba(230,150,180,0.25);
            margin-bottom: 28px;
            padding: 4px 20px 16px 20px;
        }
        .hero-clock-text { color: #9b4468; font-size: 16px; font-weight: 600; letter-spacing: 0.3px; }

        /* ---- Sidebar: nav estilo píldora (activo) ---- */
        .nav-pill-active button {
            background: linear-gradient(135deg, #f7b8d2, #f592b8) !important;
            color: white !important;
            border: none !important;
            border-radius: 50px !important;
            font-weight: 700 !important;
        }

        /* ---- Botones corazón del home ---- */
        .heart-wrap { text-align: center; }
        .heart-label {
            font-family: 'Pinyon Script', cursive;
            font-size: 34px;
            color: #9b4468;
            margin-top: -2px;
        }
        .section-cover {
            width: 100%;
            border-radius: 22px;
            object-fit: cover;
            aspect-ratio: 4/3;
            box-shadow: 0 8px 20px rgba(0,0,0,0.12);
            border: 3px solid white;
            outline: 2px solid #f6c9dc;
        }
        .section-cover-placeholder {
            width: 100%;
            aspect-ratio: 4/3;
            border-radius: 22px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 60px;
            background: linear-gradient(135deg, #ffe3ee, #fff5f8);
            border: 3px dashed #f3b8d2;
        }

        /* ---- Sidebar nav: botón activo (usa type=primary de Streamlit) ---- */
        section[data-testid="stSidebar"] button[kind="primary"] {
            background: linear-gradient(135deg, #f7b8d2, #f592b8) !important;
            color: white !important;
            border: none !important;
            border-radius: 50px !important;
            font-weight: 700 !important;
        }
        section[data-testid="stSidebar"] button[kind="secondary"] {
            background: white !important;
            border-radius: 50px !important;
        }

        /* ---- Widgets de estadísticas del inicio ---- */
        .stat-widget {
            background: white;
            border-radius: 20px;
            padding: 16px;
            text-align: center;
            box-shadow: 0 4px 14px rgba(0,0,0,0.06);
            border: 1px solid #f6d9e6;
        }
        .stat-number { font-size: 30px; font-weight: 700; color: #d9749a; font-family: 'Inter', sans-serif; }
        .stat-label { font-size: 13px; color: #a9647f; }

        /* ---- Archivador / carpeta tipo binder ---- */
        .archivador {
            position: relative;
            border-radius: 4px 16px 16px 16px;
            padding: 22px 14px 16px 14px;
            margin-top: 18px;
            margin-bottom: 6px;
            min-height: 120px;
            box-shadow: 0 6px 16px rgba(0,0,0,0.12);
            border: 2px solid rgba(0,0,0,0.05);
        }
        .archivador-tab {
            position: absolute;
            top: -18px;
            left: 14px;
            background: white;
            border: 2px dashed #d98bad;
            border-radius: 10px;
            padding: 4px 14px;
            font-size: 16px;
            font-weight: 700;
            font-family: 'Inter', sans-serif;
            color: #7a3b52;
            box-shadow: 0 2px 6px rgba(0,0,0,0.08);
        }
        .archivador-count {
            color: white;
            font-size: 12px;
            font-weight: 600;
            text-shadow: 0 1px 2px rgba(0,0,0,0.25);
        }

        /* ---- Cards de libro dentro del archivador ---- */
        .book-card {
            background: white;
            border-radius: 16px;
            padding: 12px 16px;
            margin-bottom: 9px;
            box-shadow: 0 3px 10px rgba(0,0,0,0.06);
            border-left: 7px solid #f3b8d2;
        }
        .book-title { font-weight: 700; font-size: 20px; color: #4A2E4D; font-family: 'Inter', sans-serif; }
        .stars { color: #FFC107; font-size: 15px; }
        .fav-heart { color: #FF4081; font-size: 18px; }
        .tag-chip {
            display: inline-block; padding: 2px 10px; border-radius: 12px;
            font-size: 11px; color: white; font-weight: 700;
        }

        /* ---- Tweet cards (hilo tipo diario) ---- */
        .tweet-card {
            background: #fffaf9;
            border-radius: 14px;
            padding: 12px 16px;
            margin-bottom: 10px;
            border: 1.5px dashed #eab7cc;
        }
        .tweet-date { color: #b98bc9; font-size: 11px; font-weight: 700; }

        /* ---- Dashboard widgets (estilo tipo campus/planner) ---- */
        .dash-card {
            background: white;
            border-radius: 16px;
            padding: 16px 18px;
            box-shadow: 0 3px 12px rgba(0,0,0,0.07);
            border: 1px solid #f2dbe6;
            margin-bottom: 14px;
        }
        .dash-title { font-weight: 700; color: #7a3b52; font-size: 20px; margin-bottom: 8px; font-family: 'Inter', sans-serif;}
        .badge-chip {
            display:inline-block; background:#f8d7e6; color:#a1315a;
            border-radius: 10px; padding: 2px 10px; font-size: 11px; font-weight:700;
        }

        .trash-card {
            background: #fff5f5; border: 1.5px dashed #e6a3a3;
            border-radius: 14px; padding: 10px 16px; margin-bottom: 8px;
        }

        /* ============================================================
           BENTO GRID — home discontinuo/asimétrico
           ============================================================ */
        .bento-card {
            background: white;
            border-radius: 20px;
            padding: 18px 20px;
            box-shadow: 0 4px 14px rgba(0,0,0,0.06);
            border: 1px solid #f6d9e6;
            margin-bottom: 16px;
        }
        .bento-card-title {
            font-weight: 700; font-size: 15px; color: #7a3b52;
            text-transform: uppercase; letter-spacing: 0.6px;
            margin-bottom: 12px; display:flex; justify-content:space-between; align-items:center;
        }
        div[data-testid="stTextInput"] input {
            border-radius: 20px !important;
        }
        .mini-course-card {
            background: #fff6fa; border-radius: 16px; padding: 10px 12px;
            border: 1px solid #f6d9e6; margin-bottom: 8px;
        }
        .mini-course-title { font-weight: 600; font-size: 14px; color: #4A2E4D; }
        .mini-course-meta { font-size: 11px; color: #a9647f; }
        .progress-track {
            width: 100%; height: 10px; background: #f6e0ea; border-radius: 10px; overflow: hidden;
        }
        .progress-fill {
            height: 100%; background: linear-gradient(90deg, #f7b8d2, #d9749a); border-radius: 10px;
        }
        .collection-mini {
            display:flex; align-items:center; gap: 10px; background:#fff6fa;
            border-radius: 14px; padding: 8px 10px; margin-bottom: 8px; border:1px solid #f6d9e6;
        }
        .collection-thumb {
            width: 42px; height: 42px; border-radius: 10px; object-fit: cover; flex-shrink:0;
            background: linear-gradient(135deg,#ffe3ee,#fff5f8);
        }
        .streak-card {
            text-align:center; background: linear-gradient(160deg, #fdeaf2, #fff6fa);
            border-radius: 20px; padding: 20px 16px; border: 1px solid #f6d9e6; margin-bottom: 16px;
        }
        .streak-number { font-size: 42px; font-weight: 800; color: #d9749a; line-height:1; }
        .streak-label { font-size: 12px; color: #a9647f; margin-top:4px; }
        .pill-cta {
            display:inline-block; margin-top: 12px; background: linear-gradient(135deg, #f7b8d2, #f592b8);
            color: white !important; font-weight: 700; font-size: 12px; text-decoration:none;
            padding: 8px 22px; border-radius: 50px;
        }
        .notif-item {
            display:flex; gap:10px; padding: 9px 0; border-bottom: 1px solid #f6e0ea;
        }
        .notif-item:last-child { border-bottom:none; }
        .notif-icon { font-size: 18px; }
        .notif-title { font-weight:600; font-size:13px; color:#4A2E4D; }
        .notif-meta { font-size: 11px; color:#a9647f; }
        .featured-card {
            border-radius: 20px; overflow:hidden; border:1px solid #f6d9e6;
            box-shadow: 0 6px 18px rgba(0,0,0,0.08); margin-bottom:16px; background:white;
        }
        .featured-card img { width:100%; display:block; max-height:220px; object-fit:cover; }
        .featured-body { padding: 12px 16px; }
        .featured-badge {
            display:inline-block; background:#ffe3ee; color:#c2185b; font-size:10px; font-weight:700;
            border-radius: 8px; padding: 2px 8px; margin-bottom:6px; text-transform:uppercase; letter-spacing:0.4px;
        }

        /* ============================================================
           STUDY — paleta "soft neutrals / beige aesthetic"
           ============================================================ */
        .study-beige { background:#FBF7F1; border-radius: 24px; padding: 18px 18px 4px 18px; }
        .study-beige .dash-card {
            background: #F4ECE0 !important; border: 1px solid #E7DBC7 !important;
        }
        .study-beige .dash-title {
            background:#6D5F5A; color:#ffffff !important; margin:-16px -18px 14px -18px;
            padding: 10px 18px; border-radius: 16px 16px 0 0; text-transform: uppercase;
            letter-spacing: 0.6px; font-size:13px !important;
        }
        .study-beige .badge-chip { background:#e7dbc7; color:#5b4c3a; }
        .flip-clock-wrap { display:flex; gap:12px; justify-content:center; margin-bottom:16px; }
        .flip-block {
            background:#3F3630; color:#fff; border-radius:16px; padding: 14px 22px;
            min-width: 90px; text-align:center; box-shadow: 0 8px 18px rgba(0,0,0,0.18);
        }
        .flip-number { font-size: 40px; font-weight: 800; line-height:1; }
        .flip-caption { font-size: 10px; letter-spacing: 1px; text-transform:uppercase; opacity:0.75; margin-top:4px;}
        .cal-wrap { background:#F4ECE0; border:1px solid #E7DBC7; border-radius:16px; padding:14px 16px; margin-bottom:16px; }
        .cal-head { font-weight:700; color:#5b4c3a; text-transform:uppercase; font-size:13px; margin-bottom:8px; text-align:center; }
        .cal-grid { display:grid; grid-template-columns: repeat(7, 1fr); gap:4px; text-align:center; font-size:12px; }
        .cal-dow { font-weight:700; color:#8a7a63; padding-bottom:4px; }
        .cal-day { padding:6px 0; border-radius:8px; color:#5b4c3a; }
        .cal-day.other { color:#c9bda6; }
        .cal-day.today { background:#6D5F5A; color:#fff; font-weight:700; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_live_clock():
    """Reloj/fecha en vivo (hora de Perú), pensado para ir justo debajo del hero-banner."""
    components.html(
        """
        <div class="hero-clock-wrap" style="
            font-family: 'Inter', sans-serif;
            text-align:center;
            background: linear-gradient(135deg, #ffe3ee 0%, #fff0f5 100%);
            border-left: 3px solid #f6c9dc;
            border-right: 3px solid #f6c9dc;
            border-bottom: 3px solid #f6c9dc;
            border-radius: 0 0 32px 32px;
            padding: 6px 20px 16px 20px;
            margin: 0;
        ">
            <div id="hero-clock-text" style="color:#9b4468; font-size:16px; font-weight:600; letter-spacing:0.3px;">
                cargando hora... (˶˃﹏˂˶)
            </div>
        </div>
        <style> html, body { margin:0; padding:0; background: transparent; } </style>
        <script>
        function updateHeroClock() {
            const now = new Date();
            const dOpts = { timeZone: 'America/Lima', weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
            const tOpts = { timeZone: 'America/Lima', hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: true };
            let dateStr = now.toLocaleDateString('es-PE', dOpts);
            dateStr = dateStr.charAt(0).toUpperCase() + dateStr.slice(1);
            const timeStr = now.toLocaleTimeString('es-PE', tOpts);
            const el = document.getElementById('hero-clock-text');
            if (el) { el.innerHTML = dateStr + '  ⋆  ' + timeStr + ' (Perú)'; }
        }
        updateHeroClock();
        setInterval(updateHeroClock, 1000);
        </script>
        """,
        height=66,
    )


def render_flip_clock():
    """Reloj tipo 'flip clock' (bloques oscuros, números grandes) — estética beige/planner."""
    components.html(
        """
        <div style="display:flex; gap:12px; justify-content:center;">
            <div style="background:#3F3630; color:#fff; border-radius:16px; padding:14px 22px; min-width:90px; text-align:center; box-shadow:0 8px 18px rgba(0,0,0,0.18); font-family:'Inter',sans-serif;">
                <div id="fc-hh" style="font-size:40px; font-weight:800; line-height:1;">--</div>
                <div style="font-size:10px; letter-spacing:1px; text-transform:uppercase; opacity:0.75; margin-top:4px;" id="fc-ampm">--</div>
            </div>
            <div style="background:#3F3630; color:#fff; border-radius:16px; padding:14px 22px; min-width:90px; text-align:center; box-shadow:0 8px 18px rgba(0,0,0,0.18); font-family:'Inter',sans-serif;">
                <div id="fc-mm" style="font-size:40px; font-weight:800; line-height:1;">--</div>
                <div style="font-size:10px; letter-spacing:1px; text-transform:uppercase; opacity:0.75; margin-top:4px;" id="fc-day">--</div>
            </div>
        </div>
        <style> html, body { margin:0; padding:0; background:transparent; } </style>
        <script>
        function updateFlip() {
            const now = new Date();
            const parts = new Intl.DateTimeFormat('es-PE', { timeZone:'America/Lima', hour:'2-digit', minute:'2-digit', hour12:true, weekday:'long' }).formatToParts(now);
            let hh='--', mm='--', ampm='--', wd='--';
            parts.forEach(p => {
                if (p.type==='hour') hh=p.value;
                if (p.type==='minute') mm=p.value;
                if (p.type==='dayPeriod') ampm=p.value.toUpperCase();
                if (p.type==='weekday') wd=p.value.toUpperCase();
            });
            document.getElementById('fc-hh').textContent = hh;
            document.getElementById('fc-mm').textContent = mm;
            document.getElementById('fc-ampm').textContent = ampm;
            document.getElementById('fc-day').textContent = wd;
        }
        updateFlip();
        setInterval(updateFlip, 5000);
        </script>
        """,
        height=100,
    )


def render_month_calendar():
    """Calendario mensual estático (mes actual, hora de Perú), día de hoy resaltado."""
    import calendar as _cal
    today = datetime.date.today()
    cal = _cal.Calendar(firstweekday=6)  # domingo primero, como en la referencia (S M T W T F S)
    weeks = cal.monthdayscalendar(today.year, today.month)
    month_name = today.strftime("%B %Y").capitalize()
    dows = ["S", "M", "T", "W", "T", "F", "S"]

    html = f'<div class="cal-wrap"><div class="cal-head">{month_name}</div><div class="cal-grid">'
    for d in dows:
        html += f'<div class="cal-dow">{d}</div>'
    for week in weeks:
        for day in week:
            if day == 0:
                html += '<div class="cal-day other">·</div>'
            elif day == today.day:
                html += f'<div class="cal-day today">{day}</div>'
            else:
                html += f'<div class="cal-day">{day}</div>'
    html += "</div></div>"
    st.markdown(html, unsafe_allow_html=True)


# ============================================================
# BASE DE DATOS
# ============================================================
@st.cache_resource
def get_conn():
    # Conexión única reutilizada durante toda la sesión del servidor:
    # abrir/cerrar el archivo en cada consulta era lo que hacía sentir la app lenta.
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def run(sql, params=(), fetch=False, one=False):
    conn = get_conn()
    c = conn.cursor()
    c.execute(sql, params)
    data = None
    if fetch:
        data = c.fetchone() if one else c.fetchall()
    conn.commit()
    return data


def migrate_db():
    """Agrega columnas nuevas a tablas viejas que ya existían en tu base de datos,
    sin borrar los datos que ya guardaste."""
    conn = get_conn()
    c = conn.cursor()

    def existing_columns(table):
        c.execute(f"PRAGMA table_info({table})")
        return {row["name"] for row in c.fetchall()}

    # Tablas y columnas que deben existir, con su definición para ALTER TABLE
    required = {
        "items": [
            ("trashed", "INTEGER DEFAULT 0"),
            ("favorite", "INTEGER DEFAULT 0"),
            ("link", "TEXT"),
            ("folder_id", "INTEGER"),
            ("created_at", "TEXT"),
            ("current_chapter", "TEXT"),
        ],
        "profile": [
            ("avatar_b64", "TEXT"),
        ],
    }

    for table, columns in required.items():
        c.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,))
        if not c.fetchone():
            continue  # la tabla se crea más abajo con CREATE TABLE IF NOT EXISTS
        existing = existing_columns(table)
        for col_name, col_def in columns:
            if col_name not in existing:
                c.execute(f"ALTER TABLE {table} ADD COLUMN {col_name} {col_def}")

    conn.commit()


def init_db():
    run("""CREATE TABLE IF NOT EXISTS profile (
            id INTEGER PRIMARY KEY, name TEXT, avatar_b64 TEXT)""")
    run("""CREATE TABLE IF NOT EXISTS folders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            section TEXT NOT NULL, name TEXT NOT NULL, color TEXT NOT NULL)""")
    run("""CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            section TEXT NOT NULL, title TEXT NOT NULL, link TEXT,
            folder_id INTEGER, favorite INTEGER DEFAULT 0,
            trashed INTEGER DEFAULT 0, created_at TEXT)""")
    run("""CREATE TABLE IF NOT EXISTS entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_id INTEGER NOT NULL, date TEXT, text TEXT,
            image_b64 TEXT, stars INTEGER)""")
    run("""CREATE TABLE IF NOT EXISTS schedule (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            kind TEXT NOT NULL, day TEXT, time TEXT, subject TEXT, color TEXT)""")
    run("""CREATE TABLE IF NOT EXISTS study_todos (
            id INTEGER PRIMARY KEY AUTOINCREMENT, text TEXT, done INTEGER DEFAULT 0)""")
    run("""CREATE TABLE IF NOT EXISTS study_notes (
            id INTEGER PRIMARY KEY, content TEXT)""")
    run("""CREATE TABLE IF NOT EXISTS section_images (
            section TEXT PRIMARY KEY, image_b64 TEXT)""")

    migrate_db()

    if not run("SELECT id FROM profile WHERE id=1", fetch=True, one=True):
        run("INSERT INTO profile (id, name, avatar_b64) VALUES (1, ?, NULL)", ("Katsearose",))
    if not run("SELECT id FROM study_notes WHERE id=1", fetch=True, one=True):
        run("INSERT INTO study_notes (id, content) VALUES (1, '')")

    for sec in SECTIONS:
        if not run("SELECT id FROM folders WHERE section=?", (sec,), fetch=True):
            run("INSERT INTO folders (section, name, color) VALUES (?,?,?)",
                (sec, "General", DEFAULT_COLORS[0]))


# ---------- Perfil ----------
def get_profile():
    return run("SELECT * FROM profile WHERE id=1", fetch=True, one=True)


def save_profile(name, avatar_file):
    if avatar_file is not None:
        b64 = base64.b64encode(avatar_file.read()).decode("utf-8")
        run("UPDATE profile SET name=?, avatar_b64=? WHERE id=1", (name, b64))
    else:
        run("UPDATE profile SET name=? WHERE id=1", (name,))


# ---------- Imágenes de portada del home (BL / BOOKS / STUDY) ----------
def get_section_image(section):
    r = run("SELECT image_b64 FROM section_images WHERE section=?", (section,), fetch=True, one=True)
    return r["image_b64"] if r else None


def save_section_image(section, image_file):
    b64 = base64.b64encode(image_file.read()).decode("utf-8")
    if run("SELECT section FROM section_images WHERE section=?", (section,), fetch=True, one=True):
        run("UPDATE section_images SET image_b64=? WHERE section=?", (b64, section))
    else:
        run("INSERT INTO section_images (section, image_b64) VALUES (?,?)", (section, b64))


# ---------- Folders (archivadores) ----------
def get_folders(section):
    return run("SELECT * FROM folders WHERE section=? ORDER BY name", (section,), fetch=True)


def add_folder(section, name, color):
    run("INSERT INTO folders (section, name, color) VALUES (?,?,?)", (section, name, color))


def folder_item_counts(section):
    """Cuenta títulos por carpeta en UNA sola consulta (antes se hacía una por carpeta)."""
    rows = run(
        "SELECT folder_id, COUNT(*) n FROM items WHERE section=? AND trashed=0 GROUP BY folder_id",
        (section,), fetch=True,
    )
    return {r["folder_id"]: r["n"] for r in rows} if rows else {}


def save_chapter(item_id, chapter_text):
    run("UPDATE items SET current_chapter=? WHERE id=?", (chapter_text, item_id))


def get_all_items_section(section):
    """Todos los títulos de una sección (todas las carpetas), en orden alfabético — para la hoja 'Lista completa'."""
    return run(
        "SELECT items.*, folders.name AS folder_name, folders.color AS folder_color "
        "FROM items LEFT JOIN folders ON items.folder_id = folders.id "
        "WHERE items.section=? AND items.trashed=0 ORDER BY items.title COLLATE NOCASE",
        (section,), fetch=True,
    )


# ---------- Items ----------
def add_item(section, title, link, folder_id, favorite):
    run("INSERT INTO items (section, title, link, folder_id, favorite, trashed, created_at) VALUES (?,?,?,?,?,0,?)",
        (section, title, link, folder_id, int(favorite), datetime.datetime.now().strftime("%Y-%m-%d %H:%M")))


def get_items(section, folder_id):
    return run("SELECT * FROM items WHERE section=? AND folder_id=? AND trashed=0 ORDER BY title COLLATE NOCASE",
               (section, folder_id), fetch=True)


def get_favorites_all():
    return run("SELECT * FROM items WHERE favorite=1 AND trashed=0 ORDER BY title COLLATE NOCASE", fetch=True)


def get_recent_items_all(limit=4):
    """Últimos títulos agregados en cualquier sección — para el módulo 'Nuevo' del home."""
    return run(
        "SELECT * FROM items WHERE trashed=0 ORDER BY created_at DESC, id DESC LIMIT ?",
        (limit,), fetch=True,
    )


def search_items_all(query):
    like = f"%{query}%"
    return run(
        "SELECT * FROM items WHERE trashed=0 AND title LIKE ? ORDER BY title COLLATE NOCASE LIMIT 12",
        (like,), fetch=True,
    )


def get_recent_activity(limit=5):
    """Últimas entradas del hilo (de cualquier libro/sección) — para el panel de notificaciones."""
    return run(
        "SELECT entries.*, items.title AS item_title, items.section AS section "
        "FROM entries JOIN items ON entries.item_id = items.id "
        "WHERE items.trashed=0 ORDER BY entries.id DESC LIMIT ?",
        (limit,), fetch=True,
    )


def get_streak_days():
    """Cuenta cuántos días distintos (consecutivos hacia atrás desde hoy) tienen al menos una entrada."""
    rows = run("SELECT DISTINCT date FROM entries", fetch=True)
    if not rows:
        return 0
    days = set()
    for r in rows:
        try:
            days.add(datetime.datetime.strptime(r["date"][:10], "%Y-%m-%d").date())
        except Exception:
            continue
    streak = 0
    cursor = datetime.date.today()
    while cursor in days:
        streak += 1
        cursor -= datetime.timedelta(days=1)
    return streak


def toggle_favorite(item_id, current):
    run("UPDATE items SET favorite=? WHERE id=?", (0 if current else 1, item_id))


def get_item(item_id):
    return run("SELECT * FROM items WHERE id=?", (item_id,), fetch=True, one=True)


def soft_delete_item(item_id):
    run("UPDATE items SET trashed=1 WHERE id=?", (item_id,))


def restore_item(item_id):
    run("UPDATE items SET trashed=0 WHERE id=?", (item_id,))


def hard_delete_item(item_id):
    run("DELETE FROM entries WHERE item_id=?", (item_id,))
    run("DELETE FROM items WHERE id=?", (item_id,))


def get_trashed_items():
    return run("SELECT * FROM items WHERE trashed=1 ORDER BY created_at DESC", fetch=True)


# ---------- Entries (hilo) ----------
def add_entry(item_id, text, image_file, stars):
    img_b64 = base64.b64encode(image_file.read()).decode("utf-8") if image_file is not None else None
    run("INSERT INTO entries (item_id, date, text, image_b64, stars) VALUES (?,?,?,?,?)",
        (item_id, datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), text, img_b64, stars))


def get_entries(item_id):
    return run("SELECT * FROM entries WHERE item_id=? ORDER BY id DESC", (item_id,), fetch=True)


def delete_entry(entry_id):
    run("DELETE FROM entries WHERE id=?", (entry_id,))


def average_score(item_id):
    rows = run("SELECT stars FROM entries WHERE item_id=?", (item_id,), fetch=True)
    vals = [r["stars"] for r in rows if r["stars"] is not None] if rows else []
    return round(sum(vals) / len(vals), 1) if vals else 0.0


def stars_html(score):
    full = max(0, min(5, int(round(score))))
    return "⭐" * full + "☆" * (5 - full)


# ---------- Study: horarios / to-dos / notas ----------
def get_schedule(kind):
    return run("SELECT * FROM schedule WHERE kind=? ORDER BY day, time", (kind,), fetch=True)


def add_schedule_row(kind, day, time, subject, color):
    run("INSERT INTO schedule (kind, day, time, subject, color) VALUES (?,?,?,?,?)",
        (kind, day, time, subject, color))


def delete_schedule_row(row_id):
    run("DELETE FROM schedule WHERE id=?", (row_id,))


def get_todos():
    return run("SELECT * FROM study_todos ORDER BY id", fetch=True)


def add_todo(text):
    run("INSERT INTO study_todos (text, done) VALUES (?, 0)", (text,))


def toggle_todo(todo_id, current):
    run("UPDATE study_todos SET done=? WHERE id=?", (0 if current else 1, todo_id))


def delete_todo(todo_id):
    run("DELETE FROM study_todos WHERE id=?", (todo_id,))


def get_notes():
    r = run("SELECT content FROM study_notes WHERE id=1", fetch=True, one=True)
    return r["content"] if r else ""


def save_notes(content):
    run("UPDATE study_notes SET content=? WHERE id=1", (content,))


# ============================================================
# GITHUB SYNC (opcional, vía st.secrets)
# ============================================================
def github_configured():
    return hasattr(st, "secrets") and all(k in st.secrets for k in ("GITHUB_TOKEN", "GITHUB_REPO", "GITHUB_DB_PATH"))


def github_headers():
    return {"Authorization": f"token {st.secrets['GITHUB_TOKEN']}", "Accept": "application/vnd.github+json"}


def github_api_url():
    return f"https://api.github.com/repos/{st.secrets['GITHUB_REPO']}/contents/{st.secrets['GITHUB_DB_PATH']}"


def load_db_from_github():
    if not github_configured():
        return
    try:
        r = requests.get(github_api_url(), headers=github_headers(), timeout=15)
        if r.status_code == 200:
            Path(DB_PATH).write_bytes(base64.b64decode(r.json()["content"]))
    except Exception as e:
        st.sidebar.warning(f"No se pudo cargar desde GitHub: {e}")


def save_db_to_github():
    if not github_configured():
        st.sidebar.error("Faltan GITHUB_TOKEN / GITHUB_REPO / GITHUB_DB_PATH en secrets.")
        return
    try:
        content_b64 = base64.b64encode(Path(DB_PATH).read_bytes()).decode("utf-8")
        sha = None
        r = requests.get(github_api_url(), headers=github_headers(), timeout=15)
        if r.status_code == 200:
            sha = r.json().get("sha")
        payload = {"message": f"🌸 update {datetime.datetime.now().isoformat()}", "content": content_b64}
        if sha:
            payload["sha"] = sha
        r2 = requests.put(github_api_url(), headers=github_headers(), data=json.dumps(payload), timeout=15)
        if r2.status_code in (200, 201):
            st.sidebar.success("✅ Guardado en GitHub")
        else:
            st.sidebar.error(f"Error GitHub: {r2.status_code}")
    except Exception as e:
        st.sidebar.error(f"Error al guardar en GitHub: {e}")


# ============================================================
# NAVEGACIÓN
# ============================================================
def goto(page, **kwargs):
    st.session_state["page"] = page
    for k, v in kwargs.items():
        st.session_state[k] = v


if "page" not in st.session_state:
    st.session_state["page"] = "home"

inject_css()

if "db_loaded" not in st.session_state:
    load_db_from_github()
    st.session_state["db_loaded"] = True

init_db()

# ============================================================
# SIDEBAR: perfil + navegación
# ============================================================
with st.sidebar:
    prof = get_profile()
    st.markdown('<div class="profile-card">', unsafe_allow_html=True)
    if prof["avatar_b64"]:
        st.image(base64.b64decode(prof["avatar_b64"]), width=140)
    else:
        st.markdown('<div style="font-size:80px;">🐰</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="profile-name">{prof["name"]}</div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    with st.expander("✏️ Editar perfil"):
        new_name = st.text_input("Nombre", value=prof["name"])
        new_avatar = st.file_uploader("Foto de perfil (admite GIF animado)", type=["png", "jpg", "jpeg", "webp", "gif"], key="avatar_up")
        if st.button("💾 Guardar perfil", use_container_width=True):
            save_profile(new_name, new_avatar)
            st.success("¡Perfil actualizado! (♡ˊ͈ ꒳ ˋ͈)")
            st.rerun()

    st.markdown("---")
    current_page = st.session_state.get("page")
    current_sec = st.session_state.get("current_section")

    # NOTA: usamos type="primary"/"secondary" (soporte nativo de Streamlit) en vez
    # de trucos con CSS por key — así el resaltado del ítem activo es confiable.
    if st.button("🏠 Inicio", use_container_width=True, key="nav_home",
                 type="primary" if current_page == "home" else "secondary"):
        goto("home")
    for sec in SECTIONS:
        is_active = current_page in ("section", "folder", "detail") and current_sec == sec
        if st.button(SECTIONS[sec]["label"], use_container_width=True, key=f"nav_{sec}",
                     type="primary" if is_active else "secondary"):
            goto("section", current_section=sec)
    if st.button("͙֒ FAVORITES ⋆.˚", use_container_width=True, key="nav_fav",
                 type="primary" if current_page == "favorites" else "secondary"):
        goto("favorites")
    if st.button("🗑️ Papelera", use_container_width=True, key="nav_trash",
                 type="primary" if current_page == "trash" else "secondary"):
        goto("trash")

    st.markdown("---")
    if github_configured():
        if st.button("☁️ Guardar en GitHub", use_container_width=True):
            save_db_to_github()
        st.caption("Sincronización con GitHub activa ✅")
    else:
        st.caption(
            "💡 Para persistencia en GitHub agrega en `.streamlit/secrets.toml`:\n\n"
            "```\nGITHUB_TOKEN = \"...\"\nGITHUB_REPO = \"usuario/repo\"\nGITHUB_DB_PATH = \"data/otaku_bitacora.db\"\n```"
        )


# ============================================================
# PÁGINA: HOME
# ============================================================
def page_home():
    # Zona asimétrica de 3 columnas (2fr / 1fr / 1.2fr) — orden discontinuo tipo bento grid
    left, middle, right = st.columns([2, 1, 1.2])

    # ------------------------------------------------------------------
    # ZONA IZQUIERDA — buscador, banner de bienvenida, "nuevo", progreso
    # ------------------------------------------------------------------
    with left:
        query = st.text_input("Search...", key="home_search", placeholder="🔍 Search...", label_visibility="collapsed")
        if query.strip():
            st.markdown('<div class="bento-card"><div class="bento-card-title">Resultados</div>', unsafe_allow_html=True)
            results = search_items_all(query.strip())
            if not results:
                st.caption("Nada por aquí todavía (˶˃˂˶)")
            for r in results:
                cc1, cc2 = st.columns([5, 1])
                with cc1:
                    st.markdown(f"**{r['title']}** &nbsp; <span class='mini-course-meta'>{r['section']}</span>", unsafe_allow_html=True)
                with cc2:
                    if st.button("Abrir", key=f"search_open_{r['id']}", use_container_width=True):
                        goto("detail", current_item=r["id"], current_section=r["section"])
            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown(
            """
            <div class="hero-banner">
                <p class="hero-title">Katsearose's Dreamscape ⋆ ̊꩜。</p>
                <p class="hero-sep">────୨ৎ────</p>
                <p class="hero-kaomoji">⋆ ̊꩜。՞ ܸ.ˬ.ܸ՞</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        render_live_clock()

        with st.expander("🖼️ Cambiar las imágenes de portada"):
            for sec in SECTIONS:
                up = st.file_uploader(f"Portada para {sec} (admite GIF animado)", type=["png", "jpg", "jpeg", "webp", "gif"], key=f"cover_up_{sec}")
                if up is not None and st.button(f"Guardar portada de {sec}", key=f"cover_save_{sec}"):
                    save_section_image(sec, up)
                    st.success(f"¡Portada de {sec} actualizada! ✨")
                    st.rerun()

        # Accesos directos a cada sección — la ilustración "sale" ligeramente del marco
        hcols = st.columns(3)
        for col, sec in zip(hcols, SECTIONS):
            with col:
                st.markdown('<div class="heart-wrap">', unsafe_allow_html=True)
                cover = get_section_image(sec)
                if cover:
                    st.markdown(f'<img class="section-cover" src="data:image/png;base64,{cover}">', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="section-cover-placeholder">{SECTIONS[sec]["emoji"]}</div>', unsafe_allow_html=True)
                with st.container(key=f"home_heart_{sec}"):
                    if st.button("💗", key=f"enter_{sec}"):
                        goto("section", current_section=sec)
                st.markdown(f'<p class="heart-label">{SECTIONS[sec]["label"]}</p>', unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)

        st.markdown(
            """
            <style>
            .st-key-home_heart_BL button, .st-key-home_heart_BOOKS button, .st-key-home_heart_STUDY button {
                font-size: 46px !important; padding: 20px 0 !important; width: 100%; min-height: 96px; margin-top: 10px;
                background: white !important; border-radius: 50% !important;
                border: 4px solid #f6c9dc !important;
                box-shadow: 0 8px 0 rgba(246,201,220,0.55), 0 12px 20px rgba(0,0,0,0.08) !important;
            }
            </style>
            """,
            unsafe_allow_html=True,
        )

        # Módulo "Nuevo" (tipo New Courses) — últimos títulos agregados en cualquier sección
        st.markdown('<div class="bento-card"><div class="bento-card-title">✨ Recién agregado</div>', unsafe_allow_html=True)
        recent = get_recent_items_all(4)
        if not recent:
            st.caption("Todavía no agregaste ningún título (˶˃˂˶)")
        else:
            rcols = st.columns(len(recent))
            for rc, it in zip(rcols, recent):
                with rc:
                    st.markdown(
                        f"""<div class="mini-course-card">
                                <div class="mini-course-title">{SECTIONS[it['section']]['emoji']} {it['title'][:22]}</div>
                                <div class="mini-course-meta">{it['section']} · {it['created_at'] or ''}</div>
                            </div>""",
                        unsafe_allow_html=True,
                    )
                    if st.button("Abrir", key=f"recent_open_{it['id']}", use_container_width=True):
                        goto("detail", current_item=it["id"], current_section=it["section"])
        st.markdown("</div>", unsafe_allow_html=True)

        # Módulo de progreso — total de entradas escritas (analogía a "Total hours watched")
        total_entries = sum(len(get_entries(i["id"])) for sec in SECTIONS for i in get_all_items_section(sec))
        goal = max(50, total_entries + 10)
        pct = int(min(100, round((total_entries / goal) * 100))) if goal else 0
        st.markdown(
            f"""
            <div class="bento-card">
                <div class="bento-card-title">📈 Total de entradas escritas</div>
                <div class="progress-track"><div class="progress-fill" style="width:{pct}%;"></div></div>
                <div style="text-align:right; font-size:12px; color:#a9647f; margin-top:6px;">{total_entries} entradas</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # ------------------------------------------------------------------
    # ZONA CENTRAL — colección de favoritos + racha (analogía a suscripción)
    # ------------------------------------------------------------------
    with middle:
        st.markdown('<div class="bento-card"><div class="bento-card-title">💗 Colección</div>', unsafe_allow_html=True)
        favs = get_favorites_all()
        if not favs:
            st.caption("Sin favoritos aún")
        for f in favs[:4]:
            st.markdown(
                f"""<div class="collection-mini">
                        <div class="collection-thumb"></div>
                        <div>
                            <div class="mini-course-title" style="font-size:13px;">{f['title'][:20]}</div>
                            <div class="mini-course-meta">{f['section']}</div>
                        </div>
                    </div>""",
                unsafe_allow_html=True,
            )
        st.markdown("</div>", unsafe_allow_html=True)

        streak = get_streak_days()
        st.markdown(
            f"""
            <div class="streak-card">
                <div class="streak-number">{streak}</div>
                <div class="streak-label">🔥 días seguidos escribiendo</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        for scol_sec in SECTIONS:
            total = len(get_all_items_section(scol_sec))
            st.markdown(
                f"""<div class="stat-widget" style="margin-bottom:10px;">
                        <div class="stat-number">{total}</div>
                        <div class="stat-label">{SECTIONS[scol_sec]['emoji']} títulos en {scol_sec}</div>
                    </div>""",
                unsafe_allow_html=True,
            )

    # ------------------------------------------------------------------
    # ZONA DERECHA — notificaciones/actividad + tarjeta destacada
    # ------------------------------------------------------------------
    with right:
        st.markdown('<div class="bento-card"><div class="bento-card-title">🔔 Actividad reciente</div>', unsafe_allow_html=True)
        activity = get_recent_activity(5)
        if not activity:
            st.caption("Sin actividad todavía")
        for a in activity:
            st.markdown(
                f"""<div class="notif-item">
                        <div class="notif-icon">{SECTIONS[a['section']]['emoji']}</div>
                        <div>
                            <div class="notif-title">{a['item_title'][:26]}</div>
                            <div class="notif-meta">{a['date']} · {"⭐"*a['stars'] if a['stars'] else ''}</div>
                        </div>
                    </div>""",
                unsafe_allow_html=True,
            )
        st.markdown("</div>", unsafe_allow_html=True)

        # Tarjeta destacada (última entrada con imagen) — analogía al "Video Destacado"
        featured = next((a for a in get_recent_activity(15) if a["image_b64"]), None)
        st.markdown('<div class="featured-card">', unsafe_allow_html=True)
        if featured:
            st.image(base64.b64decode(featured["image_b64"]))
            st.markdown(
                f"""<div class="featured-body">
                        <span class="featured-badge">Más reciente</span><br>
                        <b>{featured['item_title']}</b><br>
                        <span class="mini-course-meta">{featured['date']}</span>
                    </div>""",
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                '<div class="featured-body"><span class="featured-badge">Destacado</span><br>'
                'Aún no hay entradas con imagen — ¡sube una en el hilo de algún título! (˶˃˂˶)</div>',
                unsafe_allow_html=True,
            )
        st.markdown("</div>", unsafe_allow_html=True)


# ============================================================
# PÁGINA: SECCIÓN → grid de archivadores (carpetas)
# ============================================================
def page_section():
    sec = st.session_state.get("current_section", "BL")
    info = SECTIONS[sec]

    st.markdown(
        f"""
        <div class="plaid-banner">
            <p class="plaid-title">{info['label']}</p>
            <p class="plaid-sep">────୨ৎ────</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    tab_labels = ["📂 Archivadores", "📋 Lista completa", "💗 Favoritos"]
    if sec == "STUDY":
        tab_labels.append("🗓️ Dashboard / Planner")

    tabs = st.tabs(tab_labels)
    with tabs[0]:
        render_archivadores(sec, info)
    with tabs[1]:
        render_full_list(sec)
    with tabs[2]:
        render_section_favorites(sec)
    if sec == "STUDY":
        with tabs[3]:
            page_study_dashboard()


def render_full_list(sec):
    """Hoja 2: TODOS los títulos de la sección en una sola lista alfabética,
    con un punto de color mostrando a qué archivador/etiqueta pertenece."""
    items = get_all_items_section(sec)
    if not items:
        st.info("Todavía no hay títulos en esta sección (˶˃˂˶)")
        return
    for it in items:
        score = average_score(it["id"])
        heart = '<span class="fav-heart">💗</span>' if it["favorite"] else ""
        color = it["folder_color"] or "#f3b8d2"
        c1, c2 = st.columns([6, 1])
        with c1:
            st.markdown(
                f"""<div class="book-card" style="border-left-color:{color};">
                        <span class="book-title">{it['title']}</span> {heart}
                        <span class="tag-chip" style="background:{color};">● {it['folder_name'] or 'Sin carpeta'}</span><br>
                        <span class="stars">{stars_html(score)}</span> ({score}/5)
                        {f'&nbsp;&nbsp;🔖 {it["current_chapter"]}' if it["current_chapter"] else ''}
                    </div>""",
                unsafe_allow_html=True,
            )
        with c2:
            if st.button("Abrir", key=f"fulllist_open_{it['id']}", use_container_width=True):
                goto("detail", current_item=it["id"], current_section=sec)


def render_section_favorites(sec):
    """Hoja 3: solo los favoritos de ESTA sección."""
    items = [i for i in get_all_items_section(sec) if i["favorite"]]
    if not items:
        st.info("Aún no marcaste favoritos en esta sección (˶˃˂˶)")
        return
    for it in items:
        score = average_score(it["id"])
        color = it["folder_color"] or "#f3b8d2"
        c1, c2 = st.columns([6, 1])
        with c1:
            st.markdown(
                f"""<div class="book-card" style="border-left-color:{color};">
                        <span class="book-title">{it['title']}</span> <span class="fav-heart">💗</span>
                        <span class="tag-chip" style="background:{color};">● {it['folder_name'] or 'Sin carpeta'}</span><br>
                        <span class="stars">{stars_html(score)}</span> ({score}/5)
                    </div>""",
                unsafe_allow_html=True,
            )
        with c2:
            if st.button("Abrir", key=f"favsec_open_{it['id']}", use_container_width=True):
                goto("detail", current_item=it["id"], current_section=sec)


def render_archivadores(sec, info):
    folders = get_folders(sec)

    with st.expander("🎀 Crear nuevo archivador"):
        with st.form(f"add_folder_{sec}", clear_on_submit=True):
            fname = st.text_input("Nombre del archivador (ej: Yaoi, Manhwa, Física...)")
            fcolor = st.color_picker("Color de tapa", DEFAULT_COLORS[len(folders) % len(DEFAULT_COLORS)])
            if st.form_submit_button("Crear 🎀") and fname.strip():
                add_folder(sec, fname.strip(), fcolor)
                st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    counts = folder_item_counts(sec)
    cols = st.columns(3)
    for i, f in enumerate(folders):
        n = counts.get(f["id"], 0)
        with cols[i % 3]:
            st.markdown(
                f"""
                <div class="archivador" style="background:{f['color']};">
                    <div class="archivador-tab">{f['name']}</div>
                    <div style="height:60px;"></div>
                    <div class="archivador-count">{n} títulos</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if st.button("Abrir 📖", key=f"open_folder_{f['id']}", use_container_width=True):
                goto("folder", current_section=sec, current_folder=f["id"], current_folder_name=f["name"])


# ============================================================
# PÁGINA: dentro de un archivador → lista alfabética de libros
# ============================================================
def page_folder():
    sec = st.session_state.get("current_section", "BL")
    folder_id = st.session_state.get("current_folder")
    folder_name = st.session_state.get("current_folder_name", "")
    info = SECTIONS[sec]

    if st.button("⬅️ Volver a archivadores"):
        goto("section", current_section=sec)
        st.rerun()

    st.markdown(f"## 🎀 {folder_name}")

    with st.expander("➕ Agregar nuevo título aquí"):
        with st.form(f"add_item_{folder_id}", clear_on_submit=True):
            title = st.text_input("Título")
            link = st.text_input(info["link_label"])
            favorite = st.checkbox("💗 Marcar como favorito")
            if st.form_submit_button("Guardar 💾") and title.strip():
                add_item(sec, title.strip(), link.strip(), folder_id, favorite)
                st.success("¡Guardado! (♡ˊ͈ ꒳ ˋ͈)")
                st.rerun()

    st.markdown("---")
    items = get_items(sec, folder_id)
    if not items:
        st.info("Todavía no hay nada aquí (˶˃˂˶) ¡agrega tu primer título arriba!")
        return

    for it in items:
        score = average_score(it["id"])
        heart = '<span class="fav-heart">💗</span>' if it["favorite"] else ""
        c1, c2, c3 = st.columns([5, 1, 1])
        with c1:
            st.markdown(
                f"""<div class="book-card">
                        <span class="book-title">{it['title']}</span> {heart}<br>
                        <span class="stars">{stars_html(score)}</span> ({score}/5)
                    </div>""",
                unsafe_allow_html=True,
            )
        with c2:
            if st.button("Abrir", key=f"openitem_{it['id']}", use_container_width=True):
                goto("detail", current_item=it["id"], current_section=sec)
            if st.button("💗", key=f"favitem_{it['id']}", use_container_width=True):
                toggle_favorite(it["id"], it["favorite"])
                st.rerun()
        with c3:
            if st.button("🗑️", key=f"delitem_{it['id']}", use_container_width=True):
                soft_delete_item(it["id"])
                st.success("Movido a la papelera 🗑️")
                st.rerun()


# ============================================================
# PÁGINA: DETALLE (hilo tipo tweets)
# ============================================================
def page_detail():
    item_id = st.session_state.get("current_item")
    sec = st.session_state.get("current_section", "BL")
    item = get_item(item_id)
    if not item:
        st.error("No se encontró este título.")
        return
    info = SECTIONS[sec]
    score = average_score(item_id)

    col1, col2 = st.columns([5, 1])
    with col1:
        st.markdown(f"## {item['title']} {'💗' if item['favorite'] else ''}")
    with col2:
        if st.button("🗑️ Eliminar libro", use_container_width=True):
            soft_delete_item(item_id)
            st.success("Movido a la papelera 🗑️")
            goto("section", current_section=sec)
            st.rerun()

    if item["link"]:
        st.markdown(f"[{info['link_label']}]({item['link']})")
    st.markdown(f"### {stars_html(score)}  —  {score}/5 · {len(get_entries(item_id))} entradas")

    st.markdown("---")
    st.markdown("### 🔖 ¿Hasta dónde te quedaste?")
    cc1, cc2 = st.columns([4, 1])
    with cc1:
        chapter_val = st.text_input(
            "Capítulo / página / episodio actual",
            value=item["current_chapter"] or "",
            key=f"chapter_{item_id}",
            placeholder="ej: Capítulo 34, o Tomo 2 - pág. 120",
            label_visibility="collapsed",
        )
    with cc2:
        if st.button("💾 Guardar", key=f"savechap_{item_id}", use_container_width=True):
            save_chapter(item_id, chapter_val.strip())
            st.toast("¡Guardado! 🔖")
            st.rerun()
    if item["current_chapter"]:
        st.caption(f"📍 Vas por: **{item['current_chapter']}**")

    st.markdown("---")
    st.markdown("### ✏️ Nueva entrada")
    with st.form("new_entry_form", clear_on_submit=True):
        text = st.text_area("¿Qué quieres anotar hoy?")
        stars = st.slider("Puntuación de esta entrada", 1, 5, 5)
        image = st.file_uploader("Imagen o GIF (opcional)", type=["png", "jpg", "jpeg", "gif", "webp"])
        if st.form_submit_button("Publicar 🌸") and text.strip():
            add_entry(item_id, text.strip(), image, stars)
            st.success("¡Entrada guardada!")
            st.rerun()

    st.markdown("---")
    st.markdown("### 🧵 Hilo")
    entries = get_entries(item_id)
    if not entries:
        st.info("Aún no hay entradas ( ˶°ᄆ°) !! ¡escribe la primera arriba!")
    for e in entries:
        c1, c2 = st.columns([6, 1])
        with c1:
            st.markdown(
                f"""<div class="tweet-card">
                        <span class="tweet-date">{e['date']}</span><br>
                        <span class="stars">{"⭐"*e['stars']}{"☆"*(5-e['stars'])}</span><br>
                        <p>{e['text']}</p>
                    </div>""",
                unsafe_allow_html=True,
            )
            if e["image_b64"]:
                st.image(base64.b64decode(e["image_b64"]), width=280)
        with c2:
            if st.button("🗑️", key=f"delentry_{e['id']}"):
                delete_entry(e["id"])
                st.rerun()

    st.markdown("---")
    if st.button("⬅️ Volver"):
        goto("folder", current_section=sec, current_folder=item["folder_id"],
             current_folder_name=next((f["name"] for f in get_folders(sec) if f["id"] == item["folder_id"]), ""))


# ============================================================
# PÁGINA: FAVORITOS
# ============================================================
def page_favorites():
    st.markdown("## ͙֒ FAVORITES ⋆.˚")
    favs = get_favorites_all()
    if not favs:
        st.info("Todavía no marcaste favoritos (˶˃˂˶)")
        return
    for it in favs:
        score = average_score(it["id"])
        st.markdown(
            f"""<div class="book-card">
                    <span class="book-title">{it['title']}</span> <span class="fav-heart">💗</span>
                    <span class="tag-chip" style="background:#d98bad;">{it['section']}</span><br>
                    <span class="stars">{stars_html(score)}</span> ({score}/5)
                </div>""",
            unsafe_allow_html=True,
        )
        if st.button("Abrir 📖", key=f"favopen_{it['id']}"):
            goto("detail", current_item=it["id"], current_section=it["section"])


# ============================================================
# PÁGINA: PAPELERA
# ============================================================
def page_trash():
    st.markdown("## 🗑️ Papelera")
    st.caption("Aquí puedes restaurar un título o eliminarlo DEFINITIVAMENTE (no se puede deshacer).")
    trashed = get_trashed_items()
    if not trashed:
        st.info("La papelera está vacía ✨")
        return
    for it in trashed:
        st.markdown(
            f"""<div class="trash-card">
                    <b>{it['title']}</b> — {it['section']}
                </div>""",
            unsafe_allow_html=True,
        )
        c1, c2 = st.columns(2)
        with c1:
            if st.button("♻️ Restaurar", key=f"restore_{it['id']}", use_container_width=True):
                restore_item(it["id"])
                st.rerun()
        with c2:
            if st.button("❌ Eliminar para siempre", key=f"harddel_{it['id']}", use_container_width=True):
                hard_delete_item(it["id"])
                st.warning("Eliminado definitivamente.")
                st.rerun()


# ============================================================
# PÁGINA: STUDY DASHBOARD (horarios + to-do + notas)
# ============================================================
def render_schedule_block(kind, title):
    st.markdown(f'<div class="dash-card"><div class="dash-title">{title}</div>', unsafe_allow_html=True)
    rows = get_schedule(kind)
    days = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]

    if rows:
        for r in rows:
            c1, c2 = st.columns([6, 1])
            with c1:
                st.markdown(
                    f'<span class="badge-chip">{r["day"]}</span> &nbsp; 🕐 {r["time"]} &nbsp; — &nbsp; <b>{r["subject"]}</b>',
                    unsafe_allow_html=True,
                )
            with c2:
                if st.button("🗑️", key=f"delsched_{kind}_{r['id']}"):
                    delete_schedule_row(r["id"])
                    st.rerun()
    else:
        st.caption("Sin horas agregadas todavía.")

    with st.form(f"add_sched_{kind}", clear_on_submit=True):
        cc1, cc2, cc3 = st.columns(3)
        with cc1:
            day = st.selectbox("Día", days, key=f"day_{kind}")
        with cc2:
            time = st.text_input("Hora (ej: 8:00 - 9:00)", key=f"time_{kind}")
        with cc3:
            subject = st.text_input("Materia / actividad", key=f"subj_{kind}")
        if st.form_submit_button("➕ Agregar") and subject.strip():
            add_schedule_row(kind, day, time, subject.strip(), "#F7B8D2")
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)


def page_study_dashboard():
    st.markdown('<div class="study-beige">', unsafe_allow_html=True)

    ccol1, ccol2 = st.columns([1, 1.3])
    with ccol1:
        render_flip_clock()
    with ccol2:
        render_month_calendar()

    col1, col2 = st.columns(2)
    with col1:
        render_schedule_block("colegio", "🏫 Horario del colegio")
    with col2:
        render_schedule_block("personal", "🌙 Horario después del colegio")

    col3, col4 = st.columns(2)
    with col3:
        st.markdown('<div class="dash-card"><div class="dash-title">✅ To-Do</div>', unsafe_allow_html=True)
        for t in get_todos():
            cc1, cc2 = st.columns([5, 1])
            with cc1:
                checked = st.checkbox(t["text"], value=bool(t["done"]), key=f"todo_{t['id']}")
                if checked != bool(t["done"]):
                    toggle_todo(t["id"], t["done"])
                    st.rerun()
            with cc2:
                if st.button("🗑️", key=f"deltodo_{t['id']}"):
                    delete_todo(t["id"])
                    st.rerun()
        new_todo = st.text_input("Nueva tarea", key="new_todo_input")
        if st.button("➕ Agregar tarea") and new_todo.strip():
            add_todo(new_todo.strip())
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    with col4:
        st.markdown('<div class="dash-card"><div class="dash-title">📝 Notas rápidas</div>', unsafe_allow_html=True)
        content = st.text_area("", value=get_notes(), height=160, key="notes_area", label_visibility="collapsed")
        if st.button("💾 Guardar notas"):
            save_notes(content)
            st.success("Notas guardadas ✨")
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)  # cierre .study-beige


# ============================================================
# ROUTER
# ============================================================
page = st.session_state["page"]
if page == "home":
    page_home()
elif page == "section":
    page_section()
elif page == "folder":
    page_folder()
elif page == "detail":
    page_detail()
elif page == "favorites":
    page_favorites()
elif page == "trash":
    page_trash()
