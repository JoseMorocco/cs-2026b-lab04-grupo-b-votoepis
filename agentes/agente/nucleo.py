"""Bucle ReAct con decisiones reales, validación y observaciones persistidas."""

from hashlib import sha256
import json
from subprocess import SubprocessError
from time import perf_counter

from jsonschema import ValidationError

from agentes.agente.contrato import validar
from agentes.agente.herramientas import AprobacionRechazada
from agentes.agente.modelo import contexto
from agentes.agente.traza import a_mermaid


def registrar(salida, eventos, tipo, estado, **datos):
    evento = {"tipo": tipo, "estado": estado, **datos}
    eventos.append(evento)
    salida.write(json.dumps(evento, ensure_ascii=False) + "\n")
    salida.flush()


def observar(sandbox, decision):
    try:
        return sandbox.ejecutar(decision["accion"], decision["args"])
    except AprobacionRechazada as error:
        return {"error": str(error), "aprobacion": "RECHAZADA"}
    except (ValueError, OSError, SubprocessError) as error:
        return {"error": str(error)}


def ejecutar(modelo, sandbox, sesion, max_pasos=12):
    if not 1 <= max_pasos <= 12:
        raise ValueError("El máximo de pasos debe estar entre 1 y 12.")
    sesion.mkdir(parents=True, exist_ok=False)
    eventos = []
    historial = [{"rol": "objetivo", "texto": sandbox.leer_archivo(sandbox.issue_file)}]
    with (sesion / "traza.jsonl").open("x", encoding="utf-8", newline="\n") as traza:
        registrar(traza, eventos, "objetivo", "INICIO", texto=historial[0]["texto"])
        try:
            resultado = iterar(modelo, sandbox, sesion, max_pasos, historial, traza, eventos)
        except (EOFError, KeyboardInterrupt):
            registrar(traza, eventos, "interrupcion", "DETENIDO")
            resultado = "Sesión interrumpida por el operador."
        finally:
            (sesion / "trayectoria.mmd").write_text(a_mermaid(eventos), encoding="utf-8")
            (sesion / "cambios.diff").write_text(sandbox.ver_cambios(), encoding="utf-8")
    return resultado


def iterar(modelo, sandbox, sesion, max_pasos, historial, traza, eventos):
    for paso in range(1, max_pasos + 1):
        texto = contexto(historial)
        if len(texto) > 100000:
            registrar(traza, eventos, "limite_contexto", "DETENIDO", paso=paso)
            return "Límite de contexto alcanzado."
        (sesion / f"contexto-{paso:02d}.txt").write_text(texto, encoding="utf-8")
        registrar(traza, eventos, "solicitud", "DECIDIENDO", paso=paso, caracteres=len(texto))
        respuesta = modelo.decidir(texto)
        bruto = respuesta.encode("utf-8")
        nombre = f"decision-{paso:02d}.txt"
        (sesion / nombre).write_bytes(bruto)
        registrar(traza, eventos, "respuesta", "VALIDANDO", paso=paso, archivo=nombre,
                  sha256=sha256(bruto).hexdigest())
        procesar = procesar_decision(respuesta, sandbox, traza, eventos, paso)
        historial.append({"rol": "decision", "texto": respuesta[:12000]})
        historial.append({"rol": "observacion", "resultado": procesar})
        if procesar.get("final"):
            return procesar["respuesta"]
    registrar(traza, eventos, "limite_pasos", "DETENIDO", pasos=max_pasos)
    return "Límite de pasos alcanzado."


def procesar_decision(respuesta, sandbox, traza, eventos, paso):
    try:
        if len(respuesta) > 16000:
            raise ValueError("Respuesta demasiado grande.")
        decision = validar(respuesta)
    except (ValueError, ValidationError) as error:
        resultado = {"rechazo_contrato": str(error)[:2000]}
        registrar(traza, eventos, "rechazo", "BLOQUEADO", paso=paso, resultado=resultado)
        return resultado
    if decision["accion"] == "final":
        registrar(traza, eventos, "final", "FINAL", paso=paso, respuesta=decision["respuesta"])
        return {"final": True, "respuesta": decision["respuesta"]}
    inicio = perf_counter()
    resultado = observar(sandbox, decision)
    if isinstance(resultado, dict) and resultado.get("aprobacion") == "RECHAZADA":
        registrar(traza, eventos, "aprobacion", "RECHAZADA", paso=paso,
                  accion=decision["accion"], ruta=decision["args"].get("ruta"))
    elif decision["accion"] == "editar_archivo" and not (
        isinstance(resultado, dict) and "error" in resultado
    ):
        registrar(traza, eventos, "aprobacion", "APROBADA", paso=paso,
                  accion=decision["accion"], ruta=decision["args"].get("ruta"))
    estado = "BLOQUEADO" if isinstance(resultado, dict) and "error" in resultado else "OBSERVANDO"
    registrar(traza, eventos, "herramienta", estado, paso=paso,
              accion=decision["accion"], args=decision["args"],
              duracion_ms=round(1000 * (perf_counter() - inicio), 3), resultado=resultado)
    return {"resultado": resultado}
