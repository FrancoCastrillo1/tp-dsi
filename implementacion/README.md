# CU 28 – Registrar recepción de bolsín

Implementación en Python del CU 28 diseñado con el patrón **Iterator (Gamma)**, con interfaz web (Flask) y persistencia por **DAOs** sobre SQLite.

## Ejecutar

```bash
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python app.py               # http://127.0.0.1:5000
.venv\Scripts\python app.py --reiniciar   # recrea bolsines.db con los datos de prueba
.venv\Scripts\python -m pytest            # tests
```

La sesión es fija y precargada: Encargado de Bolsines **Laura Fernández**, de la *Comisión Médica Córdoba* (usuario `eb.cordoba`).

## Estructura

| Carpeta | Contenido |
|---|---|
| `iterador/` | `IIterador`, `IAgregado`, `IteradorBolsin` (filtra en `comprobarFiltros()`), `IteradorRemito`, `IteradorDetalleRemito` |
| `dominio/` | Entidades del diagrama de clases. `Bolsin` y `Remito` son agregados concretos |
| `control/` | `GestorDeBolsin`: controlador del CU y agregado concreto que crea `IteradorBolsin` |
| `boundary/` | `PantallaDeEB` y las plantillas HTML |
| `persistencia/` | `Conexion`, esquema SQL, DAOs, `FabricaDAO` y datos de prueba |
| `interfaces/` | `InterfazServidorCorreo`: stub del CU 29 que solo escribe en el log |

## Decisiones de implementación

- **Filtro de bolsines.** Respeta el diagrama de secuencia: `esTuCMOrigen(cm)` compara contra la CM **origen** del bolsín. Por eso se listan los bolsines *Enviados* cuya CM origen es la del usuario logueado.
- **Opciones de recepción.** En las opciones 2, 3 y 4 el EB marca la documentación afectada, y el resto pasa a *Recibida y Aceptada*. Según la máquina de estados de Documentacion:
  - Opción 2: *No recibida*.
  - Opciones 3 y 4: *Recibida y Rechazada*. El pasaje a *Para redirigir* corresponde al CU 31.
- **Estado del remito.** Queda en *Recibido y Aceptado Parcial* si tiene al menos una documentación afectada; si no, en *Recibido y Aceptado*.
- **Responsable.** Se agregó el atributo `responsable: Empleado` a `CambioDeEstadoBolsin` y `CambioDeEstadoDocumentacion`. `Remito` mantiene su `Estado` directo, sin historial.
- **Agregados respecto del diagrama:**
  - El estado *Recibido y Aceptado Parcial* (`esRecibidoYAceptadoParcial()`).
  - Los métodos del gestor `buscarRemitosAceptadosParcial()` y `buscarEstadoDocumentacionAfectada()`.
  - Los métodos de `DetalleRemito` `rechazarDoc()` y `registrarNoRecepcionDoc()`.
  - Un atributo `id` en las entidades, usado como identidad de persistencia.
- **Nombres.** Se usaron los del diagrama de clases en camelCase, corrigiendo errores de tipeo evidentes. Por ejemplo, `buscarCMdeUsariosLogueados` pasó a `buscarCMdeUsuarioLogueado` y `esRecibidaRechazadae` a `esRecibidaYRechazada`.
