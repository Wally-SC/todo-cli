# todo-cli

Gerenciador de tarefas para o terminal, com persistência em arquivo JSON.

## Uso

```bash
python -m tarefas add "Estudar SQL" -p alta -d 2026-12-01
python -m tarefas list
python -m tarefas done 1
python -m tarefas rm 1
python -m tarefas list --todas          # inclui concluídas
python -m tarefas --arquivo ./minhas.json list
```

Por padrão as tarefas ficam em `~/.todo-cli/tarefas.json`.
Prioridades: `baixa`, `media`, `alta`. Tarefas vencidas aparecem como `ATRASADA`.

## Decisões de projeto

- **Escrita atômica:** o JSON é gravado em arquivo temporário e depois renomeado,
  então uma queda no meio da gravação não corrompe a lista.
- **Validação no modelo:** `Tarefa` valida título, prioridade e formato do prazo.
- **Camadas separadas:** modelo, armazenamento e CLI em módulos distintos, o que
  facilita trocar o JSON por SQLite depois.

## Testes

```bash
pip install pytest
pytest
```
