import streamlit as st
from st_supabase_connection import SupabaseConnection
import pandas as pd

if "conectado" not in st.session_state or not st.session_state["conectado"]:
    st.switch_page("app.py")

conn = st.connection("supabase", type=SupabaseConnection, url=st.secrets["connections"]["supabase"]["url"], key=st.secrets["connections"]["supabase"]["key"])

st.title("🏭 Gestión de Proveedores")

# CARGA DE NUEVO PROVEEDOR
with st.expander("➕ Registrar Nuevo Proveedor"):
    with st.form("nuevo_prov", clear_on_submit=True):
        nom = st.text_input("Nombre del Proveedor (Ej: Radiadores Córdoba)")
        tel = st.text_input("Teléfono / WhatsApp")
        cont = st.text_input("Persona de contacto")
        if st.form_submit_button("Guardar Proveedor"):
            if nom:
                conn.table("proveedores").insert({"nombre": nom, "telefono": tel, "contacto": cont}).execute()
                st.success("Proveedor guardado")
                st.rerun()

# LISTADO Y EDICIÓN
st.subheader("Lista de Proveedores Registrados")
res = conn.table("proveedores").select("*").order("nombre").execute()
df_p = pd.DataFrame(res.data)

if not df_p.empty:
    df_p.insert(0, "Eliminar", False)
    ed = st.data_editor(df_p, hide_index=True, disabled=["id"], use_container_width=True)
    
    if st.button("💾 Guardar Cambios en Proveedores"):
        ids_borrar = ed[ed["Eliminar"] == True]["id"].tolist()
        if ids_borrar: conn.table("proveedores").delete().in_("id", ids_borrar).execute()
        
        upsert_data = ed[ed["Eliminar"] == False].drop(columns=["Eliminar"]).to_dict(orient="records")
        conn.table("proveedores").upsert(upsert_data).execute()
        st.rerun()

# --- SIDEBAR ---
with st.sidebar:

    # Usamos .get() con valores por defecto para evitar errores si la sesión se reinicia
    rol = st.session_state.get('rol', 'Sin Rol')
    nombre = st.session_state.get('nombre', 'Sin Nombre')

    # Mostramos el cuadro informativo
    st.info(f"👤 **{rol.capitalize()}**: **{nombre}**")
    if st.button("Cerrar Sesión"):
        st.session_state["conectado"] = False
        st.switch_page("app.py")        