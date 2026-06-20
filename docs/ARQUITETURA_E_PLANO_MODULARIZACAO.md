# Arquitetura Atual do BackupManager

## Escopo Atual

O BackupManager executa backup manual de arquivos locais a partir de perfis
configurados no modelo:

```text
perfil -> origens_configuradas -> tipos_arquivo -> destinos
```

Historico, scheduler, monitoramento automatico e execucao por intervalo foram
removidos do projeto para manter a aplicacao focada e simples.

## Modulos

- `ui/interface.py`: fachada da interface grafica e composicao da tela.
- `ui/profiles.py`: painel de perfis, criacao, selecao e exclusao.
- `ui/backup_flow.py`: origens, tipos, destinos e operacao por destino.
- `ui/restrictions.py`: extensoes, regras de nome, tamanho e datas.
- `ui/actions.py`: botoes principais, sincronizacao do formulario e backup em thread.
- `ui/converters.py`: conversores simples de inteiro e data.
- `ui/theme.py`: cores, fontes, widgets e comportamento de janelas.
- `controller.py`: fachada entre UI, persistencia, perfis e motor de backup.
- `domain/perfil_manager.py`: TAD de perfis e factories do modelo atual.
- `engine/backup_engine.py`: orquestracao da execucao de backup.
- `domain/backup_validation.py`: validacao do modelo origem -> tipo -> destino.
- `domain/backup_result.py`: montagem e acumulacao de resultados da execucao.
- `engine/file_utils.py`: operacoes de caminho, listagem, metadados e filtros.
- `infra/storage.py`: persistencia de `perfis.json` e `config.json`.
- `return_codes.py`: codigos de retorno e mensagens.

## Persistencia

Arquivos usados:

- `data/perfis.json`;
- `data/config.json`.

O arquivo `data/historico.json` nao faz parte do fluxo atual.

## Encapsulamento

Todos os modulos principais declaram `__all__` para explicitar API publica.
Helpers internos usam prefixo `_`.

Regras atuais:

- A interface fala com o backend por `controller.py`.
- O controller e o unico dono do estado em memoria.
- Modulos de dominio nao importam `tkinter`/`customtkinter`.
- Modulos de persistencia nao conhecem regras de backup.
- Perfil novo nasce apenas com `id`, `nome`, `origens_configuradas` e `ativo`.

## Funcionalidades Removidas

Foram removidos:

- `history_manager.py`;
- `scheduler.py`;
- `ui_history.py`;
- armazenamento de historico;
- campos de agendamento na interface;
- campos `agendamento` e `estado_arquivos` nos perfis novos;
- testes dos modulos removidos.

## Proximas Melhorias

1. Reduzir testes que ainda inspecionam helpers privados.
2. Separar operacoes de disco de `backup_engine.py` se o arquivo voltar a crescer.
3. Melhorar mensagens por origem/tipo/destino quando houver erro de backup.
