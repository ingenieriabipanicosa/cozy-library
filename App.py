"""
🌸 Katsearose's Dreamscape 🌸
Bitácora otaku en Streamlit: BL, Books y Study con archivadores,
hilos tipo tweet, papelera, perfil y dashboard de horarios.
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

# Tipos de contenido que se pueden archivar dentro de STUDY (ya no es "libros")
STUDY_CONTENT_TYPES = {
    "video": {"emoji": "📺", "label": "Video de YouTube"},
    "playlist": {"emoji": "🎵", "label": "Lista de reproducción"},
    "link": {"emoji": "🔗", "label": "Link / Página"},
    "doc": {"emoji": "📄", "label": "Documento"},
    "image": {"emoji": "🖼️", "label": "Imagen"},
}

# Tipos de contenido para las tarjetas de Lenguajes
LANG_CONTENT_TYPES = {
    "image": {"emoji": "🖼️", "label": "Imagen"},
    "video": {"emoji": "📺", "label": "Video"},
    "playlist": {"emoji": "🎵", "label": "Lista de reproducción"},
    "link": {"emoji": "🔗", "label": "Link / Página"},
    "file": {"emoji": "📄", "label": "Archivo"},
}

SOCIAL_PLATFORMS = {
    "twitter": {"emoji": "🐦", "label": "Twitter / X"},
    "pinterest": {"emoji": "📌", "label": "Pinterest"},
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
        h2 { font-size: 2.2em !important; }
        h3 { font-size: 1.5em !important; }
        .stTabs [data-baseweb="tab-list"] button p {
            font-family: 'Inter', sans-serif !important;
            font-size: 1.15em !important;
            font-weight: 700 !important;
        }

        .stApp {
            background:
                radial-gradient(circle, #ffe9f2 1px, transparent 1px) 10px 24px/48px 48px,
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

        /* ---- Decoración: divisores tipo lazo ---- */
        .bow-divider {
            display: flex; align-items: center; justify-content: center; gap: 10px;
            margin: 10px 0 14px 0; color: #e6a9c4;
        }
        .bow-divider::before, .bow-divider::after {
            content: ""; flex: 1; height: 1px; max-width: 120px;
            background: repeating-linear-gradient(90deg, #f3b8d2 0 4px, transparent 4px 8px);
        }
        .bow-divider span { font-size: 17px; }

        /* ---- Nubes/estrellitas decorativas dentro del hero-banner ---- */
        .deco-cloud, .deco-star, .deco-heart {
            position: absolute; pointer-events: none; z-index: 0;
        }
        .deco-cloud { color: rgba(255,255,255,0.9); }
        .deco-star { color: #ffe3ee; }
        .deco-heart { color: rgba(255,255,255,0.75); }

        /* ---- Perfil (sidebar) ---- */
        .profile-card {
            position: relative;
            text-align: center;
            background: #ffffff;
            border: 2px dashed #f3b8d2;
            border-radius: 26px;
            padding: 28px 10px 14px 10px;
            margin-bottom: 10px;
        }
        .profile-card::before {
            content: "🎀";
            position: absolute;
            top: -17px; left: 50%; transform: translateX(-50%);
            font-size: 26px;
            background: #fff6fa;
            padding: 0 6px;
        }
        .profile-card img {
            border: 3px solid white !important;
            outline: 2px solid #f6c9dc;
        }
        .profile-name {
            font-family: 'Pinyon Script', cursive;
            font-size: 30px;
            color: #C2185B;
            font-weight: 400;
            margin-top: 6px;
        }
        .profile-name::before { content: "✧˖° "; font-size: 14px; }
        .profile-name::after { content: " °˖✧"; font-size: 14px; }

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

        /* ---- Botones corazón del home (ahora pastillas ovaladas) ---- */
        .heart-wrap { text-align: center; }
        div[class*="st-key-enter_"] button {
            border-radius: 50px !important;
            background: white !important;
            border: 2px solid #f6c9dc !important;
            font-family: 'Pinyon Script', cursive !important;
            font-size: 20px !important;
            color: #9b4468 !important;
            padding: 9px 4px !important;
            margin-top: 8px;
            box-shadow: 0 6px 14px rgba(246,201,220,0.35) !important;
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
            border: 1.5px solid #f6d9e6 !important;
            color: #7a3b52 !important;
        }
        div[class*="st-key-nav_"] button {
            text-align: left !important;
            padding-left: 20px !important;
            position: relative;
        }
        div[class*="st-key-nav_"] button::after {
            content: "›";
            position: absolute;
            right: 18px; top: 50%; transform: translateY(-50%);
            font-size: 20px; font-weight: 700;
        }
        section[data-testid="stSidebar"] details {
            border-radius: 50px !important;
            border: 1.5px solid #f6d9e6 !important;
            background: white !important;
            overflow: hidden;
        }
        section[data-testid="stSidebar"] details summary {
            padding: 6px 18px !important;
            font-weight: 600;
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
            padding: 5px 16px;
            font-size: 20px;
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
        .book-title { font-weight: 700; font-size: 27px; color: #4A2E4D; font-family: 'Inter', sans-serif; }
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

        /* ---- Redes sociales (pills con icono) ---- */
        .social-pill {
            display:flex; align-items:center; gap:10px; background:#fff6fa;
            border:1px solid #f6d9e6; border-radius: 50px; padding: 8px 14px;
            margin-bottom: 8px; text-decoration:none !important; color:#7a3b52 !important;
            font-weight:600; font-size:13px; transition: transform .12s ease-in-out;
        }
        .social-pill:hover { transform: translateX(3px); background:#ffe9f2; }
        .social-emoji { font-size: 18px; }

        /* ---- Galería de imágenes/gifs del home ---- */
        .gallery-thumb-wrap {
            border-radius: 16px; overflow:hidden; border: 2px solid #f6d9e6;
            margin-bottom: 8px; background:#fff6fa;
        }
        .gallery-caption { font-size: 11px; color:#a9647f; text-align:center; padding: 2px 4px 6px 4px; }

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

        /* ---- STUDY archivador de contenidos (video/link/doc) ---- */
        .study-item-card {
            background: #F4ECE0;
            border-radius: 16px;
            padding: 14px 18px;
            margin-bottom: 9px;
            box-shadow: 0 3px 10px rgba(0,0,0,0.06);
            border-left: 7px solid #C9B79B;
        }
        .study-item-title { font-weight: 700; font-size: 27px; color: #4A3B2F; font-family: 'Inter', sans-serif; }

        /* ---- Lenguajes: galería de tarjetas (imágenes, videos, playlists, archivos) ---- */
        .lang-card {
            background: white; border-radius: 18px; overflow:hidden;
            border: 2px solid #f6d9e6; box-shadow: 0 4px 12px rgba(0,0,0,0.06);
            margin-bottom: 16px;
        }
        .lang-card img { width:100%; display:block; max-height:420px; object-fit:cover; }
        .lang-card-body { padding: 14px 18px 18px 18px; }
        .lang-card-title { font-size: 22px !important; font-weight: 700; color:#7a3b52; margin: 0 0 6px 0; }
        .lang-card-body p { font-size: 17px !important; line-height:1.5; color:#4A3B2F; }
        .lang-card .tag-chip { font-size: 13px !important; padding: 4px 14px !important; }
        .lang-card-placeholder {
            width:100%; aspect-ratio: 4/3; display:flex; align-items:center; justify-content:center;
            font-size: 64px; background: linear-gradient(135deg, #ffe3ee, #fff5f8);
        }

        /* ---- "Mis links" — links generales (no asociados a libros), letras grandes ---- */
        .custom-link-card {
            background: white; border-radius: 20px; overflow:hidden;
            border: 2px solid #f6d9e6; box-shadow: 0 4px 12px rgba(0,0,0,0.06);
            padding: 18px 22px; margin-bottom: 16px;
        }
        .custom-link-title { font-size: 24px !important; font-weight: 700; color:#7a3b52; margin:0 0 6px 0; }
        .custom-link-note { font-size: 16px !important; color:#4A3B2F; margin: 6px 0; line-height:1.5; }
        .custom-link-url {
            display:inline-block; font-size: 16px !important; font-weight:600;
            color:#c2185b !important; text-decoration:none !important; word-break: break-all;
        }
        .custom-link-url:hover { text-decoration: underline !important; }

        /* ---- Botón de descarga de archivos adjuntos ---- */
        div[data-testid="stDownloadButton"] button {
            border-radius: 50px !important;
            font-weight: 700 !important;
        }
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
            ("content_type", "TEXT"),
            ("file_b64", "TEXT"),
            ("file_name", "TEXT"),
        ],
        "profile": [
            ("avatar_b64", "TEXT"),
        ],
        "language_cards": [
            ("content_type", "TEXT"),
            ("url", "TEXT"),
            ("file_b64", "TEXT"),
            ("file_name", "TEXT"),
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
            trashed INTEGER DEFAULT 0, created_at TEXT, content_type TEXT,
            file_b64 TEXT, file_name TEXT)""")
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
    run("""CREATE TABLE IF NOT EXISTS social_links (
            platform TEXT PRIMARY KEY, url TEXT)""")
    run("""CREATE TABLE IF NOT EXISTS home_gallery (
            id INTEGER PRIMARY KEY AUTOINCREMENT, image_b64 TEXT, caption TEXT, created_at TEXT)""")
    run("""CREATE TABLE IF NOT EXISTS language_cards (
            id INTEGER PRIMARY KEY AUTOINCREMENT, image_b64 TEXT, caption TEXT, tag TEXT, created_at TEXT,
            content_type TEXT, url TEXT, file_b64 TEXT, file_name TEXT)""")
    run("""CREATE TABLE IF NOT EXISTS study_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, minutes INTEGER, created_at TEXT)""")
    run("""CREATE TABLE IF NOT EXISTS custom_links (
            id INTEGER PRIMARY KEY AUTOINCREMENT, section TEXT, title TEXT, url TEXT,
            note TEXT, created_at TEXT)""")

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


# ---------- Redes sociales ----------
def get_social_links():
    rows = run("SELECT * FROM social_links", fetch=True)
    return {r["platform"]: r["url"] for r in rows} if rows else {}


def save_social_link(platform, url):
    if run("SELECT platform FROM social_links WHERE platform=?", (platform,), fetch=True, one=True):
        run("UPDATE social_links SET url=? WHERE platform=?", (url, platform))
    else:
        run("INSERT INTO social_links (platform, url) VALUES (?,?)", (platform, url))


# ---------- Galería del home (imágenes / gifs) ----------
def get_gallery_images(limit=8):
    return run("SELECT * FROM home_gallery ORDER BY id DESC LIMIT ?", (limit,), fetch=True)


def add_gallery_image(image_file, caption):
    b64 = base64.b64encode(image_file.read()).decode("utf-8")
    run("INSERT INTO home_gallery (image_b64, caption, created_at) VALUES (?,?,?)",
        (b64, caption, datetime.datetime.now().strftime("%Y-%m-%d %H:%M")))


def delete_gallery_image(img_id):
    run("DELETE FROM home_gallery WHERE id=?", (img_id,))


# ---------- Mis links (links generales, NO asociados a libros) ----------
def get_custom_links(section):
    return run("SELECT * FROM custom_links WHERE section=? ORDER BY id DESC", (section,), fetch=True)


def add_custom_link(section, title, url, note):
    run("INSERT INTO custom_links (section, title, url, note, created_at) VALUES (?,?,?,?,?)",
        (section, title, url, note, datetime.datetime.now().strftime("%Y-%m-%d %H:%M")))


def delete_custom_link(link_id):
    run("DELETE FROM custom_links WHERE id=?", (link_id,))


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
def add_item(section, title, link, folder_id, favorite, content_type=None, file_b64=None, file_name=None):
    run("""INSERT INTO items (section, title, link, folder_id, favorite, trashed, created_at,
            content_type, file_b64, file_name) VALUES (?,?,?,?,?,0,?,?,?,?)""",
        (section, title, link, folder_id, int(favorite),
         datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), content_type, file_b64, file_name))


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


def log_study_session(minutes):
    """Registra una sesión de estudio (pomodoro) completada el día de hoy."""
    today = datetime.date.today().strftime("%Y-%m-%d")
    run("INSERT INTO study_sessions (date, minutes, created_at) VALUES (?,?,?)",
        (today, minutes, datetime.datetime.now().strftime("%Y-%m-%d %H:%M")))


def get_study_streak_days():
    """Cuenta cuántos días distintos (consecutivos hacia atrás desde hoy) tienen al menos
    una sesión de estudio (pomodoro) registrada — ya no depende de las entradas de BL/BOOKS."""
    rows = run("SELECT DISTINCT date FROM study_sessions", fetch=True)
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


def get_today_study_minutes():
    today = datetime.date.today().strftime("%Y-%m-%d")
    rows = run("SELECT minutes FROM study_sessions WHERE date=?", (today,), fetch=True)
    return sum(r["minutes"] for r in rows) if rows else 0


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


# ---------- Lenguajes (hoja vinculada a STUDY, con tarjetas de imágenes/videos/archivos) ----------
def get_language_cards(tag=None):
    if tag and tag != "Todas":
        return run("SELECT * FROM language_cards WHERE tag=? ORDER BY id DESC", (tag,), fetch=True)
    return run("SELECT * FROM language_cards ORDER BY id DESC", fetch=True)


def get_language_tags():
    rows = run("SELECT DISTINCT tag FROM language_cards WHERE tag IS NOT NULL AND tag<>'' ORDER BY tag", fetch=True)
    return [r["tag"] for r in rows] if rows else []


def add_language_card(image_file, caption, tag, content_type="image", url=None, attach_file=None):
    b64 = base64.b64encode(image_file.read()).decode("utf-8") if image_file is not None else None
    file_b64 = None
    file_name = None
    if attach_file is not None:
        file_b64 = base64.b64encode(attach_file.read()).decode("utf-8")
        file_name = attach_file.name
    run("""INSERT INTO language_cards (image_b64, caption, tag, created_at, content_type, url, file_b64, file_name)
           VALUES (?,?,?,?,?,?,?,?)""",
        (b64, caption, tag, datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
         content_type, url, file_b64, file_name))


def delete_language_card(card_id):
    run("DELETE FROM language_cards WHERE id=?", (card_id,))

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

    st.markdown('<div class="bow-divider"><span>🎀</span></div>', unsafe_allow_html=True)
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
        if sec == "STUDY":
            # Hoja "Lenguajes": vinculada a STUDY pero como página independiente
            if st.button("　🌐 Lenguajes", use_container_width=True, key="nav_languages",
                         type="primary" if current_page == "languages" else "secondary"):
                goto("languages")
    if st.button("͙֒ FAVORITES ⋆.˚", use_container_width=True, key="nav_fav",
                 type="primary" if current_page == "favorites" else "secondary"):
        goto("favorites")
    if st.button("🗑️ Papelera", use_container_width=True, key="nav_trash",
                 type="primary" if current_page == "trash" else "secondary"):
        goto("trash")

    st.markdown('<div class="bow-divider"><span>🎀</span></div>', unsafe_allow_html=True)
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
    # ZONA IZQUIERDA — buscador, banner de bienvenida, actividad reciente + destacado
    # ------------------------------------------------------------------
    with left:
        st.markdown('<div class="bow-divider"><span>🎀</span></div>', unsafe_allow_html=True)
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
                <span class="deco-cloud" style="top:8px; left:16px; font-size:34px;">☁</span>
                <span class="deco-star" style="top:16px; right:70px; font-size:20px;">✦</span>
                <span class="deco-star" style="top:72%; left:8%; font-size:16px;">✧</span>
                <span class="deco-cloud" style="bottom:14px; right:20px; font-size:28px;">☁</span>
                <span class="deco-star" style="top:14%; right:16%; font-size:14px;">⋆</span>
                <span class="deco-heart" style="bottom:18%; left:22%; font-size:16px;">♡</span>
                <p class="hero-title">Katsearose's Dreamscape ⋆ ̊꩜。</p>
                <p class="hero-sep">────୨ৎ────</p>
                <p class="hero-kaomoji">⋆ ̊꩜。՞ ܸ.ˬ.ܸ՞</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        render_live_clock()
        st.markdown('<div class="bow-divider"><span>🎀</span></div>', unsafe_allow_html=True)

        with st.expander("🖼️ Cambiar las imágenes de portada"):
            for sec in SECTIONS:
                up = st.file_uploader(f"Portada para {sec} (admite GIF animado)", type=["png", "jpg", "jpeg", "webp", "gif"], key=f"cover_up_{sec}")
                if up is not None and st.button(f"Guardar portada de {sec}", key=f"cover_save_{sec}"):
                    save_section_image(sec, up)
                    st.success(f"¡Portada de {sec} actualizada! ✨")
                    st.rerun()

        # ---- Actividad reciente + destacado (antes estaban a la derecha; ahora viven aquí) ----
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

        # ---- Racha de estudio (pomodoro en STUDY) — ya no depende de BL/BOOKS ----
        streak = get_study_streak_days()
        st.markdown(
            f"""
            <div class="streak-card">
                <div class="streak-number">{streak}</div>
                <div class="streak-label">🍅 racha estudiando</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.caption("Completa un pomodoro en STUDY para sumar racha ⋆.˚")

        # ---- Redes sociales (solo Twitter y Pinterest) ----
        st.markdown('<div class="bento-card"><div class="bento-card-title">🔗 Mis redes</div>', unsafe_allow_html=True)
        links = get_social_links()
        any_link = False
        for platform, meta in SOCIAL_PLATFORMS.items():
            url = links.get(platform, "")
            if url:
                any_link = True
                st.markdown(
                    f'<a class="social-pill" href="{url}" target="_blank">'
                    f'<span class="social-emoji">{meta["emoji"]}</span> {meta["label"]}</a>',
                    unsafe_allow_html=True,
                )
        if not any_link:
            st.caption("Aún no agregaste tus links ✨ ábrelos abajo:")
        with st.expander("✏️ Editar mis redes"):
            with st.form("edit_social_links"):
                new_vals = {}
                for platform, meta in SOCIAL_PLATFORMS.items():
                    new_vals[platform] = st.text_input(
                        f"{meta['emoji']} {meta['label']}", value=links.get(platform, ""), key=f"social_{platform}"
                    )
                if st.form_submit_button("💾 Guardar links"):
                    for platform, url in new_vals.items():
                        save_social_link(platform, url.strip())
                    st.success("¡Links guardados! ✨")
                    st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

        # ---- Galería de imágenes / gifs pegadas ----
        st.markdown('<div class="bento-card"><div class="bento-card-title">🖼️ Galería</div>', unsafe_allow_html=True)
        gallery = get_gallery_images(4)
        if not gallery:
            st.caption("Pega tu primera imagen o gif abajo 💗")
        gcols = st.columns(2)
        for idx, g in enumerate(gallery):
            with gcols[idx % 2]:
                st.markdown('<div class="gallery-thumb-wrap">', unsafe_allow_html=True)
                st.image(base64.b64decode(g["image_b64"]), use_container_width=True)
                st.markdown("</div>", unsafe_allow_html=True)
                if g["caption"]:
                    st.markdown(f'<div class="gallery-caption">{g["caption"]}</div>', unsafe_allow_html=True)
                if st.button("🗑️", key=f"delgallery_{g['id']}", use_container_width=True):
                    delete_gallery_image(g["id"])
                    st.rerun()
        with st.expander("➕ Agregar imagen / gif"):
            gimg = st.file_uploader("Imagen o GIF", type=["png", "jpg", "jpeg", "webp", "gif"], key="gallery_up")
            gcap = st.text_input("Descripción (opcional)", key="gallery_cap")
            if gimg is not None and st.button("💾 Guardar en galería", key="gallery_save"):
                add_gallery_image(gimg, gcap.strip())
                st.success("¡Agregado a la galería! ✨")
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    # ------------------------------------------------------------------
    # ZONA DERECHA — accesos rápidos a BL/BOOKS/STUDY
    # ------------------------------------------------------------------
    with right:
        st.markdown('<div class="bento-card"><div class="bento-card-title">🎀 Mis secciones</div>', unsafe_allow_html=True)
        with st.expander("🖼️ Cambiar portadas aquí también"):
            st.caption("(atajo — también puedes cambiarlas desde el panel de la izquierda)")

        for sec in SECTIONS:
            st.markdown('<div class="heart-wrap">', unsafe_allow_html=True)
            cover = get_section_image(sec)
            if cover:
                st.markdown(f'<img class="section-cover" src="data:image/png;base64,{cover}">', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="section-cover-placeholder">{SECTIONS[sec]["emoji"]}</div>', unsafe_allow_html=True)
            if st.button(f"♡ {SECTIONS[sec]['label']} ♡", key=f"enter_{sec}", use_container_width=True):
                goto("section", current_section=sec)
            st.markdown("</div>", unsafe_allow_html=True)
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

    if sec == "STUDY":
        st.caption("📁 Aquí guardas videos, listas de reproducción, links y documentos de preu — organizados por etiqueta.")
        st.markdown(
            '¿Buscas tarjetas de idiomas? Ve a la hoja <b>🌐 Lenguajes</b> desde el menú lateral.',
            unsafe_allow_html=True,
        )

    tab_labels = ["📂 Archivadores", "📋 Lista completa", "💗 Favoritos"]
    if sec == "BL":
        tab_labels.append("🔗 Mis links")
    if sec == "STUDY":
        tab_labels.append("🗓️ Dashboard / Planner")

    tabs = st.tabs(tab_labels)
    with tabs[0]:
        render_archivadores(sec, info)
    with tabs[1]:
        render_full_list(sec)
    with tabs[2]:
        render_section_favorites(sec)
    if sec == "BL":
        with tabs[3]:
            render_links_list(sec)
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
        color = it["folder_color"] or "#f3b8d2"
        heart = '<span class="fav-heart">💗</span>' if it["favorite"] else ""
        c1, c2 = st.columns([6, 1])
        with c1:
            if sec == "STUDY":
                ctype = STUDY_CONTENT_TYPES.get(it["content_type"], {"emoji": "🗂️"})
                st.markdown(
                    f"""<div class="study-item-card" style="border-left-color:{color};">
                            <span class="study-item-title">{ctype['emoji']} {it['title']}</span> {heart}
                            <span class="tag-chip" style="background:{color};">● {it['folder_name'] or 'Sin etiqueta'}</span>
                        </div>""",
                    unsafe_allow_html=True,
                )
            else:
                score = average_score(it["id"])
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
        color = it["folder_color"] or "#f3b8d2"
        c1, c2 = st.columns([6, 1])
        with c1:
            if sec == "STUDY":
                ctype = STUDY_CONTENT_TYPES.get(it["content_type"], {"emoji": "🗂️"})
                st.markdown(
                    f"""<div class="study-item-card" style="border-left-color:{color};">
                            <span class="study-item-title">{ctype['emoji']} {it['title']}</span> <span class="fav-heart">💗</span>
                            <span class="tag-chip" style="background:{color};">● {it['folder_name'] or 'Sin etiqueta'}</span>
                        </div>""",
                    unsafe_allow_html=True,
                )
            else:
                score = average_score(it["id"])
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


def render_links_list(sec):
    """🔗 Mis links — links SUELTOS que quieres guardar y que NO están asociados a
    ningún título/libro (ej: sitios de referencia, blogs, tiendas, foros, etc.).
    Letras grandes, igual que en la hoja de Lenguajes."""
    st.caption("Guarda aquí links de sitios que no están relacionados a tus títulos de BL — blogs, tiendas, foros, lo que sea ✨")

    with st.expander("➕ Agregar nuevo link"):
        with st.form(f"add_customlink_{sec}", clear_on_submit=True):
            ltitle = st.text_input("Nombre del sitio")
            lurl = st.text_input("URL (https://...)")
            lnote = st.text_area("Nota (opcional)", height=80)
            if st.form_submit_button("Guardar 💾") and ltitle.strip() and lurl.strip():
                add_custom_link(sec, ltitle.strip(), lurl.strip(), lnote.strip())
                st.success("¡Link guardado! ✨")
                st.rerun()

    st.markdown("---")
    links = get_custom_links(sec)
    if not links:
        st.info("Todavía no guardaste ningún link suelto (˶˃˂˶) ¡agrega el primero arriba!")
        return
    for lk in links:
        c1, c2 = st.columns([6, 1])
        with c1:
            note_html = f'<p class="custom-link-note">{lk["note"]}</p>' if lk["note"] else ""
            st.markdown(
                f"""<div class="custom-link-card">
                        <p class="custom-link-title">🔗 {lk['title']}</p>
                        <a class="custom-link-url" href="{lk['url']}" target="_blank">{lk['url']}</a>
                        {note_html}
                    </div>""",
                unsafe_allow_html=True,
            )
        with c2:
            if st.button("🗑️", key=f"delcustomlink_{lk['id']}", use_container_width=True):
                delete_custom_link(lk["id"])
                st.rerun()


def render_archivadores(sec, info):
    folders = get_folders(sec)
    folder_word = "etiqueta" if sec == "STUDY" else "archivador"

    with st.expander(f"🎀 Crear nueva {folder_word}"):
        with st.form(f"add_folder_{sec}", clear_on_submit=True):
            placeholder = "ej: YouTube preu, Playlists, Links preu, Documentos..." if sec == "STUDY" else "ej: Yaoi, Manhwa, Física..."
            fname = st.text_input(f"Nombre de la {folder_word}", placeholder=placeholder)
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
# PÁGINA: dentro de un archivador → lista alfabética de libros / contenidos
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
        content_type = None
        if sec == "STUDY":
            # IMPORTANTE: este selectbox va FUERA del st.form — dentro de un form,
            # streamlit no vuelve a dibujar la página hasta que envías el formulario,
            # así que el campo de link/archivo se quedaba "pegado" al tipo anterior.
            # Al ponerlo aquí afuera, el cambio de tipo se refleja al instante.
            content_type = st.selectbox(
                "Tipo de contenido",
                options=list(STUDY_CONTENT_TYPES.keys()),
                format_func=lambda k: f"{STUDY_CONTENT_TYPES[k]['emoji']} {STUDY_CONTENT_TYPES[k]['label']}",
                key=f"content_type_select_{folder_id}",
            )

        with st.form(f"add_item_{folder_id}", clear_on_submit=True):
            title = st.text_input("Título")
            if sec == "STUDY":
                needs_file = content_type in ("doc", "image")
                attach = None
                link = ""
                if needs_file:
                    file_label = "🖼️ Adjuntar imagen" if content_type == "image" else "📎 Adjuntar archivo (PDF, doc, etc.)"
                    attach = st.file_uploader(file_label, type=None, key=f"attach_{folder_id}")
                else:
                    link_help = {
                        "video": "🔗 Pega aquí el link del video de YouTube",
                        "playlist": "🔗 Pega aquí el link de la lista de reproducción",
                        "link": "🔗 Pega aquí el link de la página",
                    }[content_type]
                    link = st.text_input(link_help)
                favorite = st.checkbox("💗 Marcar como importante")
            else:
                attach = None
                link = st.text_input(info["link_label"])
                favorite = st.checkbox("💗 Marcar como favorito")
            if st.form_submit_button("Guardar 💾") and title.strip():
                file_b64 = None
                file_name = None
                if attach is not None:
                    file_b64 = base64.b64encode(attach.read()).decode("utf-8")
                    file_name = attach.name
                add_item(sec, title.strip(), link.strip(), folder_id, favorite, content_type, file_b64, file_name)
                st.success("¡Guardado! (♡ˊ͈ ꒳ ˋ͈)")
                st.rerun()

    st.markdown("---")
    items = get_items(sec, folder_id)
    if not items:
        st.info("Todavía no hay nada aquí (˶˃˂˶) ¡agrega tu primer título arriba!")
        return

    for it in items:
        heart = '<span class="fav-heart">💗</span>' if it["favorite"] else ""
        c1, c2, c3 = st.columns([5, 1, 1])
        with c1:
            if sec == "STUDY":
                ctype = STUDY_CONTENT_TYPES.get(it["content_type"], {"emoji": "🗂️", "label": "Archivo"})
                st.markdown(
                    f"""<div class="study-item-card">
                            <span class="study-item-title">{ctype['emoji']} {it['title']}</span> {heart}<br>
                            <span class="mini-course-meta">{ctype['label']}</span>
                        </div>""",
                    unsafe_allow_html=True,
                )
                if it["content_type"] == "image" and it["file_b64"]:
                    st.image(base64.b64decode(it["file_b64"]), use_container_width=True)
                if it["link"]:
                    st.markdown(f"[🔗 Abrir enlace]({it['link']})")
                if it["file_b64"] and it["content_type"] != "image":
                    st.download_button(
                        "📎 Descargar archivo adjunto",
                        data=base64.b64decode(it["file_b64"]),
                        file_name=it["file_name"] or "archivo",
                        key=f"dlfolder_{it['id']}",
                        use_container_width=True,
                    )
            else:
                score = average_score(it["id"])
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
    is_study = sec == "STUDY"

    col1, col2 = st.columns([5, 1])
    with col1:
        title_icon = STUDY_CONTENT_TYPES.get(item["content_type"], {}).get("emoji", "") if is_study else ""
        st.markdown(f"## {title_icon} {item['title']} {'💗' if item['favorite'] else ''}")
    with col2:
        if st.button("🗑️ Eliminar", use_container_width=True):
            soft_delete_item(item_id)
            st.success("Movido a la papelera 🗑️")
            goto("section", current_section=sec)
            st.rerun()

    if item["link"]:
        st.markdown(f"[{info['link_label']}]({item['link']})")

    if is_study:
        if item["content_type"] == "image" and item["file_b64"]:
            st.image(base64.b64decode(item["file_b64"]), use_container_width=True)
        elif item["file_b64"]:
            st.download_button(
                "📎 Descargar archivo adjunto",
                data=base64.b64decode(item["file_b64"]),
                file_name=item["file_name"] or "archivo",
                use_container_width=True,
            )

    if not is_study:
        score = average_score(item_id)
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
    st.markdown("### ✏️ Nueva entrada" if not is_study else "### ✏️ Notas sobre este contenido")
    with st.form("new_entry_form", clear_on_submit=True):
        text = st.text_area("¿Qué quieres anotar hoy?")
        if is_study:
            stars = 0
        else:
            stars = st.slider("Puntuación de esta entrada", 1, 5, 5)
        image = st.file_uploader("Imagen o GIF (opcional)", type=["png", "jpg", "jpeg", "gif", "webp"])
        if st.form_submit_button("Publicar 🌸") and text.strip():
            add_entry(item_id, text.strip(), image, stars if stars else None)
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
            stars_row = f'<span class="stars">{"⭐"*e["stars"]}{"☆"*(5-e["stars"])}</span><br>' if e["stars"] else ""
            st.markdown(
                f"""<div class="tweet-card">
                        <span class="tweet-date">{e['date']}</span><br>
                        {stars_row}
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
        if it["section"] == "STUDY":
            ctype = STUDY_CONTENT_TYPES.get(it["content_type"], {"emoji": "🗂️"})
            st.markdown(
                f"""<div class="study-item-card">
                        <span class="study-item-title">{ctype['emoji']} {it['title']}</span> <span class="fav-heart">💗</span>
                        <span class="tag-chip" style="background:#d98bad;">{it['section']}</span>
                    </div>""",
                unsafe_allow_html=True,
            )
        else:
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


def render_pomodoro():
    """Temporizador Pomodoro: cuenta visualmente en vivo (JS) y, al completar la sesión,
    un botón nativo de Streamlit registra la sesión de estudio (esto es lo que alimenta la racha)."""
    st.markdown('<div class="dash-card"><div class="dash-title">🍅 Pomodoro</div>', unsafe_allow_html=True)
    minutes = st.selectbox("Duración de la sesión", [15, 25, 30, 45, 50], index=1, key="pomo_minutes")
    today_min = get_today_study_minutes()
    st.caption(f"Hoy ya llevas **{today_min} min** estudiados ⋆.˚")

    components.html(
        f"""
        <div style="font-family:'Inter',sans-serif; text-align:center;">
            <div id="pomo-display" style="font-size:52px; font-weight:800; color:#6D5F5A;">{minutes:02d}:00</div>
            <div style="display:flex; gap:10px; justify-content:center; margin-top:8px;">
                <button id="pomo-start" style="background:#6D5F5A; color:white; border:none; border-radius:50px; padding:8px 20px; font-weight:700; cursor:pointer;">▶️ Iniciar</button>
                <button id="pomo-pause" style="background:white; color:#6D5F5A; border:2px solid #6D5F5A; border-radius:50px; padding:8px 20px; font-weight:700; cursor:pointer;">⏸️ Pausar</button>
                <button id="pomo-reset" style="background:white; color:#a9647f; border:2px solid #f6c9dc; border-radius:50px; padding:8px 20px; font-weight:700; cursor:pointer;">🔄 Reiniciar</button>
            </div>
            <div id="pomo-msg" style="margin-top:10px; font-size:13px; color:#a9647f;"></div>
        </div>
        <script>
        let totalSeconds = {minutes} * 60;
        let remaining = totalSeconds;
        let timer = null;
        const display = document.getElementById('pomo-display');
        const msg = document.getElementById('pomo-msg');
        function render() {{
            const m = Math.floor(remaining/60).toString().padStart(2,'0');
            const s = (remaining%60).toString().padStart(2,'0');
            display.textContent = m + ':' + s;
        }}
        document.getElementById('pomo-start').onclick = () => {{
            if (timer) return;
            timer = setInterval(() => {{
                remaining -= 1;
                render();
                if (remaining <= 0) {{
                    clearInterval(timer);
                    timer = null;
                    msg.innerHTML = '¡Sesión terminada! ✧ baja y marca "✅ Completé mi pomodoro" para sumar tu racha (˶ᵔ ᵕ ᵔ˶)';
                }}
            }}, 1000);
        }};
        document.getElementById('pomo-pause').onclick = () => {{ clearInterval(timer); timer = null; }};
        document.getElementById('pomo-reset').onclick = () => {{
            clearInterval(timer); timer = null; remaining = totalSeconds; msg.innerHTML=''; render();
        }};
        render();
        </script>
        """,
        height=170,
    )

    if st.button("✅ Completé mi pomodoro", use_container_width=True, key="pomo_complete"):
        log_study_session(minutes)
        st.success(f"¡Sesión de {minutes} min registrada! Tu racha de estudio subió 🍅✨")
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)


def page_study_dashboard():
    st.markdown('<div class="study-beige">', unsafe_allow_html=True)

    render_pomodoro()

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
# PÁGINA: LENGUAJES (hoja vinculada a STUDY, no anidada dentro de ella)
# Galería de tarjetas para repasar vocabulario / gramática, guardar videos,
# listas de reproducción, imágenes grandes y archivos adjuntos.
# ============================================================
def page_languages():
    st.markdown(
        """
        <div class="plaid-banner">
            <p class="plaid-title" style="font-size:56px;">🌐 Lenguajes</p>
            <p class="plaid-sep">────୨ৎ────</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.caption("Vinculada a STUDY, pero con su propio espacio — guarda aquí imágenes, videos, listas de reproducción, links y archivos para repasar (vocabulario, gramática, apuntes, etc.)")

    tags = ["Todas"] + get_language_tags()
    selected_tag = st.selectbox("Filtrar por etiqueta", tags, key="lang_tag_filter")

    with st.expander("➕ Agregar nueva tarjeta"):
        # IMPORTANTE: el selector de tipo va FUERA del st.form para que el campo
        # de abajo (imagen / link / archivo) cambie al instante al elegir otro tipo.
        ctype = st.selectbox(
            "Tipo de tarjeta",
            options=list(LANG_CONTENT_TYPES.keys()),
            format_func=lambda k: f"{LANG_CONTENT_TYPES[k]['emoji']} {LANG_CONTENT_TYPES[k]['label']}",
            key="lang_ctype",
        )
        with st.form("add_lang_card", clear_on_submit=True):
            lcap = st.text_input("Descripción / traducción (opcional)")
            ltag = st.text_input("Etiqueta (ej: Inglés, Francés, Gramática...)")

            limg = None
            lurl = None
            lattach = None
            if ctype == "image":
                limg = st.file_uploader("Imagen (vocabulario, apuntes, captura, etc.)", type=["png", "jpg", "jpeg", "webp", "gif"])
            elif ctype in ("video", "playlist", "link"):
                lurl = st.text_input("🔗 URL (link del video, playlist o página)")
                limg = st.file_uploader("Miniatura opcional", type=["png", "jpg", "jpeg", "webp", "gif"], key="lang_thumb")
            elif ctype == "file":
                lattach = st.file_uploader("📎 Archivo a adjuntar (PDF, doc, etc.)", type=None, key="lang_file")
                lurl = st.text_input("🔗 Link opcional (Drive, Notion, etc.)")

            submitted = st.form_submit_button("Guardar 💾")
            if submitted:
                valid = (ctype == "image" and limg is not None) or \
                        (ctype in ("video", "playlist", "link") and lurl and lurl.strip()) or \
                        (ctype == "file" and lattach is not None)
                if valid:
                    add_language_card(limg, lcap.strip(), ltag.strip() or "General",
                                       content_type=ctype, url=(lurl.strip() if lurl else None),
                                       attach_file=lattach)
                    st.success("¡Tarjeta agregada! ✨")
                    st.rerun()
                else:
                    st.warning("Falta la imagen, el link o el archivo según el tipo elegido (˶˃˂˶)")

    st.markdown("---")
    cards = get_language_cards(selected_tag)
    if not cards:
        st.info("Todavía no hay tarjetas aquí (˶˃˂˶) ¡agrega la primera arriba!")
        return

    cols = st.columns(2)
    for i, card in enumerate(cards):
        ctype = card["content_type"] or "image"
        meta = LANG_CONTENT_TYPES.get(ctype, {"emoji": "🗂️", "label": "Tarjeta"})
        with cols[i % 2]:
            st.markdown('<div class="lang-card">', unsafe_allow_html=True)
            if card["image_b64"]:
                st.image(base64.b64decode(card["image_b64"]), use_container_width=True)
            elif ctype != "file":
                st.markdown(f'<div class="lang-card-placeholder">{meta["emoji"]}</div>', unsafe_allow_html=True)
            st.markdown('<div class="lang-card-body">', unsafe_allow_html=True)
            st.markdown(f'<p class="lang-card-title">{meta["emoji"]} {meta["label"]}</p>', unsafe_allow_html=True)
            if card["tag"]:
                st.markdown(f'<span class="tag-chip" style="background:#d9749a;">{card["tag"]}</span>', unsafe_allow_html=True)
            if card["caption"]:
                st.markdown(f"<p>{card['caption']}</p>", unsafe_allow_html=True)
            st.markdown("</div></div>", unsafe_allow_html=True)
            if card["url"]:
                st.markdown(f"[🔗 Abrir enlace]({card['url']})")
            if card["file_b64"]:
                st.download_button(
                    "📎 Descargar archivo",
                    data=base64.b64decode(card["file_b64"]),
                    file_name=card["file_name"] or "archivo",
                    key=f"dllang_{card['id']}",
                    use_container_width=True,
                )
            if st.button("🗑️ Eliminar", key=f"dellang_{card['id']}", use_container_width=True):
                delete_language_card(card["id"])
                st.rerun()


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
elif page == "languages":
    page_languages()
