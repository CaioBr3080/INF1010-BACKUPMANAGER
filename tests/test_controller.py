import unittest
import tempfile
from pathlib import Path
from unittest.mock import patch

from backupmanager import controller
from backupmanager.return_codes import (
    OK,
    ERRO_BACKUP_SEM_ARQUIVOS,
    ERRO_DADOS_INVALIDOS,
    ERRO_ORIGEM_INVALIDA,
    ERRO_PERFIL_INATIVO,
)


def resetar_estado():
    """Reinicia o estado global usado pelo controller nos testes."""
    controller._ESTADO["perfis"] = []
    controller._ESTADO["config"] = {}
    controller._ESTADO["alterado"] = False


class TestControllerPersistenciaMemoria(unittest.TestCase):
    def setUp(self):
        resetar_estado()

    def test_criar_perfil_altera_apenas_memoria(self):
        codigo, perfil = controller.criar_novo_perfil("Backup Teste")

        self.assertEqual(codigo, OK)
        self.assertIsNotNone(perfil)
        self.assertEqual(controller._ESTADO["perfis"], [perfil])
        self.assertTrue(controller._ESTADO["alterado"])

    def test_criar_perfil_nao_salva_json_imediatamente(self):
        with patch("backupmanager.controller.storage.salvar_perfis") as mock_salvar:
            codigo, perfil = controller.criar_novo_perfil("Backup Teste")

        self.assertEqual(codigo, OK)
        self.assertIsNotNone(perfil)
        mock_salvar.assert_not_called()

    def test_finalizar_aplicacao_salva_json_quando_estado_foi_alterado(self):
        controller._ESTADO["perfis"] = [{"id": "perfil_001", "nome": "Teste"}]
        controller._ESTADO["config"] = {"tema": "padrao"}
        controller._ESTADO["alterado"] = True

        with patch("backupmanager.controller.storage.salvar_perfis", return_value=OK) as mock_perfis:
            with patch("backupmanager.controller.storage.salvar_configuracoes", return_value=OK) as mock_config:
                codigo = controller.finalizar_aplicacao()

        self.assertEqual(codigo, OK)
        mock_perfis.assert_called_once_with(controller._ESTADO["perfis"])
        mock_config.assert_called_once_with(controller._ESTADO["config"])
        self.assertFalse(controller._ESTADO["alterado"])

    def test_finalizar_aplicacao_sem_alteracao_nao_salva_json(self):
        controller._ESTADO["alterado"] = False

        with patch("backupmanager.controller.storage.salvar_perfis") as mock_perfis:
            with patch("backupmanager.controller.storage.salvar_configuracoes") as mock_config:
                codigo = controller.finalizar_aplicacao()

        self.assertEqual(codigo, OK)
        mock_perfis.assert_not_called()
        mock_config.assert_not_called()

    def test_inicializar_aplicacao_carrega_estado_em_memoria(self):
        perfis = [
            {
                "id": "perfil_001",
                "nome": "Backup",
                "origens_configuradas": [],
                "ativo": True,
            }
        ]
        config = {"versao": 1}
        controller._ESTADO["alterado"] = True

        with patch("backupmanager.controller.storage.criar_arquivos_padrao", return_value=OK):
            with patch("backupmanager.controller.storage.carregar_perfis", return_value=(OK, perfis)):
                with patch("backupmanager.controller.storage.carregar_configuracoes", return_value=(OK, config)):
                    codigo = controller.inicializar_aplicacao()

        self.assertEqual(codigo, OK)
        self.assertEqual(controller._ESTADO["perfis"], perfis)
        self.assertEqual(controller._ESTADO["config"], config)
        self.assertFalse(controller._ESTADO["alterado"])

    def test_executar_backup_nao_altera_estado_quando_falha_validacao(self):
        codigo, perfil = controller.criar_novo_perfil("Backup Teste")
        self.assertEqual(codigo, OK)
        controller._ESTADO["alterado"] = False

        codigo_backup, resultado = controller.executar_backup_do_perfil(perfil["id"])

        self.assertEqual(codigo_backup, ERRO_ORIGEM_INVALIDA)
        self.assertEqual(resultado["perfil_id"], perfil["id"])
        self.assertFalse(controller._ESTADO["alterado"])

    def test_salvar_perfil_editado_aplica_dados_em_memoria(self):
        codigo, perfil = controller.criar_novo_perfil("Backup Teste")
        self.assertEqual(codigo, OK)
        controller._ESTADO["alterado"] = False

        origens_configuradas = [
            {
                "id": "origem_001",
                "caminho": "C:/origem",
                "tipos_arquivo": [],
            }
        ]
        perfil_editado = {
            "id": perfil["id"],
            "nome": "Backup Editado",
            "origens_configuradas": origens_configuradas,
            "ativo": False,
        }

        with patch("backupmanager.controller.storage.salvar_perfis") as mock_salvar:
            codigo = controller.salvar_perfil_editado(perfil_editado)

        self.assertEqual(codigo, OK)
        self.assertEqual(perfil["nome"], "Backup Editado")
        self.assertEqual(perfil["origens_configuradas"], origens_configuradas)
        self.assertEqual(set(perfil.keys()), {"id", "nome", "origens_configuradas", "ativo"})
        self.assertFalse(perfil["ativo"])
        self.assertTrue(controller._ESTADO["alterado"])
        mock_salvar.assert_not_called()

    def test_salvar_perfil_editado_aplica_origens_configuradas(self):
        codigo, perfil = controller.criar_novo_perfil("Backup Teste")
        self.assertEqual(codigo, OK)
        origens_configuradas = [
            {
                "id": "origem_001",
                "caminho": "C:/origem",
                "tipos_arquivo": [
                    {
                        "id": "tipo_pdf",
                        "nome": "PDFs",
                        "restricoes": {"extensoes_permitidas": [".pdf"]},
                        "destinos": [{"caminho": "D:/backup", "operacao": "copiar"}],
                    }
                ],
            }
        ]

        codigo = controller.salvar_perfil_editado({
            "id": perfil["id"],
            "origens_configuradas": origens_configuradas,
        })

        self.assertEqual(codigo, OK)
        self.assertEqual(perfil["origens_configuradas"], origens_configuradas)

    def test_salvar_perfil_editado_rejeita_dados_invalidos(self):
        codigo, perfil = controller.criar_novo_perfil("Backup Teste")
        self.assertEqual(codigo, OK)
        controller._ESTADO["alterado"] = False

        codigo = controller.salvar_perfil_editado({
            "id": perfil["id"],
            "origens_configuradas": "C:/origem",
        })

        self.assertEqual(codigo, ERRO_DADOS_INVALIDOS)
        self.assertEqual(perfil["origens_configuradas"], [])
        self.assertFalse(controller._ESTADO["alterado"])

    def test_ativar_e_desativar_perfil_alteram_memoria(self):
        codigo, perfil = controller.criar_novo_perfil("Backup Teste")
        self.assertEqual(codigo, OK)

        controller._ESTADO["alterado"] = False
        codigo = controller.desativar_perfil_por_id(perfil["id"])
        self.assertEqual(codigo, OK)
        self.assertFalse(perfil["ativo"])
        self.assertTrue(controller._ESTADO["alterado"])

        controller._ESTADO["alterado"] = False
        codigo = controller.ativar_perfil_por_id(perfil["id"])
        self.assertEqual(codigo, OK)
        self.assertTrue(perfil["ativo"])
        self.assertTrue(controller._ESTADO["alterado"])

    def test_obter_arquivos_do_perfil_lista_arquivos_com_status_incluido(self):
        with tempfile.TemporaryDirectory() as pasta:
            arquivo_py = Path(pasta) / "main.py"
            arquivo_txt = Path(pasta) / "nota.txt"
            arquivo_py.write_text("print('ok')", encoding="utf-8")
            arquivo_txt.write_text("texto", encoding="utf-8")

            codigo, perfil = controller.criar_novo_perfil("Backup Teste")
            self.assertEqual(codigo, OK)
            codigo = controller.salvar_perfil_editado({
                "id": perfil["id"],
                "nome": perfil["nome"],
                "origens_configuradas": [
                    {
                        "id": "origem_001",
                        "caminho": pasta,
                        "tipos_arquivo": [
                            {
                                "id": "tipo_py",
                                "nome": "Python",
                                "restricoes": {
                                    "extensoes_permitidas": [".py"],
                                    "regras_nome": [],
                                    "tamanho_min": 0,
                                    "tamanho_max": None,
                                    "data_modificacao_min": None,
                                    "data_modificacao_max": None,
                                },
                                "destinos": [{"caminho": "D:/backup", "operacao": "copiar"}],
                            }
                        ],
                    }
                ],
            })
            self.assertEqual(codigo, OK)

            codigo, arquivos = controller.obter_arquivos_do_perfil(perfil["id"])

            self.assertEqual(codigo, OK)
            arquivos_por_nome = {arquivo["nome"]: arquivo for arquivo in arquivos}
            self.assertTrue(arquivos_por_nome["main.py"]["incluido"])
            self.assertFalse(arquivos_por_nome["nota.txt"]["incluido"])

    def test_obter_arquivos_do_perfil_inexistente(self):
        codigo, arquivos = controller.obter_arquivos_do_perfil("perfil_inexistente")

        self.assertNotEqual(codigo, OK)
        self.assertIsNone(arquivos)

    def test_obter_arquivos_do_perfil_configurado_lista_tipos_incluidos(self):
        with tempfile.TemporaryDirectory() as pasta:
            arquivo_pdf = Path(pasta) / "relatorio.pdf"
            arquivo_txt = Path(pasta) / "nota.txt"
            arquivo_pdf.write_text("pdf", encoding="utf-8")
            arquivo_txt.write_text("txt", encoding="utf-8")
            codigo, perfil = controller.criar_novo_perfil("Backup Teste")
            self.assertEqual(codigo, OK)
            codigo = controller.salvar_perfil_editado({
                "id": perfil["id"],
                "origens_configuradas": [
                    {
                        "id": "origem_001",
                        "caminho": pasta,
                        "tipos_arquivo": [
                            {
                                "id": "tipo_pdf",
                                "nome": "PDFs",
                                "restricoes": {"extensoes_permitidas": [".pdf"]},
                                "destinos": [{"caminho": "D:/backup", "operacao": "copiar"}],
                            }
                        ],
                    }
                ],
            })
            self.assertEqual(codigo, OK)

            codigo, arquivos = controller.obter_arquivos_do_perfil(perfil["id"])

            self.assertEqual(codigo, OK)
            arquivos_por_nome = {arquivo["nome"]: arquivo for arquivo in arquivos}
            self.assertTrue(arquivos_por_nome["relatorio.pdf"]["incluido"])
            self.assertEqual(arquivos_por_nome["relatorio.pdf"]["tipos_incluidos"], ["PDFs"])
            self.assertFalse(arquivos_por_nome["nota.txt"]["incluido"])

    def test_executar_backup_bloqueia_perfil_inativo(self):
        codigo, perfil = controller.criar_novo_perfil("Backup Teste")
        self.assertEqual(codigo, OK)
        codigo = controller.desativar_perfil_por_id(perfil["id"])
        self.assertEqual(codigo, OK)
        controller._ESTADO["alterado"] = False

        codigo_backup, resultado = controller.executar_backup_do_perfil(perfil["id"])

        self.assertEqual(codigo_backup, ERRO_PERFIL_INATIVO)
        self.assertIsNone(resultado)
        self.assertFalse(controller._ESTADO["alterado"])

    def test_configuracoes_gerais_alteram_apenas_memoria(self):
        controller._ESTADO["config"] = {"tema": "escuro"}
        controller._ESTADO["alterado"] = False

        codigo, config = controller.obter_configuracoes()
        self.assertEqual(codigo, OK)
        self.assertEqual(config, {"tema": "escuro"})

        codigo = controller.salvar_configuracoes({"tema": "claro"})

        self.assertEqual(codigo, OK)
        self.assertEqual(controller._ESTADO["config"], {"tema": "claro"})
        self.assertTrue(controller._ESTADO["alterado"])

    def test_salvar_configuracoes_rejeita_dados_invalidos(self):
        controller._ESTADO["alterado"] = False

        codigo = controller.salvar_configuracoes(["tema"])

        self.assertEqual(codigo, ERRO_DADOS_INVALIDOS)
        self.assertFalse(controller._ESTADO["alterado"])

    def test_obter_extensoes_disponiveis_une_padrao_e_config(self):
        controller._ESTADO["config"] = {"extensoes_disponiveis": ["log", ".TXT"]}

        codigo, extensoes = controller.obter_extensoes_disponiveis()

        self.assertEqual(codigo, OK)
        self.assertIn(".txt", extensoes)
        self.assertIn(".log", extensoes)
        self.assertEqual(extensoes.count(".txt"), 1)

    def test_adicionar_extensao_disponivel_normaliza_e_altera_memoria(self):
        controller._ESTADO["config"] = {}
        controller._ESTADO["alterado"] = False

        codigo = controller.adicionar_extensao_disponivel("LOG")

        self.assertEqual(codigo, OK)
        self.assertEqual(controller._ESTADO["config"]["extensoes_disponiveis"], [".log"])
        self.assertTrue(controller._ESTADO["alterado"])

    def test_adicionar_extensao_disponivel_rejeita_invalida(self):
        controller._ESTADO["alterado"] = False

        codigo = controller.adicionar_extensao_disponivel("")

        self.assertEqual(codigo, ERRO_DADOS_INVALIDOS)
        self.assertFalse(controller._ESTADO["alterado"])


if __name__ == "__main__":
    unittest.main()

