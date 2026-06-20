# Plano de Refatoracao - Origem -> Tipo de Arquivo -> Destino -> Operacao

## Objetivo

Reorganizar o BackupManager para que as regras de backup deixem de ser globais
no perfil e passem a ser vinculadas a cada origem e tipo de arquivo.

Relacao principal:

```text
Origem -> Tipo de Arquivo -> Destino -> Operacao
```

## Modelo Unico

O projeto agora aceita somente o modelo atual. Como a aplicacao nao foi
distribuida em producao, a compatibilidade com o formato antigo foi removida
para manter o codigo mais limpo.

```python
{
    "origens_configuradas": [
        {
            "id": "origem_001",
            "caminho": "C:/Documentos",
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

## Regras de Operacao

- `copiar`: pode ser usado em varios destinos para o mesmo tipo.
- `mover`: so pode ser usado por um destino para o mesmo tipo.
- `recortar`: so pode ser usado por um destino para o mesmo tipo.

Se um tipo tiver qualquer destino com `mover` ou `recortar`, ele nao pode ter
outros destinos ao mesmo tempo.

## Implementado

- Perfil novo nasce com `origens_configuradas: []`.
- `domain/perfil_manager.py` possui factories para origem, tipo e destino.
- `engine/backup_engine.py` executa somente o fluxo origem -> tipo -> destino.
- `domain/backup_validation.py` valida somente perfis no modelo atual.
- `controller.py` salva e lista arquivos usando `origens_configuradas`.
- `ui/interface.py` edita origens, tipos, destinos e operacao por destino.
- Regras de nome usam somente `regras_nome`.
- A execucao automatica foi removida; o backup atual e manual.

## Interface Implementada

A interface permite:

- adicionar e remover origens;
- ativar e desativar origens;
- selecionar uma origem e ver seus tipos;
- adicionar e remover tipos;
- editar filtros do tipo selecionado;
- adicionar e remover destinos do tipo;
- escolher operacao do destino: `copiar`, `mover` ou `recortar`;
- bloquear configuracoes invalidas de `mover`/`recortar` com multiplos destinos.

## Proximos Refinamentos

1. Melhorar exibicao visual dos destinos para separar caminho e operacao em colunas.
2. Adicionar edicao mais direta da operacao de um destino ja cadastrado.
3. Melhorar mensagens de erro por origem/tipo/destino especifico.
4. Adicionar testes de interface em nivel de funcoes puras quando a estrutura estabilizar.
