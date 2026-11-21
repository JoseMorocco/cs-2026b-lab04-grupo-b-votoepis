"""ISSUE-03 sembrado. El horario pertenece solo al contrato de demostración."""


def puede_cerrar(ahora, cierre_programado):
    return ahora.date() >= cierre_programado.date()
