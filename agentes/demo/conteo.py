"""ISSUE-02 corregido: None es voto en blanco, no válido."""


def contar(votos):
    validos = 0
    blancos = 0
    for voto in votos:
        if voto is None:
            blancos += 1
        else:
            validos += 1
    return {"validos": validos, "blancos": blancos}
