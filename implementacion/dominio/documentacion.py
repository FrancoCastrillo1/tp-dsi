from datetime import date, datetime

from dominio.cambio_de_estado_documentacion import CambioDeEstadoDocumentacion
from dominio.comision_medica import ComisionMedica
from dominio.empleado import Empleado
from dominio.estado import Estado
from dominio.tipo_documentacion import TipoDocumentacion


class Documentacion:
    """Documentación enviada en un remito.

    Transiciones del CU 28 según la máquina de estados de Documentacion
    (todas parten de "En bolsín enviado"):
      - aceptar()               -> Recibida y Aceptada
      - rechazar()              -> Recibida y Rechazada
      - registrarNoRecepcion()  -> No recibida
    """

    def __init__(self, numero: int, asunto: str, fechaPase: date,
                 tipoDocumentacion: TipoDocumentacion, comisionMedicaOrigen: ComisionMedica,
                 cambiosEstado: list[CambioDeEstadoDocumentacion] | None = None, id: int | None = None):
        self.id = id
        self.numero = numero
        self.asunto = asunto
        self.fechaPase = fechaPase
        self.tipoDocumentacion = tipoDocumentacion
        self.comisionMedicaOrigen = comisionMedicaOrigen
        self.cambiosEstado = list(cambiosEstado or [])

    def getNumero(self) -> int:
        return self.numero

    def getAsunto(self) -> str:
        return self.asunto

    def mostrarDatosDoc(self) -> dict:
        """Devuelve los datos de la documentación que no son el asunto (tipo, estado, CM origen)."""
        estadoActual = self.getEstadoActual()
        return {
            "numero": self.getNumero(),
            "tipo": self.tipoDocumentacion.getNombre(),
            "estado": estadoActual.getNombre() if estadoActual else None,
            "cmOrigen": self.comisionMedicaOrigen.getNombre(),
            "emailCMOrigen": self.comisionMedicaOrigen.getEmail(),
        }

    # --- Estado actual ---
    def obtenerCEActual(self) -> CambioDeEstadoDocumentacion | None:
        for cambioEstado in self.cambiosEstado:
            if cambioEstado.sosActual():
                return cambioEstado
        return None

    def getEstadoActual(self) -> Estado | None:
        ceActual = self.obtenerCEActual()
        return ceActual.getEstado() if ceActual else None

    # --- Transiciones del CU 28 ---
    def recibirBolsin(self, fechaHora: datetime, estado: Estado, responsable: Empleado) -> None:
        """La documentación llegó y corresponde al destino: se acepta."""
        self.__aceptar(fechaHora, estado, responsable)

    def rechazar(self, fechaHora: datetime, estado: Estado, responsable: Empleado) -> None:
        self.__validarEnBolsinEnviado()
        self.crearCEDocumentacion(fechaHora, estado, responsable)

    def registrarNoRecepcion(self, fechaHora: datetime, estado: Estado, responsable: Empleado) -> None:
        self.__validarEnBolsinEnviado()
        self.crearCEDocumentacion(fechaHora, estado, responsable)

    def __aceptar(self, fechaHora: datetime, estado: Estado, responsable: Empleado) -> None:
        self.__validarEnBolsinEnviado()
        self.crearCEDocumentacion(fechaHora, estado, responsable)

    def crearCEDocumentacion(self, fechaHora: datetime, estado: Estado, responsable: Empleado) -> None:
        """Cierra el cambio de estado actual y crea el nuevo, registrando el empleado responsable."""
        ceActual = self.obtenerCEActual()
        if ceActual is not None:
            ceActual.setFechaHoraFin(fechaHora)
        self.cambiosEstado.append(CambioDeEstadoDocumentacion(fechaHora, estado, responsable))

    def __validarEnBolsinEnviado(self) -> None:
        estadoActual = self.getEstadoActual()
        if estadoActual is None or not estadoActual.esEnBolsinEnviado():
            raise ValueError(
                f"La documentación {self.numero} no está en estado '{Estado.EN_BOLSIN_ENVIADO}'."
            )
