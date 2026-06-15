"""Controle simples de execucao automatica."""

import threading
import time
from datetime import datetime

from backupmanager import file_utils
from backupmanager.return_codes import OK

MONITORAMENTO_ATIVO = False
THREAD_MONITORAMENTO = None
INTERVALO_VERIFICACAO_SEGUNDOS = 1


def deve_executar(perfil):
    """Verifica se um perfil deve executar automaticamente."""
    if not isinstance(perfil, dict) or not perfil.get("ativo", True):
        return False

    agendamento = perfil.get("agendamento", {})
    if agendamento.get("tipo") == "intervalo":
        return deve_executar_por_intervalo(perfil)
    if agendamento.get("tipo") == "alteracao":
        return deve_executar_por_alteracao(perfil)
    return False


def deve_executar_por_intervalo(perfil):
    """Verifica execucao automatica por intervalo de minutos."""
    if not isinstance(perfil, dict) or not perfil.get("ativo", True):
        return False

    agendamento = perfil.get("agendamento", {})
    if agendamento.get("tipo") != "intervalo":
        return False

    intervalo = agendamento.get("intervalo_minutos")
    if not isinstance(intervalo, int) or intervalo <= 0:
        return False

    ultima_execucao = converter_data_para_datetime(agendamento.get("ultima_execucao"))
    if ultima_execucao is None:
        return True

    diferenca = datetime.now() - ultima_execucao
    return diferenca.total_seconds() >= intervalo * 60


def deve_executar_por_alteracao(perfil):
    """Verifica se houve alteracao nos arquivos monitorados."""
    if not isinstance(perfil, dict) or not perfil.get("ativo", True):
        return False

    agendamento = perfil.get("agendamento", {})
    if agendamento.get("tipo") != "alteracao" and not agendamento.get("executar_ao_detectar_mudanca", False):
        return False

    estado_antigo = perfil.get("estado_arquivos", {})
    estado_novo = obter_estado_atual_arquivos(perfil)
    return comparar_estado_arquivos(estado_antigo, estado_novo)


def obter_estado_atual_arquivos(perfil):
    """Retorna estado atual de arquivos monitorados."""
    if not isinstance(perfil, dict):
        return {}

    estado = {}
    caminhos = file_utils.listar_arquivos_de_origens(perfil.get("origens", []))

    for caminho in caminhos:
        arquivo = file_utils.obter_metadados_arquivo(caminho)
        if arquivo is None:
            continue
        estado[arquivo["caminho"]] = {
            "tamanho": arquivo["tamanho"],
            "data_modificacao": arquivo["data_modificacao"],
        }

    return estado


def comparar_estado_arquivos(estado_antigo, estado_novo):
    """Compara dois estados de arquivos."""
    return estado_antigo != estado_novo


def atualizar_estado_arquivos(perfil):
    """Atualiza o estado de arquivos dentro do perfil."""
    perfil["estado_arquivos"] = obter_estado_atual_arquivos(perfil)
    return OK


def iniciar_monitoramento(perfis, callback_backup):
    """Inicia monitoramento simples em uma thread daemon."""
    global MONITORAMENTO_ATIVO, THREAD_MONITORAMENTO
    if not isinstance(perfis, list) or not callable(callback_backup):
        return OK

    if MONITORAMENTO_ATIVO:
        return OK

    MONITORAMENTO_ATIVO = True
    THREAD_MONITORAMENTO = threading.Thread(
        target=loop_monitoramento,
        args=(perfis, callback_backup),
        daemon=True,
    )
    THREAD_MONITORAMENTO.start()
    return OK


def parar_monitoramento():
    """Para monitoramento simples."""
    global MONITORAMENTO_ATIVO, THREAD_MONITORAMENTO
    MONITORAMENTO_ATIVO = False
    if THREAD_MONITORAMENTO is not None and THREAD_MONITORAMENTO.is_alive():
        THREAD_MONITORAMENTO.join(timeout=2)
    THREAD_MONITORAMENTO = None
    return OK


def loop_monitoramento(perfis, callback_backup):
    """Loop interno de monitoramento."""
    while MONITORAMENTO_ATIVO:
        for perfil in perfis:
            if not MONITORAMENTO_ATIVO:
                break
            if deve_executar(perfil):
                callback_backup(perfil.get("id"))
                atualizar_estado_arquivos(perfil)
                atualizar_ultima_execucao(perfil)
        time.sleep(INTERVALO_VERIFICACAO_SEGUNDOS)


def atualizar_ultima_execucao(perfil):
    """Atualiza ultima execucao do agendamento."""
    if not isinstance(perfil, dict):
        return OK
    agendamento = perfil.setdefault("agendamento", {})
    agendamento["ultima_execucao"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return OK


def converter_data_para_datetime(valor):
    """Converte valor de data em datetime."""
    if valor is None:
        return None
    if isinstance(valor, datetime):
        return valor
    if isinstance(valor, (int, float)):
        return datetime.fromtimestamp(valor)
    if not isinstance(valor, str):
        return None

    valor = valor.strip()
    if not valor:
        return None

    try:
        return datetime.fromisoformat(valor)
    except ValueError:
        return None