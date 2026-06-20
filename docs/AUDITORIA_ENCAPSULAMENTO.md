# Auditoria de Encapsulamento

## Estrutura Atual

```text
backupmanager/
  controller.py
  main.py
  return_codes.py
  domain/
    backup_result.py
    backup_validation.py
    perfil_manager.py
  engine/
    backup_engine.py
    file_utils.py
  infra/
    storage.py
  ui/
    actions.py
    backup_flow.py
    converters.py
    interface.py
    profiles.py
    restrictions.py
    theme.py
```

## Resultado Da Verificacao

- Todos os modulos da aplicacao declaram `__all__`.
- Funcoes auxiliares internas usam prefixo `_`.
- Nenhum modulo da aplicacao acessa simbolos privados de outro modulo de forma direta.
- A UI acessa o backend pelo `controller.py`.
- O controller acessa perfis por funcoes publicas de `domain/perfil_manager.py`.
- O motor de backup usa funcoes de acesso do TAD de perfil para ler perfil, origem, tipo, destino e restricoes.
- Persistencia ficou isolada em `infra/storage.py`.
- Operacoes e filtros de arquivo ficaram isolados em `engine/file_utils.py`.
- Resultados de backup sao administrados por funcoes publicas de `domain/backup_result.py`.
- Metadados de arquivo sao administrados por funcoes publicas de `engine/file_utils.py`.

## Resultado Com Criterio Rigido

Com criterio rigido de TAD, o encapsulamento principal da aplicacao foi
completado.

As estruturas persistidas continuam sendo dicionarios/listas para manter o JSON
simples, mas modulos externos nao devem conhecer suas chaves internas. Acesso,
criacao e alteracao agora passam por funcoes publicas dos modulos donos:

- `domain/perfil_manager.py`: perfil, origem, tipo, destino e restricoes.
- `engine/file_utils.py`: metadados de arquivo e informacoes de pre-visualizacao.
- `domain/backup_result.py`: resultado geral e resultado individual de arquivo.

A varredura atual nao encontrou acesso direto por `.get()` aos TADs de perfil,
origem, tipo, destino, restricoes, arquivo ou resultado fora dos modulos donos.

Excecoes aceitaveis:

- `_ESTADO` em `controller.py` e `estado_interface` nos modulos de UI sao TADs
  locais dos proprios modulos que os administram.
- Widgets tkinter/customtkinter continuam sendo manipulados diretamente pela
  UI, pois fazem parte do contrato da biblioteca grafica.

## TAD De Perfis

O TAD de perfis possui funcoes publicas para:

- criar estruturas: `criar_perfil`, `criar_origem_configurada`, `criar_tipo_arquivo`, `criar_destino_tipo`, `criar_restricoes_padrao`, `criar_restricoes`;
- consultar perfil: `consultar_perfil`, `listar_perfis`, `obter_id_perfil`, `obter_nome_perfil`, `perfil_esta_ativo`, `obter_origens_configuradas`;
- consultar origem: `obter_id_origem`, `obter_caminho_origem`, `origem_esta_ativa`, `obter_tipos_origem`;
- consultar tipo: `obter_id_tipo`, `obter_nome_tipo`, `tipo_esta_ativo`, `obter_restricoes_tipo`, `obter_destinos_tipo`;
- consultar destino: `obter_caminho_destino`, `obter_operacao_destino`;
- consultar restricoes: `obter_extensoes_restricoes`, `obter_regras_nome_restricoes`, `obter_tamanho_min_restricoes`, `obter_tamanho_max_restricoes`, `obter_data_min_restricoes`, `obter_data_max_restricoes`;
- alterar: `alterar_nome_perfil`, `alterar_origens_configuradas`, `ativar_perfil`, `desativar_perfil`, `excluir_perfil`, `alterar_origem_ativa`, `alterar_nome_tipo`, `alterar_restricoes_tipo`, `alterar_tipo_ativo`, `alterar_operacao_destino`, `adicionar_tipo_origem`, `remover_tipo_origem_por_indice`, `adicionar_destino_tipo_configurado`, `remover_destino_tipo_por_indice`.

Assim, outros modulos nao precisam conhecer os detalhes internos do dicionario
do perfil para as operacoes principais.

## TADs Cobertos

O criterio rigido agora cobre:

- origem configurada;
- tipo de arquivo;
- destino do tipo;
- restricoes;
- metadados de arquivo;
- resultado de backup;
- estado da interface como TAD local da UI;
- estado geral da aplicacao como TAD local do controller.

Modulos externos devem continuar usando apenas as funcoes publicas de acesso.
Novas chaves persistidas so devem ser adicionadas nos modulos donos dos TADs.

## Contrato De Retorno

O padrao atual continua sendo:

- funcoes que podem falhar retornam codigo de `return_codes.py`;
- funcoes que precisam devolver dados retornam tuplas `(codigo, dados)`;
- ausencia valida de dado usa `None` ou lista vazia, conforme o contrato da funcao;
- erro e ausencia valida nao sao tratados como a mesma coisa.

## Verificacao Atual

Comandos usados:

- `python -m compileall backupmanager tests`
- busca por `perfil.get`, `origem.get`, `tipo.get`, `destino.get`,
  `restricoes.get`, `resultado.get` e `arquivo.get` fora dos modulos donos;
- busca por classes, dataclasses, structs, `NamedTuple`, `TypedDict` e
  `unittest` em `backupmanager` e `tests`.

Resultados:

- compilacao concluida sem erro;
- nenhum acesso direto aos TADs principais fora dos modulos donos;
- nenhuma classe/struct encontrada na aplicacao ou testes.

## Observacao Sobre Testes

Os testes agora seguem o mesmo criterio estrutural da aplicacao:

- a suite usa pytest em estilo funcional;
- nao ha classes, dataclasses, structs, `NamedTuple`, `TypedDict` ou `unittest`;
- fixtures do pytest substituem o antigo `setUp`;
- mocks de `unittest.mock` foram substituidos por funcoes fake simples e
  `monkeypatch`.

Para executar a suite completa, instale as dependencias de desenvolvimento com
`pip install -r requirements-dev.txt` e rode `python -m pytest -q`.
