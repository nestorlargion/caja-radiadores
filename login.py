import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

def cargar_usuarios():
    try:
        # 🔑 AQUÍ ESTÁ EL CAMBIO: Especificamos sheet_name="usuarios"
# Conexión con Google Sheets (el link lo pegamos en los secretos de Streamlit)
        conn = st.connection("gsheets", type=GSheetsConnection)

# Leer datos actuales
        df = conn.read(worksheet="usuarios", ttl=0) # ttl=0 para que no use caché y lea siempre lo último        
        # Limpieza básica: eliminamos espacios en blanco accidentales en los nombres de columnas
        df.columns = df.columns.str.strip()
        
        # Creamos el diccionario para validar {usuario: password}
        # Usamos str() para asegurar que passwords numéricos no den error
        credenciales = {str(u): str(p) for u, p in zip(df['usuario'], df['password'])}
        
        return credenciales, df
    except Exception as e:
        st.error(f"❌ Error: No se encontró la hoja 'usuarios' o el archivo. Detalle: {e}")
        return {}, None

# --- Lógica de Login ---
def login():
    st.set_page_config(page_title="Login", page_icon="🔒")
    st.title("Sistemas Internos")
    
    credenciales, df_completo = cargar_usuarios()

    if not credenciales:
        st.warning("La base de datos de usuarios está vacía o no es accesible.")
        return

    with st.form("formulario_login"):
        user_input = st.text_input("Nombre de Usuario")
        pass_input = st.text_input("Contraseña", type="password")
        boton_entrar = st.form_submit_button("Ingresar")

        if boton_entrar:
            if user_input in credenciales and credenciales[user_input] == str(pass_input):
                st.session_state["conectado"] = True
                st.session_state["user"] = user_input
                st.rerun()
            else:
                st.error("Credenciales no válidas. Revisa mayúsculas/minúsculas.")

# --- Cuerpo de la Aplicación ---
def app_principal():
    st.title(f"Bienvenido/a, {st.session_state['user']}")
    st.info("Ahora puedes ver el contenido de las otras hojas o procesar datos.")
    
    if st.button("Salir"):
        st.session_state["conectado"] = False
        st.rerun()

# --- Control de Sesión ---
if "conectado" not in st.session_state:
    st.session_state["conectado"] = False

if st.session_state["conectado"]:
    app_principal()
else:
    login()