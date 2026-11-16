"""Prueba de punta a punta del CU 28 a través de la interfaz web."""
import pytest

from app import crearApp


@pytest.fixture
def cliente(rutaBD, correo):
    app = crearApp(rutaBD, correo)
    app.config["TESTING"] = True
    yield app.test_client()
    app.config["PANTALLA"].cancelar()


def test_flujo_completo_web(cliente, correo):
    html = cliente.get("/recepcion").get_data(as_text=True)
    assert "Comisión Médica Córdoba" in html
    assert "5001" in html

    html = cliente.post("/recepcion/bolsin", data={"numeroBolsin": "101"}).get_data(as_text=True)
    assert "Remito 1001" in html
    assert "Opciones de recepción" in html

    html = cliente.post("/recepcion/opcion", data={"opcion": "2", "documentacion": ["2"]}).get_data(as_text=True)
    assert "Confirmar registro" in html

    html = cliente.post("/recepcion/confirmacion", data={"confirma": "si"}).get_data(as_text=True)
    assert "Se registró correctamente la recepción del bolsín 101" in html
    assert "Recibido y Aceptado Parcial" in html
    assert len(correo.mensajesEnviados) == 1


def test_filtro_A1_web(cliente):
    cliente.get("/recepcion")
    html = cliente.post("/recepcion/filtro", data={"precinto": "123", "cmOrigen": ""}).get_data(as_text=True)
    assert "No se encuentra bolsín con el número de precinto ingresado" in html


def test_sin_cu_en_curso_redirige(cliente):
    respuesta = cliente.post("/recepcion/bolsin", data={"numeroBolsin": "101"})
    assert respuesta.status_code == 302
