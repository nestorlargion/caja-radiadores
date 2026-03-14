import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import pytz
import time
# --- Configuración de Zona Horaria (Córdoba) ---
zona_horaria = pytz.timezone('America/Argentina/Cordoba')
fecha_hoy_ar = datetime.now(zona_horaria).date()

# Seguridad: Si no pasó por el login, lo regresamos al archivo principal
if "conectado" not in st.session_state or not st.session_state["conectado"]:
    st.warning("Por favor, inicia sesión primero.")
    st.switch_page("app.py") # Nombre de tu archivo principal
    st.stop()

st.set_page_config(page_title="Caja Radiadores CBA", layout="centered")
st.title("🛠️ Sistema de Caja - Radiadores")

# Conexión con Google Sheets (el link lo pegamos en los secretos de Streamlit)
conn = st.connection("gsheets", type=GSheetsConnection)

# Leer datos actuales
df = conn.read(worksheet="movimientos",ttl=0)
#df['fecha'] = pd.to_datetime(df['fecha'], dayfirst=True, errors='coerce')

with st.form("registro_caja", clear_on_submit=True):
    st.subheader("Cargar Movimiento")
    fecha = st.date_input("Fecha", fecha_hoy_ar)
    codigo = st.text_input("Codigo Radiador")
    concepto = st.text_input("Concepto (Ej: Radiador Peugeot 208)")
    tipo = st.selectbox("Tipo", ["Ingreso", "Egreso"])
    medio = st.selectbox("Medio", ["Efectivo", "Transferencia", "Tarjeta", "Echeq"])
    monto = st.number_input("Monto ($)", min_value=0)
    
    if st.form_submit_button("Guardar"):
        # Preparar la nueva fila
        monto_final = monto if tipo == "Ingreso" else -monto
        nueva_fila = pd.DataFrame([{
            "Fecha": fecha.strftime('%d/%m/%Y'),
            "Codigo": codigo,
            "Concepto": concepto,
            "Tipo": tipo,
            "Medio": medio,
            "Monto": monto_final
        }])
        
        # Combinar y actualizar la planilla
        df_actualizado = pd.concat([df, nueva_fila], ignore_index=True)
        conn.update(data=df_actualizado)
        #st.success(f"¡Guardado en la nube!")
        st.toast("¡Guardado en la nube!", icon="☁️")
        time.sleep(3)
        #st.rerun()

if st.button("Salir"):
     st.session_state["conectado"] = False
     st.rerun()
