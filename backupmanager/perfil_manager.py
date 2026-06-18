"""Funcoes para criar, consultar e alterar perfis de backup."""

import uuid

from backupmanager.return_codes import (
    OK,
    ERRO_DADOS_INVALIDOS,
    ERRO_NOME_INVALIDO,
    ERRO_OPERACAO_INVALIDA,
    ERRO_PERFIL_NAO_ENCONTRADO,
)

__all__ = [
    "criar_restricoes_padrao",
    "criar_agendamento_padrao",
    "criar_destino_tipo",
    "criar_tipo_arquivo",
    "criar_origem_configurada",
    "migrar_perfil_para_modelo_atual",
    "migrar_perfis_para_modelo_atual",
    "validar_nome_perfil",
    "criar_perfil",
    "consultar_perfil",
    "listar_perfis",
    "alterar_nome_perfil",
    "excluir_perfil",
    "ativar_perfil",
    "desativar_perfil",
    "adicionar_origem",
    "remover_origem",
    "adicionar_destino",
    "remover_destino",
    "alterar_operacao",
    "alterar_restricoes",
    "alterar_agendamento",
]

_OPERACOES_VALIDAS = ("copiar", "mover", "recortar")


def criar_restricoes_padrao():
    """Cria restricoes vazias no formato aceito pelo motor de backup.

    Retorna um dicionario novo com todas as chaves usadas para filtrar
    arquivos por extensao, nome, tamanho e data de modificacao. A funcao
    nao altera estado global e deve ser usada sempre que uma origem/tipo
    precisar nascer sem filtros ativos.
    """
    return {
        "extensoes_permitidas": [],
        "nome_contem": "",
        "regras_nome": [],
        "tamanho_min": 0,
        "tamanho_max": None,
        "data_modificacao_min": None,
        "data_modificacao_max": None,
    }


def criar_agendamento_padrao():
    """Cria agendamento manual no formato persistido no perfil.

    O retorno representa um backup sem execucao automatica, com campos
    preparados para intervalo em segundos/minutos/horas e monitoramento por
    alteracao. A funcao nao agenda nada por si so; apenas fornece a estrutura
    padrao usada por perfis novos e por migracoes.
    """
    return {
        "tipo": "manual",
        "intervalo_minutos": None,
        "intervalo_valor": None,
        "intervalo_unidade": "minutos",
        "executar_ao_detectar_mudanca": False,
        "ultima_execucao": None,
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


def migrar_perfil_para_modelo_atual(perfil):
    """Migra um perfil legado para origem -> tipo -> destino.

    A migracao preserva `id`, `nome`, `ativo`, `agendamento` e `estado_arquivos`,
    converte `origens`/`destinos`/`operacao`/`restricoes` para
    `origens_configuradas` e remove as chaves legadas do perfil.
    Retorna `(codigo, migrado)`.
    """
    if not isinstance(perfil, dict):
        return ERRO_DADOS_INVALIDOS, False

    migrado = False

    if "agendamento" not in perfil or not isinstance(perfil.get("agendamento"), dict):
        perfil["agendamento"] = criar_agendamento_padrao()
        migrado = True
    if "estado_arquivos" not in perfil or not isinstance(perfil.get("estado_arquivos"), dict):
        perfil["estado_arquivos"] = {}
        migrado = True
    if "ativo" not in perfil or not isinstance(perfil.get("ativo"), bool):
        perfil["ativo"] = True
        migrado = True

    origens_configuradas = perfil.get("origens_configuradas")
    if not isinstance(origens_configuradas, list):
        perfil["origens_configuradas"] = []
        origens_configuradas = perfil["origens_configuradas"]
        migrado = True

    if not origens_configuradas:
        origens = perfil.get("origens", [])
        if isinstance(origens, list) and origens:
            perfil["origens_configuradas"] = _montar_origens_configuradas_legadas(perfil, origens)
            migrado = True

    for chave in ("origens", "destinos", "operacao", "restricoes"):
        if chave in perfil:
            perfil.pop(chave, None)
            migrado = True

    return OK, migrado


def migrar_perfis_para_modelo_atual(perfis):
    """Migra em lote uma lista de perfis para o modelo atual.

    Recebe uma lista mutavel de perfis carregados do JSON e aplica
    `migrar_perfil_para_modelo_atual` em cada item. Retorna `(OK, True)` se
    pelo menos um perfil foi alterado, `(OK, False)` se todos ja estavam no
    modelo atual, ou erro quando a entrada nao e uma lista valida.
    """
    if not isinstance(perfis, list):
        return ERRO_DADOS_INVALIDOS, False

    houve_migracao = False
    for perfil in perfis:
        codigo, migrado = migrar_perfil_para_modelo_atual(perfil)
        if codigo != OK:
            return codigo, houve_migracao
        houve_migracao = houve_migracao or migrado
    return OK, houve_migracao


def _montar_origens_configuradas_legadas(perfil, origens):
    destinos = _montar_destinos_legados(perfil)
    restricoes = perfil.get("restricoes")
    if not isinstance(restricoes, dict):
        restricoes = criar_restricoes_padrao()

    configuradas = []
    for indice, caminho in enumerate(origens):
        if not caminho:
            continue
        configuradas.append({
            "id": "origem_" + str(indice + 1),
            "caminho": caminho,
            "ativo": True,
            "tipos_arquivo": [
                {
                    "id": "tipo_1",
                    "nome": "Todos os arquivos",
                    "ativo": True,
                    "restricoes": restricoes.copy(),
                    "destinos": _copiar_lista_dicionarios(destinos),
                }
            ],
        })
    return configuradas


def _montar_destinos_legados(perfil):
    destinos = perfil.get("destinos", [])
    if not isinstance(destinos, list):
        return []

    operacao = perfil.get("operacao", "copiar")
    if operacao not in _OPERACOES_VALIDAS:
        operacao = "copiar"
    return [criar_destino_tipo(caminho, operacao) for caminho in destinos if caminho]


def _copiar_lista_dicionarios(lista):
    copia = []
    for item in lista:
        if isinstance(item, dict):
            copia.append(item.copy())
    return copia


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
    `origens_configuradas`, `agendamento`, `estado_arquivos` e `ativo`.
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
        "agendamento": criar_agendamento_padrao(),
        "estado_arquivos": {},
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


def adicionar_origem(perfis, perfil_id, caminho):
    """Adiciona uma origem legada ao perfil.

    Esta funcao existe para compatibilidade com o modelo antigo baseado em
    listas globais `origens`/`destinos`. Codigo novo deve preferir
    `origens_configuradas`, mas o controller ainda pode chamar esta operacao
    enquanto houver compatibilidade com dados antigos.
    """
    codigo, perfil = consultar_perfil(perfis, perfil_id)
    if codigo != OK:
        return codigo
    origens = perfil.setdefault("origens", [])
    if caminho not in origens:
        origens.append(caminho)
    return OK


def remover_origem(perfis, perfil_id, caminho):
    """Remove uma origem legada do perfil, se ela existir.

    Mantida por compatibilidade com o modelo antigo. A operacao e idempotente:
    se o caminho nao estiver na lista, o perfil permanece inalterado e o
    retorno continua `OK` quando o perfil existe.
    """
    codigo, perfil = consultar_perfil(perfis, perfil_id)
    if codigo != OK:
        return codigo
    origens = perfil.setdefault("origens", [])
    if caminho in origens:
        origens.remove(caminho)
    return OK


def adicionar_destino(perfis, perfil_id, caminho):
    """Adiciona um destino legado ao perfil.

    Opera sobre a lista global `destinos` do modelo antigo e evita duplicatas.
    Nao valida o disco; validacao de caminho pertence ao controller.
    """
    codigo, perfil = consultar_perfil(perfis, perfil_id)
    if codigo != OK:
        return codigo
    destinos = perfil.setdefault("destinos", [])
    if caminho not in destinos:
        destinos.append(caminho)
    return OK


def remover_destino(perfis, perfil_id, caminho):
    """Remove um destino legado do perfil, se ele estiver cadastrado.

    Mantida para compatibilidade ate a remocao completa do modelo antigo. Nao
    altera `origens_configuradas`.
    """
    codigo, perfil = consultar_perfil(perfis, perfil_id)
    if codigo != OK:
        return codigo
    destinos = perfil.setdefault("destinos", [])
    if caminho in destinos:
        destinos.remove(caminho)
    return OK


def alterar_operacao(perfis, perfil_id, operacao):
    """Altera a operacao global legada de um perfil.

    Aceita apenas `copiar`, `mover` ou `recortar`. No modelo atual, a operacao
    fica em cada destino de tipo; esta funcao existe para compatibilidade com
    perfis e comandos antigos.
    """
    if operacao not in _OPERACOES_VALIDAS:
        return ERRO_OPERACAO_INVALIDA

    codigo, perfil = consultar_perfil(perfis, perfil_id)
    if codigo != OK:
        return codigo

    perfil["operacao"] = operacao
    return OK


def alterar_restricoes(perfis, perfil_id, restricoes):
    """Substitui as restricoes globais legadas de um perfil.

    A funcao nao interpreta nem valida os filtros recebidos; apenas grava o
    dicionario no perfil encontrado. No modelo atual, restricoes vivem dentro
    de cada tipo de arquivo.
    """
    codigo, perfil = consultar_perfil(perfis, perfil_id)
    if codigo != OK:
        return codigo
    perfil["restricoes"] = restricoes
    return OK


def alterar_agendamento(perfis, perfil_id, agendamento):
    """Substitui a configuracao de agendamento de um perfil.

    Recebe um dicionario ja montado pela camada de interface/controller e o
    associa ao perfil encontrado. A funcao nao inicia monitoramento; apenas
    atualiza o dado usado posteriormente pelo scheduler.
    """
    codigo, perfil = consultar_perfil(perfis, perfil_id)
    if codigo != OK:
        return codigo
    perfil["agendamento"] = agendamento
    return OK

