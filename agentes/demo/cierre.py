"""ISSUE-03 corregido: comparación de instantes con zona horaria."""


def puede_cerrar(ahora, cierre_programado):
    return ahora >= cierre_programado
