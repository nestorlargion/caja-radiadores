import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import pytz

# 1. Conexión y carga

conn = st.connection("gsheets", type=GSheetsConnection)

# Usamos ttl=0 para que no use datos viejos guardados en memoria
df = conn.read(worksheet="movimientos", ttl=0)

# --- PASO 1: LIMPIEZA DE COLUMNAS ---
# Esto elimina espacios invisibles y pasa todo a minúsculas para evitar errores
df.columns = [str(c).strip().lower() for c in df.columns]

# --- PASO 2: CONVERSIÓN FORZADA ---
# Intentamos convertir la columna que se llame 'fecha' (ahora en minúscula)
if 'fecha' in df.columns:
    # Convertimos y lo que no sea fecha lo transformamos en NaT (vacío)
    df['fecha_limpia'] = pd.to_datetime(df['fecha'], dayfirst=True, errors='coerce')
    
    # Eliminamos las filas que no tengan fecha válida
    df = df.dropna(subset=['fecha_limpia'])
else:
    st.error(f"No encontré la columna 'fecha'. Las columnas disponibles son: {list(df.columns)}")
    st.stop()

# --- PASO 3: SELECTOR Y FILTRO ---
dia_buscado = st.date_input("Seleccioná el día", value=datetime.now())

# Filtramos usando strings formateados (esto es infalible porque compara texto simple)
fecha_texto_buscada = dia_buscado.strftime('%Y-%m-%d')
df['fecha_texto_comparar'] = df['fecha_limpia'].dt.strftime('%Y-%m-%d')

df_filtrado = df[df['fecha_texto_comparar'] == fecha_texto_buscada]

# --- PASO 4: RESULTADOS Y DIAGNÓSTICO ---
st.divider()

if not df_filtrado.empty:
    st.success(f"¡Se encontraron {len(df_filtrado)} registros!")
    # Mostramos solo las columnas originales
    columnas_originales = [c for c in df.columns if c not in ['fecha_limpia', 'fecha_texto_comparar']]
    st.dataframe(df_filtrado[columnas_originales], use_container_width=True)
else:
    st.warning("No se encontró nada con el filtro.")
    
    with st.expander("🛠️ CLIC AQUÍ PARA VER POR QUÉ NO FILTRA"):
        st.write("1. Fecha que estás buscando (texto):", fecha_texto_buscada)
        st.write("2. Primeras 5 fechas encontradas en tu Excel (texto):")
        st.write(df['fecha_texto_comparar'].head().tolist())
        st.write("3. Todas las columnas detectadas:", list(df.columns))
        
        if df['fecha_texto_comparar'].empty:
            st.error("OJO: La columna 'fecha' en tu Excel parece estar vacía o con formatos irreconocibles.")