# Especificacao Atualizada do BackupManager

## Objetivo

Aplicacao desktop para executar backups manuais de arquivos locais com perfis
configuraveis.

## Escopo

Inclui:

- cadastro de perfis;
- ativacao/desativacao de perfil;
- origens configuradas;
- tipos de arquivo por origem;
- destinos por tipo;
- operacao por destino: `copiar`, `mover` ou `recortar`;
- filtros por extensao, nome, tamanho e data;
- persistencia de perfis e configuracoes.

Nao inclui:

- historico de execucoes;
- scheduler;
- monitoramento automatico;
- execucao por intervalo;
- backup ao detectar mudanca.

## Modelo de Perfil

```python
{
    "id": "perfil_001",
    "nome": "Backup",
    "ativo": True,
    "origens_configuradas": [
        {
            "id": "origem_001",
            "caminho": "C:/Origem",
            "ativo": True,
            "tipos_arquivo": [
                {
                    "id": "tipo_pdf",
                    "nome": "PDFs",
                    "ativo": True,
                    "restricoes": {
                        "extensoes_permitidas": [".pdf"],
                        "regras_nome": [],
                        "tamanho_min": 0,
                        "tamanho_max": None,
                        "data_modificacao_min": None,
                        "data_modificacao_max": None
                    },
                    "destinos": [
                        {
                            "caminho": "D:/Backup",
                            "operacao": "copiar"
                        }
                    ]
                }
            ]
        }
    ]
}
```

## Persistencia

- `data/perfis.json`: perfis do usuario.
- `data/config.json`: configuracoes globais, como extensoes customizadas.

## Modulos Principais

- `controller.py`: fachada da aplicacao.
- `domain/perfil_manager.py`: TAD de perfis.
- `domain/backup_validation.py`: validacoes do fluxo.
- `domain/backup_result.py`: estrutura de resultado.
- `engine/backup_engine.py`: execucao de backup.
- `engine/file_utils.py`: arquivos e filtros.
- `infra/storage.py`: JSON.
- `ui/*`: interface grafica.
