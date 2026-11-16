from datetime import date, datetime

from dominio.cambio_de_estado_bolsin import CambioDeEstadoBolsin
from dominio.comision_medica import ComisionMedica
from dominio.empleado import Empleado
from dominio.estado import Estado
from dominio.remito import Remito
from iterador.iagregado import IAgregado
from iterador.iiterador import IIterador
from iterador.iterador_remito import IteradorRemito


class Bolsin(IAgregado):
    """Agregado concreto: crea el IteradorRemito para recorrer sus remitos."""

    def __init__(self, numeroBolsin: int, fecha: date, peso: float, numeroPrecinto: int | None,
                 comisionMedicaOrigen: ComisionMedica, comisionMedicaDestino: ComisionMedica,
                 cambiosEstado: list[CambioDeEstadoBolsin] | None = None,
                 remitos: list[Remito] | None = None, id: int | None = None):
        self.id = id
        self.numeroBolsin = numeroBolsin
        self.fecha = fecha
        self.peso = peso
        self.numeroPrecinto = numeroPrecinto
        self.comisionMedicaOrigen = comisionMedicaOrigen
        self.comisionMedicaDestino = comisionMedicaDestino
        self.cambiosEstado = list(cambiosEstado or [])
        self.remitos = list(remitos or [])

    # --- Getters ---
    def getNumeroBolsin(self) -> int:
        return self.numeroBolsin

    def getNumeroPrecinto(self) -> int | None:
        return self.numeroPrecinto

    def getCMOrigen(self) -> ComisionMedica:
        return self.comisionMedicaOrigen

    def getCMDestino(self) -> ComisionMedica:
        return self.comisionMedicaDestino

    # --- Filtros usados por IteradorBolsin ---
    def esTuCMOrigen(self, comisionMedica: ComisionMedica) -> bool:
        return self.comisionMedicaOrigen.getNombre() == comisionMedica.getNombre()

    def sosEnviado(self) -> bool:
        ceActual = self.obtenerCEActual()
        return ceActual is not None and ceActual.sosEnviado()

    def obtenerCEActual(self) -> CambioDeEstadoBolsin | None:
        for cambioEstado in self.cambiosEstado:
            if cambioEstado.sosActual():
                return cambioEstado
        return None

    def getEstadoActual(self) -> Estado | None:
        ceActual = self.obtenerCEActual()
        return ceActual.getEstado() if ceActual else None

    # --- Iterator ---
    def crearIterador(self, elementos: list) -> IIterador:
        return IteradorRemito(elementos)

    def obtenerInformacionRemito(self) -> list[dict]:
        """Para cada remito devuelve su número y los datos de su documentación."""
        informacion = []
        iterador = self.crearIterador(self.remitos)
        iterador.primero()
        while not iterador.haFinalizado():
            remito = iterador.elementoActual()
            informacion.append({
                "numero": remito.getNumero(),
                "estado": remito.getEstado().getNombre(),
                "documentacion": remito.mostrarDocumentacion(),
            })
            iterador.siguiente()
        return informacion

    # --- Recepción ---
    def recibirBolsin(self, fechaHora: datetime, responsable: Empleado, estadoBolsin: Estado,
                      numerosDocAfectados: set[int],
                      estadoDocAceptada: Estado, estadoDocAfectada: Estado | None,
                      estadoRemitoAceptado: Estado, estadoRemitoParcial: Estado) -> None:
        if not self.sosEnviado():
            raise ValueError(f"El bolsín {self.numeroBolsin} no está en estado '{Estado.ENVIADO}'.")

        self.crearNuevoCE(fechaHora, estadoBolsin, responsable)

        iterador = self.crearIterador(self.remitos)
        iterador.primero()
        while not iterador.haFinalizado():
            remito = iterador.elementoActual()
            remito.recibir(fechaHora, responsable, numerosDocAfectados,
                           estadoDocAceptada, estadoDocAfectada,
                           estadoRemitoAceptado, estadoRemitoParcial)
            iterador.siguiente()

    def crearNuevoCE(self, fechaHora: datetime, estado: Estado, responsable: Empleado) -> None:
        """Cierra el cambio de estado actual y crea el nuevo, registrando el empleado responsable."""
        ceActual = self.obtenerCEActual()
        if ceActual is not None:
            ceActual.setFechaHoraFin(fechaHora)
        self.cambiosEstado.append(CambioDeEstadoBolsin(fechaHora, estado, responsable))
