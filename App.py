"""
🌸 Katsearose's Dreamscape 🌸
Bitácora otaku en Streamlit: BL, Books y Study con archivadores,
hilos tipo tweet, papelera, perfil y dashboard de horarios.
"""

import streamlit as st
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
        @import url('https://fonts.googleapis.com/css2?family=Quicksand:wght@400;600;700&family=Caveat:wght@600;700&display=swap');

        html, body, [class*="css"] { font-family: 'Quicksand', sans-serif; }

        .stApp {
            background:
                radial-gradient(circle, #f9d6e3 1px, transparent 1px) 0 0/26px 26px,
                #ffffff;
        }

        section[data-testid="stSidebar"] {
            background: #fff6fa;
            border-right: 2px dashed #f3b8d2;
        }

        div.stButton > button {
            border-radius: 14px;
            font-weight: 600;
            border: 1px solid #f6c9dc;
            transition: transform .08s ease-in-out;
        }
        div.stButton > button:active { transform: scale(0.92); }

        /* ---- Perfil (sidebar) ---- */
        .profile-card {
            text-align: center;
            background: #ffffff;
            border: 2px dashed #f3b8d2;
            border-radius: 20px;
            padding: 14px 10px 10px 10px;
            margin-bottom: 14px;
        }
        .profile-name {
            font-family: 'Caveat', cursive;
            font-size: 26px;
            color: #C2185B;
            font-weight: 700;
            margin-top: 4px;
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
            font-family: 'Caveat', cursive;
            font-size: 46px;
            color: #7a3b52;
            margin: 0;
        }
        .plaid-sep { color: #a9647f; letter-spacing: 2px; margin: 4px 0; }
        .plaid-kaomoji { color: #a9647f; font-size: 15px; }

        /* ---- Botones corazón del home ---- */
        .heart-wrap { text-align: center; }
        .heart-label {
            font-family: 'Caveat', cursive;
            font-size: 24px;
            color: #9b4468;
            margin-top: -6px;
        }

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
            top: -16px;
            left: 14px;
            background: white;
            border: 2px dashed #d98bad;
            border-radius: 10px;
            padding: 3px 12px;
            font-size: 13px;
            font-weight: 700;
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
        .book-title { font-weight: 700; font-size: 17px; color: #4A2E4D; }
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
        .dash-title { font-weight: 700; color: #7a3b52; font-size: 16px; margin-bottom: 8px;}
        .badge-chip {
            display:inline-block; background:#f8d7e6; color:#a1315a;
            border-radius: 10px; padding: 2px 10px; font-size: 11px; font-weight:700;
        }

        .trash-card {
            background: #fff5f5; border: 1.5px dashed #e6a3a3;
            border-radius: 14px; padding: 10px 16px; margin-bottom: 8px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# BASE DE DATOS
# ============================================================
def get_conn():
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
    conn.close()
    return data


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


# ---------- Folders (archivadores) ----------
def get_folders(section):
    return run("SELECT * FROM folders WHERE section=? ORDER BY name", (section,), fetch=True)


def add_folder(section, name, color):
    run("INSERT INTO folders (section, name, color) VALUES (?,?,?)", (section, name, color))


def folder_item_count(folder_id):
    r = run("SELECT COUNT(*) n FROM items WHERE folder_id=? AND trashed=0", (folder_id,), fetch=True, one=True)
    return r["n"] if r else 0


# ---------- Items ----------
def add_item(section, title, link, folder_id, favorite):
    run("INSERT INTO items (section, title, link, folder_id, favorite, trashed, created_at) VALUES (?,?,?,?,?,0,?)",
        (section, title, link, folder_id, int(favorite), datetime.datetime.now().strftime("%Y-%m-%d %H:%M")))


def get_items(section, folder_id):
    return run("SELECT * FROM items WHERE section=? AND folder_id=? AND trashed=0 ORDER BY title COLLATE NOCASE",
               (section, folder_id), fetch=True)


def get_favorites_all():
    return run("SELECT * FROM items WHERE favorite=1 AND trashed=0 ORDER BY title COLLATE NOCASE", fetch=True)


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
        st.image(base64.b64decode(prof["avatar_b64"]), width=90)
    else:
        st.markdown('<div style="font-size:60px;">🐰</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="profile-name">{prof["name"]}</div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    with st.expander("✏️ Editar perfil"):
        new_name = st.text_input("Nombre", value=prof["name"])
        new_avatar = st.file_uploader("Foto de perfil", type=["png", "jpg", "jpeg", "webp"], key="avatar_up")
        if st.button("💾 Guardar perfil", use_container_width=True):
            save_profile(new_name, new_avatar)
            st.success("¡Perfil actualizado! (♡ˊ͈ ꒳ ˋ͈)")
            st.rerun()

    st.markdown("---")
    if st.button("🏠 Inicio", use_container_width=True):
        goto("home")
    for sec in SECTIONS:
        if st.button(SECTIONS[sec]["label"], use_container_width=True, key=f"nav_{sec}"):
            goto("section", current_section=sec)
    if st.button("͙֒ FAVORITES ⋆.˚", use_container_width=True):
        goto("favorites")
    if st.button("🗑️ Papelera", use_container_width=True):
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
    st.markdown(
        """
        <div class="plaid-banner">
            <p class="plaid-title">Katsearose's Dreamscape ⋆ ̊꩜。</p>
            <p class="plaid-sep">────୨ৎ────</p>
            <p class="plaid-kaomoji">⋆ ̊꩜。՞ ܸ.ˬ.ܸ՞</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        '<p style="text-align:center; color:#a9647f;">presiona un corazoncito para entrar (˶˃˂˶)</p>',
        unsafe_allow_html=True,
    )

    cols = st.columns(3)
    for col, sec in zip(cols, SECTIONS):
        with col:
            st.markdown('<div class="heart-wrap">', unsafe_allow_html=True)
            with st.container(key=f"home_heart_{sec}"):
                if st.button(SECTIONS[sec]["emoji"], key=f"enter_{sec}"):
                    goto("section", current_section=sec)
            st.markdown(f'<p class="heart-label">{SECTIONS[sec]["label"]}</p>', unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(
        """
        <style>
        .st-key-home_heart_BL button, .st-key-home_heart_BOOKS button, .st-key-home_heart_STUDY button {
            font-size: 46px !important; padding: 22px 0 !important; width: 100%;
            background: white !important; border-radius: 50% !important;
            border: 3px solid #f6c9dc !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# PÁGINA: SECCIÓN → grid de archivadores (carpetas)
# ============================================================
def page_section():
    sec = st.session_state.get("current_section", "BL")
    info = SECTIONS[sec]
    st.markdown(f"## {info['label']}")

    if sec == "STUDY":
        tab_arch, tab_dash = st.tabs(["📂 Mis archivadores", "🗓️ Dashboard / Planner"])
        with tab_arch:
            render_archivadores(sec, info)
        with tab_dash:
            page_study_dashboard()
    else:
        render_archivadores(sec, info)


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
    cols = st.columns(3)
    for i, f in enumerate(folders):
        n = folder_item_count(f["id"])
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
    st.markdown("### ✏️ Nueva entrada")
    with st.form("new_entry_form", clear_on_submit=True):
        text = st.text_area("¿Qué quieres anotar hoy?")
        stars = st.slider("Puntuación de esta entrada", 1, 5, 5)
        image = st.file_uploader("Imagen (opcional)", type=["png", "jpg", "jpeg", "gif", "webp"])
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
