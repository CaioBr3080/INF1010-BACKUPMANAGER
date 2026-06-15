import tempfile
import unittest
from datetime import datetime
from pathlib import Path

from backupmanager import file_utils


class TestFileUtils(unittest.TestCase):
    def test_caminho_existe_para_arquivo_e_diretorio(self):
        with tempfile.TemporaryDirectory() as pasta:
            arquivo = Path(pasta) / "arquivo.txt"
            arquivo.write_text("conteudo", encoding="utf-8")

            self.assertTrue(file_utils.caminho_existe(pasta))
            self.assertTrue(file_utils.caminho_existe(arquivo))

    def test_caminho_existe_retorna_false_para_invalido(self):
        with tempfile.TemporaryDirectory() as pasta:
            inexistente = Path(pasta) / "nao_existe"

            self.assertFalse(file_utils.caminho_existe(inexistente))
            self.assertFalse(file_utils.caminho_existe(None))

    def test_caminho_e_diretorio(self):
        with tempfile.TemporaryDirectory() as pasta:
            arquivo = Path(pasta) / "arquivo.txt"
            arquivo.write_text("conteudo", encoding="utf-8")

            self.assertTrue(file_utils.caminho_e_diretorio(pasta))
            self.assertFalse(file_utils.caminho_e_diretorio(arquivo))
            self.assertFalse(file_utils.caminho_e_diretorio(None))

    def test_verificar_permissao_leitura(self):
        with tempfile.TemporaryDirectory() as pasta:
            arquivo = Path(pasta) / "arquivo.txt"
            arquivo.write_text("conteudo", encoding="utf-8")

            self.assertTrue(file_utils.verificar_permissao_leitura(arquivo))
            self.assertFalse(file_utils.verificar_permissao_leitura(None))

    def test_verificar_permissao_escrita(self):
        with tempfile.TemporaryDirectory() as pasta:
            self.assertTrue(file_utils.verificar_permissao_escrita(pasta))
            self.assertFalse(file_utils.verificar_permissao_escrita(None))

    def test_listar_arquivos_em_origem(self):
        with tempfile.TemporaryDirectory() as pasta:
            arquivo_1 = Path(pasta) / "a.txt"
            subpasta = Path(pasta) / "sub"
            arquivo_2 = subpasta / "b.txt"
            subpasta.mkdir()
            arquivo_1.write_text("a", encoding="utf-8")
            arquivo_2.write_text("b", encoding="utf-8")

            arquivos = file_utils.listar_arquivos_em_origem(pasta)

            self.assertEqual(set(arquivos), {str(arquivo_1), str(arquivo_2)})

    def test_listar_arquivos_em_origem_invalida(self):
        with tempfile.TemporaryDirectory() as pasta:
            arquivo = Path(pasta) / "arquivo.txt"
            arquivo.write_text("conteudo", encoding="utf-8")

            self.assertEqual(file_utils.listar_arquivos_em_origem(None), [])
            self.assertEqual(file_utils.listar_arquivos_em_origem(arquivo), [])
            self.assertEqual(file_utils.listar_arquivos_em_origem(Path(pasta) / "inexistente"), [])

    def test_listar_arquivos_de_origens(self):
        with tempfile.TemporaryDirectory() as pasta_1:
            with tempfile.TemporaryDirectory() as pasta_2:
                arquivo_1 = Path(pasta_1) / "a.txt"
                arquivo_2 = Path(pasta_2) / "b.txt"
                arquivo_1.write_text("a", encoding="utf-8")
                arquivo_2.write_text("b", encoding="utf-8")

                arquivos = file_utils.listar_arquivos_de_origens([pasta_1, pasta_2, None])

                self.assertEqual(set(arquivos), {str(arquivo_1), str(arquivo_2)})

    def test_listar_arquivos_de_origens_rejeita_tipo_invalido(self):
        self.assertEqual(file_utils.listar_arquivos_de_origens(None), [])
        self.assertEqual(file_utils.listar_arquivos_de_origens("C:/origem"), [])

    def test_obter_extensao(self):
        self.assertEqual(file_utils.obter_extensao("arquivo.TXT"), ".txt")
        self.assertEqual(file_utils.obter_extensao("arquivo"), "")
        self.assertEqual(file_utils.obter_extensao(None), "")

    def test_obter_metadados_arquivo(self):
        with tempfile.TemporaryDirectory() as pasta:
            arquivo = Path(pasta) / "Relatorio.TXT"
            conteudo = "abc"
            arquivo.write_text(conteudo, encoding="utf-8")

            metadados = file_utils.obter_metadados_arquivo(arquivo)

            self.assertEqual(metadados["caminho"], str(arquivo))
            self.assertEqual(metadados["nome"], "Relatorio.TXT")
            self.assertEqual(metadados["extensao"], ".txt")
            self.assertEqual(metadados["tamanho"], len(conteudo))
            self.assertIsInstance(metadados["data_modificacao"], float)

    def test_obter_metadados_arquivo_invalido(self):
        with tempfile.TemporaryDirectory() as pasta:
            self.assertIsNone(file_utils.obter_metadados_arquivo(None))
            self.assertIsNone(file_utils.obter_metadados_arquivo(pasta))
            self.assertIsNone(file_utils.obter_metadados_arquivo(Path(pasta) / "inexistente.txt"))

    def test_filtrar_por_extensao(self):
        arquivo = {"extensao": ".py", "nome": "main.py", "tamanho": 10}
        restricoes = {"extensoes_permitidas": [".py"]}

        self.assertTrue(file_utils.atende_restricao_extensao(arquivo, restricoes))

    def test_filtrar_por_extensao_aceita_lista_vazia(self):
        arquivo = {"extensao": ".zip", "nome": "backup.zip", "tamanho": 10}
        restricoes = {"extensoes_permitidas": []}

        self.assertTrue(file_utils.atende_restricao_extensao(arquivo, restricoes))

    def test_filtrar_por_extensao_normaliza_ponto_e_maiusculas(self):
        arquivo = {"extensao": ".py", "nome": "main.py", "tamanho": 10}
        restricoes = {"extensoes_permitidas": ["PY"]}

        self.assertTrue(file_utils.atende_restricao_extensao(arquivo, restricoes))

    def test_filtrar_por_extensao_rejeita_extensao_nao_permitida(self):
        arquivo = {"extensao": ".txt", "nome": "nota.txt", "tamanho": 10}
        restricoes = {"extensoes_permitidas": [".py"]}

        self.assertFalse(file_utils.atende_restricao_extensao(arquivo, restricoes))

    def test_filtrar_por_nome(self):
        arquivo = {"extensao": ".txt", "nome": "relatorio_final.txt", "tamanho": 10}
        restricoes = {"nome_contem": "relatorio"}

        self.assertTrue(file_utils.atende_restricao_nome(arquivo, restricoes))

    def test_filtrar_por_nome_aceita_campo_vazio(self):
        arquivo = {"extensao": ".txt", "nome": "qualquer.txt", "tamanho": 10}
        restricoes = {"nome_contem": ""}

        self.assertTrue(file_utils.atende_restricao_nome(arquivo, restricoes))

    def test_filtrar_por_nome_ignora_maiusculas(self):
        arquivo = {"extensao": ".txt", "nome": "Relatorio_Final.txt", "tamanho": 10}
        restricoes = {"nome_contem": "relatorio"}

        self.assertTrue(file_utils.atende_restricao_nome(arquivo, restricoes))

    def test_filtrar_por_nome_rejeita_trecho_ausente(self):
        arquivo = {"extensao": ".txt", "nome": "notas.txt", "tamanho": 10}
        restricoes = {"nome_contem": "relatorio"}

        self.assertFalse(file_utils.atende_restricao_nome(arquivo, restricoes))

    def test_filtrar_por_tamanho_minimo(self):
        arquivo = {"extensao": ".txt", "nome": "a.txt", "tamanho": 100}
        restricoes = {"tamanho_min": 50, "tamanho_max": None}

        self.assertTrue(file_utils.atende_restricao_tamanho(arquivo, restricoes))

    def test_filtrar_por_tamanho_maximo(self):
        arquivo = {"extensao": ".txt", "nome": "a.txt", "tamanho": 100}
        restricoes = {"tamanho_min": 0, "tamanho_max": 150}

        self.assertTrue(file_utils.atende_restricao_tamanho(arquivo, restricoes))

    def test_filtrar_por_tamanho_rejeita_menor_que_minimo(self):
        arquivo = {"extensao": ".txt", "nome": "a.txt", "tamanho": 20}
        restricoes = {"tamanho_min": 50, "tamanho_max": None}

        self.assertFalse(file_utils.atende_restricao_tamanho(arquivo, restricoes))

    def test_filtrar_por_tamanho_rejeita_maior_que_maximo(self):
        arquivo = {"extensao": ".txt", "nome": "a.txt", "tamanho": 200}
        restricoes = {"tamanho_min": 0, "tamanho_max": 150}

        self.assertFalse(file_utils.atende_restricao_tamanho(arquivo, restricoes))

    def test_filtrar_por_data_sem_limites(self):
        arquivo = {"data_modificacao": datetime(2026, 5, 11, 14, 30, 0).timestamp()}
        restricoes = {"data_modificacao_min": None, "data_modificacao_max": None}

        self.assertTrue(file_utils.atende_restricao_data_modificacao(arquivo, restricoes))

    def test_filtrar_por_data_minima_e_maxima(self):
        arquivo = {"data_modificacao": datetime(2026, 5, 11, 14, 30, 0).timestamp()}
        restricoes = {
            "data_modificacao_min": "2026-05-11 14:00:00",
            "data_modificacao_max": "2026-05-11 15:00:00",
        }

        self.assertTrue(file_utils.atende_restricao_data_modificacao(arquivo, restricoes))

    def test_filtrar_por_data_rejeita_antes_da_minima(self):
        arquivo = {"data_modificacao": datetime(2026, 5, 11, 13, 0, 0).timestamp()}
        restricoes = {"data_modificacao_min": "2026-05-11 14:00:00"}

        self.assertFalse(file_utils.atende_restricao_data_modificacao(arquivo, restricoes))

    def test_filtrar_por_data_rejeita_depois_da_maxima(self):
        arquivo = {"data_modificacao": datetime(2026, 5, 11, 16, 0, 0).timestamp()}
        restricoes = {"data_modificacao_max": "2026-05-11 15:00:00"}

        self.assertFalse(file_utils.atende_restricao_data_modificacao(arquivo, restricoes))

    def test_arquivo_atende_restricoes_combinadas(self):
        arquivo = {
            "extensao": ".py",
            "nome": "relatorio.py",
            "tamanho": 100,
            "data_modificacao": datetime(2026, 5, 11, 14, 30, 0).timestamp(),
        }
        restricoes = {
            "extensoes_permitidas": [".py"],
            "nome_contem": "relatorio",
            "tamanho_min": 50,
            "tamanho_max": 150,
            "data_modificacao_min": "2026-05-11 14:00:00",
            "data_modificacao_max": "2026-05-11 15:00:00",
        }

        self.assertTrue(file_utils.arquivo_atende_restricoes(arquivo, restricoes))

    def test_arquivo_atende_restricoes_rejeita_quando_um_filtro_falha(self):
        arquivo = {
            "extensao": ".txt",
            "nome": "relatorio.txt",
            "tamanho": 100,
            "data_modificacao": datetime(2026, 5, 11, 14, 30, 0).timestamp(),
        }
        restricoes = {
            "extensoes_permitidas": [".py"],
            "nome_contem": "relatorio",
            "tamanho_min": 50,
            "tamanho_max": 150,
            "data_modificacao_min": None,
            "data_modificacao_max": None,
        }

        self.assertFalse(file_utils.arquivo_atende_restricoes(arquivo, restricoes))

    def test_arquivo_atende_restricoes_aceita_restricoes_vazias(self):
        arquivo = {
            "extensao": ".zip",
            "nome": "backup.zip",
            "tamanho": 100,
            "data_modificacao": datetime(2026, 5, 11, 14, 30, 0).timestamp(),
        }
        restricoes = {
            "extensoes_permitidas": [],
            "nome_contem": "",
            "tamanho_min": 0,
            "tamanho_max": None,
            "data_modificacao_min": None,
            "data_modificacao_max": None,
        }

        self.assertTrue(file_utils.arquivo_atende_restricoes(arquivo, restricoes))

    def test_arquivo_atende_restricoes_rejeita_dados_invalidos(self):
        arquivo = {
            "extensao": ".py",
            "nome": "relatorio.py",
            "tamanho": 100,
            "data_modificacao": datetime(2026, 5, 11, 14, 30, 0).timestamp(),
        }
        restricoes = {
            "extensoes_permitidas": [],
            "nome_contem": "",
            "tamanho_min": 0,
            "tamanho_max": None,
            "data_modificacao_min": None,
            "data_modificacao_max": None,
        }

        self.assertFalse(file_utils.arquivo_atende_restricoes(None, restricoes))
        self.assertFalse(file_utils.arquivo_atende_restricoes(arquivo, None))


if __name__ == "__main__":
    unittest.main()
