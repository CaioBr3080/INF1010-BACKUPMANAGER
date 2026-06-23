"""Funcoes de acesso para o estado visual de origens configuradas.

Este modulo concentra as operacoes sobre `estado_interface["origens_configuradas"]`
e `estado_interface["origem_selecionada_indice"]` que antes eram feitas
diretamente em `backup_flow.py` e `actions.py` via indexacao de dicionario e
manipulacao de lista (`append`, `pop`, iteracao, indexacao por posicao).

O objetivo e que o restante da interface deixe de saber que as origens
configuradas ficam guardadas numa lista dentro de `estado_interface`: todo
acesso ou alteracao passa a ser feito atraves das funcoes abaixo.

Este modulo nao decide regras de negocio do TAD Perfil/Origem; isso continua
em `backupmanager.domain.perfil_manager`. Aqui apenas se encapsula a forma
como a interface guarda e acessa a lista de origens em memoria durante a
edicao de um perfil.
"""

from backupmanager.return_codes import OK, ERRO_DADOS_INVALIDOS

__all__ = [
    "obter_origens_configuradas",
    "definir_origens_configuradas",
    "adicionar_origem_configurada",
    "remover_origem_configurada_por_indice",
    "obter_origem_configurada_por_indice",
    "definir_origem_selecionada_indice",
    "obter_origem_selecionada_indice",
    "obter_origem_selecionada",
    "total_origens_configuradas",
]


def obter_origens_configuradas(estado_interface):
    """Retorna a lista de origens configuradas em memoria na interface.

    Funcao de acesso somente leitura: nao protege contra mutacao se o
    chamador alterar o conteudo retornado, mas centraliza o ponto de leitura
    para que `backup_flow.py`/`actions.py` deixem de indexar o dicionario
    diretamente.
    """
    origens = estado_interface.get("origens_configuradas", [])
    if not isinstance(origens, list):
        return []
    return origens


def definir_origens_configuradas(estado_interface, origens_configuradas):
    """Substitui a lista completa de origens configuradas na interface.

    Usada ao carregar um perfil selecionado ou ao limpar o formulario.
    """
    if not isinstance(origens_configuradas, list):
        return ERRO_DADOS_INVALIDOS
    estado_interface["origens_configuradas"] = origens_configuradas
    return OK


def adicionar_origem_configurada(estado_interface, origem):
    """Adiciona uma origem configurada ja construida ao estado da interface.

    Substitui o antigo `estado_interface["origens_configuradas"].append(origem)`
    feito diretamente em `backup_flow.py`.
    """
    origens = obter_origens_configuradas(estado_interface)
    origens.append(origem)
    estado_interface["origens_configuradas"] = origens
    return OK, len(origens) - 1


def remover_origem_configurada_por_indice(estado_interface, indice):
    """Remove a origem configurada na posicao informada, se existir.

    Substitui o antigo acesso direto com `origens.pop(indice)` em
    `backup_flow.py`. Retorna `ERRO_DADOS_INVALIDOS` quando o indice nao e
    valido, sem lancar excecao.
    """
    origens = obter_origens_configuradas(estado_interface)
    if not isinstance(indice, int) or indice < 0 or indice >= len(origens):
        return ERRO_DADOS_INVALIDOS
    origens.pop(indice)
    return OK


def obter_origem_configurada_por_indice(estado_interface, indice):
    """Retorna a origem configurada na posicao informada, ou `None`.

    Centraliza o acesso por indice antes feito diretamente em
    `_obter_origem_selecionada` (`backup_flow.py`).
    """
    origens = obter_origens_configuradas(estado_interface)
    if not isinstance(indice, int) or indice < 0 or indice >= len(origens):
        return None
    return origens[indice]


def definir_origem_selecionada_indice(estado_interface, indice):
    """Define qual origem esta selecionada na interface, por indice."""
    estado_interface["origem_selecionada_indice"] = indice
    return OK


def obter_origem_selecionada_indice(estado_interface):
    """Retorna o indice da origem selecionada na interface, ou `None`."""
    return estado_interface.get("origem_selecionada_indice")


def obter_origem_selecionada(estado_interface):
    """Retorna a origem configurada atualmente selecionada, ou `None`.

    Combina `obter_origem_selecionada_indice` e
    `obter_origem_configurada_por_indice` num unico ponto de acesso, evitando
    que quem chama precise conhecer os dois nomes de chave do dicionario de
    estado.
    """
    indice = obter_origem_selecionada_indice(estado_interface)
    if indice is None:
        return None
    return obter_origem_configurada_por_indice(estado_interface, indice)


def total_origens_configuradas(estado_interface):
    """Retorna a quantidade de origens configuradas em memoria."""
    return len(obter_origens_configuradas(estado_interface))
