"""DAOs de las clases de soporte: ComisionMedica, Estado, TipoDocumentacion, Usuario, Sesion y Empleado.

Los objetos de soporte se guardan en una caché por id dentro de la FabricaDAO,
así todas las referencias a una misma fila apuntan al mismo objeto.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from dominio.comision_medica import ComisionMedica
from dominio.empleado import Empleado
from dominio.estado import Estado
from dominio.sesion import Sesion
from dominio.tipo_documentacion import TipoDocumentacion
from dominio.usuario import Usuario
from persistencia.conexion import aFechaHora

if TYPE_CHECKING:
    from persistencia.fabrica_dao import FabricaDAO


class DAOBase:

    def __init__(self, fabrica: FabricaDAO):
        self._fabrica = fabrica
        self._conexion = fabrica.conexion
        self._cache: dict[int, object] = {}


class ComisionMedicaDAO(DAOBase):

    def obtenerPorId(self, id: int) -> ComisionMedica:
        if id not in self._cache:
            fila = self._conexion.consultarUno("SELECT * FROM comision_medica WHERE id = ?", (id,))
            self._cache[id] = ComisionMedica(fila["nombre"], fila["direccion"], fila["email"],
                                             fila["telefono"], id=fila["id"])
        return self._cache[id]

    def obtenerTodos(self) -> list[ComisionMedica]:
        filas = self._conexion.consultar("SELECT id FROM comision_medica ORDER BY nombre")
        return [self.obtenerPorId(fila["id"]) for fila in filas]


class EstadoDAO(DAOBase):

    def obtenerPorId(self, id: int) -> Estado:
        if id not in self._cache:
            fila = self._conexion.consultarUno("SELECT * FROM estado WHERE id = ?", (id,))
            self._cache[id] = Estado(fila["nombre"], fila["descripcion"], fila["ambito"], id=fila["id"])
        return self._cache[id]

    def obtenerTodos(self) -> list[Estado]:
        filas = self._conexion.consultar("SELECT id FROM estado ORDER BY id")
        return [self.obtenerPorId(fila["id"]) for fila in filas]


class TipoDocumentacionDAO(DAOBase):

    def obtenerPorId(self, id: int) -> TipoDocumentacion:
        if id not in self._cache:
            fila = self._conexion.consultarUno("SELECT * FROM tipo_documentacion WHERE id = ?", (id,))
            self._cache[id] = TipoDocumentacion(fila["nombre"], fila["descripcion"], id=fila["id"])
        return self._cache[id]


class UsuarioDAO(DAOBase):

    def obtenerPorId(self, id: int) -> Usuario:
        if id not in self._cache:
            fila = self._conexion.consultarUno("SELECT * FROM usuario WHERE id = ?", (id,))
            self._cache[id] = Usuario(fila["nombre"], fila["password"], id=fila["id"])
        return self._cache[id]


class SesionDAO(DAOBase):

    def buscarSesionActiva(self) -> Sesion | None:
        fila = self._conexion.consultarUno(
            "SELECT * FROM sesion WHERE fecha_hora_fin IS NULL ORDER BY fecha_hora_inicio DESC LIMIT 1"
        )
        if fila is None:
            return None
        usuario = self._fabrica.usuario.obtenerPorId(fila["usuario_id"])
        return Sesion(aFechaHora(fila["fecha_hora_inicio"]), usuario,
                      aFechaHora(fila["fecha_hora_fin"]), id=fila["id"])


class EmpleadoDAO(DAOBase):

    def obtenerPorId(self, id: int) -> Empleado:
        if id not in self._cache:
            fila = self._conexion.consultarUno("SELECT * FROM empleado WHERE id = ?", (id,))
            usuario = self._fabrica.usuario.obtenerPorId(fila["usuario_id"]) if fila["usuario_id"] else None
            comisionMedica = self._fabrica.comisionMedica.obtenerPorId(fila["comision_medica_id"])
            self._cache[id] = Empleado(fila["nombre"], fila["apellido"], fila["email"],
                                       usuario, comisionMedica, id=fila["id"])
        return self._cache[id]

    def obtenerTodos(self) -> list[Empleado]:
        filas = self._conexion.consultar("SELECT id FROM empleado ORDER BY id")
        return [self.obtenerPorId(fila["id"]) for fila in filas]
