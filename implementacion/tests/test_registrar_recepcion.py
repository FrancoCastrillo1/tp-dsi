"""Tests del CU 28 sobre una base SQLite temporal con los datos de prueba."""
from dominio.estado import Estado

# Datos de prueba: bolsín 101 (precinto 5001) -> remito 1001 [doc 1, 2], remito 1002 [doc 3]


def iniciarYSeleccionar(gestor, numeroBolsin=101):
    gestor.nuevaRecepcionBolsin()
    gestor.tomarSeleccionBolsin(numeroBolsin)


def estadoDoc(daos, numero):
    filas = daos.conexion.consultar("SELECT id FROM documentacion WHERE numero = ?", (numero,))
    return daos.documentacion.obtenerPorId(filas[0]["id"]).getEstadoActual().getNombre()


def remitosPorNumero(bolsin):
    return {r.getNumero(): r.getEstado().getNombre() for r in bolsin.remitos}


# ------------------------------------------------------------------ pasos 1 a 6
def test_lista_bolsines_enviados_cuya_cm_origen_es_la_del_usuario(gestor, pantalla):
    gestor.nuevaRecepcionBolsin()
    assert pantalla.cm == "Comisión Médica Córdoba"
    assert [b["numeroBolsin"] for b in pantalla.bolsines] == [101, 102, 103]  # 104 Cerrado, 105 es de Rosario
    assert pantalla.bolsines[0] == {"numeroBolsin": 101, "cmOrigen": "Comisión Médica Córdoba",
                                    "numeroPrecinto": 5001}


def test_muestra_remitos_y_documentacion_del_bolsin(gestor, pantalla):
    iniciarYSeleccionar(gestor)
    assert [r["numero"] for r in pantalla.remitos] == [1001, 1002]
    doc = pantalla.remitos[0]["documentacion"][0]
    assert doc["asunto"] == "Expediente de incapacidad laboral - Pérez, Juan"
    assert doc["tipo"] == "Expediente"
    assert list(pantalla.opciones) == [1, 2, 3, 4]


# ------------------------------------------------------------------ A1 / A2
def test_filtro_por_precinto(gestor, pantalla):
    gestor.nuevaRecepcionBolsin()
    gestor.tomarFiltro("5002", "")
    assert [b["numeroBolsin"] for b in pantalla.bolsines] == [102]


def test_A1_precinto_inexistente(gestor, pantalla):
    gestor.nuevaRecepcionBolsin()
    gestor.tomarFiltro("9999", "")
    assert pantalla.mensajes[-1][0] == "error"
    assert "precinto" in pantalla.mensajes[-1][1]


def test_A2_cm_origen_inexistente(gestor, pantalla):
    gestor.nuevaRecepcionBolsin()
    gestor.tomarFiltro("", "Salta")
    assert pantalla.mensajes[-1][0] == "error"
    assert "CM de origen" in pantalla.mensajes[-1][1]


# ------------------------------------------------------------------ flujo básico (opción 1)
def test_opcion_1_contenido_igual(gestor, pantalla, correo, leerBD):
    iniciarYSeleccionar(gestor)
    gestor.tomarSeleccionOpcion(1, [])
    assert pantalla.confirmacion is not None
    gestor.tomarConfirmacionDeSeleccion(True)

    daos = leerBD()
    bolsin = daos.bolsin.obtenerPorNumero(101)
    ceActual = bolsin.obtenerCEActual()
    assert ceActual.getEstado().esRecibidoEnCMDestino()
    assert ceActual.getResponsable().getNombreCompleto() == "Laura Fernández"
    assert len([ce for ce in bolsin.cambiosEstado if ce.sosActual()]) == 1  # el CE anterior quedó cerrado

    assert remitosPorNumero(bolsin) == {1001: Estado.RECIBIDO_Y_ACEPTADO, 1002: Estado.RECIBIDO_Y_ACEPTADO}
    for numero in (1, 2, 3):
        assert estadoDoc(daos, numero) == Estado.RECIBIDA_Y_ACEPTADA
    doc = daos.documentacion.obtenerPorId(1)
    assert doc.obtenerCEActual().getResponsable().getNombreCompleto() == "Laura Fernández"

    # paso 12: CU 29 (una notificación por CM origen de la documentación)
    assert [m["destinatario"] for m in correo.mensajesEnviados] == ["cm.cordoba@organismo.gob.ar"]
    assert pantalla.resultado[0] == 101


# ------------------------------------------------------------------ A3, A4, A5
def test_A3_no_se_recibe_toda_la_documentacion(gestor, leerBD):
    iniciarYSeleccionar(gestor)
    gestor.tomarSeleccionOpcion(2, [2])
    gestor.tomarConfirmacionDeSeleccion(True)

    daos = leerBD()
    assert estadoDoc(daos, 1) == Estado.RECIBIDA_Y_ACEPTADA
    assert estadoDoc(daos, 2) == Estado.NO_RECIBIDA
    assert estadoDoc(daos, 3) == Estado.RECIBIDA_Y_ACEPTADA
    assert remitosPorNumero(daos.bolsin.obtenerPorNumero(101)) == {
        1001: Estado.RECIBIDO_Y_ACEPTADO_PARCIAL, 1002: Estado.RECIBIDO_Y_ACEPTADO}


def test_A4_documentacion_que_no_corresponde_al_destino(gestor, leerBD):
    iniciarYSeleccionar(gestor)
    gestor.tomarSeleccionOpcion(3, [3])
    gestor.tomarConfirmacionDeSeleccion(True)

    daos = leerBD()
    assert estadoDoc(daos, 3) == Estado.RECIBIDA_Y_RECHAZADA
    assert remitosPorNumero(daos.bolsin.obtenerPorNumero(101)) == {
        1001: Estado.RECIBIDO_Y_ACEPTADO, 1002: Estado.RECIBIDO_Y_ACEPTADO_PARCIAL}


def test_A5_redirigir_queda_recibida_y_rechazada_segun_maquina_de_estados(gestor, leerBD):
    iniciarYSeleccionar(gestor)
    gestor.tomarSeleccionOpcion(4, [1, 3])
    gestor.tomarConfirmacionDeSeleccion(True)

    daos = leerBD()
    assert estadoDoc(daos, 1) == Estado.RECIBIDA_Y_RECHAZADA
    assert estadoDoc(daos, 2) == Estado.RECIBIDA_Y_ACEPTADA
    assert estadoDoc(daos, 3) == Estado.RECIBIDA_Y_RECHAZADA
    assert daos.bolsin.obtenerPorNumero(101).getEstadoActual().esRecibidoEnCMDestino()


def test_opciones_2_a_4_requieren_marcar_documentacion(gestor, pantalla):
    iniciarYSeleccionar(gestor)
    gestor.tomarSeleccionOpcion(2, [])
    assert pantalla.confirmacion is None
    assert pantalla.mensajes[-1][0] == "error"


def test_documentacion_de_otro_bolsin_se_ignora(gestor, pantalla):
    iniciarYSeleccionar(gestor)
    gestor.tomarSeleccionOpcion(3, [4])  # la doc 4 está en el bolsín 102
    assert pantalla.confirmacion is None


# ------------------------------------------------------------------ A6
def test_A6_no_confirma_no_modifica_nada(gestor, pantalla, correo, leerBD):
    iniciarYSeleccionar(gestor)
    gestor.tomarSeleccionOpcion(1, [])
    gestor.tomarConfirmacionDeSeleccion(False)

    assert pantalla.solicitaOpcion is True
    assert correo.mensajesEnviados == []
    daos = leerBD()
    assert daos.bolsin.obtenerPorNumero(101).sosEnviado()
    assert estadoDoc(daos, 1) == Estado.EN_BOLSIN_ENVIADO


def test_bolsin_recibido_ya_no_se_lista(gestor, rutaBD, correo):
    from tests.conftest import PantallaFalsa
    from control.gestor_de_bolsin import GestorDeBolsin
    from persistencia.conexion import Conexion
    from persistencia.fabrica_dao import FabricaDAO

    iniciarYSeleccionar(gestor)
    gestor.tomarSeleccionOpcion(1, [])
    gestor.tomarConfirmacionDeSeleccion(True)

    otraPantalla = PantallaFalsa()
    daos = FabricaDAO(Conexion(rutaBD))
    GestorDeBolsin(otraPantalla, daos.sesion.buscarSesionActiva(), daos, correo).nuevaRecepcionBolsin()
    assert [b["numeroBolsin"] for b in otraPantalla.bolsines] == [102, 103]
    daos.conexion.cerrar()
