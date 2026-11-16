"""Iterador concreto que recorre todos los detalles de un remito."""
from iterador.iiterador import IIterador


class IteradorDetalleRemito(IIterador):

    def __init__(self, elementos: list):
        self._elementos = list(elementos)
        self._actual = 0

    def primero(self) -> None:
        self._actual = 0

    def haFinalizado(self) -> bool:
        return self._actual >= len(self._elementos)

    def elementoActual(self) -> object:
        if self.haFinalizado():
            raise IndexError("El iterador de detalles de remito ha finalizado.")
        return self._elementos[self._actual]

    def siguiente(self) -> None:
        self._actual += 1
