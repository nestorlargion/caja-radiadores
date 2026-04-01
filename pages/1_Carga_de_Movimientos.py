import streamlit as st
from st_supabase_connection import SupabaseConnection
from datetime import datetime

# --- PORTERO AUTOMÁTICO ---
if "conectado" not in st.session_state or not st.session_state["conectado"]:
    st.switch_page("app.py")

# Conexión
conn = st.connection(
    "supabase",
    type=SupabaseConnection,
    url=st.secrets["connections"]["supabase"]["url"],
    key=st.secrets["connections"]["supabase"]["key"]
)

st.title("📝 Registro de Ventas y Gastos")
st.subheader("Carga de Movimiento Diario")

# Usamos el formulario sin columnas para que queden uno debajo del otro
with st.form("form_carga_vertical", clear_on_submit=True):
    
    fecha = st.date_input("📅 Fecha", datetime.now())
    codigo = st.text_input("🔢 Código del Producto (opcional)", placeholder="Ej: RAD-CORSA-123")
    concepto = st.text_input("📋 Concepto / Descripción", placeholder="Ej: Radiador Toyota Corolla XLI")
    monto = st.number_input("💰 Monto ($)", min_value=0.0, step=100.0, format="%.2f")
    tipo = st.selectbox("↕️ Tipo de Movimiento", ["Ingreso", "Egreso"])
    medio = st.selectbox("💳 Medio de Pago", ["Efectivo", "Transferencia", "Tarjeta", "Echeq", "CTE CTE", "Cheque"])
    
    st.write("---")
    btn_cargar = st.form_submit_button("🚀 Registrar en la Base de Datos", use_container_width=True)

    if btn_cargar:
        if concepto and monto > 0:
            nuevo_movimiento = {
                "fecha": str(fecha),
                "codigo": codigo, # Nuevo campo agregado
                "concepto": concepto,
                "monto": monto,
                "tipo": tipo,
                "medio": medio
            }
            try:
                conn.table("movimientos").insert(nuevo_movimiento).execute()
                st.success(f"✅ ¡{concepto} guardado correctamente!")
            except Exception as e:
                st.error(f"Error al guardar en la base de datos: {e}")
        else:
            st.warning("⚠️ El concepto y el monto son obligatorios.")

# Botón rápido para ir a ver lo cargado
if st.button("🔍 Ir a Consulta de Hoy"):
    st.switch_page("pages/2_Consulta_Cajas.py")

# --- SIDEBAR ---
with st.sidebar:

    # Usamos .get() con valores por defecto para evitar errores si la sesión se reinicia
    rol = st.session_state.get('rol', 'Sin Rol')
    nombre = st.session_state.get('nombre', 'Sin Nombre')

    # Mostramos el cuadro informativo
    st.info(f"Usuario: **{rol.capitalize()}**: **{nombre}**")
    if st.button("Cerrar Sesión"):
        st.session_state["conectado"] = False
        st.switch_page("app.py")        