import streamlit as st

# Configuración de la página (estilo amplio)
st.set_page_config(page_title="Mi Bitácora Aesthetic", layout="wide")

# Título de bienvenida
st.markdown("<h1 style='text-align: center; color: #FF69B4;'>✨ Mi Bitácora Mágica ✨</h1>", unsafe_allow_html=True)

# Crear 3 columnas para los botones de inicio
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🌸 BL"):
        st.session_state.pagina = "BL"
        st.rerun()

with col2:
    if st.button("📚 BOOKS"):
        st.session_state.pagina = "BOOKS"
        st.rerun()

with col3:
    if st.button("📝 STUDY"):
        st.session_state.pagina = "STUDY"
        st.rerun()

# Lógica para cambiar de pantalla
if 'pagina' not in st.session_state:
    st.session_state.pagina = "HOME"

if st.session_state.pagina == "BL":
    st.write("### 💖 Sección de BL")
    st.write("Aquí irán tus listas de lectura...")
