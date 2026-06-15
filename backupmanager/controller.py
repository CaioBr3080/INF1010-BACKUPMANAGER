"""Camada de controle entre interface e modulos internos."""

from backupmanager import backup_engine, file_utils, history_manager, perfil_manager, storage
from backupmanager.return_codes import (
    OK,
    ERRO_DADOS_INVALIDOS,
    ERRO_DESTINO_INVALIDO,
    ERRO_OPERACAO_INVALIDA,
    ERRO_ORIGEM_INVALIDA,
    ERRO_PERFIL_INATIVO,
)

ESTADO = {
    "perfis": [],
    "historico": [],
    "config": {},
    "alterado": False,
}

EXTENSOES_PADRAO = [
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


def marcar_estado_alterado():
    """Marca que o estado em memoria possui alteracoes nao persistidas."""
    ESTADO["alterado"] = True
    return OK


def inicializar_aplicacao():
    """Carrega dados iniciais dos arquivos JSON para a memoria."""
    codigo_padrao = storage.criar_arquivos_padrao()
    if codigo_padrao != OK:
        return codigo_padrao

    codigo_perfis, perfis = storage.carregar_perfis()
    codigo_historico, historico = storage.carregar_historico()
    codigo_config, config = storage.carregar_configuracoes()

    ESTADO["perfis"] = perfis
    ESTADO["historico"] = historico
    ESTADO["config"] = config
    ESTADO["alterado"] = False

    if codigo_perfis != OK:
        return codigo_perfis
    if codigo_historico != OK:
        return codigo_historico
    if codigo_config != OK:
        return codigo_config

    return OK


def finalizar_aplicacao():
    """Reescreve os arquivos JSON somente ao encerrar a aplicacao."""
    if not ESTADO.get("alterado", False):
        return OK

    codigo = storage.salvar_perfis(ESTADO["perfis"])
    if codigo != OK:
        return codigo

    codigo = storage.salvar_historico(ESTADO["historico"])
    if codigo != OK:
        return codigo

    codigo = storage.salvar_configuracoes(ESTADO["config"])
    if codigo != OK:
        return codigo

    ESTADO["alterado"] = False
    return OK


def criar_novo_perfil(nome):
    """Cria um perfil e guarda a alteracao em memoria."""
    codigo, perfil = perfil_manager.criar_perfil(nome)
    if codigo != OK:
        return codigo, None

    ESTADO["perfis"].append(perfil)
    marcar_estado_alterado()
    return OK, perfil


def obter_perfis():
    """Retorna todos os perfis."""
    return perfil_manager.listar_perfis(ESTADO["perfis"])


def obter_perfil_por_id(perfil_id):
    """Retorna um perfil pelo id."""
    return perfil_manager.consultar_perfil(ESTADO["perfis"], perfil_id)


def salvar_perfil_editado(perfil):
    """Aplica dados editados de um perfil ao estado em memoria."""
    if not isinstance(perfil, dict) or not perfil.get("id"):
        return ERRO_DADOS_INVALIDOS

    perfil_id = perfil["id"]
    codigo, perfil_atual = perfil_manager.consultar_perfil(ESTADO["perfis"], perfil_id)
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

    if "operacao" in perfil and perfil["operacao"] not in ("copiar", "mover"):
        return ERRO_OPERACAO_INVALIDA

    if "restricoes" in perfil and not isinstance(perfil["restricoes"], dict):
        return ERRO_DADOS_INVALIDOS

    if "agendamento" in perfil and not isinstance(perfil["agendamento"], dict):
        return ERRO_DADOS_INVALIDOS

    if "estado_arquivos" in perfil and not isinstance(perfil["estado_arquivos"], dict):
        return ERRO_DADOS_INVALIDOS

    if "ativo" in perfil and not isinstance(perfil["ativo"], bool):
        return ERRO_DADOS_INVALIDOS

    codigo = perfil_manager.alterar_nome_perfil(
        ESTADO["perfis"],
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
        codigo = perfil_manager.alterar_operacao(ESTADO["perfis"], perfil_id, perfil["operacao"])
        if codigo != OK:
            return codigo

    if "restricoes" in perfil:
        perfil_atual["restricoes"] = perfil["restricoes"]

    if "agendamento" in perfil:
        perfil_atual["agendamento"] = perfil["agendamento"]

    if "estado_arquivos" in perfil:
        perfil_atual["estado_arquivos"] = perfil["estado_arquivos"]

    if "ativo" in perfil:
        perfil_atual["ativo"] = perfil["ativo"]

    marcar_estado_alterado()
    return OK


def excluir_perfil_por_id(perfil_id):
    """Exclui um perfil em memoria."""
    codigo = perfil_manager.excluir_perfil(ESTADO["perfis"], perfil_id)
    if codigo == OK:
        marcar_estado_alterado()
    return codigo


def definir_operacao_do_perfil(perfil_id, operacao):
    """Define a operacao de backup de um perfil em memoria."""
    codigo = perfil_manager.alterar_operacao(ESTADO["perfis"], perfil_id, operacao)
    if codigo == OK:
        marcar_estado_alterado()
    return codigo


def ativar_perfil_por_id(perfil_id):
    """Ativa um perfil em memoria."""
    codigo = perfil_manager.ativar_perfil(ESTADO["perfis"], perfil_id)
    if codigo == OK:
        marcar_estado_alterado()
    return codigo


def desativar_perfil_por_id(perfil_id):
    """Desativa um perfil em memoria."""
    codigo = perfil_manager.desativar_perfil(ESTADO["perfis"], perfil_id)
    if codigo == OK:
        marcar_estado_alterado()
    return codigo


def adicionar_origem_ao_perfil(perfil_id, caminho):
    """Adiciona origem a um perfil."""
    if not caminho or not file_utils.caminho_e_diretorio(caminho):
        return ERRO_ORIGEM_INVALIDA

    codigo = perfil_manager.adicionar_origem(ESTADO["perfis"], perfil_id, caminho)
    if codigo == OK:
        marcar_estado_alterado()
    return codigo


def remover_origem_do_perfil(perfil_id, caminho):
    """Remove origem de um perfil."""
    codigo = perfil_manager.remover_origem(ESTADO["perfis"], perfil_id, caminho)
    if codigo == OK:
        marcar_estado_alterado()
    return codigo


def adicionar_destino_ao_perfil(perfil_id, caminho):
    """Adiciona destino a um perfil."""
    if not caminho or not file_utils.caminho_e_diretorio(caminho):
        return ERRO_DESTINO_INVALIDO

    codigo = perfil_manager.adicionar_destino(ESTADO["perfis"], perfil_id, caminho)
    if codigo == OK:
        marcar_estado_alterado()
    return codigo


def remover_destino_do_perfil(perfil_id, caminho):
    """Remove destino de um perfil."""
    codigo = perfil_manager.remover_destino(ESTADO["perfis"], perfil_id, caminho)
    if codigo == OK:
        marcar_estado_alterado()
    return codigo


def definir_restricoes_do_perfil(perfil_id, restricoes):
    """Define restricoes de um perfil."""
    codigo = perfil_manager.alterar_restricoes(ESTADO["perfis"], perfil_id, restricoes)
    if codigo == OK:
        marcar_estado_alterado()
    return codigo


def definir_agendamento_do_perfil(perfil_id, agendamento):
    """Define agendamento de um perfil."""
    codigo = perfil_manager.alterar_agendamento(ESTADO["perfis"], perfil_id, agendamento)
    if codigo == OK:
        marcar_estado_alterado()
    return codigo


def executar_backup_do_perfil(perfil_id):
    """Executa backup de um perfil e registra historico em memoria."""
    codigo, perfil = perfil_manager.consultar_perfil(ESTADO["perfis"], perfil_id)
    if codigo != OK:
        return codigo, None

    if not perfil.get("ativo", True):
        return ERRO_PERFIL_INATIVO, None

    codigo_backup, resultado = backup_engine.executar_backup(perfil)
    history_manager.registrar_backup(ESTADO["historico"], perfil_id, resultado)
    marcar_estado_alterado()
    return codigo_backup, resultado


def obter_arquivos_do_perfil(perfil_id):
    """Lista arquivos das origens do perfil e indica se passam nas restricoes."""
    codigo, perfil = perfil_manager.consultar_perfil(ESTADO["perfis"], perfil_id)
    if codigo != OK:
        return codigo, None

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


def consultar_historico_do_perfil(perfil_id):
    """Consulta historico de um perfil."""
    return history_manager.consultar_historico_por_perfil(ESTADO["historico"], perfil_id)


def limpar_historico_do_perfil(perfil_id):
    """Limpa historico de um perfil em memoria."""
    codigo = history_manager.limpar_historico_perfil(ESTADO["historico"], perfil_id)
    if codigo == OK:
        marcar_estado_alterado()
    return codigo


def limpar_todo_historico():
    """Limpa todo o historico em memoria."""
    codigo = history_manager.limpar_todo_historico(ESTADO["historico"])
    if codigo == OK:
        marcar_estado_alterado()
    return codigo


def obter_configuracoes():
    """Retorna configuracoes gerais em memoria."""
    return OK, ESTADO["config"]


def salvar_configuracoes(config):
    """Substitui configuracoes gerais em memoria."""
    if not isinstance(config, dict):
        return ERRO_DADOS_INVALIDOS

    ESTADO["config"] = config
    marcar_estado_alterado()
    return OK


def normalizar_extensao(extensao):
    """Normaliza extensao para o formato .ext."""
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
    """Retorna extensoes padrao e customizadas."""
    customizadas = ESTADO["config"].get("extensoes_disponiveis", [])
    extensoes = []

    for extensao in EXTENSOES_PADRAO + customizadas:
        extensao_normalizada = normalizar_extensao(extensao)
        if extensao_normalizada and extensao_normalizada not in extensoes:
            extensoes.append(extensao_normalizada)

    return OK, sorted(extensoes)


def adicionar_extensao_disponivel(extensao):
    """Adiciona extensao customizada a configuracao em memoria."""
    extensao_normalizada = normalizar_extensao(extensao)
    if extensao_normalizada is None:
        return ERRO_DADOS_INVALIDOS

    codigo, extensoes = obter_extensoes_disponiveis()
    if codigo != OK:
        return codigo
    if extensao_normalizada in extensoes:
        return OK

    customizadas = ESTADO["config"].setdefault("extensoes_disponiveis", [])
    customizadas.append(extensao_normalizada)
    marcar_estado_alterado()
    return OK
