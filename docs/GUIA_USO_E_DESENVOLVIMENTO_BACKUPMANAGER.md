# Guia de Uso e Desenvolvimento do BackupManager

## Uso

1. Crie ou selecione um perfil.
2. Adicione uma origem.
3. Adicione um tipo de arquivo para essa origem.
4. Configure restricoes, se necessario.
5. Adicione um ou mais destinos para o tipo.
6. Escolha a operacao do destino: `copiar`, `mover` ou `recortar`.
7. Clique em `Aplicar alteracoes`.
8. Clique em `Backup`.

O backup atual e sempre manual. Nao ha historico, scheduler ou monitoramento
automatico.

## Persistencia

O app mantem alteracoes em memoria durante a execucao e persiste no fechamento
seguro da janela.

Arquivos usados:

- `data/perfis.json`;
- `data/config.json`.

## Desenvolvimento

Camadas principais:

- UI: `interface.py`, `ui_profiles.py`, `ui_backup_flow.py`,
  `ui_restrictions.py`, `ui_actions.py`, `ui_converters.py`, `ui_theme.py`.
- Dominio: `perfil_manager.py`, `backup_engine.py`, `backup_validation.py`,
  `backup_result.py`, `file_utils.py`.
- Infra: `storage.py`, `return_codes.py`.

Regras:

- A UI deve acessar o backend pelo `controller.py`.
- Novas funcoes publicas devem entrar em `__all__`.
- Helpers internos devem usar prefixo `_`.
- Perfis devem usar apenas o modelo `origens_configuradas`.
