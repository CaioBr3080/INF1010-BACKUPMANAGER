"""Conversores usados pela camada de interface."""

from datetime import datetime

__all__ = [
    "converter_inteiro_opcional",
    "converter_data_opcional",
]


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
