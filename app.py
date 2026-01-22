import streamlit as st
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# --- CONFIGURACIÓN DE CORREO ---
# RECUERDA: Usa tu 'App Password' de 16 letras de Google, no tu clave normal
MI_CORREO = "tu_correo@gmail.com" 
MI_PASSWORD = "tu_clave_de_16_letras" 

def enviar_email(vendedor, fecha, df_final, total_monto, total_diff):
    asunto = f"Reporte: {vendedor} - {fecha}"
    tabla_texto = df_final.to_string(index=False)
    
    cuerpo = f"Nuevo Reporte de Cobranza:\n\n{tabla_texto}\n\n"
    cuerpo += f"----------------------------------\n"
    cuerpo += f"TOTAL CANCELADO: ${total_monto:,.2f}\n"
    cuerpo += f"TOTAL DIFERENCIA: ${total_diff:,.2f}\n"
    cuerpo += f"----------------------------------\n"
    cuerpo += "Este reporte ha sido enviado y bloqueado."

    msg = MIMEMultipart()
    msg['From'] = MI_CORREO
    msg['To'] = MI_CORREO
    msg['Subject'] = asunto
    msg.attach(MIMEText(cuerpo, 'plain'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(MI_CORREO, MI_PASSWORD)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        st.error(f"Error al conectar con el correo: {e}")
        return False

# --- INTERFAZ ---
st.set_page_config(page_title="App Cobranza", layout="centered")
st.title("📲 Reporte de Cobranza")

# 1. Datos del encabezado
col1, col2 = st.columns(2)
vendedor = col1.selectbox("Nombre del Cobrador", ["Vendedor 1", "Vendedor 2", "Vendedor 3"])
fecha = col2.date_input("Fecha")

# 2. Tabla de 20 filas (Formato simplificado)
st.write("### Complete los cobros (hasta 20 filas)")
df_init = pd.DataFrame(
    {"Cliente": [""]*20, "Factura": [""]*20, "Monto": [0.0]*20, "Diferencia": [0.0]*20}
)

# Capturamos la edición
df_editado = st.data_editor(df_init, use_container_width=True, hide_index=True)

# 3. Lógica de Envío
if st.button("ENVIAR REPORTE FINAL"):
    # Convertimos a DataFrame real y filtramos filas vacías
    res = pd.DataFrame(df_editado)
    res = res[res["Cliente"].str.strip() != ""]
    
    if not res.empty:
        total_monto = res["Monto"].sum()
        total_diff = res["Diferencia"].sum()
        
        with st.spinner('Procesando envío...'):
            if enviar_email(vendedor, str(fecha), res, total_monto, total_diff):
                st.success("✅ ¡Enviado con éxito! El reporte ha sido bloqueado.")
                st.balloons()
                st.info("Para un nuevo reporte, recargue la página.")
                st.stop() # Detiene la app para cumplir tu regla de "no modificación"
    else:
        st.warning("⚠️ La tabla está vacía. Ingrese datos del cliente.")
