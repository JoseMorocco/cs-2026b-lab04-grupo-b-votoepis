"""Construye exactamente el mismo prompt v1 para la captura y la evaluación."""

from pathlib import Path
import re


def renderizar(variables):
    plantilla = Path(__file__).with_name("v1.txt").read_text(encoding="utf-8")
    return re.sub(r"\{\{(historia_id|historia)\}\}", lambda token: variables[token[1]], plantilla)


def prompt_v1(context):
    return renderizar(context["vars"])
