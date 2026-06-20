"""Funcoes para criar, consultar e alterar perfis de backup."""

import uuid

from backupmanager.return_codes import (
    OK,
    ERRO_DADOS_INVALIDOS,
    ERRO_NOME_INVALIDO,
    ERRO_PERFIL_NAO_ENCONTRADO,
)

__all__ = [
    "criar_restricoes_padrao",
    "criar_restricoes",
    "criar_destino_tipo",
    "criar_tipo_arquivo",
    "criar_origem_configurada",
    "validar_nome_perfil",
    "criar_perfil",
    "consultar_perfil",
    "listar_perfis",
    "obter_id_perfil",
    "obter_nome_perfil",
    "perfil_esta_ativo",
    "obter_origens_configuradas",
    "perfil_possui_origens_configuradas",
    "alterar_nome_perfil",
    "alterar_origens_configuradas",
    "excluir_perfil",
    "ativar_perfil",
    "desativar_perfil",
    "origem_e_valida",
    "obter_id_origem",
    "obter_caminho_origem",
    "origem_esta_ativa",
    "obter_tipos_origem",
    "origem_possui_tipos",
    "adicionar_tipo_origem",
    "remover_tipo_origem_por_indice",
    "alterar_origem_ativa",
    "tipo_e_valido",
    "obter_id_tipo",
    "obter_nome_tipo",
    "tipo_esta_ativo",
    "obter_restricoes_tipo",
    "obter_destinos_tipo",
    "tipo_possui_destinos",
    "adicionar_destino_tipo_configurado",
    "remover_destino_tipo_por_indice",
    "alterar_nome_tipo",
    "alterar_restricoes_tipo",
    "alterar_tipo_ativo",
    "destino_e_valido",
    "obter_caminho_destino",
    "obter_operacao_destino",
    "alterar_operacao_destino",
    "restricoes_e_valida",
    "obter_extensoes_restricoes",
    "obter_regras_nome_restricoes",
    "obter_tamanho_min_restricoes",
    "obter_tamanho_max_restricoes",
    "obter_data_min_restricoes",
    "obter_data_max_restricoes",
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


def criar_restricoes(extensoes, regras_nome, tamanho_min, tamanho_max, data_min, data_max):
    """Cria restricoes completas para um tipo de arquivo.

    Centraliza a montagem do TAD de restricoes para que UI e engine nao
    precisem conhecer diretamente as chaves internas persistidas em JSON.
    """
    return {
        "extensoes_permitidas": extensoes if isinstance(extensoes, list) else [],
        "regras_nome": regras_nome if isinstance(regras_nome, list) else [],
        "tamanho_min": tamanho_min,
        "tamanho_max": tamanho_max,
        "data_modificacao_min": data_min,
        "data_modificacao_max": data_max,
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


def obter_id_perfil(perfil):
    """Retorna o identificador de um perfil.

    Funcao de acesso para modulos que precisam referenciar o perfil sem
    conhecer diretamente a chave interna usada no dicionario. Retorna `None`
    quando a entrada nao e um perfil valido.
    """
    if not isinstance(perfil, dict):
        return None
    return perfil.get("id")


def obter_nome_perfil(perfil):
    """Retorna o nome de exibicao do perfil.

    Esta funcao isola a chave interna usada para o nome do perfil e devolve
    string vazia quando a entrada nao representa um perfil valido.
    """
    if not isinstance(perfil, dict):
        return ""
    nome = perfil.get("nome", "")
    if not isinstance(nome, str):
        return ""
    return nome


def perfil_esta_ativo(perfil):
    """Indica se um perfil deve participar de execucoes.

    Trata perfis sem campo `ativo` como ativos para manter o valor padrao do
    TAD. Retorna `False` para entradas que nao sao dicionarios.
    """
    if not isinstance(perfil, dict):
        return False
    return perfil.get("ativo", True)


def obter_origens_configuradas(perfil):
    """Retorna as origens configuradas de um perfil.

    Funcao de acesso de leitura do TAD. Devolve a lista armazenada no perfil
    quando ela existe ou lista vazia para entradas invalidas/sem configuracao.
    Quem chama nao deve assumir outras chaves internas do perfil.
    """
    if not isinstance(perfil, dict):
        return []
    origens = perfil.get("origens_configuradas", [])
    if not isinstance(origens, list):
        return []
    return origens


def perfil_possui_origens_configuradas(perfil):
    """Indica se um perfil possui ao menos uma origem configurada."""
    return bool(obter_origens_configuradas(perfil))


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


def alterar_origens_configuradas(perfis, perfil_id, origens_configuradas):
    """Substitui as origens configuradas de um perfil.

    Recebe a lista completa no modelo atual `origem -> tipo -> destino`.
    Retorna `ERRO_DADOS_INVALIDOS` quando a entrada nao e lista e codigo de
    perfil inexistente quando `perfil_id` nao pertence a colecao recebida.
    """
    if not isinstance(origens_configuradas, list):
        return ERRO_DADOS_INVALIDOS

    codigo, perfil = consultar_perfil(perfis, perfil_id)
    if codigo != OK:
        return codigo

    perfil["origens_configuradas"] = origens_configuradas
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


def origem_e_valida(origem):
    """Indica se a entrada possui formato minimo de origem configurada."""
    return isinstance(origem, dict)


def obter_id_origem(origem):
    """Retorna o identificador interno da origem configurada."""
    if not origem_e_valida(origem):
        return None
    return origem.get("id")


def obter_caminho_origem(origem):
    """Retorna o caminho da pasta de origem."""
    if not origem_e_valida(origem):
        return ""
    caminho = origem.get("caminho", "")
    if not isinstance(caminho, str):
        return ""
    return caminho


def origem_esta_ativa(origem):
    """Indica se uma origem deve participar do backup."""
    if not origem_e_valida(origem):
        return False
    return origem.get("ativo", True)


def obter_tipos_origem(origem):
    """Retorna a lista de tipos de arquivo vinculados a uma origem."""
    if not origem_e_valida(origem):
        return []
    tipos = origem.get("tipos_arquivo", [])
    if not isinstance(tipos, list):
        return []
    return tipos


def origem_possui_tipos(origem):
    """Indica se a origem possui tipos cadastrados."""
    return bool(obter_tipos_origem(origem))


def alterar_origem_ativa(origem, ativo):
    """Altera o estado ativo/inativo de uma origem configurada."""
    if not origem_e_valida(origem) or not isinstance(ativo, bool):
        return ERRO_DADOS_INVALIDOS
    origem["ativo"] = ativo
    return OK


def adicionar_tipo_origem(origem, tipo):
    """Adiciona um tipo de arquivo a uma origem configurada."""
    if not origem_e_valida(origem) or not tipo_e_valido(tipo):
        return ERRO_DADOS_INVALIDOS
    origem.setdefault("tipos_arquivo", []).append(tipo)
    return OK


def remover_tipo_origem_por_indice(origem, indice):
    """Remove um tipo de arquivo da origem pelo indice."""
    tipos = obter_tipos_origem(origem)
    if not isinstance(indice, int) or indice < 0 or indice >= len(tipos):
        return ERRO_DADOS_INVALIDOS
    tipos.pop(indice)
    return OK


def tipo_e_valido(tipo):
    """Indica se a entrada possui formato minimo de tipo de arquivo."""
    return isinstance(tipo, dict)


def obter_id_tipo(tipo):
    """Retorna o identificador do tipo de arquivo."""
    if not tipo_e_valido(tipo):
        return None
    return tipo.get("id")


def obter_nome_tipo(tipo):
    """Retorna o nome exibido para o tipo de arquivo."""
    if not tipo_e_valido(tipo):
        return ""
    nome = tipo.get("nome", "")
    if not isinstance(nome, str):
        return ""
    return nome


def tipo_esta_ativo(tipo):
    """Indica se um tipo de arquivo deve participar do backup."""
    if not tipo_e_valido(tipo):
        return False
    return tipo.get("ativo", True)


def obter_restricoes_tipo(tipo):
    """Retorna as restricoes configuradas para um tipo."""
    if not tipo_e_valido(tipo):
        return criar_restricoes_padrao()
    restricoes = tipo.get("restricoes", {})
    if isinstance(restricoes, dict) and restricoes:
        return restricoes
    return criar_restricoes_padrao()


def obter_destinos_tipo(tipo):
    """Retorna a lista de destinos vinculados a um tipo."""
    if not tipo_e_valido(tipo):
        return []
    destinos = tipo.get("destinos", [])
    if not isinstance(destinos, list):
        return []
    return destinos


def tipo_possui_destinos(tipo):
    """Indica se um tipo possui ao menos um destino configurado."""
    return bool(obter_destinos_tipo(tipo))


def alterar_nome_tipo(tipo, nome):
    """Altera o nome de um tipo de arquivo."""
    if not tipo_e_valido(tipo) or not isinstance(nome, str):
        return ERRO_DADOS_INVALIDOS
    tipo["nome"] = nome
    return OK


def adicionar_destino_tipo_configurado(tipo, destino):
    """Adiciona um destino a um tipo de arquivo."""
    if not tipo_e_valido(tipo) or not destino_e_valido(destino):
        return ERRO_DADOS_INVALIDOS
    tipo.setdefault("destinos", []).append(destino)
    return OK


def remover_destino_tipo_por_indice(tipo, indice):
    """Remove um destino do tipo pelo indice."""
    destinos = obter_destinos_tipo(tipo)
    if not isinstance(indice, int) or indice < 0 or indice >= len(destinos):
        return ERRO_DADOS_INVALIDOS
    destinos.pop(indice)
    return OK


def alterar_restricoes_tipo(tipo, restricoes):
    """Substitui as restricoes de um tipo de arquivo."""
    if not tipo_e_valido(tipo) or not isinstance(restricoes, dict):
        return ERRO_DADOS_INVALIDOS
    tipo["restricoes"] = restricoes
    return OK


def alterar_tipo_ativo(tipo, ativo):
    """Altera o estado ativo/inativo de um tipo de arquivo."""
    if not tipo_e_valido(tipo) or not isinstance(ativo, bool):
        return ERRO_DADOS_INVALIDOS
    tipo["ativo"] = ativo
    return OK


def destino_e_valido(destino):
    """Indica se a entrada possui formato minimo de destino."""
    return isinstance(destino, dict)


def obter_caminho_destino(destino):
    """Retorna o caminho de pasta de um destino."""
    if not destino_e_valido(destino):
        return ""
    caminho = destino.get("caminho", "")
    if not isinstance(caminho, str):
        return ""
    return caminho


def obter_operacao_destino(destino):
    """Retorna a operacao configurada para um destino."""
    if not destino_e_valido(destino):
        return "copiar"
    operacao = destino.get("operacao", "copiar")
    if not isinstance(operacao, str):
        return "copiar"
    return operacao


def alterar_operacao_destino(destino, operacao):
    """Altera a operacao configurada em um destino."""
    if not destino_e_valido(destino) or not isinstance(operacao, str):
        return ERRO_DADOS_INVALIDOS
    destino["operacao"] = operacao
    return OK


def restricoes_e_valida(restricoes):
    """Indica se a entrada possui formato minimo de restricoes."""
    return isinstance(restricoes, dict)


def obter_extensoes_restricoes(restricoes):
    """Retorna as extensoes permitidas configuradas nas restricoes."""
    if not restricoes_e_valida(restricoes):
        return []
    extensoes = restricoes.get("extensoes_permitidas", [])
    if not isinstance(extensoes, list):
        return []
    return extensoes


def obter_regras_nome_restricoes(restricoes):
    """Retorna as regras de nome configuradas nas restricoes."""
    if not restricoes_e_valida(restricoes):
        return []
    regras = restricoes.get("regras_nome", [])
    if not isinstance(regras, list):
        return []
    return regras


def obter_tamanho_min_restricoes(restricoes):
    """Retorna o tamanho minimo configurado nas restricoes."""
    if not restricoes_e_valida(restricoes):
        return 0
    return restricoes.get("tamanho_min", 0) or 0


def obter_tamanho_max_restricoes(restricoes):
    """Retorna o tamanho maximo configurado nas restricoes."""
    if not restricoes_e_valida(restricoes):
        return None
    return restricoes.get("tamanho_max")


def obter_data_min_restricoes(restricoes):
    """Retorna a data minima configurada nas restricoes."""
    if not restricoes_e_valida(restricoes):
        return None
    return restricoes.get("data_modificacao_min")


def obter_data_max_restricoes(restricoes):
    """Retorna a data maxima configurada nas restricoes."""
    if not restricoes_e_valida(restricoes):
        return None
    return restricoes.get("data_modificacao_max")


