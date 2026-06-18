# Arquitetura e Plano de Modularizacao

## Objetivo

Este documento registra a arquitetura atual do BackupManager e define um plano de modularizacao com encapsulamento mais rigido.

O criterio adotado aqui e:

- cada modulo deve expor apenas funcoes de acesso ou operacoes publicas do seu TAD;
- funcoes auxiliares devem ficar internas ao modulo ou em modulo auxiliar dedicado;
- dados internos devem ser manipulados por funcoes, nao diretamente por outros modulos;
- o projeto continua usando dicionarios e funcoes, sem classes e sem dataclasses.

## Arquitetura atual

```text
main.py
  -> interface.py
      -> controller.py
          -> perfil_manager.py
          -> backup_engine.py
              -> file_utils.py
          -> history_manager.py
          -> storage.py
          -> scheduler.py
```

`controller.py` e a fachada principal da aplicacao. A interface deveria conversar quase sempre com o controller, e nao com os modulos internos.

## Avaliacao por modulo

### `main.py`

Responsabilidade:

- ponto de entrada da aplicacao;
- chama `iniciar_interface()`.

Estado:

- bem encapsulado;
- sem necessidade de divisao.

### `return_codes.py`

Responsabilidade:

- definir codigos de retorno;
- traduzir codigo para mensagem de usuario.

Funcoes publicas:

- `obter_mensagem(codigo)`: retorna uma mensagem legivel para um codigo de retorno conhecido ou uma mensagem generica para codigo desconhecido.

Estado:

- adequado para o projeto;
- constantes globais fazem sentido aqui.

### `storage.py`

Responsabilidade:

- ler e gravar JSON;
- garantir arquivos padrao em `data/`.

Funcoes publicas de acesso:

- `carregar_perfis()`;
- `salvar_perfis(perfis)`;
- `carregar_historico()`;
- `salvar_historico(historico)`;
- `carregar_configuracoes()`;
- `salvar_configuracoes(config)`;
- `criar_arquivos_padrao()`.

Funcoes internas candidatas:

- `garantir_pasta_data()`;
- `salvar_json(caminho, dados)`;
- `carregar_json(caminho, valor_padrao)`.

Problema de encapsulamento:

- `PERFIS_PATH`, `HISTORICO_PATH` e `CONFIG_PATH` sao detalhes internos, mas ficam publicos por convenção Python.

Plano:

- manter o modulo pequeno;
- opcionalmente renomear helpers para `_salvar_json`, `_carregar_json`, `_garantir_pasta_data`.

### `perfil_manager.py`

Responsabilidade:

- TAD de perfil;
- criar perfis e estruturas de origem/tipo/destino;
- consultar e alterar dados de perfil em memoria.

Funcoes publicas de TAD:

- `criar_perfil(nome)`: cria um perfil novo no modelo atual, sem persistir em JSON.
- `consultar_perfil(perfis, perfil_id)`: localiza um perfil pelo id dentro de uma lista.
- `listar_perfis(perfis)`: devolve a lista de perfis recebida.
- `alterar_nome_perfil(perfis, perfil_id, novo_nome)`: valida e altera o nome.
- `excluir_perfil(perfis, perfil_id)`: remove um perfil da lista.
- `ativar_perfil(perfis, perfil_id)` e `desativar_perfil(perfis, perfil_id)`: controlam o estado ativo.
- `criar_origem_configurada(caminho)`: cria uma origem no modelo atual.
- `criar_tipo_arquivo(nome, restricoes, destinos)`: cria um tipo de arquivo com filtros e destinos.
- `criar_destino_tipo(caminho, operacao)`: cria destino com operacao propria.

Funcoes legadas mantidas por compatibilidade:

- `adicionar_origem`;
- `remover_origem`;
- `adicionar_destino`;
- `remover_destino`;
- `alterar_operacao`;
- `alterar_restricoes`.

Estado:

- modulo ainda mistura modelo atual e compatibilidade com modelo antigo;
- perfil novo ja deve nascer no modelo atual.

Plano:

- manter compatibilidade enquanto houver dados antigos em `data/perfis.json`;
- depois de uma migracao definitiva, remover as funcoes legadas e seus testes.

### `file_utils.py`

Responsabilidade:

- TAD utilitario de arquivos;
- listar arquivos;
- extrair metadados;
- validar restricoes de arquivo.

Funcoes publicas importantes:

- `listar_arquivos_em_origem(origem)`: lista apenas arquivos diretamente dentro da pasta origem.
- `listar_arquivos_de_origens(origens)`: agrega a listagem de varias origens.
- `obter_metadados_arquivo(caminho)`: retorna nome, caminho, extensao, tamanho e data de modificacao.
- `arquivo_atende_restricoes(arquivo, restricoes)`: aplica todos os filtros configurados ao arquivo.

Funcoes internas candidatas:

- `atende_restricao_extensao`;
- `atende_restricao_nome`;
- `normalizar_regras_nome`;
- `nome_atende_regra`;
- `atende_restricao_tamanho`;
- `atende_restricao_data_modificacao`;
- `converter_data_restricao_para_timestamp`.

Estado:

- bom como modulo puro;
- expõe muitos helpers que poderiam ser internos.

Plano:

- manter funcoes publicas de alto nivel;
- renomear filtros auxiliares para `_atende_restricao_*` quando os testes forem reorganizados para testar pelo contrato `arquivo_atende_restricoes`.

### `backup_engine.py`

Responsabilidade:

- validar perfil para backup;
- filtrar arquivos;
- copiar, mover e recortar arquivos;
- consolidar resultado de execucao.

Funcoes publicas atuais:

- `executar_backup(perfil)`: ponto principal de execucao de backup.
- `validar_perfil_para_backup(perfil)`: valida o contrato minimo para execucao.
- `copiar_arquivo(origem, destino)`: operacao direta de copia.
- `mover_arquivo(origem, destino)`: operacao direta de movimento.

Problemas:

- arquivo grande;
- mistura validacao, selecao de arquivos, operacoes em disco, montagem de resultado e compatibilidade legada;
- muitos helpers ficam publicos por acidente.

Plano de divisao sugerido:

```text
backup_engine.py              # fachada publica: executar_backup, validar_perfil_para_backup
backup_validation.py          # validacao de perfil, origem, tipo e destino
backup_selection.py           # listagem e filtragem de arquivos por origem/tipo
backup_operations.py          # copiar_arquivo, mover_arquivo, recortar/processar destino
backup_result.py              # montar/acumular resultado e erros
```

Ordem recomendada:

1. Extrair montagem/acumulo de resultado para `backup_result.py`.
2. Extrair validacoes para `backup_validation.py`.
3. Extrair operacoes em disco para `backup_operations.py`.
4. Deixar `backup_engine.py` como fachada de orquestracao.

### `history_manager.py`

Responsabilidade:

- TAD de historico de backup;
- criar, consultar, resumir e limpar registros.

Funcoes publicas:

- `registrar_backup(historico, perfil_id, resultado)`: adiciona um registro normalizado.
- `consultar_historico_por_perfil(historico, perfil_id)`: lista registros de um perfil.
- `listar_historico(historico)`: retorna todos os registros.
- `limpar_historico_perfil(historico, perfil_id)`: remove historico de um perfil.
- `limpar_todo_historico(historico)`: remove todos os registros.
- `gerar_resumo_historico_perfil(historico, perfil_id)`: cria resumo agregado.

Funcoes internas candidatas:

- `criar_registro_historico`;
- `normalizar_status`;
- `normalizar_erros`;
- `normalizar_arquivos`.

Estado:

- modulo pequeno e coeso;
- boa chance de ficar como esta, com apenas docstrings melhores.

### `scheduler.py`

Responsabilidade:

- decidir se um perfil deve executar automaticamente;
- monitorar intervalo ou alteracao de arquivos.

Funcoes publicas:

- `deve_executar(perfil)`: decide se um perfil precisa rodar agora.
- `iniciar_monitoramento(perfis, callback_backup)`: inicia loop em thread.
- `parar_monitoramento()`: interrompe monitoramento.
- `atualizar_estado_arquivos(perfil)`: salva estado atual de arquivos no perfil.
- `atualizar_ultima_execucao(perfil)`: registra horario da ultima execucao.

Problemas:

- usa estado global `MONITORAMENTO_ATIVO` e `THREAD_MONITORAMENTO`;
- isso e aceitavel no app atual, mas e menos encapsulado que um TAD ideal.

Plano:

- manter enquanto o monitoramento for simples;
- se crescer, mover estado para um dicionario `monitoramento` passado por funcoes de acesso.

### `controller.py`

Responsabilidade:

- fachada da aplicacao;
- unico modulo que deveria manipular `ESTADO`;
- coordenar storage, perfis, backup, historico e configuracao.

Funcoes publicas principais:

- `inicializar_aplicacao()`: carrega JSON e prepara estado em memoria.
- `finalizar_aplicacao()`: persiste alteracoes pendentes.
- `criar_novo_perfil(nome)`;
- `obter_perfis()`;
- `obter_perfil_por_id(perfil_id)`;
- `salvar_perfil_editado(perfil)`;
- `executar_backup_do_perfil(perfil_id)`;
- `consultar_historico_do_perfil(perfil_id)`;
- `limpar_historico_do_perfil(perfil_id)`;
- `obter_extensoes_disponiveis()`;
- `adicionar_extensao_disponivel(extensao)`.

Problemas:

- `ESTADO` e publico por estar no modulo;
- ainda possui funcoes de acesso antigas para origem/destino/restricoes globais.

Plano:

- interface deve continuar usando apenas controller;
- funcoes antigas de origem/destino global devem ser removidas apos migracao definitiva;
- considerar helpers internos `_validar_payload_perfil` e `_aplicar_payload_perfil` para reduzir `salvar_perfil_editado`.

### `interface.py`

Responsabilidade atual:

- construir janela;
- gerenciar estado visual;
- validar formulario;
- sincronizar estado com controller;
- abrir janelas secundarias;
- formatar historico;
- controlar fluxo de backup.

Problemas:

- arquivo muito grande;
- mistura construcao de widgets, estado da tela, regras de formulario, conversores, historico e comandos;
- e o modulo que mais viola separacao de responsabilidades.

Plano de divisao sugerido:

```text
interface.py                  # fachada: iniciar_interface
ui_theme.py                   # cores, fontes, helpers de widgets
ui_state.py                   # criar_estado_interface, getters/setters do estado visual
ui_profiles.py                # painel de perfis e selecao/exclusao
ui_backup_flow.py             # origens, tipos, destinos e operacoes
ui_restrictions.py            # extensoes, regras de nome, tamanho, data, agendamento
ui_history.py                 # janela de historico e formatadores
ui_actions.py                 # backup em thread, sincronizacao, mensagens
ui_converters.py              # conversores de data, inteiros, intervalo
```

Ordem recomendada:

1. Extrair `ui_theme.py` com constantes e factories de widgets.
2. Extrair `ui_converters.py`, pois tem baixo risco.
3. Extrair `ui_history.py`, pois ja e quase uma ilha.
4. Extrair `ui_restrictions.py`.
5. Extrair `ui_backup_flow.py`.
6. Deixar `interface.py` apenas montando a tela e chamando os submodulos.

Progresso:

- `ui_theme.py` extraido com cores, fontes, factories de widgets, tooltips e helpers de janela.
- `ui_converters.py` extraido com conversores de inteiro, data e intervalo de agendamento.
- `ui_history.py` extraido com janela de historico e formatadores de resumo, arquivos e erros.
- `ui_restrictions.py` extraido com extensoes, regras de nome, tamanho, data, agendamento e normalizacao do tipo de agendamento.
- `ui_backup_flow.py` extraido com criacao e manipulacao do fluxo origem -> tipo -> destino.
- `ui_profiles.py` extraido com painel, lista, criacao, selecao e exclusao de perfis.
- `ui_actions.py` extraido com botoes principais, execucao de backup em thread, sincronizacao, preenchimento/limpeza do formulario e mensagens.
- `backup_result.py` extraido com montagem e acumulacao de resultados, arquivos processados e erros.
- `backup_validation.py` extraido com validacao de perfil, origem, tipo, destino e operacao.
- `interface.py` ficou como fachada de montagem da janela, estado inicial e composicao dos submodulos.
- `perfil_manager.py` recebeu `migrar_perfil_para_modelo_atual` e `migrar_perfis_para_modelo_atual`.
- `controller.py` executa a migracao automaticamente ao carregar os perfis e marca o estado como alterado quando algum perfil legado foi convertido.
- Testes dedicados foram adicionados para `backup_result.py`, `backup_validation.py`, `ui_converters.py` e para o contrato publico dos novos modulos.

## Regras de encapsulamento recomendadas

- Funcoes publicas devem representar operacoes completas do TAD.
- Helpers de calculo ou formatacao devem usar prefixo `_` quando ficarem no mesmo modulo.
- A interface nao deve importar `backup_engine`, `perfil_manager`, `history_manager`, `storage` ou `file_utils`; deve falar com `controller`.
- O controller deve ser o unico modulo a manipular `_ESTADO`.
- Modulos de dominio nao devem chamar `messagebox`, `customtkinter` ou `tkinter`.
- Modulos de persistencia nao devem conhecer regras de backup.

## Estado atual do encapsulamento

Todos os modulos principais declaram `__all__` para explicitar a API publica.

Estado concluido:

- `interface.py` exporta apenas `iniciar_interface`.
- `controller.py` exporta apenas operacoes de fachada; `_ESTADO`, `_EXTENSOES_PADRAO` e `_marcar_estado_alterado` sao internos.
- `backup_engine.py` exporta apenas `executar_backup`, `copiar_arquivo` e `mover_arquivo`.
- `backup_result.py` concentra construcao e acumulacao de resultados.
- `backup_validation.py` concentra validacoes de perfil, origem, tipo, destino e operacao.
- `file_utils.py` manteve como publicas apenas operacoes de arquivo de alto nivel; filtros auxiliares sao internos.
- `storage.py` manteve como publicas apenas operacoes de carga, salvamento e inicializacao de arquivos; caminhos e JSON generico sao internos.
- `scheduler.py` manteve publicas apenas operacoes de monitoramento; comparacoes e leitura de estado sao internas.
- `history_manager.py` manteve publicas operacoes do TAD historico; normalizadores sao internos.
- `ui_backup_flow.py`, `ui_restrictions.py` e `ui_history.py` expõem apenas pontos chamados por `interface.py`; callbacks e formatadores internos usam `_`.
- `return_codes.py` expõe codigos e `obter_mensagem`; o mapa de mensagens e interno.

Pendencias estruturais:

- `interface.py` esta reduzido a composicao da tela principal e inicializacao do estado visual.
- `ui_actions.py` ainda pode ser dividido futuramente se as regras de formulario crescerem: uma divisao natural seria `ui_form_state.py` para preenchimento, limpeza e validacao.
- `controller.py` ainda contem funcoes de compatibilidade para origem/destino/restricao legadas enquanto houver suporte ao modelo antigo.
- `perfil_manager.py` ainda mantem alteradores legados por compatibilidade de chamadas antigas do controller.
- `backup_engine.py` ainda suporta caminho legado de backup como fallback, embora perfis carregados do JSON sejam migrados automaticamente.

## Plano de limpeza de legado

1. Manter leitura tolerante de dados antigos enquanto `data/perfis.json` ainda tiver formato antigo.
2. Migracao explicita concluida: `migrar_perfil_para_modelo_atual(perfil)` e `migrar_perfis_para_modelo_atual(perfis)`.
3. Migracao automatica concluida no carregamento do controller.
4. Depois que os perfis reais ja tiverem sido salvos no formato atual, remover:
   - campos globais `origens`, `destinos`, `operacao`, `restricoes`;
   - funcoes antigas de origem/destino/restricao global no controller e perfil_manager;
   - caminho legado em `backup_engine.executar_backup`.
5. Atualizar testes para validar apenas o modelo atual.

## Prioridade

1. Corrigir chaves e dados corrompidos de restricoes nos perfis existentes.
2. Dividir `backup_engine.py` em operacoes de disco e selecao de arquivos se ele voltar a crescer.
3. Remover funcoes legadas do controller/perfil_manager depois de uma rodada completa com perfis migrados.
4. Reescrever testes que ainda inspecionam privados para cobrir somente contratos publicos.
