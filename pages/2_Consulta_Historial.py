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
    st.write("📝 **Para borrar:** Seleccioná la fila desde la izquierda y apretá 'Suprimir' (Delete).")

    editado = st.data_editor(
        df, 
        hide_index=True, 
        num_rows="fixed", # Bloquea el botón (+) para no agregar registros
        disabled=["id", "fecha"], # Bloquea edición de ID y Fecha
        use_container_width=True,
        key="editor_consulta",
        column_config={
            "id": st.column_config.TextColumn("ID"),
            "fecha": st.column_config.DateColumn("Fecha", format="DD/MM/YYYY"),
            "codigo": st.column_config.TextColumn("Código"), # Agregamos el código aquí también
            "monto": st.column_config.NumberColumn("Monto", format="$ %.2f"),
            "tipo": st.column_config.SelectboxColumn("Tipo", options=["Ingreso", "Egreso"]),
            "medio": st.column_config.SelectboxColumn("Medio", options=["Efectivo", "Transferencia", "Tarjeta", "Echeq"])
        }
    )

# --- LÓGICA DE GUARDADO (BORRADO + EDICIÓN) ---
if st.button("💾 Guardar Cambios"):
    try:
        # 1. Identificar filas borradas
        # Comparamos los IDs originales contra los que quedaron en el editor
        ids_originales = set(df["id"].tolist())
        ids_actuales = set(editado["id"].tolist())
        ids_a_eliminar = list(ids_originales - ids_actuales)

        # 2. Ejecutar borrado en Supabase
        if ids_a_eliminar:
            conn.table("movimientos").delete().in_("id", ids_a_eliminar).execute()
            st.warning(f"Se eliminaron {len(ids_a_eliminar)} registros.")

        # 3. Ejecutar actualización de los que quedaron (Upsert)
        datos_actualizar = editado.to_dict(orient="records")
        for d in datos_actualizar:
            d['fecha'] = str(d['fecha']) # Asegurar formato fecha para Supabase
        
        conn.table("movimientos").upsert(datos_actualizar).execute()
        
        st.success("¡Cambios guardados con éxito!")
        st.rerun()
        
    except Exception as e:
        st.error(f"Error al procesar los cambios: {e}")
else:
    st.info("Sin movimientos hoy.")

if st.sidebar.button("Cerrar Sesión"):
    st.session_state["conectado"] = False
    st.switch_page("app.py")