import streamlit as st
from st_supabase_connection import SupabaseConnection
from datetime import datetime

# --- PORTERO AUTOMÁTICO ---
if "conectado" not in st.session_state or not st.session_state["conectado"]:
    st.switch_page("app.py")

conn = st.connection(
    "supabase",
    type=SupabaseConnection,
    url=st.secrets["connections"]["supabase"]["url"],
    key=st.secrets["connections"]["supabase"]["key"]
)

st.title("📝 Carga de Movimientos")

with st.form("form_carga", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        fecha = st.date_input("Fecha", datetime.now())
        tipo = st.selectbox("Tipo", ["Ingreso", "Egreso"])
    with col2:
        monto = st.number_input("Monto ($)", min_value=0.0, step=500.0)
        medio = st.selectbox("Medio", ["Efectivo", "Transferencia", "Tarjeta", "Echeq"])
    
    concepto = st.text_input("Concepto (ej: Radiador Hilux 2023)")
    
    if st.form_submit_button("Registrar"):
        if concepto and monto > 0:
            nuevo = {"fecha": str(fecha), "concepto": concepto, "monto": monto, "tipo": tipo, "medio": medio}
            conn.table("movimientos").insert(nuevo).execute()
            st.success("¡Registrado!")
        else:
            st.warning("Completá los datos.")