"""Controle simples de execucao automatica."""

import threading
import time
from datetime import datetime

from backupmanager import file_utils
from backupmanager.return_codes import OK

__all__ = [
    "deve_executar",
    "atualizar_estado_arquivos",
    "iniciar_monitoramento",
    "parar_monitoramento",
    "atualizar_ultima_execucao",
]

_MONITORAMENTO_ATIVO = False
_THREAD_MONITORAMENTO = None
_INTERVALO_VERIFICACAO_SEGUNDOS = 1


def deve_executar(perfil):
    """Decide se um perfil deve executar backup automaticamente agora.

    Consulta o campo `ativo` e o dicionario `agendamento` do perfil. Para tipo
    `intervalo`, compara a ultima execucao com o intervalo configurado; para
    tipo `alteracao`, compara o estado atual dos arquivos com o ultimo estado
    salvo. Retorna booleano e nao altera o perfil.
    """
    if not isinstance(perfil, dict) or not perfil.get("ativo", True):
        return False

    agendamento = perfil.get("agendamento", {})
    if agendamento.get("tipo") == "intervalo":
        return _deve_executar_por_intervalo(perfil)
    if agendamento.get("tipo") == "alteracao":
        return _deve_executar_por_alteracao(perfil)
    return False


def _deve_executar_por_intervalo(perfil):
    """Verifica execucao automatica por intervalo."""
    if not isinstance(perfil, dict) or not perfil.get("ativo", True):
        return False

    agendamento = perfil.get("agendamento", {})
    if agendamento.get("tipo") != "intervalo":
        return False

    intervalo_segundos = _obter_intervalo_em_segundos(agendamento)
    if intervalo_segundos is None:
        return False

    ultima_execucao = _converter_data_para_datetime(agendamento.get("ultima_execucao"))
    if ultima_execucao is None:
        return True

    diferenca = datetime.now() - ultima_execucao
    return diferenca.total_seconds() >= intervalo_segundos


def _obter_intervalo_em_segundos(agendamento):
    """Converte intervalo de agendamento para segundos."""
    valor = agendamento.get("intervalo_valor")
    unidade = agendamento.get("intervalo_unidade", "minutos")

    if isinstance(valor, int) and valor > 0:
        if unidade == "segundos":
            return valor
        if unidade == "horas":
            return valor * 3600
        return valor * 60

    intervalo_minutos = agendamento.get("intervalo_minutos")
    if isinstance(intervalo_minutos, int) and intervalo_minutos > 0:
        return intervalo_minutos * 60
    return None


def _deve_executar_por_alteracao(perfil):
    """Verifica se houve alteracao nos arquivos monitorados."""
    if not isinstance(perfil, dict) or not perfil.get("ativo", True):
        return False

    agendamento = perfil.get("agendamento", {})
    if agendamento.get("tipo") != "alteracao" and not agendamento.get("executar_ao_detectar_mudanca", False):
        return False

    estado_antigo = perfil.get("estado_arquivos", {})
    estado_novo = _obter_estado_atual_arquivos(perfil)
    return _comparar_estado_arquivos(estado_antigo, estado_novo)


def _obter_estado_atual_arquivos(perfil):
    """Retorna estado atual de arquivos monitorados."""
    if not isinstance(perfil, dict):
        return {}

    estado = {}
    caminhos = file_utils.listar_arquivos_de_origens(_obter_origens_monitoradas(perfil))

    for caminho in caminhos:
        arquivo = file_utils.obter_metadados_arquivo(caminho)
        if arquivo is None:
            continue
        estado[arquivo["caminho"]] = {
            "tamanho": arquivo["tamanho"],
            "data_modificacao": arquivo["data_modificacao"],
        }

    return estado


def _obter_origens_monitoradas(perfil):
    """Retorna origens ativas do modelo atual ou origens antigas quando necessario."""
    origens_configuradas = perfil.get("origens_configuradas", [])
    if isinstance(origens_configuradas, list) and origens_configuradas:
        origens = []
        for origem in origens_configuradas:
            if not isinstance(origem, dict) or not origem.get("ativo", True):
                continue
            caminho = origem.get("caminho")
            if caminho:
                origens.append(caminho)
        return origens

    origens = perfil.get("origens", [])
    if isinstance(origens, list):
        return origens
    return []


def _comparar_estado_arquivos(estado_antigo, estado_novo):
    """Compara dois estados de arquivos."""
    return estado_antigo != estado_novo


def atualizar_estado_arquivos(perfil):
    """Atualiza no perfil o retrato atual dos arquivos monitorados.

    Coleta os arquivos das origens do perfil e grava em `estado_arquivos` um
    mapa caminho -> metadados relevantes. Usada apos backup ou antes de
    monitorar alteracoes. Retorna codigo de resultado.
    """
    perfil["estado_arquivos"] = _obter_estado_atual_arquivos(perfil)
    return OK


def iniciar_monitoramento(perfis, callback_backup):
    """Inicia o monitoramento automatico em thread separada.

    Recebe a lista de perfis e uma funcao callback que sera chamada para cada
    perfil que `deve_executar`. Se o monitoramento ja estiver ativo, apenas
    retorna `OK`. O estado da thread fica encapsulado no modulo.
    """
    global _MONITORAMENTO_ATIVO, _THREAD_MONITORAMENTO
    if not isinstance(perfis, list) or not callable(callback_backup):
        return OK

    if _MONITORAMENTO_ATIVO:
        return OK

    _MONITORAMENTO_ATIVO = True
    _THREAD_MONITORAMENTO = threading.Thread(
        target=_loop_monitoramento,
        args=(perfis, callback_backup),
        daemon=True,
    )
    _THREAD_MONITORAMENTO.start()
    return OK


def parar_monitoramento():
    """Solicita parada do monitoramento automatico.

    Desliga a flag interna, aguarda a thread encerrar por curto periodo e
    limpa a referencia da thread. Retorna `OK` mesmo quando nao havia
    monitoramento ativo.
    """
    global _MONITORAMENTO_ATIVO, _THREAD_MONITORAMENTO
    _MONITORAMENTO_ATIVO = False
    if _THREAD_MONITORAMENTO is not None and _THREAD_MONITORAMENTO.is_alive():
        _THREAD_MONITORAMENTO.join(timeout=2)
    _THREAD_MONITORAMENTO = None
    return OK


def _loop_monitoramento(perfis, callback_backup):
    """Loop interno de monitoramento."""
    while _MONITORAMENTO_ATIVO:
        for perfil in perfis:
            if not _MONITORAMENTO_ATIVO:
                break
            if deve_executar(perfil):
                callback_backup(perfil.get("id"))
                atualizar_estado_arquivos(perfil)
                atualizar_ultima_execucao(perfil)
        time.sleep(_INTERVALO_VERIFICACAO_SEGUNDOS)


def atualizar_ultima_execucao(perfil):
    """Registra no perfil o horario atual como ultima execucao.

    Garante a existencia do dicionario `agendamento` e grava a data/hora em
    formato ISO. O scheduler usa esse valor para calcular proximas execucoes
    por intervalo.
    """
    if not isinstance(perfil, dict):
        return OK
    agendamento = perfil.setdefault("agendamento", {})
    agendamento["ultima_execucao"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return OK


def _converter_data_para_datetime(valor):
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

