from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
from uuid import UUID, uuid4
from abc import ABC, abstractmethod

class EstadoEleccion(Enum):
    CONFIGURADA = "CONFIGURADA"
    ABIERTA = "ABIERTA"
    CERRADA = "CERRADA"
    ESCRUTADA = "ESCRUTADA"
    PUBLICADA = "PUBLICADA"

@dataclass
class Estudiante:
    id: UUID
    codigo: str
    correo_institucional: str
    
    def obtener_correo_institucional(self) -> str:
        return self.correo_institucional

@dataclass
class Candidato:
    id: UUID
    nombre: str
    agrupacion: str

@dataclass
class Eleccion:
    id: UUID
    titulo: str
    estado: EstadoEleccion
    candidatos: list[Candidato] = field(default_factory=list)
    
    def verificar_estado(self) -> EstadoEleccion:
        return self.estado

    def _estado_actual(self):
        from src.votacion.estados import ESTADOS
        return ESTADOS[self.estado]

    def abrir(self, padron_cargado=False) -> None:
        self._estado_actual().abrir(self, padron_cargado)

    def cerrar(self) -> None:
        self._estado_actual().cerrar(self)

    def iniciar_escrutinio(self, autorizado=False) -> None:
        self._estado_actual().iniciar_escrutinio(
            self, autorizado
        )

    def publicar_resultados(
        self, acta_firmada=False, totales_verificados=False
    ) -> None:
        self._estado_actual().publicar_resultados(
            self, acta_firmada, totales_verificados
        )

@dataclass
class Participacion:
    id: UUID
    fecha_hora: datetime
    
    @staticmethod
    def crear(estudiante_id: UUID, eleccion_id: UUID) -> 'Participacion':
        raise NotImplementedError

@dataclass
class Voto:
    id: UUID
    fecha_hora: datetime
    
    @staticmethod
    def crear(candidato_id: UUID, eleccion_id: UUID) -> 'Voto':
        raise NotImplementedError

@dataclass
class EventoSeguridad:
    id: UUID
    fecha_hora: datetime
    tipo: str
    detalle: str
    
    @staticmethod
    def crear_intento_duplicado(estudiante_id: UUID, eleccion_id: UUID) -> 'EventoSeguridad':
        raise NotImplementedError

class VotacionController:
    def registrar_voto(self, estudiante_id: UUID, eleccion_id: UUID, candidato_id: UUID) -> bool:
        raise NotImplementedError

class ServicioVotacion:
    def emitir_voto(self, estudiante_id: UUID, eleccion_id: UUID, candidato_id: UUID) -> bool:
        raise NotImplementedError

# --- PUERTOS (Interfaces) ---
class EleccionRepositorio(ABC):
    @abstractmethod
    def buscar_por_id(self, eleccion_id: UUID) -> Eleccion: ...

class PadronPort(ABC):
    @abstractmethod
    def esta_habilitado(self, estudiante_id: UUID, eleccion_id: UUID) -> bool: ...

class EstudianteRepositorio(ABC):
    @abstractmethod
    def buscar_por_id(self, estudiante_id: UUID) -> Estudiante: ...

class CandidatoRepositorio(ABC):
    @abstractmethod
    def pertenece_a_eleccion(self, candidato_id: UUID, eleccion_id: UUID) -> bool: ...

class ParticipacionRepositorio(ABC):
    @abstractmethod
    def existe(self, estudiante_id: UUID, eleccion_id: UUID) -> bool: ...
    @abstractmethod
    def guardar(self, participacion: Participacion) -> None: ...

class VotoRepositorio(ABC):
    @abstractmethod
    def guardar(self, voto: Voto) -> None: ...

class EventoSeguridadRepositorio(ABC):
    @abstractmethod
    def guardar(self, evento: EventoSeguridad) -> None: ...

class CorreoPort(ABC):
    @abstractmethod
    def enviar_confirmacion(self, correo_institucional: str) -> None: ...

# --- ADAPTADORES ---
class CorreoInstitucionalAdapter(CorreoPort):
    def enviar_confirmacion(self, correo_institucional: str) -> None:
        raise NotImplementedError("Integrar con servidor SMTP")
