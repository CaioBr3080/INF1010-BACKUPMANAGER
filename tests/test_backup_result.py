from backupmanager.domain import backup_result
from backupmanager.return_codes import OK, ERRO_FALHA_AO_COPIAR
from tests.assertions import (
    assert_equal,
    assert_false,
    assert_in,
    assert_is_instance,
    assert_is_none,
    assert_is_not_none,
    assert_not_equal,
    assert_not_in,
    assert_true,
)


def test_montar_resultado_backup_cria_contadores_zerados():
    resultado = backup_result.montar_resultado_backup("perfil_001")

    assert_equal(resultado["perfil_id"], "perfil_001")
    assert_equal(resultado["status"], "nao_executado")
    assert_equal(resultado["arquivos_processados"], 0)
    assert_equal(resultado["arquivos"], [])
    assert_equal(resultado["erros"], [])

def test_aplicar_resultado_arquivo_acumula_contadores_e_listas():
    resultado = backup_result.montar_resultado_backup("perfil_001")
    resultado_arquivo = {
        "processado": True,
        "arquivos_copiados": 1,
        "arquivos_movidos": 0,
        "arquivos_recortados": 0,
        "arquivos": [{"nome": "a.txt"}],
        "erros": [{"arquivo": "b.txt"}],
    }

    backup_result.aplicar_resultado_arquivo(resultado, resultado_arquivo)

    assert_equal(resultado["arquivos_processados"], 1)
    assert_equal(resultado["arquivos_copiados"], 1)
    assert_equal(resultado["arquivos"], [{"nome": "a.txt"}])
    assert_equal(resultado["erros"], [{"arquivo": "b.txt"}])

def test_montar_registro_arquivo_preserva_metadados():
    arquivo = {
        "nome": "relatorio.pdf",
        "extensao": ".pdf",
        "tipo_nome": "PDFs",
        "tamanho": 123,
        "caminho": "C:/Origem/relatorio.pdf",
    }

    registro = backup_result.montar_registro_arquivo(arquivo, "D:/Backup/relatorio.pdf", "copiar", OK)

    assert_equal(registro["nome"], "relatorio.pdf")
    assert_equal(registro["tipo"], "PDFs")
    assert_equal(registro["tamanho"], 123)
    assert_equal(registro["status"], "sucesso")

def test_montar_erro_arquivo():
    erro = backup_result.montar_erro_arquivo({"nome": "a.txt"}, "D:/Backup", ERRO_FALHA_AO_COPIAR)

    assert_equal(erro["arquivo"], "a.txt")
    assert_equal(erro["destino"], "D:/Backup")
    assert_equal(erro["codigo"], ERRO_FALHA_AO_COPIAR)
