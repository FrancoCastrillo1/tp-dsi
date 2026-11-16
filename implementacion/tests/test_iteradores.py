from datetime import date, datetime

import pytest

from dominio.bolsin import Bolsin
from dominio.cambio_de_estado_bolsin import CambioDeEstadoBolsin
from dominio.comision_medica import ComisionMedica
from dominio.estado import Estado
from iterador.iterador_bolsin import IteradorBolsin
from iterador.iterador_detalle_remito import IteradorDetalleRemito
from iterador.iterador_remito import IteradorRemito

CBA = ComisionMedica("Comisión Médica Córdoba", "", "", "")
ROS = ComisionMedica("Comisión Médica Rosario", "", "", "")
ENVIADO = Estado(Estado.ENVIADO, "", Estado.AMBITO_BOLSIN)
CERRADO = Estado(Estado.CERRADO, "", Estado.AMBITO_BOLSIN)


def bolsin(numero, origen, estadoActual):
    ces = [CambioDeEstadoBolsin(datetime(2026, 1, 1), CERRADO, None, fechaHoraFin=datetime(2026, 1, 2)),
           CambioDeEstadoBolsin(datetime(2026, 1, 2), estadoActual, None)]
    return Bolsin(numero, date(2026, 1, 1), 100, 9000 + numero, origen, ROS, ces)


def recorrer(iterador):
    elementos = []
    iterador.primero()
    while not iterador.haFinalizado():
        elementos.append(iterador.elementoActual())
        iterador.siguiente()
    return elementos


def test_iterador_bolsin_entrega_solo_enviados_de_la_cm_del_usuario():
    bolsines = [bolsin(1, CBA, ENVIADO), bolsin(2, CBA, CERRADO), bolsin(3, ROS, ENVIADO), bolsin(4, CBA, ENVIADO)]
    resultado = recorrer(IteradorBolsin(bolsines, [CBA]))
    # los que no cumplen los filtros se devuelven como None
    assert [b.getNumeroBolsin() if b else None for b in resultado] == [1, None, None, 4]


def test_comprobar_filtros_usa_cm_origen_y_estado_enviado():
    iterador = IteradorBolsin([bolsin(1, CBA, ENVIADO)], [CBA])
    iterador.primero()
    assert iterador.comprobarFiltros([CBA]) is True
    assert iterador.comprobarFiltros([ROS]) is False


@pytest.mark.parametrize("Iterador", [IteradorRemito, IteradorDetalleRemito])
def test_iteradores_sin_filtro_recorren_todo_en_orden(Iterador):
    assert recorrer(Iterador(["a", "b", "c"])) == ["a", "b", "c"]


@pytest.mark.parametrize("Iterador", [IteradorRemito, IteradorDetalleRemito])
def test_coleccion_vacia_finaliza_inmediatamente(Iterador):
    iterador = Iterador([])
    iterador.primero()
    assert iterador.haFinalizado()
    with pytest.raises(IndexError):
        iterador.elementoActual()


def test_primero_reinicia_el_recorrido():
    iterador = IteradorRemito([1, 2])
    iterador.primero()
    iterador.siguiente()
    iterador.siguiente()
    assert iterador.haFinalizado()
    iterador.primero()
    assert iterador.elementoActual() == 1


def test_recorridos_concurrentes_son_independientes():
    externo = IteradorRemito(["r1", "r2"])
    externo.primero()
    interno = IteradorDetalleRemito(["d1", "d2"])
    interno.primero()
    interno.siguiente()
    assert externo.elementoActual() == "r1"
    assert interno.elementoActual() == "d2"
