# Lab 10 E6–E8
Objective: deliver E6, E7, and E8 for the Lab 10 agent system, with explicit user gates between stages.
Branch: `lab10-e6-e7-r8` | Delivery: `exception-ok` (one staged branch, no PR requested; forecast ~500 authored lines) | Tests: `python -m pytest -q agentes/pruebas_agente`; suite `python -m pytest -q tests/`

## Specs

### S1 — E6.1: Human approval for each agent edit

User requirement: “Activen aprobar_edicion en la política del ejecutor para que un integrante apruebe o rechace cada edición desde la consola, validando que la respuesta sea "s" o "n".”

Acceptance: Every agent edit is gated before the sandbox file is written; the console accepts only `s` or `n`; rejection leaves the file unchanged. An automated test proves the acceptance, rejection, and invalid-input behavior. Approval/rejection must be distinguishable in recorded trace evidence so E6.2 can refer to it.

Checks: focused `python -m pytest -q agentes/pruebas_agente`; full `python -m pytest -q tests/`.

### S2 — E6.2: Human roles and progressive delegation

User requirement: “En delegacion.md, definan para su caso los cuatro roles humanos (ejecutor, revisor, colaborador y gobernador): qué permisos tendría el agente en cada etapa y qué evidencia de las trazas justificaría pasar a la siguiente.”

Acceptance: `agentes/delegacion.md` defines the four named roles, the agent permissions at each stage, and concrete trace evidence for each progression decision, consistent with the implemented E6 approval and existing traces.

Checks: read back the document and compare its role/evidence table against the actual trace fields and test evidence.

### S3 — E7.1: Trace metrics and trajectory

User requirement: “En observacion.md, construyan una tabla con las métricas de las trazas de los 3 issues: pasos, rondas, herramientas usadas, decisiones rechazadas por el contrato, acciones bloqueadas y contexto final. Incluyan el diagrama de una trayectoria.”

Acceptance: The requested table covers all three issue traces and all six named metrics, and includes a trajectory diagram grounded in a real trace.

Checks: recompute each metric from the three trace files and compare the diagram to its source trace.

### S4 — E7.2: AI interaction log

User requirement: “Completen bitacora-ia.md con 5 o más interacciones con su asistente, incluyendo al menos un error del agente detectado por las pruebas, el contrato o el revisor.”

Acceptance: The log contains at least five evidenced assistant interactions and at least one agent error detected by a test, contract, or reviewer.

Checks: cross-check the interactions and cited error against repository tests, contracts, review notes, and trace evidence.

### S5 — E8.1: ADR-010

User requirement: “Redacten ADR-010: arquitectura del sistema agéntico: arquetipo, coordinación, herramientas, memoria, límites y rol humano elegidos, con alternativas descartadas y consecuencias.”

Acceptance: ADR-010 addresses each requested architecture dimension, discarded alternatives, and consequences, based on the implemented system.

Checks: read back the ADR and trace every decision to implementation or repository evidence.

### S6 — E8.2: README section

User requirement: “Agreguen al README.md la sección "Sistemas agénticos (Lab 10)" con la máquina de estados, un diagrama de trayectoria y la tabla de E7.”

Acceptance: README contains the exact named section, the state machine, one trajectory diagram, and the E7 metrics table.

Checks: read back the section and compare its diagram/table with the corresponding source artifacts.

### S7 — E8.3: Tag and submission

User requirement: “Creen la etiqueta v1.0-agentes y entreguen el enlace del repositorio en el Aula Virtual hasta el sábado 21/11/2026 a las 23:59.”

Acceptance: Create the requested tag after the approved E8 content is complete and provide the repository link for submission. Any Aula Virtual submission must use an explicitly authorized account/session for that destination.

Checks: verify the tag points to the intended completed commit and confirm the final repository URL. Submission remains gated on an authorized Aula Virtual session.

## Tasks

- T1 — S1–S2; route: inline; status: verified and pushed; commit: `be34c5873b8ef088bd18884e0aba70e880f457f6`; Risk: item 2 (human approval guard controls permission to edit the sandbox).
- T2 — S3–S4; route: inline; status: verified, commit pending; Risk: none (documentation and passive trace evidence only).
- T3 — S5–S7; route: inline; status: pending explicit user confirmation after E7; commit: pending.

## Log

### L1 — Original request

```text
https://github.com/JoseMorocco/cs-2026b-lab04-grupo-b-votoepis.git este es el repositorio a revisar quiero que lo clones y entiendas todo de que va mires todas las ramas y entiendas que pone despues aca en esta direccion de mi directorio /home/bunuelo/Descargas/CSLAB/Lab10 se encuentra el pdf del laboratorio10 el cual toca realizar ahora tienes que leer todo entener el ejercicio resuelto que es lo que hace para nuestro caso de ahora, luego revisa hay una carpeta alli hay pruebas y demas quiero que revises todo eso tmb E6. Humano en el circuito y delegación progresiva
1. Activen aprobar_edicion en la política del ejecutor para que un integrante apruebe o rechace cada edición
desde la consola, validando que la respuesta sea "s" o "n".
2. En delegacion.md, definan para su caso los cuatro roles humanos (ejecutor, revisor, colaborador y gobernador):
qué permisos tendría el agente en cada etapa y qué evidencia de las trazas justificaría pasar a la siguiente.
UNIVERSIDAD NACIONAL DE SAN AGUSTIN
FACULTAD DE INGENIERÍA DE PRODUCCIÓN Y SERVICIOS
ESCUELA PROFESIONAL DE INGENIERÍA DE SISTEMA
Formato: Guía de Práctica de Laboratorio / Talleres / Centros de Simulación
Aprobación: 2022/03/01
Código: GUIA-PRLD-001
Página: 19
E7. Observación y bitácora
1. En observacion.md, construyan una tabla con las métricas de las trazas de los 3 issues: pasos, rondas,
herramientas usadas, decisiones rechazadas por el contrato, acciones bloqueadas y contexto final. Incluyan el
diagrama de una trayectoria.
2. Completen bitacora-ia.md con 5 o más interacciones con su asistente, incluyendo al menos un error del
agente detectado por las pruebas, el contrato o el revisor.
E8. ADR, README y entrega
1. Redacten ADR-010: arquitectura del sistema agéntico: arquetipo, coordinación, herramientas,
memoria, límites y rol humano elegidos, con alternativas descartadas y consecuencias.
2. Agreguen al README.md la sección "Sistemas agénticos (Lab 10)" con la máquina de estados, un diagrama de
trayectoria y la tabla de E7.
3. Creen la etiqueta v1.0-agentes y entreguen el enlace del repositorio en el Aula Virtual hasta el sábado
21/11/2026 a las 23:59.
Reto opcional (+2 puntos, sin exced a mi me tica hacer esto, ahora usa agentes de otros modelos y realiza la actividades tu trabaja como el elefante con memoria y los demas como el epz dorado le indicas que tiene que hacer y tu auditas todo eso eres orquestador y verificador usas skills que hay para orquestador y verificador haz que los peces dorados tmb usen skills que haya adecuados para sus trabajos. son e6 e7 e8. Primero haras la parte e6 despues que todo este bien crea una rama nueva llamada lab10-e6-e7-r8 y alli subiras todo esto, entonces primero subes e6 con su respectivo commit, luego de eso me avisas que subiste el e6 luego que te confirme continuas con el e7 y asi sucesivamente. PUedes usar antigravity, opencode, gentle-shell y demas ias como agentes, ahora empieza hacer
```

### L2 — Verified baseline and branch inventory

OpenCode completed a read-only inspection. Parent spot-check confirmed the E6 PDF wording, the existing sandbox write chokepoint and trace behavior, and 35 remote refs. The E6 base recommendation is `main`; OpenCode's first report incorrectly generalized that all historical branches were ancestors of `main`. Its corrected addendum identifies three exceptions and was independently checked: `lab10-reto-opcional-a` (3 unique commits, orthogonal Lab 10 optional work), `lab07-reto-prueba-fallo` (2 unique commits, deliberate fitness-gate failure fixture), and `test/lab06-c4-invalido` (5 unique commits, net tree difference only regenerated PNG). Base clone remains clean. The OpenCode worktree has untracked `.atl/` registry files; its initial status was not captured, so they are left untouched.

### L3 — Current progress

Created local branch `lab10-e6-e7-r8` from `main`. Added the E6 approval regression tests, but E6 production implementation has not started. No commit or push exists. E7 and E8 remain explicitly gated by the user's confirmation after the preceding stage.

### L4 — Test environment blocker

The focused RED test could not run: `python` is not installed; `python3 -m pytest` reports pytest missing; `uv run --offline --with pytest --with jsonschema` reports pytest absent from cache; and system Python 3.12's `jsonschema` import fails because `rpds.rpds` is missing. No package was installed and no production code was changed. Await user authorization before downloading public test dependencies from PyPI into a temporary environment outside the repository.

### L5 — E6.1 implementation and regression correction


### L6 — Independent E6 audit and correction

An independent verifier found two E6 blockers: `.strip()` accepted whitespace-padded approval tokens despite the exact `s`/`n` requirement, and the delegation table ambiguously assigned `resultado.codigo` to `ver_cambios` even though that tool returns a diff string. Added a parametrized regression test; observed RED with exactly two whitespace cases failing, then removed normalization and clarified the table. Fresh checks: focused E6 tests 11 passed; full suite 146 passed; `lint-imports` 2 kept/0 broken; CI fitness tests 5 passed; `git diff --check` clean. Independent recheck passed: exact invalid tokens reprompt, rejection leaves data unchanged, approval/rejection events and tool outcomes are distinct across all three issues, and E6.2 evidence matches trace types. E7/E8 remain gated. No commit or push has been made; awaiting user's push confirmation.

### L7 — E6 correction, review, and delivery

The native review found a deterministic blocker: EOF at the approval prompt raised `EOFError` before the trace could record the edit as rejected and blocked. Added a regression test, observed the expected failure, then made EOF fail closed as a rejection. The focused E6 file passed (12 tests), the full suite passed (147 tests), `lint-imports` kept both contracts, and `git diff --check` was clean. Native targeted validation approved the corrected candidate; the exact acknowledgement was consumed. Commit `be34c5873b8ef088bd18884e0aba70e880f457f6` was pushed to `origin/lab10-e6-e7-r8` and the remote SHA matched. E7 and E8 remain gated on explicit user confirmation. The review also noted that the verbatim original request in this task log contains a local filesystem path; that advisory was not blocking and the path is present in the pushed history.

### L8 — E7 authorized

User confirmation (2026-11-21): “continua con el 7”. T2 is now in progress; E8 remains gated until E7 is complete and the user confirms.

### L9 — E7 evidence and documentation verified

Added `agentes/observacion.md` and `agentes/bitacora-ia.md`. The repository had no ISSUE-01 session trace, so a new operator-guided `ModeloInteractivo` diagnostic session was captured without editing the sandbox; its test returned code 0 and the current source already uses `casefold`, despite the issue description claiming the defect remains. Recomputed all three primary-session metrics directly from JSONL: ISSUE-01 4 steps/3 tool actions/6543 context characters; ISSUE-02 A 6/5/6796; ISSUE-03 9/8/8199. Each has 0 contract rejections and 0 blocked tools; rounds are marked not applicable for single-agent sessions, with ISSUE-02 B's separate one-round summary called out. The six-entry interaction log cites the E6 review's EOFError blocker and its regression/fix. `git diff --check`, artifact-link checks, and metric recomputation passed. E8 remains gated on user confirmation after E7.
