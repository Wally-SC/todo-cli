from __future__ import annotations

import argparse
import sys
from pathlib import Path

from tarefas.armazenamento import ListaDeTarefas
from tarefas.modelo import PRIORIDADES

ARQUIVO_PADRAO = Path.home() / ".todo-cli" / "tarefas.json"


def _linha(tarefa) -> str:
    marca = "x" if tarefa.concluida else " "
    prazo = f" (até {tarefa.prazo})" if tarefa.prazo else ""
    alerta = " ATRASADA" if tarefa.atrasada() else ""
    return f"[{marca}] {tarefa.id:>3}  {tarefa.prioridade:<5}  {tarefa.titulo}{prazo}{alerta}"


def construir_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="todo", description="Gerenciador de tarefas no terminal.")
    parser.add_argument("--arquivo", type=Path, default=ARQUIVO_PADRAO, help="arquivo JSON das tarefas")
    sub = parser.add_subparsers(dest="comando", required=True)

    add = sub.add_parser("add", help="adiciona uma tarefa")
    add.add_argument("titulo")
    add.add_argument("-p", "--prioridade", choices=PRIORIDADES, default="media")
    add.add_argument("-d", "--prazo", help="AAAA-MM-DD")

    listar = sub.add_parser("list", help="lista tarefas")
    listar.add_argument("-a", "--todas", action="store_true", help="inclui concluídas")

    for nome, ajuda in (("done", "conclui uma tarefa"), ("rm", "remove uma tarefa")):
        cmd = sub.add_parser(nome, help=ajuda)
        cmd.add_argument("id", type=int)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = construir_parser().parse_args(argv)
    try:
        lista = ListaDeTarefas(args.arquivo)
        if args.comando == "add":
            tarefa = lista.adicionar(args.titulo, args.prioridade, args.prazo)
            print(f"adicionada: {tarefa.id} - {tarefa.titulo}")
        elif args.comando == "list":
            tarefas = lista.listar(incluir_concluidas=args.todas)
            if not tarefas:
                print("nenhuma tarefa")
            for tarefa in tarefas:
                print(_linha(tarefa))
        elif args.comando == "done":
            tarefa = lista.concluir(args.id)
            print(f"concluída: {tarefa.id} - {tarefa.titulo}")
        elif args.comando == "rm":
            lista.remover(args.id)
            print(f"removida: {args.id}")
    except (ValueError, KeyError) as exc:
        mensagem = exc.args[0] if exc.args else str(exc)
        print(f"erro: {mensagem}", file=sys.stderr)
        return 1
    return 0
