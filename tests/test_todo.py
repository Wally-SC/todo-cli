from datetime import date

import pytest

from tarefas import ListaDeTarefas, Tarefa
from tarefas.cli import main


@pytest.fixture
def arquivo(tmp_path):
    return tmp_path / "tarefas.json"


def test_adicionar_e_persistir(arquivo):
    lista = ListaDeTarefas(arquivo)
    t = lista.adicionar("Estudar SQL", prioridade="alta", prazo="2030-01-01")
    assert t.id == 1

    recarregada = ListaDeTarefas(arquivo)
    assert [x.titulo for x in recarregada.listar()] == ["Estudar SQL"]


def test_ids_sao_sequenciais_mesmo_apos_remocao(arquivo):
    lista = ListaDeTarefas(arquivo)
    lista.adicionar("a")
    lista.adicionar("b")
    lista.remover(2)
    assert lista.adicionar("c").id == 2  # reaproveita o maior id + 1


def test_concluir_esconde_da_listagem_padrao(arquivo):
    lista = ListaDeTarefas(arquivo)
    lista.adicionar("a")
    lista.concluir(1)
    assert lista.listar() == []
    assert len(lista.listar(incluir_concluidas=True)) == 1


def test_ordenacao_por_prioridade(arquivo):
    lista = ListaDeTarefas(arquivo)
    lista.adicionar("baixa", prioridade="baixa")
    lista.adicionar("alta", prioridade="alta")
    lista.adicionar("media", prioridade="media")
    assert [t.titulo for t in lista.listar()] == ["alta", "media", "baixa"]


def test_validacoes():
    with pytest.raises(ValueError):
        Tarefa(id=1, titulo="   ")
    with pytest.raises(ValueError):
        Tarefa(id=1, titulo="x", prioridade="urgente")
    with pytest.raises(ValueError):
        Tarefa(id=1, titulo="x", prazo="31/12/2030")


def test_atrasada():
    t = Tarefa(id=1, titulo="x", prazo="2020-01-01")
    assert t.atrasada(hoje=date(2020, 1, 2))
    assert not t.atrasada(hoje=date(2019, 12, 31))
    t.concluida = True
    assert not t.atrasada(hoje=date(2020, 1, 2))


def test_buscar_inexistente(arquivo):
    with pytest.raises(KeyError):
        ListaDeTarefas(arquivo).buscar(99)


def test_arquivo_corrompido(arquivo):
    arquivo.write_text("{ isso não é json", encoding="utf-8")
    with pytest.raises(ValueError):
        ListaDeTarefas(arquivo)


def test_cli_fluxo_completo(arquivo, capsys):
    base = ["--arquivo", str(arquivo)]
    assert main(base + ["add", "Revisar PR", "-p", "alta"]) == 0
    assert main(base + ["list"]) == 0
    assert "Revisar PR" in capsys.readouterr().out
    assert main(base + ["done", "1"]) == 0
    assert main(base + ["list"]) == 0
    assert "nenhuma tarefa" in capsys.readouterr().out


def test_cli_erro_retorna_1(arquivo, capsys):
    assert main(["--arquivo", str(arquivo), "done", "42"]) == 1
    assert "não encontrada" in capsys.readouterr().err
