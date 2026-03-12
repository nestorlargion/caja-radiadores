import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

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
df = conn.read(ttl=0) # ttl=0 para que no use caché y lea siempre lo último

with st.form("registro_caja"):
    st.subheader("Cargar Movimiento")
    fecha = st.date_input("Fecha", datetime.now())
    concepto = st.text_input("Concepto (Ej: Radiador Peugeot 208)")
    tipo = st.selectbox("Tipo", ["Ingreso", "Egreso"])
    medio = st.selectbox("Medio", ["Efectivo", "Transferencia", "Tarjeta", "Echeq"])
    monto = st.number_input("Monto ($)", min_value=0)
    
    if st.form_submit_button("Guardar"):
        # Preparar la nueva fila
        monto_final = monto if tipo == "Ingreso" else -monto
        nueva_fila = pd.DataFrame([{
            "Fecha": str(fecha),
            "Concepto": concepto,
            "Tipo": tipo,
            "Medio": medio,
            "Monto": monto_final
        }])
        
        # Combinar y actualizar la planilla
        df_actualizado = pd.concat([df, nueva_fila], ignore_index=True)
        conn.update(data=df_actualizado)
        st.success("¡Guardado en la nube!")
        st.rerun()

# --- RESUMEN ---
if not df.empty:
    st.divider()
    total = df["Monto"].sum()
    st.metric("Saldo Actual en Caja", f"$ {total:,.2f}")
    st.dataframe(df.tail(10), use_container_width=True)   # Muestra los últimos 10 movimientos

if st.button("Salir"):
     st.session_state["conectado"] = False
     st.rerun()
