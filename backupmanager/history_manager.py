"""Gerenciamento do historico de backups."""

import uuid
from datetime import datetime

from backupmanager.return_codes import OK

__all__ = [
    "criar_registro_historico",
    "registrar_backup",
    "consultar_historico_por_perfil",
    "listar_historico",
    "limpar_historico_perfil",
    "limpar_todo_historico",
    "gerar_resumo_historico_perfil",
]

_STATUS_HISTORICO = ("sucesso", "parcial", "erro", "sem_arquivos")


def criar_registro_historico(perfil_id, resultado):
    """Cria um registro normalizado de historico para uma execucao.

    Copia do resultado de backup os contadores, status, arquivos e erros,
    adicionando identificador do perfil e data/hora atual. A funcao nao
    adiciona o registro a nenhuma lista; apenas monta o dicionario.
    """
    if not isinstance(resultado, dict):
        resultado = {}

    return {
        "id": "hist_" + uuid.uuid4().hex[:8],
        "perfil_id": perfil_id,
        "data_hora": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "status": _normalizar_status(resultado.get("status")),
        "arquivos_processados": resultado.get("arquivos_processados", 0),
        "arquivos_copiados": resultado.get("arquivos_copiados", 0),
        "arquivos_movidos": resultado.get("arquivos_movidos", 0),
        "arquivos_recortados": resultado.get("arquivos_recortados", 0),
        "arquivos": _normalizar_arquivos(resultado.get("arquivos", [])),
        "erros": _normalizar_erros(resultado.get("erros", [])),
    }


def _normalizar_status(status):
    """Retorna status padronizado para historico."""
    if status in _STATUS_HISTORICO:
        return status
    return "erro"


def _normalizar_erros(erros):
    """Garante que erros seja sempre lista."""
    if erros is None:
        return []
    if isinstance(erros, list):
        return erros
    return [erros]


def _normalizar_arquivos(arquivos):
    """Garante lista de detalhes de arquivos processados."""
    if not isinstance(arquivos, list):
        return []

    normalizados = []
    for arquivo in arquivos:
        if isinstance(arquivo, dict):
            normalizados.append(arquivo)
    return normalizados


def registrar_backup(historico, perfil_id, resultado):
    """Registra uma execucao de backup no historico em memoria.

    Recebe a lista mutavel de historico, cria um registro normalizado e faz
    `append`. Retorna `OK` quando o registro foi adicionado. Persistencia em
    JSON e responsabilidade do controller/storage.
    """
    historico.append(criar_registro_historico(perfil_id, resultado))
    return OK


def consultar_historico_por_perfil(historico, perfil_id):
    """Retorna registros de historico pertencentes a um perfil.

    Funcao de acesso usada pela interface de historico. Nao altera a lista
    recebida e retorna nova lista com os registros filtrados.
    """
    registros = [registro for registro in historico if registro.get("perfil_id") == perfil_id]
    return OK, registros


def listar_historico(historico):
    """Retorna todos os registros de historico recebidos.

    Funcao de acesso simples para consultas globais. Mantem a mesma referencia
    da lista recebida, seguindo o padrao dos TADs em memoria do projeto.
    """
    return OK, historico


def limpar_historico_perfil(historico, perfil_id):
    """Remove registros de historico de um perfil especifico.

    Altera a lista recebida preservando apenas registros de outros perfis.
    Retorna `OK` apos a limpeza em memoria.
    """
    historico[:] = [registro for registro in historico if registro.get("perfil_id") != perfil_id]
    return OK


def limpar_todo_historico(historico):
    """Remove todos os registros de historico da lista recebida.

    A operacao esvazia a lista em memoria e nao toca em arquivos JSON.
    """
    historico.clear()
    return OK


def gerar_resumo_historico_perfil(historico, perfil_id):
    """Gera resumo numerico do historico de um perfil.

    Calcula quantidade de execucoes e totais agregados de arquivos processados
    e erros. Retorna um dicionario pronto para relatorios ou exibicao.
    """
    registros = [registro for registro in historico if registro.get("perfil_id") == perfil_id]
    total_processados = 0
    total_erros = 0

    for registro in registros:
        total_processados += registro.get("arquivos_processados", 0)
        erros = _normalizar_erros(registro.get("erros", []))
        total_erros += len(erros)

    return {
        "perfil_id": perfil_id,
        "total_execucoes": len(registros),
        "total_arquivos_processados": total_processados,
        "total_erros": total_erros,
    }

