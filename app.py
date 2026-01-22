import streamlit as st
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# --- CONFIGURACIÓN DE CORREO ---
# Reemplaza con tus datos reales
MI_CORREO = "tu_correo@gmail.com"
MI_PASSWORD = "tu_password_de_aplicacion" # No es tu clave normal, es una 'App Password' de Google

def enviar_email(vendedor, fecha, datos_tabla, total_monto, total_diff):
    asunto = f"Reporte: {vendedor} - {fecha}"
    
    # Construcción del cuerpo del mensaje
    cuerpo = f"Detalles del Reporte de Cobranza:\n\n{datos_tabla.to_string(index=False)}\n\n"
    cuerpo += f"----------------------------------\n"
    cuerpo += f"TOTAL CANCELADO: ${total_monto:,.2f}\n"
    cuerpo += f"TOTAL DIFERENCIA: ${total_diff:,.2f}\n"
    cuerpo += f"----------------------------------\n"
    cuerpo += "Este reporte ha sido enviado y no puede ser modificado."

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
        st.error(f"Error al enviar: {e}")
        return False

# --- INTERFAZ DE LA APP ---
st.title("📲 Reporte de Cobranza Diario")

# 1. Encabezado
col1, col2 = st.columns(2)
vendedor = col1.selectbox("Cobrador", ["Vendedor 1", "Vendedor 2", "Vendedor 3"])
fecha = col2.date_input("Fecha del reporte")

st.write("### Ingrese los cobros (hasta 20 filas)")

# 2. Tabla tipo Excel (20 filas iniciales)
df_inicial = pd.DataFrame(
    [{"Cliente": "", "Factura": "", "Monto": 0.0, "Diferencia": 0.0} for _ in range(20)]
)

# El editor de datos permite escribir rápido como en Excel
tabla_datos = st.data_editor(df_inicial, use_container_width=True, hide_index=True)

# 3. Botón de Envío
if st.button("ENVIAR REPORTE AHORA"):
    # Filtramos solo las filas que tengan nombre de cliente
    datos_finales = [fila for fila in tabla_datos if fila['Cliente'].strip() != ""]
    
    if len(datos_finales) > 0:
        df_final = pd.DataFrame(datos_finales)
        total_monto = df_final["Monto"].sum()
        total_diff = df_final["Diferencia"].sum()
        
        exito = enviar_email(vendedor, fecha, df_final, total_monto, total_diff)
        
        if exito:
            st.success("✅ Reporte enviado con éxito. Ya no puede modificarlo.")
            st.balloons()
            # Bloquear la pantalla después de enviar
            st.info("Puede cerrar la aplicación o recargar para un nuevo reporte.")
    else:
        st.error("⚠️ Debe ingresar al menos un cobro antes de enviar.")
