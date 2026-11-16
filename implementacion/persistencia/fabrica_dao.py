"""Punto de acceso a los DAOs. Cada instancia comparte una conexión y una caché de objetos."""
from persistencia.conexion import Conexion
from persistencia.daos_bolsin import BolsinDAO, DocumentacionDAO, RemitoDAO
from persistencia.daos_soporte import (ComisionMedicaDAO, EmpleadoDAO, EstadoDAO, SesionDAO,
                                       TipoDocumentacionDAO, UsuarioDAO)


class FabricaDAO:

    def __init__(self, conexion: Conexion):
        self.conexion = conexion
        self.comisionMedica = ComisionMedicaDAO(self)
        self.estado = EstadoDAO(self)
        self.tipoDocumentacion = TipoDocumentacionDAO(self)
        self.usuario = UsuarioDAO(self)
        self.sesion = SesionDAO(self)
        self.empleado = EmpleadoDAO(self)
        self.documentacion = DocumentacionDAO(self)
        self.remito = RemitoDAO(self)
        self.bolsin = BolsinDAO(self)

    def transaccion(self):
        return self.conexion.transaccion()
