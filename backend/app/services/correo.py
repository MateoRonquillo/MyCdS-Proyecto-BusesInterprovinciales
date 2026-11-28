import os
import smtplib
import ssl
from email.message import EmailMessage


def correo_configurado():
    habilitado = os.getenv("SMTP_ENABLED", "true").strip().lower() in {"true", "1", "yes"}
    return habilitado and bool(os.getenv("SMTP_HOST") and remitente_smtp())


def remitente_smtp():
    return os.getenv("SMTP_FROM") or os.getenv("SMTP_USERNAME")


def enviar_correo(destino, asunto, cuerpo, adjuntos=()):
    mensaje = EmailMessage()
    mensaje["From"] = remitente_smtp()
    mensaje["To"] = destino
    mensaje["Subject"] = asunto
    mensaje.set_content(cuerpo)
    for nombre, contenido in adjuntos:
        mensaje.add_attachment(contenido, maintype="application", subtype="pdf", filename=nombre)
    seguridad = os.getenv("SMTP_SECURITY", "starttls")
    contexto = ssl.create_default_context()
    host = os.environ["SMTP_HOST"]
    puerto = int(os.getenv("SMTP_PORT") or (465 if seguridad == "ssl" else 587))
    if seguridad == "ssl":
        cliente = smtplib.SMTP_SSL(host, puerto, timeout=8, context=contexto)
    elif seguridad in {"starttls", "none"}:
        cliente = smtplib.SMTP(host, puerto, timeout=8)
    else:
        raise ValueError("SMTP_SECURITY inválido")
    with cliente:
        if seguridad == "starttls":
            cliente.starttls(context=contexto)
        usuario = os.getenv("SMTP_USERNAME")
        if usuario:
            clave = os.getenv("SMTP_PASSWORD", "")
            if host.lower() == "smtp.gmail.com":
                clave = "".join(clave.split())
            cliente.login(usuario, clave)
        cliente.send_message(mensaje)
