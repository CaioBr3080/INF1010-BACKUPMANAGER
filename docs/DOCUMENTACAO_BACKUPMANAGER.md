# Documentação Final do BackupManager



## Visão Geral

BackupManager é uma aplicação desktop local em Python/Tkinter para executar backups manuais por perfis. Cada perfil possui origens; cada origem possui tipos de arquivo; cada tipo possui restrições e destinos; cada destino define sua operação (`copiar`, `mover` ou `recortar`).



O projeto usa TADs representados por dicionários persistidos em JSON, mas o acesso entre módulos deve ocorrer por funções públicas. A regra atual é: somente o módulo dono do TAD conhece suas chaves internas.



## Códigos de Retorno

Os códigos de retorno padronizados ficam em `backupmanager/return_codes.py`. Eles são usados pelos módulos para comunicar sucesso, falhas de validação e erros operacionais sem depender de texto solto. Para exibir uma mensagem legível ao usuário, use `obter_mensagem(codigo)`.

- `OK = 0`: operação realizada com sucesso.

- `ERRO_PERFIL_NAO_ENCONTRADO = 1`: perfil solicitado não existe no estado atual.

- `ERRO_NOME_INVALIDO = 2`: nome de perfil ausente ou inválido.

- `ERRO_ORIGEM_INVALIDA = 3`: origem ausente, inativa, inexistente ou inválida para backup.

- `ERRO_DESTINO_INVALIDO = 4`: destino ausente, inexistente ou inválido para operação.

- `ERRO_SEM_PERMISSAO = 5`: caminho existe, mas o app não possui permissão suficiente para acessar.

- `ERRO_ARQUIVO_NAO_ENCONTRADO = 6`: arquivo esperado não foi encontrado.

- `ERRO_RESTRICAO_INVALIDA = 7`: filtros/restrições possuem valores inválidos.

- `ERRO_OPERACAO_INVALIDA = 8`: operação não reconhecida; atualmente as válidas são `copiar`, `mover` e `recortar`.

- `ERRO_FALHA_AO_COPIAR = 10`: falha durante cópia de arquivo.

- `ERRO_FALHA_AO_MOVER = 11`: falha durante mover/recortar arquivo.

- `ERRO_JSON_CORROMPIDO = 12`: arquivo JSON persistido não pode ser interpretado corretamente.

- `ERRO_BACKUP_SEM_ARQUIVOS = 13`: nenhum arquivo elegível foi encontrado para backup.

- `ERRO_DESTINO_SEM_ESPACO = 14`: destino não possui espaço disponível suficiente.

- `ERRO_PERFIL_INATIVO = 15`: tentativa de executar backup em perfil inativo.

- `ERRO_DADOS_INVALIDOS = 16`: dados de entrada ou TAD em formato inválido.



## Comandos Básicos

- Abrir o app: `python -m backupmanager.main`

- Rodar testes: `python -m pytest -q`

- Validar sintaxe: `python -m compileall backupmanager tests`

- Instalar dependências de desenvolvimento: `pip install -r requirements-dev.txt`



## Dados Persistidos

- `data/perfis.json`: perfis, origens, tipos, restrições, destinos e estado ativo/inativo.

- `data/config.json`: configurações globais, principalmente extensões customizadas disponíveis na UI.



## TADs Principais e Obrigações

- Perfil: identifica um conjunto de backup, guarda nome, estado ativo e origens configuradas. Dono: `domain/perfil_manager.py`.

- Origem configurada: guarda pasta de entrada, estado ativo e tipos de arquivo. Dono: `domain/perfil_manager.py`.

- Tipo de arquivo: agrupa nome, ativo/inativo, restrições e destinos. Dono: `domain/perfil_manager.py`.

- Destino do tipo: guarda pasta de saída e operação. Dono: `domain/perfil_manager.py`.

- Restrições: filtros por extensão, nome, tamanho e data. Dono: `domain/perfil_manager.py`; aplicação dos filtros em `engine/file_utils.py`.

- Metadados de arquivo: caminho, nome, extensão, tamanho e data de modificação de um arquivo real. Dono: `engine/file_utils.py`.

- Resultado de backup: status, contadores, registros e erros. Dono: `domain/backup_result.py`.

- Estado da aplicação: perfis/config em memória e flag de alteração. Dono: `controller.py`.

- Estado da interface: widgets, seleções e edições em andamento. Dono operacional: `ui/ui_state.py`, com uso pelos demais módulos em `ui/`.



## Fluxo Geral da Aplicação

1. Entrada: `main.main()` chama `ui.interface.iniciar_interface()`.

2. Inicialização: a UI chama `controller.inicializar_aplicacao()`, que pede a `infra/storage.py` para carregar JSONs ou devolver valores padrao em memoria quando eles nao existem. A inicializacao nao cria nem grava JSONs.

3. Edição visual: `ui.profiles`, `ui.backup_flow` e `ui.restrictions` manipulam o TAD Estado da interface principalmente por `ui.ui_state`; Perfil, Origem, Tipo, Destino e Restrições continuam sendo criados/alterados por funções de `perfil_manager`.

4. Aplicar/backup: `ui.actions.executar_backup_interface()` sincroniza o formulário com `controller.salvar_perfil_editado()` e chama `controller.executar_backup_do_perfil()`.

5. Validação: `engine.backup_engine.executar_backup()` chama `domain.backup_validation.validar_perfil_para_backup()` usando acessores do TAD Perfil.

6. Seleção de arquivos: `backup_engine` pede arquivos a `engine.file_utils`, coleta metadados e aplica restrições por tipo.

7. Operação de disco: `backup_engine` copia/move/recorta cada arquivo para destinos configurados.

8. Resultado: `domain.backup_result` acumula contadores, registros e erros. A UI mostra o resumo final.

9. Fechamento: `controller.finalizar_aplicacao()` grava perfis/configurações se o estado foi alterado.



## Encapsulamento Atual

- Todos os módulos de aplicação declaram `__all__`.

- Não há classes, dataclasses, structs, `NamedTuple`, `TypedDict` ou `unittest` em `backupmanager` ou `tests`.

- O TAD Estado da aplicação fica concentrado em `controller.py`, dentro de `_ESTADO`. Por convenção e por uso no projeto, `_ESTADO` é interno ao controller: outros módulos pedem operações ao controller, e somente o controller altera diretamente esse dicionário.

- O controller funciona como fachada da aplicação: a UI chama funções públicas como `criar_novo_perfil`, `salvar_perfil_editado`, `executar_backup_do_perfil`, `obter_perfis` e `obter_perfil_por_id`; o controller delega criação/validação/mutação de perfis ao `perfil_manager`, delega execução ao `backup_engine` e delega persistência ao `storage`.

- O JSON está encapsulado em `infra/storage.py`. A interface e os módulos de domínio não abrem `perfis.json` ou `config.json` diretamente.

- O acesso direto ao estado visual da UI foi reduzido com `ui/ui_state.py`. Operações que antes ficavam espalhadas, como adicionar/remover origem em `estado_interface["origens_configuradas"]`, agora passam por funções como `adicionar_origem_configurada`, `remover_origem_configurada_por_indice`, `obter_origem_selecionada` e `definir_origens_configuradas`.

- A auditoria textual não encontrou acesso direto a `perfil.get`, `origem.get`, `tipo.get`, `destino.get`, `restricoes.get`, `resultado.get` ou `arquivo.get` fora dos módulos donos dos TADs.

- A auditoria textual também não encontrou escrita direta em `perfil[...]` fora de `domain/perfil_manager.py` nem escrita direta em `arquivo[...]` fora de `engine/file_utils.py`.

- Ressalva importante: algumas funções públicas ainda retornam TADs ou listas reais mutáveis, por exemplo perfis/origens/tipos/destinos. Isso não significa que `_ESTADO` seja acessado diretamente fora do controller, mas exige disciplina dos chamadores para não alterar estruturas retornadas sem passar pelas funções apropriadas. Em uma versão mais rígida, esses acessos poderiam retornar cópias ou ser substituídos por funções mais específicas.

## Mudanças recentes de encapsulamento

- `ui_state.py` passou a ser o ponto central para o TAD Estado da interface relacionado a origens configuradas e seleção de origem.

- A documentação agora distingue dois casos diferentes:
  - acesso direto proibido, como `controller._ESTADO[...]` fora do controller;
  - vazamento indireto possível, quando uma função retorna uma lista/dicionário interno mutável.

- O `_ESTADO` foi classificado como bem encapsulado enquanto apenas o controller o manipula diretamente.

- O principal risco restante de encapsulamento não está em classes/structs, pois elas não são usadas, mas sim em getters que retornam estruturas mutáveis e podem permitir alteração externa se usados de forma incorreta.

## Pasta `backupmanager`

### Módulo `controller.py`

Resumo: Camada de controle entre interface e módulos internos. O módulo é o dono do TAD Estado da aplicação (`_ESTADO`). Outros módulos não devem acessar `_ESTADO` diretamente; eles pedem operações ao controller, que consulta/delega para os módulos corretos e atualiza o estado interno quando necessário.

TADs/obrigações do módulo: Estado da aplicação (`_ESTADO`), Perfil, Configurações, Resultado de backup, Metadados de arquivo.

#### `_marcar_estado_alterado()`
- Visibilidade: interna.
- Objetivo: Marca que o estado em memória possui alterações não persistidas.
- Parâmetros:
    - nenhum parâmetro.
- Possíveis retornos:
    - `OK`: sucesso da operação.
- TADs envolvidos: Estado da aplicação (_ESTADO), Perfil, Configurações, Resultado de backup, Metadados de arquivo.

#### `inicializar_aplicacao()`
- Visibilidade: pública.
- Objetivo: Inicializa o estado em memória da aplicação lendo JSONs existentes ou usando valores padrao em memoria quando eles nao existem.
- Parâmetros:
    - nenhum parâmetro.
- Possíveis retornos:
    - `OK`: sucesso da operação.
    - `codigo_perfis`: código de retorno propagado de chamada interna.
    - `codigo_config`: código de retorno propagado de chamada interna.
- TADs envolvidos: Estado da aplicação (_ESTADO), Perfil, Configurações, Resultado de backup, Metadados de arquivo.

#### `finalizar_aplicacao()`
- Visibilidade: pública.
- Objetivo: Persiste em JSON as alterações acumuladas em memória.
- Parâmetros:
    - nenhum parâmetro.
- Possíveis retornos:
    - `OK`: sucesso da operação.
    - `codigo`: código de retorno propagado de chamada interna.
- TADs envolvidos: Estado da aplicação (_ESTADO), Perfil, Configurações, Resultado de backup, Metadados de arquivo.

#### `criar_novo_perfil(nome)`
- Visibilidade: pública.
- Objetivo: Cria um perfil novo e o registra no estado em memória.
- Parâmetros:
    - `nome`: nome informado pelo usuário ou nome interno do TAD.
- Possíveis retornos:
    - `(OK, perfil)`: tupla de retorno; normalmente combina código e dado/resultado.
    - `(codigo, None)`: tupla de retorno; normalmente combina código e dado/resultado.
- TADs envolvidos: Estado da aplicação (_ESTADO), Perfil, Configurações, Resultado de backup, Metadados de arquivo.

#### `obter_perfis()`
- Visibilidade: pública.
- Objetivo: Retorna todos os perfis mantidos em memória por meio do contrato público do controller. A função não expõe `_ESTADO` diretamente, mas retorna os perfis obtidos via `perfil_manager.listar_perfis`; por isso os chamadores devem tratar o retorno como dado de consulta/edição controlada, não como local para mutação arbitrária.
- Parâmetros:
    - nenhum parâmetro.
- Possíveis retornos:
    - `perfil_manager.listar_perfis(_ESTADO['perfis'])`: retorno delegado para outra função.
- TADs envolvidos: Estado da aplicação (_ESTADO), Perfil, Configurações, Resultado de backup, Metadados de arquivo.

#### `obter_perfil_por_id(perfil_id)`
- Visibilidade: pública.
- Objetivo: Consulta um perfil em memória pelo identificador. A busca ocorre dentro do controller sobre `_ESTADO["perfis"]`; o acesso externo continua sendo feito por esta função pública.
- Parâmetros:
    - `perfil_id`: identificador único de um perfil.
- Possíveis retornos:
    - `perfil_manager.consultar_perfil(_ESTADO['perfis'], perfil_id)`: retorno delegado para outra função.
- TADs envolvidos: Estado da aplicação (_ESTADO), Perfil, Configurações, Resultado de backup, Metadados de arquivo.

#### `salvar_perfil_editado(perfil)`
- Visibilidade: pública.
- Objetivo: Aplica ao estado em memória os dados editados de um perfil delegando a mutacao do TAD Perfil para `perfil_manager.aplicar_edicao_perfil`.
- Parâmetros:
    - `perfil`: TAD Perfil, dicionário persistido com id, nome, ativo e origens configuradas.
- Possíveis retornos:
    - `OK`: sucesso da operação.
    - `ERRO_DADOS_INVALIDOS`: entrada com tipo, formato ou valor inválido.
    - `codigo`: código de retorno propagado de chamada interna.
- TADs envolvidos: Estado da aplicação (_ESTADO), Perfil, Configurações, Resultado de backup, Metadados de arquivo.

#### `excluir_perfil_por_id(perfil_id)`
- Visibilidade: pública.
- Objetivo: Remove um perfil do estado em memória.
- Parâmetros:
    - `perfil_id`: identificador único de um perfil.
- Possíveis retornos:
    - `codigo`: código de retorno propagado de chamada interna.
- TADs envolvidos: Estado da aplicação (_ESTADO), Perfil, Configurações, Resultado de backup, Metadados de arquivo.

#### `ativar_perfil_por_id(perfil_id)`
- Visibilidade: pública.
- Objetivo: Ativa um perfil para permitir execuções de backup.
- Parâmetros:
    - `perfil_id`: identificador único de um perfil.
- Possíveis retornos:
    - `codigo`: código de retorno propagado de chamada interna.
- TADs envolvidos: Estado da aplicação (_ESTADO), Perfil, Configurações, Resultado de backup, Metadados de arquivo.

#### `desativar_perfil_por_id(perfil_id)`
- Visibilidade: pública.
- Objetivo: Desativa um perfil para impedir execuções de backup.
- Parâmetros:
    - `perfil_id`: identificador único de um perfil.
- Possíveis retornos:
    - `codigo`: código de retorno propagado de chamada interna.
- TADs envolvidos: Estado da aplicação (_ESTADO), Perfil, Configurações, Resultado de backup, Metadados de arquivo.

#### `executar_backup_do_perfil(perfil_id)`
- Visibilidade: pública.
- Objetivo: Executa o backup do perfil informado.
- Parâmetros:
    - `perfil_id`: identificador único de um perfil.
- Possíveis retornos:
    - `(codigo_backup, resultado)`: tupla de retorno; normalmente combina código e dado/resultado.
    - `(codigo, None)`: tupla de retorno; normalmente combina código e dado/resultado.
    - `(ERRO_PERFIL_INATIVO, None)`: tupla de retorno; normalmente combina código e dado/resultado.
- TADs envolvidos: Estado da aplicação (_ESTADO), Perfil, Configurações, Resultado de backup, Metadados de arquivo.

#### `obter_arquivos_do_perfil(perfil_id)`
- Visibilidade: pública.
- Objetivo: Lista arquivos do perfil e informa quais entram no backup.
- Parâmetros:
    - `perfil_id`: identificador único de um perfil.
- Possíveis retornos:
    - `obter_arquivos_do_perfil_configurado(perfil)`: retorno delegado para outra função.
    - `(codigo, None)`: tupla de retorno; normalmente combina código e dado/resultado.
- TADs envolvidos: Estado da aplicação (_ESTADO), Perfil, Configurações, Resultado de backup, Metadados de arquivo.

#### `obter_arquivos_do_perfil_configurado(perfil)`
- Visibilidade: pública.
- Objetivo: Lista arquivos de um perfil já carregado no modelo atual.
- Parâmetros:
    - `perfil`: TAD Perfil, dicionário persistido com id, nome, ativo e origens configuradas.
- Possíveis retornos:
    - `(OK, arquivos)`: tupla de retorno; normalmente combina código e dado/resultado.
- TADs envolvidos: Estado da aplicação (_ESTADO), Perfil, Configurações, Resultado de backup, Metadados de arquivo.

#### `obter_configuracoes()`
- Visibilidade: pública.
- Objetivo: Retorna o dicionário de configurações gerais em memória.
- Parâmetros:
    - nenhum parâmetro.
- Possíveis retornos:
    - `(OK, _ESTADO['config'])`: tupla de retorno; normalmente combina código e dado/resultado.
- TADs envolvidos: Estado da aplicação (_ESTADO), Perfil, Configurações, Resultado de backup, Metadados de arquivo.

#### `salvar_configuracoes(config)`
- Visibilidade: pública.
- Objetivo: Substitui as configurações gerais mantidas em memória.
- Parâmetros:
    - `config`: TAD Configurações gerais da aplicação.
- Possíveis retornos:
    - `OK`: sucesso da operação.
    - `ERRO_DADOS_INVALIDOS`: entrada com tipo, formato ou valor inválido.
- TADs envolvidos: Estado da aplicação (_ESTADO), Perfil, Configurações, Resultado de backup, Metadados de arquivo.

#### `normalizar_extensao(extensao)`
- Visibilidade: pública.
- Objetivo: Normaliza texto de extensão para o formato `.ext`.
- Parâmetros:
    - `extensao`: extensão textual, com ou sem ponto inicial.
- Possíveis retornos:
    - `extensao`: valor calculado pela função.
    - `None`: ausência válida de dado ou falha sem objeto retornável.
- TADs envolvidos: Estado da aplicação (_ESTADO), Perfil, Configurações, Resultado de backup, Metadados de arquivo.

#### `obter_extensoes_disponiveis()`
- Visibilidade: pública.
- Objetivo: Retorna a lista ordenada de extensões disponíveis na interface.
- Parâmetros:
    - nenhum parâmetro.
- Possíveis retornos:
    - `(OK, sorted(extensoes))`: tupla de retorno; normalmente combina código e dado/resultado.
- TADs envolvidos: Estado da aplicação (_ESTADO), Perfil, Configurações, Resultado de backup, Metadados de arquivo.

#### `adicionar_extensao_disponivel(extensao)`
- Visibilidade: pública.
- Objetivo: Adiciona uma extensão customizada a configuração em memória.
- Parâmetros:
    - `extensao`: extensão textual, com ou sem ponto inicial.
- Possíveis retornos:
    - `OK`: sucesso da operação.
    - `ERRO_DADOS_INVALIDOS`: entrada com tipo, formato ou valor inválido.
    - `codigo`: código de retorno propagado de chamada interna.
- TADs envolvidos: Estado da aplicação (_ESTADO), Perfil, Configurações, Resultado de backup, Metadados de arquivo.

## Pasta `backupmanager/domain`

### Módulo `backup_result.py`

Resumo: Montagem e acumulação de resultados de backup.

TADs/obrigações do módulo: Resultado geral de backup, Resultado individual de arquivo, Registro de arquivo, Erro de arquivo.

#### `montar_resultado_backup(perfil_id)`
- Visibilidade: pública.
- Objetivo: Cria o resultado base de uma execução de backup.
- Parâmetros:
    - `perfil_id`: identificador único de um perfil.
- Possíveis retornos:
    - `{'perfil_id': perfil_id, 'status': 'nao_executado', 'arquivos_processados': 0, 'arquivos_copiados': 0, 'arquivos_movidos': 0, 'arquivos_recortados': 0, 'arquivos': [], 'erros': []}`: novo dicionário/TAD montado pela função.
- TADs envolvidos: Resultado geral de backup, Resultado individual de arquivo, Registro de arquivo, Erro de arquivo.

#### `montar_resultado_arquivo()`
- Visibilidade: pública.
- Objetivo: Cria o resultado acumulado para o processamento de um arquivo.
- Parâmetros:
    - nenhum parâmetro.
- Possíveis retornos:
    - `{'codigo': OK, 'processado': False, 'arquivos_copiados': 0, 'arquivos_movidos': 0, 'arquivos_recortados': 0, 'arquivos': [], 'erros': []}`: novo dicionário/TAD montado pela função.
- TADs envolvidos: Resultado geral de backup, Resultado individual de arquivo, Registro de arquivo, Erro de arquivo.

#### `definir_status_resultado(resultado, status)`
- Visibilidade: pública.
- Objetivo: Altera o status textual do resultado geral.
- Parâmetros:
    - `resultado`: TAD Resultado geral de backup.
    - `status`: parâmetro usado pela função conforme o contexto do módulo.
- Possíveis retornos:
    - `resultado`: valor calculado pela função.
- TADs envolvidos: Resultado geral de backup, Resultado individual de arquivo, Registro de arquivo, Erro de arquivo.

#### `obter_status_resultado(resultado)`
- Visibilidade: pública.
- Objetivo: Retorna o status textual do resultado geral.
- Parâmetros:
    - `resultado`: TAD Resultado geral de backup.
- Possíveis retornos:
    - `resultado.get('status', '')`: retorno delegado para outra função.
- TADs envolvidos: Resultado geral de backup, Resultado individual de arquivo, Registro de arquivo, Erro de arquivo.

#### `obter_arquivos_processados(resultado)`
- Visibilidade: pública.
- Objetivo: Retorna a quantidade de arquivos processados no resultado geral.
- Parâmetros:
    - `resultado`: TAD Resultado geral de backup.
- Possíveis retornos:
    - `resultado.get('arquivos_processados', 0)`: retorno delegado para outra função.
- TADs envolvidos: Resultado geral de backup, Resultado individual de arquivo, Registro de arquivo, Erro de arquivo.

#### `resultado_possui_erros(resultado)`
- Visibilidade: pública.
- Objetivo: Indica se o resultado geral possui erros registrados.
- Parâmetros:
    - `resultado`: TAD Resultado geral de backup.
- Possíveis retornos:
    - `bool(resultado.get('erros', []))`: booleano calculado pela condição.
- TADs envolvidos: Resultado geral de backup, Resultado individual de arquivo, Registro de arquivo, Erro de arquivo.

#### `obter_arquivos_resultado(resultado)`
- Visibilidade: pública.
- Objetivo: Retorna os registros de arquivos do resultado geral.
- Parâmetros:
    - `resultado`: TAD Resultado geral de backup.
- Possíveis retornos:
    - `resultado.get('arquivos', [])`: retorno delegado para outra função.
- TADs envolvidos: Resultado geral de backup, Resultado individual de arquivo, Registro de arquivo, Erro de arquivo.

#### `obter_erros_resultado(resultado)`
- Visibilidade: pública.
- Objetivo: Retorna os erros do resultado geral.
- Parâmetros:
    - `resultado`: TAD Resultado geral de backup.
- Possíveis retornos:
    - `resultado.get('erros', [])`: retorno delegado para outra função.
- TADs envolvidos: Resultado geral de backup, Resultado individual de arquivo, Registro de arquivo, Erro de arquivo.

#### `obter_contador_resultado(resultado, nome)`
- Visibilidade: pública.
- Objetivo: Retorna um contador numérico do resultado geral.
- Parâmetros:
    - `resultado`: TAD Resultado geral de backup.
    - `nome`: nome informado pelo usuário ou nome interno do TAD.
- Possíveis retornos:
    - `resultado.get(nome, 0)`: retorno delegado para outra função.
- TADs envolvidos: Resultado geral de backup, Resultado individual de arquivo, Registro de arquivo, Erro de arquivo.

#### `aplicar_resultado_arquivo(resultado, resultado_arquivo)`
- Visibilidade: pública.
- Objetivo: Acumula o resultado de um arquivo no resultado geral.
- Parâmetros:
    - `resultado`: TAD Resultado geral de backup.
    - `resultado_arquivo`: TAD Resultado individual de arquivo.
- Possíveis retornos:
    - `resultado`: valor calculado pela função.
- TADs envolvidos: Resultado geral de backup, Resultado individual de arquivo, Registro de arquivo, Erro de arquivo.

#### `resultado_arquivo_foi_processado(resultado_arquivo)`
- Visibilidade: pública.
- Objetivo: Indica se o resultado individual processou o arquivo.
- Parâmetros:
    - `resultado_arquivo`: TAD Resultado individual de arquivo.
- Possíveis retornos:
    - `bool(resultado_arquivo.get('processado', False))`: booleano calculado pela condição.
- TADs envolvidos: Resultado geral de backup, Resultado individual de arquivo, Registro de arquivo, Erro de arquivo.

#### `obter_codigo_resultado_arquivo(resultado_arquivo)`
- Visibilidade: pública.
- Objetivo: Retorna o código de retorno do resultado individual.
- Parâmetros:
    - `resultado_arquivo`: TAD Resultado individual de arquivo.
- Possíveis retornos:
    - `resultado_arquivo.get('codigo', OK)`: código de sucesso junto do TAD Resultado.
- TADs envolvidos: Resultado geral de backup, Resultado individual de arquivo, Registro de arquivo, Erro de arquivo.

#### `obter_copiados_resultado_arquivo(resultado_arquivo)`
- Visibilidade: pública.
- Objetivo: Retorna o contador de copias do resultado individual.
- Parâmetros:
    - `resultado_arquivo`: TAD Resultado individual de arquivo.
- Possíveis retornos:
    - `resultado_arquivo.get('arquivos_copiados', 0)`: retorno delegado para outra função.
- TADs envolvidos: Resultado geral de backup, Resultado individual de arquivo, Registro de arquivo, Erro de arquivo.

#### `obter_movidos_resultado_arquivo(resultado_arquivo)`
- Visibilidade: pública.
- Objetivo: Retorna o contador de movimentos do resultado individual.
- Parâmetros:
    - `resultado_arquivo`: TAD Resultado individual de arquivo.
- Possíveis retornos:
    - `resultado_arquivo.get('arquivos_movidos', 0)`: retorno delegado para outra função.
- TADs envolvidos: Resultado geral de backup, Resultado individual de arquivo, Registro de arquivo, Erro de arquivo.

#### `obter_recortados_resultado_arquivo(resultado_arquivo)`
- Visibilidade: pública.
- Objetivo: Retorna o contador de recortes do resultado individual.
- Parâmetros:
    - `resultado_arquivo`: TAD Resultado individual de arquivo.
- Possíveis retornos:
    - `resultado_arquivo.get('arquivos_recortados', 0)`: retorno delegado para outra função.
- TADs envolvidos: Resultado geral de backup, Resultado individual de arquivo, Registro de arquivo, Erro de arquivo.

#### `obter_erros_resultado_arquivo(resultado_arquivo)`
- Visibilidade: pública.
- Objetivo: Retorna a lista de erros do resultado individual.
- Parâmetros:
    - `resultado_arquivo`: TAD Resultado individual de arquivo.
- Possíveis retornos:
    - `resultado_arquivo.get('erros', [])`: retorno delegado para outra função.
- TADs envolvidos: Resultado geral de backup, Resultado individual de arquivo, Registro de arquivo, Erro de arquivo.

#### `definir_codigo_resultado_arquivo(resultado_arquivo, codigo)`
- Visibilidade: pública.
- Objetivo: Altera o código de retorno do resultado individual.
- Parâmetros:
    - `resultado_arquivo`: TAD Resultado individual de arquivo.
    - `codigo`: código de retorno de return_codes.py.
- Possíveis retornos:
    - `resultado_arquivo`: valor calculado pela função.
- TADs envolvidos: Resultado geral de backup, Resultado individual de arquivo, Registro de arquivo, Erro de arquivo.

#### `definir_processado_resultado_arquivo(resultado_arquivo, processado)`
- Visibilidade: pública.
- Objetivo: Marca se o resultado individual processou o arquivo.
- Parâmetros:
    - `resultado_arquivo`: TAD Resultado individual de arquivo.
    - `processado`: parâmetro usado pela função conforme o contexto do módulo.
- Possíveis retornos:
    - `resultado_arquivo`: valor calculado pela função.
- TADs envolvidos: Resultado geral de backup, Resultado individual de arquivo, Registro de arquivo, Erro de arquivo.

#### `somar_copiados_resultado_arquivo(resultado_arquivo, quantidade=1)`
- Visibilidade: pública.
- Objetivo: Soma arquivos copiados ao resultado individual.
- Parâmetros:
    - `resultado_arquivo`: TAD Resultado individual de arquivo.
    - `quantidade`: incremento numérico aplicado a contador.
- Possíveis retornos:
    - `resultado_arquivo`: valor calculado pela função.
- TADs envolvidos: Resultado geral de backup, Resultado individual de arquivo, Registro de arquivo, Erro de arquivo.

#### `somar_movidos_resultado_arquivo(resultado_arquivo, quantidade=1)`
- Visibilidade: pública.
- Objetivo: Soma arquivos movidos ao resultado individual.
- Parâmetros:
    - `resultado_arquivo`: TAD Resultado individual de arquivo.
    - `quantidade`: incremento numérico aplicado a contador.
- Possíveis retornos:
    - `resultado_arquivo`: valor calculado pela função.
- TADs envolvidos: Resultado geral de backup, Resultado individual de arquivo, Registro de arquivo, Erro de arquivo.

#### `somar_recortados_resultado_arquivo(resultado_arquivo, quantidade=1)`
- Visibilidade: pública.
- Objetivo: Soma arquivos recortados ao resultado individual.
- Parâmetros:
    - `resultado_arquivo`: TAD Resultado individual de arquivo.
    - `quantidade`: incremento numérico aplicado a contador.
- Possíveis retornos:
    - `resultado_arquivo`: valor calculado pela função.
- TADs envolvidos: Resultado geral de backup, Resultado individual de arquivo, Registro de arquivo, Erro de arquivo.

#### `zerar_movidos_resultado_arquivo(resultado_arquivo)`
- Visibilidade: pública.
- Objetivo: Zera o contador de movimentos do resultado individual.
- Parâmetros:
    - `resultado_arquivo`: TAD Resultado individual de arquivo.
- Possíveis retornos:
    - `resultado_arquivo`: valor calculado pela função.
- TADs envolvidos: Resultado geral de backup, Resultado individual de arquivo, Registro de arquivo, Erro de arquivo.

#### `adicionar_registro_resultado_arquivo(resultado_arquivo, registro)`
- Visibilidade: pública.
- Objetivo: Adiciona um registro de arquivo ao resultado individual.
- Parâmetros:
    - `resultado_arquivo`: TAD Resultado individual de arquivo.
    - `registro`: registro detalhado de arquivo processado.
- Possíveis retornos:
    - `resultado_arquivo`: valor calculado pela função.
- TADs envolvidos: Resultado geral de backup, Resultado individual de arquivo, Registro de arquivo, Erro de arquivo.

#### `adicionar_erro_resultado_arquivo(resultado_arquivo, erro)`
- Visibilidade: pública.
- Objetivo: Adiciona um erro ao resultado individual.
- Parâmetros:
    - `resultado_arquivo`: TAD Resultado individual de arquivo.
    - `erro`: erro capturado ou registro de erro.
- Possíveis retornos:
    - `resultado_arquivo`: valor calculado pela função.
- TADs envolvidos: Resultado geral de backup, Resultado individual de arquivo, Registro de arquivo, Erro de arquivo.

#### `resultado_arquivo_possui_erros(resultado_arquivo)`
- Visibilidade: pública.
- Objetivo: Indica se o resultado individual possui erros.
- Parâmetros:
    - `resultado_arquivo`: TAD Resultado individual de arquivo.
- Possíveis retornos:
    - `bool(resultado_arquivo.get('erros', []))`: booleano calculado pela condição.
- TADs envolvidos: Resultado geral de backup, Resultado individual de arquivo, Registro de arquivo, Erro de arquivo.

#### `obter_registros_resultado_arquivo(resultado_arquivo)`
- Visibilidade: pública.
- Objetivo: Retorna os registros do resultado individual.
- Parâmetros:
    - `resultado_arquivo`: TAD Resultado individual de arquivo.
- Possíveis retornos:
    - `resultado_arquivo.get('arquivos', [])`: retorno delegado para outra função.
- TADs envolvidos: Resultado geral de backup, Resultado individual de arquivo, Registro de arquivo, Erro de arquivo.

#### `marcar_registros_como_recorte(resultado_arquivo)`
- Visibilidade: pública.
- Objetivo: Troca operação `mover` por `recortar` nos registros individuais.
- Parâmetros:
    - `resultado_arquivo`: TAD Resultado individual de arquivo.
- Possíveis retornos:
    - `resultado_arquivo`: valor calculado pela função.
- TADs envolvidos: Resultado geral de backup, Resultado individual de arquivo, Registro de arquivo, Erro de arquivo.

#### `montar_registro_arquivo(arquivo, destino, operacao, codigo)`
- Visibilidade: pública.
- Objetivo: Monta o registro detalhado de um arquivo processado.
- Parâmetros:
    - `arquivo`: TAD Metadados de Arquivo.
    - `destino`: TAD Destino ou caminho final, conforme contexto.
    - `operacao`: modo de transferência: copiar, mover ou recortar.
    - `codigo`: código de retorno de return_codes.py.
- Possíveis retornos:
    - `{'nome': file_utils.obter_nome_arquivo(arquivo), 'extensao': file_utils.obter_extensao_arquivo(arquivo), 'tipo': file_utils.obter_nome_tipo_arquivo(arquivo), 'tamanho': file_utils.obter_tamanho_arquivo(arquivo), 'origem': file_utils.obter_caminho_arquivo(arquivo), 'destino': str(destino), 'operacao': operacao, 'status': 'sucesso' if codigo == OK else 'erro', 'codigo': codigo}`: novo dicionário/TAD montado pela função.
- TADs envolvidos: Resultado geral de backup, Resultado individual de arquivo, Registro de arquivo, Erro de arquivo.

#### `montar_erro_arquivo(arquivo, destino, codigo)`
- Visibilidade: pública.
- Objetivo: Monta o registro simples de erro associado a um arquivo.
- Parâmetros:
    - `arquivo`: TAD Metadados de Arquivo.
    - `destino`: TAD Destino ou caminho final, conforme contexto.
    - `codigo`: código de retorno de return_codes.py.
- Possíveis retornos:
    - `{'arquivo': nome, 'destino': str(destino), 'codigo': codigo}`: novo dicionário/TAD montado pela função.
- TADs envolvidos: Resultado geral de backup, Resultado individual de arquivo, Registro de arquivo, Erro de arquivo.

### Módulo `backup_validation.py`

Resumo: Validação de perfis, origens, tipos, destinos e operações de backup.

TADs/obrigações do módulo: Perfil, Origem configurada, Tipo de arquivo, Destino do tipo.

#### `validar_perfil_para_backup(perfil)`
- Visibilidade: pública.
- Objetivo: Valida o contrato mínimo para executar backup.
- Parâmetros:
    - `perfil`: TAD Perfil, dicionário persistido com id, nome, ativo e origens configuradas.
- Possíveis retornos:
    - `validar_perfil_configurado_para_backup(perfil)`: retorno delegado para outra função.
    - `ERRO_DADOS_INVALIDOS`: entrada com tipo, formato ou valor inválido.
- TADs envolvidos: Perfil, Origem configurada, Tipo de arquivo, Destino do tipo.

#### `validar_perfil_configurado_para_backup(perfil)`
- Visibilidade: pública.
- Objetivo: Valida um perfil no modelo origem -> tipo -> destino.
- Parâmetros:
    - `perfil`: TAD Perfil, dicionário persistido com id, nome, ativo e origens configuradas.
- Possíveis retornos:
    - `OK`: sucesso da operação.
    - `ERRO_ORIGEM_INVALIDA`: origem ausente, vazia ou estruturalmente inválida.
    - `ERRO_DESTINO_INVALIDO`: destino ausente, vazio ou estruturalmente inválido.
    - `ERRO_DADOS_INVALIDOS`: entrada com tipo, formato ou valor inválido.
    - `codigo`: código de retorno propagado de chamada interna.
- TADs envolvidos: Perfil, Origem configurada, Tipo de arquivo, Destino do tipo.

#### `validar_destinos_do_tipo(tipo)`
- Visibilidade: pública.
- Objetivo: Valida a lista de destinos de um tipo de arquivo.
- Parâmetros:
    - `tipo`: TAD Tipo de Arquivo, com nome, ativo, restrições e destinos.
- Possíveis retornos:
    - `OK`: sucesso da operação.
    - `ERRO_OPERACAO_INVALIDA`: operação diferente de copiar/mover/recortar ou conflito de remoção.
    - `ERRO_DESTINO_INVALIDO`: destino ausente, vazio ou estruturalmente inválido.
- TADs envolvidos: Perfil, Origem configurada, Tipo de arquivo, Destino do tipo.

#### `validar_lista_destinos(destinos)`
- Visibilidade: pública.
- Objetivo: Valida diretamente uma lista de TADs Destino sem exigir que o chamador monte um TAD Tipo artificial.
- Parâmetros:
    - `destinos`: lista de TADs Destino do tipo, cada um com caminho e operação.
- Possíveis retornos:
    - `OK`: destinos válidos.
    - `ERRO_DADOS_INVALIDOS`: entrada não é uma lista.
    - `ERRO_OPERACAO_INVALIDA`: operação diferente de copiar/mover/recortar ou conflito de remoção.
    - `ERRO_DESTINO_INVALIDO`: destino ausente, vazio ou estruturalmente inválido.
- TADs envolvidos: Destino do tipo.

### Módulo `perfil_manager.py`

Resumo: Funções para criar, consultar e alterar perfis de backup.

TADs/obrigações do módulo: Perfil, Origem configurada, Tipo de arquivo, Destino do tipo, Restrições.

#### `criar_restricoes_padrao()`
- Visibilidade: pública.
- Objetivo: Cria restrições vazias no formato aceito pelo motor de backup.
- Parâmetros:
    - nenhum parâmetro.
- Possíveis retornos:
    - `{'extensoes_permitidas': [], 'regras_nome': [], 'tamanho_min': 0, 'tamanho_max': None, 'data_modificacao_min': None, 'data_modificacao_max': None}`: novo dicionário/TAD montado pela função.
- TADs envolvidos: Perfil, Origem configurada, Tipo de arquivo, Destino do tipo, Restrições.

#### `criar_restricoes(extensoes, regras_nome, tamanho_min, tamanho_max, data_min, data_max)`
- Visibilidade: pública.
- Objetivo: Cria restrições completas para um tipo de arquivo.
- Parâmetros:
    - `extensoes`: lista de extensões permitidas ou disponíveis.
    - `regras_nome`: lista de regras de nome em modo contem/exato.
    - `tamanho_min`: tamanho mínimo em bytes; 0 quando sem limite mínimo.
    - `tamanho_max`: tamanho máximo em bytes; None quando sem limite máximo.
    - `data_min`: data/timestamp mínimo de modificação; None quando sem limite.
    - `data_max`: data/timestamp máximo de modificação; None quando sem limite.
- Possíveis retornos:
    - `{'extensoes_permitidas': extensoes if isinstance(extensoes, list) else [], 'regras_nome': regras_nome if isinstance(regras_nome, list) else [], 'tamanho_min': tamanho_min, 'tamanho_max': tamanho_max, 'data_modificacao_min': data_min, 'data_modificacao_max': data_max}`: novo dicionário/TAD montado pela função.
- TADs envolvidos: Perfil, Origem configurada, Tipo de arquivo, Destino do tipo, Restrições.

#### `criar_regra_nome(valor, modo='contem')`
- Visibilidade: pública.
- Objetivo: Cria a subestrutura Regra de nome usada dentro do TAD Restrições.
- Parâmetros:
    - `valor`: texto comparado com o nome do arquivo.
    - `modo`: modo de comparação; `contem` para trecho no nome ou `exato` para nome completo.
- Possíveis retornos:
    - TAD Regra de nome normalizado.
- TADs envolvidos: Restrições, Regra de nome.

#### `criar_destino_tipo(caminho, operacao='copiar')`
- Visibilidade: pública.
- Objetivo: Cria um destino de backup vinculado a um tipo de arquivo.
- Parâmetros:
    - `caminho`: caminho de arquivo ou pasta no sistema operacional.
    - `operacao`: modo de transferência: copiar, mover ou recortar.
- Possíveis retornos:
    - `{'caminho': caminho, 'operacao': operacao}`: novo dicionário/TAD montado pela função.
- TADs envolvidos: Perfil, Origem configurada, Tipo de arquivo, Destino do tipo, Restrições.

#### `criar_tipo_arquivo(nome, restricoes=None, destinos=None)`
- Visibilidade: pública.
- Objetivo: Cria uma configuração de tipo/filtro dentro de uma origem.
- Parâmetros:
    - `nome`: nome informado pelo usuário ou nome interno do TAD.
    - `restricoes`: TAD Restrições usado para filtrar arquivos.
    - `destinos`: lista de TADs Destino ou caminhos de destino, conforme contexto.
- Possíveis retornos:
    - `{'id': 'tipo_' + uuid.uuid4().hex[:8], 'nome': nome, 'ativo': True, 'restricoes': restricoes, 'destinos': destinos}`: novo dicionário/TAD montado pela função.
- TADs envolvidos: Perfil, Origem configurada, Tipo de arquivo, Destino do tipo, Restrições.

#### `criar_origem_configurada(caminho)`
- Visibilidade: pública.
- Objetivo: Cria uma origem no modelo atual origem -> tipo -> destino.
- Parâmetros:
    - `caminho`: caminho de arquivo ou pasta no sistema operacional.
- Possíveis retornos:
    - `{'id': 'origem_' + uuid.uuid4().hex[:8], 'caminho': caminho, 'ativo': True, 'tipos_arquivo': []}`: novo dicionário/TAD montado pela função.
- TADs envolvidos: Perfil, Origem configurada, Tipo de arquivo, Destino do tipo, Restrições.

#### `_gerar_id_perfil(perfis)`
- Visibilidade: interna.
- Objetivo: Gera um identificador único para um novo perfil.
- Parâmetros:
    - `perfis`: coleção em memória de TADs Perfil.
- Possíveis retornos:
    - `'perfil_' + uuid.uuid4().hex[:8]`: retorno delegado para outra função.
- TADs envolvidos: Perfil, Origem configurada, Tipo de arquivo, Destino do tipo, Restrições.

#### `validar_nome_perfil(nome)`
- Visibilidade: pública.
- Objetivo: Valida o nome usado para criar ou renomear um perfil.
- Parâmetros:
    - `nome`: nome informado pelo usuário ou nome interno do TAD.
- Possíveis retornos:
    - `OK`: sucesso da operação.
    - `ERRO_NOME_INVALIDO`: nome vazio ou inválido.
- TADs envolvidos: Perfil, Origem configurada, Tipo de arquivo, Destino do tipo, Restrições.

#### `criar_perfil(nome)`
- Visibilidade: pública.
- Objetivo: Cria um perfil novo em memória no modelo atual.
- Parâmetros:
    - `nome`: nome informado pelo usuário ou nome interno do TAD.
- Possíveis retornos:
    - `(OK, perfil)`: tupla de retorno; normalmente combina código e dado/resultado.
    - `(codigo, None)`: tupla de retorno; normalmente combina código e dado/resultado.
- TADs envolvidos: Perfil, Origem configurada, Tipo de arquivo, Destino do tipo, Restrições.

#### `criar_edicao_perfil(perfil_id, nome=None, origens_configuradas=None, ativo=None)`
- Visibilidade: pública.
- Objetivo: Cria uma estrutura de edição parcial de Perfil sem expor chaves internas para UI ou controller.
- Parâmetros:
    - `perfil_id`: identificador único do perfil a editar.
    - `nome`: novo nome do perfil, opcional.
    - `origens_configuradas`: lista completa de TADs Origem, opcional.
    - `ativo`: estado ativo/inativo do perfil, opcional.
- Possíveis retornos:
    - TAD Perfil parcial usado como pedido de edição.
- TADs envolvidos: Perfil.

#### `consultar_perfil(perfis, perfil_id)`
- Visibilidade: pública.
- Objetivo: Consulta um perfil pelo identificador dentro de uma lista.
- Parâmetros:
    - `perfis`: coleção em memória de TADs Perfil.
    - `perfil_id`: identificador único de um perfil.
- Possíveis retornos:
    - `(ERRO_PERFIL_NAO_ENCONTRADO, None)`: tupla de retorno; normalmente combina código e dado/resultado.
    - `(OK, perfil)`: tupla de retorno; normalmente combina código e dado/resultado.
- TADs envolvidos: Perfil, Origem configurada, Tipo de arquivo, Destino do tipo, Restrições.

#### `listar_perfis(perfis)`
- Visibilidade: pública.
- Objetivo: Retorna a coleção de perfis atualmente mantida em memória.
- Parâmetros:
    - `perfis`: coleção em memória de TADs Perfil.
- Possíveis retornos:
    - `(OK, perfis)`: tupla de retorno; normalmente combina código e dado/resultado.
- TADs envolvidos: Perfil, Origem configurada, Tipo de arquivo, Destino do tipo, Restrições.

#### `obter_id_perfil(perfil)`
- Visibilidade: pública.
- Objetivo: Retorna o identificador de um perfil.
- Parâmetros:
    - `perfil`: TAD Perfil, dicionário persistido com id, nome, ativo e origens configuradas.
- Possíveis retornos:
    - `perfil.get('id')`: retorno delegado para outra função.
    - `None`: ausência válida de dado ou falha sem objeto retornável.
- TADs envolvidos: Perfil, Origem configurada, Tipo de arquivo, Destino do tipo, Restrições.

#### `obter_nome_perfil(perfil)`
- Visibilidade: pública.
- Objetivo: Retorna o nome de exibição do perfil.
- Parâmetros:
    - `perfil`: TAD Perfil, dicionário persistido com id, nome, ativo e origens configuradas.
- Possíveis retornos:
    - `nome`: valor calculado pela função.
    - `''`: valor calculado pela função.
- TADs envolvidos: Perfil, Origem configurada, Tipo de arquivo, Destino do tipo, Restrições.

#### `perfil_esta_ativo(perfil)`
- Visibilidade: pública.
- Objetivo: Indica se um perfil deve participar de execuções.
- Parâmetros:
    - `perfil`: TAD Perfil, dicionário persistido com id, nome, ativo e origens configuradas.
- Possíveis retornos:
    - `perfil.get('ativo', True)`: retorno delegado para outra função.
    - `False`: condição rejeitada/falsa.
- TADs envolvidos: Perfil, Origem configurada, Tipo de arquivo, Destino do tipo, Restrições.

#### `obter_origens_configuradas(perfil)`
- Visibilidade: pública.
- Objetivo: Retorna as origens configuradas de um perfil.
- Parâmetros:
    - `perfil`: TAD Perfil, dicionário persistido com id, nome, ativo e origens configuradas.
- Possíveis retornos:
    - `origens`: valor calculado pela função.
    - `[]`: lista vazia; nenhuma entrada aplicavel.
- TADs envolvidos: Perfil, Origem configurada, Tipo de arquivo, Destino do tipo, Restrições.

#### `perfil_possui_origens_configuradas(perfil)`
- Visibilidade: pública.
- Objetivo: Indica se um perfil possui ao menos uma origem configurada.
- Parâmetros:
    - `perfil`: TAD Perfil, dicionário persistido com id, nome, ativo e origens configuradas.
- Possíveis retornos:
    - `bool(obter_origens_configuradas(perfil))`: booleano calculado pela condição.
- TADs envolvidos: Perfil, Origem configurada, Tipo de arquivo, Destino do tipo, Restrições.

#### `aplicar_edicao_perfil(perfis, perfil_editado)`
- Visibilidade: pública.
- Objetivo: Aplica alterações em um perfil existente sem expor as chaves internas do TAD Perfil ao controller ou à interface.
- Parâmetros:
    - `perfis`: coleção em memória de TADs Perfil administrada pelo controller.
    - `perfil_editado`: TAD Perfil parcial ou completo contendo ao menos o identificador do perfil e, opcionalmente, nome, origens configuradas e estado ativo.
- Possíveis retornos:
    - `OK`: edição aplicada em memória.
    - `ERRO_DADOS_INVALIDOS`: entrada sem id, formato inválido, lista de origens inválida ou estado ativo/inativo inválido.
    - `ERRO_PERFIL_NAO_ENCONTRADO`: identificador não pertence à coleção recebida.
    - `ERRO_NOME_INVALIDO`: nome informado não pode ser usado.
- TADs envolvidos: Perfil, Origem configurada, Tipo de arquivo, Destino do tipo, Restrições.

#### `alterar_nome_perfil(perfis, perfil_id, novo_nome)`
- Visibilidade: pública.
- Objetivo: Altera o nome de um perfil existente após validação.
- Parâmetros:
    - `perfis`: coleção em memória de TADs Perfil.
    - `perfil_id`: identificador único de um perfil.
    - `novo_nome`: novo nome a gravar no perfil ou tipo.
- Possíveis retornos:
    - `OK`: sucesso da operação.
    - `codigo`: código de retorno propagado de chamada interna.
- TADs envolvidos: Perfil, Origem configurada, Tipo de arquivo, Destino do tipo, Restrições.

#### `alterar_origens_configuradas(perfis, perfil_id, origens_configuradas)`
- Visibilidade: pública.
- Objetivo: Substitui as origens configuradas de um perfil.
- Parâmetros:
    - `perfis`: coleção em memória de TADs Perfil.
    - `perfil_id`: identificador único de um perfil.
    - `origens_configuradas`: lista completa de TADs Origem do perfil.
- Possíveis retornos:
    - `OK`: sucesso da operação.
    - `ERRO_DADOS_INVALIDOS`: entrada com tipo, formato ou valor inválido.
    - `codigo`: código de retorno propagado de chamada interna.
- TADs envolvidos: Perfil, Origem configurada, Tipo de arquivo, Destino do tipo, Restrições.

#### `excluir_perfil(perfis, perfil_id)`
- Visibilidade: pública.
- Objetivo: Remove da lista o perfil identificado por `perfil_id`.
- Parâmetros:
    - `perfis`: coleção em memória de TADs Perfil.
    - `perfil_id`: identificador único de um perfil.
- Possíveis retornos:
    - `OK`: sucesso da operação.
    - `codigo`: código de retorno propagado de chamada interna.
- TADs envolvidos: Perfil, Origem configurada, Tipo de arquivo, Destino do tipo, Restrições.

#### `ativar_perfil(perfis, perfil_id)`
- Visibilidade: pública.
- Objetivo: Marca um perfil existente como ativo para execuções futuras.
- Parâmetros:
    - `perfis`: coleção em memória de TADs Perfil.
    - `perfil_id`: identificador único de um perfil.
- Possíveis retornos:
    - `OK`: sucesso da operação.
    - `codigo`: código de retorno propagado de chamada interna.
- TADs envolvidos: Perfil, Origem configurada, Tipo de arquivo, Destino do tipo, Restrições.

#### `desativar_perfil(perfis, perfil_id)`
- Visibilidade: pública.
- Objetivo: Marca um perfil existente como inativo.
- Parâmetros:
    - `perfis`: coleção em memória de TADs Perfil.
    - `perfil_id`: identificador único de um perfil.
- Possíveis retornos:
    - `OK`: sucesso da operação.
    - `codigo`: código de retorno propagado de chamada interna.
- TADs envolvidos: Perfil, Origem configurada, Tipo de arquivo, Destino do tipo, Restrições.

#### `origem_e_valida(origem)`
- Visibilidade: pública.
- Objetivo: Indica se a entrada possui formato mínimo de origem configurada.
- Parâmetros:
    - `origem`: TAD Origem Configurada, com caminho, ativo e tipos de arquivo.
- Possíveis retornos:
    - `isinstance(origem, dict)`: booleano calculado pela condição.
- TADs envolvidos: Perfil, Origem configurada, Tipo de arquivo, Destino do tipo, Restrições.

#### `obter_id_origem(origem)`
- Visibilidade: pública.
- Objetivo: Retorna o identificador interno da origem configurada.
- Parâmetros:
    - `origem`: TAD Origem Configurada, com caminho, ativo e tipos de arquivo.
- Possíveis retornos:
    - `origem.get('id')`: retorno delegado para outra função.
    - `None`: ausência válida de dado ou falha sem objeto retornável.
- TADs envolvidos: Perfil, Origem configurada, Tipo de arquivo, Destino do tipo, Restrições.

#### `obter_caminho_origem(origem)`
- Visibilidade: pública.
- Objetivo: Retorna o caminho da pasta de origem.
- Parâmetros:
    - `origem`: TAD Origem Configurada, com caminho, ativo e tipos de arquivo.
- Possíveis retornos:
    - `caminho`: valor calculado pela função.
    - `''`: valor calculado pela função.
- TADs envolvidos: Perfil, Origem configurada, Tipo de arquivo, Destino do tipo, Restrições.

#### `origem_esta_ativa(origem)`
- Visibilidade: pública.
- Objetivo: Indica se uma origem deve participar do backup.
- Parâmetros:
    - `origem`: TAD Origem Configurada, com caminho, ativo e tipos de arquivo.
- Possíveis retornos:
    - `origem.get('ativo', True)`: retorno delegado para outra função.
    - `False`: condição rejeitada/falsa.
- TADs envolvidos: Perfil, Origem configurada, Tipo de arquivo, Destino do tipo, Restrições.

#### `obter_tipos_origem(origem)`
- Visibilidade: pública.
- Objetivo: Retorna a lista de tipos de arquivo vinculados a uma origem.
- Parâmetros:
    - `origem`: TAD Origem Configurada, com caminho, ativo e tipos de arquivo.
- Possíveis retornos:
    - `tipos`: valor calculado pela função.
    - `[]`: lista vazia; nenhuma entrada aplicavel.
- TADs envolvidos: Perfil, Origem configurada, Tipo de arquivo, Destino do tipo, Restrições.

#### `origem_possui_tipos(origem)`
- Visibilidade: pública.
- Objetivo: Indica se a origem possui tipos cadastrados.
- Parâmetros:
    - `origem`: TAD Origem Configurada, com caminho, ativo e tipos de arquivo.
- Possíveis retornos:
    - `bool(obter_tipos_origem(origem))`: booleano calculado pela condição.
- TADs envolvidos: Perfil, Origem configurada, Tipo de arquivo, Destino do tipo, Restrições.

#### `alterar_origem_ativa(origem, ativo)`
- Visibilidade: pública.
- Objetivo: Altera o estado ativo/inativo de uma origem configurada.
- Parâmetros:
    - `origem`: TAD Origem Configurada, com caminho, ativo e tipos de arquivo.
    - `ativo`: parâmetro usado pela função conforme o contexto do módulo.
- Possíveis retornos:
    - `OK`: sucesso da operação.
    - `ERRO_DADOS_INVALIDOS`: entrada com tipo, formato ou valor inválido.
- TADs envolvidos: Perfil, Origem configurada, Tipo de arquivo, Destino do tipo, Restrições.

#### `adicionar_tipo_origem(origem, tipo)`
- Visibilidade: pública.
- Objetivo: Adiciona um tipo de arquivo a uma origem configurada.
- Parâmetros:
    - `origem`: TAD Origem Configurada, com caminho, ativo e tipos de arquivo.
    - `tipo`: TAD Tipo de Arquivo, com nome, ativo, restrições e destinos.
- Possíveis retornos:
    - `OK`: sucesso da operação.
    - `ERRO_DADOS_INVALIDOS`: entrada com tipo, formato ou valor inválido.
- TADs envolvidos: Perfil, Origem configurada, Tipo de arquivo, Destino do tipo, Restrições.

#### `remover_tipo_origem_por_indice(origem, indice)`
- Visibilidade: pública.
- Objetivo: Remove um tipo de arquivo da origem pelo índice.
- Parâmetros:
    - `origem`: TAD Origem Configurada, com caminho, ativo e tipos de arquivo.
    - `indice`: posição selecionada em lista/listbox.
- Possíveis retornos:
    - `OK`: sucesso da operação.
    - `ERRO_DADOS_INVALIDOS`: entrada com tipo, formato ou valor inválido.
- TADs envolvidos: Perfil, Origem configurada, Tipo de arquivo, Destino do tipo, Restrições.

#### `tipo_e_valido(tipo)`
- Visibilidade: pública.
- Objetivo: Indica se a entrada possui formato mínimo de tipo de arquivo.
- Parâmetros:
    - `tipo`: TAD Tipo de Arquivo, com nome, ativo, restrições e destinos.
- Possíveis retornos:
    - `isinstance(tipo, dict)`: booleano calculado pela condição.
- TADs envolvidos: Perfil, Origem configurada, Tipo de arquivo, Destino do tipo, Restrições.

#### `obter_id_tipo(tipo)`
- Visibilidade: pública.
- Objetivo: Retorna o identificador do tipo de arquivo.
- Parâmetros:
    - `tipo`: TAD Tipo de Arquivo, com nome, ativo, restrições e destinos.
- Possíveis retornos:
    - `tipo.get('id')`: retorno delegado para outra função.
    - `None`: ausência válida de dado ou falha sem objeto retornável.
- TADs envolvidos: Perfil, Origem configurada, Tipo de arquivo, Destino do tipo, Restrições.

#### `obter_nome_tipo(tipo)`
- Visibilidade: pública.
- Objetivo: Retorna o nome exibido para o tipo de arquivo.
- Parâmetros:
    - `tipo`: TAD Tipo de Arquivo, com nome, ativo, restrições e destinos.
- Possíveis retornos:
    - `nome`: valor calculado pela função.
    - `''`: valor calculado pela função.
- TADs envolvidos: Perfil, Origem configurada, Tipo de arquivo, Destino do tipo, Restrições.

#### `tipo_esta_ativo(tipo)`
- Visibilidade: pública.
- Objetivo: Indica se um tipo de arquivo deve participar do backup.
- Parâmetros:
    - `tipo`: TAD Tipo de Arquivo, com nome, ativo, restrições e destinos.
- Possíveis retornos:
    - `tipo.get('ativo', True)`: retorno delegado para outra função.
    - `False`: condição rejeitada/falsa.
- TADs envolvidos: Perfil, Origem configurada, Tipo de arquivo, Destino do tipo, Restrições.

#### `obter_restricoes_tipo(tipo)`
- Visibilidade: pública.
- Objetivo: Retorna as restrições configuradas para um tipo.
- Parâmetros:
    - `tipo`: TAD Tipo de Arquivo, com nome, ativo, restrições e destinos.
- Possíveis retornos:
    - `criar_restricoes_padrao()`: retorno delegado para outra função.
    - `restricoes`: valor calculado pela função.
- TADs envolvidos: Perfil, Origem configurada, Tipo de arquivo, Destino do tipo, Restrições.

#### `obter_destinos_tipo(tipo)`
- Visibilidade: pública.
- Objetivo: Retorna a lista de destinos vinculados a um tipo.
- Parâmetros:
    - `tipo`: TAD Tipo de Arquivo, com nome, ativo, restrições e destinos.
- Possíveis retornos:
    - `destinos`: valor calculado pela função.
    - `[]`: lista vazia; nenhuma entrada aplicavel.
- TADs envolvidos: Perfil, Origem configurada, Tipo de arquivo, Destino do tipo, Restrições.

#### `tipo_possui_destinos(tipo)`
- Visibilidade: pública.
- Objetivo: Indica se um tipo possui ao menos um destino configurado.
- Parâmetros:
    - `tipo`: TAD Tipo de Arquivo, com nome, ativo, restrições e destinos.
- Possíveis retornos:
    - `bool(obter_destinos_tipo(tipo))`: booleano calculado pela condição.
- TADs envolvidos: Perfil, Origem configurada, Tipo de arquivo, Destino do tipo, Restrições.

#### `alterar_nome_tipo(tipo, nome)`
- Visibilidade: pública.
- Objetivo: Altera o nome de um tipo de arquivo.
- Parâmetros:
    - `tipo`: TAD Tipo de Arquivo, com nome, ativo, restrições e destinos.
    - `nome`: nome informado pelo usuário ou nome interno do TAD.
- Possíveis retornos:
    - `OK`: sucesso da operação.
    - `ERRO_DADOS_INVALIDOS`: entrada com tipo, formato ou valor inválido.
- TADs envolvidos: Perfil, Origem configurada, Tipo de arquivo, Destino do tipo, Restrições.

#### `adicionar_destino_tipo_configurado(tipo, destino)`
- Visibilidade: pública.
- Objetivo: Adiciona um destino a um tipo de arquivo.
- Parâmetros:
    - `tipo`: TAD Tipo de Arquivo, com nome, ativo, restrições e destinos.
    - `destino`: TAD Destino ou caminho final, conforme contexto.
- Possíveis retornos:
    - `OK`: sucesso da operação.
    - `ERRO_DADOS_INVALIDOS`: entrada com tipo, formato ou valor inválido.
- TADs envolvidos: Perfil, Origem configurada, Tipo de arquivo, Destino do tipo, Restrições.

#### `remover_destino_tipo_por_indice(tipo, indice)`
- Visibilidade: pública.
- Objetivo: Remove um destino do tipo pelo índice.
- Parâmetros:
    - `tipo`: TAD Tipo de Arquivo, com nome, ativo, restrições e destinos.
    - `indice`: posição selecionada em lista/listbox.
- Possíveis retornos:
    - `OK`: sucesso da operação.
    - `ERRO_DADOS_INVALIDOS`: entrada com tipo, formato ou valor inválido.
- TADs envolvidos: Perfil, Origem configurada, Tipo de arquivo, Destino do tipo, Restrições.

#### `alterar_restricoes_tipo(tipo, restricoes)`
- Visibilidade: pública.
- Objetivo: Substitui as restrições de um tipo de arquivo.
- Parâmetros:
    - `tipo`: TAD Tipo de Arquivo, com nome, ativo, restrições e destinos.
    - `restricoes`: TAD Restrições usado para filtrar arquivos.
- Possíveis retornos:
    - `OK`: sucesso da operação.
    - `ERRO_DADOS_INVALIDOS`: entrada com tipo, formato ou valor inválido.
- TADs envolvidos: Perfil, Origem configurada, Tipo de arquivo, Destino do tipo, Restrições.

#### `alterar_tipo_ativo(tipo, ativo)`
- Visibilidade: pública.
- Objetivo: Altera o estado ativo/inativo de um tipo de arquivo.
- Parâmetros:
    - `tipo`: TAD Tipo de Arquivo, com nome, ativo, restrições e destinos.
    - `ativo`: parâmetro usado pela função conforme o contexto do módulo.
- Possíveis retornos:
    - `OK`: sucesso da operação.
    - `ERRO_DADOS_INVALIDOS`: entrada com tipo, formato ou valor inválido.
- TADs envolvidos: Perfil, Origem configurada, Tipo de arquivo, Destino do tipo, Restrições.

#### `destino_e_valido(destino)`
- Visibilidade: pública.
- Objetivo: Indica se a entrada possui formato mínimo de destino.
- Parâmetros:
    - `destino`: TAD Destino ou caminho final, conforme contexto.
- Possíveis retornos:
    - `isinstance(destino, dict)`: booleano calculado pela condição.
- TADs envolvidos: Perfil, Origem configurada, Tipo de arquivo, Destino do tipo, Restrições.

#### `obter_caminho_destino(destino)`
- Visibilidade: pública.
- Objetivo: Retorna o caminho de pasta de um destino.
- Parâmetros:
    - `destino`: TAD Destino ou caminho final, conforme contexto.
- Possíveis retornos:
    - `caminho`: valor calculado pela função.
    - `''`: valor calculado pela função.
- TADs envolvidos: Perfil, Origem configurada, Tipo de arquivo, Destino do tipo, Restrições.

#### `obter_operacao_destino(destino)`
- Visibilidade: pública.
- Objetivo: Retorna a operação configurada para um destino.
- Parâmetros:
    - `destino`: TAD Destino ou caminho final, conforme contexto.
- Possíveis retornos:
    - `operacao`: valor calculado pela função.
    - `'copiar'`: valor calculado pela função.
- TADs envolvidos: Perfil, Origem configurada, Tipo de arquivo, Destino do tipo, Restrições.

#### `alterar_operacao_destino(destino, operacao)`
- Visibilidade: pública.
- Objetivo: Altera a operação configurada em um destino.
- Parâmetros:
    - `destino`: TAD Destino ou caminho final, conforme contexto.
    - `operacao`: modo de transferência: copiar, mover ou recortar.
- Possíveis retornos:
    - `OK`: sucesso da operação.
    - `ERRO_DADOS_INVALIDOS`: entrada com tipo, formato ou valor inválido.
- TADs envolvidos: Perfil, Origem configurada, Tipo de arquivo, Destino do tipo, Restrições.

#### `restricoes_e_valida(restricoes)`
- Visibilidade: pública.
- Objetivo: Indica se a entrada possui formato mínimo de restrições.
- Parâmetros:
    - `restricoes`: TAD Restrições usado para filtrar arquivos.
- Possíveis retornos:
    - `isinstance(restricoes, dict)`: booleano calculado pela condição.
- TADs envolvidos: Perfil, Origem configurada, Tipo de arquivo, Destino do tipo, Restrições.

#### `obter_extensoes_restricoes(restricoes)`
- Visibilidade: pública.
- Objetivo: Retorna as extensões permitidas configuradas nas restrições.
- Parâmetros:
    - `restricoes`: TAD Restrições usado para filtrar arquivos.
- Possíveis retornos:
    - `extensoes`: valor calculado pela função.
    - `[]`: lista vazia; nenhuma entrada aplicavel.
- TADs envolvidos: Perfil, Origem configurada, Tipo de arquivo, Destino do tipo, Restrições.

#### `obter_regras_nome_restricoes(restricoes)`
- Visibilidade: pública.
- Objetivo: Retorna as regras de nome configuradas nas restrições.
- Parâmetros:
    - `restricoes`: TAD Restrições usado para filtrar arquivos.
- Possíveis retornos:
    - `regras`: valor calculado pela função.
    - `[]`: lista vazia; nenhuma entrada aplicavel.
- TADs envolvidos: Perfil, Origem configurada, Tipo de arquivo, Destino do tipo, Restrições.

#### `obter_tamanho_min_restricoes(restricoes)`
- Visibilidade: pública.
- Objetivo: Retorna o tamanho mínimo configurado nas restrições.
- Parâmetros:
    - `restricoes`: TAD Restrições usado para filtrar arquivos.
- Possíveis retornos:
    - `restricoes.get('tamanho_min', 0) or 0`: retorno delegado para outra função.
    - `0`: valor calculado pela função.
- TADs envolvidos: Perfil, Origem configurada, Tipo de arquivo, Destino do tipo, Restrições.

#### `obter_tamanho_max_restricoes(restricoes)`
- Visibilidade: pública.
- Objetivo: Retorna o tamanho máximo configurado nas restrições.
- Parâmetros:
    - `restricoes`: TAD Restrições usado para filtrar arquivos.
- Possíveis retornos:
    - `restricoes.get('tamanho_max')`: retorno delegado para outra função.
    - `None`: ausência válida de dado ou falha sem objeto retornável.
- TADs envolvidos: Perfil, Origem configurada, Tipo de arquivo, Destino do tipo, Restrições.

#### `obter_data_min_restricoes(restricoes)`
- Visibilidade: pública.
- Objetivo: Retorna a data mínima configurada nas restrições.
- Parâmetros:
    - `restricoes`: TAD Restrições usado para filtrar arquivos.
- Possíveis retornos:
    - `restricoes.get('data_modificacao_min')`: retorno delegado para outra função.
    - `None`: ausência válida de dado ou falha sem objeto retornável.
- TADs envolvidos: Perfil, Origem configurada, Tipo de arquivo, Destino do tipo, Restrições.

#### `obter_data_max_restricoes(restricoes)`
- Visibilidade: pública.
- Objetivo: Retorna a data máxima configurada nas restrições.
- Parâmetros:
    - `restricoes`: TAD Restrições usado para filtrar arquivos.
- Possíveis retornos:
    - `restricoes.get('data_modificacao_max')`: retorno delegado para outra função.
    - `None`: ausência válida de dado ou falha sem objeto retornável.
- TADs envolvidos: Perfil, Origem configurada, Tipo de arquivo, Destino do tipo, Restrições.

#### `obter_valor_regra_nome(regra)`
- Visibilidade: pública.
- Objetivo: Retorna o texto de comparação de uma Regra de nome sem expor sua chave interna.
- Parâmetros:
    - `regra`: TAD Regra de nome armazenado dentro de Restrições.
- Possíveis retornos:
    - string com o valor da regra.
    - `''`: entrada inválida ou valor não textual.
- TADs envolvidos: Restrições, Regra de nome.

#### `obter_modo_regra_nome(regra)`
- Visibilidade: pública.
- Objetivo: Retorna o modo normalizado de uma Regra de nome.
- Parâmetros:
    - `regra`: TAD Regra de nome armazenado dentro de Restrições.
- Possíveis retornos:
    - `contem`: modo padrão ou regra de trecho no nome.
    - `exato`: regra de nome completo.
- TADs envolvidos: Restrições, Regra de nome.

## Pasta `backupmanager/engine`

### Módulo `backup_engine.py`

Resumo: Execução das rotinas de backup.

TADs/obrigações do módulo: Perfil, Origem configurada, Tipo de arquivo, Destino do tipo, Metadados de arquivo, Resultado de backup.

#### `executar_backup(perfil)`
- Visibilidade: pública.
- Objetivo: Executa a rotina de backup de um perfil.
- Parâmetros:
    - `perfil`: TAD Perfil, dicionário persistido com id, nome, ativo e origens configuradas.
- Possíveis retornos:
    - `_executar_backup_configurado(perfil)`: retorno delegado para outra função.
    - `(codigo_validacao, resultado)`: tupla de retorno; normalmente combina código e dado/resultado.
- TADs envolvidos: Perfil, Origem configurada, Tipo de arquivo, Destino do tipo, Metadados de arquivo, Resultado de backup.

#### `_executar_backup_configurado(perfil)`
- Visibilidade: interna.
- Objetivo: Executa backup no modelo origem -> tipo -> destino.
- Parâmetros:
    - `perfil`: TAD Perfil, dicionário persistido com id, nome, ativo e origens configuradas.
- Possíveis retornos:
    - `(primeiro_erro, resultado)`: tupla de retorno; normalmente combina código e dado/resultado.
    - `(ERRO_BACKUP_SEM_ARQUIVOS, resultado)`: tupla de retorno; normalmente combina código e dado/resultado.
    - `(OK, resultado)`: tupla de retorno; normalmente combina código e dado/resultado.
- TADs envolvidos: Perfil, Origem configurada, Tipo de arquivo, Destino do tipo, Metadados de arquivo, Resultado de backup.

#### `_executar_backup_da_origem_configurada(origem, resultado)`
- Visibilidade: interna.
- Objetivo: Executa todos os tipos de uma origem configurada.
- Parâmetros:
    - `origem`: TAD Origem Configurada, com caminho, ativo e tipos de arquivo.
    - `resultado`: TAD Resultado geral de backup.
- Possíveis retornos:
    - `primeiro_erro`: valor calculado pela função.
- TADs envolvidos: Perfil, Origem configurada, Tipo de arquivo, Destino do tipo, Metadados de arquivo, Resultado de backup.

#### `_filtrar_arquivos_por_tipo(caminhos, tipo)`
- Visibilidade: interna.
- Objetivo: Filtra arquivos de uma origem para um tipo.
- Parâmetros:
    - `caminhos`: lista de caminhos de arquivos candidatos.
    - `tipo`: TAD Tipo de Arquivo, com nome, ativo, restrições e destinos.
- Possíveis retornos:
    - `arquivos`: valor calculado pela função.
- TADs envolvidos: Perfil, Origem configurada, Tipo de arquivo, Destino do tipo, Metadados de arquivo, Resultado de backup.

#### `_processar_arquivo_para_destinos(arquivo, destinos, operacao)`
- Visibilidade: interna.
- Objetivo: Processa um arquivo para uma lista de destinos.
- Parâmetros:
    - `arquivo`: TAD Metadados de Arquivo.
    - `destinos`: lista de TADs Destino ou caminhos de destino, conforme contexto.
    - `operacao`: modo de transferência: copiar, mover ou recortar.
- Possíveis retornos:
    - `resultado`: valor calculado pela função.
    - `_processar_copia_para_destinos(arquivo, destinos, resultado)`: retorno delegado para outra função.
    - `_processar_movimento_para_destinos(arquivo, destinos, resultado)`: retorno delegado para outra função.
    - `_processar_recorte_para_destinos(arquivo, destinos, resultado)`: retorno delegado para outra função.
- TADs envolvidos: Perfil, Origem configurada, Tipo de arquivo, Destino do tipo, Metadados de arquivo, Resultado de backup.

#### `_processar_arquivo_para_destinos_configurados(arquivo, destinos, tipo)`
- Visibilidade: interna.
- Objetivo: Processa arquivo usando destinos com operação individual.
- Parâmetros:
    - `arquivo`: TAD Metadados de Arquivo.
    - `destinos`: lista de TADs Destino ou caminhos de destino, conforme contexto.
    - `tipo`: TAD Tipo de Arquivo, com nome, ativo, restrições e destinos.
- Possíveis retornos:
    - `resultado`: valor calculado pela função.
    - `resultado_erro`: valor calculado pela função.
- TADs envolvidos: Perfil, Origem configurada, Tipo de arquivo, Destino do tipo, Metadados de arquivo, Resultado de backup.

#### `_processar_copia_para_destinos(arquivo, destinos, resultado)`
- Visibilidade: interna.
- Objetivo: Copia um arquivo para todos os destinos.
- Parâmetros:
    - `arquivo`: TAD Metadados de Arquivo.
    - `destinos`: lista de TADs Destino ou caminhos de destino, conforme contexto.
    - `resultado`: TAD Resultado geral de backup.
- Possíveis retornos:
    - `resultado`: valor calculado pela função.
- TADs envolvidos: Perfil, Origem configurada, Tipo de arquivo, Destino do tipo, Metadados de arquivo, Resultado de backup.

#### `_processar_movimento_para_destinos(arquivo, destinos, resultado)`
- Visibilidade: interna.
- Objetivo: Copia um arquivo para todos os destinos e remove a origem ao final.
- Parâmetros:
    - `arquivo`: TAD Metadados de Arquivo.
    - `destinos`: lista de TADs Destino ou caminhos de destino, conforme contexto.
    - `resultado`: TAD Resultado geral de backup.
- Possíveis retornos:
    - `resultado`: valor calculado pela função.
- TADs envolvidos: Perfil, Origem configurada, Tipo de arquivo, Destino do tipo, Metadados de arquivo, Resultado de backup.

#### `_processar_recorte_para_destinos(arquivo, destinos, resultado)`
- Visibilidade: interna.
- Objetivo: Recorta um arquivo para um destino.
- Parâmetros:
    - `arquivo`: TAD Metadados de Arquivo.
    - `destinos`: lista de TADs Destino ou caminhos de destino, conforme contexto.
    - `resultado`: TAD Resultado geral de backup.
- Possíveis retornos:
    - `resultado`: valor calculado pela função.
- TADs envolvidos: Perfil, Origem configurada, Tipo de arquivo, Destino do tipo, Metadados de arquivo, Resultado de backup.

#### `copiar_arquivo(origem, destino)`
- Visibilidade: pública.
- Objetivo: Copia um arquivo individual para o caminho de destino.
- Parâmetros:
    - `origem`: TAD Origem Configurada, com caminho, ativo e tipos de arquivo.
    - `destino`: TAD Destino ou caminho final, conforme contexto.
- Possíveis retornos:
    - `OK`: sucesso da operação.
    - `ERRO_DADOS_INVALIDOS`: entrada com tipo, formato ou valor inválido.
    - `ERRO_ARQUIVO_NAO_ENCONTRADO`: arquivo de origem inexistente ou não é arquivo.
    - `codigo`: código de retorno propagado de chamada interna.
    - `ERRO_FALHA_AO_COPIAR`: falha de sistema ao copiar arquivo.
- TADs envolvidos: Perfil, Origem configurada, Tipo de arquivo, Destino do tipo, Metadados de arquivo, Resultado de backup.

#### `mover_arquivo(origem, destino)`
- Visibilidade: pública.
- Objetivo: Move um arquivo individual para o caminho de destino.
- Parâmetros:
    - `origem`: TAD Origem Configurada, com caminho, ativo e tipos de arquivo.
    - `destino`: TAD Destino ou caminho final, conforme contexto.
- Possíveis retornos:
    - `OK`: sucesso da operação.
    - `ERRO_DADOS_INVALIDOS`: entrada com tipo, formato ou valor inválido.
    - `ERRO_ARQUIVO_NAO_ENCONTRADO`: arquivo de origem inexistente ou não é arquivo.
    - `codigo`: código de retorno propagado de chamada interna.
    - `ERRO_FALHA_AO_MOVER`: falha de sistema ao mover/remover arquivo.
- TADs envolvidos: Perfil, Origem configurada, Tipo de arquivo, Destino do tipo, Metadados de arquivo, Resultado de backup.

#### `_gerar_caminho_destino(arquivo, pasta_destino)`
- Visibilidade: interna.
- Objetivo: Gera caminho de destino para um arquivo.
- Parâmetros:
    - `arquivo`: TAD Metadados de Arquivo.
    - `pasta_destino`: parâmetro usado pela função conforme o contexto do módulo.
- Possíveis retornos:
    - `str(Path(pasta_destino) / nome)`: retorno delegado para outra função.
    - `None`: ausência válida de dado ou falha sem objeto retornável.
- TADs envolvidos: Perfil, Origem configurada, Tipo de arquivo, Destino do tipo, Metadados de arquivo, Resultado de backup.

#### `_criar_pasta_destino_se_necessario(caminho_destino)`
- Visibilidade: interna.
- Objetivo: Cria a pasta de destino quando necessário.
- Parâmetros:
    - `caminho_destino`: parâmetro usado pela função conforme o contexto do módulo.
- Possíveis retornos:
    - `OK`: sucesso da operação.
    - `ERRO_DESTINO_INVALIDO`: destino ausente, vazio ou estruturalmente inválido.
- TADs envolvidos: Perfil, Origem configurada, Tipo de arquivo, Destino do tipo, Metadados de arquivo, Resultado de backup.

### Módulo `file_utils.py`

Resumo: Funções auxiliares para arquivos e diretórios.

TADs/obrigações do módulo: Metadados de arquivo, Restrições, Regra de nome.

#### `caminho_existe(caminho)`
- Visibilidade: pública.
- Objetivo: Verifica se um caminho existe no sistema de arquivos.
- Parâmetros:
    - `caminho`: caminho de arquivo ou pasta no sistema operacional.
- Possíveis retornos:
    - `False`: condição rejeitada/falsa.
    - `Path(caminho).exists()`: retorno delegado para outra função.
- TADs envolvidos: Metadados de arquivo, Restrições, Regra de nome.

#### `caminho_e_diretorio(caminho)`
- Visibilidade: pública.
- Objetivo: Verifica se um caminho existe e representa uma pasta.
- Parâmetros:
    - `caminho`: caminho de arquivo ou pasta no sistema operacional.
- Possíveis retornos:
    - `False`: condição rejeitada/falsa.
    - `Path(caminho).is_dir()`: retorno delegado para outra função.
- TADs envolvidos: Metadados de arquivo, Restrições, Regra de nome.

#### `listar_arquivos_em_origem(origem)`
- Visibilidade: pública.
- Objetivo: Lista apenas arquivos diretamente dentro de uma origem.
- Parâmetros:
    - `origem`: TAD Origem Configurada, com caminho, ativo e tipos de arquivo.
- Possíveis retornos:
    - `arquivos`: valor calculado pela função.
    - `[]`: lista vazia; nenhuma entrada aplicavel.
- TADs envolvidos: Metadados de arquivo, Restrições, Regra de nome.

#### `listar_arquivos_de_origens(origens)`
- Visibilidade: pública.
- Objetivo: Lista arquivos diretamente dentro de varias origens.
- Parâmetros:
    - `origens`: coleção de caminhos/origens ou TADs de origem, conforme contexto.
- Possíveis retornos:
    - `arquivos`: valor calculado pela função.
    - `[]`: lista vazia; nenhuma entrada aplicavel.
- TADs envolvidos: Metadados de arquivo, Restrições, Regra de nome.

#### `obter_extensao(caminho)`
- Visibilidade: pública.
- Objetivo: Retorna a extensão de um arquivo em minúsculas.
- Parâmetros:
    - `caminho`: caminho de arquivo ou pasta no sistema operacional.
- Possíveis retornos:
    - `''`: valor calculado pela função.
    - `Path(caminho).suffix.lower()`: retorno delegado para outra função.
- TADs envolvidos: Metadados de arquivo, Restrições, Regra de nome.

#### `obter_metadados_arquivo(caminho)`
- Visibilidade: pública.
- Objetivo: Monta o dicionário de metadados de um arquivo real.
- Parâmetros:
    - `caminho`: caminho de arquivo ou pasta no sistema operacional.
- Possíveis retornos:
    - `{'caminho': str(caminho_path), 'nome': caminho_path.name, 'extensao': obter_extensao(caminho_path), 'tamanho': estatisticas.st_size, 'data_modificacao': estatisticas.st_mtime}`: novo dicionário/TAD montado pela função.
    - `None`: ausência válida de dado ou falha sem objeto retornável.
- TADs envolvidos: Metadados de arquivo, Restrições, Regra de nome.

#### `arquivo_e_valido(arquivo)`
- Visibilidade: pública.
- Objetivo: Indica se a entrada possui formato mínimo de metadados de arquivo.
- Parâmetros:
    - `arquivo`: TAD Metadados de Arquivo.
- Possíveis retornos:
    - `isinstance(arquivo, dict)`: booleano calculado pela condição.
- TADs envolvidos: Metadados de arquivo, Restrições, Regra de nome.

#### `obter_caminho_arquivo(arquivo)`
- Visibilidade: pública.
- Objetivo: Retorna o caminho completo de um arquivo de metadados.
- Parâmetros:
    - `arquivo`: TAD Metadados de Arquivo.
- Possíveis retornos:
    - `caminho`: valor calculado pela função.
    - `''`: valor calculado pela função.
- TADs envolvidos: Metadados de arquivo, Restrições, Regra de nome.

#### `obter_nome_arquivo(arquivo)`
- Visibilidade: pública.
- Objetivo: Retorna o nome do arquivo de metadados.
- Parâmetros:
    - `arquivo`: TAD Metadados de Arquivo.
- Possíveis retornos:
    - `Path(obter_caminho_arquivo(arquivo)).name`: retorno delegado para outra função.
    - `''`: valor calculado pela função.
    - `nome`: valor calculado pela função.
- TADs envolvidos: Metadados de arquivo, Restrições, Regra de nome.

#### `obter_extensao_arquivo(arquivo)`
- Visibilidade: pública.
- Objetivo: Retorna a extensão registrada nos metadados do arquivo.
- Parâmetros:
    - `arquivo`: TAD Metadados de Arquivo.
- Possíveis retornos:
    - `extensao`: valor calculado pela função.
    - `''`: valor calculado pela função.
- TADs envolvidos: Metadados de arquivo, Restrições, Regra de nome.

#### `obter_tamanho_arquivo(arquivo)`
- Visibilidade: pública.
- Objetivo: Retorna o tamanho em bytes registrado nos metadados.
- Parâmetros:
    - `arquivo`: TAD Metadados de Arquivo.
- Possíveis retornos:
    - `tamanho`: valor calculado pela função.
    - `0`: valor calculado pela função.
- TADs envolvidos: Metadados de arquivo, Restrições, Regra de nome.

#### `obter_data_modificacao_arquivo(arquivo)`
- Visibilidade: pública.
- Objetivo: Retorna o timestamp de modificação registrado nos metadados.
- Parâmetros:
    - `arquivo`: TAD Metadados de Arquivo.
- Possíveis retornos:
    - `arquivo.get('data_modificacao')`: retorno delegado para outra função.
    - `None`: ausência válida de dado ou falha sem objeto retornável.
- TADs envolvidos: Metadados de arquivo, Restrições, Regra de nome.

#### `obter_nome_tipo_arquivo(arquivo)`
- Visibilidade: pública.
- Objetivo: Retorna o nome do tipo associado aos metadados do arquivo.
- Parâmetros:
    - `arquivo`: TAD Metadados de Arquivo.
- Possíveis retornos:
    - `nome`: valor calculado pela função.
    - `''`: valor calculado pela função.
- TADs envolvidos: Metadados de arquivo, Restrições, Regra de nome.

#### `associar_tipo_ao_arquivo(arquivo, tipo_id, tipo_nome)`
- Visibilidade: pública.
- Objetivo: Associa informações de tipo ao dicionário de metadados do arquivo.
- Parâmetros:
    - `arquivo`: TAD Metadados de Arquivo.
    - `tipo_id`: identificador único do tipo de arquivo.
    - `tipo_nome`: nome do tipo associado ao arquivo ou exibido na UI.
- Possíveis retornos:
    - `arquivo`: valor calculado pela função.
    - `None`: ausência válida de dado ou falha sem objeto retornável.
- TADs envolvidos: Metadados de arquivo, Restrições, Regra de nome.

#### `associar_origem_ao_arquivo(arquivo, origem)`
- Visibilidade: pública.
- Objetivo: Registra a origem usada na pré-visualização do arquivo.
- Parâmetros:
    - `arquivo`: TAD Metadados de Arquivo.
    - `origem`: TAD Origem Configurada, com caminho, ativo e tipos de arquivo.
- Possíveis retornos:
    - `arquivo`: valor calculado pela função.
    - `None`: ausência válida de dado ou falha sem objeto retornável.
- TADs envolvidos: Metadados de arquivo, Restrições, Regra de nome.

#### `iniciar_tipos_incluidos_arquivo(arquivo)`
- Visibilidade: pública.
- Objetivo: Inicializa a lista de tipos incluidos na pré-visualização.
- Parâmetros:
    - `arquivo`: TAD Metadados de Arquivo.
- Possíveis retornos:
    - `arquivo`: valor calculado pela função.
    - `None`: ausência válida de dado ou falha sem objeto retornável.
- TADs envolvidos: Metadados de arquivo, Restrições, Regra de nome.

#### `adicionar_tipo_incluido_arquivo(arquivo, tipo_nome)`
- Visibilidade: pública.
- Objetivo: Adiciona um tipo aprovado na pré-visualização do arquivo.
- Parâmetros:
    - `arquivo`: TAD Metadados de Arquivo.
    - `tipo_nome`: nome do tipo associado ao arquivo ou exibido na UI.
- Possíveis retornos:
    - `arquivo`: valor calculado pela função.
    - `None`: ausência válida de dado ou falha sem objeto retornável.
- TADs envolvidos: Metadados de arquivo, Restrições, Regra de nome.

#### `arquivo_possui_tipo_incluido(arquivo)`
- Visibilidade: pública.
- Objetivo: Indica se a pré-visualização marcou algum tipo incluido.
- Parâmetros:
    - `arquivo`: TAD Metadados de Arquivo.
- Possíveis retornos:
    - `bool(arquivo.get('tipos_incluidos', []))`: booleano calculado pela condição.
    - `False`: condição rejeitada/falsa.
- TADs envolvidos: Metadados de arquivo, Restrições, Regra de nome.

#### `definir_incluido_arquivo(arquivo, incluido)`
- Visibilidade: pública.
- Objetivo: Define se um TAD Metadados de Arquivo está incluído na pré-visualização do backup sem expor o campo interno `incluido` a outros módulos.
- Parâmetros:
    - `arquivo`: TAD Metadados de Arquivo.
    - `incluido`: valor convertido para booleano e armazenado como estado de inclusão.
- Possíveis retornos:
    - `OK`: estado de inclusão definido.
    - `ERRO_DADOS_INVALIDOS`: entrada não representa metadados de arquivo.
- TADs envolvidos: Metadados de arquivo, Restrições, Regra de nome.

#### `arquivo_atende_restricoes(arquivo, restricoes)`
- Visibilidade: pública.
- Objetivo: Verifica se um arquivo atende a todas as restrições configuradas.
- Parâmetros:
    - `arquivo`: TAD Metadados de Arquivo.
    - `restricoes`: TAD Restrições usado para filtrar arquivos.
- Possíveis retornos:
    - `_atende_restricao_extensao(arquivo, restricoes) and _atende_restricao_nome(arquivo, restricoes) and _atende_restricao_tamanho(arquivo, restricoes) and _atende_restricao_data_modificacao(arquivo, restricoes)`: retorno delegado para outra função.
    - `False`: condição rejeitada/falsa.
- TADs envolvidos: Metadados de arquivo, Restrições, Regra de nome.

#### `_atende_restricao_extensao(arquivo, restricoes)`
- Visibilidade: interna.
- Objetivo: Verifica filtro por extensão.
- Parâmetros:
    - `arquivo`: TAD Metadados de Arquivo.
    - `restricoes`: TAD Restrições usado para filtrar arquivos.
- Possíveis retornos:
    - `extensao_arquivo.strip().lower() in extensoes_normalizadas`: retorno delegado para outra função.
    - `True`: condição aceita/verdadeira.
    - `False`: condição rejeitada/falsa.
- TADs envolvidos: Metadados de arquivo, Restrições, Regra de nome.

#### `_atende_restricao_nome(arquivo, restricoes)`
- Visibilidade: interna.
- Objetivo: Verifica filtros por nome do arquivo.
- Parâmetros:
    - `arquivo`: TAD Metadados de Arquivo.
    - `restricoes`: TAD Restrições usado para filtrar arquivos.
- Possíveis retornos:
    - `True`: condição aceita/verdadeira.
    - `False`: condição rejeitada/falsa.
- TADs envolvidos: Metadados de arquivo, Restrições, Regra de nome.

#### `_normalizar_regras_nome(restricoes)`
- Visibilidade: interna.
- Objetivo: Normaliza regras novas de nome, ignorando entradas inválidas.
- Parâmetros:
    - `restricoes`: TAD Restrições usado para filtrar arquivos.
- Possíveis retornos:
    - `normalizadas`: valor calculado pela função.
- TADs envolvidos: Metadados de arquivo, Restrições, Regra de nome.

#### `_nome_atende_regra(nome, regra)`
- Visibilidade: interna.
- Objetivo: Indica se o nome atende uma regra normalizada.
- Parâmetros:
    - `nome`: nome informado pelo usuário ou nome interno do TAD.
    - `regra`: parâmetro usado pela função conforme o contexto do módulo.
- Possíveis retornos:
    - `valor in nome_normalizado`: valor calculado pela função.
    - `True`: condição aceita/verdadeira.
    - `nome_normalizado == valor`: valor calculado pela função.
- TADs envolvidos: Metadados de arquivo, Restrições, Regra de nome.

#### `_atende_restricao_tamanho(arquivo, restricoes)`
- Visibilidade: interna.
- Objetivo: Verifica filtros por tamanho mínimo e máximo.
- Parâmetros:
    - `arquivo`: TAD Metadados de Arquivo.
    - `restricoes`: TAD Restrições usado para filtrar arquivos.
- Possíveis retornos:
    - `True`: condição aceita/verdadeira.
    - `False`: condição rejeitada/falsa.
- TADs envolvidos: Metadados de arquivo, Restrições, Regra de nome.

#### `_atende_restricao_data_modificacao(arquivo, restricoes)`
- Visibilidade: interna.
- Objetivo: Verifica filtros por data de modificação.
- Parâmetros:
    - `arquivo`: TAD Metadados de Arquivo.
    - `restricoes`: TAD Restrições usado para filtrar arquivos.
- Possíveis retornos:
    - `True`: condição aceita/verdadeira.
    - `False`: condição rejeitada/falsa.
- TADs envolvidos: Metadados de arquivo, Restrições, Regra de nome.

#### `_converter_data_restricao_para_timestamp(valor)`
- Visibilidade: interna.
- Objetivo: Converte data de restrição em timestamp ou None quando vazia.
- Parâmetros:
    - `valor`: valor recebido, validado ou escrito em widget/TAD.
- Possíveis retornos:
    - `None`: ausência válida de dado ou falha sem objeto retornável.
    - `float(valor)`: retorno delegado para outra função.
    - `datetime.fromisoformat(valor).timestamp()`: retorno delegado para outra função.
- TADs envolvidos: Metadados de arquivo, Restrições, Regra de nome.

#### `verificar_permissao_leitura(caminho)`
- Visibilidade: pública.
- Objetivo: Verifica permissão de leitura em um caminho.
- Parâmetros:
    - `caminho`: caminho de arquivo ou pasta no sistema operacional.
- Possíveis retornos:
    - `False`: condição rejeitada/falsa.
    - `os.access(caminho, os.R_OK)`: retorno delegado para outra função.
- TADs envolvidos: Metadados de arquivo, Restrições, Regra de nome.

#### `verificar_permissao_escrita(caminho)`
- Visibilidade: pública.
- Objetivo: Verifica permissão de escrita em um caminho.
- Parâmetros:
    - `caminho`: caminho de arquivo ou pasta no sistema operacional.
- Possíveis retornos:
    - `False`: condição rejeitada/falsa.
    - `os.access(caminho, os.W_OK)`: retorno delegado para outra função.
- TADs envolvidos: Metadados de arquivo, Restrições, Regra de nome.

## Pasta `backupmanager/infra`

### Módulo `storage.py`

Resumo: Funções de armazenamento em arquivos JSON.

TADs/obrigações do módulo: Persistência JSON, Perfil, Configurações.

#### `_garantir_pasta_data()`
- Visibilidade: interna.
- Objetivo: Garante que a pasta data exista.
- Parâmetros:
    - nenhum parâmetro.
- Possíveis retornos:
    - `OK`: sucesso da operação.
    - `ERRO_SEM_PERMISSAO`: falha de permissão ou I/O na persistência.
- TADs envolvidos: Persistência JSON, Perfil, Configurações.

#### `_salvar_json(caminho, dados)`
- Visibilidade: interna.
- Objetivo: Salva dados em um arquivo JSON.
- Parâmetros:
    - `caminho`: caminho de arquivo ou pasta no sistema operacional.
    - `dados`: parâmetro usado pela função conforme o contexto do módulo.
- Possíveis retornos:
    - `OK`: sucesso da operação.
    - `codigo`: código de retorno propagado de chamada interna.
    - `ERRO_DADOS_INVALIDOS`: entrada com tipo, formato ou valor inválido.
    - `ERRO_SEM_PERMISSAO`: falha de permissão ou I/O na persistência.
- TADs envolvidos: Persistência JSON, Perfil, Configurações.

#### `_carregar_json(caminho, valor_padrao)`
- Visibilidade: interna.
- Objetivo: Carrega dados de um JSON ou retorna valor padrão se ele não existir.
- Parâmetros:
    - `caminho`: caminho de arquivo ou pasta no sistema operacional.
    - `valor_padrao`: parâmetro usado pela função conforme o contexto do módulo.
- Possíveis retornos:
    - `(OK, valor_padrao)`: tupla de retorno; normalmente combina código e dado/resultado.
    - `(OK, json.load(arquivo))`: tupla de retorno; normalmente combina código e dado/resultado.
    - `(ERRO_JSON_CORROMPIDO, valor_padrao)`: tupla de retorno; normalmente combina código e dado/resultado.
    - `(ERRO_SEM_PERMISSAO, valor_padrao)`: tupla de retorno; normalmente combina código e dado/resultado.
- TADs envolvidos: Persistência JSON, Perfil, Configurações.

#### `salvar_perfis(perfis)`
- Visibilidade: pública.
- Objetivo: Salva a lista de perfis no arquivo JSON oficial.
- Parâmetros:
    - `perfis`: coleção em memória de TADs Perfil.
- Possíveis retornos:
    - `_salvar_json(_PERFIS_PATH, perfis)`: retorno delegado para outra função.
- TADs envolvidos: Persistência JSON, Perfil, Configurações.

#### `carregar_perfis()`
- Visibilidade: pública.
- Objetivo: Carrega a lista de perfis do arquivo JSON oficial.
- Parâmetros:
    - nenhum parâmetro.
- Possíveis retornos:
    - `_carregar_json(_PERFIS_PATH, [])`: retorno delegado para outra função.
- TADs envolvidos: Persistência JSON, Perfil, Configurações.

#### `salvar_configuracoes(config)`
- Visibilidade: pública.
- Objetivo: Salva as configurações gerais da aplicação.
- Parâmetros:
    - `config`: TAD Configurações gerais da aplicação.
- Possíveis retornos:
    - `_salvar_json(_CONFIG_PATH, config)`: retorno delegado para outra função.
- TADs envolvidos: Persistência JSON, Perfil, Configurações.

#### `carregar_configuracoes()`
- Visibilidade: pública.
- Objetivo: Carrega as configurações gerais da aplicação.
- Parâmetros:
    - nenhum parâmetro.
- Possíveis retornos:
    - `_carregar_json(_CONFIG_PATH, {})`: retorno delegado para outra função.
- TADs envolvidos: Persistência JSON, Perfil, Configurações.

#### `criar_arquivos_padrao()`
- Visibilidade: pública.
- Objetivo: Garante a pasta `data` e os arquivos JSON essenciais.
- Parâmetros:
    - nenhum parâmetro.
- Possíveis retornos:
    - `OK`: sucesso da operação.
    - `codigo`: código de retorno propagado de chamada interna.
- TADs envolvidos: Persistência JSON, Perfil, Configurações.

## Pasta `backupmanager`

### Módulo `main.py`

Resumo: Ponto de entrada do BackupManager.

TADs/obrigações do módulo: Entrada da aplicação.

#### `main()`
- Visibilidade: pública.
- Objetivo: Ponto de entrada executavel da aplicação.
- Parâmetros:
    - nenhum parâmetro.
- Possíveis retornos:
    - retorno implícito `None`: função usada por asserção/callback ou efeito colateral.
- TADs envolvidos: Entrada da aplicação.

### Módulo `return_codes.py`

Resumo: Códigos de retorno padronizados do BackupManager.

TADs/obrigações do módulo: Códigos de retorno.

#### `obter_mensagem(codigo)`
- Visibilidade: pública.
- Objetivo: Retorna a mensagem de usuário associada a um código de retorno.
- Parâmetros:
    - `codigo`: código de retorno de return_codes.py.
- Possíveis retornos:
    - `_MENSAGENS.get(codigo, 'Codigo de retorno desconhecido.')`: retorno delegado para outra função.
- TADs envolvidos: Códigos de retorno.

## Pasta `backupmanager/ui`

### Módulo `actions.py`

Resumo: Ações principais, sincronização e mensagens da interface.

TADs/obrigações do módulo: Estado da interface, Perfil, Resultado de backup.

#### `criar_area_botoes(janela, estado_interface)`
- Visibilidade: pública.
- Objetivo: Cria os botões globais do cabeçalho da interface.
- Parâmetros:
    - `janela`: janela Tk/CustomTkinter.
    - `estado_interface`: TAD local da UI com widgets, seleções e dados editados em memória.
- Possíveis retornos:
    - `frame`: valor calculado pela função.
- TADs envolvidos: Estado da interface, Perfil, Resultado de backup.

#### `executar_backup_interface(estado_interface)`
- Visibilidade: pública.
- Objetivo: Inicia a execução de backup do perfil selecionado pela interface.
- Parâmetros:
    - `estado_interface`: TAD local da UI com widgets, seleções e dados editados em memória.
- Possíveis retornos:
    - `OK`: sucesso da operação.
    - `codigo_salvar`: valor calculado pela função.
    - `ERRO_DADOS_INVALIDOS`: entrada com tipo, formato ou valor inválido.
- TADs envolvidos: Estado da interface, Perfil, Resultado de backup.

#### `sincronizar_perfil_atual_interface(estado_interface, exibir_erros)`
- Visibilidade: pública.
- Objetivo: Sincroniza o formulário atual com o perfil em memória.
- Parâmetros:
    - `estado_interface`: TAD local da UI com widgets, seleções e dados editados em memória.
    - `exibir_erros`: booleano que decide se a UI mostra mensagens de validação.
- Possíveis retornos:
    - `(codigo, perfil)`: tupla de retorno; normalmente combina código e dado/resultado.
    - `(ERRO_DADOS_INVALIDOS, None)`: tupla de retorno; normalmente combina código e dado/resultado.
- TADs envolvidos: Estado da interface, Perfil, Resultado de backup.

#### `preencher_formulario_com_perfil(estado_interface, perfil)`
- Visibilidade: pública.
- Objetivo: Carrega os dados de um perfil nos widgets da interface.
- Parâmetros:
    - `estado_interface`: TAD local da UI com widgets, seleções e dados editados em memória.
    - `perfil`: TAD Perfil, dicionário persistido com id, nome, ativo e origens configuradas.
- Possíveis retornos:
    - `perfil`: valor calculado pela função.
- TADs envolvidos: Estado da interface, Perfil, Resultado de backup.

#### `limpar_formulario(estado_interface)`
- Visibilidade: pública.
- Objetivo: Limpa todos os campos visuais ligados ao perfil selecionado.
- Parâmetros:
    - `estado_interface`: TAD local da UI com widgets, seleções e dados editados em memória.
- Possíveis retornos:
    - `OK`: sucesso da operação.
- TADs envolvidos: Estado da interface, Perfil, Resultado de backup.

#### `mostrar_mensagem_resultado(codigo)`
- Visibilidade: pública.
- Objetivo: Mostra ao usuário a mensagem associada a um código de retorno.
- Parâmetros:
    - `codigo`: código de retorno de return_codes.py.
- Possíveis retornos:
    - `codigo`: código de retorno propagado de chamada interna.
- TADs envolvidos: Estado da interface, Perfil, Resultado de backup.

#### `_executar_backup_em_thread(estado_interface, perfil_id)`
- Visibilidade: interna.
- Objetivo: Executa backup fora da thread da interface.
- Parâmetros:
    - `estado_interface`: TAD local da UI com widgets, seleções e dados editados em memória.
    - `perfil_id`: identificador único de um perfil.
- Possíveis retornos:
    - `None`: ausência válida de dado ou falha sem objeto retornável.
- TADs envolvidos: Estado da interface, Perfil, Resultado de backup.

#### `_finalizar_backup_interface(estado_interface, codigo, resultado, erro)`
- Visibilidade: interna.
- Objetivo: Atualiza a interface após o termino do backup.
- Parâmetros:
    - `estado_interface`: TAD local da UI com widgets, seleções e dados editados em memória.
    - `codigo`: código de retorno de return_codes.py.
    - `resultado`: TAD Resultado geral de backup.
    - `erro`: erro capturado ou registro de erro.
- Possíveis retornos:
    - `codigo`: código de retorno propagado de chamada interna.
    - `ERRO_DADOS_INVALIDOS`: entrada com tipo, formato ou valor inválido.
- TADs envolvidos: Estado da interface, Perfil, Resultado de backup.

#### `_definir_estado_botao_backup(estado_interface, habilitado)`
- Visibilidade: interna.
- Objetivo: Habilita ou desabilita o botão de backup.
- Parâmetros:
    - `estado_interface`: TAD local da UI com widgets, seleções e dados editados em memória.
    - `habilitado`: booleano que controla estado visual habilitado/desabilitado.
- Possíveis retornos:
    - `OK`: sucesso da operação.
- TADs envolvidos: Estado da interface, Perfil, Resultado de backup.

#### `_obter_dados_formulario(estado_interface)`
- Visibilidade: interna.
- Objetivo: Coleta dados do formulário para um dicionário de perfil.
- Parâmetros:
    - `estado_interface`: TAD local da UI com widgets, seleções e dados editados em memória.
- Possíveis retornos:
    - `{'id': perfil_id, 'nome': estado_interface['entrada_nome'].get(), 'origens_configuradas': estado_interface['origens_configuradas'], 'ativo': estado_interface['ativo_var'].get()}`: novo dicionário/TAD montado pela função.
    - `None`: ausência válida de dado ou falha sem objeto retornável.
- TADs envolvidos: Estado da interface, Perfil, Resultado de backup.

#### `_montar_origens_configuradas_para_interface(perfil)`
- Visibilidade: interna.
- Objetivo: Copia as origens configuradas do perfil para uso seguro na interface.
- Parâmetros:
    - `perfil`: TAD Perfil, dicionário persistido com id, nome, ativo e origens configuradas.
- Possíveis retornos:
    - `[]`: lista vazia; nenhuma entrada aplicavel.
    - `_copiar_lista_dicionarios(origens_configuradas)`: retorno delegado para outra função.
- TADs envolvidos: Estado da interface, Perfil, Resultado de backup.

#### `_copiar_lista_dicionarios(lista)`
- Visibilidade: interna.
- Objetivo: Copia lista simples de dicionários aninhados.
- Parâmetros:
    - `lista`: listbox ou lista Python, conforme contexto.
- Possíveis retornos:
    - `copia`: valor calculado pela função.
- TADs envolvidos: Estado da interface, Perfil, Resultado de backup.

#### `_preencher_lista(lista, itens)`
- Visibilidade: interna.
- Objetivo: Substitui os itens de uma listbox.
- Parâmetros:
    - `lista`: listbox ou lista Python, conforme contexto.
    - `itens`: itens a preencher em uma lista visual.
- Possíveis retornos:
    - `OK`: sucesso da operação.
- TADs envolvidos: Estado da interface, Perfil, Resultado de backup.

#### `_preencher_entry(entrada, valor)`
- Visibilidade: interna.
- Objetivo: Substitui o conteúdo de um campo de texto.
- Parâmetros:
    - `entrada`: campo de texto da interface.
    - `valor`: valor recebido, validado ou escrito em widget/TAD.
- Possíveis retornos:
    - `OK`: sucesso da operação.
- TADs envolvidos: Estado da interface, Perfil, Resultado de backup.

#### `_mostrar_erro_validacao_formulario(estado_interface)`
- Visibilidade: interna.
- Objetivo: Mostra mensagem específica para dados inválidos do formulário.
- Parâmetros:
    - `estado_interface`: TAD local da UI com widgets, seleções e dados editados em memória.
- Possíveis retornos:
    - `ERRO_DADOS_INVALIDOS`: entrada com tipo, formato ou valor inválido.
- TADs envolvidos: Estado da interface, Perfil, Resultado de backup.

#### `_existe_conflito_operacao_interface(estado_interface)`
- Visibilidade: interna.
- Objetivo: Verifica conflito visual de mover/recortar em multiplos destinos.
- Parâmetros:
    - `estado_interface`: TAD local da UI com widgets, seleções e dados editados em memória.
- Possíveis retornos:
    - `False`: condição rejeitada/falsa.
    - `True`: condição aceita/verdadeira.
- TADs envolvidos: Estado da interface, Perfil, Resultado de backup.

### Módulo `backup_flow.py`

Resumo: Fluxo visual origem -> tipo -> destino da interface.

TADs/obrigações do módulo: Estado da interface, Origem configurada, Tipo de arquivo, Destino do tipo, Restrições.

#### `criar_area_origens_destinos(janela, estado_interface)`
- Visibilidade: pública.
- Objetivo: Cria a área visual do fluxo origem -> tipo -> destino.
- Parâmetros:
    - `janela`: janela Tk/CustomTkinter.
    - `estado_interface`: TAD local da UI com widgets, seleções e dados editados em memória.
- Possíveis retornos:
    - `frame`: valor calculado pela função.
- TADs envolvidos: Estado da interface, Origem configurada, Tipo de arquivo, Destino do tipo, Restrições.

#### `_criar_coluna_origens(container, estado_interface)`
- Visibilidade: interna.
- Objetivo: Cria a coluna de origens do fluxo de backup.
- Parâmetros:
    - `container`: widget pai onde componentes visuais serao criados.
    - `estado_interface`: TAD local da UI com widgets, seleções e dados editados em memória.
- Possíveis retornos:
    - `coluna_origens`: valor calculado pela função.
- TADs envolvidos: Estado da interface, Origem configurada, Tipo de arquivo, Destino do tipo, Restrições.

#### `_criar_coluna_tipos(container, estado_interface)`
- Visibilidade: interna.
- Objetivo: Cria a coluna de tipos da origem selecionada.
- Parâmetros:
    - `container`: widget pai onde componentes visuais serao criados.
    - `estado_interface`: TAD local da UI com widgets, seleções e dados editados em memória.
- Possíveis retornos:
    - `coluna_tipos`: valor calculado pela função.
- TADs envolvidos: Estado da interface, Origem configurada, Tipo de arquivo, Destino do tipo, Restrições.

#### `_criar_coluna_destinos(container, estado_interface)`
- Visibilidade: interna.
- Objetivo: Cria a coluna de destinos e operação do tipo selecionado.
- Parâmetros:
    - `container`: widget pai onde componentes visuais serao criados.
    - `estado_interface`: TAD local da UI com widgets, seleções e dados editados em memória.
- Possíveis retornos:
    - `coluna_destinos`: valor calculado pela função.
- TADs envolvidos: Estado da interface, Origem configurada, Tipo de arquivo, Destino do tipo, Restrições.

#### `_adicionar_origem_interface(estado_interface)`
- Visibilidade: interna.
- Objetivo: Adiciona uma pasta de origem na lista visual.
- Parâmetros:
    - `estado_interface`: TAD local da UI com widgets, seleções e dados editados em memória.
- Possíveis retornos:
    - `OK`: sucesso da operação.
- TADs envolvidos: Estado da interface, Origem configurada, Tipo de arquivo, Destino do tipo, Restrições.

#### `_adicionar_destino_interface(estado_interface)`
- Visibilidade: interna.
- Objetivo: Adiciona uma pasta de destino ao tipo selecionado.
- Parâmetros:
    - `estado_interface`: TAD local da UI com widgets, seleções e dados editados em memória.
- Possíveis retornos:
    - `OK`: sucesso da operação.
    - `ERRO_DADOS_INVALIDOS`: entrada com tipo, formato ou valor inválido.
- TADs envolvidos: Estado da interface, Origem configurada, Tipo de arquivo, Destino do tipo, Restrições.

#### `_adicionar_tipo_arquivo_interface(estado_interface)`
- Visibilidade: interna.
- Objetivo: Adiciona tipo de arquivo a origem selecionada.
- Parâmetros:
    - `estado_interface`: TAD local da UI com widgets, seleções e dados editados em memória.
- Possíveis retornos:
    - `OK`: sucesso da operação.
    - `ERRO_DADOS_INVALIDOS`: entrada com tipo, formato ou valor inválido.
- TADs envolvidos: Estado da interface, Origem configurada, Tipo de arquivo, Destino do tipo, Restrições.

#### `_remover_origem_configurada_interface(estado_interface)`
- Visibilidade: interna.
- Objetivo: Remove origem configurada selecionada.
- Parâmetros:
    - `estado_interface`: TAD local da UI com widgets, seleções e dados editados em memória.
- Possíveis retornos:
    - `OK`: sucesso da operação.
    - `ERRO_DADOS_INVALIDOS`: entrada com tipo, formato ou valor inválido.
- TADs envolvidos: Estado da interface, Origem configurada, Tipo de arquivo, Destino do tipo, Restrições.

#### `_remover_tipo_arquivo_interface(estado_interface)`
- Visibilidade: interna.
- Objetivo: Remove tipo de arquivo selecionado.
- Parâmetros:
    - `estado_interface`: TAD local da UI com widgets, seleções e dados editados em memória.
- Possíveis retornos:
    - `OK`: sucesso da operação.
    - `ERRO_DADOS_INVALIDOS`: entrada com tipo, formato ou valor inválido.
- TADs envolvidos: Estado da interface, Origem configurada, Tipo de arquivo, Destino do tipo, Restrições.

#### `_renomear_tipo_arquivo_interface(estado_interface)`
- Visibilidade: interna.
- Objetivo: Renomeia o tipo selecionado por diálogo de texto.
- Parâmetros:
    - `estado_interface`: TAD local da UI com widgets, seleções e dados editados em memória.
- Possíveis retornos:
    - `OK`: sucesso da operação ou cancelamento do diálogo sem alteração.
    - `ERRO_DADOS_INVALIDOS`: nenhum tipo selecionado ou nome vazio/inválido.
- TADs envolvidos: Estado da interface, Tipo de arquivo.

#### `_mostrar_menu_tipos_interface(evento, estado_interface, menu)`
- Visibilidade: interna.
- Objetivo: Mostra menu de contexto para o tipo clicado.
- Parâmetros:
    - `evento`: evento Tk do clique com posição local e global do mouse.
    - `estado_interface`: TAD local da UI com widgets, seleções e dados editados em memória.
    - `menu`: menu Tk com ações de renomear e excluir tipo.
- Possíveis retornos:
    - `OK`: menu exibido após selecionar o item clicado.
    - `ERRO_DADOS_INVALIDOS`: clique fora de item válido.
- TADs envolvidos: Estado da interface, Tipo de arquivo.

#### `_remover_destino_tipo_interface(estado_interface)`
- Visibilidade: interna.
- Objetivo: Remove destino selecionado do tipo atual.
- Parâmetros:
    - `estado_interface`: TAD local da UI com widgets, seleções e dados editados em memória.
- Possíveis retornos:
    - `OK`: sucesso da operação.
    - `ERRO_DADOS_INVALIDOS`: entrada com tipo, formato ou valor inválido.
- TADs envolvidos: Estado da interface, Origem configurada, Tipo de arquivo, Destino do tipo, Restrições.

#### `_alternar_origem_ativa_interface(estado_interface)`
- Visibilidade: interna.
- Objetivo: Liga ou desliga a origem selecionada.
- Parâmetros:
    - `estado_interface`: TAD local da UI com widgets, seleções e dados editados em memória.
- Possíveis retornos:
    - `OK`: sucesso da operação.
    - `ERRO_DADOS_INVALIDOS`: entrada com tipo, formato ou valor inválido.
- TADs envolvidos: Estado da interface, Origem configurada, Tipo de arquivo, Destino do tipo, Restrições.

#### `_alternar_tipo_ativo_interface(estado_interface)`
- Visibilidade: interna.
- Objetivo: Liga ou desliga o tipo selecionado.
- Parâmetros:
    - `estado_interface`: TAD local da UI com widgets, seleções e dados editados em memória.
- Possíveis retornos:
    - `OK`: sucesso da operação.
    - `ERRO_DADOS_INVALIDOS`: entrada com tipo, formato ou valor inválido.
- TADs envolvidos: Estado da interface, Origem configurada, Tipo de arquivo, Destino do tipo, Restrições.

#### `_abrir_pasta_selecionada(lista, tipo)`
- Visibilidade: interna.
- Objetivo: Abre a pasta selecionada em uma listbox.
- Parâmetros:
    - `lista`: listbox ou lista Python, conforme contexto.
    - `tipo`: TAD Tipo de Arquivo, com nome, ativo, restrições e destinos.
- Possíveis retornos:
    - `_abrir_pasta_por_caminho(caminho, tipo)`: retorno delegado para outra função.
    - `ERRO_DADOS_INVALIDOS`: entrada com tipo, formato ou valor inválido.
- TADs envolvidos: Estado da interface, Origem configurada, Tipo de arquivo, Destino do tipo, Restrições.

#### `_abrir_pasta_por_caminho(caminho, tipo)`
- Visibilidade: interna.
- Objetivo: Abre uma pasta pelo caminho informado.
- Parâmetros:
    - `caminho`: caminho de arquivo ou pasta no sistema operacional.
    - `tipo`: TAD Tipo de Arquivo, com nome, ativo, restrições e destinos.
- Possíveis retornos:
    - `OK`: sucesso da operação.
    - `ERRO_DADOS_INVALIDOS`: entrada com tipo, formato ou valor inválido.
- TADs envolvidos: Estado da interface, Origem configurada, Tipo de arquivo, Destino do tipo, Restrições.

#### `_abrir_origem_selecionada_interface(estado_interface)`
- Visibilidade: interna.
- Objetivo: Abre a pasta da origem selecionada.
- Parâmetros:
    - `estado_interface`: TAD local da UI com widgets, seleções e dados editados em memória.
- Possíveis retornos:
    - `_abrir_pasta_por_caminho(perfil_manager.obter_caminho_origem(origem), 'origem')`: retorno delegado para outra função.
    - `ERRO_DADOS_INVALIDOS`: entrada com tipo, formato ou valor inválido.
- TADs envolvidos: Estado da interface, Origem configurada, Tipo de arquivo, Destino do tipo, Restrições.

#### `_abrir_destino_selecionado_interface(estado_interface)`
- Visibilidade: interna.
- Objetivo: Abre a pasta do destino selecionado.
- Parâmetros:
    - `estado_interface`: TAD local da UI com widgets, seleções e dados editados em memória.
- Possíveis retornos:
    - `_abrir_pasta_por_caminho(perfil_manager.obter_caminho_destino(destino), 'destino')`: retorno delegado para outra função.
    - `ERRO_DADOS_INVALIDOS`: entrada com tipo, formato ou valor inválido.
- TADs envolvidos: Estado da interface, Origem configurada, Tipo de arquivo, Destino do tipo, Restrições.

#### `atualizar_lista_origens_configuradas(estado_interface)`
- Visibilidade: pública.
- Objetivo: Atualiza a listbox de origens configuradas no estado visual.
- Parâmetros:
    - `estado_interface`: TAD local da UI com widgets, seleções e dados editados em memória.
- Possíveis retornos:
    - `OK`: sucesso da operação.
- TADs envolvidos: Estado da interface, Origem configurada, Tipo de arquivo, Destino do tipo, Restrições.

#### `_atualizar_lista_tipos_origem(estado_interface)`
- Visibilidade: interna.
- Objetivo: Atualiza tipos da origem selecionada.
- Parâmetros:
    - `estado_interface`: TAD local da UI com widgets, seleções e dados editados em memória.
- Possíveis retornos:
    - `OK`: sucesso da operação.
    - `ERRO_DADOS_INVALIDOS`: entrada com tipo, formato ou valor inválido.
- TADs envolvidos: Estado da interface, Origem configurada, Tipo de arquivo, Destino do tipo, Restrições.

#### `_atualizar_lista_destinos_tipo(estado_interface)`
- Visibilidade: interna.
- Objetivo: Atualiza destinos do tipo selecionado.
- Parâmetros:
    - `estado_interface`: TAD local da UI com widgets, seleções e dados editados em memória.
- Possíveis retornos:
    - `OK`: sucesso da operação.
    - `ERRO_DADOS_INVALIDOS`: entrada com tipo, formato ou valor inválido.
- TADs envolvidos: Estado da interface, Origem configurada, Tipo de arquivo, Destino do tipo, Restrições.

#### `_selecionar_destino_tipo_interface(estado_interface)`
- Visibilidade: interna.
- Objetivo: Seleciona destino do tipo atual e carrega sua operação.
- Parâmetros:
    - `estado_interface`: TAD local da UI com widgets, seleções e dados editados em memória.
- Possíveis retornos:
    - `OK`: sucesso da operação.
    - `ERRO_DADOS_INVALIDOS`: entrada com tipo, formato ou valor inválido.
- TADs envolvidos: Estado da interface, Origem configurada, Tipo de arquivo, Destino do tipo, Restrições.

#### `_selecionar_destino_por_indice(estado_interface, indice)`
- Visibilidade: interna.
- Objetivo: Seleciona destino visualmente por índice.
- Parâmetros:
    - `estado_interface`: TAD local da UI com widgets, seleções e dados editados em memória.
    - `indice`: posição selecionada em lista/listbox.
- Possíveis retornos:
    - `_selecionar_destino_tipo_interface(estado_interface)`: retorno delegado para outra função.
    - `ERRO_DADOS_INVALIDOS`: entrada com tipo, formato ou valor inválido.
- TADs envolvidos: Estado da interface, Origem configurada, Tipo de arquivo, Destino do tipo, Restrições.

#### `_obter_destino_selecionado(estado_interface)`
- Visibilidade: interna.
- Objetivo: Retorna destino selecionado do tipo atual.
- Parâmetros:
    - `estado_interface`: TAD local da UI com widgets, seleções e dados editados em memória.
- Possíveis retornos:
    - `destinos[indice]`: valor calculado pela função.
    - `None`: ausência válida de dado ou falha sem objeto retornável.
- TADs envolvidos: Estado da interface, Origem configurada, Tipo de arquivo, Destino do tipo, Restrições.

#### `_atualizar_operacao_destino_interface(estado_interface)`
- Visibilidade: interna.
- Objetivo: Atualiza operação do destino selecionado.
- Parâmetros:
    - `estado_interface`: TAD local da UI com widgets, seleções e dados editados em memória.
- Possíveis retornos:
    - `OK`: sucesso da operação.
- TADs envolvidos: Estado da interface, Origem configurada, Tipo de arquivo, Destino do tipo, Restrições.

#### `_selecionar_origem_configurada_interface(estado_interface)`
- Visibilidade: interna.
- Objetivo: Seleciona origem e atualiza tipos relacionados.
- Parâmetros:
    - `estado_interface`: TAD local da UI com widgets, seleções e dados editados em memória.
- Possíveis retornos:
    - `OK`: sucesso da operação.
    - `ERRO_DADOS_INVALIDOS`: entrada com tipo, formato ou valor inválido.
- TADs envolvidos: Estado da interface, Origem configurada, Tipo de arquivo, Destino do tipo, Restrições.

#### `_selecionar_tipo_arquivo_interface(estado_interface)`
- Visibilidade: interna.
- Objetivo: Seleciona tipo e carrega filtros e destinos.
- Parâmetros:
    - `estado_interface`: TAD local da UI com widgets, seleções e dados editados em memória.
- Possíveis retornos:
    - `OK`: sucesso da operação.
    - `ERRO_DADOS_INVALIDOS`: entrada com tipo, formato ou valor inválido.
- TADs envolvidos: Estado da interface, Origem configurada, Tipo de arquivo, Destino do tipo, Restrições.

#### `selecionar_origem_por_indice(estado_interface, indice)`
- Visibilidade: pública.
- Objetivo: Seleciona visualmente uma origem pelo índice da listbox.
- Parâmetros:
    - `estado_interface`: TAD local da UI com widgets, seleções e dados editados em memória.
    - `indice`: posição selecionada em lista/listbox.
- Possíveis retornos:
    - `_selecionar_origem_configurada_interface(estado_interface)`: retorno delegado para outra função.
    - `ERRO_DADOS_INVALIDOS`: entrada com tipo, formato ou valor inválido.
- TADs envolvidos: Estado da interface, Origem configurada, Tipo de arquivo, Destino do tipo, Restrições.

#### `_selecionar_tipo_por_indice(estado_interface, indice)`
- Visibilidade: interna.
- Objetivo: Seleciona tipo visualmente por índice.
- Parâmetros:
    - `estado_interface`: TAD local da UI com widgets, seleções e dados editados em memória.
    - `indice`: posição selecionada em lista/listbox.
- Possíveis retornos:
    - `_selecionar_tipo_arquivo_interface(estado_interface)`: retorno delegado para outra função.
    - `ERRO_DADOS_INVALIDOS`: entrada com tipo, formato ou valor inválido.
- TADs envolvidos: Estado da interface, Origem configurada, Tipo de arquivo, Destino do tipo, Restrições.

#### `_obter_origem_selecionada(estado_interface)`
- Visibilidade: interna.
- Objetivo: Retorna origem selecionada.
- Parâmetros:
    - `estado_interface`: TAD local da UI com widgets, seleções e dados editados em memória.
- Possíveis retornos:
    - `origens[indice]`: valor calculado pela função.
    - `None`: ausência válida de dado ou falha sem objeto retornável.
- TADs envolvidos: Estado da interface, Origem configurada, Tipo de arquivo, Destino do tipo, Restrições.

#### `_obter_tipo_selecionado(estado_interface)`
- Visibilidade: interna.
- Objetivo: Retorna tipo selecionado.
- Parâmetros:
    - `estado_interface`: TAD local da UI com widgets, seleções e dados editados em memória.
- Possíveis retornos:
    - `tipos[indice]`: valor calculado pela função.
    - `None`: ausência válida de dado ou falha sem objeto retornável.
- TADs envolvidos: Estado da interface, Origem configurada, Tipo de arquivo, Destino do tipo, Restrições.

#### `_preencher_nome_tipo_interface(estado_interface, nome)`
- Visibilidade: interna.
- Objetivo: Substitui o texto do campo de nome do tipo.
- Parâmetros:
    - `estado_interface`: TAD local da UI com widgets, seleções e dados editados em memória.
    - `nome`: nome do tipo a exibir no campo de texto.
- Possíveis retornos:
    - `OK`: sucesso da operação.
- TADs envolvidos: Estado da interface, Tipo de arquivo.

#### `salvar_tipo_selecionado_em_memoria(estado_interface)`
- Visibilidade: pública.
- Objetivo: Grava no tipo selecionado os campos editados na tela.
- Parâmetros:
    - `estado_interface`: TAD local da UI com widgets, seleções e dados editados em memória.
- Possíveis retornos:
    - `OK`: sucesso da operação.
- TADs envolvidos: Estado da interface, Origem configurada, Tipo de arquivo, Destino do tipo, Restrições.

### Módulo `converters.py`

Resumo: Conversores usados pela camada de interface.

TADs/obrigações do módulo: Valores de formulário.

#### `converter_inteiro_opcional(texto, padrao)`
- Visibilidade: pública.
- Objetivo: Converte texto para inteiro não negativo ou retorna padrão quando vazio.
- Parâmetros:
    - `texto`: texto digitado pelo usuário.
    - `padrao`: valor usado quando o campo está vazio.
- Possíveis retornos:
    - `valor`: valor calculado pela função.
    - `padrao`: valor calculado pela função.
    - `'invalido'`: sentinela de campo visual inválido.
- TADs envolvidos: Valores de formulário.

#### `converter_data_opcional(texto)`
- Visibilidade: pública.
- Objetivo: Valida uma data opcional em formato ISO e retorna o texto normalizado.
- Parâmetros:
    - `texto`: texto digitado pelo usuário.
- Possíveis retornos:
    - `texto`: valor calculado pela função.
    - `None`: ausência válida de dado ou falha sem objeto retornável.
    - `'invalido'`: sentinela de campo visual inválido.
- TADs envolvidos: Valores de formulário.

### Módulo `interface.py`

Resumo: Interface gráfica do BackupManager usando tkinter e customtkinter.

TADs/obrigações do módulo: Estado da interface, Estado da aplicação.

#### `iniciar_interface()`
- Visibilidade: pública.
- Objetivo: Inicia a interface gráfica principal do BackupManager.
- Parâmetros:
    - nenhum parâmetro.
- Possíveis retornos:
    - `None`: ausência válida de dado ou falha sem objeto retornável.
- TADs envolvidos: Estado da interface, Estado da aplicação.

#### `_criar_estado_interface()`
- Visibilidade: interna.
- Objetivo: Cria o dicionário de estado da interface.
- Parâmetros:
    - nenhum parâmetro.
- Possíveis retornos:
    - `{'janela': None, 'acao_fechar': None, 'ids_perfis': [], 'lista_perfis': None, 'entrada_nome': None, 'lista_origens': None, 'lista_tipos': None, 'lista_destinos': None, 'entrada_tipo_nome': None, 'operacao_var': None, 'destino_selecionado_indice': None, 'ativo_var': None, 'frame_extensoes': None, 'extensoes_vars': {}, 'entrada_nova_extensao': None, 'entrada_regra_nome': None, 'modo_regra_nome_var': None, 'lista_regras_nome': None, 'regras_nome': [], 'entrada_tamanho_min': None, 'entrada_tamanho_max': None, 'entrada_data_min': None, 'entrada_data_max': None, 'perfil_selecionado_id': None, 'origens_configuradas': [], 'origem_selecionada_indice': None, 'tipo_selecionado_indice': None, 'botao_backup': None, 'backup_em_execucao': False}`: novo dicionário/TAD montado pela função.
- TADs envolvidos: Estado da interface, Estado da aplicação.

#### `_criar_janela_principal()`
- Visibilidade: interna.
- Objetivo: Cria a janela principal.
- Parâmetros:
    - nenhum parâmetro.
- Possíveis retornos:
    - `janela`: valor calculado pela função.
- TADs envolvidos: Estado da interface, Estado da aplicação.

### Módulo `profiles.py`

Resumo: Painel de perfis da interface.

TADs/obrigações do módulo: Estado da interface, Perfil.

#### `criar_area_perfis(janela, estado_interface)`
- Visibilidade: pública.
- Objetivo: Cria o painel de gerenciamento de perfis.
- Parâmetros:
    - `janela`: janela Tk/CustomTkinter.
    - `estado_interface`: TAD local da UI com widgets, seleções e dados editados em memória.
- Possíveis retornos:
    - `frame`: valor calculado pela função.
- TADs envolvidos: Estado da interface, Perfil.

#### `atualizar_lista_perfis(estado_interface)`
- Visibilidade: pública.
- Objetivo: Recarrega a listbox de perfis a partir do controller.
- Parâmetros:
    - `estado_interface`: TAD local da UI com widgets, seleções e dados editados em memória.
- Possíveis retornos:
    - `codigo`: código de retorno propagado de chamada interna.
- TADs envolvidos: Estado da interface, Perfil.

#### `selecionar_perfil_por_id(estado_interface, perfil_id)`
- Visibilidade: pública.
- Objetivo: Seleciona na interface o perfil identificado por `perfil_id`.
- Parâmetros:
    - `estado_interface`: TAD local da UI com widgets, seleções e dados editados em memória.
    - `perfil_id`: identificador único de um perfil.
- Possíveis retornos:
    - `_selecionar_perfil_interface(estado_interface)`: retorno delegado para outra função.
    - `ERRO_DADOS_INVALIDOS`: entrada com tipo, formato ou valor inválido.
- TADs envolvidos: Estado da interface, Perfil.

#### `_criar_perfil_interface(estado_interface)`
- Visibilidade: interna.
- Objetivo: Cria um perfil a partir do nome informado na interface.
- Parâmetros:
    - `estado_interface`: TAD local da UI com widgets, seleções e dados editados em memória.
- Possíveis retornos:
    - `codigo`: código de retorno propagado de chamada interna.
- TADs envolvidos: Estado da interface, Perfil.

#### `_selecionar_perfil_interface(estado_interface)`
- Visibilidade: interna.
- Objetivo: Seleciona o perfil destacado na lista.
- Parâmetros:
    - `estado_interface`: TAD local da UI com widgets, seleções e dados editados em memória.
- Possíveis retornos:
    - `OK`: sucesso da operação.
    - `ERRO_DADOS_INVALIDOS`: entrada com tipo, formato ou valor inválido.
    - `codigo`: código de retorno propagado de chamada interna.
- TADs envolvidos: Estado da interface, Perfil.

#### `_excluir_perfil_interface(estado_interface)`
- Visibilidade: interna.
- Objetivo: Exclui o perfil selecionado.
- Parâmetros:
    - `estado_interface`: TAD local da UI com widgets, seleções e dados editados em memória.
- Possíveis retornos:
    - `codigo`: código de retorno propagado de chamada interna.
    - `mostrar_mensagem_resultado(ERRO_DADOS_INVALIDOS)`: retorno delegado para outra função.
    - `OK`: sucesso da operação.
- TADs envolvidos: Estado da interface, Perfil.

### Módulo `restrictions.py`

Resumo: Área de restrições e filtros da UI.

TADs/obrigações do módulo: Estado da interface, Restrições, Tipo de arquivo, Configurações.

#### `criar_area_restricoes(janela, estado_interface, ao_alterar_restricoes=None)`
- Visibilidade: pública.
- Objetivo: Cria o painel de restrições de arquivos.
- Parâmetros:
    - `janela`: janela Tk/CustomTkinter.
    - `estado_interface`: TAD local da UI com widgets, seleções e dados editados em memória.
    - `ao_alterar_restricoes`: callback chamado quando restrições mudam na UI.
- Possíveis retornos:
    - `frame`: valor calculado pela função.
- TADs envolvidos: Estado da interface, Restrições, Tipo de arquivo, Configurações.

#### `_criar_area_extensoes(container, estado_interface)`
- Visibilidade: interna.
- Objetivo: Cria a seleção de extensões disponíveis por checkbox.
- Parâmetros:
    - `container`: widget pai onde componentes visuais serao criados.
    - `estado_interface`: TAD local da UI com widgets, seleções e dados editados em memória.
- Possíveis retornos:
    - `estado_interface['frame_extensoes']`: valor calculado pela função.
- TADs envolvidos: Estado da interface, Restrições, Tipo de arquivo, Configurações.

#### `_criar_area_regras_nome(container, estado_interface, ao_alterar_restricoes=None)`
- Visibilidade: interna.
- Objetivo: Cria o formulário e a lista de regras por nome de arquivo.
- Parâmetros:
    - `container`: widget pai onde componentes visuais serao criados.
    - `estado_interface`: TAD local da UI com widgets, seleções e dados editados em memória.
    - `ao_alterar_restricoes`: callback chamado quando restrições mudam na UI.
- Possíveis retornos:
    - `estado_interface['lista_regras_nome']`: valor calculado pela função.
- TADs envolvidos: Estado da interface, Restrições, Tipo de arquivo, Configurações.

#### `_criar_area_tamanho(container, estado_interface)`
- Visibilidade: interna.
- Objetivo: Cria os campos de tamanho mínimo e máximo.
- Parâmetros:
    - `container`: widget pai onde componentes visuais serao criados.
    - `estado_interface`: TAD local da UI com widgets, seleções e dados editados em memória.
- Possíveis retornos:
    - `linha_tamanhos`: valor calculado pela função.
- TADs envolvidos: Estado da interface, Restrições, Tipo de arquivo, Configurações.

#### `_criar_area_datas(container, estado_interface)`
- Visibilidade: interna.
- Objetivo: Cria os campos de data mínima e máxima de modificação.
- Parâmetros:
    - `container`: widget pai onde componentes visuais serao criados.
    - `estado_interface`: TAD local da UI com widgets, seleções e dados editados em memória.
- Possíveis retornos:
    - `linha_datas`: valor calculado pela função.
- TADs envolvidos: Estado da interface, Restrições, Tipo de arquivo, Configurações.

#### `atualizar_checkboxes_extensoes(estado_interface, extensoes_marcadas=None)`
- Visibilidade: pública.
- Objetivo: Recria a lista de checkboxes de extensões disponíveis.
- Parâmetros:
    - `estado_interface`: TAD local da UI com widgets, seleções e dados editados em memória.
    - `extensoes_marcadas`: parâmetro usado pela função conforme o contexto do módulo.
- Possíveis retornos:
    - `OK`: sucesso da operação.
    - `ERRO_DADOS_INVALIDOS`: entrada com tipo, formato ou valor inválido.
    - `codigo`: código de retorno propagado de chamada interna.
- TADs envolvidos: Estado da interface, Restrições, Tipo de arquivo, Configurações.

#### `_adicionar_extensao_interface(estado_interface)`
- Visibilidade: interna.
- Objetivo: Adiciona uma extensão customizada a lista disponível e a marca.
- Parâmetros:
    - `estado_interface`: TAD local da UI com widgets, seleções e dados editados em memória.
- Possíveis retornos:
    - `OK`: sucesso da operação.
    - `ERRO_DADOS_INVALIDOS`: entrada com tipo, formato ou valor inválido.
    - `codigo`: código de retorno propagado de chamada interna.
- TADs envolvidos: Estado da interface, Restrições, Tipo de arquivo, Configurações.

#### `_adicionar_regra_nome_interface(estado_interface, ao_alterar_restricoes=None)`
- Visibilidade: interna.
- Objetivo: Adiciona uma regra de nome na memória visual do tipo atual.
- Parâmetros:
    - `estado_interface`: TAD local da UI com widgets, seleções e dados editados em memória.
    - `ao_alterar_restricoes`: callback chamado quando restrições mudam na UI.
- Possíveis retornos:
    - `OK`: sucesso da operação.
    - `ERRO_DADOS_INVALIDOS`: entrada com tipo, formato ou valor inválido.
- TADs envolvidos: Estado da interface, Restrições, Tipo de arquivo, Configurações.

#### `_remover_regra_nome_interface(estado_interface, ao_alterar_restricoes=None)`
- Visibilidade: interna.
- Objetivo: Remove a regra de nome selecionada da memória visual.
- Parâmetros:
    - `estado_interface`: TAD local da UI com widgets, seleções e dados editados em memória.
    - `ao_alterar_restricoes`: callback chamado quando restrições mudam na UI.
- Possíveis retornos:
    - `OK`: sucesso da operação.
    - `ERRO_DADOS_INVALIDOS`: entrada com tipo, formato ou valor inválido.
- TADs envolvidos: Estado da interface, Restrições, Tipo de arquivo, Configurações.

#### `atualizar_lista_regras_nome(estado_interface, regras)`
- Visibilidade: pública.
- Objetivo: Atualiza a listbox de regras de nome e o estado correspondente.
- Parâmetros:
    - `estado_interface`: TAD local da UI com widgets, seleções e dados editados em memória.
    - `regras`: parâmetro usado pela função conforme o contexto do módulo.
- Possíveis retornos:
    - `OK`: sucesso da operação.
    - `ERRO_DADOS_INVALIDOS`: entrada com tipo, formato ou valor inválido.
- TADs envolvidos: Estado da interface, Restrições, Tipo de arquivo, Configurações.

#### `_obter_regras_nome_interface(estado_interface)`
- Visibilidade: interna.
- Objetivo: Retorna uma copia normalizada das regras de nome em memória.
- Parâmetros:
    - `estado_interface`: TAD local da UI com widgets, seleções e dados editados em memória.
- Possíveis retornos:
    - `_normalizar_regras_nome_interface(estado_interface.get('regras_nome', []))`: retorno delegado para outra função.
- TADs envolvidos: Estado da interface, Restrições, Tipo de arquivo, Configurações.

#### `_normalizar_regras_nome_interface(regras)`
- Visibilidade: interna.
- Objetivo: Normaliza regras de nome para persistência no perfil.
- Parâmetros:
    - `regras`: parâmetro usado pela função conforme o contexto do módulo.
- Possíveis retornos:
    - `normalizadas`: valor calculado pela função.
    - `[]`: lista vazia; nenhuma entrada aplicavel.
- TADs envolvidos: Estado da interface, Restrições, Tipo de arquivo, Configurações.

#### `_obter_regras_nome_das_restricoes(restricoes)`
- Visibilidade: interna.
- Objetivo: Extrai regras de nome salvas no formato atual.
- Parâmetros:
    - `restricoes`: TAD Restrições usado para filtrar arquivos.
- Possíveis retornos:
    - `_normalizar_regras_nome_interface(perfil_manager.obter_regras_nome_restricoes(restricoes))`: retorno delegado para outra função.
- TADs envolvidos: Estado da interface, Restrições, Tipo de arquivo, Configurações.

#### `_obter_modo_regra_nome_interface(estado_interface)`
- Visibilidade: interna.
- Objetivo: Retorna o modo selecionado para uma nova regra de nome.
- Parâmetros:
    - `estado_interface`: TAD local da UI com widgets, seleções e dados editados em memória.
- Possíveis retornos:
    - `'contem'`: valor calculado pela função.
    - `'exato'`: valor calculado pela função.
- TADs envolvidos: Estado da interface, Restrições, Tipo de arquivo, Configurações.

#### `_formatar_regra_nome_interface(regra)`
- Visibilidade: interna.
- Objetivo: Formata uma regra de nome para exibição em listbox.
- Parâmetros:
    - `regra`: parâmetro usado pela função conforme o contexto do módulo.
- Possíveis retornos:
    - `rotulo + ': ' + regra.get('valor', '')`: retorno delegado para outra função.
- TADs envolvidos: Estado da interface, Restrições, Tipo de arquivo, Configurações.

#### `criar_restricoes_da_interface(estado_interface)`
- Visibilidade: pública.
- Objetivo: Monta o dicionário de restrições a partir dos campos da tela.
- Parâmetros:
    - `estado_interface`: TAD local da UI com widgets, seleções e dados editados em memória.
- Possíveis retornos:
    - `perfil_manager.criar_restricoes(_obter_extensoes_marcadas(estado_interface), _obter_regras_nome_interface(estado_interface), 0 if tamanho_min == 'invalido' else tamanho_min, None if tamanho_max == 'invalido' else tamanho_max, None if data_min == 'invalido' else data_min, None if data_max == 'invalido' else data_max)`: retorno delegado para outra função.
- TADs envolvidos: Estado da interface, Restrições, Tipo de arquivo, Configurações.

#### `_obter_restricoes_do_tipo(tipo)`
- Visibilidade: interna.
- Objetivo: Retorna restrições do tipo no formato atual.
- Parâmetros:
    - `tipo`: TAD Tipo de Arquivo, com nome, ativo, restrições e destinos.
- Possíveis retornos:
    - `perfil_manager.obter_restricoes_tipo(tipo)`: retorno delegado para outra função.
- TADs envolvidos: Estado da interface, Restrições, Tipo de arquivo, Configurações.

#### `preencher_formulario_com_tipo(estado_interface, tipo, atualizar_destinos_callback=None)`
- Visibilidade: pública.
- Objetivo: Carrega no painel de restrições os dados de um tipo selecionado.
- Parâmetros:
    - `estado_interface`: TAD local da UI com widgets, seleções e dados editados em memória.
    - `tipo`: TAD Tipo de Arquivo, com nome, ativo, restrições e destinos.
    - `atualizar_destinos_callback`: callback para atualizar destinos após carregar tipo.
- Possíveis retornos:
    - `OK`: sucesso da operação.
    - `ERRO_DADOS_INVALIDOS`: entrada com tipo, formato ou valor inválido.
- TADs envolvidos: Estado da interface, Restrições, Tipo de arquivo, Configurações.

#### `limpar_area_tipo_destino(estado_interface)`
- Visibilidade: pública.
- Objetivo: Limpa campos relacionados ao tipo e seus destinos.
- Parâmetros:
    - `estado_interface`: TAD local da UI com widgets, seleções e dados editados em memória.
- Possíveis retornos:
    - `OK`: sucesso da operação.
- TADs envolvidos: Estado da interface, Restrições, Tipo de arquivo, Configurações.

#### `formulario_tipo_possui_valor_invalido(estado_interface)`
- Visibilidade: pública.
- Objetivo: Indica se algum filtro numérico ou de data do tipo atual é inválido.
- Parâmetros:
    - `estado_interface`: TAD local da UI com widgets, seleções e dados editados em memória.
- Possíveis retornos:
    - `tamanho_min == 'invalido' or tamanho_max == 'invalido' or data_min == 'invalido' or (data_max == 'invalido')`: retorno delegado para outra função.
- TADs envolvidos: Estado da interface, Restrições, Tipo de arquivo, Configurações.

#### `_obter_extensoes_marcadas(estado_interface)`
- Visibilidade: interna.
- Objetivo: Retorna as extensões marcadas no painel de checkboxes.
- Parâmetros:
    - `estado_interface`: TAD local da UI com widgets, seleções e dados editados em memória.
- Possíveis retornos:
    - `extensoes`: valor calculado pela função.
- TADs envolvidos: Estado da interface, Restrições, Tipo de arquivo, Configurações.

#### `_preencher_entry(entrada, valor)`
- Visibilidade: interna.
- Objetivo: Sem docstring.
- Parâmetros:
    - `entrada`: campo de texto da interface.
    - `valor`: valor recebido, validado ou escrito em widget/TAD.
- Possíveis retornos:
    - `OK`: sucesso da operação.
- TADs envolvidos: Estado da interface, Restrições, Tipo de arquivo, Configurações.

#### `_executar_callback(callback)`
- Visibilidade: interna.
- Objetivo: Sem docstring.
- Parâmetros:
    - `callback`: função opcional chamada pelo fluxo visual.
- Possíveis retornos:
    - `OK`: sucesso da operação.
    - `callback()`: retorno delegado para outra função.
- TADs envolvidos: Estado da interface, Restrições, Tipo de arquivo, Configurações.

#### `_mostrar_mensagem_resultado(codigo)`
- Visibilidade: interna.
- Objetivo: Sem docstring.
- Parâmetros:
    - `codigo`: código de retorno de return_codes.py.
- Possíveis retornos:
    - `codigo`: código de retorno propagado de chamada interna.
- TADs envolvidos: Estado da interface, Restrições, Tipo de arquivo, Configurações.

### Módulo `ui_state.py`

Resumo: Funções de acesso para o estado visual de origens configuradas.

TADs/obrigações do módulo: Estado da interface, Origem configurada.

#### `obter_origens_configuradas(estado_interface)`
- Visibilidade: pública.
- Objetivo: Retorna a lista de origens configuradas mantida no estado visual da interface. Centraliza a leitura de `origens_configuradas`, evitando que `backup_flow.py` e `actions.py` precisem acessar diretamente a chave interna do dicionário.
- Parâmetros:
    - `estado_interface`: TAD local da UI com widgets, seleções e dados editados em memória.
- Possíveis retornos:
    - lista de origens configuradas.
    - `[]`: quando a entrada não possui lista válida.
- TADs envolvidos: Estado da interface, Origem configurada.

#### `definir_origens_configuradas(estado_interface, origens_configuradas)`
- Visibilidade: pública.
- Objetivo: Substitui a lista completa de origens configuradas no estado da interface, normalmente ao carregar um perfil ou limpar o formulário.
- Parâmetros:
    - `estado_interface`: TAD local da UI.
    - `origens_configuradas`: lista completa de TADs Origem.
- Possíveis retornos:
    - `OK`: sucesso da operação.
    - `ERRO_DADOS_INVALIDOS`: quando a entrada não é lista.
- TADs envolvidos: Estado da interface, Origem configurada.

#### `adicionar_origem_configurada(estado_interface, origem)`
- Visibilidade: pública.
- Objetivo: Adiciona uma origem já construída ao estado da interface. Substitui o antigo acesso direto com `estado_interface["origens_configuradas"].append(origem)`.
- Parâmetros:
    - `estado_interface`: TAD local da UI.
    - `origem`: TAD Origem Configurada.
- Possíveis retornos:
    - `(OK, indice)`: sucesso e posição da origem adicionada.
- TADs envolvidos: Estado da interface, Origem configurada.

#### `remover_origem_configurada_por_indice(estado_interface, indice)`
- Visibilidade: pública.
- Objetivo: Remove a origem configurada na posição informada. Substitui o antigo acesso direto com `pop` sobre a lista interna.
- Parâmetros:
    - `estado_interface`: TAD local da UI.
    - `indice`: posição selecionada na interface.
- Possíveis retornos:
    - `OK`: sucesso da operação.
    - `ERRO_DADOS_INVALIDOS`: índice inválido ou fora do intervalo.
- TADs envolvidos: Estado da interface, Origem configurada.

#### `obter_origem_configurada_por_indice(estado_interface, indice)`
- Visibilidade: pública.
- Objetivo: Retorna uma origem configurada por posição, sem que o chamador precise acessar diretamente a lista interna.
- Parâmetros:
    - `estado_interface`: TAD local da UI.
    - `indice`: posição da origem.
- Possíveis retornos:
    - TAD Origem Configurada.
    - `None`: índice inválido.
- TADs envolvidos: Estado da interface, Origem configurada.

#### `definir_origem_selecionada_indice(estado_interface, indice)`
- Visibilidade: pública.
- Objetivo: Define qual origem está selecionada na interface.
- Parâmetros:
    - `estado_interface`: TAD local da UI.
    - `indice`: posição selecionada.
- Possíveis retornos:
    - `OK`: sucesso da operação.
- TADs envolvidos: Estado da interface.

#### `obter_origem_selecionada_indice(estado_interface)`
- Visibilidade: pública.
- Objetivo: Retorna o índice da origem selecionada, ou `None` quando não há seleção.
- Parâmetros:
    - `estado_interface`: TAD local da UI.
- Possíveis retornos:
    - índice selecionado.
    - `None`: nenhuma origem selecionada.
- TADs envolvidos: Estado da interface.

#### `obter_origem_selecionada(estado_interface)`
- Visibilidade: pública.
- Objetivo: Retorna a origem atualmente selecionada combinando índice selecionado e acesso por índice em um único ponto.
- Parâmetros:
    - `estado_interface`: TAD local da UI.
- Possíveis retornos:
    - TAD Origem Configurada.
    - `None`: nenhuma origem válida selecionada.
- TADs envolvidos: Estado da interface, Origem configurada.

#### `total_origens_configuradas(estado_interface)`
- Visibilidade: pública.
- Objetivo: Retorna a quantidade de origens configuradas em memória na interface.
- Parâmetros:
    - `estado_interface`: TAD local da UI.
- Possíveis retornos:
    - inteiro com a quantidade de origens.
- TADs envolvidos: Estado da interface.

### Módulo `theme.py`

Resumo: Tema visual e helpers de janelas da interface.

TADs/obrigações do módulo: Widgets Tk/CustomTkinter.

#### `configurar_estilo_visual()`
- Visibilidade: pública.
- Objetivo: Configura o tema global usado pelos widgets CustomTkinter.
- Parâmetros:
    - nenhum parâmetro.
- Possíveis retornos:
    - `OK`: sucesso da operação.
- TADs envolvidos: Widgets Tk/CustomTkinter.

#### `configurar_frame(frame)`
- Visibilidade: pública.
- Objetivo: Aplica a configuração visual neutra usada em frames de layout.
- Parâmetros:
    - `frame`: widget frame da interface.
- Possíveis retornos:
    - `frame`: valor calculado pela função.
- TADs envolvidos: Widgets Tk/CustomTkinter.

#### `criar_painel(container, titulo)`
- Visibilidade: pública.
- Objetivo: Cria um painel padronizado com borda, fundo e título de seção.
- Parâmetros:
    - `container`: widget pai onde componentes visuais serao criados.
    - `titulo`: título exibido em painel.
- Possíveis retornos:
    - `frame`: valor calculado pela função.
- TADs envolvidos: Widgets Tk/CustomTkinter.

#### `criar_label(container, texto)`
- Visibilidade: pública.
- Objetivo: Cria um label auxiliar com cor e fonte padrão da interface.
- Parâmetros:
    - `container`: widget pai onde componentes visuais serao criados.
    - `texto`: texto digitado pelo usuário.
- Possíveis retornos:
    - `ctk.CTkLabel(container, text=texto, text_color=COR_TEXTO_FRACO, font=FONTE_PADRAO)`: retorno delegado para outra função.
- TADs envolvidos: Widgets Tk/CustomTkinter.

#### `criar_entry(container, largura=None)`
- Visibilidade: pública.
- Objetivo: Cria um campo de texto consistente para formulários da interface.
- Parâmetros:
    - `container`: widget pai onde componentes visuais serao criados.
    - `largura`: largura opcional do widget.
- Possíveis retornos:
    - `ctk.CTkEntry(container, width=largura or 140, height=34, fg_color=COR_CAMPO, border_color=COR_BORDA, text_color=COR_TEXTO, corner_radius=6, font=FONTE_PADRAO)`: retorno delegado para outra função.
- TADs envolvidos: Widgets Tk/CustomTkinter.

#### `criar_botao(container, texto, comando, cor=COR_PAINEL_2, texto_cor=COR_TEXTO, largura=None)`
- Visibilidade: pública.
- Objetivo: Cria um botão padronizado com hover coerente com a cor base.
- Parâmetros:
    - `container`: widget pai onde componentes visuais serao criados.
    - `texto`: texto digitado pelo usuário.
    - `comando`: callback executado por botão.
    - `cor`: cor principal do widget.
    - `texto_cor`: cor do texto do widget.
    - `largura`: largura opcional do widget.
- Possíveis retornos:
    - `ctk.CTkButton(container, text=texto, command=comando, fg_color=cor, hover_color=hover, text_color=texto_cor, width=largura or 140, height=34, corner_radius=6, font=FONTE_SELECAO)`: retorno delegado para outra função.
- TADs envolvidos: Widgets Tk/CustomTkinter.

#### `adicionar_tooltip(widget, texto)`
- Visibilidade: pública.
- Objetivo: Adiciona um tooltip simples controlado por eventos de mouse.
- Parâmetros:
    - `widget`: widget Tk/CustomTkinter.
    - `texto`: texto digitado pelo usuário.
- Possíveis retornos:
    - `widget`: valor calculado pela função.
    - `None`: ausência válida de dado ou falha sem objeto retornável.
- TADs envolvidos: Widgets Tk/CustomTkinter.

#### `criar_listbox(container, altura)`
- Visibilidade: pública.
- Objetivo: Cria uma listbox com cores e fonte alinhadas ao tema do app.
- Parâmetros:
    - `container`: widget pai onde componentes visuais serao criados.
    - `altura`: parâmetro usado pela função conforme o contexto do módulo.
- Possíveis retornos:
    - `tk.Listbox(container, height=altura, exportselection=False, bg=COR_CAMPO, fg=COR_TEXTO, selectbackground=COR_AZUL, selectforeground='#ffffff', relief='solid', bd=1, highlightthickness=1, highlightbackground=COR_BORDA, highlightcolor=COR_AZUL, font=FONTE_PADRAO)`: retorno delegado para outra função.
- TADs envolvidos: Widgets Tk/CustomTkinter.

#### `widgets_existem()`
- Visibilidade: pública.
- Objetivo: Indica se todos os widgets informados ainda existem no Tk.
- Parâmetros:
    - nenhum parâmetro.
- Possíveis retornos:
    - `all((widget is not None and widget.winfo_exists() for widget in widgets))`: retorno delegado para outra função.
    - `False`: condição rejeitada/falsa.
- TADs envolvidos: Widgets Tk/CustomTkinter.

#### `trazer_janela_para_frente(janela)`
- Visibilidade: pública.
- Objetivo: Traz a janela principal para frente ao iniciar sem fixa-la no topo.
- Parâmetros:
    - `janela`: janela Tk/CustomTkinter.
- Possíveis retornos:
    - `OK`: sucesso da operação.
- TADs envolvidos: Widgets Tk/CustomTkinter.

#### `manter_janela_acima_da_principal(janela_filha, janela_principal)`
- Visibilidade: pública.
- Objetivo: Mantem uma janela secundaria acima da principal até ela ser minimizada.
- Parâmetros:
    - `janela_filha`: janela secundaria Tk/CustomTkinter.
    - `janela_principal`: janela principal Tk/CustomTkinter.
- Possíveis retornos:
    - `OK`: sucesso da operação.
    - `None`: ausência válida de dado ou falha sem objeto retornável.
- TADs envolvidos: Widgets Tk/CustomTkinter.



## Testes

A suite usa pytest funcional, sem classes, structs ou unittest. Cada teste retorna `None` implicitamente quando passa e falha por `assert` quando o comportamento esperado não ocorre.

### `tests/assertions.py`

Escopo: Fornece helpers funcionais de asserção para pytest, sem classes.

#### `assert_equal(valor_obtido, valor_esperado, mensagem=None)`
- Visibilidade: pública.
- Objetivo: Falha se os dois valores comparados forem diferentes.
- Parâmetros:
    - `valor_obtido`: valor produzido pelo teste.
    - `valor_esperado`: valor esperado pelo teste.
    - `mensagem`: mensagem opcional de asserção em testes.
- Possíveis retornos:
    - retorno implícito `None`: função usada por asserção/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD específico; função utilitária ou teste.

#### `assert_not_equal(valor_obtido, valor_inesperado, mensagem=None)`
- Visibilidade: pública.
- Objetivo: Falha se os dois valores comparados forem iguais.
- Parâmetros:
    - `valor_obtido`: valor produzido pelo teste.
    - `valor_inesperado`: valor que não deve aparecer no teste.
    - `mensagem`: mensagem opcional de asserção em testes.
- Possíveis retornos:
    - retorno implícito `None`: função usada por asserção/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD específico; função utilitária ou teste.

#### `assert_true(valor, mensagem=None)`
- Visibilidade: pública.
- Objetivo: Falha se o valor recebido não for verdadeiro.
- Parâmetros:
    - `valor`: valor recebido, validado ou escrito em widget/TAD.
    - `mensagem`: mensagem opcional de asserção em testes.
- Possíveis retornos:
    - retorno implícito `None`: função usada por asserção/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD específico; função utilitária ou teste.

#### `assert_false(valor, mensagem=None)`
- Visibilidade: pública.
- Objetivo: Falha se o valor recebido não for falso.
- Parâmetros:
    - `valor`: valor recebido, validado ou escrito em widget/TAD.
    - `mensagem`: mensagem opcional de asserção em testes.
- Possíveis retornos:
    - retorno implícito `None`: função usada por asserção/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD específico; função utilitária ou teste.

#### `assert_is_none(valor, mensagem=None)`
- Visibilidade: pública.
- Objetivo: Falha se o valor recebido não for None.
- Parâmetros:
    - `valor`: valor recebido, validado ou escrito em widget/TAD.
    - `mensagem`: mensagem opcional de asserção em testes.
- Possíveis retornos:
    - retorno implícito `None`: função usada por asserção/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD específico; função utilitária ou teste.

#### `assert_is_not_none(valor, mensagem=None)`
- Visibilidade: pública.
- Objetivo: Falha se o valor recebido for None.
- Parâmetros:
    - `valor`: valor recebido, validado ou escrito em widget/TAD.
    - `mensagem`: mensagem opcional de asserção em testes.
- Possíveis retornos:
    - retorno implícito `None`: função usada por asserção/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD específico; função utilitária ou teste.

#### `assert_is_instance(valor, tipo_esperado, mensagem=None)`
- Visibilidade: pública.
- Objetivo: Falha se o valor recebido não for instancia do tipo esperado.
- Parâmetros:
    - `valor`: valor recebido, validado ou escrito em widget/TAD.
    - `tipo_esperado`: tipo Python esperado em asserção.
    - `mensagem`: mensagem opcional de asserção em testes.
- Possíveis retornos:
    - retorno implícito `None`: função usada por asserção/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD específico; função utilitária ou teste.

#### `assert_in(valor, colecao, mensagem=None)`
- Visibilidade: pública.
- Objetivo: Falha se o valor recebido não existir na coleção.
- Parâmetros:
    - `valor`: valor recebido, validado ou escrito em widget/TAD.
    - `colecao`: coleção usada em asserção de presença.
    - `mensagem`: mensagem opcional de asserção em testes.
- Possíveis retornos:
    - retorno implícito `None`: função usada por asserção/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD específico; função utilitária ou teste.

#### `assert_not_in(valor, colecao, mensagem=None)`
- Visibilidade: pública.
- Objetivo: Falha se o valor recebido existir na coleção.
- Parâmetros:
    - `valor`: valor recebido, validado ou escrito em widget/TAD.
    - `colecao`: coleção usada em asserção de presença.
    - `mensagem`: mensagem opcional de asserção em testes.
- Possíveis retornos:
    - retorno implícito `None`: função usada por asserção/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD específico; função utilitária ou teste.

### `tests/test_backup_engine.py`

Escopo: Cobre fluxo de backup, cópia/movimento/recorte, filtros por tipo, origem/tipo inativos e validações integradas.

#### `test_montar_resultado_backup()`
- Visibilidade: pública.
- Objetivo: Sem docstring.
- Parâmetros:
    - nenhum parâmetro.
- Possíveis retornos:
    - retorno implícito `None`: função usada por asserção/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD específico; função utilitária ou teste.

#### `test_executar_backup_base_sem_arquivos()`
- Visibilidade: pública.
- Objetivo: Sem docstring.
- Parâmetros:
    - nenhum parâmetro.
- Possíveis retornos:
    - retorno implícito `None`: função usada por asserção/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD específico; função utilitária ou teste.

#### `test_validar_perfil_para_backup_valido()`
- Visibilidade: pública.
- Objetivo: Sem docstring.
- Parâmetros:
    - nenhum parâmetro.
- Possíveis retornos:
    - retorno implícito `None`: função usada por asserção/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD específico; função utilitária ou teste.

#### `test_validar_perfil_para_backup_rejeita_dados_invalidos()`
- Visibilidade: pública.
- Objetivo: Sem docstring.
- Parâmetros:
    - nenhum parâmetro.
- Possíveis retornos:
    - retorno implícito `None`: função usada por asserção/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD específico; função utilitária ou teste.

#### `test_validar_perfil_para_backup_rejeita_sem_origem()`
- Visibilidade: pública.
- Objetivo: Sem docstring.
- Parâmetros:
    - nenhum parâmetro.
- Possíveis retornos:
    - retorno implícito `None`: função usada por asserção/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD específico; função utilitária ou teste.

#### `test_validar_perfil_para_backup_rejeita_sem_destino()`
- Visibilidade: pública.
- Objetivo: Sem docstring.
- Parâmetros:
    - nenhum parâmetro.
- Possíveis retornos:
    - retorno implícito `None`: função usada por asserção/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD específico; função utilitária ou teste.

#### `test_validar_perfil_para_backup_rejeita_operacao_invalida()`
- Visibilidade: pública.
- Objetivo: Sem docstring.
- Parâmetros:
    - nenhum parâmetro.
- Possíveis retornos:
    - retorno implícito `None`: função usada por asserção/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD específico; função utilitária ou teste.

#### `test_executar_backup_retorna_erro_de_validacao()`
- Visibilidade: pública.
- Objetivo: Sem docstring.
- Parâmetros:
    - nenhum parâmetro.
- Possíveis retornos:
    - retorno implícito `None`: função usada por asserção/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD específico; função utilitária ou teste.

#### `test_gerar_caminho_destino_com_nome()`
- Visibilidade: pública.
- Objetivo: Sem docstring.
- Parâmetros:
    - nenhum parâmetro.
- Possíveis retornos:
    - retorno implícito `None`: função usada por asserção/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD específico; função utilitária ou teste.

#### `test_gerar_caminho_destino_com_caminho_sem_nome()`
- Visibilidade: pública.
- Objetivo: Sem docstring.
- Parâmetros:
    - nenhum parâmetro.
- Possíveis retornos:
    - retorno implícito `None`: função usada por asserção/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD específico; função utilitária ou teste.

#### `test_gerar_caminho_destino_rejeita_dados_invalidos()`
- Visibilidade: pública.
- Objetivo: Sem docstring.
- Parâmetros:
    - nenhum parâmetro.
- Possíveis retornos:
    - retorno implícito `None`: função usada por asserção/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD específico; função utilitária ou teste.

#### `test_criar_pasta_destino_se_necessario_cria_diretorio()`
- Visibilidade: pública.
- Objetivo: Sem docstring.
- Parâmetros:
    - nenhum parâmetro.
- Possíveis retornos:
    - retorno implícito `None`: função usada por asserção/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD específico; função utilitária ou teste.

#### `test_criar_pasta_destino_se_necessario_aceita_diretorio_existente()`
- Visibilidade: pública.
- Objetivo: Sem docstring.
- Parâmetros:
    - nenhum parâmetro.
- Possíveis retornos:
    - retorno implícito `None`: função usada por asserção/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD específico; função utilitária ou teste.

#### `test_criar_pasta_destino_se_necessario_rejeita_caminho_invalido()`
- Visibilidade: pública.
- Objetivo: Sem docstring.
- Parâmetros:
    - nenhum parâmetro.
- Possíveis retornos:
    - retorno implícito `None`: função usada por asserção/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD específico; função utilitária ou teste.

#### `test_copiar_arquivo_copia_conteudo_e_mantem_original()`
- Visibilidade: pública.
- Objetivo: Sem docstring.
- Parâmetros:
    - nenhum parâmetro.
- Possíveis retornos:
    - retorno implícito `None`: função usada por asserção/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD específico; função utilitária ou teste.

#### `test_copiar_arquivo_retorna_erro_sem_quebrar()`
- Visibilidade: pública.
- Objetivo: Sem docstring.
- Parâmetros:
    - nenhum parâmetro.
- Possíveis retornos:
    - retorno implícito `None`: função usada por asserção/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD específico; função utilitária ou teste.

#### `test_copiar_arquivo_rejeita_dados_invalidos()`
- Visibilidade: pública.
- Objetivo: Sem docstring.
- Parâmetros:
    - nenhum parâmetro.
- Possíveis retornos:
    - retorno implícito `None`: função usada por asserção/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD específico; função utilitária ou teste.

#### `test_mover_arquivo_move_conteudo_e_remove_original()`
- Visibilidade: pública.
- Objetivo: Sem docstring.
- Parâmetros:
    - nenhum parâmetro.
- Possíveis retornos:
    - retorno implícito `None`: função usada por asserção/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD específico; função utilitária ou teste.

#### `test_mover_arquivo_retorna_erro_sem_quebrar()`
- Visibilidade: pública.
- Objetivo: Sem docstring.
- Parâmetros:
    - nenhum parâmetro.
- Possíveis retornos:
    - retorno implícito `None`: função usada por asserção/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD específico; função utilitária ou teste.

#### `test_mover_arquivo_rejeita_dados_invalidos()`
- Visibilidade: pública.
- Objetivo: Sem docstring.
- Parâmetros:
    - nenhum parâmetro.
- Possíveis retornos:
    - retorno implícito `None`: função usada por asserção/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD específico; função utilitária ou teste.

#### `test_executar_backup_retorna_sem_arquivos_quando_filtro_rejeita_todos()`
- Visibilidade: pública.
- Objetivo: Sem docstring.
- Parâmetros:
    - nenhum parâmetro.
- Possíveis retornos:
    - retorno implícito `None`: função usada por asserção/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD específico; função utilitária ou teste.

#### `test_executar_backup_configurado_envia_tipos_para_destinos_distintos()`
- Visibilidade: pública.
- Objetivo: Sem docstring.
- Parâmetros:
    - nenhum parâmetro.
- Possíveis retornos:
    - retorno implícito `None`: função usada por asserção/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD específico; função utilitária ou teste.

#### `test_executar_backup_configurado_ignora_arquivos_em_subpastas_da_origem()`
- Visibilidade: pública.
- Objetivo: Sem docstring.
- Parâmetros:
    - nenhum parâmetro.
- Possíveis retornos:
    - retorno implícito `None`: função usada por asserção/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD específico; função utilitária ou teste.

#### `test_executar_backup_configurado_recorta_para_destino_unico()`
- Visibilidade: pública.
- Objetivo: Sem docstring.
- Parâmetros:
    - nenhum parâmetro.
- Possíveis retornos:
    - retorno implícito `None`: função usada por asserção/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD específico; função utilitária ou teste.

#### `test_validar_perfil_configurado_rejeita_mover_para_multiplos_destinos()`
- Visibilidade: pública.
- Objetivo: Sem docstring.
- Parâmetros:
    - nenhum parâmetro.
- Possíveis retornos:
    - retorno implícito `None`: função usada por asserção/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD específico; função utilitária ou teste.

#### `test_executar_backup_configurado_ignora_origem_inativa()`
- Visibilidade: pública.
- Objetivo: Sem docstring.
- Parâmetros:
    - nenhum parâmetro.
- Possíveis retornos:
    - retorno implícito `None`: função usada por asserção/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD específico; função utilitária ou teste.

#### `test_executar_backup_configurado_ignora_tipo_inativo()`
- Visibilidade: pública.
- Objetivo: Sem docstring.
- Parâmetros:
    - nenhum parâmetro.
- Possíveis retornos:
    - retorno implícito `None`: função usada por asserção/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD específico; função utilitária ou teste.

#### `test_validar_perfil_configurado_ignora_conflito_de_tipo_inativo()`
- Visibilidade: pública.
- Objetivo: Sem docstring.
- Parâmetros:
    - nenhum parâmetro.
- Possíveis retornos:
    - retorno implícito `None`: função usada por asserção/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD específico; função utilitária ou teste.

### `tests/test_backup_result.py`

Escopo: Cobre montagem e acumulação dos TADs de resultado.

#### `test_montar_resultado_backup_cria_contadores_zerados()`
- Visibilidade: pública.
- Objetivo: Sem docstring.
- Parâmetros:
    - nenhum parâmetro.
- Possíveis retornos:
    - retorno implícito `None`: função usada por asserção/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD específico; função utilitária ou teste.

#### `test_aplicar_resultado_arquivo_acumula_contadores_e_listas()`
- Visibilidade: pública.
- Objetivo: Sem docstring.
- Parâmetros:
    - nenhum parâmetro.
- Possíveis retornos:
    - retorno implícito `None`: função usada por asserção/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD específico; função utilitária ou teste.

#### `test_montar_registro_arquivo_preserva_metadados()`
- Visibilidade: pública.
- Objetivo: Sem docstring.
- Parâmetros:
    - nenhum parâmetro.
- Possíveis retornos:
    - retorno implícito `None`: função usada por asserção/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD específico; função utilitária ou teste.

#### `test_montar_erro_arquivo()`
- Visibilidade: pública.
- Objetivo: Sem docstring.
- Parâmetros:
    - nenhum parâmetro.
- Possíveis retornos:
    - retorno implícito `None`: função usada por asserção/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD específico; função utilitária ou teste.

### `tests/test_backup_validation.py`

Escopo: Cobre validação estrutural de perfil, origem, destino e operação.

#### `test_validar_perfil_rejeita_formato_antigo()`
- Visibilidade: pública.
- Objetivo: Sem docstring.
- Parâmetros:
    - nenhum parâmetro.
- Possíveis retornos:
    - retorno implícito `None`: função usada por asserção/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD específico; função utilitária ou teste.

#### `test_validar_perfil_rejeita_dados_invalidos()`
- Visibilidade: pública.
- Objetivo: Sem docstring.
- Parâmetros:
    - nenhum parâmetro.
- Possíveis retornos:
    - retorno implícito `None`: função usada por asserção/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD específico; função utilitária ou teste.

#### `test_validar_perfil_configurado_valido()`
- Visibilidade: pública.
- Objetivo: Sem docstring.
- Parâmetros:
    - nenhum parâmetro.
- Possíveis retornos:
    - retorno implícito `None`: função usada por asserção/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD específico; função utilitária ou teste.

#### `test_validar_perfil_configurado_rejeita_sem_origem()`
- Visibilidade: pública.
- Objetivo: Sem docstring.
- Parâmetros:
    - nenhum parâmetro.
- Possíveis retornos:
    - retorno implícito `None`: função usada por asserção/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD específico; função utilitária ou teste.

#### `test_validar_destinos_do_tipo_rejeita_destino_invalido()`
- Visibilidade: pública.
- Objetivo: Sem docstring.
- Parâmetros:
    - nenhum parâmetro.
- Possíveis retornos:
    - retorno implícito `None`: função usada por asserção/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD específico; função utilitária ou teste.

#### `test_validar_destinos_do_tipo_rejeita_operacao_invalida()`
- Visibilidade: pública.
- Objetivo: Sem docstring.
- Parâmetros:
    - nenhum parâmetro.
- Possíveis retornos:
    - retorno implícito `None`: função usada por asserção/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD específico; função utilitária ou teste.

#### `test_validar_destinos_do_tipo_rejeita_mover_com_multiplos_destinos()`
- Visibilidade: pública.
- Objetivo: Sem docstring.
- Parâmetros:
    - nenhum parâmetro.
- Possíveis retornos:
    - retorno implícito `None`: função usada por asserção/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD específico; função utilitária ou teste.

### `tests/test_controller.py`

Escopo: Cobre estado em memória, persistência diferida, configurações, pré-visualização e bloqueio de perfil inativo.

#### `resetar_estado()`
- Visibilidade: pública.
- Objetivo: Reinicia o estado global usado pelo controller nos testes.
- Parâmetros:
    - nenhum parâmetro.
- Possíveis retornos:
    - retorno implícito `None`: função usada por asserção/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD específico; função utilitária ou teste.

#### `criar_gravador(retorno=None)`
- Visibilidade: pública.
- Objetivo: Cria uma função fake que registra chamadas e devolve um retorno fixo.
- Parâmetros:
    - `retorno`: valor fixo devolvido por função fake de teste.
- Possíveis retornos:
    - `(gravador, chamadas)`: tupla de retorno; normalmente combina código e dado/resultado.
    - `retorno`: valor calculado pela função.
- TADs envolvidos: nenhum TAD específico; função utilitária ou teste.

#### `resetar_controller_antes_de_cada_teste()`
- Visibilidade: pública.
- Objetivo: Garante que cada teste comece com o controller em memória limpa.
- Parâmetros:
    - nenhum parâmetro.
- Possíveis retornos:
    - retorno implícito `None`: função usada por asserção/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD específico; função utilitária ou teste.

#### `test_criar_perfil_altera_apenas_memoria()`
- Visibilidade: pública.
- Objetivo: Sem docstring.
- Parâmetros:
    - nenhum parâmetro.
- Possíveis retornos:
    - retorno implícito `None`: função usada por asserção/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD específico; função utilitária ou teste.

#### `test_criar_perfil_nao_salva_json_imediatamente(monkeypatch)`
- Visibilidade: pública.
- Objetivo: Sem docstring.
- Parâmetros:
    - `monkeypatch`: fixture pytest para substituir funções/atributos durante o teste.
- Possíveis retornos:
    - retorno implícito `None`: função usada por asserção/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD específico; função utilitária ou teste.

#### `test_finalizar_aplicacao_salva_json_quando_estado_foi_alterado(monkeypatch)`
- Visibilidade: pública.
- Objetivo: Sem docstring.
- Parâmetros:
    - `monkeypatch`: fixture pytest para substituir funções/atributos durante o teste.
- Possíveis retornos:
    - retorno implícito `None`: função usada por asserção/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD específico; função utilitária ou teste.

#### `test_finalizar_aplicacao_sem_alteracao_nao_salva_json(monkeypatch)`
- Visibilidade: pública.
- Objetivo: Sem docstring.
- Parâmetros:
    - `monkeypatch`: fixture pytest para substituir funções/atributos durante o teste.
- Possíveis retornos:
    - retorno implícito `None`: função usada por asserção/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD específico; função utilitária ou teste.

#### `test_inicializar_aplicacao_carrega_estado_em_memoria(monkeypatch)`
- Visibilidade: pública.
- Objetivo: Sem docstring.
- Parâmetros:
    - `monkeypatch`: fixture pytest para substituir funções/atributos durante o teste.
- Possíveis retornos:
    - retorno implícito `None`: função usada por asserção/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD específico; função utilitária ou teste.

#### `test_executar_backup_nao_altera_estado_quando_falha_validacao()`
- Visibilidade: pública.
- Objetivo: Sem docstring.
- Parâmetros:
    - nenhum parâmetro.
- Possíveis retornos:
    - retorno implícito `None`: função usada por asserção/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD específico; função utilitária ou teste.

#### `test_salvar_perfil_editado_aplica_dados_em_memoria(monkeypatch)`
- Visibilidade: pública.
- Objetivo: Sem docstring.
- Parâmetros:
    - `monkeypatch`: fixture pytest para substituir funções/atributos durante o teste.
- Possíveis retornos:
    - retorno implícito `None`: função usada por asserção/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD específico; função utilitária ou teste.

#### `test_salvar_perfil_editado_aplica_origens_configuradas()`
- Visibilidade: pública.
- Objetivo: Sem docstring.
- Parâmetros:
    - nenhum parâmetro.
- Possíveis retornos:
    - retorno implícito `None`: função usada por asserção/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD específico; função utilitária ou teste.

#### `test_salvar_perfil_editado_rejeita_dados_invalidos()`
- Visibilidade: pública.
- Objetivo: Sem docstring.
- Parâmetros:
    - nenhum parâmetro.
- Possíveis retornos:
    - retorno implícito `None`: função usada por asserção/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD específico; função utilitária ou teste.

#### `test_ativar_e_desativar_perfil_alteram_memoria()`
- Visibilidade: pública.
- Objetivo: Sem docstring.
- Parâmetros:
    - nenhum parâmetro.
- Possíveis retornos:
    - retorno implícito `None`: função usada por asserção/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD específico; função utilitária ou teste.

#### `test_obter_arquivos_do_perfil_lista_arquivos_com_status_incluido()`
- Visibilidade: pública.
- Objetivo: Sem docstring.
- Parâmetros:
    - nenhum parâmetro.
- Possíveis retornos:
    - retorno implícito `None`: função usada por asserção/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD específico; função utilitária ou teste.

#### `test_obter_arquivos_do_perfil_inexistente()`
- Visibilidade: pública.
- Objetivo: Sem docstring.
- Parâmetros:
    - nenhum parâmetro.
- Possíveis retornos:
    - retorno implícito `None`: função usada por asserção/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD específico; função utilitária ou teste.

#### `test_obter_arquivos_do_perfil_configurado_lista_tipos_incluidos()`
- Visibilidade: pública.
- Objetivo: Sem docstring.
- Parâmetros:
    - nenhum parâmetro.
- Possíveis retornos:
    - retorno implícito `None`: função usada por asserção/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD específico; função utilitária ou teste.

#### `test_executar_backup_bloqueia_perfil_inativo()`
- Visibilidade: pública.
- Objetivo: Sem docstring.
- Parâmetros:
    - nenhum parâmetro.
- Possíveis retornos:
    - retorno implícito `None`: função usada por asserção/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD específico; função utilitária ou teste.

#### `test_configuracoes_gerais_alteram_apenas_memoria()`
- Visibilidade: pública.
- Objetivo: Sem docstring.
- Parâmetros:
    - nenhum parâmetro.
- Possíveis retornos:
    - retorno implícito `None`: função usada por asserção/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD específico; função utilitária ou teste.

#### `test_salvar_configuracoes_rejeita_dados_invalidos()`
- Visibilidade: pública.
- Objetivo: Sem docstring.
- Parâmetros:
    - nenhum parâmetro.
- Possíveis retornos:
    - retorno implícito `None`: função usada por asserção/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD específico; função utilitária ou teste.

#### `test_obter_extensoes_disponiveis_une_padrao_e_config()`
- Visibilidade: pública.
- Objetivo: Sem docstring.
- Parâmetros:
    - nenhum parâmetro.
- Possíveis retornos:
    - retorno implícito `None`: função usada por asserção/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD específico; função utilitária ou teste.

#### `test_adicionar_extensao_disponivel_normaliza_e_altera_memoria()`
- Visibilidade: pública.
- Objetivo: Sem docstring.
- Parâmetros:
    - nenhum parâmetro.
- Possíveis retornos:
    - retorno implícito `None`: função usada por asserção/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD específico; função utilitária ou teste.

#### `test_adicionar_extensao_disponivel_rejeita_invalida()`
- Visibilidade: pública.
- Objetivo: Sem docstring.
- Parâmetros:
    - nenhum parâmetro.
- Possíveis retornos:
    - retorno implícito `None`: função usada por asserção/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD específico; função utilitária ou teste.

### `tests/test_file_utils.py`

Escopo: Cobre caminhos, permissões, metadados e filtros de arquivo/restrições.

#### `test_caminho_existe_para_arquivo_e_diretorio()`
- Visibilidade: pública.
- Objetivo: Sem docstring.
- Parâmetros:
    - nenhum parâmetro.
- Possíveis retornos:
    - retorno implícito `None`: função usada por asserção/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD específico; função utilitária ou teste.

#### `test_caminho_existe_retorna_false_para_invalido()`
- Visibilidade: pública.
- Objetivo: Sem docstring.
- Parâmetros:
    - nenhum parâmetro.
- Possíveis retornos:
    - retorno implícito `None`: função usada por asserção/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD específico; função utilitária ou teste.

#### `test_caminho_e_diretorio()`
- Visibilidade: pública.
- Objetivo: Sem docstring.
- Parâmetros:
    - nenhum parâmetro.
- Possíveis retornos:
    - retorno implícito `None`: função usada por asserção/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD específico; função utilitária ou teste.

#### `test_verificar_permissao_leitura()`
- Visibilidade: pública.
- Objetivo: Sem docstring.
- Parâmetros:
    - nenhum parâmetro.
- Possíveis retornos:
    - retorno implícito `None`: função usada por asserção/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD específico; função utilitária ou teste.

#### `test_verificar_permissao_escrita()`
- Visibilidade: pública.
- Objetivo: Sem docstring.
- Parâmetros:
    - nenhum parâmetro.
- Possíveis retornos:
    - retorno implícito `None`: função usada por asserção/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD específico; função utilitária ou teste.

#### `test_listar_arquivos_em_origem_ignora_subpastas()`
- Visibilidade: pública.
- Objetivo: Sem docstring.
- Parâmetros:
    - nenhum parâmetro.
- Possíveis retornos:
    - retorno implícito `None`: função usada por asserção/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD específico; função utilitária ou teste.

#### `test_listar_arquivos_em_origem_invalida()`
- Visibilidade: pública.
- Objetivo: Sem docstring.
- Parâmetros:
    - nenhum parâmetro.
- Possíveis retornos:
    - retorno implícito `None`: função usada por asserção/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD específico; função utilitária ou teste.

#### `test_listar_arquivos_de_origens()`
- Visibilidade: pública.
- Objetivo: Sem docstring.
- Parâmetros:
    - nenhum parâmetro.
- Possíveis retornos:
    - retorno implícito `None`: função usada por asserção/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD específico; função utilitária ou teste.

#### `test_listar_arquivos_de_origens_rejeita_tipo_invalido()`
- Visibilidade: pública.
- Objetivo: Sem docstring.
- Parâmetros:
    - nenhum parâmetro.
- Possíveis retornos:
    - retorno implícito `None`: função usada por asserção/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD específico; função utilitária ou teste.

#### `test_obter_extensao()`
- Visibilidade: pública.
- Objetivo: Sem docstring.
- Parâmetros:
    - nenhum parâmetro.
- Possíveis retornos:
    - retorno implícito `None`: função usada por asserção/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD específico; função utilitária ou teste.

#### `test_obter_metadados_arquivo()`
- Visibilidade: pública.
- Objetivo: Sem docstring.
- Parâmetros:
    - nenhum parâmetro.
- Possíveis retornos:
    - retorno implícito `None`: função usada por asserção/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD específico; função utilitária ou teste.

#### `test_obter_metadados_arquivo_invalido()`
- Visibilidade: pública.
- Objetivo: Sem docstring.
- Parâmetros:
    - nenhum parâmetro.
- Possíveis retornos:
    - retorno implícito `None`: função usada por asserção/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD específico; função utilitária ou teste.

#### `test_filtrar_por_extensao()`
- Visibilidade: pública.
- Objetivo: Sem docstring.
- Parâmetros:
    - nenhum parâmetro.
- Possíveis retornos:
    - retorno implícito `None`: função usada por asserção/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD específico; função utilitária ou teste.

#### `test_filtrar_por_extensao_aceita_lista_vazia()`
- Visibilidade: pública.
- Objetivo: Sem docstring.
- Parâmetros:
    - nenhum parâmetro.
- Possíveis retornos:
    - retorno implícito `None`: função usada por asserção/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD específico; função utilitária ou teste.

#### `test_filtrar_por_extensao_normaliza_ponto_e_maiusculas()`
- Visibilidade: pública.
- Objetivo: Sem docstring.
- Parâmetros:
    - nenhum parâmetro.
- Possíveis retornos:
    - retorno implícito `None`: função usada por asserção/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD específico; função utilitária ou teste.

#### `test_filtrar_por_extensao_rejeita_extensao_nao_permitida()`
- Visibilidade: pública.
- Objetivo: Sem docstring.
- Parâmetros:
    - nenhum parâmetro.
- Possíveis retornos:
    - retorno implícito `None`: função usada por asserção/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD específico; função utilitária ou teste.

#### `test_filtrar_por_nome()`
- Visibilidade: pública.
- Objetivo: Sem docstring.
- Parâmetros:
    - nenhum parâmetro.
- Possíveis retornos:
    - retorno implícito `None`: função usada por asserção/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD específico; função utilitária ou teste.

#### `test_filtrar_por_nome_aceita_sem_regras()`
- Visibilidade: pública.
- Objetivo: Sem docstring.
- Parâmetros:
    - nenhum parâmetro.
- Possíveis retornos:
    - retorno implícito `None`: função usada por asserção/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD específico; função utilitária ou teste.

#### `test_filtrar_por_nome_ignora_maiusculas()`
- Visibilidade: pública.
- Objetivo: Sem docstring.
- Parâmetros:
    - nenhum parâmetro.
- Possíveis retornos:
    - retorno implícito `None`: função usada por asserção/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD específico; função utilitária ou teste.

#### `test_filtrar_por_nome_rejeita_trecho_ausente()`
- Visibilidade: pública.
- Objetivo: Sem docstring.
- Parâmetros:
    - nenhum parâmetro.
- Possíveis retornos:
    - retorno implícito `None`: função usada por asserção/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD específico; função utilitária ou teste.

#### `test_filtrar_por_regras_nome_contem()`
- Visibilidade: pública.
- Objetivo: Sem docstring.
- Parâmetros:
    - nenhum parâmetro.
- Possíveis retornos:
    - retorno implícito `None`: função usada por asserção/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD específico; função utilitária ou teste.

#### `test_filtrar_por_regras_nome_exato()`
- Visibilidade: pública.
- Objetivo: Sem docstring.
- Parâmetros:
    - nenhum parâmetro.
- Possíveis retornos:
    - retorno implícito `None`: função usada por asserção/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD específico; função utilitária ou teste.

#### `test_filtrar_por_regras_nome_exato_aceita_nome_sem_extensao()`
- Visibilidade: pública.
- Objetivo: Garante que o modo nome completo aceite o nome base do arquivo sem extensão.
- Parâmetros:
    - nenhum parâmetro.
- Possíveis retornos:
    - retorno implícito `None`: função usada por asserção/callback ou efeito colateral.
- TADs envolvidos: Restrições, Metadados de arquivo.

#### `test_filtrar_por_regras_nome_exato_rejeita_nome_parcial()`
- Visibilidade: pública.
- Objetivo: Sem docstring.
- Parâmetros:
    - nenhum parâmetro.
- Possíveis retornos:
    - retorno implícito `None`: função usada por asserção/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD específico; função utilitária ou teste.

#### `test_filtrar_por_regras_nome_usa_qualquer_regra()`
- Visibilidade: pública.
- Objetivo: Sem docstring.
- Parâmetros:
    - nenhum parâmetro.
- Possíveis retornos:
    - retorno implícito `None`: função usada por asserção/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD específico; função utilitária ou teste.

#### `test_filtrar_por_tamanho_minimo()`
- Visibilidade: pública.
- Objetivo: Sem docstring.
- Parâmetros:
    - nenhum parâmetro.
- Possíveis retornos:
    - retorno implícito `None`: função usada por asserção/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD específico; função utilitária ou teste.

#### `test_filtrar_por_tamanho_maximo()`
- Visibilidade: pública.
- Objetivo: Sem docstring.
- Parâmetros:
    - nenhum parâmetro.
- Possíveis retornos:
    - retorno implícito `None`: função usada por asserção/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD específico; função utilitária ou teste.

#### `test_filtrar_por_tamanho_rejeita_menor_que_minimo()`
- Visibilidade: pública.
- Objetivo: Sem docstring.
- Parâmetros:
    - nenhum parâmetro.
- Possíveis retornos:
    - retorno implícito `None`: função usada por asserção/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD específico; função utilitária ou teste.

#### `test_filtrar_por_tamanho_rejeita_maior_que_maximo()`
- Visibilidade: pública.
- Objetivo: Sem docstring.
- Parâmetros:
    - nenhum parâmetro.
- Possíveis retornos:
    - retorno implícito `None`: função usada por asserção/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD específico; função utilitária ou teste.

#### `test_filtrar_por_data_sem_limites()`
- Visibilidade: pública.
- Objetivo: Sem docstring.
- Parâmetros:
    - nenhum parâmetro.
- Possíveis retornos:
    - retorno implícito `None`: função usada por asserção/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD específico; função utilitária ou teste.

#### `test_filtrar_por_data_minima_e_maxima()`
- Visibilidade: pública.
- Objetivo: Sem docstring.
- Parâmetros:
    - nenhum parâmetro.
- Possíveis retornos:
    - retorno implícito `None`: função usada por asserção/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD específico; função utilitária ou teste.

#### `test_filtrar_por_data_rejeita_antes_da_minima()`
- Visibilidade: pública.
- Objetivo: Sem docstring.
- Parâmetros:
    - nenhum parâmetro.
- Possíveis retornos:
    - retorno implícito `None`: função usada por asserção/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD específico; função utilitária ou teste.

#### `test_filtrar_por_data_rejeita_depois_da_maxima()`
- Visibilidade: pública.
- Objetivo: Sem docstring.
- Parâmetros:
    - nenhum parâmetro.
- Possíveis retornos:
    - retorno implícito `None`: função usada por asserção/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD específico; função utilitária ou teste.

#### `test_arquivo_atende_restricoes_combinadas()`
- Visibilidade: pública.
- Objetivo: Sem docstring.
- Parâmetros:
    - nenhum parâmetro.
- Possíveis retornos:
    - retorno implícito `None`: função usada por asserção/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD específico; função utilitária ou teste.

#### `test_arquivo_atende_restricoes_rejeita_quando_um_filtro_falha()`
- Visibilidade: pública.
- Objetivo: Sem docstring.
- Parâmetros:
    - nenhum parâmetro.
- Possíveis retornos:
    - retorno implícito `None`: função usada por asserção/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD específico; função utilitária ou teste.

#### `test_arquivo_atende_restricoes_aceita_restricoes_vazias()`
- Visibilidade: pública.
- Objetivo: Sem docstring.
- Parâmetros:
    - nenhum parâmetro.
- Possíveis retornos:
    - retorno implícito `None`: função usada por asserção/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD específico; função utilitária ou teste.

#### `test_arquivo_atende_restricoes_rejeita_dados_invalidos()`
- Visibilidade: pública.
- Objetivo: Sem docstring.
- Parâmetros:
    - nenhum parâmetro.
- Possíveis retornos:
    - retorno implícito `None`: função usada por asserção/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD específico; função utilitária ou teste.

### `tests/test_new_modules_contract.py`

Escopo: Cobre contrato de API pública via __all__ nos módulos novos.

#### `test_modulos_novos_declararam_api_publica()`
- Visibilidade: pública.
- Objetivo: Sem docstring.
- Parâmetros:
    - nenhum parâmetro.
- Possíveis retornos:
    - retorno implícito `None`: função usada por asserção/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD específico; função utilitária ou teste.

### `tests/test_perfil_manager.py`

Escopo: Cobre criação e consulta dos TADs de perfil/origem/tipo/destino.

#### `test_criar_perfil_valido()`
- Visibilidade: pública.
- Objetivo: Sem docstring.
- Parâmetros:
    - nenhum parâmetro.
- Possíveis retornos:
    - retorno implícito `None`: função usada por asserção/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD específico; função utilitária ou teste.

#### `test_criar_perfil_nome_vazio()`
- Visibilidade: pública.
- Objetivo: Sem docstring.
- Parâmetros:
    - nenhum parâmetro.
- Possíveis retornos:
    - retorno implícito `None`: função usada por asserção/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD específico; função utilitária ou teste.

#### `test_consultar_perfil_existente()`
- Visibilidade: pública.
- Objetivo: Sem docstring.
- Parâmetros:
    - nenhum parâmetro.
- Possíveis retornos:
    - retorno implícito `None`: função usada por asserção/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD específico; função utilitária ou teste.

#### `test_consultar_perfil_inexistente()`
- Visibilidade: pública.
- Objetivo: Sem docstring.
- Parâmetros:
    - nenhum parâmetro.
- Possíveis retornos:
    - retorno implícito `None`: função usada por asserção/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD específico; função utilitária ou teste.

#### `test_criar_origem_tipo_e_destino_configurados()`
- Visibilidade: pública.
- Objetivo: Sem docstring.
- Parâmetros:
    - nenhum parâmetro.
- Possíveis retornos:
    - retorno implícito `None`: função usada por asserção/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD específico; função utilitária ou teste.

### `tests/test_storage.py`

Escopo: Cobre persistência JSON, arquivos padrão e erro de JSON corrompido/dados inválidos.

#### `test_salvar_e_carregar_json()`
- Visibilidade: pública.
- Objetivo: Sem docstring.
- Parâmetros:
    - nenhum parâmetro.
- Possíveis retornos:
    - retorno implícito `None`: função usada por asserção/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD específico; função utilitária ou teste.

#### `test_carregar_json_inexistente()`
- Visibilidade: pública.
- Objetivo: Sem docstring.
- Parâmetros:
    - nenhum parâmetro.
- Possíveis retornos:
    - retorno implícito `None`: função usada por asserção/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD específico; função utilitária ou teste.

#### `test_carregar_json_corrompido()`
- Visibilidade: pública.
- Objetivo: Sem docstring.
- Parâmetros:
    - nenhum parâmetro.
- Possíveis retornos:
    - retorno implícito `None`: função usada por asserção/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD específico; função utilitária ou teste.

#### `test_salvar_json_rejeita_dados_nao_serializaveis()`
- Visibilidade: pública.
- Objetivo: Sem docstring.
- Parâmetros:
    - nenhum parâmetro.
- Possíveis retornos:
    - retorno implícito `None`: função usada por asserção/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD específico; função utilitária ou teste.

#### `test_criar_arquivos_padrao()`
- Visibilidade: pública.
- Objetivo: Sem docstring.
- Parâmetros:
    - nenhum parâmetro.
- Possíveis retornos:
    - retorno implícito `None`: função usada por asserção/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD específico; função utilitária ou teste.

### `tests/test_ui_converters.py`

Escopo: Cobre conversores puros de formulário usados pela UI.

#### `test_converter_inteiro_opcional()`
- Visibilidade: pública.
- Objetivo: Sem docstring.
- Parâmetros:
    - nenhum parâmetro.
- Possíveis retornos:
    - retorno implícito `None`: função usada por asserção/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD específico; função utilitária ou teste.

#### `test_converter_data_opcional()`
- Visibilidade: pública.
- Objetivo: Sem docstring.
- Parâmetros:
    - nenhum parâmetro.
- Possíveis retornos:
    - retorno implícito `None`: função usada por asserção/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD específico; função utilitária ou teste.
