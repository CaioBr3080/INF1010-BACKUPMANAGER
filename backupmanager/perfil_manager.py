"""Funcoes para criar, consultar e alterar perfis de backup."""

import uuid

from backupmanager.return_codes import (
    OK,
    ERRO_NOME_INVALIDO,
    ERRO_OPERACAO_INVALIDA,
    ERRO_PERFIL_NAO_ENCONTRADO,
)

OPERACOES_VALIDAS = ("copiar", "mover", "recortar")


def criar_restricoes_padrao():
    """Cria o dicionario padrao de restricoes de um perfil."""
    return {
        "extensoes_permitidas": [],
        "nome_contem": "",
        "tamanho_min": 0,
        "tamanho_max": None,
        "data_modificacao_min": None,
        "data_modificacao_max": None,
    }


def criar_agendamento_padrao():
    """Cria o dicionario padrao de agendamento de um perfil."""
    return {
        "tipo": "manual",
        "intervalo_minutos": None,
        "executar_ao_detectar_mudanca": False,
        "ultima_execucao": None,
    }


def criar_destino_tipo(caminho, operacao="copiar"):
    """Cria destino vinculado a um tipo de arquivo."""
    return {
        "caminho": caminho,
        "operacao": operacao,
    }


def criar_tipo_arquivo(nome, restricoes=None, destinos=None):
    """Cria configuracao de tipo de arquivo para uma origem."""
    if restricoes is None:
        restricoes = criar_restricoes_padrao()
    if destinos is None:
        destinos = []

    return {
        "id": "tipo_" + uuid.uuid4().hex[:8],
        "nome": nome,
        "ativo": True,
        "restricoes": restricoes,
        "destinos": destinos,
    }


def criar_origem_configurada(caminho):
    """Cria origem com tipos e destinos relacionados."""
    return {
        "id": "origem_" + uuid.uuid4().hex[:8],
        "caminho": caminho,
        "ativo": True,
        "tipos_arquivo": [],
    }


def gerar_id_perfil(perfis):
    """Gera um identificador unico para um novo perfil."""
    del perfis
    return "perfil_" + uuid.uuid4().hex[:8]


def validar_nome_perfil(nome):
    """Valida se o nome do perfil foi preenchido."""
    if not isinstance(nome, str) or not nome.strip():
        return ERRO_NOME_INVALIDO
    return OK


def criar_perfil(nome):
    """Cria um perfil usando dicionario, sem persisti-lo."""
    codigo = validar_nome_perfil(nome)
    if codigo != OK:
        return codigo, None

    perfil = {
        "id": gerar_id_perfil([]),
        "nome": nome.strip(),
        "origens": [],
        "destinos": [],
        "operacao": "copiar",
        "restricoes": criar_restricoes_padrao(),
        "origens_configuradas": [],
        "agendamento": criar_agendamento_padrao(),
        "estado_arquivos": {},
        "ativo": True,
    }
    return OK, perfil


def consultar_perfil(perfis, perfil_id):
    """Busca um perfil por id em uma lista de perfis."""
    for perfil in perfis:
        if perfil.get("id") == perfil_id:
            return OK, perfil
    return ERRO_PERFIL_NAO_ENCONTRADO, None


def listar_perfis(perfis):
    """Retorna a lista de perfis recebida."""
    return OK, perfis


def alterar_nome_perfil(perfis, perfil_id, novo_nome):
    """Altera o nome de um perfil existente."""
    codigo = validar_nome_perfil(novo_nome)
    if codigo != OK:
        return codigo

    codigo, perfil = consultar_perfil(perfis, perfil_id)
    if codigo != OK:
        return codigo

    perfil["nome"] = novo_nome.strip()
    return OK


def excluir_perfil(perfis, perfil_id):
    """Remove um perfil da lista pelo id."""
    codigo, perfil = consultar_perfil(perfis, perfil_id)
    if codigo != OK:
        return codigo

    perfis.remove(perfil)
    return OK


def ativar_perfil(perfis, perfil_id):
    """Marca um perfil como ativo."""
    codigo, perfil = consultar_perfil(perfis, perfil_id)
    if codigo != OK:
        return codigo
    perfil["ativo"] = True
    return OK


def desativar_perfil(perfis, perfil_id):
    """Marca um perfil como inativo."""
    codigo, perfil = consultar_perfil(perfis, perfil_id)
    if codigo != OK:
        return codigo
    perfil["ativo"] = False
    return OK


def adicionar_origem(perfis, perfil_id, caminho):
    """Adiciona uma pasta de origem ao perfil."""
    codigo, perfil = consultar_perfil(perfis, perfil_id)
    if codigo != OK:
        return codigo
    if caminho not in perfil["origens"]:
        perfil["origens"].append(caminho)
    return OK


def remover_origem(perfis, perfil_id, caminho):
    """Remove uma pasta de origem do perfil."""
    codigo, perfil = consultar_perfil(perfis, perfil_id)
    if codigo != OK:
        return codigo
    if caminho in perfil["origens"]:
        perfil["origens"].remove(caminho)
    return OK


def adicionar_destino(perfis, perfil_id, caminho):
    """Adiciona uma pasta de destino ao perfil."""
    codigo, perfil = consultar_perfil(perfis, perfil_id)
    if codigo != OK:
        return codigo
    if caminho not in perfil["destinos"]:
        perfil["destinos"].append(caminho)
    return OK


def remover_destino(perfis, perfil_id, caminho):
    """Remove uma pasta de destino do perfil."""
    codigo, perfil = consultar_perfil(perfis, perfil_id)
    if codigo != OK:
        return codigo
    if caminho in perfil["destinos"]:
        perfil["destinos"].remove(caminho)
    return OK


def alterar_operacao(perfis, perfil_id, operacao):
    """Altera a operacao do perfil para copiar ou mover."""
    if operacao not in OPERACOES_VALIDAS:
        return ERRO_OPERACAO_INVALIDA

    codigo, perfil = consultar_perfil(perfis, perfil_id)
    if codigo != OK:
        return codigo

    perfil["operacao"] = operacao
    return OK


def alterar_restricoes(perfis, perfil_id, restricoes):
    """Substitui as restricoes de um perfil."""
    codigo, perfil = consultar_perfil(perfis, perfil_id)
    if codigo != OK:
        return codigo
    perfil["restricoes"] = restricoes
    return OK


def alterar_agendamento(perfis, perfil_id, agendamento):
    """Substitui o agendamento de um perfil."""
    codigo, perfil = consultar_perfil(perfis, perfil_id)
    if codigo != OK:
        return codigo
    perfil["agendamento"] = agendamento
    return OK
