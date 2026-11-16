"""Interfaz Agregado del patrón Iterator (Gamma)."""
from abc import ABC, abstractmethod

from iterador.iiterador import IIterador


class IAgregado(ABC):
    """Define la interfaz para crear un iterador sobre una colección."""

    @abstractmethod
    def crearIterador(self, elementos: list) -> IIterador:
        """Crea el iterador concreto que recorre los elementos recibidos."""
