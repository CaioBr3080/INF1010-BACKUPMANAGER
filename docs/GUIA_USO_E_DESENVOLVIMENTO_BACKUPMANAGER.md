# Guia de Uso e Desenvolvimento - BackupManager

## Como Executar

Na pasta do projeto:

```bash
python -m backupmanager.main
```

A interface usa `tkinter` com aparencia em `customtkinter`. Se necessario:

```bash
pip install customtkinter
```

## Como Rodar Testes

```bash
python -m unittest discover -s tests
```

Para verificar sintaxe dos modulos:

```bash
python -m compileall backupmanager
```

## Persistencia

O sistema usa JSON apenas na inicializacao e no encerramento:

```text
JSON -> leitura inicial -> ESTADO em memoria -> alteracoes em memoria -> escrita final no encerramento
```

Durante o uso normal, criar perfil, editar perfil, executar backup e registrar historico nao salvam JSON imediatamente.

O salvamento ocorre em:

```python
controller.finalizar_aplicacao()
```

## Uso Basico da Interface

### Criar Perfil

Digite um nome e clique em `Criar perfil`.

### Selecionar Perfil

Clique em um perfil na lista. Os dados aparecem no formulario.

### Editar Perfil

Altere nome, estado ativo/inativo, origens, destinos, operacao, restricoes ou agendamento e clique em `Aplicar alteracoes`.

As extensoes permitidas sao escolhidas em uma lista de checkboxes. Para usar uma extensao que nao aparece na lista, digite a extensao no campo lateral e clique em `Adicionar`.

Extensoes adicionadas ficam em memoria durante a execucao e sao salvas em `config.json` ao encerrar a aplicacao.

### Adicionar Origem ou Destino

Use `Adicionar origem` ou `Adicionar destino`, escolha uma pasta e depois clique em `Aplicar alteracoes`.

### Visualizar Arquivos

Selecione um perfil e clique em `Visualizar arquivos`.

A janela mostra os arquivos encontrados nas origens, suas informacoes e se cada arquivo esta `INCLUIDO` ou `IGNORADO` pelas restricoes.

### Executar Backup

Selecione um perfil e clique em `Executar backup`.

O backup copia ou move arquivos para todos os destinos configurados.

No modo `mover`, o arquivo e copiado para todos os destinos antes de ser removido da origem.

### Ver Historico

Selecione um perfil e clique em `Historico`.

A janela mostra data, status, arquivos processados, copiados, movidos e erros.

### Sair

Ao clicar em `Sair` ou fechar a janela, a aplicacao chama `controller.finalizar_aplicacao()`.

Se houver alteracoes em memoria, os JSONs sao reescritos nesse momento.

## Modulos Principais

- `controller.py`: coordena o estado em memoria e os outros modulos.
- `perfil_manager.py`: cria, consulta e altera perfis.
- `file_utils.py`: lista arquivos, le metadados e aplica filtros.
- `backup_engine.py`: executa copia, movimentacao e backup para multiplos destinos.
- `history_manager.py`: cria, consulta, limpa e resume historico.
- `scheduler.py`: decide execucao automatica por intervalo ou alteracao.
- `storage.py`: le e escreve JSON.
- `interface.py`: interface grafica com `tkinter` e `customtkinter`.

## Regras de Desenvolvimento

- Nao usar classes na logica principal.
- Nao usar dataclasses.
- Representar entidades como dicionarios.
- Manter funcoes separadas por modulo.
- Usar codigos de retorno de `return_codes.py`.
- Atualizar ou criar testes com `unittest`.
- Rodar testes e `compileall` antes de concluir alteracoes.
