from datetime import datetime

from dominio.empleado import Empleado
from dominio.estado import Estado


class CambioDeEstadoDocumentacion:

    def __init__(self, fechaHoraInicio: datetime, estado: Estado, responsable: Empleado | None,
                 fechaHoraFin: datetime | None = None, id: int | None = None):
        self.id = id
        self.fechaHoraInicio = fechaHoraInicio
        self.fechaHoraFin = fechaHoraFin
        self.estado = estado
        self.responsable = responsable

    def sosActual(self) -> bool:
        return self.fechaHoraFin is None

    def setFechaHoraFin(self, fechaHoraFin: datetime) -> None:
        self.fechaHoraFin = fechaHoraFin

    def getEstado(self) -> Estado:
        return self.estado

    def getResponsable(self) -> Empleado | None:
        return self.responsable
