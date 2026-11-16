"""Iterador concreto de bolsines con filtros (CM del usuario logueado y estado Enviado)."""
from iterador.iiterador import IIterador


class IteradorBolsin(IIterador):
    """Recorre bolsines y sólo entrega los que cumplen los filtros.

    filtros[0] es la ComisionMedica del usuario logueado.
    """

    def __init__(self, elementos: list, filtros: list):
        self._elementos = list(elementos)
        self._filtros = list(filtros)
        self._actual = 0

    def primero(self) -> None:
        self._actual = 0

    def haFinalizado(self) -> bool:
        return self._actual >= len(self._elementos)

    def elementoActual(self) -> object:
        """Devuelve el bolsín actual si cumple los filtros, si no devuelve None."""
        if self.haFinalizado():
            raise IndexError("El iterador de bolsines ha finalizado.")
        if self.comprobarFiltros(self._filtros):
            return self._elementos[self._actual]
        return None

    def siguiente(self) -> None:
        self._actual += 1

    def comprobarFiltros(self, filtros: list) -> bool:
        bolsin = self._elementos[self._actual]
        cmUsuarioLogueado = filtros[0]
        return bolsin.esTuCMOrigen(cmUsuarioLogueado) and bolsin.sosEnviado()
