import streamlit as st
from st_supabase_connection import SupabaseConnection
import pandas as pd

# --- 1. PORTERO AUTOMÁTICO (SEGURIDAD) ---
if "conectado" not in st.session_state or not st.session_state["conectado"]:
    st.switch_page("app.py")

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

st.title("🔍 Consulta y Cierre de Caja")

# --- 3. FILTRO POR FECHA ---
fecha_busqueda = st.date_input("Seleccioná el día a consultar:", pd.to_datetime("today"))

# Función para traer datos frescos
def obtener_datos(f):
    res = conn.table("movimientos").select("*").eq("fecha", str(f)).execute()
    return pd.DataFrame(res.data)

df_dia = obtener_datos(fecha_busqueda)

if df_dia.empty:
    st.info(f"No hay movimientos registrados para el día {fecha_busqueda.strftime('%d/%m/%Y')}.")
else:
    # --- 4. SECCIÓN DE TOTALES ---
    st.subheader(f"💰 Totales del día")
    
    df_dia['monto'] = pd.to_numeric(df_dia['monto'])
    ingresos = df_dia[df_dia['tipo'] == 'Ingreso']['monto'].sum()
    egresos = df_dia[df_dia['tipo'] == 'Egreso']['monto'].sum()
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Ingresos", f"$ {ingresos:,.2f}")
    c2.metric("Egresos", f"$ {egresos:,.2f}", delta_color="inverse")
    c3.metric("Saldo Neto", f"$ {ingresos - egresos:,.2f}")

    # Totales por Medio de Pago
    st.write("**Detalle por Medio de Pago (Neto):**")
    # Agrupamos y restamos egresos de ingresos por cada medio
    resumen_medios = df_dia.groupby('medio').apply(
        lambda x: x[x['tipo'] == 'Ingreso']['monto'].sum() - x[x['tipo'] == 'Egreso']['monto'].sum()
    )
    
    cols = st.columns(len(resumen_medios))
    for i, (medio, total) in enumerate(resumen_medios.items()):
        cols[i].info(f"**{medio}**\n\n$ {total:,.2f}")

    st.write("---")

    # --- 5. TABLA DE EDICIÓN Y BORRADO ---
    st.write("📝 **Editar o marcar para eliminar:**")
    
    # Preparamos el DF con la columna de borrar
    df_para_editar = df_dia.copy()
    df_para_editar.insert(0, "Eliminar", False)

    df_editado = st.data_editor(
        df_para_editar,
        hide_index=True,
        num_rows="fixed", # Bloquea agregar filas nuevas
        disabled=["id", "fecha"], # Bloquea cambios en ID y Fecha
        use_container_width=True,
        column_config={
            "Eliminar": st.column_config.CheckboxColumn("🗑️", help="Tildá para borrar esta fila"),
            "id": st.column_config.TextColumn("ID"),
            "fecha": st.column_config.DateColumn("Fecha", format="DD/MM/YYYY"),
            "codigo": st.column_config.TextColumn("Código"),
            "monto": st.column_config.NumberColumn("Monto", format="$ %.2f"),
            "tipo": st.column_config.SelectboxColumn("Tipo", options=["Ingreso", "Egreso"]),
            "medio": st.column_config.SelectboxColumn("Medio", options=["Efectivo", "Transferencia", "Tarjeta", "Echeq"])
        }
    )

    # --- 6. BOTÓN DE GUARDADO ---
    if st.button("💾 Guardar Cambios", use_container_width=True):
        try:
            # Separamos los que se van de los que se quedan
            ids_a_borrar = df_editado[df_editado["Eliminar"] == True]["id"].tolist()
            filas_a_guardar = df_editado[df_editado["Eliminar"] == False].drop(columns=["Eliminar"])

            # A. Borramos en Supabase (solo si hay IDs seleccionados)
            if ids_a_borrar:
                conn.table("movimientos").delete().in_("id", ids_a_borrar).execute()
                st.toast(f"Eliminados {len(ids_a_borrar)} registros", icon="🗑️")
            
            # B. Actualizamos (Upsert) - SOLO SI HAY FILAS
            if not filas_a_guardar.empty:
                datos_upsert = filas_a_guardar.to_dict(orient="records")
                for d in datos_upsert:
                    d['fecha'] = str(d['fecha']) # Formato texto para DB
                
                # Aquí es donde antes fallaba si la lista iba vacía
                conn.table("movimientos").upsert(datos_upsert).execute()
            
            st.success("¡Base de datos sincronizada!")
            st.rerun()
            
        except Exception as e:
            # Si el error persiste, mostramos algo más claro
            st.error(f"Error técnico: {e}")

# --- SIDEBAR ---
with st.sidebar:
    st.info(f"Usuario: **{st.session_state.get('user', 'Admin')}**")
    if st.button("Cerrar Sesión"):
        st.session_state["conectado"] = False
        st.switch_page("app.py")