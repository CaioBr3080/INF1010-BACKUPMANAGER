"""Funcoes de armazenamento em arquivos JSON."""

import json
from pathlib import Path

from backupmanager.return_codes import OK, ERRO_DADOS_INVALIDOS, ERRO_JSON_CORROMPIDO, ERRO_SEM_PERMISSAO

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
PERFIS_PATH = DATA_DIR / "perfis.json"
HISTORICO_PATH = DATA_DIR / "historico.json"
CONFIG_PATH = DATA_DIR / "config.json"


def garantir_pasta_data():
    """Garante que a pasta data exista."""
    try:
        DATA_DIR.mkdir(exist_ok=True)
    except (OSError, TypeError, ValueError):
        return ERRO_SEM_PERMISSAO
    return OK


def salvar_json(caminho, dados):
    """Salva dados em um arquivo JSON."""
    try:
        conteudo = json.dumps(dados, indent=4, ensure_ascii=False)
    except (TypeError, ValueError):
        return ERRO_DADOS_INVALIDOS

    codigo = garantir_pasta_data()
    if codigo != OK:
        return codigo

    try:
        with open(caminho, "w", encoding="utf-8") as arquivo:
            arquivo.write(conteudo)
    except (OSError, TypeError, ValueError):
        return ERRO_SEM_PERMISSAO

    return OK


def carregar_json(caminho, valor_padrao):
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
    """Salva a lista de perfis."""
    return salvar_json(PERFIS_PATH, perfis)


def carregar_perfis():
    """Carrega a lista de perfis."""
    return carregar_json(PERFIS_PATH, [])


def salvar_historico(historico):
    """Salva a lista de registros de historico."""
    return salvar_json(HISTORICO_PATH, historico)


def carregar_historico():
    """Carrega a lista de registros de historico."""
    return carregar_json(HISTORICO_PATH, [])


def salvar_configuracoes(config):
    """Salva configuracoes gerais."""
    return salvar_json(CONFIG_PATH, config)


def carregar_configuracoes():
    """Carrega configuracoes gerais."""
    return carregar_json(CONFIG_PATH, {})


def criar_arquivos_padrao():
    """Cria arquivos JSON padrao quando eles nao existem."""
    codigo = garantir_pasta_data()
    if codigo != OK:
        return codigo

    arquivos = [
        (PERFIS_PATH, []),
        (HISTORICO_PATH, []),
        (CONFIG_PATH, {}),
    ]

    for caminho, valor_padrao in arquivos:
        if Path(caminho).exists():
            continue
        codigo = salvar_json(caminho, valor_padrao)
        if codigo != OK:
            return codigo

    return OK
