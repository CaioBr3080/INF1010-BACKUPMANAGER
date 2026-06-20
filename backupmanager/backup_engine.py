"""Execucao das rotinas de backup."""

import shutil
from pathlib import Path

from backupmanager import backup_result, backup_validation, file_utils
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
    perfil_id = perfil.get("id") if isinstance(perfil, dict) else None
    resultado = backup_result.montar_resultado_backup(perfil_id)

    codigo_validacao = backup_validation.validar_perfil_para_backup(perfil)
    if codigo_validacao != OK:
        resultado["status"] = "erro"
        resultado["erros"].append("Perfil invalido para backup.")
        return codigo_validacao, resultado

    return _executar_backup_configurado(perfil)


def _executar_backup_configurado(perfil):
    """Executa backup no modelo origem -> tipo -> destino."""
    resultado = backup_result.montar_resultado_backup(perfil.get("id"))
    primeiro_erro = OK

    for origem in perfil.get("origens_configuradas", []):
        if not origem.get("ativo", True):
            continue
        codigo = _executar_backup_da_origem_configurada(origem, resultado)
        if primeiro_erro == OK and codigo != OK:
            primeiro_erro = codigo

    if resultado["arquivos_processados"] == 0 and not resultado["erros"]:
        resultado["status"] = "sem_arquivos"
        return ERRO_BACKUP_SEM_ARQUIVOS, resultado
    if not resultado["erros"]:
        resultado["status"] = "sucesso"
        return OK, resultado
    if resultado["arquivos_processados"] > 0:
        resultado["status"] = "parcial"
        return primeiro_erro, resultado

    resultado["status"] = "erro"
    return primeiro_erro, resultado


def _executar_backup_da_origem_configurada(origem, resultado):
    """Executa todos os tipos de uma origem configurada."""
    caminhos = file_utils.listar_arquivos_em_origem(origem.get("caminho"))
    primeiro_erro = OK

    for tipo in origem.get("tipos_arquivo", []):
        if not tipo.get("ativo", True):
            continue
        arquivos_validos = _filtrar_arquivos_por_tipo(caminhos, tipo)
        for arquivo in arquivos_validos:
            resultado_arquivo = _processar_arquivo_para_destinos_configurados(arquivo, tipo.get("destinos", []), tipo)
            backup_result.aplicar_resultado_arquivo(resultado, resultado_arquivo)
            if primeiro_erro == OK and resultado_arquivo.get("codigo") != OK:
                primeiro_erro = resultado_arquivo.get("codigo")

    return primeiro_erro


def _filtrar_arquivos_por_tipo(caminhos, tipo):
    """Filtra arquivos de uma origem para um tipo."""
    arquivos = []
    restricoes = tipo.get("restricoes", {})
    for caminho in caminhos:
        arquivo = file_utils.obter_metadados_arquivo(caminho)
        if arquivo is None:
            continue
        if file_utils.arquivo_atende_restricoes(arquivo, restricoes):
            arquivo["tipo_id"] = tipo.get("id")
            arquivo["tipo_nome"] = tipo.get("nome", "")
            arquivos.append(arquivo)
    return arquivos


def _processar_arquivo_para_destinos(arquivo, destinos, operacao):
    """Processa um arquivo para uma lista de destinos."""
    resultado = {
        "codigo": OK,
        "processado": False,
        "arquivos_copiados": 0,
        "arquivos_movidos": 0,
        "arquivos_recortados": 0,
        "arquivos": [],
        "erros": [],
    }

    if not isinstance(arquivo, dict) or not isinstance(destinos, list):
        resultado["codigo"] = ERRO_DADOS_INVALIDOS
        resultado["erros"].append("Arquivo ou destinos invalidos.")
        return resultado

    caminho_origem = arquivo.get("caminho")
    if not caminho_origem:
        resultado["codigo"] = ERRO_ARQUIVO_NAO_ENCONTRADO
        resultado["erros"].append("Arquivo sem caminho de origem.")
        return resultado

    if operacao == "copiar":
        return _processar_copia_para_destinos(arquivo, destinos, resultado)
    if operacao == "mover":
        return _processar_movimento_para_destinos(arquivo, destinos, resultado)
    if operacao == "recortar":
        return _processar_recorte_para_destinos(arquivo, destinos, resultado)

    resultado["codigo"] = ERRO_OPERACAO_INVALIDA
    resultado["erros"].append("Operacao invalida.")
    return resultado


def _processar_arquivo_para_destinos_configurados(arquivo, destinos, tipo):
    """Processa arquivo usando destinos com operacao individual."""
    codigo = backup_validation.validar_destinos_do_tipo({"destinos": destinos})
    if codigo != OK:
        return {
            "codigo": codigo,
            "processado": False,
            "arquivos_copiados": 0,
            "arquivos_movidos": 0,
            "arquivos_recortados": 0,
            "arquivos": [],
            "erros": [backup_result.montar_erro_arquivo(arquivo, tipo.get("nome", ""), codigo)],
        }

    resultado = {
        "codigo": OK,
        "processado": False,
        "arquivos_copiados": 0,
        "arquivos_movidos": 0,
        "arquivos_recortados": 0,
        "arquivos": [],
        "erros": [],
    }

    for destino in destinos:
        operacao = destino.get("operacao", "copiar")
        caminho = destino.get("caminho")
        resultado_operacao = _processar_arquivo_para_destinos(arquivo, [caminho], operacao)
        if resultado_operacao.get("processado"):
            resultado["processado"] = True
        resultado["arquivos_copiados"] += resultado_operacao.get("arquivos_copiados", 0)
        resultado["arquivos_movidos"] += resultado_operacao.get("arquivos_movidos", 0)
        resultado["arquivos_recortados"] += resultado_operacao.get("arquivos_recortados", 0)
        resultado["arquivos"].extend(resultado_operacao.get("arquivos", []))
        resultado["erros"].extend(resultado_operacao.get("erros", []))
        if resultado["codigo"] == OK and resultado_operacao.get("codigo") != OK:
            resultado["codigo"] = resultado_operacao.get("codigo")

    return resultado


def _processar_copia_para_destinos(arquivo, destinos, resultado):
    """Copia um arquivo para todos os destinos."""
    for destino in destinos:
        caminho_destino = _gerar_caminho_destino(arquivo, destino)
        codigo = copiar_arquivo(arquivo.get("caminho"), caminho_destino)
        if codigo == OK:
            resultado["arquivos_copiados"] += 1
            resultado["processado"] = True
            resultado["arquivos"].append(backup_result.montar_registro_arquivo(arquivo, caminho_destino, "copiar", OK))
        else:
            resultado["codigo"] = codigo
            resultado["erros"].append(backup_result.montar_erro_arquivo(arquivo, destino, codigo))
            resultado["arquivos"].append(backup_result.montar_registro_arquivo(arquivo, caminho_destino, "copiar", codigo))
    return resultado


def _processar_movimento_para_destinos(arquivo, destinos, resultado):
    """Copia um arquivo para todos os destinos e remove a origem ao final."""
    copias_realizadas = 0
    for destino in destinos:
        caminho_destino = _gerar_caminho_destino(arquivo, destino)
        codigo = copiar_arquivo(arquivo.get("caminho"), caminho_destino)
        if codigo == OK:
            copias_realizadas += 1
            resultado["arquivos"].append(backup_result.montar_registro_arquivo(arquivo, caminho_destino, "mover", OK))
        else:
            resultado["codigo"] = codigo
            resultado["erros"].append(backup_result.montar_erro_arquivo(arquivo, destino, codigo))
            resultado["arquivos"].append(backup_result.montar_registro_arquivo(arquivo, caminho_destino, "mover", codigo))

    if resultado["erros"]:
        return resultado

    try:
        Path(arquivo.get("caminho")).unlink()
    except (OSError, TypeError, ValueError):
        resultado["codigo"] = ERRO_FALHA_AO_MOVER
        resultado["erros"].append(backup_result.montar_erro_arquivo(arquivo, "", ERRO_FALHA_AO_MOVER))
        resultado["arquivos"].append(backup_result.montar_registro_arquivo(arquivo, "", "mover", ERRO_FALHA_AO_MOVER))
        return resultado

    resultado["processado"] = True
    resultado["arquivos_movidos"] = 1
    resultado["arquivos_copiados"] = copias_realizadas
    return resultado


def _processar_recorte_para_destinos(arquivo, destinos, resultado):
    """Recorta um arquivo para um destino."""
    resultado = _processar_movimento_para_destinos(arquivo, destinos, resultado)
    for registro in resultado.get("arquivos", []):
        if registro.get("operacao") == "mover":
            registro["operacao"] = "recortar"
    if resultado.get("processado"):
        resultado["arquivos_recortados"] = resultado.get("arquivos_movidos", 0)
        resultado["arquivos_movidos"] = 0
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

    nome = arquivo.get("nome")
    caminho_origem = arquivo.get("caminho")

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
