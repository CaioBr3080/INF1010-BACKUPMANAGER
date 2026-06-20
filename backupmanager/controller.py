"""Camada de controle entre interface e modulos internos."""

from backupmanager.domain import perfil_manager
from backupmanager.engine import backup_engine, file_utils
from backupmanager.infra import storage
from backupmanager.return_codes import (
    OK,
    ERRO_DADOS_INVALIDOS,
    ERRO_PERFIL_INATIVO,
)

__all__ = [
    "inicializar_aplicacao",
    "finalizar_aplicacao",
    "criar_novo_perfil",
    "obter_perfis",
    "obter_perfil_por_id",
    "salvar_perfil_editado",
    "excluir_perfil_por_id",
    "ativar_perfil_por_id",
    "desativar_perfil_por_id",
    "executar_backup_do_perfil",
    "obter_arquivos_do_perfil",
    "obter_arquivos_do_perfil_configurado",
    "obter_configuracoes",
    "salvar_configuracoes",
    "normalizar_extensao",
    "obter_extensoes_disponiveis",
    "adicionar_extensao_disponivel",
]

_ESTADO = {
    "perfis": [],
    "config": {},
    "alterado": False,
}

_EXTENSOES_PADRAO = [
    ".7z",
    ".bak",
    ".csv",
    ".db",
    ".doc",
    ".docx",
    ".gif",
    ".jpeg",
    ".jpg",
    ".json",
    ".md",
    ".mp3",
    ".mp4",
    ".pdf",
    ".png",
    ".ppt",
    ".pptx",
    ".py",
    ".rar",
    ".sql",
    ".txt",
    ".xlsx",
    ".xml",
    ".zip",
]


def _marcar_estado_alterado():
    """Marca que o estado em memoria possui alteracoes nao persistidas."""
    _ESTADO["alterado"] = True
    return OK


def inicializar_aplicacao():
    """Inicializa o estado em memoria da aplicacao.

    Garante a existencia dos arquivos JSON, carrega perfis e configuracoes e
    atualiza `_ESTADO`. Retorna `OK` quando todo o estado esta pronto para a
    interface usar, ou o primeiro codigo de erro encontrado no carregamento.
    """
    codigo_padrao = storage.criar_arquivos_padrao()
    if codigo_padrao != OK:
        return codigo_padrao

    codigo_perfis, perfis = storage.carregar_perfis()
    codigo_config, config = storage.carregar_configuracoes()

    if codigo_perfis != OK:
        return codigo_perfis
    if codigo_config != OK:
        return codigo_config

    _ESTADO["perfis"] = perfis
    _ESTADO["config"] = config
    _ESTADO["alterado"] = False

    return OK


def finalizar_aplicacao():
    """Persiste em JSON as alteracoes acumuladas em memoria.

    Se `_ESTADO["alterado"]` estiver falso, nao grava nada. Quando ha
    alteracoes, salva perfis e configuracoes nessa ordem; em caso de erro
    interrompe a sequencia e devolve o codigo correspondente. Ao salvar tudo
    com sucesso, limpa a marca de alteracao.
    """
    if not _ESTADO.get("alterado", False):
        return OK

    codigo = storage.salvar_perfis(_ESTADO["perfis"])
    if codigo != OK:
        return codigo

    codigo = storage.salvar_configuracoes(_ESTADO["config"])
    if codigo != OK:
        return codigo

    _ESTADO["alterado"] = False
    return OK


def criar_novo_perfil(nome):
    """Cria um perfil novo e o registra no estado em memoria.

    Usa `perfil_manager.criar_perfil` para construir o dicionario no modelo
    atual, adiciona o perfil a `_ESTADO["perfis"]` e marca o estado como
    alterado. A funcao nao grava JSON imediatamente.
    """
    codigo, perfil = perfil_manager.criar_perfil(nome)
    if codigo != OK:
        return codigo, None

    _ESTADO["perfis"].append(perfil)
    _marcar_estado_alterado()
    return OK, perfil


def obter_perfis():
    """Retorna todos os perfis mantidos em memoria.

    Funcao de acesso usada pela interface para listar perfis. Devolve o par
    `(codigo, perfis)` conforme o contrato do `perfil_manager`.
    """
    return perfil_manager.listar_perfis(_ESTADO["perfis"])


def obter_perfil_por_id(perfil_id):
    """Consulta um perfil em memoria pelo identificador.

    Esta e a funcao de acesso pontual para a interface obter o perfil
    selecionado. Retorna `(OK, perfil)` ou erro quando o id nao existe.
    """
    return perfil_manager.consultar_perfil(_ESTADO["perfis"], perfil_id)


def salvar_perfil_editado(perfil):
    """Aplica ao estado em memoria os dados editados de um perfil.

    Recebe um dicionario parcial ou completo contendo obrigatoriamente `id`.
    Valida tipos basicos de cada campo conhecido, atualiza o perfil existente
    e marca o estado como alterado. Nao persiste JSON; a gravacao fica para
    `finalizar_aplicacao`.
    """
    perfil_id = perfil_manager.obter_id_perfil(perfil)
    if not perfil_id:
        return ERRO_DADOS_INVALIDOS

    codigo, perfil_atual = perfil_manager.consultar_perfil(_ESTADO["perfis"], perfil_id)
    if codigo != OK:
        return codigo

    if "nome" in perfil:
        codigo = perfil_manager.validar_nome_perfil(perfil["nome"])
        if codigo != OK:
            return codigo

    if "origens_configuradas" in perfil and not isinstance(perfil["origens_configuradas"], list):
        return ERRO_DADOS_INVALIDOS

    if "ativo" in perfil and not isinstance(perfil["ativo"], bool):
        return ERRO_DADOS_INVALIDOS

    codigo = perfil_manager.alterar_nome_perfil(
        _ESTADO["perfis"],
        perfil_id,
        perfil_manager.obter_nome_perfil(perfil) or perfil_manager.obter_nome_perfil(perfil_atual),
    )
    if codigo != OK:
        return codigo

    if "origens_configuradas" in perfil:
        codigo = perfil_manager.alterar_origens_configuradas(
            _ESTADO["perfis"],
            perfil_id,
            perfil["origens_configuradas"],
        )
        if codigo != OK:
            return codigo

    if "ativo" in perfil:
        if perfil["ativo"]:
            codigo = perfil_manager.ativar_perfil(_ESTADO["perfis"], perfil_id)
        else:
            codigo = perfil_manager.desativar_perfil(_ESTADO["perfis"], perfil_id)
        if codigo != OK:
            return codigo

    _marcar_estado_alterado()
    return OK


def excluir_perfil_por_id(perfil_id):
    """Remove um perfil do estado em memoria.

    Encapsula a operacao de exclusao do TAD de perfis e marca o estado como
    alterado somente quando a remocao e bem-sucedida.
    """
    codigo = perfil_manager.excluir_perfil(_ESTADO["perfis"], perfil_id)
    if codigo == OK:
        _marcar_estado_alterado()
    return codigo


def ativar_perfil_por_id(perfil_id):
    """Ativa um perfil para permitir execucoes de backup.

    Altera somente o estado em memoria e marca alteracao quando o perfil
    existe. Persistencia ocorre no fechamento da aplicacao.
    """
    codigo = perfil_manager.ativar_perfil(_ESTADO["perfis"], perfil_id)
    if codigo == OK:
        _marcar_estado_alterado()
    return codigo


def desativar_perfil_por_id(perfil_id):
    """Desativa um perfil para impedir execucoes de backup.

    O perfil permanece cadastrado e pode ser reativado depois. A funcao altera
    apenas memoria.
    """
    codigo = perfil_manager.desativar_perfil(_ESTADO["perfis"], perfil_id)
    if codigo == OK:
        _marcar_estado_alterado()
    return codigo


def executar_backup_do_perfil(perfil_id):
    """Executa o backup do perfil informado.

    Busca o perfil em memoria, rejeita perfis inativos, chama o motor de
    backup e retorna o resultado para a interface.
    """
    codigo, perfil = perfil_manager.consultar_perfil(_ESTADO["perfis"], perfil_id)
    if codigo != OK:
        return codigo, None

    if not perfil_manager.perfil_esta_ativo(perfil):
        return ERRO_PERFIL_INATIVO, None

    codigo_backup, resultado = backup_engine.executar_backup(perfil)
    return codigo_backup, resultado


def obter_arquivos_do_perfil(perfil_id):
    """Lista arquivos do perfil e informa quais entram no backup.

    Funcao de acesso usada por telas de pre-visualizacao. O perfil e tratado
    sempre no modelo atual `origens_configuradas`.
    """
    codigo, perfil = perfil_manager.consultar_perfil(_ESTADO["perfis"], perfil_id)
    if codigo != OK:
        return codigo, None

    return obter_arquivos_do_perfil_configurado(perfil)


def obter_arquivos_do_perfil_configurado(perfil):
    """Lista arquivos de um perfil ja carregado no modelo atual.

    Percorre origens ativas, coleta somente arquivos diretamente dentro da
    pasta de origem e calcula `tipos_incluidos` para cada arquivo conforme as
    restricoes dos tipos ativos.
    """
    arquivos = []

    for origem in perfil_manager.obter_origens_configuradas(perfil):
        if not perfil_manager.origem_esta_ativa(origem):
            continue
        caminho_origem = perfil_manager.obter_caminho_origem(origem)
        caminhos = file_utils.listar_arquivos_em_origem(caminho_origem)
        for caminho in caminhos:
            arquivo = file_utils.obter_metadados_arquivo(caminho)
            if arquivo is None:
                continue
            file_utils.associar_origem_ao_arquivo(arquivo, caminho_origem)
            file_utils.iniciar_tipos_incluidos_arquivo(arquivo)
            for tipo in perfil_manager.obter_tipos_origem(origem):
                if not perfil_manager.tipo_esta_ativo(tipo):
                    continue
                if file_utils.arquivo_atende_restricoes(arquivo, perfil_manager.obter_restricoes_tipo(tipo)):
                    file_utils.adicionar_tipo_incluido_arquivo(arquivo, perfil_manager.obter_nome_tipo(tipo))
            arquivo["incluido"] = file_utils.arquivo_possui_tipo_incluido(arquivo)
            arquivos.append(arquivo)

    return OK, arquivos


def obter_configuracoes():
    """Retorna o dicionario de configuracoes gerais em memoria.

    Funcao de acesso para opcoes globais da aplicacao, como extensoes
    customizadas. Nao copia o dicionario porque o controller centraliza o
    estado.
    """
    return OK, _ESTADO["config"]


def salvar_configuracoes(config):
    """Substitui as configuracoes gerais mantidas em memoria.

    Aceita apenas dicionarios. Quando a entrada e valida, troca
    `_ESTADO["config"]`, marca alteracao e deixa a gravacao para
    `finalizar_aplicacao`.
    """
    if not isinstance(config, dict):
        return ERRO_DADOS_INVALIDOS

    _ESTADO["config"] = config
    _marcar_estado_alterado()
    return OK


def normalizar_extensao(extensao):
    """Normaliza texto de extensao para o formato `.ext`.

    Remove espacos, converte para minusculas, adiciona ponto inicial quando
    necessario e rejeita valores vazios ou compostos apenas por ponto.
    """
    if not isinstance(extensao, str):
        return None

    extensao = extensao.strip().lower()
    if not extensao:
        return None
    if not extensao.startswith("."):
        extensao = "." + extensao
    if extensao == ".":
        return None
    return extensao


def obter_extensoes_disponiveis():
    """Retorna a lista ordenada de extensoes disponiveis na interface.

    Combina extensoes padrao com extensoes customizadas salvas em configuracao,
    normaliza todos os valores e remove duplicatas antes de devolver.
    """
    customizadas = _ESTADO["config"].get("extensoes_disponiveis", [])
    extensoes = []

    for extensao in _EXTENSOES_PADRAO + customizadas:
        extensao_normalizada = normalizar_extensao(extensao)
        if extensao_normalizada and extensao_normalizada not in extensoes:
            extensoes.append(extensao_normalizada)

    return OK, sorted(extensoes)


def adicionar_extensao_disponivel(extensao):
    """Adiciona uma extensao customizada a configuracao em memoria.

    Normaliza a extensao, ignora duplicatas ja disponiveis e marca o estado
    como alterado quando uma nova extensao e realmente adicionada.
    """
    extensao_normalizada = normalizar_extensao(extensao)
    if extensao_normalizada is None:
        return ERRO_DADOS_INVALIDOS

    codigo, extensoes = obter_extensoes_disponiveis()
    if codigo != OK:
        return codigo
    if extensao_normalizada in extensoes:
        return OK

    customizadas = _ESTADO["config"].setdefault("extensoes_disponiveis", [])
    customizadas.append(extensao_normalizada)
    _marcar_estado_alterado()
    return OK

