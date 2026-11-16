"""Interfaz con el Servidor de Correo (actor secundario del CU 29 - Notificar recepción de bolsín).

Es un stub: no envía e-mails reales, sólo registra en el log el mensaje que se enviaría.
"""
import logging

logger = logging.getLogger("bolsines.correo")


class InterfazServidorCorreo:

    def __init__(self):
        self.mensajesEnviados: list[dict] = []

    def enviarNotificacion(self, destinatario: str, asunto: str, cuerpo: str) -> None:
        mensaje = {"destinatario": destinatario, "asunto": asunto, "cuerpo": cuerpo}
        self.mensajesEnviados.append(mensaje)
        logger.info("[STUB CORREO] Para: %s | Asunto: %s\n%s", destinatario, asunto, cuerpo)
