"""Execucao das rotinas de backup."""

import shutil
from pathlib import Path

from backupmanager.domain import backup_result, backup_validation, perfil_manager
from backupmanager.engine import file_utils
from backupmanager.return_codes import (
    OK,
    ERRO_BACKUP_SEM_ARQUIVOS,
    ERRO_ARQUIVO_NAO_ENCONTRADO,
    ERRO_DADOS_INVALIDOS,
    ERRO_DESTINO_INVALIDO,
    ERRO_FALHA_AO_COPIAR,
    ERRO_FALHA_AO_MOVER,
    ERRO_OPERACAO_INVALIDA,
)

__all__ = [
    "executar_backup",
    "copiar_arquivo",
    "mover_arquivo",
]


def executar_backup(perfil):
    """Executa a rotina de backup de um perfil.

    Valida o perfil no modelo atual `origem -> tipo -> destino`, filtra
    arquivos e consolida o resultado da execucao. Retorna `(codigo,
    resultado)`, onde `resultado` contem status, contadores, arquivos
    processados e erros.
    """
    perfil_id = perfil_manager.obter_id_perfil(perfil)
    resultado = backup_result.montar_resultado_backup(perfil_id)

    codigo_validacao = backup_validation.validar_perfil_para_backup(perfil)
    if codigo_validacao != OK:
        backup_result.definir_status_resultado(resultado, "erro")
        backup_result.obter_erros_resultado(resultado).append("Perfil invalido para backup.")
        return codigo_validacao, resultado

    return _executar_backup_configurado(perfil)


def _executar_backup_configurado(perfil):
    """Executa backup no modelo origem -> tipo -> destino."""
    resultado = backup_result.montar_resultado_backup(perfil_manager.obter_id_perfil(perfil))
    primeiro_erro = OK

    for origem in perfil_manager.obter_origens_configuradas(perfil):
        if not perfil_manager.origem_esta_ativa(origem):
            continue
        codigo = _executar_backup_da_origem_configurada(origem, resultado)
        if primeiro_erro == OK and codigo != OK:
            primeiro_erro = codigo

    if backup_result.obter_arquivos_processados(resultado) == 0 and not backup_result.resultado_possui_erros(resultado):
        backup_result.definir_status_resultado(resultado, "sem_arquivos")
        return ERRO_BACKUP_SEM_ARQUIVOS, resultado
    if not backup_result.resultado_possui_erros(resultado):
        backup_result.definir_status_resultado(resultado, "sucesso")
        return OK, resultado
    if backup_result.obter_arquivos_processados(resultado) > 0:
        backup_result.definir_status_resultado(resultado, "parcial")
        return primeiro_erro, resultado

    backup_result.definir_status_resultado(resultado, "erro")
    return primeiro_erro, resultado


def _executar_backup_da_origem_configurada(origem, resultado):
    """Executa todos os tipos de uma origem configurada."""
    caminhos = file_utils.listar_arquivos_em_origem(perfil_manager.obter_caminho_origem(origem))
    primeiro_erro = OK

    for tipo in perfil_manager.obter_tipos_origem(origem):
        if not perfil_manager.tipo_esta_ativo(tipo):
            continue
        arquivos_validos = _filtrar_arquivos_por_tipo(caminhos, tipo)
        for arquivo in arquivos_validos:
            resultado_arquivo = _processar_arquivo_para_destinos_configurados(
                arquivo,
                perfil_manager.obter_destinos_tipo(tipo),
                tipo,
            )
            backup_result.aplicar_resultado_arquivo(resultado, resultado_arquivo)
            codigo_resultado_arquivo = backup_result.obter_codigo_resultado_arquivo(resultado_arquivo)
            if primeiro_erro == OK and codigo_resultado_arquivo != OK:
                primeiro_erro = codigo_resultado_arquivo

    return primeiro_erro


def _filtrar_arquivos_por_tipo(caminhos, tipo):
    """Filtra arquivos de uma origem para um tipo."""
    arquivos = []
    restricoes = perfil_manager.obter_restricoes_tipo(tipo)
    for caminho in caminhos:
        arquivo = file_utils.obter_metadados_arquivo(caminho)
        if arquivo is None:
            continue
        if file_utils.arquivo_atende_restricoes(arquivo, restricoes):
            file_utils.associar_tipo_ao_arquivo(
                arquivo,
                perfil_manager.obter_id_tipo(tipo),
                perfil_manager.obter_nome_tipo(tipo),
            )
            arquivos.append(arquivo)
    return arquivos


def _processar_arquivo_para_destinos(arquivo, destinos, operacao):
    """Processa um arquivo para uma lista de destinos."""
    resultado = backup_result.montar_resultado_arquivo()

    if not isinstance(arquivo, dict) or not isinstance(destinos, list):
        backup_result.definir_codigo_resultado_arquivo(resultado, ERRO_DADOS_INVALIDOS)
        backup_result.adicionar_erro_resultado_arquivo(resultado, "Arquivo ou destinos invalidos.")
        return resultado

    caminho_origem = file_utils.obter_caminho_arquivo(arquivo)
    if not caminho_origem:
        backup_result.definir_codigo_resultado_arquivo(resultado, ERRO_ARQUIVO_NAO_ENCONTRADO)
        backup_result.adicionar_erro_resultado_arquivo(resultado, "Arquivo sem caminho de origem.")
        return resultado

    if operacao == "copiar":
        return _processar_copia_para_destinos(arquivo, destinos, resultado)
    if operacao == "mover":
        return _processar_movimento_para_destinos(arquivo, destinos, resultado)
    if operacao == "recortar":
        return _processar_recorte_para_destinos(arquivo, destinos, resultado)

    backup_result.definir_codigo_resultado_arquivo(resultado, ERRO_OPERACAO_INVALIDA)
    backup_result.adicionar_erro_resultado_arquivo(resultado, "Operacao invalida.")
    return resultado


def _processar_arquivo_para_destinos_configurados(arquivo, destinos, tipo):
    """Processa arquivo usando destinos com operacao individual."""
    codigo = backup_validation.validar_destinos_do_tipo({"destinos": destinos})
    if codigo != OK:
        resultado_erro = backup_result.montar_resultado_arquivo()
        backup_result.definir_codigo_resultado_arquivo(resultado_erro, codigo)
        backup_result.adicionar_erro_resultado_arquivo(
            resultado_erro,
            backup_result.montar_erro_arquivo(arquivo, perfil_manager.obter_nome_tipo(tipo), codigo),
        )
        return resultado_erro

    resultado = backup_result.montar_resultado_arquivo()

    for destino in destinos:
        operacao = perfil_manager.obter_operacao_destino(destino)
        caminho = perfil_manager.obter_caminho_destino(destino)
        resultado_operacao = _processar_arquivo_para_destinos(arquivo, [caminho], operacao)
        if backup_result.resultado_arquivo_foi_processado(resultado_operacao):
            backup_result.definir_processado_resultado_arquivo(resultado, True)
        backup_result.somar_copiados_resultado_arquivo(
            resultado,
            backup_result.obter_copiados_resultado_arquivo(resultado_operacao),
        )
        backup_result.somar_movidos_resultado_arquivo(
            resultado,
            backup_result.obter_movidos_resultado_arquivo(resultado_operacao),
        )
        backup_result.somar_recortados_resultado_arquivo(
            resultado,
            backup_result.obter_recortados_resultado_arquivo(resultado_operacao),
        )
        for registro in backup_result.obter_registros_resultado_arquivo(resultado_operacao):
            backup_result.adicionar_registro_resultado_arquivo(resultado, registro)
        for erro in backup_result.obter_erros_resultado_arquivo(resultado_operacao):
            backup_result.adicionar_erro_resultado_arquivo(resultado, erro)
        codigo_operacao = backup_result.obter_codigo_resultado_arquivo(resultado_operacao)
        if backup_result.obter_codigo_resultado_arquivo(resultado) == OK and codigo_operacao != OK:
            backup_result.definir_codigo_resultado_arquivo(resultado, codigo_operacao)

    return resultado


def _processar_copia_para_destinos(arquivo, destinos, resultado):
    """Copia um arquivo para todos os destinos."""
    for destino in destinos:
        caminho_destino = _gerar_caminho_destino(arquivo, destino)
        codigo = copiar_arquivo(file_utils.obter_caminho_arquivo(arquivo), caminho_destino)
        if codigo == OK:
            backup_result.somar_copiados_resultado_arquivo(resultado)
            backup_result.definir_processado_resultado_arquivo(resultado, True)
            backup_result.adicionar_registro_resultado_arquivo(
                resultado,
                backup_result.montar_registro_arquivo(arquivo, caminho_destino, "copiar", OK),
            )
        else:
            backup_result.definir_codigo_resultado_arquivo(resultado, codigo)
            backup_result.adicionar_erro_resultado_arquivo(
                resultado,
                backup_result.montar_erro_arquivo(arquivo, destino, codigo),
            )
            backup_result.adicionar_registro_resultado_arquivo(
                resultado,
                backup_result.montar_registro_arquivo(arquivo, caminho_destino, "copiar", codigo),
            )
    return resultado


def _processar_movimento_para_destinos(arquivo, destinos, resultado):
    """Copia um arquivo para todos os destinos e remove a origem ao final."""
    copias_realizadas = 0
    for destino in destinos:
        caminho_destino = _gerar_caminho_destino(arquivo, destino)
        codigo = copiar_arquivo(file_utils.obter_caminho_arquivo(arquivo), caminho_destino)
        if codigo == OK:
            copias_realizadas += 1
            backup_result.adicionar_registro_resultado_arquivo(
                resultado,
                backup_result.montar_registro_arquivo(arquivo, caminho_destino, "mover", OK),
            )
        else:
            backup_result.definir_codigo_resultado_arquivo(resultado, codigo)
            backup_result.adicionar_erro_resultado_arquivo(
                resultado,
                backup_result.montar_erro_arquivo(arquivo, destino, codigo),
            )
            backup_result.adicionar_registro_resultado_arquivo(
                resultado,
                backup_result.montar_registro_arquivo(arquivo, caminho_destino, "mover", codigo),
            )

    if backup_result.resultado_arquivo_possui_erros(resultado):
        return resultado

    try:
        Path(file_utils.obter_caminho_arquivo(arquivo)).unlink()
    except (OSError, TypeError, ValueError):
        backup_result.definir_codigo_resultado_arquivo(resultado, ERRO_FALHA_AO_MOVER)
        backup_result.adicionar_erro_resultado_arquivo(
            resultado,
            backup_result.montar_erro_arquivo(arquivo, "", ERRO_FALHA_AO_MOVER),
        )
        backup_result.adicionar_registro_resultado_arquivo(
            resultado,
            backup_result.montar_registro_arquivo(arquivo, "", "mover", ERRO_FALHA_AO_MOVER),
        )
        return resultado

    backup_result.definir_processado_resultado_arquivo(resultado, True)
    backup_result.somar_movidos_resultado_arquivo(resultado)
    backup_result.somar_copiados_resultado_arquivo(resultado, copias_realizadas)
    return resultado


def _processar_recorte_para_destinos(arquivo, destinos, resultado):
    """Recorta um arquivo para um destino."""
    resultado = _processar_movimento_para_destinos(arquivo, destinos, resultado)
    backup_result.marcar_registros_como_recorte(resultado)
    if backup_result.resultado_arquivo_foi_processado(resultado):
        movidos = backup_result.obter_movidos_resultado_arquivo(resultado)
        backup_result.somar_recortados_resultado_arquivo(resultado, movidos)
        backup_result.zerar_movidos_resultado_arquivo(resultado)
    return resultado


def copiar_arquivo(origem, destino):
    """Copia um arquivo individual para o caminho de destino.

    Verifica entradas obrigatorias, confirma que a origem e arquivo, cria a
    pasta de destino quando necessario e usa `shutil.copy2` para preservar
    metadados. Retorna apenas codigo de resultado.
    """
    if not origem or not destino:
        return ERRO_DADOS_INVALIDOS

    try:
        caminho_origem = Path(origem)
        caminho_destino = Path(destino)
        if not caminho_origem.is_file():
            return ERRO_ARQUIVO_NAO_ENCONTRADO

        codigo = _criar_pasta_destino_se_necessario(caminho_destino)
        if codigo != OK:
            return codigo

        shutil.copy2(caminho_origem, caminho_destino)
    except (OSError, shutil.Error, TypeError, ValueError):
        return ERRO_FALHA_AO_COPIAR

    return OK


def mover_arquivo(origem, destino):
    """Move um arquivo individual para o caminho de destino.

    Verifica entradas obrigatorias, confirma que a origem e arquivo, cria a
    pasta de destino quando necessario e usa `shutil.move`. Retorna codigo de
    sucesso ou falha sem levantar excecoes para a camada de interface.
    """
    if not origem or not destino:
        return ERRO_DADOS_INVALIDOS

    try:
        caminho_origem = Path(origem)
        caminho_destino = Path(destino)
        if not caminho_origem.is_file():
            return ERRO_ARQUIVO_NAO_ENCONTRADO

        codigo = _criar_pasta_destino_se_necessario(caminho_destino)
        if codigo != OK:
            return codigo

        shutil.move(str(caminho_origem), str(caminho_destino))
    except (OSError, shutil.Error, TypeError, ValueError):
        return ERRO_FALHA_AO_MOVER

    return OK


def _gerar_caminho_destino(arquivo, pasta_destino):
    """Gera caminho de destino para um arquivo."""
    if not isinstance(arquivo, dict) or not pasta_destino:
        return None

    nome = file_utils.obter_nome_arquivo(arquivo)
    caminho_origem = file_utils.obter_caminho_arquivo(arquivo)

    if not nome and caminho_origem:
        nome = Path(caminho_origem).name
    if not nome:
        return None

    return str(Path(pasta_destino) / nome)


def _criar_pasta_destino_se_necessario(caminho_destino):
    """Cria a pasta de destino quando necessario."""
    if not caminho_destino:
        return ERRO_DESTINO_INVALIDO

    try:
        pasta_destino = Path(caminho_destino).parent
        pasta_destino.mkdir(parents=True, exist_ok=True)
    except (OSError, TypeError, ValueError):
        return ERRO_DESTINO_INVALIDO

    return OK
