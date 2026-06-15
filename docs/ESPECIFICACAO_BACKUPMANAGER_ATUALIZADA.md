# Especificacao Atualizada - BackupManager

Este documento consolida as regras atuais do projeto BackupManager para a disciplina INF1040.

## Objetivo

O BackupManager e uma aplicacao desktop local para gerenciar perfis de backup. Cada perfil define:

- nome;
- origens;
- destinos;
- operacao de copiar ou mover;
- restricoes de arquivos;
- agendamento;
- estado ativo/inativo;
- estado de arquivos monitorados;
- historico de execucoes.

## Regras Principais

- Usar Python.
- Usar dicionarios para representar entidades.
- Nao usar classes na logica principal.
- Nao usar dataclasses.
- Manter o projeto modular.
- Usar codigos de retorno padronizados.
- Usar testes automatizados com `unittest`.
- Usar JSON para persistencia local.
- Usar `customtkinter` apenas para aparencia da interface.

## Persistencia em Memoria

A regra de persistencia e:

```text
JSON -> leitura inicial -> ESTADO em memoria -> alteracoes em memoria -> escrita final no encerramento
```

O `controller.py` mantem o estado central:

```python
ESTADO = {
    "perfis": [],
    "historico": [],
    "config": {},
    "alterado": False
}
```

Quando houver alteracao em perfis, historico ou configuracao:

```python
ESTADO["alterado"] = True
```

`ESTADO["config"]` tambem guarda extensoes customizadas em `extensoes_disponiveis`. A interface mostra extensoes padrao e customizadas em checkboxes; o perfil salva somente as extensoes marcadas em `restricoes["extensoes_permitidas"]`.

Os JSONs sao reescritos somente em:

```python
controller.finalizar_aplicacao()
```

## Arquitetura

```text
Usuario
  ->
interface.py
  ->
controller.py
  |-- perfil_manager.py
  |-- backup_engine.py
  |     `-- file_utils.py
  |-- scheduler.py
  |     `-- file_utils.py
  |-- history_manager.py
  `-- storage.py
        `-- data/*.json
```

Durante a execucao normal:

```text
interface.py -> controller.py -> modulos internos -> ESTADO em memoria
```

`storage.py` e usado principalmente na inicializacao e finalizacao.

## Responsabilidade dos Modulos

### `interface.py`

Interface grafica com `tkinter` e `customtkinter`.

Deve chamar o `controller.py` e nao executar regras complexas de backup diretamente.

### `controller.py`

Camada central da aplicacao.

Responsavel por carregar dados, manter `ESTADO`, coordenar modulos internos, validar perfil inativo, validar caminhos de origem/destino, manter a lista de extensoes disponiveis e salvar JSON apenas no encerramento.

### `perfil_manager.py`

Criacao, consulta, edicao, ativacao, desativacao e exclusao de perfis em memoria.

### `file_utils.py`

Funcoes auxiliares de sistema de arquivos: listar arquivos, obter metadados, verificar caminhos e aplicar filtros por extensao, nome, tamanho e data.

### `backup_engine.py`

Execucao real do backup:

- validacao minima de perfil;
- geracao de caminho de destino;
- criacao de pasta destino;
- copia de arquivo;
- movimentacao de arquivo;
- backup para multiplos destinos;
- registro de erros por arquivo no resultado.

No modo `mover`, o arquivo e copiado para todos os destinos antes de ser removido da origem.

### `history_manager.py`

Criacao, consulta, limpeza e resumo de registros de historico em memoria.

Status padronizados:

- `sucesso`;
- `parcial`;
- `erro`;
- `sem_arquivos`.

Erros devem sempre ser lista.

### `scheduler.py`

Execucao automatica simples:

- verificacao por intervalo;
- deteccao de alteracao de arquivos;
- atualizacao de estado de arquivos em memoria;
- monitoramento com `threading`;
- respeito a perfil ativo/inativo.

### `storage.py`

Leitura e escrita de JSON.

Tambem cria arquivos padrao quando necessario:

- `data/perfis.json`;
- `data/historico.json`;
- `data/config.json`.

### `return_codes.py`

Codigos de retorno e mensagens padronizadas.

## Validacao Recomendada

Antes de concluir alteracoes:

```bash
python -m unittest discover -s tests
python -m compileall backupmanager
```
