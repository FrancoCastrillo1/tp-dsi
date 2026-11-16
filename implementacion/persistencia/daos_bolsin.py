"""DAOs de Bolsin, Remito (con sus DetalleRemito) y Documentacion (con sus cambios de estado)."""
from __future__ import annotations

from dominio.bolsin import Bolsin
from dominio.cambio_de_estado_bolsin import CambioDeEstadoBolsin
from dominio.cambio_de_estado_documentacion import CambioDeEstadoDocumentacion
from dominio.detalle_remito import DetalleRemito
from dominio.documentacion import Documentacion
from dominio.remito import Remito
from persistencia.conexion import aFecha, aFechaHora, aTexto
from persistencia.daos_soporte import DAOBase


class DocumentacionDAO(DAOBase):

    def obtenerPorId(self, id: int) -> Documentacion:
        if id not in self._cache:
            fila = self._conexion.consultarUno("SELECT * FROM documentacion WHERE id = ?", (id,))
            self._cache[id] = Documentacion(
                numero=fila["numero"],
                asunto=fila["asunto"],
                fechaPase=aFecha(fila["fecha_pase"]),
                tipoDocumentacion=self._fabrica.tipoDocumentacion.obtenerPorId(fila["tipo_documentacion_id"]),
                comisionMedicaOrigen=self._fabrica.comisionMedica.obtenerPorId(fila["comision_medica_origen_id"]),
                cambiosEstado=self._obtenerCambiosEstado(id),
                id=fila["id"],
            )
        return self._cache[id]

    def _obtenerCambiosEstado(self, documentacionId: int) -> list[CambioDeEstadoDocumentacion]:
        filas = self._conexion.consultar(
            "SELECT * FROM cambio_estado_documentacion WHERE documentacion_id = ? ORDER BY fecha_hora_inicio, id",
            (documentacionId,),
        )
        return [
            CambioDeEstadoDocumentacion(
                fechaHoraInicio=aFechaHora(fila["fecha_hora_inicio"]),
                estado=self._fabrica.estado.obtenerPorId(fila["estado_id"]),
                responsable=self._fabrica.empleado.obtenerPorId(fila["responsable_id"]) if fila["responsable_id"] else None,
                fechaHoraFin=aFechaHora(fila["fecha_hora_fin"]),
                id=fila["id"],
            )
            for fila in filas
        ]

    def actualizar(self, documentacion: Documentacion) -> None:
        """Inserta los cambios de estado nuevos y actualiza la fecha de fin de los existentes."""
        for cambioEstado in documentacion.cambiosEstado:
            responsableId = cambioEstado.responsable.id if cambioEstado.responsable else None
            if cambioEstado.id is None:
                cambioEstado.id = self._conexion.ejecutar(
                    "INSERT INTO cambio_estado_documentacion "
                    "(documentacion_id, estado_id, fecha_hora_inicio, fecha_hora_fin, responsable_id) "
                    "VALUES (?, ?, ?, ?, ?)",
                    (documentacion.id, cambioEstado.estado.id, aTexto(cambioEstado.fechaHoraInicio),
                     aTexto(cambioEstado.fechaHoraFin), responsableId),
                )
            else:
                self._conexion.ejecutar(
                    "UPDATE cambio_estado_documentacion SET fecha_hora_fin = ? WHERE id = ?",
                    (aTexto(cambioEstado.fechaHoraFin), cambioEstado.id),
                )


class RemitoDAO(DAOBase):

    def obtenerPorBolsin(self, bolsinId: int) -> list[Remito]:
        filas = self._conexion.consultar(
            "SELECT * FROM remito WHERE bolsin_id = ? ORDER BY numero", (bolsinId,)
        )
        return [self._armarRemito(fila) for fila in filas]

    def _armarRemito(self, fila) -> Remito:
        if fila["id"] not in self._cache:
            self._cache[fila["id"]] = Remito(
                numero=fila["numero"],
                fecha=aFecha(fila["fecha"]),
                estado=self._fabrica.estado.obtenerPorId(fila["estado_id"]),
                detalles=self._obtenerDetalles(fila["id"]),
                id=fila["id"],
            )
        return self._cache[fila["id"]]

    def _obtenerDetalles(self, remitoId: int) -> list[DetalleRemito]:
        filas = self._conexion.consultar(
            "SELECT * FROM detalle_remito WHERE remito_id = ? ORDER BY id", (remitoId,)
        )
        return [
            DetalleRemito(
                documentacion=self._fabrica.documentacion.obtenerPorId(fila["documentacion_id"]),
                areaCMCDestino=fila["area_cmc_destino"],
                id=fila["id"],
            )
            for fila in filas
        ]

    def actualizar(self, remito: Remito) -> None:
        self._conexion.ejecutar(
            "UPDATE remito SET estado_id = ? WHERE id = ?", (remito.estado.id, remito.id)
        )
        for detalle in remito.detalles:
            self._conexion.ejecutar(
                "UPDATE detalle_remito SET area_cmc_destino = ? WHERE id = ?",
                (detalle.areaCMCDestino, detalle.id),
            )
            self._fabrica.documentacion.actualizar(detalle.documentacion)


class BolsinDAO(DAOBase):

    def obtenerTodos(self) -> list[Bolsin]:
        filas = self._conexion.consultar("SELECT * FROM bolsin ORDER BY numero_bolsin")
        return [self._armarBolsin(fila) for fila in filas]

    def obtenerPorNumero(self, numeroBolsin: int) -> Bolsin | None:
        fila = self._conexion.consultarUno("SELECT * FROM bolsin WHERE numero_bolsin = ?", (numeroBolsin,))
        return self._armarBolsin(fila) if fila else None

    def _armarBolsin(self, fila) -> Bolsin:
        if fila["id"] not in self._cache:
            self._cache[fila["id"]] = Bolsin(
                numeroBolsin=fila["numero_bolsin"],
                fecha=aFecha(fila["fecha"]),
                peso=fila["peso"],
                numeroPrecinto=fila["numero_precinto"],
                comisionMedicaOrigen=self._fabrica.comisionMedica.obtenerPorId(fila["comision_medica_origen_id"]),
                comisionMedicaDestino=self._fabrica.comisionMedica.obtenerPorId(fila["comision_medica_destino_id"]),
                cambiosEstado=self._obtenerCambiosEstado(fila["id"]),
                remitos=self._fabrica.remito.obtenerPorBolsin(fila["id"]),
                id=fila["id"],
            )
        return self._cache[fila["id"]]

    def _obtenerCambiosEstado(self, bolsinId: int) -> list[CambioDeEstadoBolsin]:
        filas = self._conexion.consultar(
            "SELECT * FROM cambio_estado_bolsin WHERE bolsin_id = ? ORDER BY fecha_hora_inicio, id",
            (bolsinId,),
        )
        return [
            CambioDeEstadoBolsin(
                fechaHoraInicio=aFechaHora(fila["fecha_hora_inicio"]),
                estado=self._fabrica.estado.obtenerPorId(fila["estado_id"]),
                responsable=self._fabrica.empleado.obtenerPorId(fila["responsable_id"]) if fila["responsable_id"] else None,
                fechaHoraFin=aFechaHora(fila["fecha_hora_fin"]),
                id=fila["id"],
            )
            for fila in filas
        ]

    def actualizar(self, bolsin: Bolsin) -> None:
        """Persiste los cambios de estado del bolsín y, en cascada, los de sus remitos y su documentación."""
        for cambioEstado in bolsin.cambiosEstado:
            responsableId = cambioEstado.responsable.id if cambioEstado.responsable else None
            if cambioEstado.id is None:
                cambioEstado.id = self._conexion.ejecutar(
                    "INSERT INTO cambio_estado_bolsin "
                    "(bolsin_id, estado_id, fecha_hora_inicio, fecha_hora_fin, responsable_id) "
                    "VALUES (?, ?, ?, ?, ?)",
                    (bolsin.id, cambioEstado.estado.id, aTexto(cambioEstado.fechaHoraInicio),
                     aTexto(cambioEstado.fechaHoraFin), responsableId),
                )
            else:
                self._conexion.ejecutar(
                    "UPDATE cambio_estado_bolsin SET fecha_hora_fin = ? WHERE id = ?",
                    (aTexto(cambioEstado.fechaHoraFin), cambioEstado.id),
                )
        for remito in bolsin.remitos:
            self._fabrica.remito.actualizar(remito)
