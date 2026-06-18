"""Camada de controle entre interface e modulos internos."""

from backupmanager import backup_engine, backup_validation, file_utils, history_manager, perfil_manager, storage
from backupmanager.return_codes import (
    OK,
    ERRO_DADOS_INVALIDOS,
    ERRO_DESTINO_INVALIDO,
    ERRO_OPERACAO_INVALIDA,
    ERRO_ORIGEM_INVALIDA,
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
    "definir_operacao_do_perfil",
    "ativar_perfil_por_id",
    "desativar_perfil_por_id",
    "adicionar_origem_ao_perfil",
    "remover_origem_do_perfil",
    "adicionar_destino_ao_perfil",
    "remover_destino_do_perfil",
    "definir_restricoes_do_perfil",
    "definir_agendamento_do_perfil",
    "executar_backup_do_perfil",
    "obter_arquivos_do_perfil",
    "obter_arquivos_do_perfil_configurado",
    "consultar_historico_do_perfil",
    "limpar_historico_do_perfil",
    "limpar_todo_historico",
    "obter_configuracoes",
    "salvar_configuracoes",
    "normalizar_extensao",
    "obter_extensoes_disponiveis",
    "adicionar_extensao_disponivel",
]

_ESTADO = {
    "perfis": [],
    "historico": [],
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

    Garante a existencia dos arquivos JSON, carrega perfis, historico e
    configuracoes, executa a migracao de perfis legados para o modelo atual e
    atualiza `_ESTADO`. Retorna `OK` quando todo o estado esta pronto para a
    interface usar, ou o primeiro codigo de erro encontrado no carregamento.
    """
    codigo_padrao = storage.criar_arquivos_padrao()
    if codigo_padrao != OK:
        return codigo_padrao

    codigo_perfis, perfis = storage.carregar_perfis()
    codigo_historico, historico = storage.carregar_historico()
    codigo_config, config = storage.carregar_configuracoes()

    if codigo_perfis != OK:
        return codigo_perfis
    if codigo_historico != OK:
        return codigo_historico
    if codigo_config != OK:
        return codigo_config

    codigo_migracao, houve_migracao = perfil_manager.migrar_perfis_para_modelo_atual(perfis)
    if codigo_migracao != OK:
        return codigo_migracao

    _ESTADO["perfis"] = perfis
    _ESTADO["historico"] = historico
    _ESTADO["config"] = config
    _ESTADO["alterado"] = houve_migracao

    return OK


def finalizar_aplicacao():
    """Persiste em JSON as alteracoes acumuladas em memoria.

    Se `_ESTADO["alterado"]` estiver falso, nao grava nada. Quando ha
    alteracoes, salva perfis, historico e configuracoes nessa ordem; em caso
    de erro interrompe a sequencia e devolve o codigo correspondente. Ao
    salvar tudo com sucesso, limpa a marca de alteracao.
    """
    if not _ESTADO.get("alterado", False):
        return OK

    codigo = storage.salvar_perfis(_ESTADO["perfis"])
    if codigo != OK:
        return codigo

    codigo = storage.salvar_historico(_ESTADO["historico"])
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
    if not isinstance(perfil, dict) or not perfil.get("id"):
        return ERRO_DADOS_INVALIDOS

    perfil_id = perfil["id"]
    codigo, perfil_atual = perfil_manager.consultar_perfil(_ESTADO["perfis"], perfil_id)
    if codigo != OK:
        return codigo

    if "nome" in perfil:
        codigo = perfil_manager.validar_nome_perfil(perfil["nome"])
        if codigo != OK:
            return codigo

    if "origens" in perfil and not isinstance(perfil["origens"], list):
        return ERRO_DADOS_INVALIDOS

    if "destinos" in perfil and not isinstance(perfil["destinos"], list):
        return ERRO_DADOS_INVALIDOS

    if "operacao" in perfil and perfil["operacao"] not in ("copiar", "mover", "recortar"):
        return ERRO_OPERACAO_INVALIDA

    if "restricoes" in perfil and not isinstance(perfil["restricoes"], dict):
        return ERRO_DADOS_INVALIDOS

    if "origens_configuradas" in perfil and not isinstance(perfil["origens_configuradas"], list):
        return ERRO_DADOS_INVALIDOS

    if "agendamento" in perfil and not isinstance(perfil["agendamento"], dict):
        return ERRO_DADOS_INVALIDOS

    if "estado_arquivos" in perfil and not isinstance(perfil["estado_arquivos"], dict):
        return ERRO_DADOS_INVALIDOS

    if "ativo" in perfil and not isinstance(perfil["ativo"], bool):
        return ERRO_DADOS_INVALIDOS

    codigo = perfil_manager.alterar_nome_perfil(
        _ESTADO["perfis"],
        perfil_id,
        perfil.get("nome", perfil_atual.get("nome", "")),
    )
    if codigo != OK:
        return codigo

    if "origens" in perfil:
        perfil_atual["origens"] = perfil["origens"]

    if "destinos" in perfil:
        perfil_atual["destinos"] = perfil["destinos"]

    if "operacao" in perfil:
        codigo = perfil_manager.alterar_operacao(_ESTADO["perfis"], perfil_id, perfil["operacao"])
        if codigo != OK:
            return codigo

    if "restricoes" in perfil:
        perfil_atual["restricoes"] = perfil["restricoes"]

    if "origens_configuradas" in perfil:
        perfil_atual["origens_configuradas"] = perfil["origens_configuradas"]

    if "agendamento" in perfil:
        perfil_atual["agendamento"] = perfil["agendamento"]

    if "estado_arquivos" in perfil:
        perfil_atual["estado_arquivos"] = perfil["estado_arquivos"]

    if "ativo" in perfil:
        perfil_atual["ativo"] = perfil["ativo"]

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


def definir_operacao_do_perfil(perfil_id, operacao):
    """Define a operacao global legada de um perfil.

    Mantida para compatibilidade com comandos antigos. Para o modelo atual,
    operacoes devem ser configuradas por destino dentro de
    `origens_configuradas`.
    """
    codigo = perfil_manager.alterar_operacao(_ESTADO["perfis"], perfil_id, operacao)
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


def adicionar_origem_ao_perfil(perfil_id, caminho):
    """Adiciona uma origem legada a um perfil apos validar o caminho.

    Esta funcao e uma operacao de compatibilidade com o modelo antigo. Ela
    valida se `caminho` e diretorio e delega a mutacao ao `perfil_manager`.
    """
    if not caminho or not file_utils.caminho_e_diretorio(caminho):
        return ERRO_ORIGEM_INVALIDA

    codigo = perfil_manager.adicionar_origem(_ESTADO["perfis"], perfil_id, caminho)
    if codigo == OK:
        _marcar_estado_alterado()
    return codigo


def remover_origem_do_perfil(perfil_id, caminho):
    """Remove uma origem legada de um perfil em memoria.

    A funcao nao valida o disco, pois remover um caminho inexistente da lista
    ainda e uma operacao valida sobre a configuracao.
    """
    codigo = perfil_manager.remover_origem(_ESTADO["perfis"], perfil_id, caminho)
    if codigo == OK:
        _marcar_estado_alterado()
    return codigo


def adicionar_destino_ao_perfil(perfil_id, caminho):
    """Adiciona um destino legado a um perfil apos validar o caminho.

    Mantida para compatibilidade. No modelo atual, destinos ficam associados
    aos tipos de arquivo de cada origem.
    """
    if not caminho or not file_utils.caminho_e_diretorio(caminho):
        return ERRO_DESTINO_INVALIDO

    codigo = perfil_manager.adicionar_destino(_ESTADO["perfis"], perfil_id, caminho)
    if codigo == OK:
        _marcar_estado_alterado()
    return codigo


def remover_destino_do_perfil(perfil_id, caminho):
    """Remove um destino legado de um perfil em memoria.

    Encapsula a chamada ao TAD de perfis e marca alteracao apenas quando a
    operacao retorna `OK`.
    """
    codigo = perfil_manager.remover_destino(_ESTADO["perfis"], perfil_id, caminho)
    if codigo == OK:
        _marcar_estado_alterado()
    return codigo


def definir_restricoes_do_perfil(perfil_id, restricoes):
    """Define restricoes globais legadas de um perfil.

    Existe para compatibilidade com o formato antigo. No modelo atual, filtros
    sao salvos em cada tipo de arquivo dentro de `origens_configuradas`.
    """
    codigo = perfil_manager.alterar_restricoes(_ESTADO["perfis"], perfil_id, restricoes)
    if codigo == OK:
        _marcar_estado_alterado()
    return codigo


def definir_agendamento_do_perfil(perfil_id, agendamento):
    """Substitui o agendamento de um perfil em memoria.

    Recebe um dicionario de agendamento ja normalizado pela interface e delega
    a alteracao ao `perfil_manager`. Nao inicia monitoramento automaticamente.
    """
    codigo = perfil_manager.alterar_agendamento(_ESTADO["perfis"], perfil_id, agendamento)
    if codigo == OK:
        _marcar_estado_alterado()
    return codigo


def executar_backup_do_perfil(perfil_id):
    """Executa o backup do perfil informado e registra historico.

    Busca o perfil em memoria, rejeita perfis inativos, chama o motor de
    backup e registra o resultado no historico em memoria. A persistencia do
    historico ocorre somente no fechamento da aplicacao.
    """
    codigo, perfil = perfil_manager.consultar_perfil(_ESTADO["perfis"], perfil_id)
    if codigo != OK:
        return codigo, None

    if not perfil.get("ativo", True):
        return ERRO_PERFIL_INATIVO, None

    codigo_backup, resultado = backup_engine.executar_backup(perfil)
    history_manager.registrar_backup(_ESTADO["historico"], perfil_id, resultado)
    _marcar_estado_alterado()
    return codigo_backup, resultado


def obter_arquivos_do_perfil(perfil_id):
    """Lista arquivos do perfil e informa quais entram no backup.

    Funcao de acesso usada por telas de pre-visualizacao. Para perfis no
    modelo atual, delega ao fluxo configurado por origem/tipo; para perfis
    legados, aplica as restricoes globais antigas.
    """
    codigo, perfil = perfil_manager.consultar_perfil(_ESTADO["perfis"], perfil_id)
    if codigo != OK:
        return codigo, None

    if backup_validation.perfil_usa_fluxo_configurado(perfil):
        return obter_arquivos_do_perfil_configurado(perfil)

    caminhos = file_utils.listar_arquivos_de_origens(perfil.get("origens", []))
    restricoes = perfil.get("restricoes", {})
    arquivos = []

    for caminho in caminhos:
        arquivo = file_utils.obter_metadados_arquivo(caminho)
        if arquivo is None:
            continue
        arquivo["incluido"] = file_utils.arquivo_atende_restricoes(arquivo, restricoes)
        arquivos.append(arquivo)

    return OK, arquivos


def obter_arquivos_do_perfil_configurado(perfil):
    """Lista arquivos de um perfil ja carregado no modelo atual.

    Percorre origens ativas, coleta somente arquivos diretamente dentro da
    pasta de origem e calcula `tipos_incluidos` para cada arquivo conforme as
    restricoes dos tipos ativos.
    """
    arquivos = []

    for origem in perfil.get("origens_configuradas", []):
        if not origem.get("ativo", True):
            continue
        caminhos = file_utils.listar_arquivos_em_origem(origem.get("caminho"))
        for caminho in caminhos:
            arquivo = file_utils.obter_metadados_arquivo(caminho)
            if arquivo is None:
                continue
            arquivo["origem"] = origem.get("caminho")
            arquivo["tipos_incluidos"] = []
            for tipo in origem.get("tipos_arquivo", []):
                if not tipo.get("ativo", True):
                    continue
                if file_utils.arquivo_atende_restricoes(arquivo, tipo.get("restricoes", {})):
                    arquivo["tipos_incluidos"].append(tipo.get("nome", ""))
            arquivo["incluido"] = bool(arquivo["tipos_incluidos"])
            arquivos.append(arquivo)

    return OK, arquivos


def consultar_historico_do_perfil(perfil_id):
    """Retorna os registros de historico associados a um perfil.

    Funcao de acesso da interface de historico. Nao altera memoria nem
    persistencia.
    """
    return history_manager.consultar_historico_por_perfil(_ESTADO["historico"], perfil_id)


def limpar_historico_do_perfil(perfil_id):
    """Remove da memoria o historico de um perfil especifico.

    Marca o estado como alterado quando a limpeza e concluida com sucesso,
    permitindo persistir a remocao no fechamento da aplicacao.
    """
    codigo = history_manager.limpar_historico_perfil(_ESTADO["historico"], perfil_id)
    if codigo == OK:
        _marcar_estado_alterado()
    return codigo


def limpar_todo_historico():
    """Remove todos os registros de historico da memoria.

    Operacao global usada pela interface quando o usuario deseja apagar o
    historico completo. Persistencia ocorre posteriormente.
    """
    codigo = history_manager.limpar_todo_historico(_ESTADO["historico"])
    if codigo == OK:
        _marcar_estado_alterado()
    return codigo


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

