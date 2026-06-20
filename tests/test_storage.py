import tempfile
import unittest
from pathlib import Path

from backupmanager import storage
from backupmanager.return_codes import OK, ERRO_DADOS_INVALIDOS, ERRO_JSON_CORROMPIDO


class TestStorage(unittest.TestCase):
    def test_salvar_e_carregar_json(self):
        with tempfile.TemporaryDirectory() as pasta:
            caminho = Path(pasta) / "dados.json"
            dados = [{"nome": "Backup"}]

            codigo_salvar = storage._salvar_json(caminho, dados)
            codigo_carregar, carregado = storage._carregar_json(caminho, [])

            self.assertEqual(codigo_salvar, OK)
            self.assertEqual(codigo_carregar, OK)
            self.assertEqual(carregado, dados)

    def test_carregar_json_inexistente(self):
        with tempfile.TemporaryDirectory() as pasta:
            caminho = Path(pasta) / "inexistente.json"

            codigo, carregado = storage._carregar_json(caminho, [])

            self.assertEqual(codigo, OK)
            self.assertEqual(carregado, [])

    def test_carregar_json_corrompido(self):
        with tempfile.TemporaryDirectory() as pasta:
            caminho = Path(pasta) / "dados.json"
            caminho.write_text("{json invalido", encoding="utf-8")

            codigo, carregado = storage._carregar_json(caminho, [])

            self.assertEqual(codigo, ERRO_JSON_CORROMPIDO)
            self.assertEqual(carregado, [])

    def test_salvar_json_rejeita_dados_nao_serializaveis(self):
        with tempfile.TemporaryDirectory() as pasta:
            caminho = Path(pasta) / "dados.json"

            codigo = storage._salvar_json(caminho, {"valores": {1, 2}})

            self.assertEqual(codigo, ERRO_DADOS_INVALIDOS)

    def test_criar_arquivos_padrao(self):
        data_dir_original = storage._DATA_DIR
        perfis_path_original = storage._PERFIS_PATH
        config_path_original = storage._CONFIG_PATH

        try:
            with tempfile.TemporaryDirectory() as pasta:
                storage._DATA_DIR = Path(pasta) / "data"
                storage._PERFIS_PATH = storage._DATA_DIR / "perfis.json"
                storage._CONFIG_PATH = storage._DATA_DIR / "config.json"

                codigo = storage.criar_arquivos_padrao()

                self.assertEqual(codigo, OK)
                self.assertTrue(storage._PERFIS_PATH.exists())
                self.assertTrue(storage._CONFIG_PATH.exists())
                self.assertEqual(storage._carregar_json(storage._PERFIS_PATH, None), (OK, []))
                self.assertEqual(storage._carregar_json(storage._CONFIG_PATH, None), (OK, {}))
        finally:
            storage._DATA_DIR = data_dir_original
            storage._PERFIS_PATH = perfis_path_original
            storage._CONFIG_PATH = config_path_original


if __name__ == "__main__":
    unittest.main()
