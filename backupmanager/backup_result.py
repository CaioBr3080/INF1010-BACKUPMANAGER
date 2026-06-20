"""Montagem e acumulacao de resultados de backup."""

from pathlib import Path

from backupmanager.return_codes import OK

__all__ = [
    "montar_resultado_backup",
    "aplicar_resultado_arquivo",
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


def montar_registro_arquivo(arquivo, destino, operacao, codigo):
    """Monta o registro detalhado de um arquivo processado.

    Usa os metadados coletados em `arquivo`, registra destino, operacao,
    status derivado do codigo de retorno e informacoes uteis para mensagens
    da interface. Aceita entrada parcialmente vazia para registrar falhas.
    """
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
    """Monta o registro simples de erro associado a um arquivo.

    O retorno contem nome do arquivo, destino envolvido e codigo de erro.
    """
    nome = arquivo.get("nome", arquivo.get("caminho", "")) if isinstance(arquivo, dict) else ""
    return {
        "arquivo": nome,
        "destino": str(destino),
        "codigo": codigo,
    }
