# Lab 09 — Integración, CI y entrega E6–E8
Branch: `lab09/e6-e7-e8` from `origin/main` (`e560379`); delivery: single PR, separate E6/E7/E8 commits and pushes; no tag or main changes.
Runner: pytest, `npx promptfoo@0.125.1 eval`; forecast ~450–650 authored changed lines, single PR explicitly requested.

## Specs
S1 (E6): "Implementen generador_*.py detrás del puerto ProveedorLLM del Laboratorio 07, cargando la plantilla por versión y validando la salida con el esquema." "Escriban 2 o más pruebas con un proveedor grabado: una respuesta válida que se acepta y una inválida que se rechaza."
S2 (E7): "Configuren .github/workflows/prompts.yml para ejecutar npx promptfoo eval con el proveedor grabado en cada Pull Request." "Completen bitacora-ia.md con 5 o más interacciones, incluyendo una sugerencia de la IA que rechazaron con evidencia." "No determinismo (obligatorio): ejecuten su mejor prompt 3 veces sobre los mismos 3 casos y comparen las respuestas. Escriban en 5 líneas qué cambió y qué implica para las grabaciones."
S3 (E8): "Agreguen al README.md la sección \"Prompt engineering (Lab 09)\": tabla de versiones con su tasa de aprobación, gráfico de resultados y lecciones aprendidas." "Cada integrante abre un Pull Request con una versión de prompt; otro integrante lo revisa con la lista de verificación del Paso 9." "Creen la etiqueta v0.9-prompts y entreguen el enlace del repositorio en el Aula Virtual hasta el sábado 14/11/2026 a las 23:59."
S4 (human constraints): "no hagas eso, mis compañeros ya hicieron las otras partes e1 al e5 y crearon sus ramos en el github alli revisa que este todo y de acuerdo a eso trabaja" "no modifiques el main" "no pushees todo de golpee digamos terminas e6 lo pusheas todo eso con e6: tal tal una descripcuon y luego pasas a e7 y lo mismo hasta e8 y luego creas un pullrquest de la rama para que lo acepte otro de mis compañeros". No crear etiqueta antes de aceptar el PR.

## Tasks
T1 — S1,S4; route: bounded writer (context backstop), status: done; commit: 06a3fd1 (pushed); test: 12 focused, 72 suite, 22 existing criteria passed; RED blocked by missing runner, GREEN observed.
T2 — S2,S4; route: bounded writer (context backstop) + parent local Ollama experiment; status: done (remote CI awaits PR); commit: E7 work unit (hash in L4); check: workflow, eight documented interactions, replay and nine live captures on three cases.
T3 — S3,S4; route: inline, status: pending; commit: pending; check: version rates derived from results, graph, checklist and PR; tag deferred until PR accepted.

## Log
L1 (original request, verbatim): /home/bunuelo/Descargas/CSLAB/Lab9 quiero que entres y mires el pdf y aprendas de que trata la actividad luego mira la carpeta recursos que esta alli mismo E6. Integración en el código
1. Implementen generador_*.py detrás del puerto ProveedorLLM del Laboratorio 07, cargando la plantilla por
versión y validando la salida con el esquema.
2. Escriban 2 o más pruebas con un proveedor grabado: una respuesta válida que se acepta y una inválida que se
rechaza.
E7. Integración continua y bitácora
1. Configuren .github/workflows/prompts.yml para ejecutar npx promptfoo eval con el proveedor grabado
en cada Pull Request.
2. Completen bitacora-ia.md con 5 o más interacciones, incluyendo una sugerencia de la IA que rechazaron con
evidencia.
3. No determinismo (obligatorio): ejecuten su mejor prompt 3 veces sobre los mismos 3 casos y comparen las
respuestas. Escriban en 5 líneas qué cambió y qué implica para las grabaciones.
E8. README, revisión y entrega
1. Agreguen al README.md la sección "Prompt engineering (Lab 09)": tabla de versiones con su tasa de aprobación,
gráfico de resultados y lecciones aprendidas.
2. Cada integrante abre un Pull Request con una versión de prompt; otro integrante lo revisa con la lista de
verificación del Paso 9.
3. Creen la etiqueta v0.9-prompts y entreguen el enlace del repositorio en el Aula Virtual hasta el sábado
14/11/2026 a las 23:59. esta parte me toco hacer en la ultima parte e6 e7 e8, en la parte e8 dice crear etiqueta pero primero me deben aceptar el pull request entonces no hagas eso, mis compañeros ya hicieron las otras partes e1 al e5 y crearon sus ramos en el github alli revisa que este todo y de acuerdo a eso trabaja este es el link https://github.com/JoseMorocco/cs-2026b-lab04-grupo-b-votoepis.git y todas las ramas  correspodientes al labroatorio epiezan con lab09 listo empieza a trabajar modificas y realizas todo lo que indica el documento creas una rama nuevo llamada lab09/e6-e7-e8 y alli subes los cambios puedes clonar el repo descargar para modificar leer y todas las demas ramas, no modifiques el main eso si, una indicacion mas no pushees todo de golpee digamos terminas e6 lo pusheas todo eso con e6: tal tal una descripcuon y luego pasas a e7 y lo mismo hasta e8 y luego creas un pullrquest de la rama para que lo acepte otro de mis compañeros bueno ponte a trabajar
L2: PDF extracted locally with pdftotext, section III E6–E8 and steps 8–9 read; resource sample is AgroConecta, not VotoEPIS. `origin/main` includes ancestors `origin/lab09-e1-e2`, `origin/lab09-publicar-estructura`, and `origin/lab09/e3-4-5`. `gh auth status` reports not logged in: remote push and PR may need human login. Engram mirror unavailable (no callable memory tool); local document is canonical, mirror pending.
L3: E6 test-first attempt: RED could not collect because worker had no `python`; local `python3` lacked pytest. After isolated `.venv` install, tests/test_generador_criterios.py: 12 passed; tests/: 72 passed; prompts/criterios/: 22 passed. First suite attempt: 4 failed (missing radon), resolved by installing runner dependency. New adapter preserves ProveedorLLM and recorded prompt bytes. `git commit` refused: author identity unknown; no commit exists. `gh auth status` shows no GitHub session. GitHub login completed as Bunuuelo; local Git identity set from GitHub profile and noreply address. Commit 06a3fd1 pushed independently to origin/lab09/e6-e7-e8. Native E6 assessment: medium, reviewDue=false (under_budget), so no review started; boundary remains origin/main. Proceeding to E7.
L4: E7 local verification: 72 tests passed; promptfoo recorded v3 criteria 9/9 and security 8/8; replay 3×3 byte-identical. Independently ran exact rendered v3 prompt nine times on local Ollama gemma3:1b, temp 0.7, on HU-01/LAB09-AMB/LAB09-ADV; all nine hashes differ within their cases, 9/9 rejected by existing JSON contract, one adversarial marker leaked. Raw captures under prompts/criterios/variacion-v3-ollama.json; no original recording overwritten. Independent verifier confirmed workflow structure, matching hashes, all cases, baseline preservation and rejection. GitHub Actions actual PR run remains pending until T3. Risk: item 5 (CI/environment), independently verified locally; no CI green claim.
