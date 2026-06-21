"""Funcoes auxiliares para arquivos e diretorios."""

import os
from pathlib import Path
from datetime import datetime

from backupmanager.domain import perfil_manager
from backupmanager.return_codes import OK, ERRO_DADOS_INVALIDOS

__all__ = [
    "caminho_existe",
    "caminho_e_diretorio",
    "listar_arquivos_em_origem",
    "listar_arquivos_de_origens",
    "obter_extensao",
    "obter_metadados_arquivo",
    "arquivo_e_valido",
    "obter_caminho_arquivo",
    "obter_nome_arquivo",
    "obter_extensao_arquivo",
    "obter_tamanho_arquivo",
    "obter_data_modificacao_arquivo",
    "obter_nome_tipo_arquivo",
    "associar_tipo_ao_arquivo",
    "associar_origem_ao_arquivo",
    "iniciar_tipos_incluidos_arquivo",
    "adicionar_tipo_incluido_arquivo",
    "arquivo_possui_tipo_incluido",
    "definir_incluido_arquivo",
    "arquivo_atende_restricoes",
    "verificar_permissao_leitura",
    "verificar_permissao_escrita",
]


def caminho_existe(caminho):
    """Verifica se um caminho existe no sistema de arquivos.

    Retorna `True` apenas quando `caminho` e um valor aceito por `Path` e
    aponta para algo existente. Entradas nulas, vazias ou invalidas retornam
    `False` em vez de propagar excecoes.
    """
    if caminho is None:
        return False
    try:
        return Path(caminho).exists()
    except (OSError, TypeError, ValueError):
        return False


def caminho_e_diretorio(caminho):
    """Verifica se um caminho existe e representa uma pasta.

    Usada pelo controller antes de aceitar origens/destinos escolhidos pelo
    usuario. Retorna `False` para arquivos, caminhos inexistentes ou entradas
    invalidas.
    """
    if caminho is None:
        return False
    try:
        return Path(caminho).is_dir()
    except (OSError, TypeError, ValueError):
        return False


def listar_arquivos_em_origem(origem):
    """Lista apenas arquivos diretamente dentro de uma origem.

    Nao percorre subpastas. Essa escolha define o comportamento do backup:
    apenas arquivos no nivel imediato da origem sao candidatos. Retorna lista
    de caminhos em texto ou lista vazia quando a origem e invalida.
    """
    if not caminho_e_diretorio(origem):
        return []

    arquivos = []
    try:
        for item in Path(origem).iterdir():
            if item.is_file():
                arquivos.append(str(item))
    except (OSError, TypeError, ValueError):
        return []
    return arquivos


def listar_arquivos_de_origens(origens):
    """Lista arquivos diretamente dentro de varias origens.

    Recebe uma lista de pastas e concatena o resultado de
    `listar_arquivos_em_origem` para cada item. Entradas invalidas sao
    ignoradas pela funcao chamada.
    """
    if not isinstance(origens, list):
        return []

    arquivos = []
    for origem in origens:
        arquivos.extend(listar_arquivos_em_origem(origem))
    return arquivos


def obter_extensao(caminho):
    """Retorna a extensao de um arquivo em minusculas.

    A extensao inclui o ponto inicial, como `.pdf`. Se o caminho nao possuir
    extensao ou for invalido, retorna string vazia.
    """
    if caminho is None:
        return ""
    try:
        return Path(caminho).suffix.lower()
    except (OSError, TypeError, ValueError):
        return ""


def obter_metadados_arquivo(caminho):
    """Monta o dicionario de metadados de um arquivo real.

    Quando `caminho` aponta para um arquivo, devolve dicionario com nome,
    caminho, extensao, tamanho em bytes e timestamp de modificacao. Retorna
    `None` para pastas, arquivos inexistentes ou erros de acesso.
    """
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


def arquivo_e_valido(arquivo):
    """Indica se a entrada possui formato minimo de metadados de arquivo."""
    return isinstance(arquivo, dict)


def obter_caminho_arquivo(arquivo):
    """Retorna o caminho completo de um arquivo de metadados."""
    if not arquivo_e_valido(arquivo):
        return ""
    caminho = arquivo.get("caminho", "")
    if not isinstance(caminho, str):
        return ""
    return caminho


def obter_nome_arquivo(arquivo):
    """Retorna o nome do arquivo de metadados."""
    if not arquivo_e_valido(arquivo):
        return ""
    nome = arquivo.get("nome", "")
    if isinstance(nome, str) and nome:
        return nome
    return Path(obter_caminho_arquivo(arquivo)).name


def obter_extensao_arquivo(arquivo):
    """Retorna a extensao registrada nos metadados do arquivo."""
    if not arquivo_e_valido(arquivo):
        return ""
    extensao = arquivo.get("extensao", "")
    if not isinstance(extensao, str):
        return ""
    return extensao


def obter_tamanho_arquivo(arquivo):
    """Retorna o tamanho em bytes registrado nos metadados."""
    if not arquivo_e_valido(arquivo):
        return 0
    tamanho = arquivo.get("tamanho", 0)
    if not isinstance(tamanho, int):
        return 0
    return tamanho


def obter_data_modificacao_arquivo(arquivo):
    """Retorna o timestamp de modificacao registrado nos metadados."""
    if not arquivo_e_valido(arquivo):
        return None
    return arquivo.get("data_modificacao")


def obter_nome_tipo_arquivo(arquivo):
    """Retorna o nome do tipo associado aos metadados do arquivo."""
    if not arquivo_e_valido(arquivo):
        return ""
    nome = arquivo.get("tipo_nome", "")
    if not isinstance(nome, str):
        return ""
    return nome


def associar_tipo_ao_arquivo(arquivo, tipo_id, tipo_nome):
    """Associa informacoes de tipo ao dicionario de metadados do arquivo."""
    if not arquivo_e_valido(arquivo):
        return None
    arquivo["tipo_id"] = tipo_id
    arquivo["tipo_nome"] = tipo_nome
    return arquivo


def associar_origem_ao_arquivo(arquivo, origem):
    """Registra a origem usada na pre-visualizacao do arquivo."""
    if not arquivo_e_valido(arquivo):
        return None
    arquivo["origem"] = origem
    return arquivo


def iniciar_tipos_incluidos_arquivo(arquivo):
    """Inicializa a lista de tipos incluidos na pre-visualizacao."""
    if not arquivo_e_valido(arquivo):
        return None
    arquivo["tipos_incluidos"] = []
    return arquivo


def adicionar_tipo_incluido_arquivo(arquivo, tipo_nome):
    """Adiciona um tipo aprovado na pre-visualizacao do arquivo."""
    if not arquivo_e_valido(arquivo):
        return None
    if "tipos_incluidos" not in arquivo or not isinstance(arquivo["tipos_incluidos"], list):
        arquivo["tipos_incluidos"] = []
    arquivo["tipos_incluidos"].append(tipo_nome)
    return arquivo


def arquivo_possui_tipo_incluido(arquivo):
    """Indica se a pre-visualizacao marcou algum tipo incluido."""
    if not arquivo_e_valido(arquivo):
        return False
    return bool(arquivo.get("tipos_incluidos", []))


def definir_incluido_arquivo(arquivo, incluido):
    """Define o estado de inclusao de um arquivo de pre-visualizacao.

    Esta e a funcao publica para alterar o campo `incluido` do TAD Arquivo.
    Recebe o dicionario de metadados e um valor interpretavel como booleano,
    grava `True` ou `False` internamente e retorna `OK`. Entradas que nao sao
    metadados validos retornam `ERRO_DADOS_INVALIDOS`.
    """
    if not arquivo_e_valido(arquivo):
        return ERRO_DADOS_INVALIDOS
    arquivo["incluido"] = bool(incluido)
    return OK


def arquivo_atende_restricoes(arquivo, restricoes):
    """Verifica se um arquivo atende a todas as restricoes configuradas.

    Aplica filtros de extensao, nome, tamanho e data de modificacao sobre um
    dicionario de metadados. Retorna `True` somente quando todos os filtros
    ativos aceitam o arquivo. Dados invalidos retornam `False`.
    """
    if not isinstance(arquivo, dict) or not isinstance(restricoes, dict):
        return False

    return (
        _atende_restricao_extensao(arquivo, restricoes)
        and _atende_restricao_nome(arquivo, restricoes)
        and _atende_restricao_tamanho(arquivo, restricoes)
        and _atende_restricao_data_modificacao(arquivo, restricoes)
    )


def _atende_restricao_extensao(arquivo, restricoes):
    """Verifica filtro por extensao."""
    extensoes = perfil_manager.obter_extensoes_restricoes(restricoes)
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

    extensao_arquivo = obter_extensao_arquivo(arquivo)
    if not isinstance(extensao_arquivo, str):
        return False
    return extensao_arquivo.strip().lower() in extensoes_normalizadas


def _atende_restricao_nome(arquivo, restricoes):
    """Verifica filtros por nome do arquivo."""
    nome = obter_nome_arquivo(arquivo)
    if not isinstance(nome, str):
        return False

    regras = _normalizar_regras_nome(restricoes)
    if regras:
        for regra in regras:
            if _nome_atende_regra(nome, regra):
                return True
        return False

    return True


def _normalizar_regras_nome(restricoes):
    """Normaliza regras novas de nome, ignorando entradas invalidas."""
    regras = perfil_manager.obter_regras_nome_restricoes(restricoes)

    normalizadas = []
    for regra in regras:
        valor = perfil_manager.obter_valor_regra_nome(regra)
        if not isinstance(valor, str) or not valor.strip():
            continue
        normalizadas.append(
            perfil_manager.criar_regra_nome(
                valor.strip(),
                perfil_manager.obter_modo_regra_nome(regra),
            )
        )
    return normalizadas


def _nome_atende_regra(nome, regra):
    """Indica se o nome atende uma regra normalizada."""
    nome_normalizado = nome.strip().lower()
    valor = perfil_manager.obter_valor_regra_nome(regra).strip().lower()
    if not valor:
        return True
    if perfil_manager.obter_modo_regra_nome(regra) == "exato":
        nome_sem_extensao = Path(nome_normalizado).stem
        return nome_normalizado == valor or nome_sem_extensao == valor
    return valor in nome_normalizado


def _atende_restricao_tamanho(arquivo, restricoes):
    """Verifica filtros por tamanho minimo e maximo."""
    tamanho = obter_tamanho_arquivo(arquivo)
    tamanho_min = perfil_manager.obter_tamanho_min_restricoes(restricoes)
    tamanho_max = perfil_manager.obter_tamanho_max_restricoes(restricoes)

    if not isinstance(tamanho, int) or not isinstance(tamanho_min, int):
        return False
    if tamanho_max is not None and not isinstance(tamanho_max, int):
        return False

    if tamanho < tamanho_min:
        return False
    if tamanho_max is not None and tamanho > tamanho_max:
        return False
    return True


def _atende_restricao_data_modificacao(arquivo, restricoes):
    """Verifica filtros por data de modificacao."""
    data_arquivo = obter_data_modificacao_arquivo(arquivo)
    if not isinstance(data_arquivo, (int, float)):
        return False

    data_min = _converter_data_restricao_para_timestamp(
        perfil_manager.obter_data_min_restricoes(restricoes)
    )
    data_max = _converter_data_restricao_para_timestamp(
        perfil_manager.obter_data_max_restricoes(restricoes)
    )

    if data_min is not None and data_arquivo < data_min:
        return False
    if data_max is not None and data_arquivo > data_max:
        return False
    return True


def _converter_data_restricao_para_timestamp(valor):
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
    """Verifica permissao de leitura em um caminho.

    Retorna `True` quando o sistema operacional informa acesso de leitura.
    Entradas invalidas ou erros de sistema retornam `False`.
    """
    if caminho is None:
        return False
    try:
        return os.access(caminho, os.R_OK)
    except (OSError, TypeError, ValueError):
        return False


def verificar_permissao_escrita(caminho):
    """Verifica permissao de escrita em um caminho.

    Usada para validar destinos antes de operacoes de arquivo. Retorna `False`
    para entradas invalidas ou quando o sistema operacional nega escrita.
    """
    if caminho is None:
        return False
    try:
        return os.access(caminho, os.W_OK)
    except (OSError, TypeError, ValueError):
        return False
