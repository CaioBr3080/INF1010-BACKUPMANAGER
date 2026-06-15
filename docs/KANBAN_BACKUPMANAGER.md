# Kanban de Desenvolvimento - BackupManager

Este documento organiza o que falta ser feito no BackupManager em tarefas pequenas o suficiente para serem colocadas em um quadro Kanban.

Use as colunas:

```text
Backlog -> Pronto para fazer -> Em andamento -> Em revisao -> Concluido
```

## Regras para Qualquer Tarefa

- Nao usar classes na logica principal.
- Nao usar dataclasses.
- Manter entidades como dicionarios.
- Manter a separacao por modulos.
- Nao salvar JSON durante operacoes comuns.
- Salvar JSON somente em `controller.finalizar_aplicacao()`.
- Usar codigos de retorno de `return_codes.py`.
- Criar ou atualizar testes com `unittest`.
- Rodar antes de concluir:

```bash
python -m unittest discover -s tests
python -m compileall backupmanager
```

## Ordem Recomendada

1. `BM-01` a `BM-06`: finalizar `file_utils.py`.
2. `BM-07` a `BM-12`: implementar backup real em `backup_engine.py`.
3. `BM-13` a `BM-16`: reforcar validacoes no `controller.py`.
4. `BM-17` a `BM-19`: melhorar historico.
5. `BM-20` a `BM-24`: implementar scheduler.
6. `BM-25` a `BM-29`: melhorar interface.
7. `BM-30` a `BM-32`: reforcar storage e documentacao final.

---

# Pronto para Fazer

## BM-01 - Implementar verificacoes basicas de caminho

Status: Concluido

Prioridade: Alta

Modulo principal: `backupmanager/file_utils.py`

Depende de: nada

Objetivo:

Implementar funcoes basicas para validar caminhos no sistema de arquivos.

Funcoes esperadas:

- `caminho_existe(caminho)`
- `caminho_e_diretorio(caminho)`
- `verificar_permissao_leitura(caminho)`
- `verificar_permissao_escrita(caminho)`

Criterios de aceite:

- Retorna `True` ou `False`, sem levantar excecao para caminho invalido.
- Funciona com arquivos e diretorios temporarios.
- Possui testes em `tests/test_file_utils.py`.

Resultado:

- Implementado em `backupmanager/file_utils.py`.
- Testado em `tests/test_file_utils.py`.
- Validado com `python -m unittest discover -s tests`.

## BM-02 - Listar arquivos de uma origem

Status: Concluido

Prioridade: Alta

Modulo principal: `backupmanager/file_utils.py`

Depende de: `BM-01`

Objetivo:

Implementar listagem de arquivos dentro de uma pasta de origem.

Funcoes esperadas:

- `listar_arquivos_em_origem(origem)`
- `listar_arquivos_de_origens(origens)`

Criterios de aceite:

- Ignora subpastas ou trata subpastas de forma definida no teste.
- Retorna lista vazia se a origem nao existir.
- Nao quebra caso uma origem seja invalida.
- Possui testes com `tempfile`.

Resultado:

- Implementado com listagem recursiva usando `os.walk`.
- Origens invalidas retornam lista vazia.
- Lista de origens invalida retorna lista vazia.
- Testado em `tests/test_file_utils.py`.

## BM-02.1 - Visualizar arquivos das origens

Status: Concluido

Prioridade: Alta

Modulo principal: `backupmanager/controller.py`, `backupmanager/interface.py`

Depende de: `BM-02`, `BM-03`, `BM-06`

Objetivo:

Permitir que o usuario veja quais arquivos existem nas origens do perfil e quais passam nas restricoes configuradas.

Funcoes esperadas:

- `controller.obter_arquivos_do_perfil(perfil_id)`
- Botao `Visualizar arquivos` na interface.

Criterios de aceite:

- Lista arquivos das origens do perfil.
- Mostra nome, extensao, tamanho, caminho e status.
- Indica se o arquivo esta `INCLUIDO` ou `IGNORADO`.
- Usa `file_utils.py` para listar, obter metadados e aplicar filtros.
- Nao salva JSON imediatamente.
- Possui testes no controller.

Resultado:

- `controller.obter_arquivos_do_perfil` retorna lista de arquivos com campo `incluido`.
- Interface possui botao `Visualizar arquivos`.
- A janela de visualizacao mostra arquivos encontrados e status por restricao.
- Testado em `tests/test_controller.py`.

## BM-03 - Obter metadados de arquivo

Status: Concluido

Prioridade: Alta

Modulo principal: `backupmanager/file_utils.py`

Depende de: `BM-01`

Objetivo:

Criar dicionario padrao para cada arquivo encontrado.

Funcoes esperadas:

- `obter_metadados_arquivo(caminho)`
- `obter_extensao(caminho)`

Formato esperado:

```python
{
    "caminho": str,
    "nome": str,
    "extensao": str,
    "tamanho": int,
    "data_modificacao": float
}
```

Criterios de aceite:

- Retorna dados corretos para arquivo temporario.
- Extensao vem em minusculo.
- Nome inclui o nome do arquivo.
- Possui testes.

Resultado:

- `obter_extensao` retorna extensao em minusculo e `""` para caminho invalido.
- `obter_metadados_arquivo` retorna dicionario no formato esperado para arquivos.
- Caminhos invalidos, inexistentes ou diretorios retornam `None`.
- Testado em `tests/test_file_utils.py`.

## BM-04 - Implementar filtro por extensao e nome

Status: Concluido

Prioridade: Alta

Modulo principal: `backupmanager/file_utils.py`

Depende de: `BM-03`

Objetivo:

Filtrar arquivos com base em extensoes permitidas e trecho obrigatorio no nome.

Funcoes esperadas:

- `atende_restricao_extensao(arquivo, restricoes)`
- `atende_restricao_nome(arquivo, restricoes)`

Criterios de aceite:

- Lista de extensoes vazia aceita qualquer extensao.
- Comparacao de extensao funciona com `.py`, `.txt`, etc.
- `nome_contem` vazio aceita qualquer nome.
- Filtro por nome ignora diferenca entre maiusculas e minusculas.
- Possui testes.

Resultado:

- Filtro por extensao normaliza ponto e maiusculas/minusculas.
- Lista vazia aceita qualquer extensao.
- Filtro por nome aceita campo vazio e ignora maiusculas/minusculas.
- Testado em `tests/test_file_utils.py`.

## BM-05 - Implementar filtro por tamanho e data

Status: Concluido

Prioridade: Alta

Modulo principal: `backupmanager/file_utils.py`

Depende de: `BM-03`

Objetivo:

Filtrar arquivos por tamanho minimo, tamanho maximo e data de modificacao.

Funcoes esperadas:

- `atende_restricao_tamanho(arquivo, restricoes)`
- `atende_restricao_data_modificacao(arquivo, restricoes)`

Criterios de aceite:

- `tamanho_min` padrao 0.
- `tamanho_max` igual a `None` significa sem limite.
- Data vazia ou `None` nao bloqueia arquivo.
- Possui testes.

Resultado:

- Filtro por tamanho minimo e maximo validado.
- `tamanho_max == None` continua sem limite.
- Filtro por data aceita limites vazios ou `None`.
- Datas ISO como `2026-05-11 14:30:00` sao convertidas para timestamp.
- Testado em `tests/test_file_utils.py`.

## BM-06 - Integrar todos os filtros de arquivo

Status: Concluido

Prioridade: Alta

Modulo principal: `backupmanager/file_utils.py`

Depende de: `BM-04`, `BM-05`

Objetivo:

Implementar filtro final que combina todas as restricoes.

Funcao esperada:

- `arquivo_atende_restricoes(arquivo, restricoes)`

Criterios de aceite:

- Retorna `True` apenas se o arquivo passar por todos os filtros.
- Possui testes combinando extensao, nome e tamanho.

Resultado:

- `arquivo_atende_restricoes` combina extensao, nome, tamanho e data.
- Rejeita dados invalidos quando arquivo ou restricoes nao sao dicionarios.
- Aceita restricoes vazias quando o arquivo possui metadados validos.
- Testado em `tests/test_file_utils.py`.

---

# Backlog - Backup Real

## BM-07 - Validar perfil antes do backup

Status: Concluido

Prioridade: Alta

Modulo principal: `backupmanager/backup_engine.py`

Depende de: `BM-01`, `BM-02`

Objetivo:

Validar se o perfil tem origens, destinos e operacao correta antes de executar backup.

Criterios de aceite:

- Perfil sem origem retorna erro adequado.
- Perfil sem destino retorna erro adequado.
- Operacao diferente de `copiar` ou `mover` retorna erro.
- Possui testes em `tests/test_backup_engine.py`.

Resultado:

- Criada funcao `validar_perfil_para_backup`.
- Perfil invalido retorna `ERRO_DADOS_INVALIDOS`.
- Perfil sem origem retorna `ERRO_ORIGEM_INVALIDA`.
- Perfil sem destino retorna `ERRO_DESTINO_INVALIDO`.
- Operacao invalida retorna `ERRO_OPERACAO_INVALIDA`.
- `executar_backup` usa a validacao antes de continuar.
- Testado em `tests/test_backup_engine.py`.

## BM-08 - Gerar caminho de destino

Status: Concluido

Prioridade: Alta

Modulo principal: `backupmanager/backup_engine.py`

Depende de: `BM-03`

Objetivo:

Gerar o caminho final do arquivo dentro da pasta destino.

Funcao esperada:

- `gerar_caminho_destino(arquivo, pasta_destino)`

Criterios de aceite:

- Usa o nome original do arquivo.
- Funciona com `pathlib` ou `os.path`.
- Possui teste unitario.

Resultado:

- `gerar_caminho_destino` combina pasta destino com nome do arquivo.
- Usa `arquivo["nome"]` quando disponivel.
- Usa o nome extraido de `arquivo["caminho"]` como fallback.
- Retorna `None` para dados invalidos.
- Testado em `tests/test_backup_engine.py`.

## BM-09 - Criar pasta de destino quando necessario

Status: Concluido

Prioridade: Alta

Modulo principal: `backupmanager/backup_engine.py`

Depende de: `BM-08`

Objetivo:

Garantir que a pasta de destino exista antes da copia.

Funcao esperada:

- `criar_pasta_destino_se_necessario(caminho_destino)`

Criterios de aceite:

- Cria diretorio inexistente.
- Nao falha se diretorio ja existe.
- Retorna codigo padronizado.
- Possui teste com `tempfile`.

Resultado:

- `criar_pasta_destino_se_necessario` cria diretorios pais do caminho de destino.
- Diretorio existente retorna `OK`.
- Caminho vazio ou invalido retorna `ERRO_DESTINO_INVALIDO`.
- Testado em `tests/test_backup_engine.py`.

## BM-10 - Implementar copia de arquivo

Status: Concluido

Prioridade: Alta

Modulo principal: `backupmanager/backup_engine.py`

Depende de: `BM-09`

Objetivo:

Copiar arquivo de origem para destino.

Funcao esperada:

- `copiar_arquivo(origem, destino)`

Criterios de aceite:

- Arquivo original continua existindo.
- Arquivo copiado aparece no destino.
- Conteudo permanece igual.
- Falha retorna codigo de erro, nao quebra a aplicacao.
- Possui teste com `tempfile`.

Resultado:

- `copiar_arquivo` copia arquivos usando `shutil.copy2`.
- Cria a pasta de destino antes da copia.
- Mantem o arquivo original na origem.
- Retorna codigo de erro sem levantar excecao para dados invalidos ou origem inexistente.
- Testado em `tests/test_backup_engine.py`.

## BM-11 - Implementar movimentacao de arquivo

Status: Concluido

Prioridade: Alta

Modulo principal: `backupmanager/backup_engine.py`

Depende de: `BM-09`

Objetivo:

Mover arquivo de origem para destino.

Funcao esperada:

- `mover_arquivo(origem, destino)`

Criterios de aceite:

- Arquivo aparece no destino.
- Arquivo deixa de existir na origem.
- Falha retorna codigo de erro.
- Possui teste com `tempfile`.

Resultado:

- `mover_arquivo` move arquivos usando `shutil.move`.
- Cria a pasta de destino antes da movimentacao.
- Remove o arquivo da origem quando a movimentacao tem sucesso.
- Retorna codigo de erro sem levantar excecao para dados invalidos ou origem inexistente.
- Testado em `tests/test_backup_engine.py`.

## BM-12 - Executar backup para multiplos destinos

Status: Concluido

Prioridade: Alta

Modulo principal: `backupmanager/backup_engine.py`

Depende de: `BM-10`, `BM-11`

Objetivo:

Implementar backup completo considerando varios destinos.

Funcoes esperadas:

- `executar_backup(perfil)`
- `executar_backup_multiplos_destinos(perfil, arquivos_validos)`
- `processar_arquivo_para_destinos(arquivo, destinos, operacao)`

Criterios de aceite:

- Copia arquivo para todos os destinos.
- No modo `mover`, copia para todos os destinos e remove original somente depois.
- Registra erros por arquivo sem cancelar tudo.
- Atualiza contadores no resultado.
- Retorna erro especifico se nenhum arquivo passar nos filtros.
- Possui testes de copia, mover e multiplos destinos.

Resultado:

- `executar_backup` lista arquivos, aplica restricoes e processa arquivos validos.
- `executar_backup_multiplos_destinos` atualiza contadores e status.
- `processar_arquivo_para_destinos` registra erros por arquivo sem cancelar tudo.
- Modo `mover` copia para todos os destinos antes de remover o original.
- Testado em `tests/test_backup_engine.py`.

---

# Backlog - Controller

## BM-13 - Bloquear backup de perfil inativo

Status: Concluido

Prioridade: Media

Modulo principal: `backupmanager/controller.py`

Depende de: `BM-12`

Objetivo:

Impedir backup manual e automatico de perfil inativo.

Criterios de aceite:

- Perfil com `ativo == False` retorna `ERRO_PERFIL_INATIVO`.
- Nenhum historico de backup bem-sucedido deve ser registrado nesse caso.
- Possui teste em `tests/test_controller.py`.

Resultado:

- `controller.executar_backup_do_perfil` bloqueia perfil inativo.
- Perfil inativo nao registra historico nem marca estado alterado.
- Testado em `tests/test_controller.py`.

## BM-14 - Validar origem e destino no controller

Status: Concluido

Prioridade: Media

Modulo principal: `backupmanager/controller.py`

Depende de: `BM-01`

Objetivo:

Validar caminhos ao adicionar origem e destino.

Criterios de aceite:

- Origem inexistente retorna `ERRO_ORIGEM_INVALIDA`.
- Destino invalido retorna `ERRO_DESTINO_INVALIDO`.
- Caminho vazio retorna erro.
- Nao salva JSON imediatamente.
- Possui testes.

Resultado:

- `adicionar_origem_ao_perfil` valida diretorio existente.
- `adicionar_destino_ao_perfil` valida diretorio existente.
- Caminhos vazios retornam erro padronizado.
- Testado em `tests/test_controller.py`.

## BM-15 - Adicionar funcoes de limpeza de historico

Status: Concluido

Prioridade: Baixa

Modulo principal: `backupmanager/controller.py`

Depende de: `BM-17`

Objetivo:

Expor funcoes do `history_manager.py` para a interface.

Funcoes sugeridas:

- `limpar_historico_do_perfil(perfil_id)`
- `limpar_todo_historico()`

Criterios de aceite:

- Altera somente memoria.
- Marca `ESTADO["alterado"] = True`.
- Possui testes.

Resultado:

- Criadas funcoes `limpar_historico_do_perfil` e `limpar_todo_historico`.
- Ambas alteram apenas memoria e marcam estado alterado.
- Testado em `tests/test_controller.py`.

## BM-16 - Adicionar configuracoes gerais

Status: Concluido

Prioridade: Baixa

Modulo principal: `backupmanager/controller.py`

Depende de: nada

Objetivo:

Criar funcoes de leitura e alteracao de `ESTADO["config"]`.

Funcoes sugeridas:

- `obter_configuracoes()`
- `salvar_configuracoes(config)`

Criterios de aceite:

- Altera apenas memoria.
- Marca `ESTADO["alterado"] = True`.
- Nao salva JSON imediatamente.
- Possui testes.

Resultado:

- Criadas funcoes `obter_configuracoes` e `salvar_configuracoes`.
- Configuracoes sao mantidas em memoria ate `finalizar_aplicacao`.
- Testado em `tests/test_controller.py`.

---

# Backlog - Historico

## BM-17 - Padronizar status do historico

Status: Concluido

Prioridade: Media

Modulo principal: `backupmanager/history_manager.py`

Depende de: `BM-12`

Objetivo:

Garantir status claros no historico.

Status sugeridos:

- `sucesso`
- `parcial`
- `erro`
- `sem_arquivos`

Criterios de aceite:

- Historico reflete o resultado do backup.
- Erros sempre sao lista.
- Possui testes.

Resultado:

- Status ficam padronizados em `sucesso`, `parcial`, `erro` e `sem_arquivos`.
- Erros sao normalizados para lista.
- Testado em `tests/test_history_manager.py`.

## BM-18 - Testar limpeza de historico

Status: Concluido

Prioridade: Baixa

Modulo principal: `backupmanager/history_manager.py`

Depende de: nada

Objetivo:

Adicionar cobertura para:

- `limpar_historico_perfil`
- `limpar_todo_historico`

Criterios de aceite:

- Testes confirmam que apenas registros esperados sao removidos.

Resultado:

- Adicionados testes para limpeza por perfil e limpeza total.
- Testado em `tests/test_history_manager.py`.

## BM-19 - Criar resumo de historico por perfil

Status: Concluido

Prioridade: Baixa

Modulo principal: `backupmanager/history_manager.py`

Depende de: `BM-17`

Objetivo:

Criar funcao opcional para resumir execucoes de um perfil.

Funcao sugerida:

- `gerar_resumo_historico_perfil(historico, perfil_id)`

Criterios de aceite:

- Retorna total de execucoes.
- Retorna total de arquivos processados.
- Retorna quantidade de erros.
- Possui testes.

Resultado:

- Criada funcao `gerar_resumo_historico_perfil`.
- Resumo retorna execucoes, arquivos processados e erros.
- Testado em `tests/test_history_manager.py`.

---

# Backlog - Scheduler

## BM-20 - Implementar execucao por intervalo

Status: Concluido

Prioridade: Media

Modulo principal: `backupmanager/scheduler.py`

Depende de: nada

Objetivo:

Verificar se um perfil deve executar com base em `ultima_execucao` e `intervalo_minutos`.

Criterios de aceite:

- `tipo == "intervalo"` respeita intervalo.
- `ultima_execucao == None` permite executar.
- Perfil inativo nao executa.
- Possui testes.

Resultado:

- `deve_executar_por_intervalo` respeita intervalo e ultima execucao.
- Perfil inativo nao executa.
- Testado em `tests/test_scheduler.py`.

## BM-21 - Obter estado atual dos arquivos

Status: Concluido

Prioridade: Media

Modulo principal: `backupmanager/scheduler.py`

Depende de: `BM-02`, `BM-03`

Objetivo:

Criar um dicionario com caminho, tamanho e data de modificacao dos arquivos monitorados.

Funcao esperada:

- `obter_estado_atual_arquivos(perfil)`

Criterios de aceite:

- Retorna dicionario por caminho.
- Ignora origens invalidas sem quebrar.
- Possui testes.

Resultado:

- `obter_estado_atual_arquivos` retorna tamanho e data de modificacao por caminho.
- Origens invalidas sao ignoradas.
- Testado em `tests/test_scheduler.py`.

## BM-22 - Detectar alteracao de arquivos

Status: Concluido

Prioridade: Media

Modulo principal: `backupmanager/scheduler.py`

Depende de: `BM-21`

Objetivo:

Comparar estado antigo e novo.

Funcoes esperadas:

- `comparar_estado_arquivos(estado_antigo, estado_novo)`
- `deve_executar_por_alteracao(perfil)`

Criterios de aceite:

- Detecta arquivo novo.
- Detecta arquivo removido.
- Detecta arquivo modificado.
- Possui testes.

Resultado:

- `comparar_estado_arquivos` compara estados antigos e novos.
- `deve_executar_por_alteracao` detecta mudancas respeitando perfil ativo.
- Testado em `tests/test_scheduler.py`.

## BM-23 - Atualizar estado de arquivos em memoria

Status: Concluido

Prioridade: Media

Modulo principal: `backupmanager/scheduler.py`

Depende de: `BM-21`

Objetivo:

Atualizar `perfil["estado_arquivos"]`.

Criterios de aceite:

- Modifica apenas memoria.
- Nao chama `storage`.
- Retorna `OK`.
- Possui testes.

Resultado:

- `atualizar_estado_arquivos` atualiza `perfil["estado_arquivos"]` em memoria.
- Nao usa persistencia.
- Testado em `tests/test_scheduler.py`.

## BM-24 - Implementar monitoramento simples

Status: Concluido

Prioridade: Baixa

Modulo principal: `backupmanager/scheduler.py`

Depende de: `BM-20`, `BM-22`

Objetivo:

Rodar loop simples com `threading` e chamar callback de backup quando necessario.

Criterios de aceite:

- `iniciar_monitoramento(perfis, callback_backup)` inicia loop.
- `parar_monitoramento()` encerra loop.
- Nao trava a interface.
- Nao salva JSON diretamente.
- Possui teste simples sem loop infinito.

Resultado:

- `iniciar_monitoramento` inicia thread daemon de monitoramento.
- `parar_monitoramento` encerra o loop.
- Callback de backup e atualizado quando um perfil deve executar.
- Testado em `tests/test_scheduler.py`.

---

# Backlog - Interface

## BM-25 - Criar janela de historico

Status: Concluido

Prioridade: Media

Modulo principal: `backupmanager/interface.py`

Depende de: `BM-17`

Objetivo:

Substituir mensagem simples de historico por uma janela com lista ou tabela.

Criterios de aceite:

- Mostra data, status, processados, copiados, movidos e erros.
- Nao acessa historico diretamente; usa controller.
- Funciona sem historico.

Resultado:

- Historico abre em janela propria com lista e detalhes.
- Mostra data, status, processados, copiados, movidos e erros.
- Funciona quando nao ha registros.

## BM-26 - Adicionar campos de data de modificacao

Status: Concluido

Prioridade: Media

Modulo principal: `backupmanager/interface.py`

Depende de: `BM-05`

Objetivo:

Permitir preencher data minima e maxima de modificacao.

Criterios de aceite:

- Campos aparecem no formulario.
- Dados sao enviados em `restricoes`.
- Valores vazios viram `None`.
- Mensagem de erro para formato invalido.

Resultado:

- Interface possui campos de data minima e maxima.
- Valores sao enviados em `restricoes`.
- Datas vazias viram `None`; formato invalido mostra mensagem.

## BM-27 - Melhorar validacao visual do formulario

Status: Concluido

Prioridade: Baixa

Modulo principal: `backupmanager/interface.py`

Depende de: `BM-14`

Objetivo:

Mostrar mensagens mais claras quando dados forem invalidos.

Criterios de aceite:

- Nome vazio mostra mensagem especifica.
- Tamanho invalido mostra mensagem especifica.
- Sem perfil selecionado mostra mensagem especifica.

Resultado:

- Formulario mostra mensagens especificas para perfil ausente, nome vazio, tamanho invalido, intervalo invalido e data invalida.

## BM-28 - Atualizar interface apos backup

Status: Concluido

Prioridade: Baixa

Modulo principal: `backupmanager/interface.py`

Depende de: `BM-12`, `BM-17`

Objetivo:

Atualizar historico/estado visual apos executar backup.

Criterios de aceite:

- Mostra resumo do resultado.
- Historico atualizado aparece ao abrir a janela.

Resultado:

- Execucao de backup mostra resumo de processados, copiados e movidos.
- Historico atualizado aparece na janela de historico.

## BM-29 - Revisar layout final

Status: Concluido

Prioridade: Baixa

Modulo principal: `backupmanager/interface.py`

Depende de: `BM-25`, `BM-26`, `BM-28`

Objetivo:

Refinar espacamento, textos e organizacao visual.

Criterios de aceite:

- Janela abre sem elementos sobrepostos.
- Textos cabem nos botoes.
- Interface continua sem classes.

Resultado:

- Layout recebeu campos de data, janela de historico e botoes mantendo funcoes em dicionarios.
- Interface continua sem classes.

---

# Backlog - Storage e Documentacao

## BM-30 - Reforcar tratamento de erro no storage

Status: Concluido

Prioridade: Baixa

Modulo principal: `backupmanager/storage.py`

Depende de: nada

Objetivo:

Tratar falhas de escrita, permissao e tipos invalidos.

Criterios de aceite:

- `salvar_json` retorna codigo de erro em falhas.
- `carregar_json` continua tratando JSON corrompido.
- Possui testes.

Resultado:

- `salvar_json` trata dados invalidos e falhas de escrita.
- `carregar_json` trata JSON corrompido e falhas de leitura.
- Testado em `tests/test_storage.py`.

## BM-31 - Criar arquivos JSON padrao quando necessario

Status: Concluido

Prioridade: Baixa

Modulo principal: `backupmanager/storage.py`

Depende de: `BM-30`

Objetivo:

Garantir que `data/perfis.json`, `data/historico.json` e `data/config.json` possam ser criados com valores padrao.

Criterios de aceite:

- Pasta `data` e arquivos padrao podem ser criados.
- Nao quebra testes existentes.

Resultado:

- Criada funcao `criar_arquivos_padrao`.
- Inicializacao do controller prepara arquivos padrao antes de carregar dados.
- Testado em `tests/test_storage.py` e `tests/test_controller.py`.

## BM-32 - Atualizar documentacao final

Status: Concluido

Prioridade: Baixa

Modulo principal: `docs/`, `README.md`

Depende de: todas as tarefas principais

Objetivo:

Atualizar documentos com comportamento final do sistema.

Criterios de aceite:

- README explica como executar.
- README explica como testar.
- Documentacao reflete persistencia em memoria.
- Documentacao cita `customtkinter` como biblioteca visual permitida.

Resultado:

- README e documentos de apoio atualizados para o comportamento final do sistema.

---

# Concluido

## Base ja implementada

- Estrutura modular inicial.
- `return_codes.py` com codigos principais.
- `storage.py` com leitura/escrita JSON basica.
- `perfil_manager.py` com operacoes basicas de perfil.
- `history_manager.py` com registro e consulta basica.
- `controller.py` com `ESTADO` em memoria.
- `controller.finalizar_aplicacao()` salvando JSON apenas no encerramento.
- `tests/test_controller.py` cobrindo persistencia em memoria.
- Interface principal com `customtkinter`.
- Documentacao inicial em `docs/`.
- `BM-01`: verificacoes basicas de caminho em `file_utils.py`.
- `BM-02`: listagem de arquivos por origem e multiplas origens.
- `BM-02.1`: visualizacao dos arquivos das origens com status incluido/ignorado.
- `BM-03`: obtencao de extensao e metadados de arquivo.
- `BM-04`: filtros por extensao e nome.
- `BM-05`: filtros por tamanho e data de modificacao.
- `BM-06`: integracao final dos filtros em `arquivo_atende_restricoes`.
- `BM-07`: validacao minima de perfil antes do backup.
- `BM-08`: geracao de caminho de destino.
