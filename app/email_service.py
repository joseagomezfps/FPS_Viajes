import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

# Configuración del servidor de correo
SMTP_SERVER = os.getenv("SMTP_SERVER", "correo.fpsevillistas.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 465))
SMTP_USERNAME = os.getenv("SMTP_USERNAME", "fps_viajes@fpsevillistas.com")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "Fps@2026")
SENDER_EMAIL = os.getenv("SENDER_EMAIL", "FPS Viajes <fps_viajes@fpsevillistas.com>")

def send_email_notification(to_email: str, subject: str, html_body: str):
    """Envía un correo electrónico mediante conexión SSL directa (puerto 465)."""
    if not SMTP_USERNAME or not to_email:
        print("[EMAIL] Envío cancelado: falta usuario SMTP o destinatario.")
        return

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = SENDER_EMAIL
    msg["To"] = to_email

    part = MIMEText(html_body, "html", "utf-8")
    msg.attach(part)

    context = ssl.create_default_context()

    try:
        # Para el puerto 465 se emplea SMTP_SSL
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, context=context) as server:
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.sendmail(SMTP_USERNAME, to_email, msg.as_string())
        print(f"[EMAIL] Mensaje enviado correctamente a {to_email}")
    except Exception as e:
        print(f"[EMAIL ERROR] Fallo al enviar a {to_email}: {e}")

# Plantilla 1: Notificación al conductor de nueva reserva
def send_driver_new_booking_email(driver_email: str, driver_name: str, passenger_name: str, seats: int, origin: str, match_desc: str):
    subject = f"🚗 Nueva solicitud de plaza de {passenger_name} - FPS Viajes"
    html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: auto; padding: 20px; border: 1px solid #e2e5e9; border-radius: 8px;">
      <h2 style="color: #c4122d; margin-top: 0;">¡Hola, {driver_name}!</h2>
      <p>Has recibido una nueva solicitud de plaza para tu desplazamiento:</p>
      <div style="background-color: #f8f9fa; padding: 15px; border-radius: 6px; margin: 15px 0;">
        <p><strong>Pasajero:</strong> {passenger_name}</p>
        <p><strong>Plazas solicitadas:</strong> {seats}</p>
        <p><strong>Trayecto:</strong> {origin} ➔ {match_desc}</p>
      </div>
      <p>Accede a tu cuenta de <strong>FPS Viajes</strong> para aceptar o rechazar la solicitud.</p>
    </div>
    """
    send_email_notification(driver_email, subject, html)

# Plantilla 2: Notificación al pasajero (Aceptada o Rechazada)
def send_passenger_booking_status_email(passenger_email: str, passenger_name: str, driver_name: str, driver_phone: str, status: str, origin: str, match_desc: str):
    is_accepted = (status.lower() == "accepted")
    status_text = "ACEPTADA" if is_accepted else "RECHAZADA"
    color = "#28a745" if is_accepted else "#c4122d"
    subject = f"Estado de tu solicitud de viaje: {status_text} - FPS Viajes"

    contact_info = ""
    if is_accepted and driver_phone:
        contact_info = f"""
        <p>Puedes contactar con el conductor por WhatsApp o llamada para coordinar el viaje:</p>
        <p style="font-size: 16px;"><strong>📞 Teléfono:</strong> {driver_phone}</p>
        """

    html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: auto; padding: 20px; border: 1px solid #e2e5e9; border-radius: 8px;">
      <h2 style="color: {color}; margin-top: 0;">Solicitud {status_text}</h2>
      <p>Hola, {passenger_name}:</p>
      <p>El conductor <strong>{driver_name}</strong> ha <strong>{status_text.lower()}</strong> tu solicitud de plaza.</p>
      <div style="background-color: #f8f9fa; padding: 15px; border-radius: 6px; margin: 15px 0;">
        <p><strong>Ruta:</strong> {origin} ➔ {match_desc}</p>
        <p><strong>Estado:</strong> <span style="color: {color}; font-weight: bold;">{status_text}</span></p>
      </div>
      {contact_info}
      <p>¡Buen viaje con el Sevillismo!</p>
    </div>
    """
    send_email_notification(passenger_email, subject, html)