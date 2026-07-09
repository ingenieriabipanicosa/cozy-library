"""
🌸 Bitácora Otaku 🌸
Una app en Streamlit para llevar registro de tus BL, Books y Study
con puntuación por estrellas, favoritos, hilos tipo Twitter,
carpetas de colores y sincronización opcional con GitHub.
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
    page_title="🌸 Bitácora Otaku 🌸",
    page_icon="🌸",
    layout="wide",
    initial_sidebar_state="expanded",
)

DB_PATH = "otaku_bitacora.db"

SECTIONS = {
    "BL": {"label": "💗 BL", "emoji": "💗", "link_label": "🔗 Enlace donde lo leo"},
    "BOOKS": {"label": "📚 Books", "emoji": "📚", "link_label": "🔗 Enlace donde lo leo"},
    "STUDY": {"label": "📝 Study", "emoji": "📝", "link_label": "☁️ Enlace de Google Drive / Notion"},
}

DEFAULT_COLORS = ["#FFB6C1", "#B5EAD7", "#C7CEEA", "#FFDAC1", "#E2F0CB", "#F1C0E8", "#FFF5BA"]

# ============================================================
# ESTILO "KAWAII" (CSS)
# ============================================================
def inject_css():
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Quicksand:wght@400;600;700&family=Poppins:wght@400;600&display=swap');

        html, body, [class*="css"]  {
            font-family: 'Quicksand', sans-serif;
        }

        .stApp {
            background: linear-gradient(160deg, #FFE9F0 0%, #F1E6FF 45%, #E6F0FF 100%);
        }

        /* Tarjetas grandes de inicio */
        .home-card {
            background: white;
            border-radius: 28px;
            padding: 40px 20px;
            text-align: center;
            box-shadow: 0 8px 20px rgba(255, 182, 193, 0.35);
            transition: transform 0.15s ease-in-out;
            border: 3px solid #FFD6E8;
        }
        .home-card:hover {
            transform: translateY(-6px) scale(1.02);
        }
        .home-title {
            font-family: 'Poppins', sans-serif;
            font-weight: 700;
            font-size: 42px;
            text-align: center;
            color: #C2185B;
            margin-bottom: 0px;
        }
        .home-sub {
            text-align: center;
            color: #9C7AB0;
            margin-bottom: 30px;
            font-size: 16px;
        }

        /* Tarjeta de item (libro) */
        .book-card {
            background: white;
            border-radius: 18px;
            padding: 14px 18px;
            margin-bottom: 10px;
            box-shadow: 0 3px 10px rgba(0,0,0,0.06);
            border-left: 8px solid #FFD6E8;
        }
        .book-title {
            font-weight: 700;
            font-size: 18px;
            color: #4A2E4D;
        }
        .stars {
            color: #FFC107;
            font-size: 16px;
        }
        .fav-heart {
            color: #FF4081;
            font-size: 20px;
        }
        .tag-chip {
            display: inline-block;
            padding: 2px 10px;
            border-radius: 12px;
            font-size: 12px;
            color: white;
            font-weight: 600;
        }

        /* Tweet-like entries */
        .tweet-card {
            background: white;
            border-radius: 16px;
            padding: 14px 18px;
            margin-bottom: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
            border: 1px solid #F3D9E8;
        }
        .tweet-date {
            color: #B98BC9;
            font-size: 12px;
            font-weight: 600;
        }

        div.stButton > button {
            border-radius: 14px;
            font-weight: 600;
            border: none;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# BASE DE DATOS (SQLite)
# ============================================================
def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS folders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            section TEXT NOT NULL,
            name TEXT NOT NULL,
            color TEXT NOT NULL
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            section TEXT NOT NULL,
            title TEXT NOT NULL,
            link TEXT,
            folder_id INTEGER,
            favorite INTEGER DEFAULT 0,
            created_at TEXT
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_id INTEGER NOT NULL,
            date TEXT,
            text TEXT,
            image_b64 TEXT,
            stars INTEGER
        )
    """)
    conn.commit()

    # Carpetas por defecto si no existen
    for sec in SECTIONS:
        c.execute("SELECT COUNT(*) as n FROM folders WHERE section=?", (sec,))
        if c.fetchone()["n"] == 0:
            c.execute(
                "INSERT INTO folders (section, name, color) VALUES (?,?,?)",
                (sec, "General", DEFAULT_COLORS[0]),
            )
    conn.commit()
    conn.close()


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


# ---------- Folders ----------
def get_folders(section):
    return run("SELECT * FROM folders WHERE section=? ORDER BY name", (section,), fetch=True)


def add_folder(section, name, color):
    run("INSERT INTO folders (section, name, color) VALUES (?,?,?)", (section, name, color))


# ---------- Items ----------
def add_item(section, title, link, folder_id, favorite):
    run(
        "INSERT INTO items (section, title, link, folder_id, favorite, created_at) VALUES (?,?,?,?,?,?)",
        (section, title, link, folder_id, int(favorite), datetime.datetime.now().isoformat()),
    )


def get_items(section, folder_id=None):
    if folder_id and folder_id != "Todas":
        rows = run(
            "SELECT * FROM items WHERE section=? AND folder_id=? ORDER BY title COLLATE NOCASE",
            (section, folder_id), fetch=True,
        )
    else:
        rows = run(
            "SELECT * FROM items WHERE section=? ORDER BY title COLLATE NOCASE",
            (section,), fetch=True,
        )
    return rows


def toggle_favorite(item_id, current):
    run("UPDATE items SET favorite=? WHERE id=?", (0 if current else 1, item_id))


def get_item(item_id):
    return run("SELECT * FROM items WHERE id=?", (item_id,), fetch=True, one=True)


# ---------- Entries (hilo tipo tweets) ----------
def add_entry(item_id, text, image_file, stars):
    img_b64 = None
    if image_file is not None:
        img_b64 = base64.b64encode(image_file.read()).decode("utf-8")
    run(
        "INSERT INTO entries (item_id, date, text, image_b64, stars) VALUES (?,?,?,?,?)",
        (item_id, datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), text, img_b64, stars),
    )


def get_entries(item_id):
    return run(
        "SELECT * FROM entries WHERE item_id=? ORDER BY id DESC", (item_id,), fetch=True
    )


def average_score(item_id):
    rows = run("SELECT stars FROM entries WHERE item_id=?", (item_id,), fetch=True)
    if not rows:
        return 0.0
    vals = [r["stars"] for r in rows if r["stars"] is not None]
    if not vals:
        return 0.0
    return round(sum(vals) / len(vals), 1)


def stars_html(score):
    full = int(round(score))
    full = max(0, min(5, full))
    return "⭐" * full + "☆" * (5 - full)


# ============================================================
# SINCRONIZACIÓN CON GITHUB (opcional, vía st.secrets)
# ============================================================
def github_configured():
    return all(
        k in st.secrets for k in ("GITHUB_TOKEN", "GITHUB_REPO", "GITHUB_DB_PATH")
    ) if hasattr(st, "secrets") else False


def github_headers():
    return {
        "Authorization": f"token {st.secrets['GITHUB_TOKEN']}",
        "Accept": "application/vnd.github+json",
    }


def github_api_url():
    repo = st.secrets["GITHUB_REPO"]  # ej: "usuario/mi-repo"
    path = st.secrets["GITHUB_DB_PATH"]  # ej: "data/otaku_bitacora.db"
    return f"https://api.github.com/repos/{repo}/contents/{path}"


def load_db_from_github():
    """Descarga la base de datos guardada en GitHub (si existe) al iniciar la app."""
    if not github_configured():
        return
    try:
        r = requests.get(github_api_url(), headers=github_headers(), timeout=15)
        if r.status_code == 200:
            content = base64.b64decode(r.json()["content"])
            Path(DB_PATH).write_bytes(content)
    except Exception as e:
        st.sidebar.warning(f"No se pudo cargar desde GitHub: {e}")


def save_db_to_github():
    """Sube el archivo .db actual al repo de GitHub (crea o actualiza)."""
    if not github_configured():
        st.sidebar.error("Faltan GITHUB_TOKEN / GITHUB_REPO / GITHUB_DB_PATH en secrets.")
        return
    try:
        content_bytes = Path(DB_PATH).read_bytes()
        content_b64 = base64.b64encode(content_bytes).decode("utf-8")

        # Necesitamos el sha actual si el archivo ya existe, para poder actualizarlo
        sha = None
        r = requests.get(github_api_url(), headers=github_headers(), timeout=15)
        if r.status_code == 200:
            sha = r.json().get("sha")

        payload = {
            "message": f"🌸 Update bitácora {datetime.datetime.now().isoformat()}",
            "content": content_b64,
        }
        if sha:
            payload["sha"] = sha

        r2 = requests.put(github_api_url(), headers=github_headers(), data=json.dumps(payload), timeout=15)
        if r2.status_code in (200, 201):
            st.sidebar.success("✅ Guardado en GitHub")
        else:
            st.sidebar.error(f"Error GitHub: {r2.status_code} - {r2.text[:200]}")
    except Exception as e:
        st.sidebar.error(f"Error al guardar en GitHub: {e}")


# ============================================================
# NAVEGACIÓN (session_state)
# ============================================================
def goto(page, **kwargs):
    st.session_state["page"] = page
    for k, v in kwargs.items():
        st.session_state[k] = v


if "page" not in st.session_state:
    st.session_state["page"] = "home"

# ============================================================
# INICIALIZACIÓN
# ============================================================
inject_css()

if "db_loaded" not in st.session_state:
    load_db_from_github()
    st.session_state["db_loaded"] = True

init_db()

# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    st.markdown("### 🌸 Menú")
    if st.button("🏠 Inicio", use_container_width=True):
        goto("home")
    st.markdown("---")
    for sec in SECTIONS:
        if st.button(SECTIONS[sec]["label"], use_container_width=True, key=f"nav_{sec}"):
            goto("section", current_section=sec)
    st.markdown("---")
    if github_configured():
        if st.button("☁️ Guardar en GitHub", use_container_width=True):
            save_db_to_github()
        st.caption("Sincronización con GitHub activa ✅")
    else:
        st.caption(
            "💡 Para guardar tus datos en GitHub, agrega en `.streamlit/secrets.toml`:\n\n"
            "```\nGITHUB_TOKEN = \"tu_token\"\nGITHUB_REPO = \"usuario/repo\"\nGITHUB_DB_PATH = \"data/otaku_bitacora.db\"\n```"
        )

# ============================================================
# PÁGINA: HOME
# ============================================================
def page_home():
    st.markdown('<p class="home-title">🌸 Bitácora Otaku 🌸</p>', unsafe_allow_html=True)
    st.markdown('<p class="home-sub">elige a dónde quieres entrar hoy ✨</p>', unsafe_allow_html=True)

    cols = st.columns(3)
    icons = {"BL": "💗", "BOOKS": "📚", "STUDY": "📝"}
    for col, sec in zip(cols, SECTIONS):
        with col:
            st.markdown(
                f"""<div class="home-card">
                        <div style="font-size:60px">{icons[sec]}</div>
                        <div style="font-size:22px; font-weight:700; color:#C2185B;">{sec}</div>
                    </div>""",
                unsafe_allow_html=True,
            )
            if st.button(f"Entrar a {sec}", key=f"enter_{sec}", use_container_width=True):
                goto("section", current_section=sec)


# ============================================================
# PÁGINA: SECCIÓN (lista de libros/temas de una sección)
# ============================================================
def page_section():
    sec = st.session_state.get("current_section", "BL")
    info = SECTIONS[sec]
    st.markdown(f"## {info['label']}")

    folders = get_folders(sec)
    folder_names = ["Todas"] + [f["name"] for f in folders]
    folder_map = {f["name"]: f["id"] for f in folders}
    color_map = {f["id"]: f["color"] for f in folders}

    col_a, col_b = st.columns([2, 1])
    with col_a:
        selected_folder_name = st.selectbox("📁 Filtrar por carpeta/etiqueta", folder_names)
    with col_b:
        show_only_fav = st.checkbox("💗 Solo favoritos")

    folder_id = folder_map.get(selected_folder_name) if selected_folder_name != "Todas" else None
    items = get_items(sec, folder_id)

    if show_only_fav:
        items = [i for i in items if i["favorite"]]

    st.markdown("---")

    with st.expander("➕ Agregar nuevo título"):
        with st.form(f"add_item_form_{sec}", clear_on_submit=True):
            title = st.text_input("Título")
            link = st.text_input(info["link_label"])
            folder_choice = st.selectbox(
                "Carpeta/etiqueta", [f["name"] for f in folders], key=f"fchoice_{sec}"
            )
            favorite = st.checkbox("💗 Marcar como favorito")
            submitted = st.form_submit_button("Guardar")
            if submitted and title.strip():
                add_item(sec, title.strip(), link.strip(), folder_map[folder_choice], favorite)
                st.success(f"¡'{title}' agregado! 🎉")
                st.rerun()

    with st.expander("🎨 Crear nueva carpeta/etiqueta de color"):
        with st.form(f"add_folder_form_{sec}", clear_on_submit=True):
            fname = st.text_input("Nombre de la carpeta (ej: Yaoi, Manhwa, Físicos...)")
            fcolor = st.color_picker("Color", DEFAULT_COLORS[len(folders) % len(DEFAULT_COLORS)])
            fsub = st.form_submit_button("Crear carpeta")
            if fsub and fname.strip():
                add_folder(sec, fname.strip(), fcolor)
                st.success("Carpeta creada 🎨")
                st.rerun()

    st.markdown("---")

    if not items:
        st.info("Todavía no hay nada aquí. ¡Agrega tu primer título arriba! 🌸")
        return

    for it in items:
        score = average_score(it["id"])
        color = color_map.get(it["folder_id"], "#FFD6E8")
        heart = '<span class="fav-heart">💗</span>' if it["favorite"] else ""
        folder_name = next((f["name"] for f in folders if f["id"] == it["folder_id"]), "")

        c1, c2 = st.columns([5, 1])
        with c1:
            st.markdown(
                f"""
                <div class="book-card" style="border-left-color:{color};">
                    <span class="book-title">{it['title']}</span> {heart}
                    <span class="tag-chip" style="background:{color};">{folder_name}</span>
                    <br>
                    <span class="stars">{stars_html(score)}</span> ({score}/5)
                </div>
                """,
                unsafe_allow_html=True,
            )
        with c2:
            if st.button("Abrir 📖", key=f"open_{it['id']}", use_container_width=True):
                goto("detail", current_item=it["id"], current_section=sec)
            if st.button("💗", key=f"fav_{it['id']}", use_container_width=True):
                toggle_favorite(it["id"], it["favorite"])
                st.rerun()


# ============================================================
# PÁGINA: DETALLE (hilo tipo tweets de un libro)
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

    st.markdown(f"## {item['title']} {'💗' if item['favorite'] else ''}")
    if item["link"]:
        st.markdown(f"[{info['link_label']}]({item['link']})")
    st.markdown(f"### {stars_html(score)}  —  {score}/5 (promedio de {len(get_entries(item_id))} entradas)")

    st.markdown("---")
    st.markdown("### ✏️ Nueva entrada")
    with st.form("new_entry_form", clear_on_submit=True):
        text = st.text_area("¿Qué quieres anotar hoy? (comentario, avance, opinión...)")
        stars = st.slider("Puntuación de esta entrada", 1, 5, 5)
        image = st.file_uploader("Imagen (opcional)", type=["png", "jpg", "jpeg", "gif", "webp"])
        submit_entry = st.form_submit_button("Publicar 🌸")
        if submit_entry and text.strip():
            add_entry(item_id, text.strip(), image, stars)
            st.success("¡Entrada publicada!")
            st.rerun()

    st.markdown("---")
    st.markdown("### 🧵 Hilo")
    entries = get_entries(item_id)
    if not entries:
        st.info("Aún no hay entradas. ¡Escribe la primera arriba! ✨")
    for e in entries:
        st.markdown(
            f"""<div class="tweet-card">
                    <span class="tweet-date">{e['date']}</span><br>
                    <span class="stars">{"⭐"*e['stars']}{"☆"*(5-e['stars'])}</span><br>
                    <p>{e['text']}</p>
                </div>""",
            unsafe_allow_html=True,
        )
        if e["image_b64"]:
            st.image(base64.b64decode(e["image_b64"]), width=300)

    st.markdown("---")
    if st.button("⬅️ Volver a la lista"):
        goto("section", current_section=sec)


# ============================================================
# ROUTER
# ============================================================
page = st.session_state["page"]
if page == "home":
    page_home()
elif page == "section":
    page_section()
elif page == "detail":
    page_detail()
