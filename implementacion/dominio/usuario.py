class Usuario:

    def __init__(self, nombre: str, password: str, id: int | None = None):
        self.id = id
        self.nombre = nombre
        self.password = password

    def getNombre(self) -> str:
        return self.nombre
