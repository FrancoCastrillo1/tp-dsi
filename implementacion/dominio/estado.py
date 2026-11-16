"""Clase Estado: estados posibles de Bolsin, Remito y Documentacion, según su ámbito."""


class Estado:
    # Ámbitos
    AMBITO_BOLSIN = "Bolsin"
    AMBITO_REMITO = "Remito"
    AMBITO_DOCUMENTACION = "Documentacion"

    # Nombres de estados (los estados se persisten como datos, estos son sus nombres)
    CREADO = "Creado"
    CERRADO = "Cerrado"
    ENVIADO = "Enviado"
    RECIBIDO_EN_CM_DESTINO = "Recibido en CM destino"
    REGISTRADA = "Registrada"
    EN_REMITO = "En remito"
    EN_BOLSIN_SALIENTE = "En bolsín saliente"
    EN_BOLSIN_ENVIADO = "En bolsín enviado"
    RECIBIDO_Y_ACEPTADO = "Recibido y Aceptado"
    RECIBIDO_Y_ACEPTADO_PARCIAL = "Recibido y Aceptado Parcial"
    RECIBIDA_Y_ACEPTADA = "Recibida y Aceptada"
    RECIBIDA_Y_RECHAZADA = "Recibida y Rechazada"
    NO_RECIBIDA = "No recibida"
    PARA_REDIRIGIR = "Para redirigir"
    DE_BAJA = "De baja"

    def __init__(self, nombre: str, descripcion: str, ambito: str, id: int | None = None):
        self.id = id
        self.nombre = nombre
        self.descripcion = descripcion
        self.ambito = ambito

    def getNombre(self) -> str:
        return self.nombre

    def getDescripcion(self) -> str:
        return self.descripcion

    def getAmbito(self) -> str:
        return self.ambito

    # --- Ámbitos ---
    def esAmbitoBolsin(self) -> bool:
        return self.ambito == Estado.AMBITO_BOLSIN

    def esAmbitoRemito(self) -> bool:
        return self.ambito == Estado.AMBITO_REMITO

    def esAmbitoDocumentacion(self) -> bool:
        return self.ambito == Estado.AMBITO_DOCUMENTACION

    # --- Estados ---
    def esRegistrada(self) -> bool:
        return self.nombre == Estado.REGISTRADA

    def esEnRemito(self) -> bool:
        return self.nombre == Estado.EN_REMITO

    def esEnBolsinSaliente(self) -> bool:
        return self.nombre == Estado.EN_BOLSIN_SALIENTE

    def esEnBolsinEnviado(self) -> bool:
        return self.nombre == Estado.EN_BOLSIN_ENVIADO

    def esNoRecibida(self) -> bool:
        return self.nombre == Estado.NO_RECIBIDA

    def esDadaDeBaja(self) -> bool:
        return self.nombre == Estado.DE_BAJA

    def esRecibidaYRechazada(self) -> bool:
        return self.nombre == Estado.RECIBIDA_Y_RECHAZADA

    def esRecibidaYAceptada(self) -> bool:
        return self.nombre == Estado.RECIBIDA_Y_ACEPTADA

    def esParaRedirigir(self) -> bool:
        return self.nombre == Estado.PARA_REDIRIGIR

    def esEnviado(self) -> bool:
        return self.nombre == Estado.ENVIADO

    def esRecibidoEnCMDestino(self) -> bool:
        return self.nombre == Estado.RECIBIDO_EN_CM_DESTINO

    def esRecibidoYAceptado(self) -> bool:
        return self.nombre == Estado.RECIBIDO_Y_ACEPTADO

    def esRecibidoYAceptadoParcial(self) -> bool:
        return self.nombre == Estado.RECIBIDO_Y_ACEPTADO_PARCIAL

    def __repr__(self) -> str:
        return f"Estado({self.ambito}: {self.nombre})"
