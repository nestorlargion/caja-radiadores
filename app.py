import streamlit as st
from st_supabase_connection import SupabaseConnection

# --- Configuración de Página (Debe ir al principio del script) ---
st.set_page_config(page_title="Login", page_icon="🔒", initial_sidebar_state="collapsed")

# 1. Conexión a Supabase
# Asegúrate de tener url y key en .streamlit/secrets.toml
conn = st.connection("supabase", type=SupabaseConnection)

def cargar_usuarios():
    try:
        # Consultamos la tabla 'usuarios' que creamos en Supabase
        # Seleccionamos solo las columnas necesarias para validar
        res = conn.query("usuario, password", table="usuarios", ttl=0).execute()
        
        if res.data:
            # Creamos el diccionario {usuario: password}
            credenciales = {str(row['usuario']): str(row['password']) for row in res.data}
            return credenciales
        return {}
    except Exception as e:
        st.error(f"❌ Error al conectar con Supabase: {e}")
        return {}

# --- Lógica de Login ---
def login():
    st.title("Sistemas Internos - Acceso")
    
    # Intentamos cargar usuarios de la DB
    credenciales = cargar_usuarios()

    if not credenciales:
        st.warning("No se pudo cargar la base de datos de usuarios.")
        return

    with st.form("formulario_login"):
        user_input = st.text_input("Nombre de Usuario")
        pass_input = st.text_input("Contraseña", type="password")
        boton_entrar = st.form_submit_button("Ingresar")

        if boton_entrar:
            # Validación de credenciales
            if user_input in credenciales and credenciales[user_input] == str(pass_input):
                st.session_state["conectado"] = True
                st.session_state["user"] = user_input
                st.success("¡Ingreso exitoso!")
                st.rerun()
            else:
                st.error("Usuario o contraseña incorrectos.")

# --- Cuerpo de la Aplicación ---
def app_principal():
    # Redirigir a la página de caja diaria tras el login exitoso
    st.switch_page("pages/caja_diaria.py")

# --- Control de Sesión ---
if "conectado" not in st.session_state:
    st.session_state["conectado"] = False

if st.session_state["conectado"]:
    app_principal()
else:
    login()