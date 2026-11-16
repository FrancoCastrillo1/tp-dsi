import pytest

from control.gestor_de_bolsin import GestorDeBolsin
from interfaces.interfaz_servidor_correo import InterfazServidorCorreo
from persistencia.conexion import Conexion
from persistencia.datos_semilla import inicializarBaseDeDatos
from persistencia.fabrica_dao import FabricaDAO


class PantallaFalsa:
    """Doble de prueba de PantallaDeEB: registra lo que el gestor le pide mostrar."""

    def __init__(self):
        self.cm = None
        self.bolsines = []
        self.remitos = []
        self.opciones = {}
        self.mensajes = []
        self.confirmacion = None
        self.solicitaOpcion = False
        self.resultado = None
        self.errorRegistro = None

    def mostrarCMUsuarioLogueado(self, nombreCM, nombreEmpleado): self.cm = nombreCM
    def mostrarDatosBolsin(self, datos): self.bolsines = datos
    def solicitarIngresoFiltro(self): pass
    def solicitarSeleccionListado(self): pass
    def mostrarDatosRemitos(self, datos): self.remitos = datos
    def mostrarOpciones(self, opciones): self.opciones = opciones
    def solicitarSeleccionOpcion(self): self.solicitaOpcion = True; self.confirmacion = None
    def solicitarSeleccionConfirmacion(self, resumen): self.solicitaOpcion = False; self.confirmacion = resumen
    def informarRegistroExitoso(self, numero, remitos, notificaciones): self.resultado = (numero, remitos, notificaciones)
    def mostrarErrorRegistro(self, texto): self.errorRegistro = texto
    def mostrarMensaje(self, texto, tipo="info"): self.mensajes.append((tipo, texto))


@pytest.fixture
def rutaBD(tmp_path):
    ruta = str(tmp_path / "test.db")
    inicializarBaseDeDatos(ruta)
    return ruta


@pytest.fixture
def correo():
    return InterfazServidorCorreo()


@pytest.fixture
def pantalla():
    return PantallaFalsa()


@pytest.fixture
def gestor(rutaBD, pantalla, correo):
    daos = FabricaDAO(Conexion(rutaBD))
    gestor = GestorDeBolsin(pantalla, daos.sesion.buscarSesionActiva(), daos, correo)
    yield gestor
    try:
        daos.conexion.cerrar()
    except Exception:
        pass


@pytest.fixture
def leerBD(rutaBD):
    """Devuelve una FabricaDAO nueva (sin caché) para verificar lo que quedó persistido."""
    abiertas = []

    def _leer():
        daos = FabricaDAO(Conexion(rutaBD))
        abiertas.append(daos)
        return daos

    yield _leer
    for daos in abiertas:
        daos.conexion.cerrar()
