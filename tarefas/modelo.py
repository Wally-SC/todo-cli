from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import date

PRIORIDADES = ("baixa", "media", "alta")


@dataclass
class Tarefa:
    id: int
    titulo: str
    prioridade: str = "media"
    prazo: str | None = None  # AAAA-MM-DD
    concluida: bool = False
    criada_em: str = field(default_factory=lambda: date.today().isoformat())

    def __post_init__(self) -> None:
        if not self.titulo.strip():
            raise ValueError("o título não pode ser vazio")
        if self.prioridade not in PRIORIDADES:
            raise ValueError(f"prioridade inválida: {self.prioridade!r} (use {', '.join(PRIORIDADES)})")
        if self.prazo is not None:
            try:
                date.fromisoformat(self.prazo)
            except ValueError as exc:
                raise ValueError(f"prazo inválido: {self.prazo!r} (use AAAA-MM-DD)") from exc

    def atrasada(self, hoje: date | None = None) -> bool:
        if self.concluida or self.prazo is None:
            return False
        return date.fromisoformat(self.prazo) < (hoje or date.today())

    def para_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def de_dict(cls, dados: dict) -> "Tarefa":
        return cls(**dados)
