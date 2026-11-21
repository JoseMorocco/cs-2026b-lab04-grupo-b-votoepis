"""ISSUE-01 sembrado para Lab 10. Registro en memoria aislado del servicio real."""


class RegistroPorCodigo:
    def __init__(self):
        self.participaciones = set()

    def emitir(self, eleccion, codigo):
        clave = (eleccion, codigo)
        if clave in self.participaciones:
            return False
        self.participaciones.add(clave)
        return True
