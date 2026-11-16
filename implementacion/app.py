"""Aplicación web (Flask) del CU 28 - Registrar recepción de bolsín.

Ejecutar:  python app.py            (crea bolsines.db con datos de prueba si no existe)
           python app.py --reiniciar (vuelve a crear la base con los datos de prueba)
"""
import argparse
import logging
from pathlib import Path

from flask import Flask, redirect, render_template, request, url_for

from boundary.pantalla_de_eb import PantallaDeEB
from control.gestor_de_bolsin import GestorDeBolsin
from interfaces.interfaz_servidor_correo import InterfazServidorCorreo
from persistencia.conexion import Conexion
from persistencia.datos_semilla import inicializarBaseDeDatos
from persistencia.fabrica_dao import FabricaDAO

RUTA_BD_POR_DEFECTO = str(Path(__file__).with_name("bolsines.db"))


def crearApp(rutaBaseDatos: str = RUTA_BD_POR_DEFECTO,
             interfazCorreo: InterfazServidorCorreo | None = None) -> Flask:
    app = Flask(__name__, template_folder="boundary/templates", static_folder="boundary/static")
    interfazCorreo = interfazCorreo or InterfazServidorCorreo()

    def crearGestor(pantalla: PantallaDeEB) -> GestorDeBolsin:
        daos = FabricaDAO(Conexion(rutaBaseDatos))
        sesion = daos.sesion.buscarSesionActiva()  # sesión fija precargada
        if sesion is None:
            raise RuntimeError("No hay una sesión activa precargada en la base de datos.")
        return GestorDeBolsin(pantalla, sesion, daos, interfazCorreo)

    # Una única pantalla: la sesión es fija y hay un solo usuario.
    pantalla = PantallaDeEB(crearGestor)
    app.config["PANTALLA"] = pantalla

    def requiereCUEnCurso(funcion):
        def envoltura(*args, **kwargs):
            if not pantalla.hayCUEnCurso():
                return redirect(url_for("opcionRegistrarRecepcionBolsin"))
            return funcion(*args, **kwargs)
        envoltura.__name__ = funcion.__name__
        return envoltura

    @app.get("/")
    def inicio():
        return render_template("inicio.html")

    @app.get("/recepcion")
    def opcionRegistrarRecepcionBolsin():
        pantalla.cancelar()  # si había un CU a medio terminar, se descarta
        pantalla.opcionRegistrarRecepcionBolsin()
        return pantalla.renderizar()

    @app.post("/recepcion/filtro")
    @requiereCUEnCurso
    def tomarFiltro():
        pantalla.tomarFiltro(request.form.get("precinto", ""), request.form.get("cmOrigen", ""))
        return pantalla.renderizar()

    @app.post("/recepcion/bolsin")
    @requiereCUEnCurso
    def tomarSeleccionBolsin():
        pantalla.tomarSeleccionBolsin(request.form.get("numeroBolsin", type=int))
        return pantalla.renderizar()

    @app.post("/recepcion/opcion")
    @requiereCUEnCurso
    def tomarSeleccionOpcion():
        numeros = [int(n) for n in request.form.getlist("documentacion") if n.isdigit()]
        pantalla.tomarSeleccionOpcion(request.form.get("opcion", type=int), numeros)
        return pantalla.renderizar()

    @app.post("/recepcion/confirmacion")
    @requiereCUEnCurso
    def tomarSeleccionConfirmacion():
        pantalla.tomarSeleccionConfirmacion(request.form.get("confirma") == "si")
        return pantalla.renderizar()

    @app.post("/recepcion/cancelar")
    def cancelar():
        pantalla.cancelar()
        return redirect(url_for("inicio"))

    return app


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CU 28 - Registrar recepción de bolsín")
    parser.add_argument("--reiniciar", action="store_true", help="recrea la base con los datos de prueba")
    parser.add_argument("--puerto", type=int, default=5000)
    argumentos = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(message)s")
    inicializarBaseDeDatos(RUTA_BD_POR_DEFECTO, reiniciar=argumentos.reiniciar)
    crearApp().run(port=argumentos.puerto, debug=False, threaded=False)
