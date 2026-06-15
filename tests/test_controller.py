import unittest
import tempfile
from pathlib import Path
from unittest.mock import patch

from backupmanager import controller
from backupmanager.return_codes import (
    OK,
    ERRO_BACKUP_SEM_ARQUIVOS,
    ERRO_DADOS_INVALIDOS,
    ERRO_DESTINO_INVALIDO,
    ERRO_OPERACAO_INVALIDA,
    ERRO_ORIGEM_INVALIDA,
    ERRO_PERFIL_INATIVO,
)


def resetar_estado():
    """Reinicia o estado global usado pelo controller nos testes."""
    controller.ESTADO["perfis"] = []
    controller.ESTADO["historico"] = []
    controller.ESTADO["config"] = {}
    controller.ESTADO["alterado"] = False


class TestControllerPersistenciaMemoria(unittest.TestCase):
    def setUp(self):
        resetar_estado()

    def test_criar_perfil_altera_apenas_memoria(self):
        codigo, perfil = controller.criar_novo_perfil("Backup Teste")

        self.assertEqual(codigo, OK)
        self.assertIsNotNone(perfil)
        self.assertEqual(controller.ESTADO["perfis"], [perfil])
        self.assertTrue(controller.ESTADO["alterado"])

    def test_criar_perfil_nao_salva_json_imediatamente(self):
        with patch("backupmanager.controller.storage.salvar_perfis") as mock_salvar:
            codigo, perfil = controller.criar_novo_perfil("Backup Teste")

        self.assertEqual(codigo, OK)
        self.assertIsNotNone(perfil)
        mock_salvar.assert_not_called()

    def test_finalizar_aplicacao_salva_json_quando_estado_foi_alterado(self):
        controller.ESTADO["perfis"] = [{"id": "perfil_001", "nome": "Teste"}]
        controller.ESTADO["historico"] = [{"id": "hist_001"}]
        controller.ESTADO["config"] = {"tema": "padrao"}
        controller.ESTADO["alterado"] = True

        with patch("backupmanager.controller.storage.salvar_perfis", return_value=OK) as mock_perfis:
            with patch("backupmanager.controller.storage.salvar_historico", return_value=OK) as mock_historico:
                with patch("backupmanager.controller.storage.salvar_configuracoes", return_value=OK) as mock_config:
                    codigo = controller.finalizar_aplicacao()

        self.assertEqual(codigo, OK)
        mock_perfis.assert_called_once_with(controller.ESTADO["perfis"])
        mock_historico.assert_called_once_with(controller.ESTADO["historico"])
        mock_config.assert_called_once_with(controller.ESTADO["config"])
        self.assertFalse(controller.ESTADO["alterado"])

    def test_finalizar_aplicacao_sem_alteracao_nao_salva_json(self):
        controller.ESTADO["alterado"] = False

        with patch("backupmanager.controller.storage.salvar_perfis") as mock_perfis:
            with patch("backupmanager.controller.storage.salvar_historico") as mock_historico:
                with patch("backupmanager.controller.storage.salvar_configuracoes") as mock_config:
                    codigo = controller.finalizar_aplicacao()

        self.assertEqual(codigo, OK)
        mock_perfis.assert_not_called()
        mock_historico.assert_not_called()
        mock_config.assert_not_called()

    def test_inicializar_aplicacao_carrega_estado_em_memoria(self):
        perfis = [{"id": "perfil_001", "nome": "Backup"}]
        historico = [{"id": "hist_001", "perfil_id": "perfil_001"}]
        config = {"versao": 1}
        controller.ESTADO["alterado"] = True

        with patch("backupmanager.controller.storage.criar_arquivos_padrao", return_value=OK):
            with patch("backupmanager.controller.storage.carregar_perfis", return_value=(OK, perfis)):
                with patch("backupmanager.controller.storage.carregar_historico", return_value=(OK, historico)):
                    with patch("backupmanager.controller.storage.carregar_configuracoes", return_value=(OK, config)):
                        codigo = controller.inicializar_aplicacao()

        self.assertEqual(codigo, OK)
        self.assertEqual(controller.ESTADO["perfis"], perfis)
        self.assertEqual(controller.ESTADO["historico"], historico)
        self.assertEqual(controller.ESTADO["config"], config)
        self.assertFalse(controller.ESTADO["alterado"])

    def test_executar_backup_registra_historico_sem_salvar_json_imediatamente(self):
        codigo, perfil = controller.criar_novo_perfil("Backup Teste")
        self.assertEqual(codigo, OK)
        controller.ESTADO["alterado"] = False

        with patch("backupmanager.controller.storage.salvar_historico") as mock_salvar:
            codigo_backup, resultado = controller.executar_backup_do_perfil(perfil["id"])

        self.assertEqual(codigo_backup, ERRO_ORIGEM_INVALIDA)
        self.assertEqual(resultado["perfil_id"], perfil["id"])
        self.assertEqual(len(controller.ESTADO["historico"]), 1)
        self.assertTrue(controller.ESTADO["alterado"])
        mock_salvar.assert_not_called()

    def test_salvar_perfil_editado_aplica_dados_em_memoria(self):
        codigo, perfil = controller.criar_novo_perfil("Backup Teste")
        self.assertEqual(codigo, OK)
        controller.ESTADO["alterado"] = False

        perfil_editado = {
            "id": perfil["id"],
            "nome": "Backup Editado",
            "origens": ["C:/origem"],
            "destinos": ["D:/destino"],
            "operacao": "mover",
            "restricoes": {"extensoes_permitidas": [".py"]},
            "agendamento": {"tipo": "manual"},
            "estado_arquivos": {"arquivo.txt": 10},
            "ativo": False,
        }

        with patch("backupmanager.controller.storage.salvar_perfis") as mock_salvar:
            codigo = controller.salvar_perfil_editado(perfil_editado)

        self.assertEqual(codigo, OK)
        self.assertEqual(perfil["nome"], "Backup Editado")
        self.assertEqual(perfil["origens"], ["C:/origem"])
        self.assertEqual(perfil["destinos"], ["D:/destino"])
        self.assertEqual(perfil["operacao"], "mover")
        self.assertEqual(perfil["restricoes"], {"extensoes_permitidas": [".py"]})
        self.assertEqual(perfil["agendamento"], {"tipo": "manual"})
        self.assertEqual(perfil["estado_arquivos"], {"arquivo.txt": 10})
        self.assertFalse(perfil["ativo"])
        self.assertTrue(controller.ESTADO["alterado"])
        mock_salvar.assert_not_called()

    def test_salvar_perfil_editado_rejeita_dados_invalidos(self):
        codigo, perfil = controller.criar_novo_perfil("Backup Teste")
        self.assertEqual(codigo, OK)
        controller.ESTADO["alterado"] = False

        codigo = controller.salvar_perfil_editado({
            "id": perfil["id"],
            "origens": "C:/origem",
        })

        self.assertEqual(codigo, ERRO_DADOS_INVALIDOS)
        self.assertEqual(perfil["origens"], [])
        self.assertFalse(controller.ESTADO["alterado"])

    def test_definir_operacao_do_perfil_altera_memoria(self):
        codigo, perfil = controller.criar_novo_perfil("Backup Teste")
        self.assertEqual(codigo, OK)
        controller.ESTADO["alterado"] = False

        with patch("backupmanager.controller.storage.salvar_perfis") as mock_salvar:
            codigo = controller.definir_operacao_do_perfil(perfil["id"], "mover")

        self.assertEqual(codigo, OK)
        self.assertEqual(perfil["operacao"], "mover")
        self.assertTrue(controller.ESTADO["alterado"])
        mock_salvar.assert_not_called()

    def test_definir_operacao_invalida_nao_marca_alterado(self):
        codigo, perfil = controller.criar_novo_perfil("Backup Teste")
        self.assertEqual(codigo, OK)
        controller.ESTADO["alterado"] = False

        codigo = controller.definir_operacao_do_perfil(perfil["id"], "compactar")

        self.assertEqual(codigo, ERRO_OPERACAO_INVALIDA)
        self.assertEqual(perfil["operacao"], "copiar")
        self.assertFalse(controller.ESTADO["alterado"])

    def test_ativar_e_desativar_perfil_alteram_memoria(self):
        codigo, perfil = controller.criar_novo_perfil("Backup Teste")
        self.assertEqual(codigo, OK)

        controller.ESTADO["alterado"] = False
        codigo = controller.desativar_perfil_por_id(perfil["id"])
        self.assertEqual(codigo, OK)
        self.assertFalse(perfil["ativo"])
        self.assertTrue(controller.ESTADO["alterado"])

        controller.ESTADO["alterado"] = False
        codigo = controller.ativar_perfil_por_id(perfil["id"])
        self.assertEqual(codigo, OK)
        self.assertTrue(perfil["ativo"])
        self.assertTrue(controller.ESTADO["alterado"])

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
                "origens": [pasta],
                "restricoes": {
                    "extensoes_permitidas": [".py"],
                    "nome_contem": "",
                    "tamanho_min": 0,
                    "tamanho_max": None,
                    "data_modificacao_min": None,
                    "data_modificacao_max": None,
                },
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

    def test_executar_backup_bloqueia_perfil_inativo_sem_registrar_historico(self):
        codigo, perfil = controller.criar_novo_perfil("Backup Teste")
        self.assertEqual(codigo, OK)
        codigo = controller.desativar_perfil_por_id(perfil["id"])
        self.assertEqual(codigo, OK)
        controller.ESTADO["historico"] = []
        controller.ESTADO["alterado"] = False

        codigo_backup, resultado = controller.executar_backup_do_perfil(perfil["id"])

        self.assertEqual(codigo_backup, ERRO_PERFIL_INATIVO)
        self.assertIsNone(resultado)
        self.assertEqual(controller.ESTADO["historico"], [])
        self.assertFalse(controller.ESTADO["alterado"])

    def test_adicionar_origem_valida_caminho(self):
        codigo, perfil = controller.criar_novo_perfil("Backup Teste")
        self.assertEqual(codigo, OK)
        controller.ESTADO["alterado"] = False

        with tempfile.TemporaryDirectory() as pasta:
            codigo = controller.adicionar_origem_ao_perfil(perfil["id"], pasta)

        self.assertEqual(codigo, OK)
        self.assertTrue(controller.ESTADO["alterado"])

        controller.ESTADO["alterado"] = False
        codigo = controller.adicionar_origem_ao_perfil(perfil["id"], "")

        self.assertEqual(codigo, ERRO_ORIGEM_INVALIDA)
        self.assertFalse(controller.ESTADO["alterado"])

    def test_adicionar_destino_valida_caminho(self):
        codigo, perfil = controller.criar_novo_perfil("Backup Teste")
        self.assertEqual(codigo, OK)
        controller.ESTADO["alterado"] = False

        with tempfile.TemporaryDirectory() as pasta:
            codigo = controller.adicionar_destino_ao_perfil(perfil["id"], pasta)

        self.assertEqual(codigo, OK)
        self.assertTrue(controller.ESTADO["alterado"])

        controller.ESTADO["alterado"] = False
        codigo = controller.adicionar_destino_ao_perfil(perfil["id"], "")

        self.assertEqual(codigo, ERRO_DESTINO_INVALIDO)
        self.assertFalse(controller.ESTADO["alterado"])

    def test_limpar_historico_do_perfil_altera_apenas_memoria(self):
        controller.ESTADO["historico"] = [
            {"id": "hist_1", "perfil_id": "perfil_1"},
            {"id": "hist_2", "perfil_id": "perfil_2"},
        ]
        controller.ESTADO["alterado"] = False

        codigo = controller.limpar_historico_do_perfil("perfil_1")

        self.assertEqual(codigo, OK)
        self.assertEqual(controller.ESTADO["historico"], [{"id": "hist_2", "perfil_id": "perfil_2"}])
        self.assertTrue(controller.ESTADO["alterado"])

    def test_limpar_todo_historico_altera_apenas_memoria(self):
        controller.ESTADO["historico"] = [{"id": "hist_1", "perfil_id": "perfil_1"}]
        controller.ESTADO["alterado"] = False

        codigo = controller.limpar_todo_historico()

        self.assertEqual(codigo, OK)
        self.assertEqual(controller.ESTADO["historico"], [])
        self.assertTrue(controller.ESTADO["alterado"])

    def test_configuracoes_gerais_alteram_apenas_memoria(self):
        controller.ESTADO["config"] = {"tema": "escuro"}
        controller.ESTADO["alterado"] = False

        codigo, config = controller.obter_configuracoes()
        self.assertEqual(codigo, OK)
        self.assertEqual(config, {"tema": "escuro"})

        codigo = controller.salvar_configuracoes({"tema": "claro"})

        self.assertEqual(codigo, OK)
        self.assertEqual(controller.ESTADO["config"], {"tema": "claro"})
        self.assertTrue(controller.ESTADO["alterado"])

    def test_salvar_configuracoes_rejeita_dados_invalidos(self):
        controller.ESTADO["alterado"] = False

        codigo = controller.salvar_configuracoes(["tema"])

        self.assertEqual(codigo, ERRO_DADOS_INVALIDOS)
        self.assertFalse(controller.ESTADO["alterado"])

    def test_obter_extensoes_disponiveis_une_padrao_e_config(self):
        controller.ESTADO["config"] = {"extensoes_disponiveis": ["log", ".TXT"]}

        codigo, extensoes = controller.obter_extensoes_disponiveis()

        self.assertEqual(codigo, OK)
        self.assertIn(".txt", extensoes)
        self.assertIn(".log", extensoes)
        self.assertEqual(extensoes.count(".txt"), 1)

    def test_adicionar_extensao_disponivel_normaliza_e_altera_memoria(self):
        controller.ESTADO["config"] = {}
        controller.ESTADO["alterado"] = False

        codigo = controller.adicionar_extensao_disponivel("LOG")

        self.assertEqual(codigo, OK)
        self.assertEqual(controller.ESTADO["config"]["extensoes_disponiveis"], [".log"])
        self.assertTrue(controller.ESTADO["alterado"])

    def test_adicionar_extensao_disponivel_rejeita_invalida(self):
        controller.ESTADO["alterado"] = False

        codigo = controller.adicionar_extensao_disponivel("")

        self.assertEqual(codigo, ERRO_DADOS_INVALIDOS)
        self.assertFalse(controller.ESTADO["alterado"])


if __name__ == "__main__":
    unittest.main()
