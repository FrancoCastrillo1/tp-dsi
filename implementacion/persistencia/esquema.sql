-- Esquema de base de datos (SQLite) para el CU 28 - Registrar recepción de bolsín.

CREATE TABLE IF NOT EXISTS comision_medica (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre    TEXT NOT NULL UNIQUE,
    direccion TEXT,
    email     TEXT,
    telefono  TEXT
);

CREATE TABLE IF NOT EXISTS estado (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre      TEXT NOT NULL,
    descripcion TEXT,
    ambito      TEXT NOT NULL,
    UNIQUE (nombre, ambito)
);

CREATE TABLE IF NOT EXISTS usuario (
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre   TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS sesion (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id        INTEGER NOT NULL REFERENCES usuario(id),
    fecha_hora_inicio TEXT NOT NULL,
    fecha_hora_fin    TEXT
);

CREATE TABLE IF NOT EXISTS empleado (
    id                 INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre             TEXT NOT NULL,
    apellido           TEXT NOT NULL,
    email              TEXT,
    usuario_id         INTEGER REFERENCES usuario(id),
    comision_medica_id INTEGER NOT NULL REFERENCES comision_medica(id)
);

CREATE TABLE IF NOT EXISTS tipo_documentacion (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre      TEXT NOT NULL UNIQUE,
    descripcion TEXT
);

CREATE TABLE IF NOT EXISTS documentacion (
    id                        INTEGER PRIMARY KEY AUTOINCREMENT,
    numero                    INTEGER NOT NULL UNIQUE,
    asunto                    TEXT NOT NULL,
    fecha_pase                TEXT NOT NULL,
    tipo_documentacion_id     INTEGER NOT NULL REFERENCES tipo_documentacion(id),
    comision_medica_origen_id INTEGER NOT NULL REFERENCES comision_medica(id)
);

CREATE TABLE IF NOT EXISTS cambio_estado_documentacion (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    documentacion_id  INTEGER NOT NULL REFERENCES documentacion(id),
    estado_id         INTEGER NOT NULL REFERENCES estado(id),
    fecha_hora_inicio TEXT NOT NULL,
    fecha_hora_fin    TEXT,
    responsable_id    INTEGER REFERENCES empleado(id)
);

CREATE TABLE IF NOT EXISTS bolsin (
    id                         INTEGER PRIMARY KEY AUTOINCREMENT,
    numero_bolsin              INTEGER NOT NULL UNIQUE,
    fecha                      TEXT NOT NULL,
    peso                       REAL NOT NULL,
    numero_precinto            INTEGER,
    comision_medica_origen_id  INTEGER NOT NULL REFERENCES comision_medica(id),
    comision_medica_destino_id INTEGER NOT NULL REFERENCES comision_medica(id)
);

CREATE TABLE IF NOT EXISTS cambio_estado_bolsin (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    bolsin_id         INTEGER NOT NULL REFERENCES bolsin(id),
    estado_id         INTEGER NOT NULL REFERENCES estado(id),
    fecha_hora_inicio TEXT NOT NULL,
    fecha_hora_fin    TEXT,
    responsable_id    INTEGER REFERENCES empleado(id)
);

CREATE TABLE IF NOT EXISTS remito (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    numero    INTEGER NOT NULL UNIQUE,
    fecha     TEXT NOT NULL,
    estado_id INTEGER NOT NULL REFERENCES estado(id),
    bolsin_id INTEGER REFERENCES bolsin(id)
);

CREATE TABLE IF NOT EXISTS detalle_remito (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    remito_id        INTEGER NOT NULL REFERENCES remito(id),
    documentacion_id INTEGER NOT NULL REFERENCES documentacion(id),
    area_cmc_destino TEXT
);
