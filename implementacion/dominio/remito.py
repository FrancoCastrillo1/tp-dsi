from datetime import date, datetime

from dominio.detalle_remito import DetalleRemito
from dominio.empleado import Empleado
from dominio.estado import Estado
from iterador.iagregado import IAgregado
from iterador.iiterador import IIterador
from iterador.iterador_detalle_remito import IteradorDetalleRemito


class Remito(IAgregado):
    """Agregado concreto: crea el IteradorDetalleRemito para recorrer sus detalles."""

    def __init__(self, numero: int, fecha: date, estado: Estado,
                 detalles: list[DetalleRemito] | None = None, id: int | None = None):
        self.id = id
        self.numero = numero
        self.fecha = fecha
        self.estado = estado
        self.detalles = list(detalles or [])

    def getNumero(self) -> int:
        return self.numero

    def getEstado(self) -> Estado:
        return self.estado

    def setEstado(self, estado: Estado) -> None:
        self.estado = estado

    def crearIterador(self, elementos: list) -> IIterador:
        return IteradorDetalleRemito(elementos)

    def mostrarDocumentacion(self) -> list[dict]:
        """Para cada documentación del remito devuelve su asunto y tipo (y datos auxiliares)."""
        datosDocumentacion = []
        iterador = self.crearIterador(self.detalles)
        iterador.primero()
        while not iterador.haFinalizado():
            detalle = iterador.elementoActual()
            datosDocumentacion.append(detalle.mostrarDatosDocumentacion())
            iterador.siguiente()
        return datosDocumentacion

    def recibir(self, fechaHora: datetime, responsable: Empleado,
                numerosDocAfectados: set[int],
                estadoDocAceptada: Estado, estadoDocAfectada: Estado | None,
                estadoRemitoAceptado: Estado, estadoRemitoParcial: Estado) -> None:
        """Registra la recepción de cada documentación del remito y actualiza el estado del remito.

        - La documentación no afectada se acepta.
        - La documentación afectada pasa a No recibida o a Recibida y Rechazada,
          según el estado recibido.
        - El remito queda Recibido y Aceptado Parcial si tiene al menos una documentación afectada.
        """
        tieneDocAfectada = False
        iterador = self.crearIterador(self.detalles)
        iterador.primero()
        while not iterador.haFinalizado():
            detalle = iterador.elementoActual()
            if estadoDocAfectada is not None and detalle.esDeDocumentacion(numerosDocAfectados):
                tieneDocAfectada = True
                if estadoDocAfectada.esNoRecibida():
                    detalle.registrarNoRecepcionDoc(fechaHora, estadoDocAfectada, responsable)
                elif estadoDocAfectada.esRecibidaYRechazada():
                    detalle.rechazarDoc(fechaHora, estadoDocAfectada, responsable)
                else:
                    raise ValueError(f"Estado no válido para documentación afectada: {estadoDocAfectada}")
            else:
                detalle.aceptarDoc(fechaHora, estadoDocAceptada, responsable)
            iterador.siguiente()

        self.setEstado(estadoRemitoParcial if tieneDocAfectada else estadoRemitoAceptado)
