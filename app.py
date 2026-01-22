import streamlit as st
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# --- CONFIGURACIÓN ---
# Asegúrate de poner tus 16 letras amarillas aquí
MI_CORREO = "lgil32@gmail.com" 
MI_PASSWORD = "dlkn cnpz cera lphi" 

def enviar_email(vendedor, fecha, df_final, total_monto, total_diff, neto):
    asunto = f"Reporte: {vendedor} - {fecha}"
    
    tabla_texto = df_final.to_string(index=False)
    
    cuerpo = f"Nuevo Reporte de Cobranza:\n\n{tabla_texto}\n\n"
    cuerpo += f"----------------------------------\n"
    cuerpo += f"TOTAL CANCELADO:   ${total_monto:,.2f}\n"
    cuerpo += f"TOTAL DIFERENCIA:  ${total_diff:,.2f}\n"
    cuerpo += f"NETO A ENTREGAR:   ${neto:,.2f}\n" # <--- Agregado al correo
    cuerpo += f"----------------------------------\n"
    cuerpo += "Este reporte ha sido enviado y bloqueado contra modificaciones."

    msg = MIMEMultipart()
    msg['From'] = MI_CORREO
    msg['To'] = MI_CORREO
    msg['Subject'] = asunto
    msg.attach(MIMEText(cuerpo, 'plain'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(MI_CORREO.strip(), MI_PASSWORD.strip())
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        st.error(f"Error de envío: {e}")
        return False

# --- INTERFAZ ---
st.set_page_config(page_title="App Cobranza", layout="centered")
st.title("📲 Reporte de Cobranza")

vendedor = st.selectbox("Nombre del Cobrador", ["Vendedor 1", "Vendedor 2", "Vendedor 3"])
fecha = st.date_input("Fecha")

df_init = pd.DataFrame(
    {"Cliente": [""]*20, "Factura": [""]*20, "Monto": [0.0]*20, "Diferencia": [0.0]*20}
)

st.write("### Complete los cobros")
df_editado = st.data_editor(df_init, use_container_width=True, hide_index=True)

# Cálculos en tiempo real para que el vendedor vea el Neto antes de enviar
res_preview = pd.DataFrame(df_editado)
res_preview = res_preview[res_preview["Cliente"].str.strip() != ""]

if not res_preview.empty:
    monto_p = res_preview["Monto"].sum()
    diff_p = res_preview["Diferencia"].sum()
    neto_p = monto_p - diff_p
    st.info(f"**Resumen actual:** Total: ${monto_p:,.2f} | Dif: ${diff_p:,.2f} | **Neto: ${neto_p:,.2f}**")

if st.button("ENVIAR REPORTE FINAL"):
    res = pd.DataFrame(df_editado)
    res = res[res["Cliente"].str.strip() != ""]
    
    if not res.empty:
        total_monto = res["Monto"].sum()
        total_diff = res["Diferencia"].sum()
        neto_entregar = total_monto - total_diff # <--- Cálculo de la resta
        
        with st.spinner('Enviando al correo...'):
            if enviar_email(vendedor, str(fecha), res, total_monto, total_diff, neto_entregar):
                st.success(f"✅ ¡Enviado! Neto a entregar: ${neto_entregar:,.2f}")
                st.balloons()
                st.stop() 
    else:
        st.warning("⚠️ Escriba al menos un cliente.")
