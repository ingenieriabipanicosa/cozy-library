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
    page_title="Katsearose's Dreamscape",
    page_icon="🪷",
    layout="wide",
    initial_sidebar_state="expanded",
)

DB_PATH = "otaku_bitacora.db"

APP_TITLE = "𑣲⋆  Katsearose's Dreamscape ⋆˚꩜｡"
APP_DIVIDER = "────୨ৎ────"
APP_KAOMOJI_SUB = "⋆˚꩜｡𐔌՞ ܸ.ˬ.ܸ՞𐦯"

KAOMOJI_HAPPY = "(♡ˊ͈ ꒳ ˋ͈)"
KAOMOJI_SHY = "(˶˃𐃷˂˶)"
KAOMOJI_SURPRISED = "( ˶°ㅁ°) !!"

FAVORITES_LABEL = "🌷͙֒ FAVORITES ㅤㅤㅤㅤ⋆.˚"

SECTIONS = {
    "BL": {"label": "⋆.𐙚 ̊  BL  🪷", "emoji": "🪷", "link_label": "🔗 Enlace donde lo leo"},
    "BOOKS": {"label": "⋆.𐙚 ̊ BOOKS 📚", "emoji": "📚", "link_label": "🔗 Enlace donde lo leo"},
    "STUDY": {"label": "⋆.𐙚 ̊ STUDY 📖", "emoji": "📖", "link_label": "☁️ Enlace de Google Drive / Notion"},
}

DEFAULT_COLORS = ["#FFD6E8", "#FFC2D6", "#FBE4EF", "#F7A8C4", "#FADDE8", "#F6C6DA", "#FFE9F2"]

# ============================================================
# ESTILO "KAWAII" (CSS)
# ============================================================
def inject_css():
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Quicksand:wght@400;500;600;700&family=Poppins:wght@400;600;700&family=Caveat:wght@600;700&display=swap');

        html, body, [class*="css"]  {
            font-family: 'Quicksand', sans-serif;
        }

        /* ---------- Fondo general: blanco con tonos rosa ---------- */
        .stApp {
            background: #FFFFFF;
            background-image:
                radial-gradient(circle at 6% 8%, #FFF1F7 0%, rgba(255,255,255,0) 30%),
                radial-gradient(circle at 95% 12%, #FFF1F7 0%, rgba(255,255,255,0) 28%),
                radial-gradient(circle at 50% 100%, #FFF6FA 0%, rgba(255,255,255,0) 40%);
        }

        section[data-testid="stSidebar"] {
            background: #FFFAFC;
            border-right: 2px dashed #FBD3E4;
        }

        /* ---------- Encabezado / título decorativo ---------- */
        .app-title {
            font-family: 'Poppins', sans-serif;
            font-weight: 700;
            font-size: 40px;
            text-align: center;
            color: #E0699A;
            margin-bottom: 2px;
            letter-spacing: 0.5px;
        }
        .app-divider {
            text-align: center;
            color: #F3B6CE;
            font-size: 18px;
            letter-spacing: 3px;
            margin: 2px 0 4px 0;
        }
        .app-kaomoji {
            text-align: center;
            color: #E9A6C4;
            font-size: 15px;
            margin-bottom: 22px;
        }
        .home-sub {
            text-align: center;
            color: #C98BAE;
            margin-bottom: 30px;
            font-family: 'Caveat', cursive;
            font-size: 22px;
        }

        /* ---------- Tarjetas grandes de inicio (BL / BOOKS / STUDY) ---------- */
        .home-card {
            background: #FFFCFD;
            border-radius: 26px;
            padding: 38px 18px 30px 18px;
            text-align: center;
            box-shadow: 0 6px 18px rgba(247, 168, 196, 0.25);
            transition: transform 0.15s ease-in-out;
            border: 2px dashed #F8C7DC;
            position: relative;
        }
        .home-card:hover {
            transform: translateY(-6px) scale(1.02);
            border: 2px dashed #E0699A;
        }
        .home-card-icon {
            font-size: 52px;
            margin-bottom: 6px;
        }
        .home-card-label {
            font-family: 'Poppins', sans-serif;
            font-size: 19px;
            font-weight: 700;
            color: #C2185B;
            letter-spacing: 1px;
        }

        /* ---------- Cabeceras de sección con estilito 2D ---------- */
        .section-header {
            font-family: 'Poppins', sans-serif;
            font-weight: 700;
            font-size: 30px;
            color: #D6538A;
            border-bottom: 2px dotted #F6C7DC;
            padding-bottom: 8px;
            margin-bottom: 6px;
        }

        /* ---------- Tarjeta de item (libro) ---------- */
        .book-card {
            background: #FFFDFE;
            border-radius: 16px;
            padding: 14px 18px;
            margin-bottom: 10px;
            box-shadow: 0 2px 8px rgba(230, 150, 180, 0.12);
            border: 1.5px solid #FCE1EC;
            border-left: 7px solid #FFD6E8;
        }
        .book-title {
            font-weight: 700;
            font-size: 17px;
            color: #7A3B57;
        }
        .stars {
            color: #F2A6C4;
            font-size: 15px;
        }
        .fav-heart {
            color: #E0699A;
            font-size: 18px;
        }
        .tag-chip {
            display: inline-block;
            padding: 2px 10px;
            border-radius: 12px;
            font-size: 11px;
            color: #8A3F5C;
            font-weight: 700;
            border: 1px solid rgba(0,0,0,0.05);
        }

        /* ---------- Tweet-like entries (hilo) ---------- */
        .tweet-card {
            background: #FFFDFE;
            border-radius: 14px;
            padding: 14px 18px;
            margin-bottom: 12px;
            box-shadow: 0 2px 6px rgba(230, 150, 180, 0.10);
            border: 1px dashed #F6C7DC;
        }
        .tweet-date {
            color: #D79BB8;
            font-size: 11px;
            font-weight: 700;
            letter-spacing: 0.5px;
        }

        /* ---------- Botones ---------- */
        div.stButton > button {
            border-radius: 14px;
            font-weight: 600;
            border: 1.5px solid #F8C7DC;
            background: #FFF6FA;
            color: #C2185B;
        }
        div.stButton > button:hover {
            border: 1.5px solid #E0699A;
            background: #FFEAF3;
            color: #A8104C;
        }

        /* Inputs / selects con toque suave */
        .stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] {
            border-radius: 12px !important;
            border: 1.5px solid #FBD3E4 !important;
        }

        .kaomoji-empty {
            text-align: center;
            font-size: 22px;
            color: #E0A6C0;
            margin: 18px 0;
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
    st.markdown(
        """
        <div style="text-align:center; padding: 6px 0 2px 0;">
            <div style="font-family:'Caveat',cursive; font-size:26px; color:#E0699A; font-weight:700;">
                Katsearose's
            </div>
            <div style="font-family:'Poppins',sans-serif; font-size:15px; color:#C2185B; letter-spacing:2px;">
                DREAMSCAPE
            </div>
        </div>
        <div style="text-align:center; color:#F3B6CE; margin: 4px 0 14px 0;">────୨ৎ────</div>
        """,
        unsafe_allow_html=True,
    )
    if st.button("🏠  Home", use_container_width=True):
        goto("home")
    st.markdown("<div style='color:#F6C7DC; text-align:center;'>. . . . . . . . . . .</div>", unsafe_allow_html=True)
    for sec in SECTIONS:
        if st.button(SECTIONS[sec]["label"], use_container_width=True, key=f"nav_{sec}"):
            goto("section", current_section=sec)
    st.markdown("<div style='color:#F6C7DC; text-align:center;'>. . . . . . . . . . .</div>", unsafe_allow_html=True)
    if st.button(FAVORITES_LABEL, use_container_width=True):
        goto("favorites")
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
    st.markdown(f'<p class="app-title">{APP_TITLE}</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="app-divider">{APP_DIVIDER}</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="app-kaomoji">{APP_KAOMOJI_SUB}</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="home-sub">elige a dónde quieres entrar hoy {KAOMOJI_SHY}</p>', unsafe_allow_html=True)

    cols = st.columns(3)
    icons = {"BL": "🪷", "BOOKS": "📚", "STUDY": "📖"}
    pretty_names = {"BL": "BL", "BOOKS": "BOOKS", "STUDY": "STUDY"}
    for col, sec in zip(cols, SECTIONS):
        with col:
            st.markdown(
                f"""<div class="home-card">
                        <div class="home-card-icon">{icons[sec]}</div>
                        <div class="home-card-label">⋆.𐙚 ̊ {pretty_names[sec]}</div>
                    </div>""",
                unsafe_allow_html=True,
            )
            if st.button(f"Entrar a {sec}", key=f"enter_{sec}", use_container_width=True):
                goto("section", current_section=sec)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        f'<p style="text-align:center; color:#E0A6C0;">{FAVORITES_LABEL}</p>',
        unsafe_allow_html=True,
    )
    if st.button("💗 Ver mis favoritos", use_container_width=False):
        goto("favorites")


# ============================================================
# PÁGINA: FAVORITES (todos los favoritos de todas las secciones)
# ============================================================
def page_favorites():
    st.markdown(f'<p class="section-header">{FAVORITES_LABEL}</p>', unsafe_allow_html=True)
    any_fav = False
    for sec in SECTIONS:
        rows = [i for i in get_items(sec) if i["favorite"]]
        if not rows:
            continue
        any_fav = True
        st.markdown(f"#### {SECTIONS[sec]['label']}")
        folders = get_folders(sec)
        color_map = {f["id"]: f["color"] for f in folders}
        for it in rows:
            score = average_score(it["id"])
            color = color_map.get(it["folder_id"], "#FFD6E8")
            c1, c2 = st.columns([5, 1])
            with c1:
                st.markdown(
                    f"""<div class="book-card" style="border-left-color:{color};">
                            <span class="book-title">{it['title']}</span> <span class="fav-heart">💗</span><br>
                            <span class="stars">{stars_html(score)}</span> ({score}/5)
                        </div>""",
                    unsafe_allow_html=True,
                )
            with c2:
                if st.button("Abrir 📖", key=f"favopen_{sec}_{it['id']}", use_container_width=True):
                    goto("detail", current_item=it["id"], current_section=sec)
    if not any_fav:
        st.markdown(f'<p class="kaomoji-empty">{KAOMOJI_HAPPY}<br>Todavía no tienes favoritos ✨</p>', unsafe_allow_html=True)


# ============================================================
# PÁGINA: SECCIÓN (lista de libros/temas de una sección)
# ============================================================
def page_section():
    sec = st.session_state.get("current_section", "BL")
    info = SECTIONS[sec]
    st.markdown(f'<p class="section-header">{info["label"]}</p>', unsafe_allow_html=True)

    folders = get_folders(sec)
    folder_names = ["Todas"] + [f["name"] for f in folders]
    folder_map = {f["name"]: f["id"] for f in folders}
    color_map = {f["id"]: f["color"] for f in folders}

    col_a, col_b = st.columns([2, 1])
    with col_a:
        selected_folder_name = st.selectbox("📁 Filtrar por carpeta/etiqueta", folder_names)
    with col_b:
        show_only_fav = st.checkbox(FAVORITES_LABEL)

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
                st.success(f"¡'{title}' agregado! {KAOMOJI_HAPPY}")
                st.rerun()

    with st.expander("🎨 Crear nueva carpeta/etiqueta de color"):
        with st.form(f"add_folder_form_{sec}", clear_on_submit=True):
            fname = st.text_input("Nombre de la carpeta (ej: Yaoi, Manhwa, Físicos...)")
            fcolor = st.color_picker("Color", DEFAULT_COLORS[len(folders) % len(DEFAULT_COLORS)])
            fsub = st.form_submit_button("Crear carpeta")
            if fsub and fname.strip():
                add_folder(sec, fname.strip(), fcolor)
                st.success(f"Carpeta creada {KAOMOJI_SHY}")
                st.rerun()

    st.markdown("---")

    if not items:
        st.markdown(
            f'<p class="kaomoji-empty">{KAOMOJI_HAPPY}<br>Todavía no hay nada aquí. ¡Agrega tu primer título arriba!</p>',
            unsafe_allow_html=True,
        )
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

    st.markdown(f'<p class="section-header">{item["title"]} {"💗" if item["favorite"] else ""}</p>', unsafe_allow_html=True)
    if item["link"]:
        st.markdown(f"[{info['link_label']}]({item['link']})")
    st.markdown(f"### {stars_html(score)}  —  {score}/5 (promedio de {len(get_entries(item_id))} entradas)")

    st.markdown("---")
    st.markdown("### ✏️ Nueva entrada")
    with st.form("new_entry_form", clear_on_submit=True):
        text = st.text_area("¿Qué quieres anotar hoy? (comentario, avance, opinión...)")
        stars = st.slider("Puntuación de esta entrada", 1, 5, 5)
        image = st.file_uploader("Imagen (opcional)", type=["png", "jpg", "jpeg", "gif", "webp"])
        submit_entry = st.form_submit_button("Publicar 🪷")
        if submit_entry and text.strip():
            add_entry(item_id, text.strip(), image, stars)
            st.success(f"¡Entrada publicada! {KAOMOJI_SURPRISED}")
            st.rerun()

    st.markdown("---")
    st.markdown("### 🧵 Hilo")
    entries = get_entries(item_id)
    if not entries:
        st.markdown(
            f'<p class="kaomoji-empty">{KAOMOJI_HAPPY}<br>Aún no hay entradas. ¡Escribe la primera arriba!</p>',
            unsafe_allow_html=True,
        )
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
elif page == "favorites":
    page_favorites()
