from dominio.comision_medica import ComisionMedica
from dominio.usuario import Usuario


class Empleado:

    def __init__(self, nombre: str, apellido: str, email: str, usuario: Usuario | None,
                 comisionMedica: ComisionMedica, id: int | None = None):
        self.id = id
        self.nombre = nombre
        self.apellido = apellido
        self.email = email
        self.usuario = usuario
        self.comisionMedica = comisionMedica

    def getCM(self) -> ComisionMedica:
        return self.comisionMedica

    def esTuUsuario(self, usuario: Usuario) -> bool:
        return self.usuario is not None and self.usuario.getNombre() == usuario.getNombre()

    def getNombreCompleto(self) -> str:
        return f"{self.nombre} {self.apellido}"
