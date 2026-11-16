class TipoDocumentacion:

    def __init__(self, nombre: str, descripcion: str, id: int | None = None):
        self.id = id
        self.nombre = nombre
        self.descripcion = descripcion

    def getNombre(self) -> str:
        return self.nombre
