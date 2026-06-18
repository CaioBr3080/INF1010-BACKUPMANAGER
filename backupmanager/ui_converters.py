"""Conversores usados pela camada de interface."""

from datetime import datetime

__all__ = [
    "obter_unidade_intervalo_interface",
    "converter_intervalo_para_minutos",
    "obter_intervalo_para_interface",
    "converter_inteiro_opcional",
    "converter_data_opcional",
]


def obter_unidade_intervalo_interface(estado_interface):
    """Retorna a unidade de intervalo selecionada na UI com fallback seguro.

    Le `intervalo_unidade_var` do estado visual e aceita apenas `segundos`,
    `minutos` ou `horas`. Qualquer ausencia ou valor desconhecido retorna
    `minutos`.
    """
    unidade_var = estado_interface.get("intervalo_unidade_var")
    if unidade_var is None:
        return "minutos"
    unidade = unidade_var.get()
    if unidade not in ("segundos", "minutos", "horas"):
        return "minutos"
    return unidade


def converter_intervalo_para_minutos(valor, unidade):
    """Converte intervalo da UI para minutos quando houver equivalencia valida.

    O backend legado ainda entende minutos; por isso esta funcao transforma
    horas e minutos diretamente. Segundos abaixo de um minuto retornam `None`
    para evitar intervalo legado truncado para zero.
    """
    if valor is None:
        return None
    if unidade == "segundos":
        return max(1, valor // 60) if valor >= 60 else None
    if unidade == "horas":
        return valor * 60
    return valor


def obter_intervalo_para_interface(agendamento):
    """Retorna valor e unidade adequados para preencher os campos da UI.

    Prefere os campos atuais `intervalo_valor` e `intervalo_unidade`. Quando
    eles nao existem, usa `intervalo_minutos` legado e assume unidade
    `minutos`.
    """
    valor = agendamento.get("intervalo_valor")
    unidade = agendamento.get("intervalo_unidade", "minutos")
    if isinstance(valor, int) and valor > 0 and unidade in ("segundos", "minutos", "horas"):
        return valor, unidade

    minutos = agendamento.get("intervalo_minutos")
    if isinstance(minutos, int) and minutos > 0:
        return minutos, "minutos"
    return None, "minutos"


def converter_inteiro_opcional(texto, padrao):
    """Converte texto para inteiro nao negativo ou retorna padrao quando vazio.

    Retorna o inteiro convertido, `padrao` para texto vazio e a string
    sentinela `invalido` para numeros negativos ou texto nao numerico.
    """
    texto = texto.strip()
    if not texto:
        return padrao
    try:
        valor = int(texto)
    except ValueError:
        return "invalido"
    if valor < 0:
        return "invalido"
    return valor


def converter_data_opcional(texto):
    """Valida uma data opcional em formato ISO e retorna o texto normalizado.

    Texto vazio vira `None`, datas aceitas por `datetime.fromisoformat`
    retornam como string original e entradas invalidas retornam `invalido`.
    """
    texto = texto.strip()
    if not texto:
        return None
    try:
        datetime.fromisoformat(texto)
    except ValueError:
        return "invalido"
    return texto
