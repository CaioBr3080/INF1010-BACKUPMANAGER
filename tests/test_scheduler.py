import unittest
import tempfile
import time
from datetime import datetime, timedelta
from pathlib import Path

from backupmanager import scheduler
from backupmanager.return_codes import OK


class TestScheduler(unittest.TestCase):
    def tearDown(self):
        scheduler.parar_monitoramento()
        scheduler.INTERVALO_VERIFICACAO_SEGUNDOS = 1

    def test_comparar_estado_arquivos(self):
        self.assertTrue(scheduler.comparar_estado_arquivos({"a": 1}, {"a": 2}))
        self.assertFalse(scheduler.comparar_estado_arquivos({"a": 1}, {"a": 1}))

    def test_deve_executar_por_intervalo_sem_ultima_execucao(self):
        perfil = {
            "ativo": True,
            "agendamento": {
                "tipo": "intervalo",
                "intervalo_minutos": 10,
                "ultima_execucao": None,
            },
        }

        self.assertTrue(scheduler.deve_executar_por_intervalo(perfil))

    def test_deve_executar_por_intervalo_respeita_intervalo(self):
        recente = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        antiga = (datetime.now() - timedelta(minutes=20)).strftime("%Y-%m-%d %H:%M:%S")
        perfil = {
            "ativo": True,
            "agendamento": {
                "tipo": "intervalo",
                "intervalo_minutos": 10,
                "ultima_execucao": recente,
            },
        }

        self.assertFalse(scheduler.deve_executar_por_intervalo(perfil))
        perfil["agendamento"]["ultima_execucao"] = antiga
        self.assertTrue(scheduler.deve_executar_por_intervalo(perfil))

    def test_deve_executar_por_intervalo_ignora_perfil_inativo(self):
        perfil = {
            "ativo": False,
            "agendamento": {
                "tipo": "intervalo",
                "intervalo_minutos": 10,
                "ultima_execucao": None,
            },
        }

        self.assertFalse(scheduler.deve_executar_por_intervalo(perfil))

    def test_obter_estado_atual_arquivos(self):
        with tempfile.TemporaryDirectory() as pasta:
            arquivo = Path(pasta) / "arquivo.txt"
            arquivo.write_text("conteudo", encoding="utf-8")
            perfil = {"origens": [pasta]}

            estado = scheduler.obter_estado_atual_arquivos(perfil)

            self.assertIn(str(arquivo), estado)
            self.assertEqual(estado[str(arquivo)]["tamanho"], len("conteudo"))

    def test_deve_executar_por_alteracao_detecta_mudanca(self):
        with tempfile.TemporaryDirectory() as pasta:
            arquivo = Path(pasta) / "arquivo.txt"
            arquivo.write_text("a", encoding="utf-8")
            perfil = {
                "ativo": True,
                "origens": [pasta],
                "estado_arquivos": {},
                "agendamento": {
                    "tipo": "alteracao",
                    "executar_ao_detectar_mudanca": True,
                },
            }

            self.assertTrue(scheduler.deve_executar_por_alteracao(perfil))
            scheduler.atualizar_estado_arquivos(perfil)
            self.assertFalse(scheduler.deve_executar_por_alteracao(perfil))

    def test_atualizar_estado_arquivos(self):
        with tempfile.TemporaryDirectory() as pasta:
            arquivo = Path(pasta) / "arquivo.txt"
            arquivo.write_text("a", encoding="utf-8")
            perfil = {"origens": [pasta]}

            codigo = scheduler.atualizar_estado_arquivos(perfil)

            self.assertEqual(codigo, OK)
            self.assertIn(str(arquivo), perfil["estado_arquivos"])

    def test_iniciar_monitoramento_chama_callback(self):
        chamadas = []
        perfil = {
            "id": "perfil_001",
            "ativo": True,
            "origens": [],
            "estado_arquivos": {},
            "agendamento": {
                "tipo": "intervalo",
                "intervalo_minutos": 1,
                "ultima_execucao": None,
            },
        }
        scheduler.INTERVALO_VERIFICACAO_SEGUNDOS = 0.01

        codigo = scheduler.iniciar_monitoramento([perfil], chamadas.append)
        time.sleep(0.05)
        scheduler.parar_monitoramento()

        self.assertEqual(codigo, OK)
        self.assertIn("perfil_001", chamadas)

    def test_parar_monitoramento(self):
        codigo = scheduler.parar_monitoramento()

        self.assertEqual(codigo, OK)


if __name__ == "__main__":
    unittest.main()
