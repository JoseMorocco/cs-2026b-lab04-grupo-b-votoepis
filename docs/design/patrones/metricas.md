# E6 — Métricas de Refactorización y Análisis de Trade-off (VotoEPIS)

## 1. Comparación de Complejidad Ciclomática (`radon cc -s -a`) y Tamaño (`radon raw -s`)

Se midió el módulo `src/votacion` en tres momentos: la versión inicial ingenua (`antes/servicio.py`), el primer corte tras introducir `Strategy + Adapter + Factory` (E2), y el diseño final completo con los 7 patrones integrados (E2–E5: `servicio.py`, `elegibilidad.py`, `estados.py`, `decoradores.py`, `eventos.py` e `ia.py`).

### Tabla Resumen Antes vs. Después

| Métrica | Versión Antes (`antes/servicio.py`) | Corte E2 (`servicio.py` + `elegibilidad.py`) | Versión Final Refactorizada (E2–E5) | Variación (Antes → Final) |
|---|---|---|---|---|
| **Complejidad de `emitir_voto()`** | **18 (C)** — Riesgo moderado/alto | **13 (C)** | **4 (A)** (y máx. **4 (A)** en cualquier método) | **-14 puntos (-77.8 %)** |
| **Complejidad de la clase `ServicioVotacion`** | **11 (C)** | **9 (B)** | **2 (A)** | **-9 puntos (-81.8 %)** |
| **Complejidad ciclomática promedio** | **10.00 (B)** (3 bloques) | **2.92 (A)** (13 bloques) | **1.68 (A)** (57 bloques) | **-8.32 puntos (-83.2 %)** |
| **Líneas de código fuente (SLOC)** | **73 SLOC** (94 LOC) | **113 SLOC** (154 LOC) | **259 SLOC** (360 LOC) | **+186 SLOC (+254.8 %)** |
| **Líneas lógicas (LLOC)** | **53 LLOC** | **77 LLOC** | **185 LLOC** | **+132 LLOC** |
| **Archivos de implementación** | **1 archivo** | **2 archivos** | **6 archivos** | **+5 archivos** |
| **Métodos a modificar en `ServicioVotacion` para nueva fuente** | **1 (`emitir_voto`)** | **0 (Open/Closed)** | **0 (Open/Closed)** | **Cumple OCP** |

---

### Detalle de Complejidad Ciclomática por Módulo (Versión Final)

| Archivo | Clase / Método principal | Complejidad (`radon cc`) | Clasificación | Rol / Patrón GoF |
|---|---|---|---|---|
| `antes/servicio.py` | `ServicioVotacion.emitir_voto` | 18 | **C** | Versión monolítica sin patrones |
| `servicio.py` | `ServicioVotacion.emitir_voto` | 4 | **A** | Cliente orquestador del flujo |
| `servicio.py` | `ServicioVotacion._solicitud_valida` | 4 | **A** | Validación previa extraída (SRP) |
| `servicio.py` | `ServicioVotacion._registrar_o_auditar` | 3 | **A** | Persistencia y disparo de eventos |
| `elegibilidad.py` | `PadronLocalAdapter` / `SistemaAcademicoAdapter` | 2 / 2 | **A** | `<<Adapter>>` / `<<Strategy>>` |
| `elegibilidad.py` | `FabricaFuentes.crear` | 2 | **A** | `<<Factory>>` basada en registro |
| `decoradores.py` | `ConReintentos.esta_habilitado` | 4 | **A** | `<<Decorator>>` de tolerancia a fallos |
| `estados.py` | `Configurada.abrir` / `Escrutada.publicar_resultados` | 3 / 3 | **A** | `<<State>>` del ciclo electoral |
| `eventos.py` | `PublicadorEventos.publicar` / `ConfirmacionCorreo.actualizar` | 2 / 3 | **A** | `<<Observer>>` de auditoría y correo |
| `ia.py` | `ConCache.completar` / `Guardrail.validar` | 2 / 2 | **A** | `<<Decorator>>` y `<<Chain of Responsibility>>` |

---

## 2. Análisis del Trade-off (5 a 8 líneas)

Con la refactorización ganamos que ningún método del sistema supere una complejidad ciclomática de **4 (rango A)** —bajando `emitir_voto()` de **18 (C)** a **4 (A)** y el promedio global de **10.0 (B)** a **1.68 (A)**—, eliminando los condicionales por proveedor y aislando los reintentos, notificaciones, estados y guardrails de IA en unidades probables sin red ni claves de API. Además, incorporar una nueva fuente de habilitación, un nuevo suscriptor de auditoría o un nuevo guardrail ya no requiere modificar `ServicioVotacion` (principio Abierto/Cerrado). A cambio, el costo real fue triplicar el tamaño del código (de **73 a 259 SLOC**) y pasar de **1 a 6 archivos**, introduciendo mayor indirección que exige que todo el equipo comprenda los contratos e interfaces. Si VotoEPIS fuera a operar únicamente con un padrón local fijo, sin integración con el Sistema Académico UNSA, sin reglas de reintento ante *timeouts* y sin asistente de IA, la versión `antes/servicio.py` de 73 líneas habría sido suficiente y más rápida de mantener.

---

## 3. Patrones Rechazados y Justificación

1. **Abstract Factory (Rechazado):**
   * **Motivo:** La IA sugirió crear una jerarquía de fábricas abstractas para instanciar familias de conectores electorales (padrón + validador + auditor por cada origen). Sin embargo, VotoEPIS solo necesita resolver una única variación (el puerto `PadronPort`) y el resto del flujo es común. Una `FabricaFuentes` basada en un diccionario de registro (`dict[str, Callable]`) cumple el principio Abierto/Cerrado con 15 líneas y sin clases redundantes.
2. **Singleton en `FabricaFuentes` y `PublicadorEventos` (Rechazado):**
   * **Motivo:** Convertir la fábrica o el publicador de eventos en un `Singleton` introduce estado global compartido entre pruebas, impidiendo inyectar dobles de prueba aislados (`PadronLocalSimulado`, `CorreoSimulado`, `ClienteLLMFalso`) en paralelo durante la ejecución de `pytest`. Se optó por inyección de dependencias en el constructor de `ServicioVotacion`.