from __future__ import annotations

import json
from pathlib import Path

from tarefas.modelo import Tarefa


class ListaDeTarefas:
    """Lista de tarefas persistida em um arquivo JSON."""

    def __init__(self, caminho: str | Path) -> None:
        self.caminho = Path(caminho)
        self._tarefas: list[Tarefa] = []
        self._carregar()

    # --- persistência -------------------------------------------------
    def _carregar(self) -> None:
        if not self.caminho.exists():
            return
        conteudo = self.caminho.read_text(encoding="utf-8").strip()
        if not conteudo:
            return
        try:
            dados = json.loads(conteudo)
        except json.JSONDecodeError as exc:
            raise ValueError(f"arquivo corrompido: {self.caminho}") from exc
        self._tarefas = [Tarefa.de_dict(item) for item in dados]

    def _salvar(self) -> None:
        self.caminho.parent.mkdir(parents=True, exist_ok=True)
        temporario = self.caminho.with_suffix(self.caminho.suffix + ".tmp")
        temporario.write_text(
            json.dumps([t.para_dict() for t in self._tarefas], ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        temporario.replace(self.caminho)  # escrita atômica

    # --- operações ----------------------------------------------------
    def _proximo_id(self) -> int:
        return max((t.id for t in self._tarefas), default=0) + 1

    def adicionar(self, titulo: str, prioridade: str = "media", prazo: str | None = None) -> Tarefa:
        tarefa = Tarefa(id=self._proximo_id(), titulo=titulo.strip(), prioridade=prioridade, prazo=prazo)
        self._tarefas.append(tarefa)
        self._salvar()
        return tarefa

    def buscar(self, id_: int) -> Tarefa:
        for tarefa in self._tarefas:
            if tarefa.id == id_:
                return tarefa
        raise KeyError(f"tarefa {id_} não encontrada")

    def concluir(self, id_: int) -> Tarefa:
        tarefa = self.buscar(id_)
        tarefa.concluida = True
        self._salvar()
        return tarefa

    def remover(self, id_: int) -> None:
        tarefa = self.buscar(id_)
        self._tarefas.remove(tarefa)
        self._salvar()

    def listar(self, incluir_concluidas: bool = False) -> list[Tarefa]:
        ordem = {"alta": 0, "media": 1, "baixa": 2}
        tarefas = [t for t in self._tarefas if incluir_concluidas or not t.concluida]
        return sorted(tarefas, key=lambda t: (t.concluida, ordem[t.prioridade], t.prazo or "9999-12-31", t.id))
