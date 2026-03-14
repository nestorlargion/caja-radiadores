import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pytz

# --- Configuración de Zona Horaria (Córdoba) ---
zona_horaria = pytz.timezone('America/Argentina/Cordoba')


# Seguridad: Si no pasó por el login, lo regresamos al archivo principal
if "conectado" not in st.session_state or not st.session_state["conectado"]:
    st.warning("Por favor, inicia sesión primero.")
    st.switch_page("app.py") # Nombre de tu archivo principal
    st.stop()

# 1. Configuración de la conexión
conn = st.connection("gsheets", type=GSheetsConnection)

# 2. Lectura de datos (ttl=0 para evitar datos viejos en caché)
df_original = conn.read(worksheet="movimientos", ttl=0)

st.title("Control de Movimientos")
st.subheader("Edición de Conceptos y Montos")

st.info("""
**Instrucciones:**
- Las columnas **Fecha** y **Código Radiador** están bloqueadas (solo lectura).
- Puedes editar el **Concepto** y **TipoMontoMedio**.
- Para **borrar** un registro: haz clic en el número de fila a la izquierda y presiona 'Suprimir' en tu teclado.
""")

# 3. Editor de datos con columnas deshabilitadas
df_editado = st.data_editor(
    df_original, 
    num_rows="fixed", # Bloquea la opción de añadir nuevas filas
    use_container_width=True,
    disabled=["Fecha", "Codigo"], # Bloquea la edición de estas columnas
    column_config={
        "Fecha": st.column_config.DateColumn("Fecha"),
        "Codigo": st.column_config.TextColumn("Código Radiador"),
        "TipoMontoMedio": st.column_config.SelectboxColumn(
            "Tipo Monto", 
            options=["Efectivo", "Transferencia", "Tarjeta", "Otros"]
        )
    }
)

# 4. Botón para sincronizar con Google Sheets
if st.button("Guardar Cambios Permanentemente"):
    try:
        conn.update(worksheet="movimientos", data=df_editado)
        st.success("¡La hoja de Google Sheets ha sido actualizada!")
        # Forzamos un rerun para limpiar cualquier estado residual del editor
        st.rerun()
    except Exception as e:
        st.error(f"Hubo un error al intentar guardar: {e}")