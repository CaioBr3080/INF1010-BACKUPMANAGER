"""Funcoes de armazenamento em arquivos JSON."""

import json
from pathlib import Path

from backupmanager.return_codes import OK, ERRO_DADOS_INVALIDOS, ERRO_JSON_CORROMPIDO, ERRO_SEM_PERMISSAO

__all__ = [
    "salvar_perfis",
    "carregar_perfis",
    "salvar_configuracoes",
    "carregar_configuracoes",
    "criar_arquivos_padrao",
]

_BASE_DIR = Path(__file__).resolve().parent.parent
_DATA_DIR = _BASE_DIR / "data"
_PERFIS_PATH = _DATA_DIR / "perfis.json"
_CONFIG_PATH = _DATA_DIR / "config.json"


def _garantir_pasta_data():
    """Garante que a pasta data exista."""
    try:
        _DATA_DIR.mkdir(exist_ok=True)
    except (OSError, TypeError, ValueError):
        return ERRO_SEM_PERMISSAO
    return OK


def _salvar_json(caminho, dados):
    """Salva dados em um arquivo JSON."""
    try:
        conteudo = json.dumps(dados, indent=4, ensure_ascii=False)
    except (TypeError, ValueError):
        return ERRO_DADOS_INVALIDOS

    codigo = _garantir_pasta_data()
    if codigo != OK:
        return codigo

    try:
        with open(caminho, "w", encoding="utf-8") as arquivo:
            arquivo.write(conteudo)
    except (OSError, TypeError, ValueError):
        return ERRO_SEM_PERMISSAO

    return OK


def _carregar_json(caminho, valor_padrao):
    """Carrega dados de um JSON ou retorna valor padrao se ele nao existir."""
    caminho = Path(caminho)
    if not caminho.exists():
        return OK, valor_padrao

    try:
        with open(caminho, "r", encoding="utf-8") as arquivo:
            return OK, json.load(arquivo)
    except json.JSONDecodeError:
        return ERRO_JSON_CORROMPIDO, valor_padrao
    except (OSError, TypeError, ValueError):
        return ERRO_SEM_PERMISSAO, valor_padrao


def salvar_perfis(perfis):
    """Salva a lista de perfis no arquivo JSON oficial.

    Recebe a estrutura completa de perfis mantida pelo controller e grava em
    `data/perfis.json`. Retorna codigo de sucesso ou erro de permissao/dados
    invalidos conforme a falha encontrada.
    """
    return _salvar_json(_PERFIS_PATH, perfis)


def carregar_perfis():
    """Carrega a lista de perfis do arquivo JSON oficial.

    Retorna `(codigo, perfis)`. Quando o arquivo nao existe ou esta vazio,
    devolve a lista padrao vazia. A funcao nao migra perfis; essa etapa
    pertence ao controller/perfil_manager.
    """
    return _carregar_json(_PERFIS_PATH, [])


def salvar_configuracoes(config):
    """Salva as configuracoes gerais da aplicacao.

    O dicionario recebido representa opcoes globais, como extensoes
    customizadas. A funcao substitui o JSON de configuracao por esse conteudo.
    """
    return _salvar_json(_CONFIG_PATH, config)


def carregar_configuracoes():
    """Carrega as configuracoes gerais da aplicacao.

    Retorna `(codigo, config)` e usa dicionario vazio como padrao quando o
    arquivo ainda nao existe ou nao contem dados aproveitaveis.
    """
    return _carregar_json(_CONFIG_PATH, {})


def criar_arquivos_padrao():
    """Garante a pasta `data` e os arquivos JSON essenciais.

    Cria `perfis.json` e `config.json` quando ainda nao existem. Nao
    sobrescreve arquivos existentes. Deve ser chamada antes do primeiro
    carregamento da aplicacao.
    """
    codigo = _garantir_pasta_data()
    if codigo != OK:
        return codigo

    arquivos = [
        (_PERFIS_PATH, []),
        (_CONFIG_PATH, {}),
    ]

    for caminho, valor_padrao in arquivos:
        if Path(caminho).exists():
            continue
        codigo = _salvar_json(caminho, valor_padrao)
        if codigo != OK:
            return codigo

    return OK
