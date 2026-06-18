import unittest

from backupmanager import backup_result
from backupmanager.return_codes import OK, ERRO_FALHA_AO_COPIAR


class TestBackupResult(unittest.TestCase):
    def test_montar_resultado_backup_cria_contadores_zerados(self):
        resultado = backup_result.montar_resultado_backup("perfil_001")

        self.assertEqual(resultado["perfil_id"], "perfil_001")
        self.assertEqual(resultado["status"], "nao_executado")
        self.assertEqual(resultado["arquivos_processados"], 0)
        self.assertEqual(resultado["arquivos"], [])
        self.assertEqual(resultado["erros"], [])

    def test_aplicar_resultado_arquivo_acumula_contadores_e_listas(self):
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

        self.assertEqual(resultado["arquivos_processados"], 1)
        self.assertEqual(resultado["arquivos_copiados"], 1)
        self.assertEqual(resultado["arquivos"], [{"nome": "a.txt"}])
        self.assertEqual(resultado["erros"], [{"arquivo": "b.txt"}])

    def test_montar_registro_arquivo_preserva_metadados(self):
        arquivo = {
            "nome": "relatorio.pdf",
            "extensao": ".pdf",
            "tipo_nome": "PDFs",
            "tamanho": 123,
            "caminho": "C:/Origem/relatorio.pdf",
        }

        registro = backup_result.montar_registro_arquivo(arquivo, "D:/Backup/relatorio.pdf", "copiar", OK)

        self.assertEqual(registro["nome"], "relatorio.pdf")
        self.assertEqual(registro["tipo"], "PDFs")
        self.assertEqual(registro["tamanho"], 123)
        self.assertEqual(registro["status"], "sucesso")

    def test_montar_erro_arquivo(self):
        erro = backup_result.montar_erro_arquivo({"nome": "a.txt"}, "D:/Backup", ERRO_FALHA_AO_COPIAR)

        self.assertEqual(erro["arquivo"], "a.txt")
        self.assertEqual(erro["destino"], "D:/Backup")
        self.assertEqual(erro["codigo"], ERRO_FALHA_AO_COPIAR)


if __name__ == "__main__":
    unittest.main()
