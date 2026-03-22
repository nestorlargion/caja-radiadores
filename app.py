import streamlit as st
from st_supabase_connection import SupabaseConnection

# 1. Forzamos los datos (Copiá tus datos reales de Supabase aquí mismo para probar)
# Una vez que funcione, los volvemos a pasar a los secretos.
URL_PROYECTO = "https://resbthzvttorxktyeopx.supabase.co"
KEY_PROYECTO = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJlc2J0aHp2dHRvcnhrdHllb3B4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzQxNzUwMzUsImV4cCI6MjA4OTc1MTAzNX0.YhXag2IHDVaRw5UrT1FgI136_WruASSZis14RGCtp18"

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