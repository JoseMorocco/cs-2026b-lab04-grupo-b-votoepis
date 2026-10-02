# Matriz de Decisión - VotoEPIS

## 1. Alternativas Evaluadas
A partir del análisis generado con apoyo de IA y la crítica adversarial, se evaluaron las siguientes alternativas arquitectónicas:
* **A. Monolito en capas:** Una sola aplicación organizada en capas de presentación, lógica y datos. Utiliza una base de datos relacional y concentra el despliegue en una única aplicación.
* **B. Monolito modular hexagonal con registro de eventos inmutable:** Mantiene un único despliegue, pero separa los módulos del dominio mediante puertos y adaptadores. Incorpora un registro de eventos con hash encadenado.
* **C. Serverless / BaaS:** Utiliza funciones administradas y servicios de backend gestionados para implementar los casos de uso.

## 2. Criterios y Pesos
Los criterios se derivan directamente de los drivers identificados en el proyecto:

| Criterio | Peso | Justificación |
| :--- | :--- | :--- |
| Seguridad e integridad | 30 % | QA-01: Es el atributo crítico del sistema. |
| Tiempo de implementación | 25 % | R-01: El MVP debe estar en producción en un máximo de 1 mes. |
| Mantenibilidad | 20 % | QA-04: El sistema debe poder modificarse sin afectar todo su funcionamiento. |
| Complejidad operativa | 15 % | R-02 y R-03: El equipo es pequeño (3 integrantes) y debe usar tecnologías conocidas. |
| Costo | 10 % | R-04: El presupuesto disponible es bajo (VPS económico). |

## 3. Matriz de Decisión Ponderada
Los puntajes (escala 1 a 5) fueron asignados por el equipo tras la evaluación crítica, priorizando las restricciones de tiempo y tamaño del equipo.

| Criterio | Peso | A: Monolito en capas | B: Monolito Hexagonal | C: Serverless / BaaS |
| :--- | :--- | :--- | :--- | :--- |
| Seguridad e integridad | 30 % | 4 | 5 | 3 |
| Tiempo de implementación | 25 % | 5 | 2 | 4 |
| Mantenibilidad | 20 % | 3 | 5 | 3 |
| Complejidad operativa | 15 % | 5 | 2 | 4 |
| Costo | 10 % | 5 | 4 | 4 |
| **Total ponderado** | **100 %** | **4.30** | **3.70** | **3.50** |

## 4. Decisión Final
**Alternativa seleccionada: Alternativa A (Monolito en capas)**

**Justificación:**
Aunque la arquitectura hexagonal (Alternativa B) ofrece ventajas teóricas en mantenibilidad y auditoría profunda, el **Monolito en capas** es la opción técnica más viable. Es la única que garantiza el cumplimiento estricto del plazo de un mes para el MVP (R-01) y minimiza la complejidad operativa para el equipo de tres personas (R-02), logrando un balance sólido y suficiente para cumplir con la seguridad del proceso electoral (QA-01).



