import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import pytz

# --- Configuración de Zona Horaria (Córdoba) ---
zona_horaria = pytz.timezone('America/Argentina/Cordoba')


# Seguridad: Si no pasó por el login, lo regresamos al archivo principal
if "conectado" not in st.session_state or not st.session_state["conectado"]:
    st.warning("Por favor, inicia sesión primero.")
    st.switch_page("app.py") # Nombre de tu archivo principal
    st.stop()

# Conexión con Google Sheets (el link lo pegamos en los secretos de Streamlit)
#conn = st.connection("gsheets", type=GSheetsConnection)

# Leer datos actuales
#df = conn.read(ttl=0) # ttl=0 para que no use caché y lea siempre lo último

def app_caja_diaria():
    st.set_page_config(page_title="Caja Radiadores CBA", layout="centered")
    st.title("💰 Caja Diaria - Movimientos")

    # 1. Cargar tus datos (esto vendría de tu Excel o Google Sheets)
    # Simulamos un DataFrame para el ejemplo
    # Asegúrate de que la columna 'fecha' sea de tipo datetime
    try:
        # Si usas st.connection para GSheets:
        conn = st.connection("gsheets", type=GSheetsConnection)
        df = conn.read(worksheet="movimientos",ttl=0)
        df.columns = [str(c).strip().lower() for c in df.columns]

        if 'fecha' in df.columns:
            # Convertimos y lo que no sea fecha lo transformamos en NaT (vacío)
            df['fecha_limpia'] = pd.to_datetime(df['fecha'], dayfirst=True, errors='coerce')
            
            # Eliminamos las filas que no tengan fecha válida
            df = df.dropna(subset=['fecha_limpia'])
        else:
            st.error(f"No encontré la columna 'fecha'. Las columnas disponibles son: {list(df.columns)}")
            st.stop()

    except:
        st.error("No se pudo cargar la hoja de movimientos.")
        return

    # 2. Selector de fecha (Por defecto: hoy)
    fecha_hoy = datetime.now(zona_horaria).date()
    
    st.subheader("Seleccionar Fecha")
    #fecha_seleccionada = st.date_input(
    #    "Ver movimientos del día:",
    #    value=fecha_hoy
    #    ,format="DD/MM/YYYY"
    #)
    fecha_seleccionada = st.date_input("Ver movimientos del día:",value=datetime.now())

    # Filtramos usando strings formateados (esto es infalible porque compara texto simple)
    fecha_texto_buscada = fecha_seleccionada.strftime('%Y-%m-%d')
    df['fecha_texto_comparar'] = df['fecha_limpia'].dt.strftime('%Y-%m-%d')

    df_filtrado = df[df['fecha_texto_comparar'] == fecha_texto_buscada]
    
    # 4. Mostrar resultados
    st.divider()
    if not df_filtrado.empty:
        st.write(f"### Movimientos del {fecha_seleccionada.strftime('%d/%m/%Y')}")
        
        # Mostrar tabla
        st.dataframe(df_filtrado, use_container_width=True)
 
        # Totales rápidos
        total_ingresos = df_filtrado[df_filtrado['Tipo'] == 'Ingreso']['Monto'].sum()
        total_egresos = df_filtrado[df_filtrado['Tipo'] == 'Egreso']['Monto'].sum()
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Ingresos", f"$ {total_ingresos:,.2f}")
        col2.metric("Egresos", f"$ {total_egresos:,.2f}")
        col3.metric("Saldo Día", f"$ {(total_ingresos - total_egresos):,.2f}")

    else:
        st.warning(f"No hay movimientos registrados para el día {fecha_seleccionada.strftime('%d/%m/%Y')}.")

if __name__ == "__main__":
    app_caja_diaria()

if st.button("Salir"):
     st.session_state["conectado"] = False
     st.rerun()
