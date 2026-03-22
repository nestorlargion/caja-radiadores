import streamlit as st
from st_supabase_connection import SupabaseConnection

# 1. Forzamos los datos (Copiá tus datos reales de Supabase aquí mismo para probar)
# Una vez que funcione, los volvemos a pasar a los secretos.
URL_PROYECTO = "https://resbthzvttorxktyeopx.supabase.co"
KEY_PROYECTO = "PEGÁ_ACÁ_TU_ANON_KEY_QUE_SACASTE_DE_SUPABASE"

# 2. Creamos la conexión pasando los parámetros manuales
try:
    conn = st.connection(
        "supabase",
        type=SupabaseConnection,
        url=URL_PROYECTO,
        key=KEY_PROYECTO
    )
    st.success("¡Conexión establecida manualmente!")
except Exception as e:
    st.error(f"Error crítico de conexión: {e}")

# 3. Prueba rápida: Intentar leer la tabla usuarios
if st.button("Probar lectura de Usuarios"):
    try:
        res = conn.table("usuarios").select("*").limit(1).execute()
        st.write("Datos recibidos:", res.data)
    except Exception as e:
        st.error(f"La conexión se hizo pero falló la lectura: {e}")


import streamlit as st
from st_supabase_connection import SupabaseConnection

# 1. Configuración de página
st.set_page_config(page_title="Login Radiadores", page_icon="🔒", initial_sidebar_state="collapsed")

# 2. Conexión (Usa los secretos que ya detectó)
conn = st.connection("supabase", type=SupabaseConnection)

def validar_usuario(user, password):
    try:
        # Buscamos el usuario en la tabla de Supabase
        res = conn.table("usuarios").select("*").eq("usuario", user).eq("password", password).execute()
        
        # Si devuelve datos, es que el usuario y contraseña coinciden
        return len(res.data) > 0
    except Exception as e:
        st.error(f"Error al consultar la base de datos: {e}")
        return False

# --- Interfaz de Login ---
if "conectado" not in st.session_state:
    st.session_state["conectado"] = False

if not st.session_state["conectado"]:
    st.title("Sistema de Caja Diaria")
    st.subheader("Control de Ventas de Radiadores")
    
    with st.form("login_form"):
        u = st.text_input("Usuario")
        p = st.text_input("Contraseña", type="password")
        btn = st.form_submit_button("Entrar")
        
        if btn:
            if validar_usuario(u, p):
                st.session_state["conectado"] = True
                st.session_state["user"] = u
                st.success("¡Bienvenido!")
                st.rerun()
            else:
                st.error("Usuario o contraseña incorrectos")
else:
    # Si ya está conectado, lo mandamos a la página de la caja
    st.write(f"Conectado como: **{st.session_state['user']}**")
    if st.button("Ir a Caja Diaria"):
        st.switch_page("pages/caja_diaria.py")
    
    if st.button("Cerrar Sesión"):
        st.session_state["conectado"] = False
        st.rerun()        