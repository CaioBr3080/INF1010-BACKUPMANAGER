"""Gerenciamento do historico de backups."""

import uuid
from datetime import datetime

from backupmanager.return_codes import OK

STATUS_HISTORICO = ("sucesso", "parcial", "erro", "sem_arquivos")


def criar_registro_historico(perfil_id, resultado):
    """Cria um registro de historico a partir do resultado do backup."""
    if not isinstance(resultado, dict):
        resultado = {}

    return {
        "id": "hist_" + uuid.uuid4().hex[:8],
        "perfil_id": perfil_id,
        "data_hora": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "status": normalizar_status(resultado.get("status")),
        "arquivos_processados": resultado.get("arquivos_processados", 0),
        "arquivos_copiados": resultado.get("arquivos_copiados", 0),
        "arquivos_movidos": resultado.get("arquivos_movidos", 0),
        "erros": normalizar_erros(resultado.get("erros", [])),
    }


def normalizar_status(status):
    """Retorna status padronizado para historico."""
    if status in STATUS_HISTORICO:
        return status
    return "erro"


def normalizar_erros(erros):
    """Garante que erros seja sempre lista."""
    if erros is None:
        return []
    if isinstance(erros, list):
        return erros
    return [erros]


def registrar_backup(historico, perfil_id, resultado):
    """Adiciona uma execucao ao historico."""
    historico.append(criar_registro_historico(perfil_id, resultado))
    return OK


def consultar_historico_por_perfil(historico, perfil_id):
    """Lista registros de historico de um perfil."""
    registros = [registro for registro in historico if registro.get("perfil_id") == perfil_id]
    return OK, registros


def listar_historico(historico):
    """Retorna todos os registros de historico."""
    return OK, historico


def limpar_historico_perfil(historico, perfil_id):
    """Remove registros de historico de um perfil."""
    historico[:] = [registro for registro in historico if registro.get("perfil_id") != perfil_id]
    return OK


def limpar_todo_historico(historico):
    """Remove todos os registros de historico."""
    historico.clear()
    return OK


def preparar_historico_para_tabela(registros):
    """Formata uma lista de registros de historico para exibicao em tabela.
    Converte listas internas em strings e extrai apenas as colunas visuais."""
    linhas = []
    for reg in registros:
        erros = reg.get("erros", [])
        erros_str = ", ".join(erros) if erros else "Nenhum erro"
        
        linha = (
            reg.get("data_hora", ""),
            reg.get("status", "desconhecido").upper(),
            reg.get("arquivos_processados", 0),
            reg.get("arquivos_copiados", 0),
            reg.get("arquivos_movidos", 0),
            erros_str
        )
        linhas.append(linha)
        
    return OK, linhas


def gerar_resumo_historico_perfil(historico, perfil_id):
    """Gera resumo simples de execucoes de um perfil."""
    registros = [registro for registro in historico if registro.get("perfil_id") == perfil_id]
    total_processados = 0
    total_erros = 0

    for registro in registros:
        total_processados += registro.get("arquivos_processados", 0)
        erros = normalizar_erros(registro.get("erros", []))
        total_erros += len(erros)

    return {
        "perfil_id": perfil_id,
        "total_execucoes": len(registros),
        "total_arquivos_processados": total_processados,
        "total_erros": total_erros,
    }