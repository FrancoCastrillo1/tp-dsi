from datetime import datetime

from dominio.documentacion import Documentacion
from dominio.empleado import Empleado
from dominio.estado import Estado


class DetalleRemito:

    def __init__(self, documentacion: Documentacion, areaCMCDestino: str | None = None, id: int | None = None):
        self.id = id
        self.areaCMCDestino = areaCMCDestino
        self.documentacion = documentacion

    def mostrarDatosDocumentacion(self) -> dict:
        datos = {"asunto": self.documentacion.getAsunto()}
        datos.update(self.documentacion.mostrarDatosDoc())
        return datos

    def esDeDocumentacion(self, numerosDocumentacion: set[int]) -> bool:
        return self.documentacion.getNumero() in numerosDocumentacion

    def aceptarDoc(self, fechaHora: datetime, estado: Estado, responsable: Empleado) -> None:
        self.documentacion.recibirBolsin(fechaHora, estado, responsable)

    def rechazarDoc(self, fechaHora: datetime, estado: Estado, responsable: Empleado) -> None:
        self.documentacion.rechazar(fechaHora, estado, responsable)

    def registrarNoRecepcionDoc(self, fechaHora: datetime, estado: Estado, responsable: Empleado) -> None:
        self.documentacion.registrarNoRecepcion(fechaHora, estado, responsable)
