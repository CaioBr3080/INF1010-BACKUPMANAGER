"""Montagem e acumulacao de resultados de backup."""

from backupmanager.engine import file_utils
from backupmanager.return_codes import OK

__all__ = [
    "montar_resultado_backup",
    "montar_resultado_arquivo",
    "definir_status_resultado",
    "obter_status_resultado",
    "obter_arquivos_processados",
    "resultado_possui_erros",
    "obter_arquivos_resultado",
    "obter_erros_resultado",
    "obter_contador_resultado",
    "aplicar_resultado_arquivo",
    "resultado_arquivo_foi_processado",
    "obter_codigo_resultado_arquivo",
    "obter_copiados_resultado_arquivo",
    "obter_movidos_resultado_arquivo",
    "obter_recortados_resultado_arquivo",
    "obter_erros_resultado_arquivo",
    "definir_codigo_resultado_arquivo",
    "definir_processado_resultado_arquivo",
    "somar_copiados_resultado_arquivo",
    "somar_movidos_resultado_arquivo",
    "somar_recortados_resultado_arquivo",
    "zerar_movidos_resultado_arquivo",
    "adicionar_registro_resultado_arquivo",
    "adicionar_erro_resultado_arquivo",
    "resultado_arquivo_possui_erros",
    "obter_registros_resultado_arquivo",
    "marcar_registros_como_recorte",
    "montar_registro_arquivo",
    "montar_erro_arquivo",
]


def montar_resultado_backup(perfil_id):
    """Cria o resultado base de uma execucao de backup.

    O dicionario retornado acompanha todo o ciclo da execucao e concentra
    status, contadores, registros de arquivos e erros. `perfil_id` e copiado
    para identificar qual perfil gerou o resultado.
    """
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


def montar_resultado_arquivo():
    """Cria o resultado acumulado para o processamento de um arquivo.

    O retorno e administrado pelas funcoes publicas deste modulo e depois pode
    ser agregado ao resultado geral com `aplicar_resultado_arquivo`.
    """
    return {
        "codigo": OK,
        "processado": False,
        "arquivos_copiados": 0,
        "arquivos_movidos": 0,
        "arquivos_recortados": 0,
        "arquivos": [],
        "erros": [],
    }


def definir_status_resultado(resultado, status):
    """Altera o status textual do resultado geral."""
    resultado["status"] = status
    return resultado


def obter_status_resultado(resultado):
    """Retorna o status textual do resultado geral."""
    return resultado.get("status", "")


def obter_arquivos_processados(resultado):
    """Retorna a quantidade de arquivos processados no resultado geral."""
    return resultado.get("arquivos_processados", 0)


def resultado_possui_erros(resultado):
    """Indica se o resultado geral possui erros registrados."""
    return bool(resultado.get("erros", []))


def obter_arquivos_resultado(resultado):
    """Retorna os registros de arquivos do resultado geral."""
    return resultado.get("arquivos", [])


def obter_erros_resultado(resultado):
    """Retorna os erros do resultado geral."""
    return resultado.get("erros", [])


def obter_contador_resultado(resultado, nome):
    """Retorna um contador numerico do resultado geral."""
    return resultado.get(nome, 0)


def aplicar_resultado_arquivo(resultado, resultado_arquivo):
    """Acumula o resultado de um arquivo no resultado geral.

    Soma contadores de copia/movimento/recorte, incrementa processados quando
    o arquivo foi efetivamente tratado e anexa listas de registros e erros. A
    mutacao ocorre no dicionario `resultado` recebido.
    """
    if resultado_arquivo.get("processado"):
        resultado["arquivos_processados"] += 1
    resultado["arquivos_copiados"] += resultado_arquivo.get("arquivos_copiados", 0)
    resultado["arquivos_movidos"] += resultado_arquivo.get("arquivos_movidos", 0)
    resultado["arquivos_recortados"] += resultado_arquivo.get("arquivos_recortados", 0)
    resultado["arquivos"].extend(resultado_arquivo.get("arquivos", []))
    resultado["erros"].extend(resultado_arquivo.get("erros", []))
    return resultado


def resultado_arquivo_foi_processado(resultado_arquivo):
    """Indica se o resultado individual processou o arquivo."""
    return bool(resultado_arquivo.get("processado", False))


def obter_codigo_resultado_arquivo(resultado_arquivo):
    """Retorna o codigo de retorno do resultado individual."""
    return resultado_arquivo.get("codigo", OK)


def obter_copiados_resultado_arquivo(resultado_arquivo):
    """Retorna o contador de copias do resultado individual."""
    return resultado_arquivo.get("arquivos_copiados", 0)


def obter_movidos_resultado_arquivo(resultado_arquivo):
    """Retorna o contador de movimentos do resultado individual."""
    return resultado_arquivo.get("arquivos_movidos", 0)


def obter_recortados_resultado_arquivo(resultado_arquivo):
    """Retorna o contador de recortes do resultado individual."""
    return resultado_arquivo.get("arquivos_recortados", 0)


def obter_erros_resultado_arquivo(resultado_arquivo):
    """Retorna a lista de erros do resultado individual."""
    return resultado_arquivo.get("erros", [])


def definir_codigo_resultado_arquivo(resultado_arquivo, codigo):
    """Altera o codigo de retorno do resultado individual."""
    resultado_arquivo["codigo"] = codigo
    return resultado_arquivo


def definir_processado_resultado_arquivo(resultado_arquivo, processado):
    """Marca se o resultado individual processou o arquivo."""
    resultado_arquivo["processado"] = bool(processado)
    return resultado_arquivo


def somar_copiados_resultado_arquivo(resultado_arquivo, quantidade=1):
    """Soma arquivos copiados ao resultado individual."""
    resultado_arquivo["arquivos_copiados"] += quantidade
    return resultado_arquivo


def somar_movidos_resultado_arquivo(resultado_arquivo, quantidade=1):
    """Soma arquivos movidos ao resultado individual."""
    resultado_arquivo["arquivos_movidos"] += quantidade
    return resultado_arquivo


def somar_recortados_resultado_arquivo(resultado_arquivo, quantidade=1):
    """Soma arquivos recortados ao resultado individual."""
    resultado_arquivo["arquivos_recortados"] += quantidade
    return resultado_arquivo


def zerar_movidos_resultado_arquivo(resultado_arquivo):
    """Zera o contador de movimentos do resultado individual."""
    resultado_arquivo["arquivos_movidos"] = 0
    return resultado_arquivo


def adicionar_registro_resultado_arquivo(resultado_arquivo, registro):
    """Adiciona um registro de arquivo ao resultado individual."""
    resultado_arquivo["arquivos"].append(registro)
    return resultado_arquivo


def adicionar_erro_resultado_arquivo(resultado_arquivo, erro):
    """Adiciona um erro ao resultado individual."""
    resultado_arquivo["erros"].append(erro)
    return resultado_arquivo


def resultado_arquivo_possui_erros(resultado_arquivo):
    """Indica se o resultado individual possui erros."""
    return bool(resultado_arquivo.get("erros", []))


def obter_registros_resultado_arquivo(resultado_arquivo):
    """Retorna os registros do resultado individual."""
    return resultado_arquivo.get("arquivos", [])


def marcar_registros_como_recorte(resultado_arquivo):
    """Troca operacao `mover` por `recortar` nos registros individuais."""
    for registro in obter_registros_resultado_arquivo(resultado_arquivo):
        if registro.get("operacao") == "mover":
            registro["operacao"] = "recortar"
    return resultado_arquivo


def montar_registro_arquivo(arquivo, destino, operacao, codigo):
    """Monta o registro detalhado de um arquivo processado.

    Usa os metadados coletados em `arquivo`, registra destino, operacao,
    status derivado do codigo de retorno e informacoes uteis para mensagens
    da interface. Aceita entrada parcialmente vazia para registrar falhas.
    """
    if not isinstance(arquivo, dict):
        arquivo = {}

    return {
        "nome": file_utils.obter_nome_arquivo(arquivo),
        "extensao": file_utils.obter_extensao_arquivo(arquivo),
        "tipo": file_utils.obter_nome_tipo_arquivo(arquivo),
        "tamanho": file_utils.obter_tamanho_arquivo(arquivo),
        "origem": file_utils.obter_caminho_arquivo(arquivo),
        "destino": str(destino),
        "operacao": operacao,
        "status": "sucesso" if codigo == OK else "erro",
        "codigo": codigo,
    }


def montar_erro_arquivo(arquivo, destino, codigo):
    """Monta o registro simples de erro associado a um arquivo.

    O retorno contem nome do arquivo, destino envolvido e codigo de erro.
    """
    nome = file_utils.obter_nome_arquivo(arquivo)
    return {
        "arquivo": nome,
        "destino": str(destino),
        "codigo": codigo,
    }
