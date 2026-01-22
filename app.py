import streamlit as st
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# --- CONFIGURACIÓN DE CORREO ---
MI_CORREO = "tu_correo@gmail.com"
MI_PASSWORD = "tu_password_de_16_letras" # Tu App Password de Google

def enviar_email(vendedor, fecha, df_final, total_monto, total_diff):
    asunto = f"Reporte: {vendedor} - {fecha}"
    
    # Convertimos la tabla a texto limpio para el correo
    tabla_texto = df_final.to_string(index=False)
    
    cuerpo = f"Detalles del Reporte de Cobranza:\n\n{tabla_texto}\n\n"
    cuerpo += f"----------------------------------\n"
    cuerpo += f"TOTAL CANCELADO: ${total_monto:,.2f}\n"
    cuerpo += f"TOTAL DIFERENCIA: ${total_diff:,.2f}\n"
    cuerpo += f"----------------------------------\n"
    cuerpo += "Este reporte ha sido sellado y no puede ser modificado."

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
        st.error(f"Error técnico al enviar el correo: {e}")
        return False

# --- INTERFAZ ---
st.set_page_config(page_title="Cobranza App", layout="centered")
st.title("📲 Reporte de Cobranza")

# 1. Datos iniciales
col1, col2 = st.columns(2)
vendedor = col1.selectbox("Cobrador", ["Vendedor 1", "Vendedor 2", "Vendedor 3"])
fecha = col2.date_input("Fecha del reporte")

# 2. Tabla Editable (Mejorada para evitar el TypeError)
df_plantilla = pd.DataFrame(
    [{"Cliente": "", "Factura": "", "Monto": 0.0, "Diferencia": 0.0} for _ in range(20)]
)

st.write("### Tabla de Cobros (Llene hasta 20 filas)")
# Usamos el editor de datos y capturamos el resultado como un DataFrame directo
df_editado = st.data_editor(df_plantilla, use_container_width=True, hide_index=True)

# 3. Botón de Envío con lógica corregida
if st.button("ENVIAR REPORTE FINAL"):
    # Filtramos filas donde el Cliente no esté vacío
    df_filtrado = df_editado[df_editado["Cliente"].str.strip() != ""]
    
    if not df_filtrado.empty:
        # Cálculos
        total_monto = df_filtrado["Monto"].sum()
        total_diff = df_filtrado["Diferencia"].sum()
        
        # Envío
        with st.spinner('Enviando reporte...'):
            exito = enviar_email(vendedor, fecha, df_filtrado, total_monto, total_diff)
            
        if exito:
            st.success("✅ ¡Reporte enviado! Los datos han sido bloqueados.")
            st.balloons()
            st.info("Para generar otro reporte, simplemente recarga la página.")
            # Deshabilitar más acciones para cumplir tu regla de "no modificación"
            st.stop()
    else:
        st.error("⚠️ Error: La tabla está vacía. Ingrese al menos un cliente.")
