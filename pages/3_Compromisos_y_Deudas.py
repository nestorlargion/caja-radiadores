import streamlit as st
from st_supabase_connection import SupabaseConnection
import pandas as pd
from datetime import datetime

# --- 1. PORTERO AUTOMÁTICO (SEGURIDAD) ---
if "conectado" not in st.session_state or not st.session_state["conectado"]:
    st.switch_page("app.py")

# Verificamos el rol guardado en el login (app.py)
rol = st.session_state.get('rol', 'user')

if rol != "administrador":
    st.error("No tienes permisos para acceder a esta sección.")
    st.info("Por favor, vuelve al inicio para cargar movimientos.")
    st.stop() # Esto detiene la ejecución del resto de la página

# --- 2. CONEXIÓN A SUPABASE ---
try:
    conn = st.connection(
        "supabase",
        type=SupabaseConnection,
        url=st.secrets["connections"]["supabase"]["url"],
        key=st.secrets["connections"]["supabase"]["key"]
    )
except Exception as e:
    st.error(f"Error de conexión: {e}")
    st.stop()

st.title("🗓️ Compromisos y Deudas")

# --- 3. OBTENER LISTA DE PROVEEDORES ---
try:
    res_p = conn.table("proveedores").select("nombre").order("nombre").execute()
    lista_proveedores = [p['nombre'] for p in res_p.data]
except Exception as e:
    st.error("No se pudo cargar la lista de proveedores.")
    lista_proveedores = []

# --- 4. SECCIÓN DE CARGA (DISEÑO VERTICAL) ---
with st.expander("➕ Registrar Nuevo Compromiso / ECHEQ", expanded=True):
    if not lista_proveedores:
        st.warning("⚠️ No hay proveedores registrados. Cargá uno primero en la página de Proveedores.")
    else:
        with st.form("form_compromiso_vertical", clear_on_submit=True):
            
            fecha_emision = st.date_input("📅 Fecha de Emisión (Compra/Emisión de Cheque)", datetime.now())
            
            vence = st.date_input("🚨 Fecha de Vencimiento / Cobro", datetime.now())
            
            prov_seleccionado = st.selectbox("👤 Seleccionar Proveedor", lista_proveedores)
            
            monto = st.number_input("💰 Monto ($)", min_value=0.0, step=1000.0, format="%.2f")
            
            tipo_deuda = st.selectbox("📝 Tipo de Compromiso", ["Cuenta Corriente", "ECHEQ", "Cheque Físico", "Otro"])
            
            estado_inicial = st.selectbox("📌 Estado Inicial", ["Pendiente", "Pagado"])
            
            obs = st.text_area("🗒️ Observaciones", placeholder="Nro de cheque, detalle de factura, etc.")
            
            st.write("---")
            btn_guardar = st.form_submit_button("💾 Guardar Compromiso", use_container_width=True)

            if btn_guardar:
                if monto > 0:
                    nuevo = {
                        "fecha": str(fecha_emision),
                        "fecha_vencimiento": str(vence),
                        "proveedor": prov_seleccionado,
                        "monto": monto,
                        "tipo": tipo_deuda,
                        "estado": estado_inicial,
                        "observaciones": obs
                    }
                    try:
                        conn.table("compromisos").insert(nuevo).execute()
                        st.success(f"✅ ¡Compromiso con {prov_seleccionado} guardado!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error al insertar: {e}")
                else:
                    st.warning("⚠️ El monto debe ser mayor a 0.")

st.write("---")

# --- 5. CONSULTA Y EDICIÓN ---
st.subheader("📊 Listado de Compromisos")

res_c = conn.table("compromisos").select("*").order("fecha_vencimiento").execute()
df_deudas = pd.DataFrame(res_c.data)

if df_deudas.empty:
    st.info("No hay compromisos cargados todavía.")
else:
    # Filtros rápidos
    c1, c2 = st.columns(2)
    with c1:
        ver_estado = st.multiselect("Filtrar Estado:", ["Pendiente", "Pagado"], default=["Pendiente"])
    with c2:
        ver_tipo = st.multiselect("Filtrar Tipo:", ["Cuenta Corriente", "ECHEQ", "Cheque Físico", "Otro"], 
                                  default=["Cuenta Corriente", "ECHEQ", "Cheque Físico", "Otro"])

    mask = df_deudas['estado'].isin(ver_estado) & df_deudas['tipo'].isin(ver_tipo)
    df_mostrar = df_deudas[mask].copy()

    total_pendiente = df_mostrar[df_mostrar["estado"] == "Pendiente"]["monto"].sum()
    st.metric("Deuda Pendiente (en pantalla)", f"$ {total_pendiente:,.2f}")

    # Tabla Editor
    df_para_editar = df_mostrar.copy()
    df_para_editar.insert(0, "Eliminar", False)

    df_editado = st.data_editor(
        df_para_editar,
        hide_index=True,
        num_rows="fixed",
        disabled=["id"],
        use_container_width=True,
        column_config={
            "Eliminar": st.column_config.CheckboxColumn("🗑️"),
            "fecha": st.column_config.DateColumn("Emisión", format="DD/MM/YYYY"),
            "fecha_vencimiento": st.column_config.DateColumn("Vencimiento", format="DD/MM/YYYY"),
            "proveedor": st.column_config.SelectboxColumn("Proveedor", options=lista_proveedores),
            "monto": st.column_config.NumberColumn("Monto", format="$ %.2f"),
            "estado": st.column_config.SelectboxColumn("Estado", options=["Pendiente", "Pagado"]),
            "tipo": st.column_config.SelectboxColumn("Tipo", options=["Cuenta Corriente", "ECHEQ", "Cheque Físico", "Otro"])
        }
    )

    if st.button("💾 Sincronizar Cambios", use_container_width=True):
        try:
            ids_borrar = df_editado[df_editado["Eliminar"] == True]["id"].tolist()
            if ids_borrar:
                conn.table("compromisos").delete().in_("id", ids_borrar).execute()

            filas_para_actualizar = df_editado[df_editado["Eliminar"] == False].drop(columns=["Eliminar"])
            if not filas_para_actualizar.empty:
                datos_upsert = filas_para_actualizar.to_dict(orient="records")
                for d in datos_upsert:
                    d['fecha'] = str(d['fecha'])
                    d['fecha_vencimiento'] = str(d['fecha_vencimiento'])
                conn.table("compromisos").upsert(datos_upsert).execute()
            
            st.success("¡Base de datos sincronizada!")
            st.rerun()
        except Exception as e:
            st.error(f"Error al guardar: {e}")

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