"""Validacao de perfis, origens, tipos, destinos e operacoes de backup."""

from backupmanager.domain import perfil_manager
from backupmanager.return_codes import (
    OK,
    ERRO_DADOS_INVALIDOS,
    ERRO_DESTINO_INVALIDO,
    ERRO_OPERACAO_INVALIDA,
    ERRO_ORIGEM_INVALIDA,
)

__all__ = [
    "validar_perfil_para_backup",
    "validar_perfil_configurado_para_backup",
    "validar_destinos_do_tipo",
]

_OPERACOES_VALIDAS = ("copiar", "mover", "recortar")


def validar_perfil_para_backup(perfil):
    """Valida o contrato minimo para executar backup.

    Aceita somente o modelo atual `origens_configuradas`. Retorna
    `ERRO_DADOS_INVALIDOS` quando a entrada nao e um perfil e delega a
    validacao estrutural para `validar_perfil_configurado_para_backup`.
    """
    if not isinstance(perfil, dict):
        return ERRO_DADOS_INVALIDOS

    return validar_perfil_configurado_para_backup(perfil)


def validar_perfil_configurado_para_backup(perfil):
    """Valida um perfil no modelo origem -> tipo -> destino.

    Confere se existem origens, se cada origem ativa possui caminho, se tipos
    e destinos usam listas/dicionarios validos e se ha pelo menos um destino
    configurado. Tambem valida conflitos de operacao por tipo.
    """
    origens = perfil_manager.obter_origens_configuradas(perfil)
    if not origens:
        return ERRO_ORIGEM_INVALIDA

    possui_destino = False
    for origem in origens:
        if not perfil_manager.origem_e_valida(origem):
            return ERRO_ORIGEM_INVALIDA
        if perfil_manager.origem_esta_ativa(origem) and not perfil_manager.obter_caminho_origem(origem):
            return ERRO_ORIGEM_INVALIDA
        for tipo in perfil_manager.obter_tipos_origem(origem):
            if not perfil_manager.tipo_e_valido(tipo):
                return ERRO_DADOS_INVALIDOS
            destinos = perfil_manager.obter_destinos_tipo(tipo)
            if destinos:
                possui_destino = True
            if not perfil_manager.origem_esta_ativa(origem) or not perfil_manager.tipo_esta_ativo(tipo):
                continue
            codigo = validar_destinos_do_tipo(tipo)
            if codigo != OK:
                return codigo

    if not possui_destino:
        return ERRO_DESTINO_INVALIDO
    return OK


def validar_destinos_do_tipo(tipo):
    """Valida a lista de destinos de um tipo de arquivo.

    Cada destino precisa ter caminho e operacao valida. Operacoes de remocao
    (`mover` ou `recortar`) nao podem coexistir com multiplos destinos, pois a
    origem deixaria de existir apos a primeira remocao.
    """
    destinos = perfil_manager.obter_destinos_tipo(tipo)
    operacoes_remocao = []

    for destino in destinos:
        if not perfil_manager.destino_e_valido(destino) or not perfil_manager.obter_caminho_destino(destino):
            return ERRO_DESTINO_INVALIDO
        operacao = perfil_manager.obter_operacao_destino(destino)
        if operacao not in _OPERACOES_VALIDAS:
            return ERRO_OPERACAO_INVALIDA
        if operacao in ("mover", "recortar"):
            operacoes_remocao.append(destino)

    if operacoes_remocao and len(destinos) > 1:
        return ERRO_OPERACAO_INVALIDA

    return OK

