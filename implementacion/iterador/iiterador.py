"""Interfaz Iterador del patrón Iterator (Gamma)."""
from abc import ABC, abstractmethod


class IIterador(ABC):
    """Define la interfaz para acceder y recorrer los elementos de un agregado."""

    @abstractmethod
    def primero(self) -> None:
        """Posiciona el iterador en el primer elemento."""

    @abstractmethod
    def haFinalizado(self) -> bool:
        """Indica si ya se recorrieron todos los elementos."""

    @abstractmethod
    def elementoActual(self) -> object:
        """Devuelve el elemento de la posición actual."""

    @abstractmethod
    def siguiente(self) -> None:
        """Avanza a la siguiente posición."""
