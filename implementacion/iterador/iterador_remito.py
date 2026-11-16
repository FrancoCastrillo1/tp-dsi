"""Iterador concreto que recorre todos los remitos de un bolsín."""
from iterador.iiterador import IIterador


class IteradorRemito(IIterador):

    def __init__(self, elementos: list):
        self._elementos = list(elementos)
        self._actual = 0

    def primero(self) -> None:
        self._actual = 0

    def haFinalizado(self) -> bool:
        return self._actual >= len(self._elementos)

    def elementoActual(self) -> object:
        if self.haFinalizado():
            raise IndexError("El iterador de remitos ha finalizado.")
        return self._elementos[self._actual]

    def siguiente(self) -> None:
        self._actual += 1
