"""Datos de prueba para ejecutar el CU 28.

La sesión fija precargada es la del Encargado de Bolsines de la CM Córdoba (usuario "eb.cordoba").
Como IteradorBolsin filtra con esTuCMOrigen(), se listan los bolsines Enviados cuya CM origen es Córdoba.
"""
from datetime import datetime, timedelta
from pathlib import Path

from dominio.estado import Estado as E
from persistencia.conexion import Conexion

ESTADOS = [
    # (nombre, descripcion, ambito)
    (E.CREADO, "Bolsín registrado, todavía abierto", E.AMBITO_BOLSIN),
    (E.CERRADO, "Bolsín cerrado con precinto", E.AMBITO_BOLSIN),
    (E.ENVIADO, "Bolsín retirado por el correo", E.AMBITO_BOLSIN),
    (E.RECIBIDO_EN_CM_DESTINO, "Bolsín recibido en la CM destino", E.AMBITO_BOLSIN),
    (E.DE_BAJA, "Bolsín eliminado", E.AMBITO_BOLSIN),

    (E.CREADO, "Remito generado", E.AMBITO_REMITO),
    (E.EN_BOLSIN_SALIENTE, "Remito incluido en un bolsín", E.AMBITO_REMITO),
    (E.EN_BOLSIN_ENVIADO, "Remito en un bolsín retirado por el correo", E.AMBITO_REMITO),
    (E.RECIBIDO_Y_ACEPTADO, "Remito recibido con toda su documentación aceptada", E.AMBITO_REMITO),
    (E.RECIBIDO_Y_ACEPTADO_PARCIAL, "Remito recibido con documentación no aceptada", E.AMBITO_REMITO),

    (E.REGISTRADA, "Documentación registrada", E.AMBITO_DOCUMENTACION),
    (E.EN_REMITO, "Documentación incluida en un remito", E.AMBITO_DOCUMENTACION),
    (E.EN_BOLSIN_SALIENTE, "Documentación en un bolsín saliente", E.AMBITO_DOCUMENTACION),
    (E.EN_BOLSIN_ENVIADO, "Documentación en un bolsín enviado", E.AMBITO_DOCUMENTACION),
    (E.RECIBIDA_Y_ACEPTADA, "Documentación recibida y aceptada", E.AMBITO_DOCUMENTACION),
    (E.RECIBIDA_Y_RECHAZADA, "Documentación recibida que no corresponde", E.AMBITO_DOCUMENTACION),
    (E.NO_RECIBIDA, "Documentación que no llegó en el bolsín", E.AMBITO_DOCUMENTACION),
    (E.PARA_REDIRIGIR, "Documentación a redirigir a un área de la CMC", E.AMBITO_DOCUMENTACION),
    (E.DE_BAJA, "Documentación dada de baja", E.AMBITO_DOCUMENTACION),
]

COMISIONES = [
    # (nombre, direccion, email, telefono)
    ("Comisión Médica Córdoba", "Av. Colón 1234, Córdoba", "cm.cordoba@organismo.gob.ar", "0351-4000000"),
    ("Comisión Médica Rosario", "Bv. Oroño 456, Rosario", "cm.rosario@organismo.gob.ar", "0341-4000000"),
    ("Comisión Médica Mendoza", "Av. San Martín 789, Mendoza", "cm.mendoza@organismo.gob.ar", "0261-4000000"),
    ("Comisión Médica Central", "Florida 100, C.A.B.A.", "cmc@organismo.gob.ar", "011-40000000"),
    ("Comisión Médica Villa María", "Bv. España 321, Villa María", "cm.villamaria@organismo.gob.ar", "0353-4000000"),
]

TIPOS = [
    ("Expediente", "Expediente administrativo"),
    ("Dictamen", "Dictamen médico"),
    ("Estudio médico", "Estudio o informe médico"),
    ("Carta documento", "Carta documento"),
]

# (numero, asunto, tipo, cm origen)
DOCUMENTACION = [
    (1, "Expediente de incapacidad laboral - Pérez, Juan", "Expediente", "Comisión Médica Córdoba"),
    (2, "Dictamen de junta médica - Gómez, Ana", "Dictamen", "Comisión Médica Córdoba"),
    (3, "Resonancia magnética - Díaz, Carlos", "Estudio médico", "Comisión Médica Córdoba"),
    (4, "Carta documento - Rechazo de siniestro", "Carta documento", "Comisión Médica Córdoba"),
    (5, "Expediente de reingreso - López, María", "Expediente", "Comisión Médica Córdoba"),
    (6, "Dictamen de divergencia - Sosa, Pedro", "Dictamen", "Comisión Médica Córdoba"),
    (7, "Radiografía de columna - Ruiz, Laura", "Estudio médico", "Comisión Médica Córdoba"),
    (8, "Expediente de apelación - Torres, Luis", "Expediente", "Comisión Médica Córdoba"),
    (9, "Dictamen de alta - Molina, Sofía", "Dictamen", "Comisión Médica Córdoba"),
    (10, "Expediente de homologación - Vera, Raúl", "Expediente", "Comisión Médica Rosario"),
]

# (numero, cm origen, cm destino, precinto, peso, estado actual, [(nro remito, [nros documentacion])])
BOLSINES = [
    (101, "Comisión Médica Córdoba", "Comisión Médica Central", 5001, 850.0, E.ENVIADO,
     [(1001, [1, 2]), (1002, [3])]),
    (102, "Comisión Médica Córdoba", "Comisión Médica Rosario", 5002, 420.5, E.ENVIADO,
     [(1003, [4, 5])]),
    (103, "Comisión Médica Córdoba", "Comisión Médica Mendoza", 5003, 1200.0, E.ENVIADO,
     [(1004, [6]), (1005, [7, 8])]),
    (104, "Comisión Médica Córdoba", "Comisión Médica Villa María", 5004, 300.0, E.CERRADO,
     [(1006, [9])]),
    (105, "Comisión Médica Rosario", "Comisión Médica Córdoba", 6001, 500.0, E.ENVIADO,
     [(1007, [10])]),
]

FECHA_BASE = datetime(2026, 11, 10, 9, 0)


def cargarDatosSemilla(conexion: Conexion) -> None:
    with conexion.transaccion():
        ids_estado = {}
        for nombre, descripcion, ambito in ESTADOS:
            ids_estado[(nombre, ambito)] = conexion.ejecutar(
                "INSERT INTO estado (nombre, descripcion, ambito) VALUES (?, ?, ?)", (nombre, descripcion, ambito))

        ids_cm = {}
        for nombre, direccion, email, telefono in COMISIONES:
            ids_cm[nombre] = conexion.ejecutar(
                "INSERT INTO comision_medica (nombre, direccion, email, telefono) VALUES (?, ?, ?, ?)",
                (nombre, direccion, email, telefono))

        ids_tipo = {}
        for nombre, descripcion in TIPOS:
            ids_tipo[nombre] = conexion.ejecutar(
                "INSERT INTO tipo_documentacion (nombre, descripcion) VALUES (?, ?)", (nombre, descripcion))

        id_usr_cba = conexion.ejecutar("INSERT INTO usuario (nombre, password) VALUES (?, ?)", ("eb.cordoba", "1234"))
        id_usr_ros = conexion.ejecutar("INSERT INTO usuario (nombre, password) VALUES (?, ?)", ("eb.rosario", "1234"))
        id_emp_cba = conexion.ejecutar(
            "INSERT INTO empleado (nombre, apellido, email, usuario_id, comision_medica_id) VALUES (?, ?, ?, ?, ?)",
            ("Laura", "Fernández", "lfernandez@organismo.gob.ar", id_usr_cba, ids_cm["Comisión Médica Córdoba"]))
        id_emp_ros = conexion.ejecutar(
            "INSERT INTO empleado (nombre, apellido, email, usuario_id, comision_medica_id) VALUES (?, ?, ?, ?, ?)",
            ("Martín", "Acosta", "macosta@organismo.gob.ar", id_usr_ros, ids_cm["Comisión Médica Rosario"]))
        empleado_por_cm = {"Comisión Médica Córdoba": id_emp_cba, "Comisión Médica Rosario": id_emp_ros}

        # Sesión fija precargada del EB de Córdoba
        conexion.ejecutar("INSERT INTO sesion (usuario_id, fecha_hora_inicio) VALUES (?, ?)",
                          (id_usr_cba, datetime(2026, 11, 16, 8, 0).isoformat()))

        ids_doc = {}
        for numero, asunto, tipo, cm_origen in DOCUMENTACION:
            ids_doc[numero] = conexion.ejecutar(
                "INSERT INTO documentacion (numero, asunto, fecha_pase, tipo_documentacion_id, "
                "comision_medica_origen_id) VALUES (?, ?, ?, ?, ?)",
                (numero, asunto, FECHA_BASE.date().isoformat(), ids_tipo[tipo], ids_cm[cm_origen]))

        for numero, cm_origen, cm_destino, precinto, peso, estado_actual, remitos in BOLSINES:
            responsable = empleado_por_cm[cm_origen]
            id_bolsin = conexion.ejecutar(
                "INSERT INTO bolsin (numero_bolsin, fecha, peso, numero_precinto, comision_medica_origen_id, "
                "comision_medica_destino_id) VALUES (?, ?, ?, ?, ?, ?)",
                (numero, FECHA_BASE.date().isoformat(), peso, precinto, ids_cm[cm_origen], ids_cm[cm_destino]))

            estados_bolsin = [E.CREADO, E.CERRADO] + ([E.ENVIADO] if estado_actual == E.ENVIADO else [])
            _insertarHistorial(conexion, "cambio_estado_bolsin", "bolsin_id", id_bolsin,
                               [ids_estado[(e, E.AMBITO_BOLSIN)] for e in estados_bolsin], responsable)

            enviado = estado_actual == E.ENVIADO
            estado_remito = E.EN_BOLSIN_ENVIADO if enviado else E.EN_BOLSIN_SALIENTE
            for nro_remito, nros_doc in remitos:
                id_remito = conexion.ejecutar(
                    "INSERT INTO remito (numero, fecha, estado_id, bolsin_id) VALUES (?, ?, ?, ?)",
                    (nro_remito, FECHA_BASE.date().isoformat(), ids_estado[(estado_remito, E.AMBITO_REMITO)],
                     id_bolsin))
                for nro_doc in nros_doc:
                    conexion.ejecutar("INSERT INTO detalle_remito (remito_id, documentacion_id) VALUES (?, ?)",
                                      (id_remito, ids_doc[nro_doc]))
                    estados_doc = [E.REGISTRADA, E.EN_REMITO, E.EN_BOLSIN_SALIENTE] + \
                                  ([E.EN_BOLSIN_ENVIADO] if enviado else [])
                    _insertarHistorial(conexion, "cambio_estado_documentacion", "documentacion_id",
                                       ids_doc[nro_doc],
                                       [ids_estado[(e, E.AMBITO_DOCUMENTACION)] for e in estados_doc],
                                       responsable)


def _insertarHistorial(conexion: Conexion, tabla: str, columna: str, id_objeto: int,
                       ids_estados: list[int], responsable: int) -> None:
    """Inserta una cadena de cambios de estado: cada uno termina cuando empieza el siguiente."""
    for i, id_estado in enumerate(ids_estados):
        inicio = FECHA_BASE + timedelta(hours=6 * i)
        fin = FECHA_BASE + timedelta(hours=6 * (i + 1)) if i < len(ids_estados) - 1 else None
        conexion.ejecutar(
            f"INSERT INTO {tabla} ({columna}, estado_id, fecha_hora_inicio, fecha_hora_fin, responsable_id) "
            "VALUES (?, ?, ?, ?, ?)",
            (id_objeto, id_estado, inicio.isoformat(), fin.isoformat() if fin else None, responsable))


def inicializarBaseDeDatos(rutaBaseDatos: str, reiniciar: bool = False) -> None:
    """Crea la base con el esquema y los datos de prueba si no existe (o si se pide reiniciarla)."""
    ruta = Path(rutaBaseDatos)
    if reiniciar and ruta.exists():
        ruta.unlink()
    existia = ruta.exists()
    conexion = Conexion(str(ruta))
    try:
        if not existia:
            conexion.crearEsquema()
            cargarDatosSemilla(conexion)
    finally:
        conexion.cerrar()
