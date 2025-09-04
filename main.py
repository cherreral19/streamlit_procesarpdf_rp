import base64
import requests
import streamlit as st

st.set_page_config(page_title="Subir Documento", layout="wide")

# --- Config rápida ---
API_DEFAULT = st.secrets["ENDPOINT"]

# --- UI en dos columnas ---
col_left, col_right = st.columns([1, 4], gap="large")

def _safe_json(resp: requests.Response):
    try:
        return resp.json()
    except Exception:
        return {"raw_text": resp.text}

with col_left:
    st.markdown("### 📄 Cargar PDF")
    pdf_file = st.file_uploader("Selecciona un archivo PDF", type=["pdf"])
    enviar = st.button("📤 Procesar documento", use_container_width=True)

    if enviar:
        if not API_DEFAULT.strip():
            st.error("Configura la URL del endpoint en la barra lateral.")
        elif not pdf_file:
            st.warning("Primero selecciona un PDF.")
        else:
            # Leer y convertir a base64
            pdf_bytes = pdf_file.read()
            pdf_b64 = base64.b64encode(pdf_bytes).decode("utf-8")

            payload = {
                "filename": pdf_file.name,
                "file_b64": pdf_b64,
            }

            try:
                r = requests.post(API_DEFAULT, json=payload, timeout=200)
                st.session_state["resp_status"] = r.status_code
                st.session_state["resp_json"] = _safe_json(r)
            except Exception as e:
                st.session_state["resp_status"] = None
                st.session_state["resp_json"] = {"error": str(e)}

with col_right:
    st.markdown("### 🧾 Respuesta")
    status = st.session_state.get("resp_status")
    data = st.session_state.get("resp_json")

    if data is None:
        st.info("Aquí verás la respuesta cuando envíes un PDF.")
    else:
        # Mensaje breve arriba
        if isinstance(data, dict) and data.get("ok"):
            st.success(data.get("mensaje", "Operación exitosa"))
        elif isinstance(data, dict) and data.get("error"):
            st.error(data.get("error"))
