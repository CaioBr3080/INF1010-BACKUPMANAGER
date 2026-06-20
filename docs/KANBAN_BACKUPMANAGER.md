# Kanban BackupManager

## Direcao Atual

O projeto foi simplificado para backup manual com perfis locais. Recursos de
historico, scheduler, monitoramento automatico e execucao por intervalo foram
removidos.

## Concluido

- Modelo unico `origens_configuradas -> tipos_arquivo -> destinos`.
- Remocao de compatibilidade com perfil antigo.
- Interface modularizada em `ui_*`.
- Filtros por extensao, nome, tamanho e data.
- Operacao por destino: `copiar`, `mover`, `recortar`.
- Backup ignora arquivos em subpastas da origem.
- Janela principal sem area de agendamento.
- Cabecalho sem botao de historico.
- Persistencia limitada a perfis e configuracoes.

## Backlog Atual

### BM-UI-01 - Refinar Destinos

Melhorar a exibicao dos destinos para separar caminho e operacao de forma mais
legivel.

### BM-UI-02 - Melhorar Mensagens De Erro

Exibir mensagens mais especificas quando uma origem, tipo ou destino impedir a
execucao do backup.

### BM-TST-01 - Reduzir Acesso A Privados Nos Testes

Reescrever testes que ainda acessam helpers internos para cobrir contratos
publicos sempre que possivel.

### BM-ENG-01 - Separar Operacoes De Disco

Se `backup_engine.py` voltar a crescer, extrair copia/movimento/recorte para
um modulo dedicado de operacoes.
