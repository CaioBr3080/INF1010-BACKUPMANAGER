"""Execucao das rotinas de backup."""

import shutil
from pathlib import Path

from backupmanager import file_utils
from backupmanager.return_codes import (
    OK,
    ERRO_BACKUP_SEM_ARQUIVOS,
    ERRO_ARQUIVO_NAO_ENCONTRADO,
    ERRO_DADOS_INVALIDOS,
    ERRO_DESTINO_INVALIDO,
    ERRO_FALHA_AO_COPIAR,
    ERRO_FALHA_AO_MOVER,
    ERRO_OPERACAO_INVALIDA,
    ERRO_ORIGEM_INVALIDA,
)

OPERACOES_VALIDAS = ("copiar", "mover", "recortar")


def montar_resultado_backup(perfil_id):
    """Cria o dicionario base de resultado de backup."""
    return {
        "perfil_id": perfil_id,
        "status": "nao_executado",
        "arquivos_processados": 0,
        "arquivos_copiados": 0,
        "arquivos_movidos": 0,
        "arquivos_recortados": 0,
        "arquivos": [],
        "erros": [],
    }


def validar_perfil_para_backup(perfil):
    """Valida os dados minimos necessarios para executar backup."""
    if not isinstance(perfil, dict):
        return ERRO_DADOS_INVALIDOS

    if perfil_usa_fluxo_configurado(perfil):
        return validar_perfil_configurado_para_backup(perfil)

    origens = perfil.get("origens", [])
    destinos = perfil.get("destinos", [])
    operacao = perfil.get("operacao", "copiar")

    if not isinstance(origens, list) or len(origens) == 0:
        return ERRO_ORIGEM_INVALIDA
    if not isinstance(destinos, list) or len(destinos) == 0:
        return ERRO_DESTINO_INVALIDO
    if operacao not in OPERACOES_VALIDAS:
        return ERRO_OPERACAO_INVALIDA

    return OK


def perfil_usa_fluxo_configurado(perfil):
    """Indica se o perfil usa origem -> tipo -> destino."""
    return isinstance(perfil, dict) and isinstance(perfil.get("origens_configuradas"), list) and len(perfil.get("origens_configuradas")) > 0


def validar_perfil_configurado_para_backup(perfil):
    """Valida o modelo origem -> tipo -> destino."""
    origens = perfil.get("origens_configuradas", [])
    if not isinstance(origens, list) or not origens:
        return ERRO_ORIGEM_INVALIDA

    possui_destino = False
    for origem in origens:
        if not isinstance(origem, dict):
            return ERRO_ORIGEM_INVALIDA
        if origem.get("ativo", True) and not origem.get("caminho"):
            return ERRO_ORIGEM_INVALIDA
        tipos = origem.get("tipos_arquivo", [])
        if not isinstance(tipos, list):
            return ERRO_DADOS_INVALIDOS
        for tipo in tipos:
            if not isinstance(tipo, dict):
                return ERRO_DADOS_INVALIDOS
            destinos = tipo.get("destinos", [])
            if not isinstance(destinos, list):
                return ERRO_DESTINO_INVALIDO
            if destinos:
                possui_destino = True
            if not origem.get("ativo", True) or not tipo.get("ativo", True):
                continue
            codigo = validar_destinos_do_tipo(tipo)
            if codigo != OK:
                return codigo

    if not possui_destino:
        return ERRO_DESTINO_INVALIDO
    return OK


def validar_destinos_do_tipo(tipo):
    """Valida destinos e conflito de operacoes de um tipo."""
    destinos = tipo.get("destinos", [])
    operacoes_remocao = []

    for destino in destinos:
        if not isinstance(destino, dict) or not destino.get("caminho"):
            return ERRO_DESTINO_INVALIDO
        operacao = destino.get("operacao", "copiar")
        if operacao not in OPERACOES_VALIDAS:
            return ERRO_OPERACAO_INVALIDA
        if operacao in ("mover", "recortar"):
            operacoes_remocao.append(destino)

    if operacoes_remocao and len(destinos) > 1:
        return ERRO_OPERACAO_INVALIDA

    return OK


def executar_backup(perfil):
    """Executa backup de um perfil."""
    perfil_id = perfil.get("id") if isinstance(perfil, dict) else None
    resultado = montar_resultado_backup(perfil_id)

    codigo_validacao = validar_perfil_para_backup(perfil)
    if codigo_validacao != OK:
        resultado["status"] = "erro"
        resultado["erros"].append("Perfil invalido para backup.")
        return codigo_validacao, resultado

    if perfil_usa_fluxo_configurado(perfil):
        return executar_backup_configurado(perfil)

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


def executar_backup_configurado(perfil):
    """Executa backup no modelo origem -> tipo -> destino."""
    resultado = montar_resultado_backup(perfil.get("id"))
    primeiro_erro = OK

    for origem in perfil.get("origens_configuradas", []):
        if not origem.get("ativo", True):
            continue
        codigo = executar_backup_da_origem_configurada(origem, resultado)
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


def executar_backup_da_origem_configurada(origem, resultado):
    """Executa todos os tipos de uma origem configurada."""
    caminhos = file_utils.listar_arquivos_em_origem(origem.get("caminho"))
    primeiro_erro = OK

    for tipo in origem.get("tipos_arquivo", []):
        if not tipo.get("ativo", True):
            continue
        arquivos_validos = filtrar_arquivos_por_tipo(caminhos, tipo)
        for arquivo in arquivos_validos:
            resultado_arquivo = processar_arquivo_para_destinos_configurados(arquivo, tipo.get("destinos", []), tipo)
            aplicar_resultado_arquivo(resultado, resultado_arquivo)
            if primeiro_erro == OK and resultado_arquivo.get("codigo") != OK:
                primeiro_erro = resultado_arquivo.get("codigo")

    return primeiro_erro


def filtrar_arquivos_por_tipo(caminhos, tipo):
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


def aplicar_resultado_arquivo(resultado, resultado_arquivo):
    """Acumula resultado de um arquivo no resultado geral."""
    if resultado_arquivo.get("processado"):
        resultado["arquivos_processados"] += 1
    resultado["arquivos_copiados"] += resultado_arquivo.get("arquivos_copiados", 0)
    resultado["arquivos_movidos"] += resultado_arquivo.get("arquivos_movidos", 0)
    resultado["arquivos_recortados"] += resultado_arquivo.get("arquivos_recortados", 0)
    resultado["arquivos"].extend(resultado_arquivo.get("arquivos", []))
    resultado["erros"].extend(resultado_arquivo.get("erros", []))
    return resultado


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
        resultado["arquivos_recortados"] += resultado_arquivo.get("arquivos_recortados", 0)
        resultado["arquivos"].extend(resultado_arquivo.get("arquivos", []))
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
        return processar_copia_para_destinos(arquivo, destinos, resultado)
    if operacao == "mover":
        return processar_movimento_para_destinos(arquivo, destinos, resultado)
    if operacao == "recortar":
        return processar_recorte_para_destinos(arquivo, destinos, resultado)

    resultado["codigo"] = ERRO_OPERACAO_INVALIDA
    resultado["erros"].append("Operacao invalida.")
    return resultado


def processar_arquivo_para_destinos_configurados(arquivo, destinos, tipo):
    """Processa arquivo usando destinos com operacao individual."""
    codigo = validar_destinos_do_tipo({"destinos": destinos})
    if codigo != OK:
        return {
            "codigo": codigo,
            "processado": False,
            "arquivos_copiados": 0,
            "arquivos_movidos": 0,
            "arquivos_recortados": 0,
            "arquivos": [],
            "erros": [montar_erro_arquivo(arquivo, tipo.get("nome", ""), codigo)],
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
        resultado_operacao = processar_arquivo_para_destinos(arquivo, [caminho], operacao)
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


def processar_copia_para_destinos(arquivo, destinos, resultado):
    """Copia um arquivo para todos os destinos."""
    for destino in destinos:
        caminho_destino = gerar_caminho_destino(arquivo, destino)
        codigo = copiar_arquivo(arquivo.get("caminho"), caminho_destino)
        if codigo == OK:
            resultado["arquivos_copiados"] += 1
            resultado["processado"] = True
            resultado["arquivos"].append(montar_registro_arquivo(arquivo, caminho_destino, "copiar", OK))
        else:
            resultado["codigo"] = codigo
            resultado["erros"].append(montar_erro_arquivo(arquivo, destino, codigo))
            resultado["arquivos"].append(montar_registro_arquivo(arquivo, caminho_destino, "copiar", codigo))
    return resultado


def processar_movimento_para_destinos(arquivo, destinos, resultado):
    """Copia um arquivo para todos os destinos e remove a origem ao final."""
    copias_realizadas = 0
    for destino in destinos:
        caminho_destino = gerar_caminho_destino(arquivo, destino)
        codigo = copiar_arquivo(arquivo.get("caminho"), caminho_destino)
        if codigo == OK:
            copias_realizadas += 1
            resultado["arquivos"].append(montar_registro_arquivo(arquivo, caminho_destino, "mover", OK))
        else:
            resultado["codigo"] = codigo
            resultado["erros"].append(montar_erro_arquivo(arquivo, destino, codigo))
            resultado["arquivos"].append(montar_registro_arquivo(arquivo, caminho_destino, "mover", codigo))

    if resultado["erros"]:
        return resultado

    try:
        Path(arquivo.get("caminho")).unlink()
    except (OSError, TypeError, ValueError):
        resultado["codigo"] = ERRO_FALHA_AO_MOVER
        resultado["erros"].append(montar_erro_arquivo(arquivo, "", ERRO_FALHA_AO_MOVER))
        resultado["arquivos"].append(montar_registro_arquivo(arquivo, "", "mover", ERRO_FALHA_AO_MOVER))
        return resultado

    resultado["processado"] = True
    resultado["arquivos_movidos"] = 1
    resultado["arquivos_copiados"] = copias_realizadas
    return resultado


def processar_recorte_para_destinos(arquivo, destinos, resultado):
    """Recorta um arquivo para um destino."""
    resultado = processar_movimento_para_destinos(arquivo, destinos, resultado)
    for registro in resultado.get("arquivos", []):
        if registro.get("operacao") == "mover":
            registro["operacao"] = "recortar"
    if resultado.get("processado"):
        resultado["arquivos_recortados"] = resultado.get("arquivos_movidos", 0)
        resultado["arquivos_movidos"] = 0
    return resultado


def montar_registro_arquivo(arquivo, destino, operacao, codigo):
    """Monta registro detalhado de arquivo processado."""
    if not isinstance(arquivo, dict):
        arquivo = {}

    return {
        "nome": arquivo.get("nome", Path(arquivo.get("caminho", "")).name),
        "extensao": arquivo.get("extensao", ""),
        "tipo": arquivo.get("tipo_nome", ""),
        "tamanho": arquivo.get("tamanho", 0),
        "origem": arquivo.get("caminho", ""),
        "destino": str(destino),
        "operacao": operacao,
        "status": "sucesso" if codigo == OK else "erro",
        "codigo": codigo,
    }


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
    except (OSError, TypeError, ValueError):
        return ERRO_DESTINO_INVALIDO

    return OK
