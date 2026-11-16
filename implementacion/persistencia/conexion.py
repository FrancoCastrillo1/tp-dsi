"""Manejo de la conexión a la base de datos SQLite."""
import sqlite3
from contextlib import contextmanager
from datetime import date, datetime
from pathlib import Path

RUTA_ESQUEMA = Path(__file__).with_name("esquema.sql")


class Conexion:

    def __init__(self, rutaBaseDatos: str):
        # check_same_thread=False: el gestor vive entre requests del servidor web.
        self._conexion = sqlite3.connect(rutaBaseDatos, check_same_thread=False)
        self._conexion.row_factory = sqlite3.Row
        self._conexion.execute("PRAGMA foreign_keys = ON")

    def consultar(self, sql: str, parametros: tuple = ()) -> list[sqlite3.Row]:
        return self._conexion.execute(sql, parametros).fetchall()

    def consultarUno(self, sql: str, parametros: tuple = ()) -> sqlite3.Row | None:
        return self._conexion.execute(sql, parametros).fetchone()

    def ejecutar(self, sql: str, parametros: tuple = ()) -> int:
        """Ejecuta una sentencia y devuelve el id de la última fila insertada."""
        return self._conexion.execute(sql, parametros).lastrowid

    @contextmanager
    def transaccion(self):
        """Confirma los cambios si el bloque termina bien; si falla, los deshace."""
        try:
            yield self
            self._conexion.commit()
        except Exception:
            self._conexion.rollback()
            raise

    def crearEsquema(self) -> None:
        self._conexion.executescript(RUTA_ESQUEMA.read_text(encoding="utf-8"))
        self._conexion.commit()

    def cerrar(self) -> None:
        self._conexion.close()


# --- Conversión de fechas entre Python y texto ISO de SQLite ---
def aTexto(valor: date | datetime | None) -> str | None:
    return valor.isoformat() if valor is not None else None


def aFechaHora(texto: str | None) -> datetime | None:
    return datetime.fromisoformat(texto) if texto else None


def aFecha(texto: str | None) -> date | None:
    return date.fromisoformat(texto) if texto else None
