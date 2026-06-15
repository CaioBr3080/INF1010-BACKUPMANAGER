import unittest

from backupmanager import history_manager
from backupmanager.return_codes import OK


class TestHistoryManager(unittest.TestCase):
    def test_criar_registro_historico_padroniza_status_e_erros(self):
        resultado = {
            "status": "sucesso",
            "arquivos_processados": 2,
            "arquivos_copiados": 4,
            "arquivos_movidos": 0,
            "erros": None,
        }

        registro = history_manager.criar_registro_historico("perfil_001", resultado)

        self.assertEqual(registro["perfil_id"], "perfil_001")
        self.assertEqual(registro["status"], "sucesso")
        self.assertEqual(registro["erros"], [])

    def test_criar_registro_historico_converte_status_desconhecido_para_erro(self):
        registro = history_manager.criar_registro_historico("perfil_001", {"status": "desconhecido", "erros": "falha"})

        self.assertEqual(registro["status"], "erro")
        self.assertEqual(registro["erros"], ["falha"])

    def test_registrar_backup_adiciona_historico(self):
        historico = []

        codigo = history_manager.registrar_backup(historico, "perfil_001", {"status": "sem_arquivos"})

        self.assertEqual(codigo, OK)
        self.assertEqual(len(historico), 1)
        self.assertEqual(historico[0]["status"], "sem_arquivos")

    def test_limpar_historico_perfil_remove_apenas_perfil_alvo(self):
        historico = [
            {"id": "hist_1", "perfil_id": "perfil_001"},
            {"id": "hist_2", "perfil_id": "perfil_002"},
        ]

        codigo = history_manager.limpar_historico_perfil(historico, "perfil_001")

        self.assertEqual(codigo, OK)
        self.assertEqual(historico, [{"id": "hist_2", "perfil_id": "perfil_002"}])

    def test_limpar_todo_historico_remove_tudo(self):
        historico = [{"id": "hist_1", "perfil_id": "perfil_001"}]

        codigo = history_manager.limpar_todo_historico(historico)

        self.assertEqual(codigo, OK)
        self.assertEqual(historico, [])

    def test_gerar_resumo_historico_perfil(self):
        historico = [
            {
                "perfil_id": "perfil_001",
                "arquivos_processados": 2,
                "erros": [{"codigo": 10}],
            },
            {
                "perfil_id": "perfil_001",
                "arquivos_processados": 3,
                "erros": [],
            },
            {
                "perfil_id": "perfil_002",
                "arquivos_processados": 7,
                "erros": [{"codigo": 11}],
            },
        ]

        resumo = history_manager.gerar_resumo_historico_perfil(historico, "perfil_001")

        self.assertEqual(resumo["total_execucoes"], 2)
        self.assertEqual(resumo["total_arquivos_processados"], 5)
        self.assertEqual(resumo["total_erros"], 1)


if __name__ == "__main__":
    unittest.main()
