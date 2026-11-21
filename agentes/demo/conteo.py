"""ISSUE-02 sembrado. None representa un voto en blanco en esta demostración."""


def contar(votos):
    return {"validos": len(votos), "blancos": votos.count(None)}
