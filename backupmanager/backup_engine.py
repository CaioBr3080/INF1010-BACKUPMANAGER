"""Execucao das rotinas de backup."""

import shutil
from pathlib import Path

from backupmanager import file_utils
from backupmanager.return_codes import (
    OK,
    ERRO_BACKUP_SEM_ARQUIVOS,
    ERRO_PERFIL_INATIVO,
    ERRO_ARQUIVO_NAO_ENCONTRADO,
    ERRO_DADOS_INVALIDOS,
    ERRO_DESTINO_INVALIDO,
    ERRO_FALHA_AO_COPIAR,
    ERRO_FALHA_AO_MOVER,
    ERRO_OPERACAO_INVALIDA,
    ERRO_ORIGEM_INVALIDA,
    ERRO_SEM_PERMISSAO,
)


def montar_resultado_backup(perfil_id):
    """Cria o dicionario base de resultado de backup."""
    return {
        "perfil_id": perfil_id,
        "status": "nao_executado",
        "arquivos_processados": 0,
        "arquivos_copiados": 0,
        "arquivos_movidos": 0,
        "erros": [],
    }


def validar_perfil_para_backup(perfil):
    """Valida os dados minimos necessarios para executar backup."""
    if not isinstance(perfil, dict):
        return ERRO_DADOS_INVALIDOS

    origens = perfil.get("origens", [])
    destinos = perfil.get("destinos", [])
    operacao = perfil.get("operacao", "copiar")

    if not isinstance(origens, list) or len(origens) == 0:
        return ERRO_ORIGEM_INVALIDA
    if not isinstance(destinos, list) or len(destinos) == 0:
        return ERRO_DESTINO_INVALIDO
    if operacao not in ("copiar", "mover"):
        return ERRO_OPERACAO_INVALIDA

    return OK


def executar_backup(perfil):
    """Executa backup de um perfil."""
    perfil_id = perfil.get("id") if isinstance(perfil, dict) else None
    resultado = montar_resultado_backup(perfil_id)

    if isinstance(perfil, dict) and not perfil.get("ativo", True):
        resultado["status"] = "falha"
        resultado["erros"].append("O perfil esta inativo.")
        return ERRO_PERFIL_INATIVO, resultado

    codigo_validacao = validar_perfil_para_backup(perfil)
    if codigo_validacao != OK:
        resultado["status"] = "erro"
        resultado["erros"].append("Perfil invalido para backup.")
        return codigo_validacao, resultado

    caminhos = file_utils.listar_arquivos_de_origens(perfil.get("origens", []))
    restricoes = perfil.get("restricoes", {})
    arquivos_validos = []

    for caminho in caminhos:
        arquivo = file_utils.obter_metadados_arquivo(caminho)
        if arquivo is None:
            continue
        if file_utils.arquivo_atende_restricoes(arquivo, restricoes):
            arquivos_validos.append(arquivo)

    if not arquivos_validos:
        resultado["status"] = "sem_arquivos"
        return ERRO_BACKUP_SEM_ARQUIVOS, resultado

    return executar_backup_multiplos_destinos(perfil, arquivos_validos)


def executar_backup_multiplos_destinos(perfil, arquivos_validos):
    """Processa arquivos validos para todos os destinos do perfil."""
    resultado = montar_resultado_backup(perfil.get("id") if isinstance(perfil, dict) else None)
    if not isinstance(perfil, dict) or not isinstance(arquivos_validos, list):
        resultado["status"] = "erro"
        resultado["erros"].append("Dados invalidos para backup.")
        return ERRO_DADOS_INVALIDOS, resultado

    destinos = perfil.get("destinos", [])
    operacao = perfil.get("operacao", "copiar")
    primeiro_erro = OK

    for arquivo in arquivos_validos:
        resultado_arquivo = processar_arquivo_para_destinos(arquivo, destinos, operacao)
        if resultado_arquivo.get("processado"):
            resultado["arquivos_processados"] += 1
        resultado["arquivos_copiados"] += resultado_arquivo.get("arquivos_copiados", 0)
        resultado["arquivos_movidos"] += resultado_arquivo.get("arquivos_movidos", 0)
        resultado["erros"].extend(resultado_arquivo.get("erros", []))
        if primeiro_erro == OK and resultado_arquivo.get("codigo") != OK:
            primeiro_erro = resultado_arquivo.get("codigo")

    if not resultado["erros"]:
        resultado["status"] = "sucesso"
        return OK, resultado
    if resultado["arquivos_processados"] > 0:
        resultado["status"] = "parcial"
        return primeiro_erro, resultado

    resultado["status"] = "erro"
    return primeiro_erro, resultado


def processar_arquivo_para_destinos(arquivo, destinos, operacao):
    """Processa um arquivo para uma lista de destinos."""
    resultado = {
        "codigo": OK,
        "processado": False,
        "arquivos_copiados": 0,
        "arquivos_movidos": 0,
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
        return processar_copia_para_destinos(arquivo, destinos, resultado)
    if operacao == "mover":
        return processar_movimento_para_destinos(arquivo, destinos, resultado)

    resultado["codigo"] = ERRO_OPERACAO_INVALIDA
    resultado["erros"].append("Operacao invalida.")
    return resultado


def processar_copia_para_destinos(arquivo, destinos, resultado):
    """Copia um arquivo para todos os destinos."""
    for destino in destinos:
        caminho_destino = gerar_caminho_destino(arquivo, destino)
        codigo = copiar_arquivo(arquivo.get("caminho"), caminho_destino)
        if codigo == OK:
            resultado["arquivos_copiados"] += 1
            resultado["processado"] = True
        else:
            resultado["codigo"] = codigo
            resultado["erros"].append(montar_erro_arquivo(arquivo, destino, codigo))
    return resultado


def processar_movimento_para_destinos(arquivo, destinos, resultado):
    """Copia um arquivo para todos os destinos e remove a origem ao final."""
    copias_realizadas = 0
    for destino in destinos:
        caminho_destino = gerar_caminho_destino(arquivo, destino)
        codigo = copiar_arquivo(arquivo.get("caminho"), caminho_destino)
        if codigo == OK:
            copias_realizadas += 1
        else:
            resultado["codigo"] = codigo
            resultado["erros"].append(montar_erro_arquivo(arquivo, destino, codigo))

    if resultado["erros"]:
        return resultado

    try:
        Path(arquivo.get("caminho")).unlink()
    except PermissionError:
        resultado["codigo"] = ERRO_SEM_PERMISSAO
        resultado["erros"].append(montar_erro_arquivo(arquivo, "", ERRO_SEM_PERMISSAO))
        return resultado
    except (OSError, TypeError, ValueError):
        resultado["codigo"] = ERRO_FALHA_AO_MOVER
        resultado["erros"].append(montar_erro_arquivo(arquivo, "", ERRO_FALHA_AO_MOVER))
        return resultado

    resultado["processado"] = True
    resultado["arquivos_movidos"] = 1
    resultado["arquivos_copiados"] = copias_realizadas
    return resultado


def montar_erro_arquivo(arquivo, destino, codigo):
    """Monta mensagem simples de erro por arquivo."""
    nome = arquivo.get("nome", arquivo.get("caminho", "")) if isinstance(arquivo, dict) else ""
    return {
        "arquivo": nome,
        "destino": str(destino),
        "codigo": codigo,
    }


def copiar_arquivo(origem, destino):
    """Copia um arquivo para o destino informado."""
    if not origem or not destino:
        return ERRO_DADOS_INVALIDOS

    try:
        caminho_origem = Path(origem)
        caminho_destino = Path(destino)
        if not caminho_origem.is_file():
            return ERRO_ARQUIVO_NAO_ENCONTRADO

        codigo = criar_pasta_destino_se_necessario(caminho_destino)
        if codigo != OK:
            return codigo

        shutil.copy2(caminho_origem, caminho_destino)
    except PermissionError:
        return ERRO_SEM_PERMISSAO
    except (OSError, shutil.Error, TypeError, ValueError):
        return ERRO_FALHA_AO_COPIAR

    return OK


def mover_arquivo(origem, destino):
    """Move um arquivo para o destino informado."""
    if not origem or not destino:
        return ERRO_DADOS_INVALIDOS

    try:
        caminho_origem = Path(origem)
        caminho_destino = Path(destino)
        if not caminho_origem.is_file():
            return ERRO_ARQUIVO_NAO_ENCONTRADO

        codigo = criar_pasta_destino_se_necessario(caminho_destino)
        if codigo != OK:
            return codigo

        shutil.move(str(caminho_origem), str(caminho_destino))
    except PermissionError:
        return ERRO_SEM_PERMISSAO
    except (OSError, shutil.Error, TypeError, ValueError):
        return ERRO_FALHA_AO_MOVER

    return OK


def gerar_caminho_destino(arquivo, pasta_destino):
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


def criar_pasta_destino_se_necessario(caminho_destino):
    """Cria a pasta de destino quando necessario."""
    if not caminho_destino:
        return ERRO_DESTINO_INVALIDO

    try:
        pasta_destino = Path(caminho_destino).parent
        pasta_destino.mkdir(parents=True, exist_ok=True)
    except PermissionError:
        return ERRO_SEM_PERMISSAO
    except (OSError, TypeError, ValueError):
        return ERRO_DESTINO_INVALIDO

    return OK