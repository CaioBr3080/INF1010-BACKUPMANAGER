"""Funcoes para criar, consultar e alterar perfis de backup."""

import uuid

from backupmanager.return_codes import (
    OK,
    ERRO_NOME_INVALIDO,
    ERRO_PERFIL_NAO_ENCONTRADO,
)

__all__ = [
    "criar_restricoes_padrao",
    "criar_destino_tipo",
    "criar_tipo_arquivo",
    "criar_origem_configurada",
    "validar_nome_perfil",
    "criar_perfil",
    "consultar_perfil",
    "listar_perfis",
    "alterar_nome_perfil",
    "excluir_perfil",
    "ativar_perfil",
    "desativar_perfil",
]


def criar_restricoes_padrao():
    """Cria restricoes vazias no formato aceito pelo motor de backup.

    Retorna um dicionario novo com todas as chaves usadas para filtrar
    arquivos por extensao, nome, tamanho e data de modificacao. A funcao
    nao altera estado global e deve ser usada sempre que uma origem/tipo
    precisar nascer sem filtros ativos.
    """
    return {
        "extensoes_permitidas": [],
        "regras_nome": [],
        "tamanho_min": 0,
        "tamanho_max": None,
        "data_modificacao_min": None,
        "data_modificacao_max": None,
    }


def criar_destino_tipo(caminho, operacao="copiar"):
    """Cria um destino de backup vinculado a um tipo de arquivo.

    `caminho` deve ser a pasta de destino e `operacao` deve indicar como o
    arquivo sera tratado ao chegar nesse destino (`copiar`, `mover` ou
    `recortar`). A funcao apenas monta a estrutura em memoria; ela nao valida
    se a pasta existe e nao executa operacao de arquivo.
    """
    return {
        "caminho": caminho,
        "operacao": operacao,
    }


def criar_tipo_arquivo(nome, restricoes=None, destinos=None):
    """Cria uma configuracao de tipo/filtro dentro de uma origem.

    O tipo agrupa um nome exibido na interface, as restricoes aplicadas aos
    arquivos daquela origem e a lista de destinos que receberao os arquivos
    aprovados. Quando `restricoes` ou `destinos` nao sao informados, a funcao
    cria estruturas vazias e independentes para evitar compartilhamento
    acidental entre perfis.
    """
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
    """Cria uma origem no modelo atual origem -> tipo -> destino.

    `caminho` representa a pasta de entrada monitorada pelo perfil. A origem
    nasce ativa e sem tipos cadastrados; os tipos devem ser adicionados depois
    por quem estiver montando a configuracao. A funcao nao acessa o disco.
    """
    return {
        "id": "origem_" + uuid.uuid4().hex[:8],
        "caminho": caminho,
        "ativo": True,
        "tipos_arquivo": [],
    }


def _gerar_id_perfil(perfis):
    """Gera um identificador unico para um novo perfil."""
    del perfis
    return "perfil_" + uuid.uuid4().hex[:8]


def validar_nome_perfil(nome):
    """Valida o nome usado para criar ou renomear um perfil.

    Aceita apenas strings nao vazias apos `strip`. Retorna `OK` quando o
    nome pode ser persistido no perfil e `ERRO_NOME_INVALIDO` quando a entrada
    nao representa um nome utilizavel.
    """
    if not isinstance(nome, str) or not nome.strip():
        return ERRO_NOME_INVALIDO
    return OK


def criar_perfil(nome):
    """Cria um perfil novo em memoria no modelo atual.

    Valida o nome, gera um identificador unico, inicializa
    `origens_configuradas` e `ativo`.
    A funcao nao salva JSON e nao registra o perfil em nenhuma lista; quem
    chama decide onde armazenar o dicionario retornado.
    """
    codigo = validar_nome_perfil(nome)
    if codigo != OK:
        return codigo, None

    perfil = {
        "id": _gerar_id_perfil([]),
        "nome": nome.strip(),
        "origens_configuradas": [],
        "ativo": True,
    }
    return OK, perfil


def consultar_perfil(perfis, perfil_id):
    """Consulta um perfil pelo identificador dentro de uma lista.

    Esta e a funcao de acesso principal para recuperar um perfil do TAD.
    Retorna `(OK, perfil)` mantendo a referencia original encontrada na lista,
    permitindo alteracao controlada por outras operacoes do modulo. Quando o
    id nao existe, retorna `(ERRO_PERFIL_NAO_ENCONTRADO, None)`.
    """
    for perfil in perfis:
        if perfil.get("id") == perfil_id:
            return OK, perfil
    return ERRO_PERFIL_NAO_ENCONTRADO, None


def listar_perfis(perfis):
    """Retorna a colecao de perfis atualmente mantida em memoria.

    Funcao de acesso usada pelo controller para expor a lista de perfis para a
    interface. Ela nao copia a lista, porque o controller e o dono do estado e
    controla quando mutacoes podem acontecer.
    """
    return OK, perfis


def alterar_nome_perfil(perfis, perfil_id, novo_nome):
    """Altera o nome de um perfil existente apos validacao.

    Busca o perfil por `perfil_id`, valida `novo_nome` com
    `validar_nome_perfil` e grava o nome sem espacos externos. Retorna codigo
    de erro quando o perfil nao existe ou o nome e invalido.
    """
    codigo = validar_nome_perfil(novo_nome)
    if codigo != OK:
        return codigo

    codigo, perfil = consultar_perfil(perfis, perfil_id)
    if codigo != OK:
        return codigo

    perfil["nome"] = novo_nome.strip()
    return OK


def excluir_perfil(perfis, perfil_id):
    """Remove da lista o perfil identificado por `perfil_id`.

    A operacao altera a lista recebida em memoria e nao toca em persistencia.
    Retorna `OK` se removeu o item ou `ERRO_PERFIL_NAO_ENCONTRADO` se o id nao
    pertence a lista.
    """
    codigo, perfil = consultar_perfil(perfis, perfil_id)
    if codigo != OK:
        return codigo

    perfis.remove(perfil)
    return OK


def ativar_perfil(perfis, perfil_id):
    """Marca um perfil existente como ativo para execucoes futuras.

    A funcao altera somente o campo `ativo` do perfil encontrado. O backup
    automatico e manual deve consultar esse campo antes de executar.
    """
    codigo, perfil = consultar_perfil(perfis, perfil_id)
    if codigo != OK:
        return codigo
    perfil["ativo"] = True
    return OK


def desativar_perfil(perfis, perfil_id):
    """Marca um perfil existente como inativo.

    Perfis inativos permanecem cadastrados e configurados, mas devem ser
    ignorados por rotinas de execucao ate serem ativados novamente.
    """
    codigo, perfil = consultar_perfil(perfis, perfil_id)
    if codigo != OK:
        return codigo
    perfil["ativo"] = False
    return OK


