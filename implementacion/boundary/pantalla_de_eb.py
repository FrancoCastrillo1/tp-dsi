"""Boundary del CU 28. Guarda lo que hay que mostrar y lo dibuja con la plantilla HTML de Flask."""
from __future__ import annotations

from typing import TYPE_CHECKING, Callable

from flask import render_template

if TYPE_CHECKING:
    from control.gestor_de_bolsin import GestorDeBolsin


class PantallaDeEB:

    def __init__(self, crearGestor: Callable[[PantallaDeEB], GestorDeBolsin]):
        self._crearGestor = crearGestor
        self.gestor: GestorDeBolsin | None = None
        self.vista: dict = {}

    def hayCUEnCurso(self) -> bool:
        return self.gestor is not None and not self.vista.get("finalizado")

    # ------------------------------------------------------------------ paso 1
    def opcionRegistrarRecepcionBolsin(self) -> None:
        self.habilitarVentana()
        self.gestor = self._crearGestor(self)
        self.gestor.nuevaRecepcionBolsin()

    def habilitarVentana(self) -> None:
        self.vista = {
            "cmUsuario": None, "empleado": None, "mensajes": [],
            "bolsines": [], "solicitaFiltro": False, "filtro": {"precinto": "", "cmOrigen": ""},
            "solicitaSeleccionBolsin": False, "bolsinSeleccionado": None,
            "remitos": [], "opciones": {}, "solicitaOpcion": False,
            "opcionSeleccionada": None, "docsMarcados": [],
            "confirmacion": None, "resultado": None, "finalizado": False,
        }

    def _limpiarMensajes(self) -> None:
        self.vista["mensajes"] = []

    # ------------------------------------------------------------------ pasos 2 a 4
    def mostrarCMUsuarioLogueado(self, nombreCM: str, nombreEmpleado: str) -> None:
        self.vista["cmUsuario"] = nombreCM
        self.vista["empleado"] = nombreEmpleado

    def mostrarDatosBolsin(self, datosBolsines: list[dict]) -> None:
        self.vista["bolsines"] = datosBolsines

    def solicitarIngresoFiltro(self) -> None:
        self.vista["solicitaFiltro"] = True

    def solicitarSeleccionListado(self) -> None:
        self.solicitarSeleccionBolsin()

    def solicitarSeleccionBolsin(self) -> None:
        self.vista["solicitaSeleccionBolsin"] = True

    def tomarFiltro(self, numeroPrecinto: str, cmOrigen: str) -> None:
        self._limpiarMensajes()
        self.vista["filtro"] = {"precinto": numeroPrecinto, "cmOrigen": cmOrigen}
        self._reiniciarSeleccion()
        self.gestor.tomarFiltro(numeroPrecinto, cmOrigen)

    # ------------------------------------------------------------------ pasos 5 a 7
    def tomarSeleccionBolsin(self, numeroBolsin: int | None) -> None:
        self._limpiarMensajes()
        self._reiniciarSeleccion()
        self.vista["bolsinSeleccionado"] = numeroBolsin
        self.gestor.tomarSeleccionBolsin(numeroBolsin)

    def _reiniciarSeleccion(self) -> None:
        self.vista.update({"bolsinSeleccionado": None, "remitos": [], "opciones": {}, "solicitaOpcion": False,
                           "opcionSeleccionada": None, "docsMarcados": [], "confirmacion": None})

    def mostrarDatosRemitos(self, datosRemitos: list[dict]) -> None:
        self.vista["remitos"] = datosRemitos

    def mostrarOpciones(self, opciones: dict[int, str]) -> None:
        self.vista["opciones"] = opciones

    def solicitarSeleccionOpcion(self) -> None:
        self.vista["solicitaOpcion"] = True
        self.vista["confirmacion"] = None

    def tomarSeleccionOpcion(self, opcion: int | None, numerosDocumentacion: list[int]) -> None:
        self._limpiarMensajes()
        self.vista["opcionSeleccionada"] = opcion
        self.vista["docsMarcados"] = numerosDocumentacion
        self.gestor.tomarSeleccionOpcion(opcion, numerosDocumentacion)

    # ------------------------------------------------------------------ pasos 9 a 12
    def solicitarSeleccionConfirmacion(self, resumen: dict) -> None:
        self.vista["solicitaOpcion"] = False
        self.vista["confirmacion"] = resumen

    def tomarSeleccionConfirmacion(self, confirma: bool) -> None:
        self._limpiarMensajes()
        self.gestor.tomarConfirmacionDeSeleccion(confirma)

    def informarRegistroExitoso(self, numeroBolsin: int, datosRemitos: list[dict],
                                notificaciones: list[str]) -> None:
        self.vista["confirmacion"] = None
        self.vista["solicitaOpcion"] = False
        self.vista["resultado"] = {"numeroBolsin": numeroBolsin, "remitos": datosRemitos,
                                   "notificaciones": notificaciones}
        self.vista["finalizado"] = True
        self.mostrarMensaje(f"Se registró correctamente la recepción del bolsín {numeroBolsin}.", "exito")

    def mostrarErrorRegistro(self, texto: str) -> None:
        self.vista["confirmacion"] = None
        self.vista["solicitaOpcion"] = False
        self.vista["finalizado"] = True
        self.mostrarMensaje(texto, "error")

    def mostrarMensaje(self, texto: str, tipo: str = "info") -> None:
        self.vista["mensajes"].append({"texto": texto, "tipo": tipo})

    # ------------------------------------------------------------------ cancelación (Obs. 1)
    def cancelar(self) -> None:
        if self.hayCUEnCurso():
            self.gestor.cancelarCU()
        self.gestor = None
        self.vista = {}

    def renderizar(self) -> str:
        return render_template("recepcion.html", **self.vista)
