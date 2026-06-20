# Documentacao Final do BackupManager



## Visao Geral

BackupManager e uma aplicacao desktop local em Python/Tkinter para executar backups manuais por perfis. Cada perfil possui origens; cada origem possui tipos de arquivo; cada tipo possui restricoes e destinos; cada destino define sua operacao (`copiar`, `mover` ou `recortar`).



O projeto usa TADs representados por dicionarios persistidos em JSON, mas o acesso entre modulos deve ocorrer por funcoes publicas. A regra atual e: somente o modulo dono do TAD conhece suas chaves internas.



## Codigos de Retorno

Os codigos de retorno padronizados ficam em `backupmanager/return_codes.py`. Eles sao usados pelos modulos para comunicar sucesso, falhas de validacao e erros operacionais sem depender de texto solto. Para exibir uma mensagem legivel ao usuario, use `obter_mensagem(codigo)`.

- `OK = 0`: operacao realizada com sucesso.

- `ERRO_PERFIL_NAO_ENCONTRADO = 1`: perfil solicitado nao existe no estado atual.

- `ERRO_NOME_INVALIDO = 2`: nome de perfil ausente ou invalido.

- `ERRO_ORIGEM_INVALIDA = 3`: origem ausente, inativa, inexistente ou invalida para backup.

- `ERRO_DESTINO_INVALIDO = 4`: destino ausente, inexistente ou invalido para operacao.

- `ERRO_SEM_PERMISSAO = 5`: caminho existe, mas o app nao possui permissao suficiente para acessar.

- `ERRO_ARQUIVO_NAO_ENCONTRADO = 6`: arquivo esperado nao foi encontrado.

- `ERRO_RESTRICAO_INVALIDA = 7`: filtros/restricoes possuem valores invalidos.

- `ERRO_OPERACAO_INVALIDA = 8`: operacao nao reconhecida; atualmente as validas sao `copiar`, `mover` e `recortar`.

- `ERRO_FALHA_AO_COPIAR = 10`: falha durante copia de arquivo.

- `ERRO_FALHA_AO_MOVER = 11`: falha durante mover/recortar arquivo.

- `ERRO_JSON_CORROMPIDO = 12`: arquivo JSON persistido nao pode ser interpretado corretamente.

- `ERRO_BACKUP_SEM_ARQUIVOS = 13`: nenhum arquivo elegivel foi encontrado para backup.

- `ERRO_DESTINO_SEM_ESPACO = 14`: destino nao possui espaco disponivel suficiente.

- `ERRO_PERFIL_INATIVO = 15`: tentativa de executar backup em perfil inativo.

- `ERRO_DADOS_INVALIDOS = 16`: dados de entrada ou TAD em formato invalido.



## Comandos Basicos

- Abrir o app: `python -m backupmanager.main`

- Rodar testes: `python -m pytest -q`

- Validar sintaxe: `python -m compileall backupmanager tests`

- Instalar dependencias de desenvolvimento: `pip install -r requirements-dev.txt`



## Dados Persistidos

- `data/perfis.json`: perfis, origens, tipos, restricoes, destinos e estado ativo/inativo.

- `data/config.json`: configuracoes globais, principalmente extensoes customizadas disponiveis na UI.



## TADs Principais e Obrigacoes

- Perfil: identifica um conjunto de backup, guarda nome, estado ativo e origens configuradas. Dono: `domain/perfil_manager.py`.

- Origem configurada: guarda pasta de entrada, estado ativo e tipos de arquivo. Dono: `domain/perfil_manager.py`.

- Tipo de arquivo: agrupa nome, ativo/inativo, restricoes e destinos. Dono: `domain/perfil_manager.py`.

- Destino do tipo: guarda pasta de saida e operacao. Dono: `domain/perfil_manager.py`.

- Restricoes: filtros por extensao, nome, tamanho e data. Dono: `domain/perfil_manager.py`; aplicacao dos filtros em `engine/file_utils.py`.

- Metadados de arquivo: caminho, nome, extensao, tamanho e data de modificacao de um arquivo real. Dono: `engine/file_utils.py`.

- Resultado de backup: status, contadores, registros e erros. Dono: `domain/backup_result.py`.

- Estado da aplicacao: perfis/config em memoria e flag de alteracao. Dono: `controller.py`.

- Estado da interface: widgets, selecoes e edicoes em andamento. Dono: modulos em `ui/`.



## Fluxo Geral da Aplicacao

1. Entrada: `main.main()` chama `ui.interface.iniciar_interface()`.

2. Inicializacao: a UI chama `controller.inicializar_aplicacao()`, que pede a `infra/storage.py` para criar/carregar JSONs e popula o TAD Estado da aplicacao.

3. Edicao visual: `ui.profiles`, `ui.backup_flow` e `ui.restrictions` manipulam o TAD Estado da interface e criam/alteram Perfil, Origem, Tipo, Destino e Restricoes por funcoes de `perfil_manager`.

4. Aplicar/backup: `ui.actions.executar_backup_interface()` sincroniza o formulario com `controller.salvar_perfil_editado()` e chama `controller.executar_backup_do_perfil()`.

5. Validacao: `engine.backup_engine.executar_backup()` chama `domain.backup_validation.validar_perfil_para_backup()` usando acessores do TAD Perfil.

6. Selecao de arquivos: `backup_engine` pede arquivos a `engine.file_utils`, coleta metadados e aplica restricoes por tipo.

7. Operacao de disco: `backup_engine` copia/move/recorta cada arquivo para destinos configurados.

8. Resultado: `domain.backup_result` acumula contadores, registros e erros. A UI mostra o resumo final.

9. Fechamento: `controller.finalizar_aplicacao()` grava perfis/configuracoes se o estado foi alterado.



## Encapsulamento Atual

- Todos os modulos de aplicacao declaram `__all__`.

- Nao ha classes, dataclasses, structs, `NamedTuple`, `TypedDict` ou `unittest` em `backupmanager` ou `tests`.

- A auditoria textual nao encontrou acesso direto a `perfil.get`, `origem.get`, `tipo.get`, `destino.get`, `restricoes.get`, `resultado.get` ou `arquivo.get` fora dos modulos donos dos TADs.

- Excecao controlada: `estado_interface` e `_ESTADO` sao TADs locais administrados pelos proprios modulos da UI/controller.



## Pasta `backupmanager`

### Modulo `controller.py`

Resumo: Camada de controle entre interface e modulos internos.

TADs/obrigacoes do modulo: Estado da aplicacao (_ESTADO), Perfil, Configuracoes, Resultado de backup, Metadados de arquivo.

#### `_marcar_estado_alterado()`
- Visibilidade: interna.
- Objetivo: Marca que o estado em memoria possui alteracoes nao persistidas.
- Parametros:
    - nenhum parametro.
- Possiveis retornos:
    - `OK`: sucesso da operacao.
- TADs envolvidos: Estado da aplicacao (_ESTADO), Perfil, Configuracoes, Resultado de backup, Metadados de arquivo.

#### `inicializar_aplicacao()`
- Visibilidade: publica.
- Objetivo: Inicializa o estado em memoria da aplicacao.
- Parametros:
    - nenhum parametro.
- Possiveis retornos:
    - `OK`: sucesso da operacao.
    - `codigo_padrao`: codigo de retorno propagado de chamada interna.
    - `codigo_perfis`: codigo de retorno propagado de chamada interna.
    - `codigo_config`: codigo de retorno propagado de chamada interna.
- TADs envolvidos: Estado da aplicacao (_ESTADO), Perfil, Configuracoes, Resultado de backup, Metadados de arquivo.

#### `finalizar_aplicacao()`
- Visibilidade: publica.
- Objetivo: Persiste em JSON as alteracoes acumuladas em memoria.
- Parametros:
    - nenhum parametro.
- Possiveis retornos:
    - `OK`: sucesso da operacao.
    - `codigo`: codigo de retorno propagado de chamada interna.
- TADs envolvidos: Estado da aplicacao (_ESTADO), Perfil, Configuracoes, Resultado de backup, Metadados de arquivo.

#### `criar_novo_perfil(nome)`
- Visibilidade: publica.
- Objetivo: Cria um perfil novo e o registra no estado em memoria.
- Parametros:
    - `nome`: nome informado pelo usuario ou nome interno do TAD.
- Possiveis retornos:
    - `(OK, perfil)`: tupla de retorno; normalmente combina codigo e dado/resultado.
    - `(codigo, None)`: tupla de retorno; normalmente combina codigo e dado/resultado.
- TADs envolvidos: Estado da aplicacao (_ESTADO), Perfil, Configuracoes, Resultado de backup, Metadados de arquivo.

#### `obter_perfis()`
- Visibilidade: publica.
- Objetivo: Retorna todos os perfis mantidos em memoria.
- Parametros:
    - nenhum parametro.
- Possiveis retornos:
    - `perfil_manager.listar_perfis(_ESTADO['perfis'])`: retorno delegado para outra funcao.
- TADs envolvidos: Estado da aplicacao (_ESTADO), Perfil, Configuracoes, Resultado de backup, Metadados de arquivo.

#### `obter_perfil_por_id(perfil_id)`
- Visibilidade: publica.
- Objetivo: Consulta um perfil em memoria pelo identificador.
- Parametros:
    - `perfil_id`: identificador unico de um perfil.
- Possiveis retornos:
    - `perfil_manager.consultar_perfil(_ESTADO['perfis'], perfil_id)`: retorno delegado para outra funcao.
- TADs envolvidos: Estado da aplicacao (_ESTADO), Perfil, Configuracoes, Resultado de backup, Metadados de arquivo.

#### `salvar_perfil_editado(perfil)`
- Visibilidade: publica.
- Objetivo: Aplica ao estado em memoria os dados editados de um perfil.
- Parametros:
    - `perfil`: TAD Perfil, dicionario persistido com id, nome, ativo e origens configuradas.
- Possiveis retornos:
    - `OK`: sucesso da operacao.
    - `ERRO_DADOS_INVALIDOS`: entrada com tipo, formato ou valor invalido.
    - `codigo`: codigo de retorno propagado de chamada interna.
- TADs envolvidos: Estado da aplicacao (_ESTADO), Perfil, Configuracoes, Resultado de backup, Metadados de arquivo.

#### `excluir_perfil_por_id(perfil_id)`
- Visibilidade: publica.
- Objetivo: Remove um perfil do estado em memoria.
- Parametros:
    - `perfil_id`: identificador unico de um perfil.
- Possiveis retornos:
    - `codigo`: codigo de retorno propagado de chamada interna.
- TADs envolvidos: Estado da aplicacao (_ESTADO), Perfil, Configuracoes, Resultado de backup, Metadados de arquivo.

#### `ativar_perfil_por_id(perfil_id)`
- Visibilidade: publica.
- Objetivo: Ativa um perfil para permitir execucoes de backup.
- Parametros:
    - `perfil_id`: identificador unico de um perfil.
- Possiveis retornos:
    - `codigo`: codigo de retorno propagado de chamada interna.
- TADs envolvidos: Estado da aplicacao (_ESTADO), Perfil, Configuracoes, Resultado de backup, Metadados de arquivo.

#### `desativar_perfil_por_id(perfil_id)`
- Visibilidade: publica.
- Objetivo: Desativa um perfil para impedir execucoes de backup.
- Parametros:
    - `perfil_id`: identificador unico de um perfil.
- Possiveis retornos:
    - `codigo`: codigo de retorno propagado de chamada interna.
- TADs envolvidos: Estado da aplicacao (_ESTADO), Perfil, Configuracoes, Resultado de backup, Metadados de arquivo.

#### `executar_backup_do_perfil(perfil_id)`
- Visibilidade: publica.
- Objetivo: Executa o backup do perfil informado.
- Parametros:
    - `perfil_id`: identificador unico de um perfil.
- Possiveis retornos:
    - `(codigo_backup, resultado)`: tupla de retorno; normalmente combina codigo e dado/resultado.
    - `(codigo, None)`: tupla de retorno; normalmente combina codigo e dado/resultado.
    - `(ERRO_PERFIL_INATIVO, None)`: tupla de retorno; normalmente combina codigo e dado/resultado.
- TADs envolvidos: Estado da aplicacao (_ESTADO), Perfil, Configuracoes, Resultado de backup, Metadados de arquivo.

#### `obter_arquivos_do_perfil(perfil_id)`
- Visibilidade: publica.
- Objetivo: Lista arquivos do perfil e informa quais entram no backup.
- Parametros:
    - `perfil_id`: identificador unico de um perfil.
- Possiveis retornos:
    - `obter_arquivos_do_perfil_configurado(perfil)`: retorno delegado para outra funcao.
    - `(codigo, None)`: tupla de retorno; normalmente combina codigo e dado/resultado.
- TADs envolvidos: Estado da aplicacao (_ESTADO), Perfil, Configuracoes, Resultado de backup, Metadados de arquivo.

#### `obter_arquivos_do_perfil_configurado(perfil)`
- Visibilidade: publica.
- Objetivo: Lista arquivos de um perfil ja carregado no modelo atual.
- Parametros:
    - `perfil`: TAD Perfil, dicionario persistido com id, nome, ativo e origens configuradas.
- Possiveis retornos:
    - `(OK, arquivos)`: tupla de retorno; normalmente combina codigo e dado/resultado.
- TADs envolvidos: Estado da aplicacao (_ESTADO), Perfil, Configuracoes, Resultado de backup, Metadados de arquivo.

#### `obter_configuracoes()`
- Visibilidade: publica.
- Objetivo: Retorna o dicionario de configuracoes gerais em memoria.
- Parametros:
    - nenhum parametro.
- Possiveis retornos:
    - `(OK, _ESTADO['config'])`: tupla de retorno; normalmente combina codigo e dado/resultado.
- TADs envolvidos: Estado da aplicacao (_ESTADO), Perfil, Configuracoes, Resultado de backup, Metadados de arquivo.

#### `salvar_configuracoes(config)`
- Visibilidade: publica.
- Objetivo: Substitui as configuracoes gerais mantidas em memoria.
- Parametros:
    - `config`: TAD Configuracoes gerais da aplicacao.
- Possiveis retornos:
    - `OK`: sucesso da operacao.
    - `ERRO_DADOS_INVALIDOS`: entrada com tipo, formato ou valor invalido.
- TADs envolvidos: Estado da aplicacao (_ESTADO), Perfil, Configuracoes, Resultado de backup, Metadados de arquivo.

#### `normalizar_extensao(extensao)`
- Visibilidade: publica.
- Objetivo: Normaliza texto de extensao para o formato `.ext`.
- Parametros:
    - `extensao`: extensao textual, com ou sem ponto inicial.
- Possiveis retornos:
    - `extensao`: valor calculado pela funcao.
    - `None`: ausencia valida de dado ou falha sem objeto retornavel.
- TADs envolvidos: Estado da aplicacao (_ESTADO), Perfil, Configuracoes, Resultado de backup, Metadados de arquivo.

#### `obter_extensoes_disponiveis()`
- Visibilidade: publica.
- Objetivo: Retorna a lista ordenada de extensoes disponiveis na interface.
- Parametros:
    - nenhum parametro.
- Possiveis retornos:
    - `(OK, sorted(extensoes))`: tupla de retorno; normalmente combina codigo e dado/resultado.
- TADs envolvidos: Estado da aplicacao (_ESTADO), Perfil, Configuracoes, Resultado de backup, Metadados de arquivo.

#### `adicionar_extensao_disponivel(extensao)`
- Visibilidade: publica.
- Objetivo: Adiciona uma extensao customizada a configuracao em memoria.
- Parametros:
    - `extensao`: extensao textual, com ou sem ponto inicial.
- Possiveis retornos:
    - `OK`: sucesso da operacao.
    - `ERRO_DADOS_INVALIDOS`: entrada com tipo, formato ou valor invalido.
    - `codigo`: codigo de retorno propagado de chamada interna.
- TADs envolvidos: Estado da aplicacao (_ESTADO), Perfil, Configuracoes, Resultado de backup, Metadados de arquivo.

## Pasta `backupmanager/domain`

### Modulo `backup_result.py`

Resumo: Montagem e acumulacao de resultados de backup.

TADs/obrigacoes do modulo: Resultado geral de backup, Resultado individual de arquivo, Registro de arquivo, Erro de arquivo.

#### `montar_resultado_backup(perfil_id)`
- Visibilidade: publica.
- Objetivo: Cria o resultado base de uma execucao de backup.
- Parametros:
    - `perfil_id`: identificador unico de um perfil.
- Possiveis retornos:
    - `{'perfil_id': perfil_id, 'status': 'nao_executado', 'arquivos_processados': 0, 'arquivos_copiados': 0, 'arquivos_movidos': 0, 'arquivos_recortados': 0, 'arquivos': [], 'erros': []}`: novo dicionario/TAD montado pela funcao.
- TADs envolvidos: Resultado geral de backup, Resultado individual de arquivo, Registro de arquivo, Erro de arquivo.

#### `montar_resultado_arquivo()`
- Visibilidade: publica.
- Objetivo: Cria o resultado acumulado para o processamento de um arquivo.
- Parametros:
    - nenhum parametro.
- Possiveis retornos:
    - `{'codigo': OK, 'processado': False, 'arquivos_copiados': 0, 'arquivos_movidos': 0, 'arquivos_recortados': 0, 'arquivos': [], 'erros': []}`: novo dicionario/TAD montado pela funcao.
- TADs envolvidos: Resultado geral de backup, Resultado individual de arquivo, Registro de arquivo, Erro de arquivo.

#### `definir_status_resultado(resultado, status)`
- Visibilidade: publica.
- Objetivo: Altera o status textual do resultado geral.
- Parametros:
    - `resultado`: TAD Resultado geral de backup.
    - `status`: parametro usado pela funcao conforme o contexto do modulo.
- Possiveis retornos:
    - `resultado`: valor calculado pela funcao.
- TADs envolvidos: Resultado geral de backup, Resultado individual de arquivo, Registro de arquivo, Erro de arquivo.

#### `obter_status_resultado(resultado)`
- Visibilidade: publica.
- Objetivo: Retorna o status textual do resultado geral.
- Parametros:
    - `resultado`: TAD Resultado geral de backup.
- Possiveis retornos:
    - `resultado.get('status', '')`: retorno delegado para outra funcao.
- TADs envolvidos: Resultado geral de backup, Resultado individual de arquivo, Registro de arquivo, Erro de arquivo.

#### `obter_arquivos_processados(resultado)`
- Visibilidade: publica.
- Objetivo: Retorna a quantidade de arquivos processados no resultado geral.
- Parametros:
    - `resultado`: TAD Resultado geral de backup.
- Possiveis retornos:
    - `resultado.get('arquivos_processados', 0)`: retorno delegado para outra funcao.
- TADs envolvidos: Resultado geral de backup, Resultado individual de arquivo, Registro de arquivo, Erro de arquivo.

#### `resultado_possui_erros(resultado)`
- Visibilidade: publica.
- Objetivo: Indica se o resultado geral possui erros registrados.
- Parametros:
    - `resultado`: TAD Resultado geral de backup.
- Possiveis retornos:
    - `bool(resultado.get('erros', []))`: booleano calculado pela condicao.
- TADs envolvidos: Resultado geral de backup, Resultado individual de arquivo, Registro de arquivo, Erro de arquivo.

#### `obter_arquivos_resultado(resultado)`
- Visibilidade: publica.
- Objetivo: Retorna os registros de arquivos do resultado geral.
- Parametros:
    - `resultado`: TAD Resultado geral de backup.
- Possiveis retornos:
    - `resultado.get('arquivos', [])`: retorno delegado para outra funcao.
- TADs envolvidos: Resultado geral de backup, Resultado individual de arquivo, Registro de arquivo, Erro de arquivo.

#### `obter_erros_resultado(resultado)`
- Visibilidade: publica.
- Objetivo: Retorna os erros do resultado geral.
- Parametros:
    - `resultado`: TAD Resultado geral de backup.
- Possiveis retornos:
    - `resultado.get('erros', [])`: retorno delegado para outra funcao.
- TADs envolvidos: Resultado geral de backup, Resultado individual de arquivo, Registro de arquivo, Erro de arquivo.

#### `obter_contador_resultado(resultado, nome)`
- Visibilidade: publica.
- Objetivo: Retorna um contador numerico do resultado geral.
- Parametros:
    - `resultado`: TAD Resultado geral de backup.
    - `nome`: nome informado pelo usuario ou nome interno do TAD.
- Possiveis retornos:
    - `resultado.get(nome, 0)`: retorno delegado para outra funcao.
- TADs envolvidos: Resultado geral de backup, Resultado individual de arquivo, Registro de arquivo, Erro de arquivo.

#### `aplicar_resultado_arquivo(resultado, resultado_arquivo)`
- Visibilidade: publica.
- Objetivo: Acumula o resultado de um arquivo no resultado geral.
- Parametros:
    - `resultado`: TAD Resultado geral de backup.
    - `resultado_arquivo`: TAD Resultado individual de arquivo.
- Possiveis retornos:
    - `resultado`: valor calculado pela funcao.
- TADs envolvidos: Resultado geral de backup, Resultado individual de arquivo, Registro de arquivo, Erro de arquivo.

#### `resultado_arquivo_foi_processado(resultado_arquivo)`
- Visibilidade: publica.
- Objetivo: Indica se o resultado individual processou o arquivo.
- Parametros:
    - `resultado_arquivo`: TAD Resultado individual de arquivo.
- Possiveis retornos:
    - `bool(resultado_arquivo.get('processado', False))`: booleano calculado pela condicao.
- TADs envolvidos: Resultado geral de backup, Resultado individual de arquivo, Registro de arquivo, Erro de arquivo.

#### `obter_codigo_resultado_arquivo(resultado_arquivo)`
- Visibilidade: publica.
- Objetivo: Retorna o codigo de retorno do resultado individual.
- Parametros:
    - `resultado_arquivo`: TAD Resultado individual de arquivo.
- Possiveis retornos:
    - `resultado_arquivo.get('codigo', OK)`: codigo de sucesso junto do TAD Resultado.
- TADs envolvidos: Resultado geral de backup, Resultado individual de arquivo, Registro de arquivo, Erro de arquivo.

#### `obter_copiados_resultado_arquivo(resultado_arquivo)`
- Visibilidade: publica.
- Objetivo: Retorna o contador de copias do resultado individual.
- Parametros:
    - `resultado_arquivo`: TAD Resultado individual de arquivo.
- Possiveis retornos:
    - `resultado_arquivo.get('arquivos_copiados', 0)`: retorno delegado para outra funcao.
- TADs envolvidos: Resultado geral de backup, Resultado individual de arquivo, Registro de arquivo, Erro de arquivo.

#### `obter_movidos_resultado_arquivo(resultado_arquivo)`
- Visibilidade: publica.
- Objetivo: Retorna o contador de movimentos do resultado individual.
- Parametros:
    - `resultado_arquivo`: TAD Resultado individual de arquivo.
- Possiveis retornos:
    - `resultado_arquivo.get('arquivos_movidos', 0)`: retorno delegado para outra funcao.
- TADs envolvidos: Resultado geral de backup, Resultado individual de arquivo, Registro de arquivo, Erro de arquivo.

#### `obter_recortados_resultado_arquivo(resultado_arquivo)`
- Visibilidade: publica.
- Objetivo: Retorna o contador de recortes do resultado individual.
- Parametros:
    - `resultado_arquivo`: TAD Resultado individual de arquivo.
- Possiveis retornos:
    - `resultado_arquivo.get('arquivos_recortados', 0)`: retorno delegado para outra funcao.
- TADs envolvidos: Resultado geral de backup, Resultado individual de arquivo, Registro de arquivo, Erro de arquivo.

#### `obter_erros_resultado_arquivo(resultado_arquivo)`
- Visibilidade: publica.
- Objetivo: Retorna a lista de erros do resultado individual.
- Parametros:
    - `resultado_arquivo`: TAD Resultado individual de arquivo.
- Possiveis retornos:
    - `resultado_arquivo.get('erros', [])`: retorno delegado para outra funcao.
- TADs envolvidos: Resultado geral de backup, Resultado individual de arquivo, Registro de arquivo, Erro de arquivo.

#### `definir_codigo_resultado_arquivo(resultado_arquivo, codigo)`
- Visibilidade: publica.
- Objetivo: Altera o codigo de retorno do resultado individual.
- Parametros:
    - `resultado_arquivo`: TAD Resultado individual de arquivo.
    - `codigo`: codigo de retorno de return_codes.py.
- Possiveis retornos:
    - `resultado_arquivo`: valor calculado pela funcao.
- TADs envolvidos: Resultado geral de backup, Resultado individual de arquivo, Registro de arquivo, Erro de arquivo.

#### `definir_processado_resultado_arquivo(resultado_arquivo, processado)`
- Visibilidade: publica.
- Objetivo: Marca se o resultado individual processou o arquivo.
- Parametros:
    - `resultado_arquivo`: TAD Resultado individual de arquivo.
    - `processado`: parametro usado pela funcao conforme o contexto do modulo.
- Possiveis retornos:
    - `resultado_arquivo`: valor calculado pela funcao.
- TADs envolvidos: Resultado geral de backup, Resultado individual de arquivo, Registro de arquivo, Erro de arquivo.

#### `somar_copiados_resultado_arquivo(resultado_arquivo, quantidade=1)`
- Visibilidade: publica.
- Objetivo: Soma arquivos copiados ao resultado individual.
- Parametros:
    - `resultado_arquivo`: TAD Resultado individual de arquivo.
    - `quantidade`: incremento numerico aplicado a contador.
- Possiveis retornos:
    - `resultado_arquivo`: valor calculado pela funcao.
- TADs envolvidos: Resultado geral de backup, Resultado individual de arquivo, Registro de arquivo, Erro de arquivo.

#### `somar_movidos_resultado_arquivo(resultado_arquivo, quantidade=1)`
- Visibilidade: publica.
- Objetivo: Soma arquivos movidos ao resultado individual.
- Parametros:
    - `resultado_arquivo`: TAD Resultado individual de arquivo.
    - `quantidade`: incremento numerico aplicado a contador.
- Possiveis retornos:
    - `resultado_arquivo`: valor calculado pela funcao.
- TADs envolvidos: Resultado geral de backup, Resultado individual de arquivo, Registro de arquivo, Erro de arquivo.

#### `somar_recortados_resultado_arquivo(resultado_arquivo, quantidade=1)`
- Visibilidade: publica.
- Objetivo: Soma arquivos recortados ao resultado individual.
- Parametros:
    - `resultado_arquivo`: TAD Resultado individual de arquivo.
    - `quantidade`: incremento numerico aplicado a contador.
- Possiveis retornos:
    - `resultado_arquivo`: valor calculado pela funcao.
- TADs envolvidos: Resultado geral de backup, Resultado individual de arquivo, Registro de arquivo, Erro de arquivo.

#### `zerar_movidos_resultado_arquivo(resultado_arquivo)`
- Visibilidade: publica.
- Objetivo: Zera o contador de movimentos do resultado individual.
- Parametros:
    - `resultado_arquivo`: TAD Resultado individual de arquivo.
- Possiveis retornos:
    - `resultado_arquivo`: valor calculado pela funcao.
- TADs envolvidos: Resultado geral de backup, Resultado individual de arquivo, Registro de arquivo, Erro de arquivo.

#### `adicionar_registro_resultado_arquivo(resultado_arquivo, registro)`
- Visibilidade: publica.
- Objetivo: Adiciona um registro de arquivo ao resultado individual.
- Parametros:
    - `resultado_arquivo`: TAD Resultado individual de arquivo.
    - `registro`: registro detalhado de arquivo processado.
- Possiveis retornos:
    - `resultado_arquivo`: valor calculado pela funcao.
- TADs envolvidos: Resultado geral de backup, Resultado individual de arquivo, Registro de arquivo, Erro de arquivo.

#### `adicionar_erro_resultado_arquivo(resultado_arquivo, erro)`
- Visibilidade: publica.
- Objetivo: Adiciona um erro ao resultado individual.
- Parametros:
    - `resultado_arquivo`: TAD Resultado individual de arquivo.
    - `erro`: erro capturado ou registro de erro.
- Possiveis retornos:
    - `resultado_arquivo`: valor calculado pela funcao.
- TADs envolvidos: Resultado geral de backup, Resultado individual de arquivo, Registro de arquivo, Erro de arquivo.

#### `resultado_arquivo_possui_erros(resultado_arquivo)`
- Visibilidade: publica.
- Objetivo: Indica se o resultado individual possui erros.
- Parametros:
    - `resultado_arquivo`: TAD Resultado individual de arquivo.
- Possiveis retornos:
    - `bool(resultado_arquivo.get('erros', []))`: booleano calculado pela condicao.
- TADs envolvidos: Resultado geral de backup, Resultado individual de arquivo, Registro de arquivo, Erro de arquivo.

#### `obter_registros_resultado_arquivo(resultado_arquivo)`
- Visibilidade: publica.
- Objetivo: Retorna os registros do resultado individual.
- Parametros:
    - `resultado_arquivo`: TAD Resultado individual de arquivo.
- Possiveis retornos:
    - `resultado_arquivo.get('arquivos', [])`: retorno delegado para outra funcao.
- TADs envolvidos: Resultado geral de backup, Resultado individual de arquivo, Registro de arquivo, Erro de arquivo.

#### `marcar_registros_como_recorte(resultado_arquivo)`
- Visibilidade: publica.
- Objetivo: Troca operacao `mover` por `recortar` nos registros individuais.
- Parametros:
    - `resultado_arquivo`: TAD Resultado individual de arquivo.
- Possiveis retornos:
    - `resultado_arquivo`: valor calculado pela funcao.
- TADs envolvidos: Resultado geral de backup, Resultado individual de arquivo, Registro de arquivo, Erro de arquivo.

#### `montar_registro_arquivo(arquivo, destino, operacao, codigo)`
- Visibilidade: publica.
- Objetivo: Monta o registro detalhado de um arquivo processado.
- Parametros:
    - `arquivo`: TAD Metadados de Arquivo.
    - `destino`: TAD Destino ou caminho final, conforme contexto.
    - `operacao`: modo de transferencia: copiar, mover ou recortar.
    - `codigo`: codigo de retorno de return_codes.py.
- Possiveis retornos:
    - `{'nome': file_utils.obter_nome_arquivo(arquivo), 'extensao': file_utils.obter_extensao_arquivo(arquivo), 'tipo': file_utils.obter_nome_tipo_arquivo(arquivo), 'tamanho': file_utils.obter_tamanho_arquivo(arquivo), 'origem': file_utils.obter_caminho_arquivo(arquivo), 'destino': str(destino), 'operacao': operacao, 'status': 'sucesso' if codigo == OK else 'erro', 'codigo': codigo}`: novo dicionario/TAD montado pela funcao.
- TADs envolvidos: Resultado geral de backup, Resultado individual de arquivo, Registro de arquivo, Erro de arquivo.

#### `montar_erro_arquivo(arquivo, destino, codigo)`
- Visibilidade: publica.
- Objetivo: Monta o registro simples de erro associado a um arquivo.
- Parametros:
    - `arquivo`: TAD Metadados de Arquivo.
    - `destino`: TAD Destino ou caminho final, conforme contexto.
    - `codigo`: codigo de retorno de return_codes.py.
- Possiveis retornos:
    - `{'arquivo': nome, 'destino': str(destino), 'codigo': codigo}`: novo dicionario/TAD montado pela funcao.
- TADs envolvidos: Resultado geral de backup, Resultado individual de arquivo, Registro de arquivo, Erro de arquivo.

### Modulo `backup_validation.py`

Resumo: Validacao de perfis, origens, tipos, destinos e operacoes de backup.

TADs/obrigacoes do modulo: Perfil, Origem configurada, Tipo de arquivo, Destino do tipo.

#### `validar_perfil_para_backup(perfil)`
- Visibilidade: publica.
- Objetivo: Valida o contrato minimo para executar backup.
- Parametros:
    - `perfil`: TAD Perfil, dicionario persistido com id, nome, ativo e origens configuradas.
- Possiveis retornos:
    - `validar_perfil_configurado_para_backup(perfil)`: retorno delegado para outra funcao.
    - `ERRO_DADOS_INVALIDOS`: entrada com tipo, formato ou valor invalido.
- TADs envolvidos: Perfil, Origem configurada, Tipo de arquivo, Destino do tipo.

#### `validar_perfil_configurado_para_backup(perfil)`
- Visibilidade: publica.
- Objetivo: Valida um perfil no modelo origem -> tipo -> destino.
- Parametros:
    - `perfil`: TAD Perfil, dicionario persistido com id, nome, ativo e origens configuradas.
- Possiveis retornos:
    - `OK`: sucesso da operacao.
    - `ERRO_ORIGEM_INVALIDA`: origem ausente, vazia ou estruturalmente invalida.
    - `ERRO_DESTINO_INVALIDO`: destino ausente, vazio ou estruturalmente invalido.
    - `ERRO_DADOS_INVALIDOS`: entrada com tipo, formato ou valor invalido.
    - `codigo`: codigo de retorno propagado de chamada interna.
- TADs envolvidos: Perfil, Origem configurada, Tipo de arquivo, Destino do tipo.

#### `validar_destinos_do_tipo(tipo)`
- Visibilidade: publica.
- Objetivo: Valida a lista de destinos de um tipo de arquivo.
- Parametros:
    - `tipo`: TAD Tipo de Arquivo, com nome, ativo, restricoes e destinos.
- Possiveis retornos:
    - `OK`: sucesso da operacao.
    - `ERRO_OPERACAO_INVALIDA`: operacao diferente de copiar/mover/recortar ou conflito de remocao.
    - `ERRO_DESTINO_INVALIDO`: destino ausente, vazio ou estruturalmente invalido.
- TADs envolvidos: Perfil, Origem configurada, Tipo de arquivo, Destino do tipo.

### Modulo `perfil_manager.py`

Resumo: Funcoes para criar, consultar e alterar perfis de backup.

TADs/obrigacoes do modulo: Perfil, Origem configurada, Tipo de arquivo, Destino do tipo, Restricoes.

#### `criar_restricoes_padrao()`
- Visibilidade: publica.
- Objetivo: Cria restricoes vazias no formato aceito pelo motor de backup.
- Parametros:
    - nenhum parametro.
- Possiveis retornos:
    - `{'extensoes_permitidas': [], 'regras_nome': [], 'tamanho_min': 0, 'tamanho_max': None, 'data_modificacao_min': None, 'data_modificacao_max': None}`: novo dicionario/TAD montado pela funcao.
- TADs envolvidos: Perfil, Origem configurada, Tipo de arquivo, Destino do tipo, Restricoes.

#### `criar_restricoes(extensoes, regras_nome, tamanho_min, tamanho_max, data_min, data_max)`
- Visibilidade: publica.
- Objetivo: Cria restricoes completas para um tipo de arquivo.
- Parametros:
    - `extensoes`: lista de extensoes permitidas ou disponiveis.
    - `regras_nome`: lista de regras de nome em modo contem/exato.
    - `tamanho_min`: tamanho minimo em bytes; 0 quando sem limite minimo.
    - `tamanho_max`: tamanho maximo em bytes; None quando sem limite maximo.
    - `data_min`: data/timestamp minimo de modificacao; None quando sem limite.
    - `data_max`: data/timestamp maximo de modificacao; None quando sem limite.
- Possiveis retornos:
    - `{'extensoes_permitidas': extensoes if isinstance(extensoes, list) else [], 'regras_nome': regras_nome if isinstance(regras_nome, list) else [], 'tamanho_min': tamanho_min, 'tamanho_max': tamanho_max, 'data_modificacao_min': data_min, 'data_modificacao_max': data_max}`: novo dicionario/TAD montado pela funcao.
- TADs envolvidos: Perfil, Origem configurada, Tipo de arquivo, Destino do tipo, Restricoes.

#### `criar_destino_tipo(caminho, operacao='copiar')`
- Visibilidade: publica.
- Objetivo: Cria um destino de backup vinculado a um tipo de arquivo.
- Parametros:
    - `caminho`: caminho de arquivo ou pasta no sistema operacional.
    - `operacao`: modo de transferencia: copiar, mover ou recortar.
- Possiveis retornos:
    - `{'caminho': caminho, 'operacao': operacao}`: novo dicionario/TAD montado pela funcao.
- TADs envolvidos: Perfil, Origem configurada, Tipo de arquivo, Destino do tipo, Restricoes.

#### `criar_tipo_arquivo(nome, restricoes=None, destinos=None)`
- Visibilidade: publica.
- Objetivo: Cria uma configuracao de tipo/filtro dentro de uma origem.
- Parametros:
    - `nome`: nome informado pelo usuario ou nome interno do TAD.
    - `restricoes`: TAD Restricoes usado para filtrar arquivos.
    - `destinos`: lista de TADs Destino ou caminhos de destino, conforme contexto.
- Possiveis retornos:
    - `{'id': 'tipo_' + uuid.uuid4().hex[:8], 'nome': nome, 'ativo': True, 'restricoes': restricoes, 'destinos': destinos}`: novo dicionario/TAD montado pela funcao.
- TADs envolvidos: Perfil, Origem configurada, Tipo de arquivo, Destino do tipo, Restricoes.

#### `criar_origem_configurada(caminho)`
- Visibilidade: publica.
- Objetivo: Cria uma origem no modelo atual origem -> tipo -> destino.
- Parametros:
    - `caminho`: caminho de arquivo ou pasta no sistema operacional.
- Possiveis retornos:
    - `{'id': 'origem_' + uuid.uuid4().hex[:8], 'caminho': caminho, 'ativo': True, 'tipos_arquivo': []}`: novo dicionario/TAD montado pela funcao.
- TADs envolvidos: Perfil, Origem configurada, Tipo de arquivo, Destino do tipo, Restricoes.

#### `_gerar_id_perfil(perfis)`
- Visibilidade: interna.
- Objetivo: Gera um identificador unico para um novo perfil.
- Parametros:
    - `perfis`: colecao em memoria de TADs Perfil.
- Possiveis retornos:
    - `'perfil_' + uuid.uuid4().hex[:8]`: retorno delegado para outra funcao.
- TADs envolvidos: Perfil, Origem configurada, Tipo de arquivo, Destino do tipo, Restricoes.

#### `validar_nome_perfil(nome)`
- Visibilidade: publica.
- Objetivo: Valida o nome usado para criar ou renomear um perfil.
- Parametros:
    - `nome`: nome informado pelo usuario ou nome interno do TAD.
- Possiveis retornos:
    - `OK`: sucesso da operacao.
    - `ERRO_NOME_INVALIDO`: nome vazio ou invalido.
- TADs envolvidos: Perfil, Origem configurada, Tipo de arquivo, Destino do tipo, Restricoes.

#### `criar_perfil(nome)`
- Visibilidade: publica.
- Objetivo: Cria um perfil novo em memoria no modelo atual.
- Parametros:
    - `nome`: nome informado pelo usuario ou nome interno do TAD.
- Possiveis retornos:
    - `(OK, perfil)`: tupla de retorno; normalmente combina codigo e dado/resultado.
    - `(codigo, None)`: tupla de retorno; normalmente combina codigo e dado/resultado.
- TADs envolvidos: Perfil, Origem configurada, Tipo de arquivo, Destino do tipo, Restricoes.

#### `consultar_perfil(perfis, perfil_id)`
- Visibilidade: publica.
- Objetivo: Consulta um perfil pelo identificador dentro de uma lista.
- Parametros:
    - `perfis`: colecao em memoria de TADs Perfil.
    - `perfil_id`: identificador unico de um perfil.
- Possiveis retornos:
    - `(ERRO_PERFIL_NAO_ENCONTRADO, None)`: tupla de retorno; normalmente combina codigo e dado/resultado.
    - `(OK, perfil)`: tupla de retorno; normalmente combina codigo e dado/resultado.
- TADs envolvidos: Perfil, Origem configurada, Tipo de arquivo, Destino do tipo, Restricoes.

#### `listar_perfis(perfis)`
- Visibilidade: publica.
- Objetivo: Retorna a colecao de perfis atualmente mantida em memoria.
- Parametros:
    - `perfis`: colecao em memoria de TADs Perfil.
- Possiveis retornos:
    - `(OK, perfis)`: tupla de retorno; normalmente combina codigo e dado/resultado.
- TADs envolvidos: Perfil, Origem configurada, Tipo de arquivo, Destino do tipo, Restricoes.

#### `obter_id_perfil(perfil)`
- Visibilidade: publica.
- Objetivo: Retorna o identificador de um perfil.
- Parametros:
    - `perfil`: TAD Perfil, dicionario persistido com id, nome, ativo e origens configuradas.
- Possiveis retornos:
    - `perfil.get('id')`: retorno delegado para outra funcao.
    - `None`: ausencia valida de dado ou falha sem objeto retornavel.
- TADs envolvidos: Perfil, Origem configurada, Tipo de arquivo, Destino do tipo, Restricoes.

#### `obter_nome_perfil(perfil)`
- Visibilidade: publica.
- Objetivo: Retorna o nome de exibicao do perfil.
- Parametros:
    - `perfil`: TAD Perfil, dicionario persistido com id, nome, ativo e origens configuradas.
- Possiveis retornos:
    - `nome`: valor calculado pela funcao.
    - `''`: valor calculado pela funcao.
- TADs envolvidos: Perfil, Origem configurada, Tipo de arquivo, Destino do tipo, Restricoes.

#### `perfil_esta_ativo(perfil)`
- Visibilidade: publica.
- Objetivo: Indica se um perfil deve participar de execucoes.
- Parametros:
    - `perfil`: TAD Perfil, dicionario persistido com id, nome, ativo e origens configuradas.
- Possiveis retornos:
    - `perfil.get('ativo', True)`: retorno delegado para outra funcao.
    - `False`: condicao rejeitada/falsa.
- TADs envolvidos: Perfil, Origem configurada, Tipo de arquivo, Destino do tipo, Restricoes.

#### `obter_origens_configuradas(perfil)`
- Visibilidade: publica.
- Objetivo: Retorna as origens configuradas de um perfil.
- Parametros:
    - `perfil`: TAD Perfil, dicionario persistido com id, nome, ativo e origens configuradas.
- Possiveis retornos:
    - `origens`: valor calculado pela funcao.
    - `[]`: lista vazia; nenhuma entrada aplicavel.
- TADs envolvidos: Perfil, Origem configurada, Tipo de arquivo, Destino do tipo, Restricoes.

#### `perfil_possui_origens_configuradas(perfil)`
- Visibilidade: publica.
- Objetivo: Indica se um perfil possui ao menos uma origem configurada.
- Parametros:
    - `perfil`: TAD Perfil, dicionario persistido com id, nome, ativo e origens configuradas.
- Possiveis retornos:
    - `bool(obter_origens_configuradas(perfil))`: booleano calculado pela condicao.
- TADs envolvidos: Perfil, Origem configurada, Tipo de arquivo, Destino do tipo, Restricoes.

#### `alterar_nome_perfil(perfis, perfil_id, novo_nome)`
- Visibilidade: publica.
- Objetivo: Altera o nome de um perfil existente apos validacao.
- Parametros:
    - `perfis`: colecao em memoria de TADs Perfil.
    - `perfil_id`: identificador unico de um perfil.
    - `novo_nome`: novo nome a gravar no perfil ou tipo.
- Possiveis retornos:
    - `OK`: sucesso da operacao.
    - `codigo`: codigo de retorno propagado de chamada interna.
- TADs envolvidos: Perfil, Origem configurada, Tipo de arquivo, Destino do tipo, Restricoes.

#### `alterar_origens_configuradas(perfis, perfil_id, origens_configuradas)`
- Visibilidade: publica.
- Objetivo: Substitui as origens configuradas de um perfil.
- Parametros:
    - `perfis`: colecao em memoria de TADs Perfil.
    - `perfil_id`: identificador unico de um perfil.
    - `origens_configuradas`: lista completa de TADs Origem do perfil.
- Possiveis retornos:
    - `OK`: sucesso da operacao.
    - `ERRO_DADOS_INVALIDOS`: entrada com tipo, formato ou valor invalido.
    - `codigo`: codigo de retorno propagado de chamada interna.
- TADs envolvidos: Perfil, Origem configurada, Tipo de arquivo, Destino do tipo, Restricoes.

#### `excluir_perfil(perfis, perfil_id)`
- Visibilidade: publica.
- Objetivo: Remove da lista o perfil identificado por `perfil_id`.
- Parametros:
    - `perfis`: colecao em memoria de TADs Perfil.
    - `perfil_id`: identificador unico de um perfil.
- Possiveis retornos:
    - `OK`: sucesso da operacao.
    - `codigo`: codigo de retorno propagado de chamada interna.
- TADs envolvidos: Perfil, Origem configurada, Tipo de arquivo, Destino do tipo, Restricoes.

#### `ativar_perfil(perfis, perfil_id)`
- Visibilidade: publica.
- Objetivo: Marca um perfil existente como ativo para execucoes futuras.
- Parametros:
    - `perfis`: colecao em memoria de TADs Perfil.
    - `perfil_id`: identificador unico de um perfil.
- Possiveis retornos:
    - `OK`: sucesso da operacao.
    - `codigo`: codigo de retorno propagado de chamada interna.
- TADs envolvidos: Perfil, Origem configurada, Tipo de arquivo, Destino do tipo, Restricoes.

#### `desativar_perfil(perfis, perfil_id)`
- Visibilidade: publica.
- Objetivo: Marca um perfil existente como inativo.
- Parametros:
    - `perfis`: colecao em memoria de TADs Perfil.
    - `perfil_id`: identificador unico de um perfil.
- Possiveis retornos:
    - `OK`: sucesso da operacao.
    - `codigo`: codigo de retorno propagado de chamada interna.
- TADs envolvidos: Perfil, Origem configurada, Tipo de arquivo, Destino do tipo, Restricoes.

#### `origem_e_valida(origem)`
- Visibilidade: publica.
- Objetivo: Indica se a entrada possui formato minimo de origem configurada.
- Parametros:
    - `origem`: TAD Origem Configurada, com caminho, ativo e tipos de arquivo.
- Possiveis retornos:
    - `isinstance(origem, dict)`: booleano calculado pela condicao.
- TADs envolvidos: Perfil, Origem configurada, Tipo de arquivo, Destino do tipo, Restricoes.

#### `obter_id_origem(origem)`
- Visibilidade: publica.
- Objetivo: Retorna o identificador interno da origem configurada.
- Parametros:
    - `origem`: TAD Origem Configurada, com caminho, ativo e tipos de arquivo.
- Possiveis retornos:
    - `origem.get('id')`: retorno delegado para outra funcao.
    - `None`: ausencia valida de dado ou falha sem objeto retornavel.
- TADs envolvidos: Perfil, Origem configurada, Tipo de arquivo, Destino do tipo, Restricoes.

#### `obter_caminho_origem(origem)`
- Visibilidade: publica.
- Objetivo: Retorna o caminho da pasta de origem.
- Parametros:
    - `origem`: TAD Origem Configurada, com caminho, ativo e tipos de arquivo.
- Possiveis retornos:
    - `caminho`: valor calculado pela funcao.
    - `''`: valor calculado pela funcao.
- TADs envolvidos: Perfil, Origem configurada, Tipo de arquivo, Destino do tipo, Restricoes.

#### `origem_esta_ativa(origem)`
- Visibilidade: publica.
- Objetivo: Indica se uma origem deve participar do backup.
- Parametros:
    - `origem`: TAD Origem Configurada, com caminho, ativo e tipos de arquivo.
- Possiveis retornos:
    - `origem.get('ativo', True)`: retorno delegado para outra funcao.
    - `False`: condicao rejeitada/falsa.
- TADs envolvidos: Perfil, Origem configurada, Tipo de arquivo, Destino do tipo, Restricoes.

#### `obter_tipos_origem(origem)`
- Visibilidade: publica.
- Objetivo: Retorna a lista de tipos de arquivo vinculados a uma origem.
- Parametros:
    - `origem`: TAD Origem Configurada, com caminho, ativo e tipos de arquivo.
- Possiveis retornos:
    - `tipos`: valor calculado pela funcao.
    - `[]`: lista vazia; nenhuma entrada aplicavel.
- TADs envolvidos: Perfil, Origem configurada, Tipo de arquivo, Destino do tipo, Restricoes.

#### `origem_possui_tipos(origem)`
- Visibilidade: publica.
- Objetivo: Indica se a origem possui tipos cadastrados.
- Parametros:
    - `origem`: TAD Origem Configurada, com caminho, ativo e tipos de arquivo.
- Possiveis retornos:
    - `bool(obter_tipos_origem(origem))`: booleano calculado pela condicao.
- TADs envolvidos: Perfil, Origem configurada, Tipo de arquivo, Destino do tipo, Restricoes.

#### `alterar_origem_ativa(origem, ativo)`
- Visibilidade: publica.
- Objetivo: Altera o estado ativo/inativo de uma origem configurada.
- Parametros:
    - `origem`: TAD Origem Configurada, com caminho, ativo e tipos de arquivo.
    - `ativo`: parametro usado pela funcao conforme o contexto do modulo.
- Possiveis retornos:
    - `OK`: sucesso da operacao.
    - `ERRO_DADOS_INVALIDOS`: entrada com tipo, formato ou valor invalido.
- TADs envolvidos: Perfil, Origem configurada, Tipo de arquivo, Destino do tipo, Restricoes.

#### `adicionar_tipo_origem(origem, tipo)`
- Visibilidade: publica.
- Objetivo: Adiciona um tipo de arquivo a uma origem configurada.
- Parametros:
    - `origem`: TAD Origem Configurada, com caminho, ativo e tipos de arquivo.
    - `tipo`: TAD Tipo de Arquivo, com nome, ativo, restricoes e destinos.
- Possiveis retornos:
    - `OK`: sucesso da operacao.
    - `ERRO_DADOS_INVALIDOS`: entrada com tipo, formato ou valor invalido.
- TADs envolvidos: Perfil, Origem configurada, Tipo de arquivo, Destino do tipo, Restricoes.

#### `remover_tipo_origem_por_indice(origem, indice)`
- Visibilidade: publica.
- Objetivo: Remove um tipo de arquivo da origem pelo indice.
- Parametros:
    - `origem`: TAD Origem Configurada, com caminho, ativo e tipos de arquivo.
    - `indice`: posicao selecionada em lista/listbox.
- Possiveis retornos:
    - `OK`: sucesso da operacao.
    - `ERRO_DADOS_INVALIDOS`: entrada com tipo, formato ou valor invalido.
- TADs envolvidos: Perfil, Origem configurada, Tipo de arquivo, Destino do tipo, Restricoes.

#### `tipo_e_valido(tipo)`
- Visibilidade: publica.
- Objetivo: Indica se a entrada possui formato minimo de tipo de arquivo.
- Parametros:
    - `tipo`: TAD Tipo de Arquivo, com nome, ativo, restricoes e destinos.
- Possiveis retornos:
    - `isinstance(tipo, dict)`: booleano calculado pela condicao.
- TADs envolvidos: Perfil, Origem configurada, Tipo de arquivo, Destino do tipo, Restricoes.

#### `obter_id_tipo(tipo)`
- Visibilidade: publica.
- Objetivo: Retorna o identificador do tipo de arquivo.
- Parametros:
    - `tipo`: TAD Tipo de Arquivo, com nome, ativo, restricoes e destinos.
- Possiveis retornos:
    - `tipo.get('id')`: retorno delegado para outra funcao.
    - `None`: ausencia valida de dado ou falha sem objeto retornavel.
- TADs envolvidos: Perfil, Origem configurada, Tipo de arquivo, Destino do tipo, Restricoes.

#### `obter_nome_tipo(tipo)`
- Visibilidade: publica.
- Objetivo: Retorna o nome exibido para o tipo de arquivo.
- Parametros:
    - `tipo`: TAD Tipo de Arquivo, com nome, ativo, restricoes e destinos.
- Possiveis retornos:
    - `nome`: valor calculado pela funcao.
    - `''`: valor calculado pela funcao.
- TADs envolvidos: Perfil, Origem configurada, Tipo de arquivo, Destino do tipo, Restricoes.

#### `tipo_esta_ativo(tipo)`
- Visibilidade: publica.
- Objetivo: Indica se um tipo de arquivo deve participar do backup.
- Parametros:
    - `tipo`: TAD Tipo de Arquivo, com nome, ativo, restricoes e destinos.
- Possiveis retornos:
    - `tipo.get('ativo', True)`: retorno delegado para outra funcao.
    - `False`: condicao rejeitada/falsa.
- TADs envolvidos: Perfil, Origem configurada, Tipo de arquivo, Destino do tipo, Restricoes.

#### `obter_restricoes_tipo(tipo)`
- Visibilidade: publica.
- Objetivo: Retorna as restricoes configuradas para um tipo.
- Parametros:
    - `tipo`: TAD Tipo de Arquivo, com nome, ativo, restricoes e destinos.
- Possiveis retornos:
    - `criar_restricoes_padrao()`: retorno delegado para outra funcao.
    - `restricoes`: valor calculado pela funcao.
- TADs envolvidos: Perfil, Origem configurada, Tipo de arquivo, Destino do tipo, Restricoes.

#### `obter_destinos_tipo(tipo)`
- Visibilidade: publica.
- Objetivo: Retorna a lista de destinos vinculados a um tipo.
- Parametros:
    - `tipo`: TAD Tipo de Arquivo, com nome, ativo, restricoes e destinos.
- Possiveis retornos:
    - `destinos`: valor calculado pela funcao.
    - `[]`: lista vazia; nenhuma entrada aplicavel.
- TADs envolvidos: Perfil, Origem configurada, Tipo de arquivo, Destino do tipo, Restricoes.

#### `tipo_possui_destinos(tipo)`
- Visibilidade: publica.
- Objetivo: Indica se um tipo possui ao menos um destino configurado.
- Parametros:
    - `tipo`: TAD Tipo de Arquivo, com nome, ativo, restricoes e destinos.
- Possiveis retornos:
    - `bool(obter_destinos_tipo(tipo))`: booleano calculado pela condicao.
- TADs envolvidos: Perfil, Origem configurada, Tipo de arquivo, Destino do tipo, Restricoes.

#### `alterar_nome_tipo(tipo, nome)`
- Visibilidade: publica.
- Objetivo: Altera o nome de um tipo de arquivo.
- Parametros:
    - `tipo`: TAD Tipo de Arquivo, com nome, ativo, restricoes e destinos.
    - `nome`: nome informado pelo usuario ou nome interno do TAD.
- Possiveis retornos:
    - `OK`: sucesso da operacao.
    - `ERRO_DADOS_INVALIDOS`: entrada com tipo, formato ou valor invalido.
- TADs envolvidos: Perfil, Origem configurada, Tipo de arquivo, Destino do tipo, Restricoes.

#### `adicionar_destino_tipo_configurado(tipo, destino)`
- Visibilidade: publica.
- Objetivo: Adiciona um destino a um tipo de arquivo.
- Parametros:
    - `tipo`: TAD Tipo de Arquivo, com nome, ativo, restricoes e destinos.
    - `destino`: TAD Destino ou caminho final, conforme contexto.
- Possiveis retornos:
    - `OK`: sucesso da operacao.
    - `ERRO_DADOS_INVALIDOS`: entrada com tipo, formato ou valor invalido.
- TADs envolvidos: Perfil, Origem configurada, Tipo de arquivo, Destino do tipo, Restricoes.

#### `remover_destino_tipo_por_indice(tipo, indice)`
- Visibilidade: publica.
- Objetivo: Remove um destino do tipo pelo indice.
- Parametros:
    - `tipo`: TAD Tipo de Arquivo, com nome, ativo, restricoes e destinos.
    - `indice`: posicao selecionada em lista/listbox.
- Possiveis retornos:
    - `OK`: sucesso da operacao.
    - `ERRO_DADOS_INVALIDOS`: entrada com tipo, formato ou valor invalido.
- TADs envolvidos: Perfil, Origem configurada, Tipo de arquivo, Destino do tipo, Restricoes.

#### `alterar_restricoes_tipo(tipo, restricoes)`
- Visibilidade: publica.
- Objetivo: Substitui as restricoes de um tipo de arquivo.
- Parametros:
    - `tipo`: TAD Tipo de Arquivo, com nome, ativo, restricoes e destinos.
    - `restricoes`: TAD Restricoes usado para filtrar arquivos.
- Possiveis retornos:
    - `OK`: sucesso da operacao.
    - `ERRO_DADOS_INVALIDOS`: entrada com tipo, formato ou valor invalido.
- TADs envolvidos: Perfil, Origem configurada, Tipo de arquivo, Destino do tipo, Restricoes.

#### `alterar_tipo_ativo(tipo, ativo)`
- Visibilidade: publica.
- Objetivo: Altera o estado ativo/inativo de um tipo de arquivo.
- Parametros:
    - `tipo`: TAD Tipo de Arquivo, com nome, ativo, restricoes e destinos.
    - `ativo`: parametro usado pela funcao conforme o contexto do modulo.
- Possiveis retornos:
    - `OK`: sucesso da operacao.
    - `ERRO_DADOS_INVALIDOS`: entrada com tipo, formato ou valor invalido.
- TADs envolvidos: Perfil, Origem configurada, Tipo de arquivo, Destino do tipo, Restricoes.

#### `destino_e_valido(destino)`
- Visibilidade: publica.
- Objetivo: Indica se a entrada possui formato minimo de destino.
- Parametros:
    - `destino`: TAD Destino ou caminho final, conforme contexto.
- Possiveis retornos:
    - `isinstance(destino, dict)`: booleano calculado pela condicao.
- TADs envolvidos: Perfil, Origem configurada, Tipo de arquivo, Destino do tipo, Restricoes.

#### `obter_caminho_destino(destino)`
- Visibilidade: publica.
- Objetivo: Retorna o caminho de pasta de um destino.
- Parametros:
    - `destino`: TAD Destino ou caminho final, conforme contexto.
- Possiveis retornos:
    - `caminho`: valor calculado pela funcao.
    - `''`: valor calculado pela funcao.
- TADs envolvidos: Perfil, Origem configurada, Tipo de arquivo, Destino do tipo, Restricoes.

#### `obter_operacao_destino(destino)`
- Visibilidade: publica.
- Objetivo: Retorna a operacao configurada para um destino.
- Parametros:
    - `destino`: TAD Destino ou caminho final, conforme contexto.
- Possiveis retornos:
    - `operacao`: valor calculado pela funcao.
    - `'copiar'`: valor calculado pela funcao.
- TADs envolvidos: Perfil, Origem configurada, Tipo de arquivo, Destino do tipo, Restricoes.

#### `alterar_operacao_destino(destino, operacao)`
- Visibilidade: publica.
- Objetivo: Altera a operacao configurada em um destino.
- Parametros:
    - `destino`: TAD Destino ou caminho final, conforme contexto.
    - `operacao`: modo de transferencia: copiar, mover ou recortar.
- Possiveis retornos:
    - `OK`: sucesso da operacao.
    - `ERRO_DADOS_INVALIDOS`: entrada com tipo, formato ou valor invalido.
- TADs envolvidos: Perfil, Origem configurada, Tipo de arquivo, Destino do tipo, Restricoes.

#### `restricoes_e_valida(restricoes)`
- Visibilidade: publica.
- Objetivo: Indica se a entrada possui formato minimo de restricoes.
- Parametros:
    - `restricoes`: TAD Restricoes usado para filtrar arquivos.
- Possiveis retornos:
    - `isinstance(restricoes, dict)`: booleano calculado pela condicao.
- TADs envolvidos: Perfil, Origem configurada, Tipo de arquivo, Destino do tipo, Restricoes.

#### `obter_extensoes_restricoes(restricoes)`
- Visibilidade: publica.
- Objetivo: Retorna as extensoes permitidas configuradas nas restricoes.
- Parametros:
    - `restricoes`: TAD Restricoes usado para filtrar arquivos.
- Possiveis retornos:
    - `extensoes`: valor calculado pela funcao.
    - `[]`: lista vazia; nenhuma entrada aplicavel.
- TADs envolvidos: Perfil, Origem configurada, Tipo de arquivo, Destino do tipo, Restricoes.

#### `obter_regras_nome_restricoes(restricoes)`
- Visibilidade: publica.
- Objetivo: Retorna as regras de nome configuradas nas restricoes.
- Parametros:
    - `restricoes`: TAD Restricoes usado para filtrar arquivos.
- Possiveis retornos:
    - `regras`: valor calculado pela funcao.
    - `[]`: lista vazia; nenhuma entrada aplicavel.
- TADs envolvidos: Perfil, Origem configurada, Tipo de arquivo, Destino do tipo, Restricoes.

#### `obter_tamanho_min_restricoes(restricoes)`
- Visibilidade: publica.
- Objetivo: Retorna o tamanho minimo configurado nas restricoes.
- Parametros:
    - `restricoes`: TAD Restricoes usado para filtrar arquivos.
- Possiveis retornos:
    - `restricoes.get('tamanho_min', 0) or 0`: retorno delegado para outra funcao.
    - `0`: valor calculado pela funcao.
- TADs envolvidos: Perfil, Origem configurada, Tipo de arquivo, Destino do tipo, Restricoes.

#### `obter_tamanho_max_restricoes(restricoes)`
- Visibilidade: publica.
- Objetivo: Retorna o tamanho maximo configurado nas restricoes.
- Parametros:
    - `restricoes`: TAD Restricoes usado para filtrar arquivos.
- Possiveis retornos:
    - `restricoes.get('tamanho_max')`: retorno delegado para outra funcao.
    - `None`: ausencia valida de dado ou falha sem objeto retornavel.
- TADs envolvidos: Perfil, Origem configurada, Tipo de arquivo, Destino do tipo, Restricoes.

#### `obter_data_min_restricoes(restricoes)`
- Visibilidade: publica.
- Objetivo: Retorna a data minima configurada nas restricoes.
- Parametros:
    - `restricoes`: TAD Restricoes usado para filtrar arquivos.
- Possiveis retornos:
    - `restricoes.get('data_modificacao_min')`: retorno delegado para outra funcao.
    - `None`: ausencia valida de dado ou falha sem objeto retornavel.
- TADs envolvidos: Perfil, Origem configurada, Tipo de arquivo, Destino do tipo, Restricoes.

#### `obter_data_max_restricoes(restricoes)`
- Visibilidade: publica.
- Objetivo: Retorna a data maxima configurada nas restricoes.
- Parametros:
    - `restricoes`: TAD Restricoes usado para filtrar arquivos.
- Possiveis retornos:
    - `restricoes.get('data_modificacao_max')`: retorno delegado para outra funcao.
    - `None`: ausencia valida de dado ou falha sem objeto retornavel.
- TADs envolvidos: Perfil, Origem configurada, Tipo de arquivo, Destino do tipo, Restricoes.

## Pasta `backupmanager/engine`

### Modulo `backup_engine.py`

Resumo: Execucao das rotinas de backup.

TADs/obrigacoes do modulo: Perfil, Origem configurada, Tipo de arquivo, Destino do tipo, Metadados de arquivo, Resultado de backup.

#### `executar_backup(perfil)`
- Visibilidade: publica.
- Objetivo: Executa a rotina de backup de um perfil.
- Parametros:
    - `perfil`: TAD Perfil, dicionario persistido com id, nome, ativo e origens configuradas.
- Possiveis retornos:
    - `_executar_backup_configurado(perfil)`: retorno delegado para outra funcao.
    - `(codigo_validacao, resultado)`: tupla de retorno; normalmente combina codigo e dado/resultado.
- TADs envolvidos: Perfil, Origem configurada, Tipo de arquivo, Destino do tipo, Metadados de arquivo, Resultado de backup.

#### `_executar_backup_configurado(perfil)`
- Visibilidade: interna.
- Objetivo: Executa backup no modelo origem -> tipo -> destino.
- Parametros:
    - `perfil`: TAD Perfil, dicionario persistido com id, nome, ativo e origens configuradas.
- Possiveis retornos:
    - `(primeiro_erro, resultado)`: tupla de retorno; normalmente combina codigo e dado/resultado.
    - `(ERRO_BACKUP_SEM_ARQUIVOS, resultado)`: tupla de retorno; normalmente combina codigo e dado/resultado.
    - `(OK, resultado)`: tupla de retorno; normalmente combina codigo e dado/resultado.
- TADs envolvidos: Perfil, Origem configurada, Tipo de arquivo, Destino do tipo, Metadados de arquivo, Resultado de backup.

#### `_executar_backup_da_origem_configurada(origem, resultado)`
- Visibilidade: interna.
- Objetivo: Executa todos os tipos de uma origem configurada.
- Parametros:
    - `origem`: TAD Origem Configurada, com caminho, ativo e tipos de arquivo.
    - `resultado`: TAD Resultado geral de backup.
- Possiveis retornos:
    - `primeiro_erro`: valor calculado pela funcao.
- TADs envolvidos: Perfil, Origem configurada, Tipo de arquivo, Destino do tipo, Metadados de arquivo, Resultado de backup.

#### `_filtrar_arquivos_por_tipo(caminhos, tipo)`
- Visibilidade: interna.
- Objetivo: Filtra arquivos de uma origem para um tipo.
- Parametros:
    - `caminhos`: lista de caminhos de arquivos candidatos.
    - `tipo`: TAD Tipo de Arquivo, com nome, ativo, restricoes e destinos.
- Possiveis retornos:
    - `arquivos`: valor calculado pela funcao.
- TADs envolvidos: Perfil, Origem configurada, Tipo de arquivo, Destino do tipo, Metadados de arquivo, Resultado de backup.

#### `_processar_arquivo_para_destinos(arquivo, destinos, operacao)`
- Visibilidade: interna.
- Objetivo: Processa um arquivo para uma lista de destinos.
- Parametros:
    - `arquivo`: TAD Metadados de Arquivo.
    - `destinos`: lista de TADs Destino ou caminhos de destino, conforme contexto.
    - `operacao`: modo de transferencia: copiar, mover ou recortar.
- Possiveis retornos:
    - `resultado`: valor calculado pela funcao.
    - `_processar_copia_para_destinos(arquivo, destinos, resultado)`: retorno delegado para outra funcao.
    - `_processar_movimento_para_destinos(arquivo, destinos, resultado)`: retorno delegado para outra funcao.
    - `_processar_recorte_para_destinos(arquivo, destinos, resultado)`: retorno delegado para outra funcao.
- TADs envolvidos: Perfil, Origem configurada, Tipo de arquivo, Destino do tipo, Metadados de arquivo, Resultado de backup.

#### `_processar_arquivo_para_destinos_configurados(arquivo, destinos, tipo)`
- Visibilidade: interna.
- Objetivo: Processa arquivo usando destinos com operacao individual.
- Parametros:
    - `arquivo`: TAD Metadados de Arquivo.
    - `destinos`: lista de TADs Destino ou caminhos de destino, conforme contexto.
    - `tipo`: TAD Tipo de Arquivo, com nome, ativo, restricoes e destinos.
- Possiveis retornos:
    - `resultado`: valor calculado pela funcao.
    - `resultado_erro`: valor calculado pela funcao.
- TADs envolvidos: Perfil, Origem configurada, Tipo de arquivo, Destino do tipo, Metadados de arquivo, Resultado de backup.

#### `_processar_copia_para_destinos(arquivo, destinos, resultado)`
- Visibilidade: interna.
- Objetivo: Copia um arquivo para todos os destinos.
- Parametros:
    - `arquivo`: TAD Metadados de Arquivo.
    - `destinos`: lista de TADs Destino ou caminhos de destino, conforme contexto.
    - `resultado`: TAD Resultado geral de backup.
- Possiveis retornos:
    - `resultado`: valor calculado pela funcao.
- TADs envolvidos: Perfil, Origem configurada, Tipo de arquivo, Destino do tipo, Metadados de arquivo, Resultado de backup.

#### `_processar_movimento_para_destinos(arquivo, destinos, resultado)`
- Visibilidade: interna.
- Objetivo: Copia um arquivo para todos os destinos e remove a origem ao final.
- Parametros:
    - `arquivo`: TAD Metadados de Arquivo.
    - `destinos`: lista de TADs Destino ou caminhos de destino, conforme contexto.
    - `resultado`: TAD Resultado geral de backup.
- Possiveis retornos:
    - `resultado`: valor calculado pela funcao.
- TADs envolvidos: Perfil, Origem configurada, Tipo de arquivo, Destino do tipo, Metadados de arquivo, Resultado de backup.

#### `_processar_recorte_para_destinos(arquivo, destinos, resultado)`
- Visibilidade: interna.
- Objetivo: Recorta um arquivo para um destino.
- Parametros:
    - `arquivo`: TAD Metadados de Arquivo.
    - `destinos`: lista de TADs Destino ou caminhos de destino, conforme contexto.
    - `resultado`: TAD Resultado geral de backup.
- Possiveis retornos:
    - `resultado`: valor calculado pela funcao.
- TADs envolvidos: Perfil, Origem configurada, Tipo de arquivo, Destino do tipo, Metadados de arquivo, Resultado de backup.

#### `copiar_arquivo(origem, destino)`
- Visibilidade: publica.
- Objetivo: Copia um arquivo individual para o caminho de destino.
- Parametros:
    - `origem`: TAD Origem Configurada, com caminho, ativo e tipos de arquivo.
    - `destino`: TAD Destino ou caminho final, conforme contexto.
- Possiveis retornos:
    - `OK`: sucesso da operacao.
    - `ERRO_DADOS_INVALIDOS`: entrada com tipo, formato ou valor invalido.
    - `ERRO_ARQUIVO_NAO_ENCONTRADO`: arquivo de origem inexistente ou nao e arquivo.
    - `codigo`: codigo de retorno propagado de chamada interna.
    - `ERRO_FALHA_AO_COPIAR`: falha de sistema ao copiar arquivo.
- TADs envolvidos: Perfil, Origem configurada, Tipo de arquivo, Destino do tipo, Metadados de arquivo, Resultado de backup.

#### `mover_arquivo(origem, destino)`
- Visibilidade: publica.
- Objetivo: Move um arquivo individual para o caminho de destino.
- Parametros:
    - `origem`: TAD Origem Configurada, com caminho, ativo e tipos de arquivo.
    - `destino`: TAD Destino ou caminho final, conforme contexto.
- Possiveis retornos:
    - `OK`: sucesso da operacao.
    - `ERRO_DADOS_INVALIDOS`: entrada com tipo, formato ou valor invalido.
    - `ERRO_ARQUIVO_NAO_ENCONTRADO`: arquivo de origem inexistente ou nao e arquivo.
    - `codigo`: codigo de retorno propagado de chamada interna.
    - `ERRO_FALHA_AO_MOVER`: falha de sistema ao mover/remover arquivo.
- TADs envolvidos: Perfil, Origem configurada, Tipo de arquivo, Destino do tipo, Metadados de arquivo, Resultado de backup.

#### `_gerar_caminho_destino(arquivo, pasta_destino)`
- Visibilidade: interna.
- Objetivo: Gera caminho de destino para um arquivo.
- Parametros:
    - `arquivo`: TAD Metadados de Arquivo.
    - `pasta_destino`: parametro usado pela funcao conforme o contexto do modulo.
- Possiveis retornos:
    - `str(Path(pasta_destino) / nome)`: retorno delegado para outra funcao.
    - `None`: ausencia valida de dado ou falha sem objeto retornavel.
- TADs envolvidos: Perfil, Origem configurada, Tipo de arquivo, Destino do tipo, Metadados de arquivo, Resultado de backup.

#### `_criar_pasta_destino_se_necessario(caminho_destino)`
- Visibilidade: interna.
- Objetivo: Cria a pasta de destino quando necessario.
- Parametros:
    - `caminho_destino`: parametro usado pela funcao conforme o contexto do modulo.
- Possiveis retornos:
    - `OK`: sucesso da operacao.
    - `ERRO_DESTINO_INVALIDO`: destino ausente, vazio ou estruturalmente invalido.
- TADs envolvidos: Perfil, Origem configurada, Tipo de arquivo, Destino do tipo, Metadados de arquivo, Resultado de backup.

### Modulo `file_utils.py`

Resumo: Funcoes auxiliares para arquivos e diretorios.

TADs/obrigacoes do modulo: Metadados de arquivo, Restricoes, Regra de nome.

#### `caminho_existe(caminho)`
- Visibilidade: publica.
- Objetivo: Verifica se um caminho existe no sistema de arquivos.
- Parametros:
    - `caminho`: caminho de arquivo ou pasta no sistema operacional.
- Possiveis retornos:
    - `False`: condicao rejeitada/falsa.
    - `Path(caminho).exists()`: retorno delegado para outra funcao.
- TADs envolvidos: Metadados de arquivo, Restricoes, Regra de nome.

#### `caminho_e_diretorio(caminho)`
- Visibilidade: publica.
- Objetivo: Verifica se um caminho existe e representa uma pasta.
- Parametros:
    - `caminho`: caminho de arquivo ou pasta no sistema operacional.
- Possiveis retornos:
    - `False`: condicao rejeitada/falsa.
    - `Path(caminho).is_dir()`: retorno delegado para outra funcao.
- TADs envolvidos: Metadados de arquivo, Restricoes, Regra de nome.

#### `listar_arquivos_em_origem(origem)`
- Visibilidade: publica.
- Objetivo: Lista apenas arquivos diretamente dentro de uma origem.
- Parametros:
    - `origem`: TAD Origem Configurada, com caminho, ativo e tipos de arquivo.
- Possiveis retornos:
    - `arquivos`: valor calculado pela funcao.
    - `[]`: lista vazia; nenhuma entrada aplicavel.
- TADs envolvidos: Metadados de arquivo, Restricoes, Regra de nome.

#### `listar_arquivos_de_origens(origens)`
- Visibilidade: publica.
- Objetivo: Lista arquivos diretamente dentro de varias origens.
- Parametros:
    - `origens`: colecao de caminhos/origens ou TADs de origem, conforme contexto.
- Possiveis retornos:
    - `arquivos`: valor calculado pela funcao.
    - `[]`: lista vazia; nenhuma entrada aplicavel.
- TADs envolvidos: Metadados de arquivo, Restricoes, Regra de nome.

#### `obter_extensao(caminho)`
- Visibilidade: publica.
- Objetivo: Retorna a extensao de um arquivo em minusculas.
- Parametros:
    - `caminho`: caminho de arquivo ou pasta no sistema operacional.
- Possiveis retornos:
    - `''`: valor calculado pela funcao.
    - `Path(caminho).suffix.lower()`: retorno delegado para outra funcao.
- TADs envolvidos: Metadados de arquivo, Restricoes, Regra de nome.

#### `obter_metadados_arquivo(caminho)`
- Visibilidade: publica.
- Objetivo: Monta o dicionario de metadados de um arquivo real.
- Parametros:
    - `caminho`: caminho de arquivo ou pasta no sistema operacional.
- Possiveis retornos:
    - `{'caminho': str(caminho_path), 'nome': caminho_path.name, 'extensao': obter_extensao(caminho_path), 'tamanho': estatisticas.st_size, 'data_modificacao': estatisticas.st_mtime}`: novo dicionario/TAD montado pela funcao.
    - `None`: ausencia valida de dado ou falha sem objeto retornavel.
- TADs envolvidos: Metadados de arquivo, Restricoes, Regra de nome.

#### `arquivo_e_valido(arquivo)`
- Visibilidade: publica.
- Objetivo: Indica se a entrada possui formato minimo de metadados de arquivo.
- Parametros:
    - `arquivo`: TAD Metadados de Arquivo.
- Possiveis retornos:
    - `isinstance(arquivo, dict)`: booleano calculado pela condicao.
- TADs envolvidos: Metadados de arquivo, Restricoes, Regra de nome.

#### `obter_caminho_arquivo(arquivo)`
- Visibilidade: publica.
- Objetivo: Retorna o caminho completo de um arquivo de metadados.
- Parametros:
    - `arquivo`: TAD Metadados de Arquivo.
- Possiveis retornos:
    - `caminho`: valor calculado pela funcao.
    - `''`: valor calculado pela funcao.
- TADs envolvidos: Metadados de arquivo, Restricoes, Regra de nome.

#### `obter_nome_arquivo(arquivo)`
- Visibilidade: publica.
- Objetivo: Retorna o nome do arquivo de metadados.
- Parametros:
    - `arquivo`: TAD Metadados de Arquivo.
- Possiveis retornos:
    - `Path(obter_caminho_arquivo(arquivo)).name`: retorno delegado para outra funcao.
    - `''`: valor calculado pela funcao.
    - `nome`: valor calculado pela funcao.
- TADs envolvidos: Metadados de arquivo, Restricoes, Regra de nome.

#### `obter_extensao_arquivo(arquivo)`
- Visibilidade: publica.
- Objetivo: Retorna a extensao registrada nos metadados do arquivo.
- Parametros:
    - `arquivo`: TAD Metadados de Arquivo.
- Possiveis retornos:
    - `extensao`: valor calculado pela funcao.
    - `''`: valor calculado pela funcao.
- TADs envolvidos: Metadados de arquivo, Restricoes, Regra de nome.

#### `obter_tamanho_arquivo(arquivo)`
- Visibilidade: publica.
- Objetivo: Retorna o tamanho em bytes registrado nos metadados.
- Parametros:
    - `arquivo`: TAD Metadados de Arquivo.
- Possiveis retornos:
    - `tamanho`: valor calculado pela funcao.
    - `0`: valor calculado pela funcao.
- TADs envolvidos: Metadados de arquivo, Restricoes, Regra de nome.

#### `obter_data_modificacao_arquivo(arquivo)`
- Visibilidade: publica.
- Objetivo: Retorna o timestamp de modificacao registrado nos metadados.
- Parametros:
    - `arquivo`: TAD Metadados de Arquivo.
- Possiveis retornos:
    - `arquivo.get('data_modificacao')`: retorno delegado para outra funcao.
    - `None`: ausencia valida de dado ou falha sem objeto retornavel.
- TADs envolvidos: Metadados de arquivo, Restricoes, Regra de nome.

#### `obter_nome_tipo_arquivo(arquivo)`
- Visibilidade: publica.
- Objetivo: Retorna o nome do tipo associado aos metadados do arquivo.
- Parametros:
    - `arquivo`: TAD Metadados de Arquivo.
- Possiveis retornos:
    - `nome`: valor calculado pela funcao.
    - `''`: valor calculado pela funcao.
- TADs envolvidos: Metadados de arquivo, Restricoes, Regra de nome.

#### `associar_tipo_ao_arquivo(arquivo, tipo_id, tipo_nome)`
- Visibilidade: publica.
- Objetivo: Associa informacoes de tipo ao dicionario de metadados do arquivo.
- Parametros:
    - `arquivo`: TAD Metadados de Arquivo.
    - `tipo_id`: identificador unico do tipo de arquivo.
    - `tipo_nome`: nome do tipo associado ao arquivo ou exibido na UI.
- Possiveis retornos:
    - `arquivo`: valor calculado pela funcao.
    - `None`: ausencia valida de dado ou falha sem objeto retornavel.
- TADs envolvidos: Metadados de arquivo, Restricoes, Regra de nome.

#### `associar_origem_ao_arquivo(arquivo, origem)`
- Visibilidade: publica.
- Objetivo: Registra a origem usada na pre-visualizacao do arquivo.
- Parametros:
    - `arquivo`: TAD Metadados de Arquivo.
    - `origem`: TAD Origem Configurada, com caminho, ativo e tipos de arquivo.
- Possiveis retornos:
    - `arquivo`: valor calculado pela funcao.
    - `None`: ausencia valida de dado ou falha sem objeto retornavel.
- TADs envolvidos: Metadados de arquivo, Restricoes, Regra de nome.

#### `iniciar_tipos_incluidos_arquivo(arquivo)`
- Visibilidade: publica.
- Objetivo: Inicializa a lista de tipos incluidos na pre-visualizacao.
- Parametros:
    - `arquivo`: TAD Metadados de Arquivo.
- Possiveis retornos:
    - `arquivo`: valor calculado pela funcao.
    - `None`: ausencia valida de dado ou falha sem objeto retornavel.
- TADs envolvidos: Metadados de arquivo, Restricoes, Regra de nome.

#### `adicionar_tipo_incluido_arquivo(arquivo, tipo_nome)`
- Visibilidade: publica.
- Objetivo: Adiciona um tipo aprovado na pre-visualizacao do arquivo.
- Parametros:
    - `arquivo`: TAD Metadados de Arquivo.
    - `tipo_nome`: nome do tipo associado ao arquivo ou exibido na UI.
- Possiveis retornos:
    - `arquivo`: valor calculado pela funcao.
    - `None`: ausencia valida de dado ou falha sem objeto retornavel.
- TADs envolvidos: Metadados de arquivo, Restricoes, Regra de nome.

#### `arquivo_possui_tipo_incluido(arquivo)`
- Visibilidade: publica.
- Objetivo: Indica se a pre-visualizacao marcou algum tipo incluido.
- Parametros:
    - `arquivo`: TAD Metadados de Arquivo.
- Possiveis retornos:
    - `bool(arquivo.get('tipos_incluidos', []))`: booleano calculado pela condicao.
    - `False`: condicao rejeitada/falsa.
- TADs envolvidos: Metadados de arquivo, Restricoes, Regra de nome.

#### `arquivo_atende_restricoes(arquivo, restricoes)`
- Visibilidade: publica.
- Objetivo: Verifica se um arquivo atende a todas as restricoes configuradas.
- Parametros:
    - `arquivo`: TAD Metadados de Arquivo.
    - `restricoes`: TAD Restricoes usado para filtrar arquivos.
- Possiveis retornos:
    - `_atende_restricao_extensao(arquivo, restricoes) and _atende_restricao_nome(arquivo, restricoes) and _atende_restricao_tamanho(arquivo, restricoes) and _atende_restricao_data_modificacao(arquivo, restricoes)`: retorno delegado para outra funcao.
    - `False`: condicao rejeitada/falsa.
- TADs envolvidos: Metadados de arquivo, Restricoes, Regra de nome.

#### `_atende_restricao_extensao(arquivo, restricoes)`
- Visibilidade: interna.
- Objetivo: Verifica filtro por extensao.
- Parametros:
    - `arquivo`: TAD Metadados de Arquivo.
    - `restricoes`: TAD Restricoes usado para filtrar arquivos.
- Possiveis retornos:
    - `extensao_arquivo.strip().lower() in extensoes_normalizadas`: retorno delegado para outra funcao.
    - `True`: condicao aceita/verdadeira.
    - `False`: condicao rejeitada/falsa.
- TADs envolvidos: Metadados de arquivo, Restricoes, Regra de nome.

#### `_atende_restricao_nome(arquivo, restricoes)`
- Visibilidade: interna.
- Objetivo: Verifica filtros por nome do arquivo.
- Parametros:
    - `arquivo`: TAD Metadados de Arquivo.
    - `restricoes`: TAD Restricoes usado para filtrar arquivos.
- Possiveis retornos:
    - `True`: condicao aceita/verdadeira.
    - `False`: condicao rejeitada/falsa.
- TADs envolvidos: Metadados de arquivo, Restricoes, Regra de nome.

#### `_normalizar_regras_nome(restricoes)`
- Visibilidade: interna.
- Objetivo: Normaliza regras novas de nome, ignorando entradas invalidas.
- Parametros:
    - `restricoes`: TAD Restricoes usado para filtrar arquivos.
- Possiveis retornos:
    - `normalizadas`: valor calculado pela funcao.
- TADs envolvidos: Metadados de arquivo, Restricoes, Regra de nome.

#### `_nome_atende_regra(nome, regra)`
- Visibilidade: interna.
- Objetivo: Indica se o nome atende uma regra normalizada.
- Parametros:
    - `nome`: nome informado pelo usuario ou nome interno do TAD.
    - `regra`: parametro usado pela funcao conforme o contexto do modulo.
- Possiveis retornos:
    - `valor in nome_normalizado`: valor calculado pela funcao.
    - `True`: condicao aceita/verdadeira.
    - `nome_normalizado == valor`: valor calculado pela funcao.
- TADs envolvidos: Metadados de arquivo, Restricoes, Regra de nome.

#### `_atende_restricao_tamanho(arquivo, restricoes)`
- Visibilidade: interna.
- Objetivo: Verifica filtros por tamanho minimo e maximo.
- Parametros:
    - `arquivo`: TAD Metadados de Arquivo.
    - `restricoes`: TAD Restricoes usado para filtrar arquivos.
- Possiveis retornos:
    - `True`: condicao aceita/verdadeira.
    - `False`: condicao rejeitada/falsa.
- TADs envolvidos: Metadados de arquivo, Restricoes, Regra de nome.

#### `_atende_restricao_data_modificacao(arquivo, restricoes)`
- Visibilidade: interna.
- Objetivo: Verifica filtros por data de modificacao.
- Parametros:
    - `arquivo`: TAD Metadados de Arquivo.
    - `restricoes`: TAD Restricoes usado para filtrar arquivos.
- Possiveis retornos:
    - `True`: condicao aceita/verdadeira.
    - `False`: condicao rejeitada/falsa.
- TADs envolvidos: Metadados de arquivo, Restricoes, Regra de nome.

#### `_converter_data_restricao_para_timestamp(valor)`
- Visibilidade: interna.
- Objetivo: Converte data de restricao em timestamp ou None quando vazia.
- Parametros:
    - `valor`: valor recebido, validado ou escrito em widget/TAD.
- Possiveis retornos:
    - `None`: ausencia valida de dado ou falha sem objeto retornavel.
    - `float(valor)`: retorno delegado para outra funcao.
    - `datetime.fromisoformat(valor).timestamp()`: retorno delegado para outra funcao.
- TADs envolvidos: Metadados de arquivo, Restricoes, Regra de nome.

#### `verificar_permissao_leitura(caminho)`
- Visibilidade: publica.
- Objetivo: Verifica permissao de leitura em um caminho.
- Parametros:
    - `caminho`: caminho de arquivo ou pasta no sistema operacional.
- Possiveis retornos:
    - `False`: condicao rejeitada/falsa.
    - `os.access(caminho, os.R_OK)`: retorno delegado para outra funcao.
- TADs envolvidos: Metadados de arquivo, Restricoes, Regra de nome.

#### `verificar_permissao_escrita(caminho)`
- Visibilidade: publica.
- Objetivo: Verifica permissao de escrita em um caminho.
- Parametros:
    - `caminho`: caminho de arquivo ou pasta no sistema operacional.
- Possiveis retornos:
    - `False`: condicao rejeitada/falsa.
    - `os.access(caminho, os.W_OK)`: retorno delegado para outra funcao.
- TADs envolvidos: Metadados de arquivo, Restricoes, Regra de nome.

## Pasta `backupmanager/infra`

### Modulo `storage.py`

Resumo: Funcoes de armazenamento em arquivos JSON.

TADs/obrigacoes do modulo: Persistencia JSON, Perfil, Configuracoes.

#### `_garantir_pasta_data()`
- Visibilidade: interna.
- Objetivo: Garante que a pasta data exista.
- Parametros:
    - nenhum parametro.
- Possiveis retornos:
    - `OK`: sucesso da operacao.
    - `ERRO_SEM_PERMISSAO`: falha de permissao ou I/O na persistencia.
- TADs envolvidos: Persistencia JSON, Perfil, Configuracoes.

#### `_salvar_json(caminho, dados)`
- Visibilidade: interna.
- Objetivo: Salva dados em um arquivo JSON.
- Parametros:
    - `caminho`: caminho de arquivo ou pasta no sistema operacional.
    - `dados`: parametro usado pela funcao conforme o contexto do modulo.
- Possiveis retornos:
    - `OK`: sucesso da operacao.
    - `codigo`: codigo de retorno propagado de chamada interna.
    - `ERRO_DADOS_INVALIDOS`: entrada com tipo, formato ou valor invalido.
    - `ERRO_SEM_PERMISSAO`: falha de permissao ou I/O na persistencia.
- TADs envolvidos: Persistencia JSON, Perfil, Configuracoes.

#### `_carregar_json(caminho, valor_padrao)`
- Visibilidade: interna.
- Objetivo: Carrega dados de um JSON ou retorna valor padrao se ele nao existir.
- Parametros:
    - `caminho`: caminho de arquivo ou pasta no sistema operacional.
    - `valor_padrao`: parametro usado pela funcao conforme o contexto do modulo.
- Possiveis retornos:
    - `(OK, valor_padrao)`: tupla de retorno; normalmente combina codigo e dado/resultado.
    - `(OK, json.load(arquivo))`: tupla de retorno; normalmente combina codigo e dado/resultado.
    - `(ERRO_JSON_CORROMPIDO, valor_padrao)`: tupla de retorno; normalmente combina codigo e dado/resultado.
    - `(ERRO_SEM_PERMISSAO, valor_padrao)`: tupla de retorno; normalmente combina codigo e dado/resultado.
- TADs envolvidos: Persistencia JSON, Perfil, Configuracoes.

#### `salvar_perfis(perfis)`
- Visibilidade: publica.
- Objetivo: Salva a lista de perfis no arquivo JSON oficial.
- Parametros:
    - `perfis`: colecao em memoria de TADs Perfil.
- Possiveis retornos:
    - `_salvar_json(_PERFIS_PATH, perfis)`: retorno delegado para outra funcao.
- TADs envolvidos: Persistencia JSON, Perfil, Configuracoes.

#### `carregar_perfis()`
- Visibilidade: publica.
- Objetivo: Carrega a lista de perfis do arquivo JSON oficial.
- Parametros:
    - nenhum parametro.
- Possiveis retornos:
    - `_carregar_json(_PERFIS_PATH, [])`: retorno delegado para outra funcao.
- TADs envolvidos: Persistencia JSON, Perfil, Configuracoes.

#### `salvar_configuracoes(config)`
- Visibilidade: publica.
- Objetivo: Salva as configuracoes gerais da aplicacao.
- Parametros:
    - `config`: TAD Configuracoes gerais da aplicacao.
- Possiveis retornos:
    - `_salvar_json(_CONFIG_PATH, config)`: retorno delegado para outra funcao.
- TADs envolvidos: Persistencia JSON, Perfil, Configuracoes.

#### `carregar_configuracoes()`
- Visibilidade: publica.
- Objetivo: Carrega as configuracoes gerais da aplicacao.
- Parametros:
    - nenhum parametro.
- Possiveis retornos:
    - `_carregar_json(_CONFIG_PATH, {})`: retorno delegado para outra funcao.
- TADs envolvidos: Persistencia JSON, Perfil, Configuracoes.

#### `criar_arquivos_padrao()`
- Visibilidade: publica.
- Objetivo: Garante a pasta `data` e os arquivos JSON essenciais.
- Parametros:
    - nenhum parametro.
- Possiveis retornos:
    - `OK`: sucesso da operacao.
    - `codigo`: codigo de retorno propagado de chamada interna.
- TADs envolvidos: Persistencia JSON, Perfil, Configuracoes.

## Pasta `backupmanager`

### Modulo `main.py`

Resumo: Ponto de entrada do BackupManager.

TADs/obrigacoes do modulo: Entrada da aplicacao.

#### `main()`
- Visibilidade: publica.
- Objetivo: Ponto de entrada executavel da aplicacao.
- Parametros:
    - nenhum parametro.
- Possiveis retornos:
    - retorno implicito `None`: funcao usada por assercao/callback ou efeito colateral.
- TADs envolvidos: Entrada da aplicacao.

### Modulo `return_codes.py`

Resumo: Codigos de retorno padronizados do BackupManager.

TADs/obrigacoes do modulo: Codigos de retorno.

#### `obter_mensagem(codigo)`
- Visibilidade: publica.
- Objetivo: Retorna a mensagem de usuario associada a um codigo de retorno.
- Parametros:
    - `codigo`: codigo de retorno de return_codes.py.
- Possiveis retornos:
    - `_MENSAGENS.get(codigo, 'Codigo de retorno desconhecido.')`: retorno delegado para outra funcao.
- TADs envolvidos: Codigos de retorno.

## Pasta `backupmanager/ui`

### Modulo `actions.py`

Resumo: Acoes principais, sincronizacao e mensagens da interface.

TADs/obrigacoes do modulo: Estado da interface, Perfil, Resultado de backup.

#### `criar_area_botoes(janela, estado_interface)`
- Visibilidade: publica.
- Objetivo: Cria os botoes globais do cabecalho da interface.
- Parametros:
    - `janela`: janela Tk/CustomTkinter.
    - `estado_interface`: TAD local da UI com widgets, selecoes e dados editados em memoria.
- Possiveis retornos:
    - `frame`: valor calculado pela funcao.
- TADs envolvidos: Estado da interface, Perfil, Resultado de backup.

#### `executar_backup_interface(estado_interface)`
- Visibilidade: publica.
- Objetivo: Inicia a execucao de backup do perfil selecionado pela interface.
- Parametros:
    - `estado_interface`: TAD local da UI com widgets, selecoes e dados editados em memoria.
- Possiveis retornos:
    - `OK`: sucesso da operacao.
    - `codigo_salvar`: valor calculado pela funcao.
    - `ERRO_DADOS_INVALIDOS`: entrada com tipo, formato ou valor invalido.
- TADs envolvidos: Estado da interface, Perfil, Resultado de backup.

#### `sincronizar_perfil_atual_interface(estado_interface, exibir_erros)`
- Visibilidade: publica.
- Objetivo: Sincroniza o formulario atual com o perfil em memoria.
- Parametros:
    - `estado_interface`: TAD local da UI com widgets, selecoes e dados editados em memoria.
    - `exibir_erros`: booleano que decide se a UI mostra mensagens de validacao.
- Possiveis retornos:
    - `(codigo, perfil)`: tupla de retorno; normalmente combina codigo e dado/resultado.
    - `(ERRO_DADOS_INVALIDOS, None)`: tupla de retorno; normalmente combina codigo e dado/resultado.
- TADs envolvidos: Estado da interface, Perfil, Resultado de backup.

#### `preencher_formulario_com_perfil(estado_interface, perfil)`
- Visibilidade: publica.
- Objetivo: Carrega os dados de um perfil nos widgets da interface.
- Parametros:
    - `estado_interface`: TAD local da UI com widgets, selecoes e dados editados em memoria.
    - `perfil`: TAD Perfil, dicionario persistido com id, nome, ativo e origens configuradas.
- Possiveis retornos:
    - `perfil`: valor calculado pela funcao.
- TADs envolvidos: Estado da interface, Perfil, Resultado de backup.

#### `limpar_formulario(estado_interface)`
- Visibilidade: publica.
- Objetivo: Limpa todos os campos visuais ligados ao perfil selecionado.
- Parametros:
    - `estado_interface`: TAD local da UI com widgets, selecoes e dados editados em memoria.
- Possiveis retornos:
    - `OK`: sucesso da operacao.
- TADs envolvidos: Estado da interface, Perfil, Resultado de backup.

#### `mostrar_mensagem_resultado(codigo)`
- Visibilidade: publica.
- Objetivo: Mostra ao usuario a mensagem associada a um codigo de retorno.
- Parametros:
    - `codigo`: codigo de retorno de return_codes.py.
- Possiveis retornos:
    - `codigo`: codigo de retorno propagado de chamada interna.
- TADs envolvidos: Estado da interface, Perfil, Resultado de backup.

#### `_executar_backup_em_thread(estado_interface, perfil_id)`
- Visibilidade: interna.
- Objetivo: Executa backup fora da thread da interface.
- Parametros:
    - `estado_interface`: TAD local da UI com widgets, selecoes e dados editados em memoria.
    - `perfil_id`: identificador unico de um perfil.
- Possiveis retornos:
    - `None`: ausencia valida de dado ou falha sem objeto retornavel.
- TADs envolvidos: Estado da interface, Perfil, Resultado de backup.

#### `_finalizar_backup_interface(estado_interface, codigo, resultado, erro)`
- Visibilidade: interna.
- Objetivo: Atualiza a interface apos o termino do backup.
- Parametros:
    - `estado_interface`: TAD local da UI com widgets, selecoes e dados editados em memoria.
    - `codigo`: codigo de retorno de return_codes.py.
    - `resultado`: TAD Resultado geral de backup.
    - `erro`: erro capturado ou registro de erro.
- Possiveis retornos:
    - `codigo`: codigo de retorno propagado de chamada interna.
    - `ERRO_DADOS_INVALIDOS`: entrada com tipo, formato ou valor invalido.
- TADs envolvidos: Estado da interface, Perfil, Resultado de backup.

#### `_definir_estado_botao_backup(estado_interface, habilitado)`
- Visibilidade: interna.
- Objetivo: Habilita ou desabilita o botao de backup.
- Parametros:
    - `estado_interface`: TAD local da UI com widgets, selecoes e dados editados em memoria.
    - `habilitado`: booleano que controla estado visual habilitado/desabilitado.
- Possiveis retornos:
    - `OK`: sucesso da operacao.
- TADs envolvidos: Estado da interface, Perfil, Resultado de backup.

#### `_obter_dados_formulario(estado_interface)`
- Visibilidade: interna.
- Objetivo: Coleta dados do formulario para um dicionario de perfil.
- Parametros:
    - `estado_interface`: TAD local da UI com widgets, selecoes e dados editados em memoria.
- Possiveis retornos:
    - `{'id': perfil_id, 'nome': estado_interface['entrada_nome'].get(), 'origens_configuradas': estado_interface['origens_configuradas'], 'ativo': estado_interface['ativo_var'].get()}`: novo dicionario/TAD montado pela funcao.
    - `None`: ausencia valida de dado ou falha sem objeto retornavel.
- TADs envolvidos: Estado da interface, Perfil, Resultado de backup.

#### `_montar_origens_configuradas_para_interface(perfil)`
- Visibilidade: interna.
- Objetivo: Copia as origens configuradas do perfil para uso seguro na interface.
- Parametros:
    - `perfil`: TAD Perfil, dicionario persistido com id, nome, ativo e origens configuradas.
- Possiveis retornos:
    - `[]`: lista vazia; nenhuma entrada aplicavel.
    - `_copiar_lista_dicionarios(origens_configuradas)`: retorno delegado para outra funcao.
- TADs envolvidos: Estado da interface, Perfil, Resultado de backup.

#### `_copiar_lista_dicionarios(lista)`
- Visibilidade: interna.
- Objetivo: Copia lista simples de dicionarios aninhados.
- Parametros:
    - `lista`: listbox ou lista Python, conforme contexto.
- Possiveis retornos:
    - `copia`: valor calculado pela funcao.
- TADs envolvidos: Estado da interface, Perfil, Resultado de backup.

#### `_preencher_lista(lista, itens)`
- Visibilidade: interna.
- Objetivo: Substitui os itens de uma listbox.
- Parametros:
    - `lista`: listbox ou lista Python, conforme contexto.
    - `itens`: itens a preencher em uma lista visual.
- Possiveis retornos:
    - `OK`: sucesso da operacao.
- TADs envolvidos: Estado da interface, Perfil, Resultado de backup.

#### `_preencher_entry(entrada, valor)`
- Visibilidade: interna.
- Objetivo: Substitui o conteudo de um campo de texto.
- Parametros:
    - `entrada`: campo de texto da interface.
    - `valor`: valor recebido, validado ou escrito em widget/TAD.
- Possiveis retornos:
    - `OK`: sucesso da operacao.
- TADs envolvidos: Estado da interface, Perfil, Resultado de backup.

#### `_mostrar_erro_validacao_formulario(estado_interface)`
- Visibilidade: interna.
- Objetivo: Mostra mensagem especifica para dados invalidos do formulario.
- Parametros:
    - `estado_interface`: TAD local da UI com widgets, selecoes e dados editados em memoria.
- Possiveis retornos:
    - `ERRO_DADOS_INVALIDOS`: entrada com tipo, formato ou valor invalido.
- TADs envolvidos: Estado da interface, Perfil, Resultado de backup.

#### `_existe_conflito_operacao_interface(estado_interface)`
- Visibilidade: interna.
- Objetivo: Verifica conflito visual de mover/recortar em multiplos destinos.
- Parametros:
    - `estado_interface`: TAD local da UI com widgets, selecoes e dados editados em memoria.
- Possiveis retornos:
    - `False`: condicao rejeitada/falsa.
    - `True`: condicao aceita/verdadeira.
- TADs envolvidos: Estado da interface, Perfil, Resultado de backup.

### Modulo `backup_flow.py`

Resumo: Fluxo visual origem -> tipo -> destino da interface.

TADs/obrigacoes do modulo: Estado da interface, Origem configurada, Tipo de arquivo, Destino do tipo, Restricoes.

#### `criar_area_origens_destinos(janela, estado_interface)`
- Visibilidade: publica.
- Objetivo: Cria a area visual do fluxo origem -> tipo -> destino.
- Parametros:
    - `janela`: janela Tk/CustomTkinter.
    - `estado_interface`: TAD local da UI com widgets, selecoes e dados editados em memoria.
- Possiveis retornos:
    - `frame`: valor calculado pela funcao.
- TADs envolvidos: Estado da interface, Origem configurada, Tipo de arquivo, Destino do tipo, Restricoes.

#### `_criar_coluna_origens(container, estado_interface)`
- Visibilidade: interna.
- Objetivo: Cria a coluna de origens do fluxo de backup.
- Parametros:
    - `container`: widget pai onde componentes visuais serao criados.
    - `estado_interface`: TAD local da UI com widgets, selecoes e dados editados em memoria.
- Possiveis retornos:
    - `coluna_origens`: valor calculado pela funcao.
- TADs envolvidos: Estado da interface, Origem configurada, Tipo de arquivo, Destino do tipo, Restricoes.

#### `_criar_coluna_tipos(container, estado_interface)`
- Visibilidade: interna.
- Objetivo: Cria a coluna de tipos da origem selecionada.
- Parametros:
    - `container`: widget pai onde componentes visuais serao criados.
    - `estado_interface`: TAD local da UI com widgets, selecoes e dados editados em memoria.
- Possiveis retornos:
    - `coluna_tipos`: valor calculado pela funcao.
- TADs envolvidos: Estado da interface, Origem configurada, Tipo de arquivo, Destino do tipo, Restricoes.

#### `_criar_coluna_destinos(container, estado_interface)`
- Visibilidade: interna.
- Objetivo: Cria a coluna de destinos e operacao do tipo selecionado.
- Parametros:
    - `container`: widget pai onde componentes visuais serao criados.
    - `estado_interface`: TAD local da UI com widgets, selecoes e dados editados em memoria.
- Possiveis retornos:
    - `coluna_destinos`: valor calculado pela funcao.
- TADs envolvidos: Estado da interface, Origem configurada, Tipo de arquivo, Destino do tipo, Restricoes.

#### `_adicionar_origem_interface(estado_interface)`
- Visibilidade: interna.
- Objetivo: Adiciona uma pasta de origem na lista visual.
- Parametros:
    - `estado_interface`: TAD local da UI com widgets, selecoes e dados editados em memoria.
- Possiveis retornos:
    - `OK`: sucesso da operacao.
- TADs envolvidos: Estado da interface, Origem configurada, Tipo de arquivo, Destino do tipo, Restricoes.

#### `_adicionar_destino_interface(estado_interface)`
- Visibilidade: interna.
- Objetivo: Adiciona uma pasta de destino ao tipo selecionado.
- Parametros:
    - `estado_interface`: TAD local da UI com widgets, selecoes e dados editados em memoria.
- Possiveis retornos:
    - `OK`: sucesso da operacao.
    - `ERRO_DADOS_INVALIDOS`: entrada com tipo, formato ou valor invalido.
- TADs envolvidos: Estado da interface, Origem configurada, Tipo de arquivo, Destino do tipo, Restricoes.

#### `_adicionar_tipo_arquivo_interface(estado_interface)`
- Visibilidade: interna.
- Objetivo: Adiciona tipo de arquivo a origem selecionada.
- Parametros:
    - `estado_interface`: TAD local da UI com widgets, selecoes e dados editados em memoria.
- Possiveis retornos:
    - `OK`: sucesso da operacao.
    - `ERRO_DADOS_INVALIDOS`: entrada com tipo, formato ou valor invalido.
- TADs envolvidos: Estado da interface, Origem configurada, Tipo de arquivo, Destino do tipo, Restricoes.

#### `_remover_origem_configurada_interface(estado_interface)`
- Visibilidade: interna.
- Objetivo: Remove origem configurada selecionada.
- Parametros:
    - `estado_interface`: TAD local da UI com widgets, selecoes e dados editados em memoria.
- Possiveis retornos:
    - `OK`: sucesso da operacao.
    - `ERRO_DADOS_INVALIDOS`: entrada com tipo, formato ou valor invalido.
- TADs envolvidos: Estado da interface, Origem configurada, Tipo de arquivo, Destino do tipo, Restricoes.

#### `_remover_tipo_arquivo_interface(estado_interface)`
- Visibilidade: interna.
- Objetivo: Remove tipo de arquivo selecionado.
- Parametros:
    - `estado_interface`: TAD local da UI com widgets, selecoes e dados editados em memoria.
- Possiveis retornos:
    - `OK`: sucesso da operacao.
    - `ERRO_DADOS_INVALIDOS`: entrada com tipo, formato ou valor invalido.
- TADs envolvidos: Estado da interface, Origem configurada, Tipo de arquivo, Destino do tipo, Restricoes.

#### `_renomear_tipo_arquivo_interface(estado_interface)`
- Visibilidade: interna.
- Objetivo: Renomeia o tipo selecionado por dialogo de texto.
- Parametros:
    - `estado_interface`: TAD local da UI com widgets, selecoes e dados editados em memoria.
- Possiveis retornos:
    - `OK`: sucesso da operacao ou cancelamento do dialogo sem alteracao.
    - `ERRO_DADOS_INVALIDOS`: nenhum tipo selecionado ou nome vazio/invalido.
- TADs envolvidos: Estado da interface, Tipo de arquivo.

#### `_mostrar_menu_tipos_interface(evento, estado_interface, menu)`
- Visibilidade: interna.
- Objetivo: Mostra menu de contexto para o tipo clicado.
- Parametros:
    - `evento`: evento Tk do clique com posicao local e global do mouse.
    - `estado_interface`: TAD local da UI com widgets, selecoes e dados editados em memoria.
    - `menu`: menu Tk com acoes de renomear e excluir tipo.
- Possiveis retornos:
    - `OK`: menu exibido apos selecionar o item clicado.
    - `ERRO_DADOS_INVALIDOS`: clique fora de item valido.
- TADs envolvidos: Estado da interface, Tipo de arquivo.

#### `_remover_destino_tipo_interface(estado_interface)`
- Visibilidade: interna.
- Objetivo: Remove destino selecionado do tipo atual.
- Parametros:
    - `estado_interface`: TAD local da UI com widgets, selecoes e dados editados em memoria.
- Possiveis retornos:
    - `OK`: sucesso da operacao.
    - `ERRO_DADOS_INVALIDOS`: entrada com tipo, formato ou valor invalido.
- TADs envolvidos: Estado da interface, Origem configurada, Tipo de arquivo, Destino do tipo, Restricoes.

#### `_alternar_origem_ativa_interface(estado_interface)`
- Visibilidade: interna.
- Objetivo: Liga ou desliga a origem selecionada.
- Parametros:
    - `estado_interface`: TAD local da UI com widgets, selecoes e dados editados em memoria.
- Possiveis retornos:
    - `OK`: sucesso da operacao.
    - `ERRO_DADOS_INVALIDOS`: entrada com tipo, formato ou valor invalido.
- TADs envolvidos: Estado da interface, Origem configurada, Tipo de arquivo, Destino do tipo, Restricoes.

#### `_alternar_tipo_ativo_interface(estado_interface)`
- Visibilidade: interna.
- Objetivo: Liga ou desliga o tipo selecionado.
- Parametros:
    - `estado_interface`: TAD local da UI com widgets, selecoes e dados editados em memoria.
- Possiveis retornos:
    - `OK`: sucesso da operacao.
    - `ERRO_DADOS_INVALIDOS`: entrada com tipo, formato ou valor invalido.
- TADs envolvidos: Estado da interface, Origem configurada, Tipo de arquivo, Destino do tipo, Restricoes.

#### `_abrir_pasta_selecionada(lista, tipo)`
- Visibilidade: interna.
- Objetivo: Abre a pasta selecionada em uma listbox.
- Parametros:
    - `lista`: listbox ou lista Python, conforme contexto.
    - `tipo`: TAD Tipo de Arquivo, com nome, ativo, restricoes e destinos.
- Possiveis retornos:
    - `_abrir_pasta_por_caminho(caminho, tipo)`: retorno delegado para outra funcao.
    - `ERRO_DADOS_INVALIDOS`: entrada com tipo, formato ou valor invalido.
- TADs envolvidos: Estado da interface, Origem configurada, Tipo de arquivo, Destino do tipo, Restricoes.

#### `_abrir_pasta_por_caminho(caminho, tipo)`
- Visibilidade: interna.
- Objetivo: Abre uma pasta pelo caminho informado.
- Parametros:
    - `caminho`: caminho de arquivo ou pasta no sistema operacional.
    - `tipo`: TAD Tipo de Arquivo, com nome, ativo, restricoes e destinos.
- Possiveis retornos:
    - `OK`: sucesso da operacao.
    - `ERRO_DADOS_INVALIDOS`: entrada com tipo, formato ou valor invalido.
- TADs envolvidos: Estado da interface, Origem configurada, Tipo de arquivo, Destino do tipo, Restricoes.

#### `_abrir_origem_selecionada_interface(estado_interface)`
- Visibilidade: interna.
- Objetivo: Abre a pasta da origem selecionada.
- Parametros:
    - `estado_interface`: TAD local da UI com widgets, selecoes e dados editados em memoria.
- Possiveis retornos:
    - `_abrir_pasta_por_caminho(perfil_manager.obter_caminho_origem(origem), 'origem')`: retorno delegado para outra funcao.
    - `ERRO_DADOS_INVALIDOS`: entrada com tipo, formato ou valor invalido.
- TADs envolvidos: Estado da interface, Origem configurada, Tipo de arquivo, Destino do tipo, Restricoes.

#### `_abrir_destino_selecionado_interface(estado_interface)`
- Visibilidade: interna.
- Objetivo: Abre a pasta do destino selecionado.
- Parametros:
    - `estado_interface`: TAD local da UI com widgets, selecoes e dados editados em memoria.
- Possiveis retornos:
    - `_abrir_pasta_por_caminho(perfil_manager.obter_caminho_destino(destino), 'destino')`: retorno delegado para outra funcao.
    - `ERRO_DADOS_INVALIDOS`: entrada com tipo, formato ou valor invalido.
- TADs envolvidos: Estado da interface, Origem configurada, Tipo de arquivo, Destino do tipo, Restricoes.

#### `atualizar_lista_origens_configuradas(estado_interface)`
- Visibilidade: publica.
- Objetivo: Atualiza a listbox de origens configuradas no estado visual.
- Parametros:
    - `estado_interface`: TAD local da UI com widgets, selecoes e dados editados em memoria.
- Possiveis retornos:
    - `OK`: sucesso da operacao.
- TADs envolvidos: Estado da interface, Origem configurada, Tipo de arquivo, Destino do tipo, Restricoes.

#### `_atualizar_lista_tipos_origem(estado_interface)`
- Visibilidade: interna.
- Objetivo: Atualiza tipos da origem selecionada.
- Parametros:
    - `estado_interface`: TAD local da UI com widgets, selecoes e dados editados em memoria.
- Possiveis retornos:
    - `OK`: sucesso da operacao.
    - `ERRO_DADOS_INVALIDOS`: entrada com tipo, formato ou valor invalido.
- TADs envolvidos: Estado da interface, Origem configurada, Tipo de arquivo, Destino do tipo, Restricoes.

#### `_atualizar_lista_destinos_tipo(estado_interface)`
- Visibilidade: interna.
- Objetivo: Atualiza destinos do tipo selecionado.
- Parametros:
    - `estado_interface`: TAD local da UI com widgets, selecoes e dados editados em memoria.
- Possiveis retornos:
    - `OK`: sucesso da operacao.
    - `ERRO_DADOS_INVALIDOS`: entrada com tipo, formato ou valor invalido.
- TADs envolvidos: Estado da interface, Origem configurada, Tipo de arquivo, Destino do tipo, Restricoes.

#### `_selecionar_destino_tipo_interface(estado_interface)`
- Visibilidade: interna.
- Objetivo: Seleciona destino do tipo atual e carrega sua operacao.
- Parametros:
    - `estado_interface`: TAD local da UI com widgets, selecoes e dados editados em memoria.
- Possiveis retornos:
    - `OK`: sucesso da operacao.
    - `ERRO_DADOS_INVALIDOS`: entrada com tipo, formato ou valor invalido.
- TADs envolvidos: Estado da interface, Origem configurada, Tipo de arquivo, Destino do tipo, Restricoes.

#### `_selecionar_destino_por_indice(estado_interface, indice)`
- Visibilidade: interna.
- Objetivo: Seleciona destino visualmente por indice.
- Parametros:
    - `estado_interface`: TAD local da UI com widgets, selecoes e dados editados em memoria.
    - `indice`: posicao selecionada em lista/listbox.
- Possiveis retornos:
    - `_selecionar_destino_tipo_interface(estado_interface)`: retorno delegado para outra funcao.
    - `ERRO_DADOS_INVALIDOS`: entrada com tipo, formato ou valor invalido.
- TADs envolvidos: Estado da interface, Origem configurada, Tipo de arquivo, Destino do tipo, Restricoes.

#### `_obter_destino_selecionado(estado_interface)`
- Visibilidade: interna.
- Objetivo: Retorna destino selecionado do tipo atual.
- Parametros:
    - `estado_interface`: TAD local da UI com widgets, selecoes e dados editados em memoria.
- Possiveis retornos:
    - `destinos[indice]`: valor calculado pela funcao.
    - `None`: ausencia valida de dado ou falha sem objeto retornavel.
- TADs envolvidos: Estado da interface, Origem configurada, Tipo de arquivo, Destino do tipo, Restricoes.

#### `_atualizar_operacao_destino_interface(estado_interface)`
- Visibilidade: interna.
- Objetivo: Atualiza operacao do destino selecionado.
- Parametros:
    - `estado_interface`: TAD local da UI com widgets, selecoes e dados editados em memoria.
- Possiveis retornos:
    - `OK`: sucesso da operacao.
- TADs envolvidos: Estado da interface, Origem configurada, Tipo de arquivo, Destino do tipo, Restricoes.

#### `_selecionar_origem_configurada_interface(estado_interface)`
- Visibilidade: interna.
- Objetivo: Seleciona origem e atualiza tipos relacionados.
- Parametros:
    - `estado_interface`: TAD local da UI com widgets, selecoes e dados editados em memoria.
- Possiveis retornos:
    - `OK`: sucesso da operacao.
    - `ERRO_DADOS_INVALIDOS`: entrada com tipo, formato ou valor invalido.
- TADs envolvidos: Estado da interface, Origem configurada, Tipo de arquivo, Destino do tipo, Restricoes.

#### `_selecionar_tipo_arquivo_interface(estado_interface)`
- Visibilidade: interna.
- Objetivo: Seleciona tipo e carrega filtros e destinos.
- Parametros:
    - `estado_interface`: TAD local da UI com widgets, selecoes e dados editados em memoria.
- Possiveis retornos:
    - `OK`: sucesso da operacao.
    - `ERRO_DADOS_INVALIDOS`: entrada com tipo, formato ou valor invalido.
- TADs envolvidos: Estado da interface, Origem configurada, Tipo de arquivo, Destino do tipo, Restricoes.

#### `selecionar_origem_por_indice(estado_interface, indice)`
- Visibilidade: publica.
- Objetivo: Seleciona visualmente uma origem pelo indice da listbox.
- Parametros:
    - `estado_interface`: TAD local da UI com widgets, selecoes e dados editados em memoria.
    - `indice`: posicao selecionada em lista/listbox.
- Possiveis retornos:
    - `_selecionar_origem_configurada_interface(estado_interface)`: retorno delegado para outra funcao.
    - `ERRO_DADOS_INVALIDOS`: entrada com tipo, formato ou valor invalido.
- TADs envolvidos: Estado da interface, Origem configurada, Tipo de arquivo, Destino do tipo, Restricoes.

#### `_selecionar_tipo_por_indice(estado_interface, indice)`
- Visibilidade: interna.
- Objetivo: Seleciona tipo visualmente por indice.
- Parametros:
    - `estado_interface`: TAD local da UI com widgets, selecoes e dados editados em memoria.
    - `indice`: posicao selecionada em lista/listbox.
- Possiveis retornos:
    - `_selecionar_tipo_arquivo_interface(estado_interface)`: retorno delegado para outra funcao.
    - `ERRO_DADOS_INVALIDOS`: entrada com tipo, formato ou valor invalido.
- TADs envolvidos: Estado da interface, Origem configurada, Tipo de arquivo, Destino do tipo, Restricoes.

#### `_obter_origem_selecionada(estado_interface)`
- Visibilidade: interna.
- Objetivo: Retorna origem selecionada.
- Parametros:
    - `estado_interface`: TAD local da UI com widgets, selecoes e dados editados em memoria.
- Possiveis retornos:
    - `origens[indice]`: valor calculado pela funcao.
    - `None`: ausencia valida de dado ou falha sem objeto retornavel.
- TADs envolvidos: Estado da interface, Origem configurada, Tipo de arquivo, Destino do tipo, Restricoes.

#### `_obter_tipo_selecionado(estado_interface)`
- Visibilidade: interna.
- Objetivo: Retorna tipo selecionado.
- Parametros:
    - `estado_interface`: TAD local da UI com widgets, selecoes e dados editados em memoria.
- Possiveis retornos:
    - `tipos[indice]`: valor calculado pela funcao.
    - `None`: ausencia valida de dado ou falha sem objeto retornavel.
- TADs envolvidos: Estado da interface, Origem configurada, Tipo de arquivo, Destino do tipo, Restricoes.

#### `_preencher_nome_tipo_interface(estado_interface, nome)`
- Visibilidade: interna.
- Objetivo: Substitui o texto do campo de nome do tipo.
- Parametros:
    - `estado_interface`: TAD local da UI com widgets, selecoes e dados editados em memoria.
    - `nome`: nome do tipo a exibir no campo de texto.
- Possiveis retornos:
    - `OK`: sucesso da operacao.
- TADs envolvidos: Estado da interface, Tipo de arquivo.

#### `salvar_tipo_selecionado_em_memoria(estado_interface)`
- Visibilidade: publica.
- Objetivo: Grava no tipo selecionado os campos editados na tela.
- Parametros:
    - `estado_interface`: TAD local da UI com widgets, selecoes e dados editados em memoria.
- Possiveis retornos:
    - `OK`: sucesso da operacao.
- TADs envolvidos: Estado da interface, Origem configurada, Tipo de arquivo, Destino do tipo, Restricoes.

### Modulo `converters.py`

Resumo: Conversores usados pela camada de interface.

TADs/obrigacoes do modulo: Valores de formulario.

#### `converter_inteiro_opcional(texto, padrao)`
- Visibilidade: publica.
- Objetivo: Converte texto para inteiro nao negativo ou retorna padrao quando vazio.
- Parametros:
    - `texto`: texto digitado pelo usuario.
    - `padrao`: valor usado quando o campo esta vazio.
- Possiveis retornos:
    - `valor`: valor calculado pela funcao.
    - `padrao`: valor calculado pela funcao.
    - `'invalido'`: sentinela de campo visual invalido.
- TADs envolvidos: Valores de formulario.

#### `converter_data_opcional(texto)`
- Visibilidade: publica.
- Objetivo: Valida uma data opcional em formato ISO e retorna o texto normalizado.
- Parametros:
    - `texto`: texto digitado pelo usuario.
- Possiveis retornos:
    - `texto`: valor calculado pela funcao.
    - `None`: ausencia valida de dado ou falha sem objeto retornavel.
    - `'invalido'`: sentinela de campo visual invalido.
- TADs envolvidos: Valores de formulario.

### Modulo `interface.py`

Resumo: Interface grafica do BackupManager usando tkinter e customtkinter.

TADs/obrigacoes do modulo: Estado da interface, Estado da aplicacao.

#### `iniciar_interface()`
- Visibilidade: publica.
- Objetivo: Inicia a interface grafica principal do BackupManager.
- Parametros:
    - nenhum parametro.
- Possiveis retornos:
    - `None`: ausencia valida de dado ou falha sem objeto retornavel.
- TADs envolvidos: Estado da interface, Estado da aplicacao.

#### `_criar_estado_interface()`
- Visibilidade: interna.
- Objetivo: Cria o dicionario de estado da interface.
- Parametros:
    - nenhum parametro.
- Possiveis retornos:
    - `{'janela': None, 'acao_fechar': None, 'ids_perfis': [], 'lista_perfis': None, 'entrada_nome': None, 'lista_origens': None, 'lista_tipos': None, 'lista_destinos': None, 'entrada_tipo_nome': None, 'operacao_var': None, 'destino_selecionado_indice': None, 'ativo_var': None, 'frame_extensoes': None, 'extensoes_vars': {}, 'entrada_nova_extensao': None, 'entrada_regra_nome': None, 'modo_regra_nome_var': None, 'lista_regras_nome': None, 'regras_nome': [], 'entrada_tamanho_min': None, 'entrada_tamanho_max': None, 'entrada_data_min': None, 'entrada_data_max': None, 'perfil_selecionado_id': None, 'origens_configuradas': [], 'origem_selecionada_indice': None, 'tipo_selecionado_indice': None, 'botao_backup': None, 'backup_em_execucao': False}`: novo dicionario/TAD montado pela funcao.
- TADs envolvidos: Estado da interface, Estado da aplicacao.

#### `_criar_janela_principal()`
- Visibilidade: interna.
- Objetivo: Cria a janela principal.
- Parametros:
    - nenhum parametro.
- Possiveis retornos:
    - `janela`: valor calculado pela funcao.
- TADs envolvidos: Estado da interface, Estado da aplicacao.

### Modulo `profiles.py`

Resumo: Painel de perfis da interface.

TADs/obrigacoes do modulo: Estado da interface, Perfil.

#### `criar_area_perfis(janela, estado_interface)`
- Visibilidade: publica.
- Objetivo: Cria o painel de gerenciamento de perfis.
- Parametros:
    - `janela`: janela Tk/CustomTkinter.
    - `estado_interface`: TAD local da UI com widgets, selecoes e dados editados em memoria.
- Possiveis retornos:
    - `frame`: valor calculado pela funcao.
- TADs envolvidos: Estado da interface, Perfil.

#### `atualizar_lista_perfis(estado_interface)`
- Visibilidade: publica.
- Objetivo: Recarrega a listbox de perfis a partir do controller.
- Parametros:
    - `estado_interface`: TAD local da UI com widgets, selecoes e dados editados em memoria.
- Possiveis retornos:
    - `codigo`: codigo de retorno propagado de chamada interna.
- TADs envolvidos: Estado da interface, Perfil.

#### `selecionar_perfil_por_id(estado_interface, perfil_id)`
- Visibilidade: publica.
- Objetivo: Seleciona na interface o perfil identificado por `perfil_id`.
- Parametros:
    - `estado_interface`: TAD local da UI com widgets, selecoes e dados editados em memoria.
    - `perfil_id`: identificador unico de um perfil.
- Possiveis retornos:
    - `_selecionar_perfil_interface(estado_interface)`: retorno delegado para outra funcao.
    - `ERRO_DADOS_INVALIDOS`: entrada com tipo, formato ou valor invalido.
- TADs envolvidos: Estado da interface, Perfil.

#### `_criar_perfil_interface(estado_interface)`
- Visibilidade: interna.
- Objetivo: Cria um perfil a partir do nome informado na interface.
- Parametros:
    - `estado_interface`: TAD local da UI com widgets, selecoes e dados editados em memoria.
- Possiveis retornos:
    - `codigo`: codigo de retorno propagado de chamada interna.
- TADs envolvidos: Estado da interface, Perfil.

#### `_selecionar_perfil_interface(estado_interface)`
- Visibilidade: interna.
- Objetivo: Seleciona o perfil destacado na lista.
- Parametros:
    - `estado_interface`: TAD local da UI com widgets, selecoes e dados editados em memoria.
- Possiveis retornos:
    - `OK`: sucesso da operacao.
    - `ERRO_DADOS_INVALIDOS`: entrada com tipo, formato ou valor invalido.
    - `codigo`: codigo de retorno propagado de chamada interna.
- TADs envolvidos: Estado da interface, Perfil.

#### `_excluir_perfil_interface(estado_interface)`
- Visibilidade: interna.
- Objetivo: Exclui o perfil selecionado.
- Parametros:
    - `estado_interface`: TAD local da UI com widgets, selecoes e dados editados em memoria.
- Possiveis retornos:
    - `codigo`: codigo de retorno propagado de chamada interna.
    - `mostrar_mensagem_resultado(ERRO_DADOS_INVALIDOS)`: retorno delegado para outra funcao.
    - `OK`: sucesso da operacao.
- TADs envolvidos: Estado da interface, Perfil.

### Modulo `restrictions.py`

Resumo: Area de restricoes e filtros da UI.

TADs/obrigacoes do modulo: Estado da interface, Restricoes, Tipo de arquivo, Configuracoes.

#### `criar_area_restricoes(janela, estado_interface, ao_alterar_restricoes=None)`
- Visibilidade: publica.
- Objetivo: Cria o painel de restricoes de arquivos.
- Parametros:
    - `janela`: janela Tk/CustomTkinter.
    - `estado_interface`: TAD local da UI com widgets, selecoes e dados editados em memoria.
    - `ao_alterar_restricoes`: callback chamado quando restricoes mudam na UI.
- Possiveis retornos:
    - `frame`: valor calculado pela funcao.
- TADs envolvidos: Estado da interface, Restricoes, Tipo de arquivo, Configuracoes.

#### `_criar_area_extensoes(container, estado_interface)`
- Visibilidade: interna.
- Objetivo: Cria a selecao de extensoes disponiveis por checkbox.
- Parametros:
    - `container`: widget pai onde componentes visuais serao criados.
    - `estado_interface`: TAD local da UI com widgets, selecoes e dados editados em memoria.
- Possiveis retornos:
    - `estado_interface['frame_extensoes']`: valor calculado pela funcao.
- TADs envolvidos: Estado da interface, Restricoes, Tipo de arquivo, Configuracoes.

#### `_criar_area_regras_nome(container, estado_interface, ao_alterar_restricoes=None)`
- Visibilidade: interna.
- Objetivo: Cria o formulario e a lista de regras por nome de arquivo.
- Parametros:
    - `container`: widget pai onde componentes visuais serao criados.
    - `estado_interface`: TAD local da UI com widgets, selecoes e dados editados em memoria.
    - `ao_alterar_restricoes`: callback chamado quando restricoes mudam na UI.
- Possiveis retornos:
    - `estado_interface['lista_regras_nome']`: valor calculado pela funcao.
- TADs envolvidos: Estado da interface, Restricoes, Tipo de arquivo, Configuracoes.

#### `_criar_area_tamanho(container, estado_interface)`
- Visibilidade: interna.
- Objetivo: Cria os campos de tamanho minimo e maximo.
- Parametros:
    - `container`: widget pai onde componentes visuais serao criados.
    - `estado_interface`: TAD local da UI com widgets, selecoes e dados editados em memoria.
- Possiveis retornos:
    - `linha_tamanhos`: valor calculado pela funcao.
- TADs envolvidos: Estado da interface, Restricoes, Tipo de arquivo, Configuracoes.

#### `_criar_area_datas(container, estado_interface)`
- Visibilidade: interna.
- Objetivo: Cria os campos de data minima e maxima de modificacao.
- Parametros:
    - `container`: widget pai onde componentes visuais serao criados.
    - `estado_interface`: TAD local da UI com widgets, selecoes e dados editados em memoria.
- Possiveis retornos:
    - `linha_datas`: valor calculado pela funcao.
- TADs envolvidos: Estado da interface, Restricoes, Tipo de arquivo, Configuracoes.

#### `atualizar_checkboxes_extensoes(estado_interface, extensoes_marcadas=None)`
- Visibilidade: publica.
- Objetivo: Recria a lista de checkboxes de extensoes disponiveis.
- Parametros:
    - `estado_interface`: TAD local da UI com widgets, selecoes e dados editados em memoria.
    - `extensoes_marcadas`: parametro usado pela funcao conforme o contexto do modulo.
- Possiveis retornos:
    - `OK`: sucesso da operacao.
    - `ERRO_DADOS_INVALIDOS`: entrada com tipo, formato ou valor invalido.
    - `codigo`: codigo de retorno propagado de chamada interna.
- TADs envolvidos: Estado da interface, Restricoes, Tipo de arquivo, Configuracoes.

#### `_adicionar_extensao_interface(estado_interface)`
- Visibilidade: interna.
- Objetivo: Adiciona uma extensao customizada a lista disponivel e a marca.
- Parametros:
    - `estado_interface`: TAD local da UI com widgets, selecoes e dados editados em memoria.
- Possiveis retornos:
    - `OK`: sucesso da operacao.
    - `ERRO_DADOS_INVALIDOS`: entrada com tipo, formato ou valor invalido.
    - `codigo`: codigo de retorno propagado de chamada interna.
- TADs envolvidos: Estado da interface, Restricoes, Tipo de arquivo, Configuracoes.

#### `_adicionar_regra_nome_interface(estado_interface, ao_alterar_restricoes=None)`
- Visibilidade: interna.
- Objetivo: Adiciona uma regra de nome na memoria visual do tipo atual.
- Parametros:
    - `estado_interface`: TAD local da UI com widgets, selecoes e dados editados em memoria.
    - `ao_alterar_restricoes`: callback chamado quando restricoes mudam na UI.
- Possiveis retornos:
    - `OK`: sucesso da operacao.
    - `ERRO_DADOS_INVALIDOS`: entrada com tipo, formato ou valor invalido.
- TADs envolvidos: Estado da interface, Restricoes, Tipo de arquivo, Configuracoes.

#### `_remover_regra_nome_interface(estado_interface, ao_alterar_restricoes=None)`
- Visibilidade: interna.
- Objetivo: Remove a regra de nome selecionada da memoria visual.
- Parametros:
    - `estado_interface`: TAD local da UI com widgets, selecoes e dados editados em memoria.
    - `ao_alterar_restricoes`: callback chamado quando restricoes mudam na UI.
- Possiveis retornos:
    - `OK`: sucesso da operacao.
    - `ERRO_DADOS_INVALIDOS`: entrada com tipo, formato ou valor invalido.
- TADs envolvidos: Estado da interface, Restricoes, Tipo de arquivo, Configuracoes.

#### `atualizar_lista_regras_nome(estado_interface, regras)`
- Visibilidade: publica.
- Objetivo: Atualiza a listbox de regras de nome e o estado correspondente.
- Parametros:
    - `estado_interface`: TAD local da UI com widgets, selecoes e dados editados em memoria.
    - `regras`: parametro usado pela funcao conforme o contexto do modulo.
- Possiveis retornos:
    - `OK`: sucesso da operacao.
    - `ERRO_DADOS_INVALIDOS`: entrada com tipo, formato ou valor invalido.
- TADs envolvidos: Estado da interface, Restricoes, Tipo de arquivo, Configuracoes.

#### `_obter_regras_nome_interface(estado_interface)`
- Visibilidade: interna.
- Objetivo: Retorna uma copia normalizada das regras de nome em memoria.
- Parametros:
    - `estado_interface`: TAD local da UI com widgets, selecoes e dados editados em memoria.
- Possiveis retornos:
    - `_normalizar_regras_nome_interface(estado_interface.get('regras_nome', []))`: retorno delegado para outra funcao.
- TADs envolvidos: Estado da interface, Restricoes, Tipo de arquivo, Configuracoes.

#### `_normalizar_regras_nome_interface(regras)`
- Visibilidade: interna.
- Objetivo: Normaliza regras de nome para persistencia no perfil.
- Parametros:
    - `regras`: parametro usado pela funcao conforme o contexto do modulo.
- Possiveis retornos:
    - `normalizadas`: valor calculado pela funcao.
    - `[]`: lista vazia; nenhuma entrada aplicavel.
- TADs envolvidos: Estado da interface, Restricoes, Tipo de arquivo, Configuracoes.

#### `_obter_regras_nome_das_restricoes(restricoes)`
- Visibilidade: interna.
- Objetivo: Extrai regras de nome salvas no formato atual.
- Parametros:
    - `restricoes`: TAD Restricoes usado para filtrar arquivos.
- Possiveis retornos:
    - `_normalizar_regras_nome_interface(perfil_manager.obter_regras_nome_restricoes(restricoes))`: retorno delegado para outra funcao.
- TADs envolvidos: Estado da interface, Restricoes, Tipo de arquivo, Configuracoes.

#### `_obter_modo_regra_nome_interface(estado_interface)`
- Visibilidade: interna.
- Objetivo: Retorna o modo selecionado para uma nova regra de nome.
- Parametros:
    - `estado_interface`: TAD local da UI com widgets, selecoes e dados editados em memoria.
- Possiveis retornos:
    - `'contem'`: valor calculado pela funcao.
    - `'exato'`: valor calculado pela funcao.
- TADs envolvidos: Estado da interface, Restricoes, Tipo de arquivo, Configuracoes.

#### `_formatar_regra_nome_interface(regra)`
- Visibilidade: interna.
- Objetivo: Formata uma regra de nome para exibicao em listbox.
- Parametros:
    - `regra`: parametro usado pela funcao conforme o contexto do modulo.
- Possiveis retornos:
    - `rotulo + ': ' + regra.get('valor', '')`: retorno delegado para outra funcao.
- TADs envolvidos: Estado da interface, Restricoes, Tipo de arquivo, Configuracoes.

#### `criar_restricoes_da_interface(estado_interface)`
- Visibilidade: publica.
- Objetivo: Monta o dicionario de restricoes a partir dos campos da tela.
- Parametros:
    - `estado_interface`: TAD local da UI com widgets, selecoes e dados editados em memoria.
- Possiveis retornos:
    - `perfil_manager.criar_restricoes(_obter_extensoes_marcadas(estado_interface), _obter_regras_nome_interface(estado_interface), 0 if tamanho_min == 'invalido' else tamanho_min, None if tamanho_max == 'invalido' else tamanho_max, None if data_min == 'invalido' else data_min, None if data_max == 'invalido' else data_max)`: retorno delegado para outra funcao.
- TADs envolvidos: Estado da interface, Restricoes, Tipo de arquivo, Configuracoes.

#### `_obter_restricoes_do_tipo(tipo)`
- Visibilidade: interna.
- Objetivo: Retorna restricoes do tipo no formato atual.
- Parametros:
    - `tipo`: TAD Tipo de Arquivo, com nome, ativo, restricoes e destinos.
- Possiveis retornos:
    - `perfil_manager.obter_restricoes_tipo(tipo)`: retorno delegado para outra funcao.
- TADs envolvidos: Estado da interface, Restricoes, Tipo de arquivo, Configuracoes.

#### `preencher_formulario_com_tipo(estado_interface, tipo, atualizar_destinos_callback=None)`
- Visibilidade: publica.
- Objetivo: Carrega no painel de restricoes os dados de um tipo selecionado.
- Parametros:
    - `estado_interface`: TAD local da UI com widgets, selecoes e dados editados em memoria.
    - `tipo`: TAD Tipo de Arquivo, com nome, ativo, restricoes e destinos.
    - `atualizar_destinos_callback`: callback para atualizar destinos apos carregar tipo.
- Possiveis retornos:
    - `OK`: sucesso da operacao.
    - `ERRO_DADOS_INVALIDOS`: entrada com tipo, formato ou valor invalido.
- TADs envolvidos: Estado da interface, Restricoes, Tipo de arquivo, Configuracoes.

#### `limpar_area_tipo_destino(estado_interface)`
- Visibilidade: publica.
- Objetivo: Limpa campos relacionados ao tipo e seus destinos.
- Parametros:
    - `estado_interface`: TAD local da UI com widgets, selecoes e dados editados em memoria.
- Possiveis retornos:
    - `OK`: sucesso da operacao.
- TADs envolvidos: Estado da interface, Restricoes, Tipo de arquivo, Configuracoes.

#### `formulario_tipo_possui_valor_invalido(estado_interface)`
- Visibilidade: publica.
- Objetivo: Indica se algum filtro numerico ou de data do tipo atual e invalido.
- Parametros:
    - `estado_interface`: TAD local da UI com widgets, selecoes e dados editados em memoria.
- Possiveis retornos:
    - `tamanho_min == 'invalido' or tamanho_max == 'invalido' or data_min == 'invalido' or (data_max == 'invalido')`: retorno delegado para outra funcao.
- TADs envolvidos: Estado da interface, Restricoes, Tipo de arquivo, Configuracoes.

#### `_obter_extensoes_marcadas(estado_interface)`
- Visibilidade: interna.
- Objetivo: Retorna as extensoes marcadas no painel de checkboxes.
- Parametros:
    - `estado_interface`: TAD local da UI com widgets, selecoes e dados editados em memoria.
- Possiveis retornos:
    - `extensoes`: valor calculado pela funcao.
- TADs envolvidos: Estado da interface, Restricoes, Tipo de arquivo, Configuracoes.

#### `_preencher_entry(entrada, valor)`
- Visibilidade: interna.
- Objetivo: Sem docstring.
- Parametros:
    - `entrada`: campo de texto da interface.
    - `valor`: valor recebido, validado ou escrito em widget/TAD.
- Possiveis retornos:
    - `OK`: sucesso da operacao.
- TADs envolvidos: Estado da interface, Restricoes, Tipo de arquivo, Configuracoes.

#### `_executar_callback(callback)`
- Visibilidade: interna.
- Objetivo: Sem docstring.
- Parametros:
    - `callback`: funcao opcional chamada pelo fluxo visual.
- Possiveis retornos:
    - `OK`: sucesso da operacao.
    - `callback()`: retorno delegado para outra funcao.
- TADs envolvidos: Estado da interface, Restricoes, Tipo de arquivo, Configuracoes.

#### `_mostrar_mensagem_resultado(codigo)`
- Visibilidade: interna.
- Objetivo: Sem docstring.
- Parametros:
    - `codigo`: codigo de retorno de return_codes.py.
- Possiveis retornos:
    - `codigo`: codigo de retorno propagado de chamada interna.
- TADs envolvidos: Estado da interface, Restricoes, Tipo de arquivo, Configuracoes.

### Modulo `theme.py`

Resumo: Tema visual e helpers de janelas da interface.

TADs/obrigacoes do modulo: Widgets Tk/CustomTkinter.

#### `configurar_estilo_visual()`
- Visibilidade: publica.
- Objetivo: Configura o tema global usado pelos widgets CustomTkinter.
- Parametros:
    - nenhum parametro.
- Possiveis retornos:
    - `OK`: sucesso da operacao.
- TADs envolvidos: Widgets Tk/CustomTkinter.

#### `configurar_frame(frame)`
- Visibilidade: publica.
- Objetivo: Aplica a configuracao visual neutra usada em frames de layout.
- Parametros:
    - `frame`: widget frame da interface.
- Possiveis retornos:
    - `frame`: valor calculado pela funcao.
- TADs envolvidos: Widgets Tk/CustomTkinter.

#### `criar_painel(container, titulo)`
- Visibilidade: publica.
- Objetivo: Cria um painel padronizado com borda, fundo e titulo de secao.
- Parametros:
    - `container`: widget pai onde componentes visuais serao criados.
    - `titulo`: titulo exibido em painel.
- Possiveis retornos:
    - `frame`: valor calculado pela funcao.
- TADs envolvidos: Widgets Tk/CustomTkinter.

#### `criar_label(container, texto)`
- Visibilidade: publica.
- Objetivo: Cria um label auxiliar com cor e fonte padrao da interface.
- Parametros:
    - `container`: widget pai onde componentes visuais serao criados.
    - `texto`: texto digitado pelo usuario.
- Possiveis retornos:
    - `ctk.CTkLabel(container, text=texto, text_color=COR_TEXTO_FRACO, font=FONTE_PADRAO)`: retorno delegado para outra funcao.
- TADs envolvidos: Widgets Tk/CustomTkinter.

#### `criar_entry(container, largura=None)`
- Visibilidade: publica.
- Objetivo: Cria um campo de texto consistente para formularios da interface.
- Parametros:
    - `container`: widget pai onde componentes visuais serao criados.
    - `largura`: largura opcional do widget.
- Possiveis retornos:
    - `ctk.CTkEntry(container, width=largura or 140, height=34, fg_color=COR_CAMPO, border_color=COR_BORDA, text_color=COR_TEXTO, corner_radius=6, font=FONTE_PADRAO)`: retorno delegado para outra funcao.
- TADs envolvidos: Widgets Tk/CustomTkinter.

#### `criar_botao(container, texto, comando, cor=COR_PAINEL_2, texto_cor=COR_TEXTO, largura=None)`
- Visibilidade: publica.
- Objetivo: Cria um botao padronizado com hover coerente com a cor base.
- Parametros:
    - `container`: widget pai onde componentes visuais serao criados.
    - `texto`: texto digitado pelo usuario.
    - `comando`: callback executado por botao.
    - `cor`: cor principal do widget.
    - `texto_cor`: cor do texto do widget.
    - `largura`: largura opcional do widget.
- Possiveis retornos:
    - `ctk.CTkButton(container, text=texto, command=comando, fg_color=cor, hover_color=hover, text_color=texto_cor, width=largura or 140, height=34, corner_radius=6, font=FONTE_SELECAO)`: retorno delegado para outra funcao.
- TADs envolvidos: Widgets Tk/CustomTkinter.

#### `adicionar_tooltip(widget, texto)`
- Visibilidade: publica.
- Objetivo: Adiciona um tooltip simples controlado por eventos de mouse.
- Parametros:
    - `widget`: widget Tk/CustomTkinter.
    - `texto`: texto digitado pelo usuario.
- Possiveis retornos:
    - `widget`: valor calculado pela funcao.
    - `None`: ausencia valida de dado ou falha sem objeto retornavel.
- TADs envolvidos: Widgets Tk/CustomTkinter.

#### `criar_listbox(container, altura)`
- Visibilidade: publica.
- Objetivo: Cria uma listbox com cores e fonte alinhadas ao tema do app.
- Parametros:
    - `container`: widget pai onde componentes visuais serao criados.
    - `altura`: parametro usado pela funcao conforme o contexto do modulo.
- Possiveis retornos:
    - `tk.Listbox(container, height=altura, exportselection=False, bg=COR_CAMPO, fg=COR_TEXTO, selectbackground=COR_AZUL, selectforeground='#ffffff', relief='solid', bd=1, highlightthickness=1, highlightbackground=COR_BORDA, highlightcolor=COR_AZUL, font=FONTE_PADRAO)`: retorno delegado para outra funcao.
- TADs envolvidos: Widgets Tk/CustomTkinter.

#### `widgets_existem()`
- Visibilidade: publica.
- Objetivo: Indica se todos os widgets informados ainda existem no Tk.
- Parametros:
    - nenhum parametro.
- Possiveis retornos:
    - `all((widget is not None and widget.winfo_exists() for widget in widgets))`: retorno delegado para outra funcao.
    - `False`: condicao rejeitada/falsa.
- TADs envolvidos: Widgets Tk/CustomTkinter.

#### `trazer_janela_para_frente(janela)`
- Visibilidade: publica.
- Objetivo: Traz a janela principal para frente ao iniciar sem fixa-la no topo.
- Parametros:
    - `janela`: janela Tk/CustomTkinter.
- Possiveis retornos:
    - `OK`: sucesso da operacao.
- TADs envolvidos: Widgets Tk/CustomTkinter.

#### `manter_janela_acima_da_principal(janela_filha, janela_principal)`
- Visibilidade: publica.
- Objetivo: Mantem uma janela secundaria acima da principal ate ela ser minimizada.
- Parametros:
    - `janela_filha`: janela secundaria Tk/CustomTkinter.
    - `janela_principal`: janela principal Tk/CustomTkinter.
- Possiveis retornos:
    - `OK`: sucesso da operacao.
    - `None`: ausencia valida de dado ou falha sem objeto retornavel.
- TADs envolvidos: Widgets Tk/CustomTkinter.



## Testes

A suite usa pytest funcional, sem classes, structs ou unittest. Cada teste retorna `None` implicitamente quando passa e falha por `assert` quando o comportamento esperado nao ocorre.

### `tests/assertions.py`

Escopo: Fornece helpers funcionais de assercao para pytest, sem classes.

#### `assert_equal(valor_obtido, valor_esperado, mensagem=None)`
- Visibilidade: publica.
- Objetivo: Falha se os dois valores comparados forem diferentes.
- Parametros:
    - `valor_obtido`: valor produzido pelo teste.
    - `valor_esperado`: valor esperado pelo teste.
    - `mensagem`: mensagem opcional de assercao em testes.
- Possiveis retornos:
    - retorno implicito `None`: funcao usada por assercao/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD especifico; funcao utilitaria ou teste.

#### `assert_not_equal(valor_obtido, valor_inesperado, mensagem=None)`
- Visibilidade: publica.
- Objetivo: Falha se os dois valores comparados forem iguais.
- Parametros:
    - `valor_obtido`: valor produzido pelo teste.
    - `valor_inesperado`: valor que nao deve aparecer no teste.
    - `mensagem`: mensagem opcional de assercao em testes.
- Possiveis retornos:
    - retorno implicito `None`: funcao usada por assercao/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD especifico; funcao utilitaria ou teste.

#### `assert_true(valor, mensagem=None)`
- Visibilidade: publica.
- Objetivo: Falha se o valor recebido nao for verdadeiro.
- Parametros:
    - `valor`: valor recebido, validado ou escrito em widget/TAD.
    - `mensagem`: mensagem opcional de assercao em testes.
- Possiveis retornos:
    - retorno implicito `None`: funcao usada por assercao/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD especifico; funcao utilitaria ou teste.

#### `assert_false(valor, mensagem=None)`
- Visibilidade: publica.
- Objetivo: Falha se o valor recebido nao for falso.
- Parametros:
    - `valor`: valor recebido, validado ou escrito em widget/TAD.
    - `mensagem`: mensagem opcional de assercao em testes.
- Possiveis retornos:
    - retorno implicito `None`: funcao usada por assercao/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD especifico; funcao utilitaria ou teste.

#### `assert_is_none(valor, mensagem=None)`
- Visibilidade: publica.
- Objetivo: Falha se o valor recebido nao for None.
- Parametros:
    - `valor`: valor recebido, validado ou escrito em widget/TAD.
    - `mensagem`: mensagem opcional de assercao em testes.
- Possiveis retornos:
    - retorno implicito `None`: funcao usada por assercao/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD especifico; funcao utilitaria ou teste.

#### `assert_is_not_none(valor, mensagem=None)`
- Visibilidade: publica.
- Objetivo: Falha se o valor recebido for None.
- Parametros:
    - `valor`: valor recebido, validado ou escrito em widget/TAD.
    - `mensagem`: mensagem opcional de assercao em testes.
- Possiveis retornos:
    - retorno implicito `None`: funcao usada por assercao/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD especifico; funcao utilitaria ou teste.

#### `assert_is_instance(valor, tipo_esperado, mensagem=None)`
- Visibilidade: publica.
- Objetivo: Falha se o valor recebido nao for instancia do tipo esperado.
- Parametros:
    - `valor`: valor recebido, validado ou escrito em widget/TAD.
    - `tipo_esperado`: tipo Python esperado em assercao.
    - `mensagem`: mensagem opcional de assercao em testes.
- Possiveis retornos:
    - retorno implicito `None`: funcao usada por assercao/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD especifico; funcao utilitaria ou teste.

#### `assert_in(valor, colecao, mensagem=None)`
- Visibilidade: publica.
- Objetivo: Falha se o valor recebido nao existir na colecao.
- Parametros:
    - `valor`: valor recebido, validado ou escrito em widget/TAD.
    - `colecao`: colecao usada em assercao de presenca.
    - `mensagem`: mensagem opcional de assercao em testes.
- Possiveis retornos:
    - retorno implicito `None`: funcao usada por assercao/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD especifico; funcao utilitaria ou teste.

#### `assert_not_in(valor, colecao, mensagem=None)`
- Visibilidade: publica.
- Objetivo: Falha se o valor recebido existir na colecao.
- Parametros:
    - `valor`: valor recebido, validado ou escrito em widget/TAD.
    - `colecao`: colecao usada em assercao de presenca.
    - `mensagem`: mensagem opcional de assercao em testes.
- Possiveis retornos:
    - retorno implicito `None`: funcao usada por assercao/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD especifico; funcao utilitaria ou teste.

### `tests/test_backup_engine.py`

Escopo: Cobre fluxo de backup, copia/movimento/recorte, filtros por tipo, origem/tipo inativos e validacoes integradas.

#### `test_montar_resultado_backup()`
- Visibilidade: publica.
- Objetivo: Sem docstring.
- Parametros:
    - nenhum parametro.
- Possiveis retornos:
    - retorno implicito `None`: funcao usada por assercao/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD especifico; funcao utilitaria ou teste.

#### `test_executar_backup_base_sem_arquivos()`
- Visibilidade: publica.
- Objetivo: Sem docstring.
- Parametros:
    - nenhum parametro.
- Possiveis retornos:
    - retorno implicito `None`: funcao usada por assercao/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD especifico; funcao utilitaria ou teste.

#### `test_validar_perfil_para_backup_valido()`
- Visibilidade: publica.
- Objetivo: Sem docstring.
- Parametros:
    - nenhum parametro.
- Possiveis retornos:
    - retorno implicito `None`: funcao usada por assercao/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD especifico; funcao utilitaria ou teste.

#### `test_validar_perfil_para_backup_rejeita_dados_invalidos()`
- Visibilidade: publica.
- Objetivo: Sem docstring.
- Parametros:
    - nenhum parametro.
- Possiveis retornos:
    - retorno implicito `None`: funcao usada por assercao/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD especifico; funcao utilitaria ou teste.

#### `test_validar_perfil_para_backup_rejeita_sem_origem()`
- Visibilidade: publica.
- Objetivo: Sem docstring.
- Parametros:
    - nenhum parametro.
- Possiveis retornos:
    - retorno implicito `None`: funcao usada por assercao/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD especifico; funcao utilitaria ou teste.

#### `test_validar_perfil_para_backup_rejeita_sem_destino()`
- Visibilidade: publica.
- Objetivo: Sem docstring.
- Parametros:
    - nenhum parametro.
- Possiveis retornos:
    - retorno implicito `None`: funcao usada por assercao/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD especifico; funcao utilitaria ou teste.

#### `test_validar_perfil_para_backup_rejeita_operacao_invalida()`
- Visibilidade: publica.
- Objetivo: Sem docstring.
- Parametros:
    - nenhum parametro.
- Possiveis retornos:
    - retorno implicito `None`: funcao usada por assercao/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD especifico; funcao utilitaria ou teste.

#### `test_executar_backup_retorna_erro_de_validacao()`
- Visibilidade: publica.
- Objetivo: Sem docstring.
- Parametros:
    - nenhum parametro.
- Possiveis retornos:
    - retorno implicito `None`: funcao usada por assercao/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD especifico; funcao utilitaria ou teste.

#### `test_gerar_caminho_destino_com_nome()`
- Visibilidade: publica.
- Objetivo: Sem docstring.
- Parametros:
    - nenhum parametro.
- Possiveis retornos:
    - retorno implicito `None`: funcao usada por assercao/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD especifico; funcao utilitaria ou teste.

#### `test_gerar_caminho_destino_com_caminho_sem_nome()`
- Visibilidade: publica.
- Objetivo: Sem docstring.
- Parametros:
    - nenhum parametro.
- Possiveis retornos:
    - retorno implicito `None`: funcao usada por assercao/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD especifico; funcao utilitaria ou teste.

#### `test_gerar_caminho_destino_rejeita_dados_invalidos()`
- Visibilidade: publica.
- Objetivo: Sem docstring.
- Parametros:
    - nenhum parametro.
- Possiveis retornos:
    - retorno implicito `None`: funcao usada por assercao/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD especifico; funcao utilitaria ou teste.

#### `test_criar_pasta_destino_se_necessario_cria_diretorio()`
- Visibilidade: publica.
- Objetivo: Sem docstring.
- Parametros:
    - nenhum parametro.
- Possiveis retornos:
    - retorno implicito `None`: funcao usada por assercao/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD especifico; funcao utilitaria ou teste.

#### `test_criar_pasta_destino_se_necessario_aceita_diretorio_existente()`
- Visibilidade: publica.
- Objetivo: Sem docstring.
- Parametros:
    - nenhum parametro.
- Possiveis retornos:
    - retorno implicito `None`: funcao usada por assercao/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD especifico; funcao utilitaria ou teste.

#### `test_criar_pasta_destino_se_necessario_rejeita_caminho_invalido()`
- Visibilidade: publica.
- Objetivo: Sem docstring.
- Parametros:
    - nenhum parametro.
- Possiveis retornos:
    - retorno implicito `None`: funcao usada por assercao/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD especifico; funcao utilitaria ou teste.

#### `test_copiar_arquivo_copia_conteudo_e_mantem_original()`
- Visibilidade: publica.
- Objetivo: Sem docstring.
- Parametros:
    - nenhum parametro.
- Possiveis retornos:
    - retorno implicito `None`: funcao usada por assercao/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD especifico; funcao utilitaria ou teste.

#### `test_copiar_arquivo_retorna_erro_sem_quebrar()`
- Visibilidade: publica.
- Objetivo: Sem docstring.
- Parametros:
    - nenhum parametro.
- Possiveis retornos:
    - retorno implicito `None`: funcao usada por assercao/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD especifico; funcao utilitaria ou teste.

#### `test_copiar_arquivo_rejeita_dados_invalidos()`
- Visibilidade: publica.
- Objetivo: Sem docstring.
- Parametros:
    - nenhum parametro.
- Possiveis retornos:
    - retorno implicito `None`: funcao usada por assercao/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD especifico; funcao utilitaria ou teste.

#### `test_mover_arquivo_move_conteudo_e_remove_original()`
- Visibilidade: publica.
- Objetivo: Sem docstring.
- Parametros:
    - nenhum parametro.
- Possiveis retornos:
    - retorno implicito `None`: funcao usada por assercao/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD especifico; funcao utilitaria ou teste.

#### `test_mover_arquivo_retorna_erro_sem_quebrar()`
- Visibilidade: publica.
- Objetivo: Sem docstring.
- Parametros:
    - nenhum parametro.
- Possiveis retornos:
    - retorno implicito `None`: funcao usada por assercao/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD especifico; funcao utilitaria ou teste.

#### `test_mover_arquivo_rejeita_dados_invalidos()`
- Visibilidade: publica.
- Objetivo: Sem docstring.
- Parametros:
    - nenhum parametro.
- Possiveis retornos:
    - retorno implicito `None`: funcao usada por assercao/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD especifico; funcao utilitaria ou teste.

#### `test_executar_backup_retorna_sem_arquivos_quando_filtro_rejeita_todos()`
- Visibilidade: publica.
- Objetivo: Sem docstring.
- Parametros:
    - nenhum parametro.
- Possiveis retornos:
    - retorno implicito `None`: funcao usada por assercao/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD especifico; funcao utilitaria ou teste.

#### `test_executar_backup_configurado_envia_tipos_para_destinos_distintos()`
- Visibilidade: publica.
- Objetivo: Sem docstring.
- Parametros:
    - nenhum parametro.
- Possiveis retornos:
    - retorno implicito `None`: funcao usada por assercao/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD especifico; funcao utilitaria ou teste.

#### `test_executar_backup_configurado_ignora_arquivos_em_subpastas_da_origem()`
- Visibilidade: publica.
- Objetivo: Sem docstring.
- Parametros:
    - nenhum parametro.
- Possiveis retornos:
    - retorno implicito `None`: funcao usada por assercao/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD especifico; funcao utilitaria ou teste.

#### `test_executar_backup_configurado_recorta_para_destino_unico()`
- Visibilidade: publica.
- Objetivo: Sem docstring.
- Parametros:
    - nenhum parametro.
- Possiveis retornos:
    - retorno implicito `None`: funcao usada por assercao/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD especifico; funcao utilitaria ou teste.

#### `test_validar_perfil_configurado_rejeita_mover_para_multiplos_destinos()`
- Visibilidade: publica.
- Objetivo: Sem docstring.
- Parametros:
    - nenhum parametro.
- Possiveis retornos:
    - retorno implicito `None`: funcao usada por assercao/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD especifico; funcao utilitaria ou teste.

#### `test_executar_backup_configurado_ignora_origem_inativa()`
- Visibilidade: publica.
- Objetivo: Sem docstring.
- Parametros:
    - nenhum parametro.
- Possiveis retornos:
    - retorno implicito `None`: funcao usada por assercao/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD especifico; funcao utilitaria ou teste.

#### `test_executar_backup_configurado_ignora_tipo_inativo()`
- Visibilidade: publica.
- Objetivo: Sem docstring.
- Parametros:
    - nenhum parametro.
- Possiveis retornos:
    - retorno implicito `None`: funcao usada por assercao/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD especifico; funcao utilitaria ou teste.

#### `test_validar_perfil_configurado_ignora_conflito_de_tipo_inativo()`
- Visibilidade: publica.
- Objetivo: Sem docstring.
- Parametros:
    - nenhum parametro.
- Possiveis retornos:
    - retorno implicito `None`: funcao usada por assercao/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD especifico; funcao utilitaria ou teste.

### `tests/test_backup_result.py`

Escopo: Cobre montagem e acumulacao dos TADs de resultado.

#### `test_montar_resultado_backup_cria_contadores_zerados()`
- Visibilidade: publica.
- Objetivo: Sem docstring.
- Parametros:
    - nenhum parametro.
- Possiveis retornos:
    - retorno implicito `None`: funcao usada por assercao/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD especifico; funcao utilitaria ou teste.

#### `test_aplicar_resultado_arquivo_acumula_contadores_e_listas()`
- Visibilidade: publica.
- Objetivo: Sem docstring.
- Parametros:
    - nenhum parametro.
- Possiveis retornos:
    - retorno implicito `None`: funcao usada por assercao/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD especifico; funcao utilitaria ou teste.

#### `test_montar_registro_arquivo_preserva_metadados()`
- Visibilidade: publica.
- Objetivo: Sem docstring.
- Parametros:
    - nenhum parametro.
- Possiveis retornos:
    - retorno implicito `None`: funcao usada por assercao/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD especifico; funcao utilitaria ou teste.

#### `test_montar_erro_arquivo()`
- Visibilidade: publica.
- Objetivo: Sem docstring.
- Parametros:
    - nenhum parametro.
- Possiveis retornos:
    - retorno implicito `None`: funcao usada por assercao/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD especifico; funcao utilitaria ou teste.

### `tests/test_backup_validation.py`

Escopo: Cobre validacao estrutural de perfil, origem, destino e operacao.

#### `test_validar_perfil_rejeita_formato_antigo()`
- Visibilidade: publica.
- Objetivo: Sem docstring.
- Parametros:
    - nenhum parametro.
- Possiveis retornos:
    - retorno implicito `None`: funcao usada por assercao/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD especifico; funcao utilitaria ou teste.

#### `test_validar_perfil_rejeita_dados_invalidos()`
- Visibilidade: publica.
- Objetivo: Sem docstring.
- Parametros:
    - nenhum parametro.
- Possiveis retornos:
    - retorno implicito `None`: funcao usada por assercao/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD especifico; funcao utilitaria ou teste.

#### `test_validar_perfil_configurado_valido()`
- Visibilidade: publica.
- Objetivo: Sem docstring.
- Parametros:
    - nenhum parametro.
- Possiveis retornos:
    - retorno implicito `None`: funcao usada por assercao/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD especifico; funcao utilitaria ou teste.

#### `test_validar_perfil_configurado_rejeita_sem_origem()`
- Visibilidade: publica.
- Objetivo: Sem docstring.
- Parametros:
    - nenhum parametro.
- Possiveis retornos:
    - retorno implicito `None`: funcao usada por assercao/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD especifico; funcao utilitaria ou teste.

#### `test_validar_destinos_do_tipo_rejeita_destino_invalido()`
- Visibilidade: publica.
- Objetivo: Sem docstring.
- Parametros:
    - nenhum parametro.
- Possiveis retornos:
    - retorno implicito `None`: funcao usada por assercao/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD especifico; funcao utilitaria ou teste.

#### `test_validar_destinos_do_tipo_rejeita_operacao_invalida()`
- Visibilidade: publica.
- Objetivo: Sem docstring.
- Parametros:
    - nenhum parametro.
- Possiveis retornos:
    - retorno implicito `None`: funcao usada por assercao/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD especifico; funcao utilitaria ou teste.

#### `test_validar_destinos_do_tipo_rejeita_mover_com_multiplos_destinos()`
- Visibilidade: publica.
- Objetivo: Sem docstring.
- Parametros:
    - nenhum parametro.
- Possiveis retornos:
    - retorno implicito `None`: funcao usada por assercao/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD especifico; funcao utilitaria ou teste.

### `tests/test_controller.py`

Escopo: Cobre estado em memoria, persistencia diferida, configuracoes, pre-visualizacao e bloqueio de perfil inativo.

#### `resetar_estado()`
- Visibilidade: publica.
- Objetivo: Reinicia o estado global usado pelo controller nos testes.
- Parametros:
    - nenhum parametro.
- Possiveis retornos:
    - retorno implicito `None`: funcao usada por assercao/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD especifico; funcao utilitaria ou teste.

#### `criar_gravador(retorno=None)`
- Visibilidade: publica.
- Objetivo: Cria uma funcao fake que registra chamadas e devolve um retorno fixo.
- Parametros:
    - `retorno`: valor fixo devolvido por funcao fake de teste.
- Possiveis retornos:
    - `(gravador, chamadas)`: tupla de retorno; normalmente combina codigo e dado/resultado.
    - `retorno`: valor calculado pela funcao.
- TADs envolvidos: nenhum TAD especifico; funcao utilitaria ou teste.

#### `resetar_controller_antes_de_cada_teste()`
- Visibilidade: publica.
- Objetivo: Garante que cada teste comece com o controller em memoria limpa.
- Parametros:
    - nenhum parametro.
- Possiveis retornos:
    - retorno implicito `None`: funcao usada por assercao/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD especifico; funcao utilitaria ou teste.

#### `test_criar_perfil_altera_apenas_memoria()`
- Visibilidade: publica.
- Objetivo: Sem docstring.
- Parametros:
    - nenhum parametro.
- Possiveis retornos:
    - retorno implicito `None`: funcao usada por assercao/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD especifico; funcao utilitaria ou teste.

#### `test_criar_perfil_nao_salva_json_imediatamente(monkeypatch)`
- Visibilidade: publica.
- Objetivo: Sem docstring.
- Parametros:
    - `monkeypatch`: fixture pytest para substituir funcoes/atributos durante o teste.
- Possiveis retornos:
    - retorno implicito `None`: funcao usada por assercao/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD especifico; funcao utilitaria ou teste.

#### `test_finalizar_aplicacao_salva_json_quando_estado_foi_alterado(monkeypatch)`
- Visibilidade: publica.
- Objetivo: Sem docstring.
- Parametros:
    - `monkeypatch`: fixture pytest para substituir funcoes/atributos durante o teste.
- Possiveis retornos:
    - retorno implicito `None`: funcao usada por assercao/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD especifico; funcao utilitaria ou teste.

#### `test_finalizar_aplicacao_sem_alteracao_nao_salva_json(monkeypatch)`
- Visibilidade: publica.
- Objetivo: Sem docstring.
- Parametros:
    - `monkeypatch`: fixture pytest para substituir funcoes/atributos durante o teste.
- Possiveis retornos:
    - retorno implicito `None`: funcao usada por assercao/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD especifico; funcao utilitaria ou teste.

#### `test_inicializar_aplicacao_carrega_estado_em_memoria(monkeypatch)`
- Visibilidade: publica.
- Objetivo: Sem docstring.
- Parametros:
    - `monkeypatch`: fixture pytest para substituir funcoes/atributos durante o teste.
- Possiveis retornos:
    - retorno implicito `None`: funcao usada por assercao/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD especifico; funcao utilitaria ou teste.

#### `test_executar_backup_nao_altera_estado_quando_falha_validacao()`
- Visibilidade: publica.
- Objetivo: Sem docstring.
- Parametros:
    - nenhum parametro.
- Possiveis retornos:
    - retorno implicito `None`: funcao usada por assercao/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD especifico; funcao utilitaria ou teste.

#### `test_salvar_perfil_editado_aplica_dados_em_memoria(monkeypatch)`
- Visibilidade: publica.
- Objetivo: Sem docstring.
- Parametros:
    - `monkeypatch`: fixture pytest para substituir funcoes/atributos durante o teste.
- Possiveis retornos:
    - retorno implicito `None`: funcao usada por assercao/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD especifico; funcao utilitaria ou teste.

#### `test_salvar_perfil_editado_aplica_origens_configuradas()`
- Visibilidade: publica.
- Objetivo: Sem docstring.
- Parametros:
    - nenhum parametro.
- Possiveis retornos:
    - retorno implicito `None`: funcao usada por assercao/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD especifico; funcao utilitaria ou teste.

#### `test_salvar_perfil_editado_rejeita_dados_invalidos()`
- Visibilidade: publica.
- Objetivo: Sem docstring.
- Parametros:
    - nenhum parametro.
- Possiveis retornos:
    - retorno implicito `None`: funcao usada por assercao/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD especifico; funcao utilitaria ou teste.

#### `test_ativar_e_desativar_perfil_alteram_memoria()`
- Visibilidade: publica.
- Objetivo: Sem docstring.
- Parametros:
    - nenhum parametro.
- Possiveis retornos:
    - retorno implicito `None`: funcao usada por assercao/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD especifico; funcao utilitaria ou teste.

#### `test_obter_arquivos_do_perfil_lista_arquivos_com_status_incluido()`
- Visibilidade: publica.
- Objetivo: Sem docstring.
- Parametros:
    - nenhum parametro.
- Possiveis retornos:
    - retorno implicito `None`: funcao usada por assercao/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD especifico; funcao utilitaria ou teste.

#### `test_obter_arquivos_do_perfil_inexistente()`
- Visibilidade: publica.
- Objetivo: Sem docstring.
- Parametros:
    - nenhum parametro.
- Possiveis retornos:
    - retorno implicito `None`: funcao usada por assercao/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD especifico; funcao utilitaria ou teste.

#### `test_obter_arquivos_do_perfil_configurado_lista_tipos_incluidos()`
- Visibilidade: publica.
- Objetivo: Sem docstring.
- Parametros:
    - nenhum parametro.
- Possiveis retornos:
    - retorno implicito `None`: funcao usada por assercao/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD especifico; funcao utilitaria ou teste.

#### `test_executar_backup_bloqueia_perfil_inativo()`
- Visibilidade: publica.
- Objetivo: Sem docstring.
- Parametros:
    - nenhum parametro.
- Possiveis retornos:
    - retorno implicito `None`: funcao usada por assercao/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD especifico; funcao utilitaria ou teste.

#### `test_configuracoes_gerais_alteram_apenas_memoria()`
- Visibilidade: publica.
- Objetivo: Sem docstring.
- Parametros:
    - nenhum parametro.
- Possiveis retornos:
    - retorno implicito `None`: funcao usada por assercao/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD especifico; funcao utilitaria ou teste.

#### `test_salvar_configuracoes_rejeita_dados_invalidos()`
- Visibilidade: publica.
- Objetivo: Sem docstring.
- Parametros:
    - nenhum parametro.
- Possiveis retornos:
    - retorno implicito `None`: funcao usada por assercao/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD especifico; funcao utilitaria ou teste.

#### `test_obter_extensoes_disponiveis_une_padrao_e_config()`
- Visibilidade: publica.
- Objetivo: Sem docstring.
- Parametros:
    - nenhum parametro.
- Possiveis retornos:
    - retorno implicito `None`: funcao usada por assercao/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD especifico; funcao utilitaria ou teste.

#### `test_adicionar_extensao_disponivel_normaliza_e_altera_memoria()`
- Visibilidade: publica.
- Objetivo: Sem docstring.
- Parametros:
    - nenhum parametro.
- Possiveis retornos:
    - retorno implicito `None`: funcao usada por assercao/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD especifico; funcao utilitaria ou teste.

#### `test_adicionar_extensao_disponivel_rejeita_invalida()`
- Visibilidade: publica.
- Objetivo: Sem docstring.
- Parametros:
    - nenhum parametro.
- Possiveis retornos:
    - retorno implicito `None`: funcao usada por assercao/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD especifico; funcao utilitaria ou teste.

### `tests/test_file_utils.py`

Escopo: Cobre caminhos, permissoes, metadados e filtros de arquivo/restricoes.

#### `test_caminho_existe_para_arquivo_e_diretorio()`
- Visibilidade: publica.
- Objetivo: Sem docstring.
- Parametros:
    - nenhum parametro.
- Possiveis retornos:
    - retorno implicito `None`: funcao usada por assercao/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD especifico; funcao utilitaria ou teste.

#### `test_caminho_existe_retorna_false_para_invalido()`
- Visibilidade: publica.
- Objetivo: Sem docstring.
- Parametros:
    - nenhum parametro.
- Possiveis retornos:
    - retorno implicito `None`: funcao usada por assercao/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD especifico; funcao utilitaria ou teste.

#### `test_caminho_e_diretorio()`
- Visibilidade: publica.
- Objetivo: Sem docstring.
- Parametros:
    - nenhum parametro.
- Possiveis retornos:
    - retorno implicito `None`: funcao usada por assercao/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD especifico; funcao utilitaria ou teste.

#### `test_verificar_permissao_leitura()`
- Visibilidade: publica.
- Objetivo: Sem docstring.
- Parametros:
    - nenhum parametro.
- Possiveis retornos:
    - retorno implicito `None`: funcao usada por assercao/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD especifico; funcao utilitaria ou teste.

#### `test_verificar_permissao_escrita()`
- Visibilidade: publica.
- Objetivo: Sem docstring.
- Parametros:
    - nenhum parametro.
- Possiveis retornos:
    - retorno implicito `None`: funcao usada por assercao/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD especifico; funcao utilitaria ou teste.

#### `test_listar_arquivos_em_origem_ignora_subpastas()`
- Visibilidade: publica.
- Objetivo: Sem docstring.
- Parametros:
    - nenhum parametro.
- Possiveis retornos:
    - retorno implicito `None`: funcao usada por assercao/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD especifico; funcao utilitaria ou teste.

#### `test_listar_arquivos_em_origem_invalida()`
- Visibilidade: publica.
- Objetivo: Sem docstring.
- Parametros:
    - nenhum parametro.
- Possiveis retornos:
    - retorno implicito `None`: funcao usada por assercao/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD especifico; funcao utilitaria ou teste.

#### `test_listar_arquivos_de_origens()`
- Visibilidade: publica.
- Objetivo: Sem docstring.
- Parametros:
    - nenhum parametro.
- Possiveis retornos:
    - retorno implicito `None`: funcao usada por assercao/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD especifico; funcao utilitaria ou teste.

#### `test_listar_arquivos_de_origens_rejeita_tipo_invalido()`
- Visibilidade: publica.
- Objetivo: Sem docstring.
- Parametros:
    - nenhum parametro.
- Possiveis retornos:
    - retorno implicito `None`: funcao usada por assercao/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD especifico; funcao utilitaria ou teste.

#### `test_obter_extensao()`
- Visibilidade: publica.
- Objetivo: Sem docstring.
- Parametros:
    - nenhum parametro.
- Possiveis retornos:
    - retorno implicito `None`: funcao usada por assercao/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD especifico; funcao utilitaria ou teste.

#### `test_obter_metadados_arquivo()`
- Visibilidade: publica.
- Objetivo: Sem docstring.
- Parametros:
    - nenhum parametro.
- Possiveis retornos:
    - retorno implicito `None`: funcao usada por assercao/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD especifico; funcao utilitaria ou teste.

#### `test_obter_metadados_arquivo_invalido()`
- Visibilidade: publica.
- Objetivo: Sem docstring.
- Parametros:
    - nenhum parametro.
- Possiveis retornos:
    - retorno implicito `None`: funcao usada por assercao/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD especifico; funcao utilitaria ou teste.

#### `test_filtrar_por_extensao()`
- Visibilidade: publica.
- Objetivo: Sem docstring.
- Parametros:
    - nenhum parametro.
- Possiveis retornos:
    - retorno implicito `None`: funcao usada por assercao/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD especifico; funcao utilitaria ou teste.

#### `test_filtrar_por_extensao_aceita_lista_vazia()`
- Visibilidade: publica.
- Objetivo: Sem docstring.
- Parametros:
    - nenhum parametro.
- Possiveis retornos:
    - retorno implicito `None`: funcao usada por assercao/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD especifico; funcao utilitaria ou teste.

#### `test_filtrar_por_extensao_normaliza_ponto_e_maiusculas()`
- Visibilidade: publica.
- Objetivo: Sem docstring.
- Parametros:
    - nenhum parametro.
- Possiveis retornos:
    - retorno implicito `None`: funcao usada por assercao/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD especifico; funcao utilitaria ou teste.

#### `test_filtrar_por_extensao_rejeita_extensao_nao_permitida()`
- Visibilidade: publica.
- Objetivo: Sem docstring.
- Parametros:
    - nenhum parametro.
- Possiveis retornos:
    - retorno implicito `None`: funcao usada por assercao/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD especifico; funcao utilitaria ou teste.

#### `test_filtrar_por_nome()`
- Visibilidade: publica.
- Objetivo: Sem docstring.
- Parametros:
    - nenhum parametro.
- Possiveis retornos:
    - retorno implicito `None`: funcao usada por assercao/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD especifico; funcao utilitaria ou teste.

#### `test_filtrar_por_nome_aceita_sem_regras()`
- Visibilidade: publica.
- Objetivo: Sem docstring.
- Parametros:
    - nenhum parametro.
- Possiveis retornos:
    - retorno implicito `None`: funcao usada por assercao/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD especifico; funcao utilitaria ou teste.

#### `test_filtrar_por_nome_ignora_maiusculas()`
- Visibilidade: publica.
- Objetivo: Sem docstring.
- Parametros:
    - nenhum parametro.
- Possiveis retornos:
    - retorno implicito `None`: funcao usada por assercao/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD especifico; funcao utilitaria ou teste.

#### `test_filtrar_por_nome_rejeita_trecho_ausente()`
- Visibilidade: publica.
- Objetivo: Sem docstring.
- Parametros:
    - nenhum parametro.
- Possiveis retornos:
    - retorno implicito `None`: funcao usada por assercao/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD especifico; funcao utilitaria ou teste.

#### `test_filtrar_por_regras_nome_contem()`
- Visibilidade: publica.
- Objetivo: Sem docstring.
- Parametros:
    - nenhum parametro.
- Possiveis retornos:
    - retorno implicito `None`: funcao usada por assercao/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD especifico; funcao utilitaria ou teste.

#### `test_filtrar_por_regras_nome_exato()`
- Visibilidade: publica.
- Objetivo: Sem docstring.
- Parametros:
    - nenhum parametro.
- Possiveis retornos:
    - retorno implicito `None`: funcao usada por assercao/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD especifico; funcao utilitaria ou teste.

#### `test_filtrar_por_regras_nome_exato_aceita_nome_sem_extensao()`
- Visibilidade: publica.
- Objetivo: Garante que o modo nome completo aceite o nome base do arquivo sem extensao.
- Parametros:
    - nenhum parametro.
- Possiveis retornos:
    - retorno implicito `None`: funcao usada por assercao/callback ou efeito colateral.
- TADs envolvidos: Restricoes, Metadados de arquivo.

#### `test_filtrar_por_regras_nome_exato_rejeita_nome_parcial()`
- Visibilidade: publica.
- Objetivo: Sem docstring.
- Parametros:
    - nenhum parametro.
- Possiveis retornos:
    - retorno implicito `None`: funcao usada por assercao/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD especifico; funcao utilitaria ou teste.

#### `test_filtrar_por_regras_nome_usa_qualquer_regra()`
- Visibilidade: publica.
- Objetivo: Sem docstring.
- Parametros:
    - nenhum parametro.
- Possiveis retornos:
    - retorno implicito `None`: funcao usada por assercao/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD especifico; funcao utilitaria ou teste.

#### `test_filtrar_por_tamanho_minimo()`
- Visibilidade: publica.
- Objetivo: Sem docstring.
- Parametros:
    - nenhum parametro.
- Possiveis retornos:
    - retorno implicito `None`: funcao usada por assercao/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD especifico; funcao utilitaria ou teste.

#### `test_filtrar_por_tamanho_maximo()`
- Visibilidade: publica.
- Objetivo: Sem docstring.
- Parametros:
    - nenhum parametro.
- Possiveis retornos:
    - retorno implicito `None`: funcao usada por assercao/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD especifico; funcao utilitaria ou teste.

#### `test_filtrar_por_tamanho_rejeita_menor_que_minimo()`
- Visibilidade: publica.
- Objetivo: Sem docstring.
- Parametros:
    - nenhum parametro.
- Possiveis retornos:
    - retorno implicito `None`: funcao usada por assercao/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD especifico; funcao utilitaria ou teste.

#### `test_filtrar_por_tamanho_rejeita_maior_que_maximo()`
- Visibilidade: publica.
- Objetivo: Sem docstring.
- Parametros:
    - nenhum parametro.
- Possiveis retornos:
    - retorno implicito `None`: funcao usada por assercao/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD especifico; funcao utilitaria ou teste.

#### `test_filtrar_por_data_sem_limites()`
- Visibilidade: publica.
- Objetivo: Sem docstring.
- Parametros:
    - nenhum parametro.
- Possiveis retornos:
    - retorno implicito `None`: funcao usada por assercao/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD especifico; funcao utilitaria ou teste.

#### `test_filtrar_por_data_minima_e_maxima()`
- Visibilidade: publica.
- Objetivo: Sem docstring.
- Parametros:
    - nenhum parametro.
- Possiveis retornos:
    - retorno implicito `None`: funcao usada por assercao/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD especifico; funcao utilitaria ou teste.

#### `test_filtrar_por_data_rejeita_antes_da_minima()`
- Visibilidade: publica.
- Objetivo: Sem docstring.
- Parametros:
    - nenhum parametro.
- Possiveis retornos:
    - retorno implicito `None`: funcao usada por assercao/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD especifico; funcao utilitaria ou teste.

#### `test_filtrar_por_data_rejeita_depois_da_maxima()`
- Visibilidade: publica.
- Objetivo: Sem docstring.
- Parametros:
    - nenhum parametro.
- Possiveis retornos:
    - retorno implicito `None`: funcao usada por assercao/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD especifico; funcao utilitaria ou teste.

#### `test_arquivo_atende_restricoes_combinadas()`
- Visibilidade: publica.
- Objetivo: Sem docstring.
- Parametros:
    - nenhum parametro.
- Possiveis retornos:
    - retorno implicito `None`: funcao usada por assercao/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD especifico; funcao utilitaria ou teste.

#### `test_arquivo_atende_restricoes_rejeita_quando_um_filtro_falha()`
- Visibilidade: publica.
- Objetivo: Sem docstring.
- Parametros:
    - nenhum parametro.
- Possiveis retornos:
    - retorno implicito `None`: funcao usada por assercao/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD especifico; funcao utilitaria ou teste.

#### `test_arquivo_atende_restricoes_aceita_restricoes_vazias()`
- Visibilidade: publica.
- Objetivo: Sem docstring.
- Parametros:
    - nenhum parametro.
- Possiveis retornos:
    - retorno implicito `None`: funcao usada por assercao/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD especifico; funcao utilitaria ou teste.

#### `test_arquivo_atende_restricoes_rejeita_dados_invalidos()`
- Visibilidade: publica.
- Objetivo: Sem docstring.
- Parametros:
    - nenhum parametro.
- Possiveis retornos:
    - retorno implicito `None`: funcao usada por assercao/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD especifico; funcao utilitaria ou teste.

### `tests/test_new_modules_contract.py`

Escopo: Cobre contrato de API publica via __all__ nos modulos novos.

#### `test_modulos_novos_declararam_api_publica()`
- Visibilidade: publica.
- Objetivo: Sem docstring.
- Parametros:
    - nenhum parametro.
- Possiveis retornos:
    - retorno implicito `None`: funcao usada por assercao/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD especifico; funcao utilitaria ou teste.

### `tests/test_perfil_manager.py`

Escopo: Cobre criacao e consulta dos TADs de perfil/origem/tipo/destino.

#### `test_criar_perfil_valido()`
- Visibilidade: publica.
- Objetivo: Sem docstring.
- Parametros:
    - nenhum parametro.
- Possiveis retornos:
    - retorno implicito `None`: funcao usada por assercao/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD especifico; funcao utilitaria ou teste.

#### `test_criar_perfil_nome_vazio()`
- Visibilidade: publica.
- Objetivo: Sem docstring.
- Parametros:
    - nenhum parametro.
- Possiveis retornos:
    - retorno implicito `None`: funcao usada por assercao/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD especifico; funcao utilitaria ou teste.

#### `test_consultar_perfil_existente()`
- Visibilidade: publica.
- Objetivo: Sem docstring.
- Parametros:
    - nenhum parametro.
- Possiveis retornos:
    - retorno implicito `None`: funcao usada por assercao/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD especifico; funcao utilitaria ou teste.

#### `test_consultar_perfil_inexistente()`
- Visibilidade: publica.
- Objetivo: Sem docstring.
- Parametros:
    - nenhum parametro.
- Possiveis retornos:
    - retorno implicito `None`: funcao usada por assercao/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD especifico; funcao utilitaria ou teste.

#### `test_criar_origem_tipo_e_destino_configurados()`
- Visibilidade: publica.
- Objetivo: Sem docstring.
- Parametros:
    - nenhum parametro.
- Possiveis retornos:
    - retorno implicito `None`: funcao usada por assercao/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD especifico; funcao utilitaria ou teste.

### `tests/test_storage.py`

Escopo: Cobre persistencia JSON, arquivos padrao e erro de JSON corrompido/dados invalidos.

#### `test_salvar_e_carregar_json()`
- Visibilidade: publica.
- Objetivo: Sem docstring.
- Parametros:
    - nenhum parametro.
- Possiveis retornos:
    - retorno implicito `None`: funcao usada por assercao/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD especifico; funcao utilitaria ou teste.

#### `test_carregar_json_inexistente()`
- Visibilidade: publica.
- Objetivo: Sem docstring.
- Parametros:
    - nenhum parametro.
- Possiveis retornos:
    - retorno implicito `None`: funcao usada por assercao/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD especifico; funcao utilitaria ou teste.

#### `test_carregar_json_corrompido()`
- Visibilidade: publica.
- Objetivo: Sem docstring.
- Parametros:
    - nenhum parametro.
- Possiveis retornos:
    - retorno implicito `None`: funcao usada por assercao/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD especifico; funcao utilitaria ou teste.

#### `test_salvar_json_rejeita_dados_nao_serializaveis()`
- Visibilidade: publica.
- Objetivo: Sem docstring.
- Parametros:
    - nenhum parametro.
- Possiveis retornos:
    - retorno implicito `None`: funcao usada por assercao/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD especifico; funcao utilitaria ou teste.

#### `test_criar_arquivos_padrao()`
- Visibilidade: publica.
- Objetivo: Sem docstring.
- Parametros:
    - nenhum parametro.
- Possiveis retornos:
    - retorno implicito `None`: funcao usada por assercao/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD especifico; funcao utilitaria ou teste.

### `tests/test_ui_converters.py`

Escopo: Cobre conversores puros de formulario usados pela UI.

#### `test_converter_inteiro_opcional()`
- Visibilidade: publica.
- Objetivo: Sem docstring.
- Parametros:
    - nenhum parametro.
- Possiveis retornos:
    - retorno implicito `None`: funcao usada por assercao/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD especifico; funcao utilitaria ou teste.

#### `test_converter_data_opcional()`
- Visibilidade: publica.
- Objetivo: Sem docstring.
- Parametros:
    - nenhum parametro.
- Possiveis retornos:
    - retorno implicito `None`: funcao usada por assercao/callback ou efeito colateral.
- TADs envolvidos: nenhum TAD especifico; funcao utilitaria ou teste.
