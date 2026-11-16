class ComisionMedica:

    def __init__(self, nombre: str, direccion: str, email: str, telefono: str, id: int | None = None):
        self.id = id
        self.nombre = nombre
        self.direccion = direccion
        self.email = email
        self.telefono = telefono

    def getNombre(self) -> str:
        return self.nombre

    def getEmail(self) -> str:
        return self.email

    def __repr__(self) -> str:
        return f"ComisionMedica({self.nombre})"
