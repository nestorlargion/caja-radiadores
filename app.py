import streamlit as st
from st_supabase_connection import SupabaseConnection

# Configuración inicial
st.set_page_config(page_title="Login - Radiadores", page_icon="🔒")

# Conexión infalible a Supabase
try:
    conn = st.connection(
        "supabase",
        type=SupabaseConnection,
        url=st.secrets["connections"]["supabase"]["url"],
        key=st.secrets["connections"]["supabase"]["key"]
    )
except Exception as e:
    st.error("Error de configuración de base de datos.")
    st.stop()

# Redirección automática si ya inició sesión
if "conectado" in st.session_state and st.session_state["conectado"]:
    st.switch_page("pages/1_Carga_de_Movimientos.py")

def validar_usuario(u, p):
    try:
        res = conn.table("usuarios").select("*").eq("usuario", u).eq("password", p).execute()
        if len(res.data) > 0:
            return res.data[0] 
        return None
    except:
        return None

st.title("🚀 Sistema de Gestión")
st.subheader("Venta de Radiadores")

with st.form("login_form"):
    u = st.text_input("Usuario")
    p = st.text_input("Contraseña", type="password")
    if st.form_submit_button("Entrar"):
        usuario_info = validar_usuario(u, p)
        if usuario_info:
            st.session_state["conectado"] = True
            st.session_state['user'] = usuario_info['usuario']
            st.session_state['rol'] = usuario_info['rol']  # <--- AQUÍ SE GUARDA EL ROL
            st.session_state['nombre'] = usuario_info['nombre']
            st.success("¡Ingreso exitoso!")
            st.switch_page("pages/1_Carga_de_Movimientos.py")
        else:
            st.error("Credenciales incorrectas")