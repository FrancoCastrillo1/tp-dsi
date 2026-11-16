from datetime import datetime

from dominio.usuario import Usuario


class Sesion:

    def __init__(self, fechaHoraInicio: datetime, usuario: Usuario,
                 fechaHoraFin: datetime | None = None, id: int | None = None):
        self.id = id
        self.fechaHoraInicio = fechaHoraInicio
        self.fechaHoraFin = fechaHoraFin
        self.usuario = usuario

    def getUsuarioLogueado(self) -> Usuario:
        return self.usuario
