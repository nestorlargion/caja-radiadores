import streamlit as st
from st_supabase_connection import SupabaseConnection
import pandas as pd

# --- PORTERO AUTOMÁTICO ---
if "conectado" not in st.session_state or not st.session_state["conectado"]:
    st.switch_page("app.py")

conn = st.connection(
    "supabase",
    type=SupabaseConnection,
    url=st.secrets["connections"]["supabase"]["url"],
    key=st.secrets["connections"]["supabase"]["key"]
)

st.title("🔍 Consulta y Totales")

f_busqueda = st.date_input("Fecha a consultar:", pd.to_datetime("today"))
res = conn.table("movimientos").select("*").eq("fecha", str(f_busqueda)).execute()
df = pd.DataFrame(res.data)

if not df.empty:
    # Totales
    df['monto'] = pd.to_numeric(df['monto'])
    ing = df[df['tipo'] == 'Ingreso']['monto'].sum()
    egr = df[df['tipo'] == 'Egreso']['monto'].sum()
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Ingresos", f"$ {ing:,.2f}")
    c2.metric("Egresos", f"$ {egr:,.2f}")
    c3.metric("Saldo", f"$ {ing - egr:,.2f}")

    # Totales por Medio
    st.write("**Por medio de pago:**")
    resumen = df.groupby('medio').apply(lambda x: x[x['tipo']=='Ingreso']['monto'].sum() - x[x['tipo']=='Egreso']['monto'].sum())
    st.dataframe(resumen, use_container_width=True)

    # Edición
    st.write("---")
    editado = st.data_editor(df, hide_index=True, num_rows="dynamic", disabled=["id"], use_container_width=True)

    if st.button("💾 Guardar Cambios"):
        ids_a_borrar = list(set(df["id"]) - set(editado["id"].dropna()))
        if ids_a_borrar: conn.table("movimientos").delete().in_("id", ids_a_borrar).execute()
        
        datos = editado.to_dict(orient="records")
        for d in datos:
            if pd.isna(d['id']): del d['id']
            d['fecha'] = str(d['fecha'])
        
        conn.table("movimientos").upsert(datos).execute()
        st.success("Actualizado")
        st.rerun()
else:
    st.info("Sin movimientos hoy.")

if st.sidebar.button("Cerrar Sesión"):
    st.session_state["conectado"] = False
    st.switch_page("app.py")