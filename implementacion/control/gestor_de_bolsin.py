"""Controlador del CU 28 - Registrar recepción de bolsín."""
from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from dominio.bolsin import Bolsin
from dominio.comision_medica import ComisionMedica
from dominio.empleado import Empleado
from dominio.estado import Estado
from dominio.sesion import Sesion
from interfaces.interfaz_servidor_correo import InterfazServidorCorreo
from iterador.iagregado import IAgregado
from iterador.iiterador import IIterador
from iterador.iterador_bolsin import IteradorBolsin
from persistencia.fabrica_dao import FabricaDAO

if TYPE_CHECKING:
    from boundary.pantalla_de_eb import PantallaDeEB


class GestorDeBolsin(IAgregado):
    """Agregado concreto: crea el IteradorBolsin para recorrer los bolsines."""

    OPCION_CONTENIDO_IGUAL = 1
    OPCION_NO_SE_RECIBE_TODO = 2
    OPCION_NO_CORRESPONDE_DESTINO = 3
    OPCION_REDIRIGIR_OTRA_AREA = 4

    def __init__(self, pantalla: PantallaDeEB, sesion: Sesion, daos: FabricaDAO,
                 interfazCorreo: InterfazServidorCorreo):
        self.pantalla = pantalla
        self.sesion = sesion
        self.daos = daos
        self.interfazCorreo = interfazCorreo

        self.empleadoLogueado: Empleado | None = None
        self.cmUsuarioLogueado: ComisionMedica | None = None
        self.bolsinesEnviadosPorUsuario: list[Bolsin] = []
        self.bolsinSeleccionado: Bolsin | None = None
        self.opcionesRecepcion: dict[int, str] = {
            self.OPCION_CONTENIDO_IGUAL: "El contenido del bolsín es igual al registrado",
            self.OPCION_NO_SE_RECIBE_TODO: "No se recibe toda la documentación asociada a los remitos que contiene el bolsín",
            self.OPCION_NO_CORRESPONDE_DESTINO: "Existe documentación que no corresponde al destino",
            self.OPCION_REDIRIGIR_OTRA_AREA: "La documentación se debe redirigir a otra área",
        }
        self.opcionSeleccionada: int | None = None
        self.documentacionAfectada: set[int] = set()
        self.fechaYHora: datetime | None = None

    # ------------------------------------------------------------------ pasos 1 a 4
    def nuevaRecepcionBolsin(self) -> None:
        cm = self.buscarCMdeUsuarioLogueado()
        self.pantalla.mostrarCMUsuarioLogueado(cm.getNombre(), self.empleadoLogueado.getNombreCompleto())

        datosBolsines = self.buscarBolsinesEnviadosUsr()
        if not datosBolsines:
            self.pantalla.mostrarMensaje("No se encontraron bolsines en estado Enviado para la CM del usuario logueado.",
                                         "error")
            return
        self.habilitarSeleccion(datosBolsines)

    def buscarCMdeUsuarioLogueado(self) -> ComisionMedica:
        usuario = self.sesion.getUsuarioLogueado()
        for empleado in self.daos.empleado.obtenerTodos():
            if empleado.esTuUsuario(usuario):
                self.empleadoLogueado = empleado
                self.cmUsuarioLogueado = empleado.getCM()
                return self.cmUsuarioLogueado
        raise LookupError(f"El usuario {usuario.getNombre()} no está asociado a ningún empleado.")

    def buscarBolsinesEnviadosUsr(self) -> list[dict]:
        """Recorre los bolsines con IteradorBolsin, que sólo entrega los Enviados de la CM del usuario."""
        self.bolsinesEnviadosPorUsuario = []
        datosBolsines = []

        iterador = self.crearIterador(self.daos.bolsin.obtenerTodos())
        iterador.primero()
        while not iterador.haFinalizado():
            bolsin = iterador.elementoActual()
            if bolsin is not None:
                self.bolsinesEnviadosPorUsuario.append(bolsin)
                datosBolsines.append(self._datosBolsin(bolsin))
            iterador.siguiente()
        return datosBolsines

    def crearIterador(self, elementos: list) -> IIterador:
        return IteradorBolsin(elementos, [self.cmUsuarioLogueado])

    @staticmethod
    def _datosBolsin(bolsin: Bolsin) -> dict:
        return {
            "numeroBolsin": bolsin.getNumeroBolsin(),
            "cmOrigen": bolsin.getCMOrigen().getNombre(),
            "numeroPrecinto": bolsin.getNumeroPrecinto(),
        }

    def habilitarSeleccion(self, datosBolsines: list[dict]) -> None:
        self.pantalla.mostrarDatosBolsin(datosBolsines)
        self.pantalla.solicitarIngresoFiltro()
        self.pantalla.solicitarSeleccionListado()

    # ------------------------------------------------------------------ filtro (A1 / A2)
    def tomarFiltro(self, numeroPrecinto: str, cmOrigen: str) -> None:
        resultado = self.filtrar(numeroPrecinto.strip(), cmOrigen.strip())
        if resultado is not None:
            self.pantalla.mostrarDatosBolsin([self._datosBolsin(b) for b in resultado])
            self.pantalla.solicitarSeleccionListado()

    def filtrar(self, numeroPrecinto: str, cmOrigen: str) -> list[Bolsin] | None:
        bolsines = self.bolsinesEnviadosPorUsuario

        if numeroPrecinto:
            bolsines = [b for b in bolsines if str(b.getNumeroPrecinto()) == numeroPrecinto]
            if not bolsines:  # A1
                self.pantalla.mostrarMensaje(
                    f"No se encuentra bolsín con el número de precinto ingresado ({numeroPrecinto}).", "error")
                return None

        if cmOrigen:
            bolsines = [b for b in bolsines if cmOrigen.lower() in b.getCMOrigen().getNombre().lower()]
            if not bolsines:  # A2
                self.pantalla.mostrarMensaje(
                    f"No se encuentra bolsín con la CM de origen ingresada ({cmOrigen}).", "error")
                return None

        return bolsines

    # ------------------------------------------------------------------ pasos 5 a 7
    def tomarSeleccionBolsin(self, numeroBolsin: int) -> None:
        self.bolsinSeleccionado = next(
            (b for b in self.bolsinesEnviadosPorUsuario if b.getNumeroBolsin() == numeroBolsin), None)
        if self.bolsinSeleccionado is None:
            self.pantalla.mostrarMensaje("Debe seleccionar un bolsín del listado.", "error")
            return

        self.pantalla.mostrarDatosRemitos(self.buscarDatosBolsin())
        self.pantalla.mostrarOpciones(self.opcionesRecepcion)
        self.pantalla.solicitarSeleccionOpcion()

    def buscarDatosBolsin(self) -> list[dict]:
        return self.bolsinSeleccionado.obtenerInformacionRemito()

    def buscarCMDestino(self) -> str:
        return self.bolsinSeleccionado.getCMDestino().getNombre()

    # ------------------------------------------------------------------ pasos 8 a 10 (A3, A4, A5, A6)
    def tomarSeleccionOpcion(self, opcion: int | None, numerosDocumentacion: list[int]) -> None:
        if opcion not in self.opcionesRecepcion:
            self.pantalla.mostrarMensaje("Debe seleccionar una opción de recepción.", "error")
            self.pantalla.solicitarSeleccionOpcion()
            return

        if opcion == self.OPCION_CONTENIDO_IGUAL:
            afectada = set()
        else:
            numerosDelBolsin = self._numerosDocumentacionDelBolsin()
            afectada = set(numerosDocumentacion) & numerosDelBolsin
            if not afectada:
                self.pantalla.mostrarMensaje(
                    "Para la opción seleccionada debe marcar al menos una documentación afectada.", "error")
                self.pantalla.solicitarSeleccionOpcion()
                return

        self.opcionSeleccionada = opcion
        self.documentacionAfectada = afectada
        self.solicitarConfirmacionRegistro()

    def _numerosDocumentacionDelBolsin(self) -> set[int]:
        return {doc["numero"] for remito in self.buscarDatosBolsin() for doc in remito["documentacion"]}

    def solicitarConfirmacionRegistro(self) -> None:
        self.pantalla.solicitarSeleccionConfirmacion({
            "numeroBolsin": self.bolsinSeleccionado.getNumeroBolsin(),
            "numeroPrecinto": self.bolsinSeleccionado.getNumeroPrecinto(),
            "cmDestino": self.buscarCMDestino(),
            "opcion": self.opcionesRecepcion[self.opcionSeleccionada],
            "documentacionAfectada": sorted(self.documentacionAfectada),
            "estadoDocAfectada": self._nombreEstadoDocAfectada(),
        })

    def tomarConfirmacionDeSeleccion(self, confirma: bool) -> None:
        if not confirma:  # A6
            self.opcionSeleccionada = None
            self.documentacionAfectada = set()
            self.pantalla.mostrarMensaje("No se confirmó la opción de recepción. Seleccione nuevamente.", "info")
            self.pantalla.mostrarOpciones(self.opcionesRecepcion)
            self.pantalla.solicitarSeleccionOpcion()
            return

        try:
            self.registrarRecepcionDeBolsin()
        except (ValueError, LookupError) as error:
            # La transacción se deshizo; los objetos en memoria quedan descartados al terminar el CU.
            self.pantalla.mostrarErrorRegistro(f"No se pudo registrar la recepción: {error}")
            self.finCU()
            return

        notificaciones = self.notificarRecepcionBolsin()
        self.pantalla.informarRegistroExitoso(self.bolsinSeleccionado.getNumeroBolsin(),
                                              self.buscarDatosBolsin(), notificaciones)
        self.finCU()

    # ------------------------------------------------------------------ paso 11
    def getFechaHoraActual(self) -> datetime:
        return datetime.now().replace(microsecond=0)

    def registrarRecepcionDeBolsin(self) -> None:
        self.fechaYHora = self.getFechaHoraActual()
        estados = self.daos.estado.obtenerTodos()

        self.recibirBolsin(
            estadoBolsin=self.buscarBolsinRecibido(estados),
            estadoRemitoAceptado=self.buscarRemitosAceptados(estados),
            estadoRemitoParcial=self.buscarRemitosAceptadosParcial(estados),
            estadoDocAceptada=self.buscarDocumentacionAceptada(estados),
            estadoDocAfectada=self.buscarEstadoDocumentacionAfectada(estados),
        )

        with self.daos.transaccion():
            self.daos.bolsin.actualizar(self.bolsinSeleccionado)

    def recibirBolsin(self, estadoBolsin: Estado, estadoRemitoAceptado: Estado, estadoRemitoParcial: Estado,
                      estadoDocAceptada: Estado, estadoDocAfectada: Estado | None) -> None:
        self.bolsinSeleccionado.recibirBolsin(
            fechaHora=self.fechaYHora,
            responsable=self.empleadoLogueado,
            estadoBolsin=estadoBolsin,
            numerosDocAfectados=self.documentacionAfectada,
            estadoDocAceptada=estadoDocAceptada,
            estadoDocAfectada=estadoDocAfectada,
            estadoRemitoAceptado=estadoRemitoAceptado,
            estadoRemitoParcial=estadoRemitoParcial,
        )

    # --- Búsqueda de estados (recorriendo los estados con esAmbitoX() y esX()) ---
    @staticmethod
    def _buscarEstado(estados: list[Estado], esDelAmbito, esElEstado) -> Estado:
        for estado in estados:
            if esDelAmbito(estado) and esElEstado(estado):
                return estado
        raise LookupError("No se encontró el estado buscado.")

    def buscarBolsinRecibido(self, estados: list[Estado]) -> Estado:
        return self._buscarEstado(estados, Estado.esAmbitoBolsin, Estado.esRecibidoEnCMDestino)

    def buscarRemitosAceptados(self, estados: list[Estado]) -> Estado:
        return self._buscarEstado(estados, Estado.esAmbitoRemito, Estado.esRecibidoYAceptado)

    def buscarRemitosAceptadosParcial(self, estados: list[Estado]) -> Estado:
        return self._buscarEstado(estados, Estado.esAmbitoRemito, Estado.esRecibidoYAceptadoParcial)

    def buscarDocumentacionAceptada(self, estados: list[Estado]) -> Estado:
        return self._buscarEstado(estados, Estado.esAmbitoDocumentacion, Estado.esRecibidaYAceptada)

    def buscarEstadoDocumentacionAfectada(self, estados: list[Estado]) -> Estado | None:
        """Opción 2 -> No recibida. Opciones 3 y 4 -> Recibida y Rechazada (máquina de estados de Documentacion;
        el pasaje a Para redirigir lo hace el CU 31)."""
        if self.opcionSeleccionada == self.OPCION_NO_SE_RECIBE_TODO:
            return self._buscarEstado(estados, Estado.esAmbitoDocumentacion, Estado.esNoRecibida)
        if self.opcionSeleccionada in (self.OPCION_NO_CORRESPONDE_DESTINO, self.OPCION_REDIRIGIR_OTRA_AREA):
            return self._buscarEstado(estados, Estado.esAmbitoDocumentacion, Estado.esRecibidaYRechazada)
        return None

    def _nombreEstadoDocAfectada(self) -> str | None:
        if self.opcionSeleccionada == self.OPCION_NO_SE_RECIBE_TODO:
            return Estado.NO_RECIBIDA
        if self.opcionSeleccionada in (self.OPCION_NO_CORRESPONDE_DESTINO, self.OPCION_REDIRIGIR_OTRA_AREA):
            return Estado.RECIBIDA_Y_RECHAZADA
        return None

    # ------------------------------------------------------------------ paso 12: include CU 29
    def notificarRecepcionBolsin(self) -> list[str]:
        """CU 29: notifica a cada CM origen que envió documentación la recepción y la situación de su documentación."""
        documentacionPorCM: dict[str, list[dict]] = {}
        for remito in self.buscarDatosBolsin():
            for doc in remito["documentacion"]:
                documentacionPorCM.setdefault(doc["emailCMOrigen"], []).append({**doc, "remito": remito["numero"]})

        numeroBolsin = self.bolsinSeleccionado.getNumeroBolsin()
        for email, documentacion in documentacionPorCM.items():
            lineas = [f"- Remito {d['remito']} | Doc. {d['numero']} ({d['tipo']}) {d['asunto']}: {d['estado']}"
                      for d in documentacion]
            cuerpo = (f"El bolsín {numeroBolsin} fue recibido en {self.cmUsuarioLogueado.getNombre()} "
                      f"el {self.fechaYHora:%d/%m/%Y %H:%M} por {self.empleadoLogueado.getNombreCompleto()}.\n"
                      "Situación de la documentación:\n" + "\n".join(lineas))
            self.interfazCorreo.enviarNotificacion(email, f"Recepción del bolsín {numeroBolsin}", cuerpo)
        return list(documentacionPorCM)

    # ------------------------------------------------------------------ fin / cancelación
    def cancelarCU(self) -> None:
        """Observación 1: el EB puede cancelar el caso de uso cuando lo decida."""
        self.finCU()

    def finCU(self) -> None:
        self.daos.conexion.cerrar()
