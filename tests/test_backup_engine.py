import tempfile
import unittest
from pathlib import Path

from backupmanager import backup_engine
from backupmanager.return_codes import (
    OK,
    ERRO_ARQUIVO_NAO_ENCONTRADO,
    ERRO_BACKUP_SEM_ARQUIVOS,
    ERRO_DADOS_INVALIDOS,
    ERRO_DESTINO_INVALIDO,
    ERRO_OPERACAO_INVALIDA,
    ERRO_ORIGEM_INVALIDA,
)


class TestBackupEngine(unittest.TestCase):
    def test_montar_resultado_backup(self):
        resultado = backup_engine.montar_resultado_backup("perfil_001")

        self.assertEqual(resultado["perfil_id"], "perfil_001")
        self.assertEqual(resultado["arquivos_processados"], 0)

    def test_executar_backup_base_sem_arquivos(self):
        codigo, resultado = backup_engine.executar_backup({
            "id": "perfil_001",
            "origens": ["C:/origem"],
            "destinos": ["D:/destino"],
            "operacao": "copiar",
        })

        self.assertEqual(codigo, ERRO_BACKUP_SEM_ARQUIVOS)
        self.assertEqual(resultado["perfil_id"], "perfil_001")

    def test_validar_perfil_para_backup_valido(self):
        perfil = {
            "id": "perfil_001",
            "origens": ["C:/origem"],
            "destinos": ["D:/destino"],
            "operacao": "copiar",
        }

        self.assertEqual(backup_engine.validar_perfil_para_backup(perfil), OK)

    def test_validar_perfil_para_backup_rejeita_dados_invalidos(self):
        self.assertEqual(
            backup_engine.validar_perfil_para_backup(None),
            ERRO_DADOS_INVALIDOS,
        )

    def test_validar_perfil_para_backup_rejeita_sem_origem(self):
        perfil = {
            "id": "perfil_001",
            "origens": [],
            "destinos": ["D:/destino"],
            "operacao": "copiar",
        }

        self.assertEqual(
            backup_engine.validar_perfil_para_backup(perfil),
            ERRO_ORIGEM_INVALIDA,
        )

    def test_validar_perfil_para_backup_rejeita_sem_destino(self):
        perfil = {
            "id": "perfil_001",
            "origens": ["C:/origem"],
            "destinos": [],
            "operacao": "copiar",
        }

        self.assertEqual(
            backup_engine.validar_perfil_para_backup(perfil),
            ERRO_DESTINO_INVALIDO,
        )

    def test_validar_perfil_para_backup_rejeita_operacao_invalida(self):
        perfil = {
            "id": "perfil_001",
            "origens": ["C:/origem"],
            "destinos": ["D:/destino"],
            "operacao": "compactar",
        }

        self.assertEqual(
            backup_engine.validar_perfil_para_backup(perfil),
            ERRO_OPERACAO_INVALIDA,
        )

    def test_executar_backup_retorna_erro_de_validacao(self):
        codigo, resultado = backup_engine.executar_backup({
            "id": "perfil_001",
            "origens": [],
            "destinos": ["D:/destino"],
            "operacao": "copiar",
        })

        self.assertEqual(codigo, ERRO_ORIGEM_INVALIDA)
        self.assertEqual(resultado["status"], "erro")
        self.assertEqual(resultado["perfil_id"], "perfil_001")
        self.assertTrue(resultado["erros"])

    def test_gerar_caminho_destino_com_nome(self):
        arquivo = {"nome": "relatorio.txt", "caminho": "C:/origem/relatorio.txt"}

        caminho = backup_engine.gerar_caminho_destino(arquivo, "D:/backup")

        self.assertEqual(caminho, str(Path("D:/backup") / "relatorio.txt"))

    def test_gerar_caminho_destino_com_caminho_sem_nome(self):
        arquivo = {"caminho": "C:/origem/relatorio.txt"}

        caminho = backup_engine.gerar_caminho_destino(arquivo, "D:/backup")

        self.assertEqual(caminho, str(Path("D:/backup") / "relatorio.txt"))

    def test_gerar_caminho_destino_rejeita_dados_invalidos(self):
        self.assertIsNone(backup_engine.gerar_caminho_destino(None, "D:/backup"))
        self.assertIsNone(backup_engine.gerar_caminho_destino({}, "D:/backup"))
        self.assertIsNone(backup_engine.gerar_caminho_destino({"nome": "a.txt"}, ""))

    def test_criar_pasta_destino_se_necessario_cria_diretorio(self):
        with tempfile.TemporaryDirectory() as pasta:
            caminho_destino = Path(pasta) / "backup" / "subpasta" / "arquivo.txt"

            codigo = backup_engine.criar_pasta_destino_se_necessario(caminho_destino)

            self.assertEqual(codigo, OK)
            self.assertTrue(caminho_destino.parent.is_dir())

    def test_criar_pasta_destino_se_necessario_aceita_diretorio_existente(self):
        with tempfile.TemporaryDirectory() as pasta:
            caminho_destino = Path(pasta) / "arquivo.txt"

            codigo = backup_engine.criar_pasta_destino_se_necessario(caminho_destino)

            self.assertEqual(codigo, OK)
            self.assertTrue(Path(pasta).is_dir())

    def test_criar_pasta_destino_se_necessario_rejeita_caminho_invalido(self):
        self.assertEqual(
            backup_engine.criar_pasta_destino_se_necessario(None),
            ERRO_DESTINO_INVALIDO,
        )
        self.assertEqual(
            backup_engine.criar_pasta_destino_se_necessario(""),
            ERRO_DESTINO_INVALIDO,
        )

    def test_copiar_arquivo_copia_conteudo_e_mantem_original(self):
        with tempfile.TemporaryDirectory() as pasta:
            origem = Path(pasta) / "origem.txt"
            destino = Path(pasta) / "backup" / "origem.txt"
            origem.write_text("conteudo original", encoding="utf-8")

            codigo = backup_engine.copiar_arquivo(origem, destino)

            self.assertEqual(codigo, OK)
            self.assertTrue(origem.is_file())
            self.assertTrue(destino.is_file())
            self.assertEqual(destino.read_text(encoding="utf-8"), "conteudo original")

    def test_copiar_arquivo_retorna_erro_sem_quebrar(self):
        with tempfile.TemporaryDirectory() as pasta:
            origem = Path(pasta) / "inexistente.txt"
            destino = Path(pasta) / "backup" / "inexistente.txt"

            codigo = backup_engine.copiar_arquivo(origem, destino)

            self.assertEqual(codigo, ERRO_ARQUIVO_NAO_ENCONTRADO)

    def test_copiar_arquivo_rejeita_dados_invalidos(self):
        self.assertEqual(backup_engine.copiar_arquivo(None, "destino.txt"), ERRO_DADOS_INVALIDOS)
        self.assertEqual(backup_engine.copiar_arquivo("origem.txt", ""), ERRO_DADOS_INVALIDOS)

    def test_mover_arquivo_move_conteudo_e_remove_original(self):
        with tempfile.TemporaryDirectory() as pasta:
            origem = Path(pasta) / "origem.txt"
            destino = Path(pasta) / "backup" / "origem.txt"
            origem.write_text("conteudo movido", encoding="utf-8")

            codigo = backup_engine.mover_arquivo(origem, destino)

            self.assertEqual(codigo, OK)
            self.assertFalse(origem.exists())
            self.assertTrue(destino.is_file())
            self.assertEqual(destino.read_text(encoding="utf-8"), "conteudo movido")

    def test_mover_arquivo_retorna_erro_sem_quebrar(self):
        with tempfile.TemporaryDirectory() as pasta:
            origem = Path(pasta) / "inexistente.txt"
            destino = Path(pasta) / "backup" / "inexistente.txt"

            codigo = backup_engine.mover_arquivo(origem, destino)

            self.assertEqual(codigo, ERRO_ARQUIVO_NAO_ENCONTRADO)

    def test_mover_arquivo_rejeita_dados_invalidos(self):
        self.assertEqual(backup_engine.mover_arquivo(None, "destino.txt"), ERRO_DADOS_INVALIDOS)
        self.assertEqual(backup_engine.mover_arquivo("origem.txt", ""), ERRO_DADOS_INVALIDOS)

    def test_executar_backup_copia_para_multiplos_destinos(self):
        with tempfile.TemporaryDirectory() as origem:
            with tempfile.TemporaryDirectory() as destino_1:
                with tempfile.TemporaryDirectory() as destino_2:
                    arquivo = Path(origem) / "relatorio.txt"
                    arquivo.write_text("backup", encoding="utf-8")
                    perfil = {
                        "id": "perfil_001",
                        "origens": [origem],
                        "destinos": [destino_1, destino_2],
                        "operacao": "copiar",
                        "restricoes": {
                            "extensoes_permitidas": [".txt"],
                            "nome_contem": "",
                            "tamanho_min": 0,
                            "tamanho_max": None,
                            "data_modificacao_min": None,
                            "data_modificacao_max": None,
                        },
                    }

                    codigo, resultado = backup_engine.executar_backup(perfil)

                    self.assertEqual(codigo, OK)
                    self.assertEqual(resultado["status"], "sucesso")
                    self.assertEqual(resultado["arquivos_processados"], 1)
                    self.assertEqual(resultado["arquivos_copiados"], 2)
                    self.assertTrue(arquivo.exists())
                    self.assertEqual((Path(destino_1) / "relatorio.txt").read_text(encoding="utf-8"), "backup")
                    self.assertEqual((Path(destino_2) / "relatorio.txt").read_text(encoding="utf-8"), "backup")

    def test_executar_backup_move_para_multiplos_destinos(self):
        with tempfile.TemporaryDirectory() as origem:
            with tempfile.TemporaryDirectory() as destino_1:
                with tempfile.TemporaryDirectory() as destino_2:
                    arquivo = Path(origem) / "relatorio.txt"
                    arquivo.write_text("mover", encoding="utf-8")
                    perfil = {
                        "id": "perfil_001",
                        "origens": [origem],
                        "destinos": [destino_1, destino_2],
                        "operacao": "mover",
                        "restricoes": {
                            "extensoes_permitidas": [],
                            "nome_contem": "",
                            "tamanho_min": 0,
                            "tamanho_max": None,
                            "data_modificacao_min": None,
                            "data_modificacao_max": None,
                        },
                    }

                    codigo, resultado = backup_engine.executar_backup(perfil)

                    self.assertEqual(codigo, OK)
                    self.assertEqual(resultado["status"], "sucesso")
                    self.assertEqual(resultado["arquivos_processados"], 1)
                    self.assertEqual(resultado["arquivos_movidos"], 1)
                    self.assertFalse(arquivo.exists())
                    self.assertEqual((Path(destino_1) / "relatorio.txt").read_text(encoding="utf-8"), "mover")
                    self.assertEqual((Path(destino_2) / "relatorio.txt").read_text(encoding="utf-8"), "mover")

    def test_executar_backup_retorna_sem_arquivos_quando_filtro_rejeita_todos(self):
        with tempfile.TemporaryDirectory() as origem:
            with tempfile.TemporaryDirectory() as destino:
                arquivo = Path(origem) / "nota.txt"
                arquivo.write_text("texto", encoding="utf-8")
                perfil = {
                    "id": "perfil_001",
                    "origens": [origem],
                    "destinos": [destino],
                    "operacao": "copiar",
                    "restricoes": {
                        "extensoes_permitidas": [".py"],
                        "nome_contem": "",
                        "tamanho_min": 0,
                        "tamanho_max": None,
                        "data_modificacao_min": None,
                        "data_modificacao_max": None,
                    },
                }

                codigo, resultado = backup_engine.executar_backup(perfil)

                self.assertEqual(codigo, ERRO_BACKUP_SEM_ARQUIVOS)
                self.assertEqual(resultado["status"], "sem_arquivos")
                self.assertFalse((Path(destino) / "nota.txt").exists())


if __name__ == "__main__":
    unittest.main()
