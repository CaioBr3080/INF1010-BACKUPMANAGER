"""Funcoes auxiliares para arquivos e diretorios."""

import os
from pathlib import Path
from datetime import datetime


def caminho_existe(caminho):
    """Verifica se um caminho existe."""
    if caminho is None:
        return False
    try:
        return Path(caminho).exists()
    except (OSError, TypeError, ValueError):
        return False


def caminho_e_diretorio(caminho):
    """Verifica se um caminho existe e e diretorio."""
    if caminho is None:
        return False
    try:
        return Path(caminho).is_dir()
    except (OSError, TypeError, ValueError):
        return False


def listar_arquivos_em_origem(origem):
    """Lista recursivamente arquivos de uma origem."""
    if not caminho_e_diretorio(origem):
        return []

    arquivos = []
    try:
        for raiz, _, nomes in os.walk(origem):
            for nome in nomes:
                arquivos.append(str(Path(raiz) / nome))
    except (OSError, TypeError, ValueError):
        return []
    return arquivos


def listar_arquivos_de_origens(origens):
    """Lista arquivos de varias origens."""
    if not isinstance(origens, list):
        return []

    arquivos = []
    for origem in origens:
        arquivos.extend(listar_arquivos_em_origem(origem))
    return arquivos


def obter_extensao(caminho):
    """Retorna a extensao de um arquivo em minusculas."""
    if caminho is None:
        return ""
    try:
        return Path(caminho).suffix.lower()
    except (OSError, TypeError, ValueError):
        return ""


def obter_metadados_arquivo(caminho):
    """Monta o dicionario de metadados de um arquivo."""
    if caminho is None:
        return None

    try:
        caminho_path = Path(caminho)
        if not caminho_path.is_file():
            return None
        estatisticas = caminho_path.stat()
    except (OSError, TypeError, ValueError):
        return None

    return {
        "caminho": str(caminho_path),
        "nome": caminho_path.name,
        "extensao": obter_extensao(caminho_path),
        "tamanho": estatisticas.st_size,
        "data_modificacao": estatisticas.st_mtime,
    }


def arquivo_atende_restricoes(arquivo, restricoes):
    """Verifica se um arquivo passa por todas as restricoes."""
    if not isinstance(arquivo, dict) or not isinstance(restricoes, dict):
        return False

    return (
        atende_restricao_extensao(arquivo, restricoes)
        and atende_restricao_nome(arquivo, restricoes)
        and atende_restricao_tamanho(arquivo, restricoes)
        and atende_restricao_data_modificacao(arquivo, restricoes)
    )


def atende_restricao_extensao(arquivo, restricoes):
    """Verifica filtro por extensao."""
    extensoes = restricoes.get("extensoes_permitidas", [])
    if not extensoes:
        return True

    extensoes_normalizadas = []
    for extensao in extensoes:
        if not isinstance(extensao, str):
            continue
        extensao = extensao.strip().lower()
        if not extensao:
            continue
        if not extensao.startswith("."):
            extensao = "." + extensao
        extensoes_normalizadas.append(extensao)

    if not extensoes_normalizadas:
        return True

    extensao_arquivo = arquivo.get("extensao", "")
    if not isinstance(extensao_arquivo, str):
        return False
    return extensao_arquivo.strip().lower() in extensoes_normalizadas


def atende_restricao_nome(arquivo, restricoes):
    """Verifica filtro por trecho no nome."""
    trecho = restricoes.get("nome_contem", "")
    if not trecho:
        return True
    if not isinstance(trecho, str):
        return False

    nome = arquivo.get("nome", "")
    if not isinstance(nome, str):
        return False
    return trecho.strip().lower() in nome.lower()


def atende_restricao_tamanho(arquivo, restricoes):
    """Verifica filtros por tamanho minimo e maximo."""
    tamanho = arquivo.get("tamanho", 0)
    tamanho_min = restricoes.get("tamanho_min", 0) or 0
    tamanho_max = restricoes.get("tamanho_max")

    if not isinstance(tamanho, int) or not isinstance(tamanho_min, int):
        return False
    if tamanho_max is not None and not isinstance(tamanho_max, int):
        return False

    if tamanho < tamanho_min:
        return False
    if tamanho_max is not None and tamanho > tamanho_max:
        return False
    return True


def atende_restricao_data_modificacao(arquivo, restricoes):
    """Verifica filtros por data de modificacao."""
    data_arquivo = arquivo.get("data_modificacao")
    if not isinstance(data_arquivo, (int, float)):
        return False

    data_min = converter_data_restricao_para_timestamp(
        restricoes.get("data_modificacao_min")
    )
    data_max = converter_data_restricao_para_timestamp(
        restricoes.get("data_modificacao_max")
    )

    if data_min is not None and data_arquivo < data_min:
        return False
    if data_max is not None and data_arquivo > data_max:
        return False
    return True


def converter_data_restricao_para_timestamp(valor):
    """Converte data de restricao em timestamp ou None quando vazia."""
    if valor is None:
        return None
    if isinstance(valor, (int, float)):
        return float(valor)
    if not isinstance(valor, str):
        return None

    valor = valor.strip()
    if not valor:
        return None

    try:
        return datetime.fromisoformat(valor).timestamp()
    except ValueError:
        return None


def verificar_permissao_leitura(caminho):
    """Verifica permissao de leitura."""
    if caminho is None:
        return False
    try:
        return os.access(caminho, os.R_OK)
    except (OSError, TypeError, ValueError):
        return False


def verificar_permissao_escrita(caminho):
    """Verifica permissao de escrita."""
    if caminho is None:
        return False
    try:
        return os.access(caminho, os.W_OK)
    except (OSError, TypeError, ValueError):
        return False
