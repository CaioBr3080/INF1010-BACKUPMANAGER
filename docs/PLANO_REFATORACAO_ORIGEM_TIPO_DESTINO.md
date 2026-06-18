# Plano de Refatoracao - Origem -> Tipo de Arquivo -> Destino -> Operacao

## Objetivo

Reorganizar o BackupManager para que as regras de backup deixem de ser globais no perfil e passem a ser vinculadas a cada origem.

Nova relacao principal:

```text
Origem -> Tipo de Arquivo -> Destino -> Operacao
```

## Compatibilidade

O modelo antigo continua aceito:

```python
{
    "origens": [],
    "destinos": [],
    "operacao": "copiar",
    "restricoes": {}
}
```

O novo modelo usa `origens_configuradas`:

```python
{
    "origens_configuradas": [
        {
            "id": "origem_001",
            "caminho": "C:/Documentos",
            "tipos_arquivo": [
                {
                    "id": "tipo_pdf",
                    "nome": "PDFs",
                    "restricoes": {
                        "extensoes_permitidas": [".pdf"],
                        "nome_contem": "",
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

Na implementacao inicial, se um tipo tiver qualquer destino com `mover` ou `recortar`, ele nao pode ter outros destinos ao mesmo tempo.

## Ja Implementado

- Perfil novo passa a nascer com `origens_configuradas: []`.
- `perfil_manager.py` possui factories para:
  - `criar_origem_configurada`;
  - `criar_tipo_arquivo`;
  - `criar_destino_tipo`.
- `backup_engine.py` detecta automaticamente se o perfil usa modelo novo ou legado.
- `backup_engine.py` executa o novo fluxo por origem, tipo e destino.
- `backup_engine.py` valida conflito de `mover`/`recortar` para multiplos destinos.
- `controller.py` aceita salvar `origens_configuradas`.
- `controller.py` migra automaticamente perfis legados ao carregar os dados.
- `controller.py` lista arquivos do perfil configurado com `tipos_incluidos`.
- `interface.py` ja expõe `recortar` na operacao legada.
- `interface.py` possui uma primeira tela operacional em tres colunas:
  - origens configuradas;
  - tipos da origem selecionada;
  - destinos do tipo selecionado com operacao.
- Testes automatizados cobrem o novo fluxo.

## Interface Implementada

A interface ja permite:

- adicionar e remover origens;
- selecionar uma origem e ver seus tipos;
- adicionar e remover tipos;
- editar filtros do tipo selecionado;
- adicionar e remover destinos do tipo;
- escolher operacao do destino: `copiar`, `mover` ou `recortar`;
- bloquear configuracoes invalidas de `mover`/`recortar` com multiplos destinos.

## Proximos Refinamentos de Interface

1. Melhorar exibicao visual dos destinos para separar caminho e operacao em colunas.
2. Adicionar edicao da operacao de um destino ja cadastrado sem precisar remover e adicionar novamente.
3. Criar uma tela de revisao de migracao, caso seja necessario inspecionar perfis antigos antes de salvar.
4. Melhorar mensagens de erro por origem/tipo/destino especifico.
5. Adicionar testes de interface em nivel de funcoes puras quando a estrutura estabilizar.

## Estrategia Recomendada

Implementar a interface em dois passos:

1. Tela simples baseada no novo modelo, sem remover os campos legados ainda.
2. Depois que o fluxo novo estiver validado, ocultar ou aposentar os campos legados.

Isso reduz risco de perder compatibilidade com os perfis existentes em `data/perfis.json`.
