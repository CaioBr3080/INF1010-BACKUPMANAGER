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
        scheduler._INTERVALO_VERIFICACAO_SEGUNDOS = 1

    def test_comparar_estado_arquivos(self):
        self.assertTrue(scheduler._comparar_estado_arquivos({"a": 1}, {"a": 2}))
        self.assertFalse(scheduler._comparar_estado_arquivos({"a": 1}, {"a": 1}))

    def test_deve_executar_por_intervalo_sem_ultima_execucao(self):
        perfil = {
            "ativo": True,
            "agendamento": {
                "tipo": "intervalo",
                "intervalo_minutos": 10,
                "ultima_execucao": None,
            },
        }

        self.assertTrue(scheduler._deve_executar_por_intervalo(perfil))

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

        self.assertFalse(scheduler._deve_executar_por_intervalo(perfil))
        perfil["agendamento"]["ultima_execucao"] = antiga
        self.assertTrue(scheduler._deve_executar_por_intervalo(perfil))

    def test_deve_executar_por_intervalo_em_segundos(self):
        recente = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        antiga = (datetime.now() - timedelta(seconds=20)).strftime("%Y-%m-%d %H:%M:%S")
        perfil = {
            "ativo": True,
            "agendamento": {
                "tipo": "intervalo",
                "intervalo_valor": 10,
                "intervalo_unidade": "segundos",
                "ultima_execucao": recente,
            },
        }

        self.assertFalse(scheduler._deve_executar_por_intervalo(perfil))
        perfil["agendamento"]["ultima_execucao"] = antiga
        self.assertTrue(scheduler._deve_executar_por_intervalo(perfil))

    def test_obter_intervalo_em_segundos_converte_horas(self):
        agendamento = {
            "intervalo_valor": 2,
            "intervalo_unidade": "horas",
        }

        self.assertEqual(scheduler._obter_intervalo_em_segundos(agendamento), 7200)

    def test_deve_executar_por_intervalo_ignora_perfil_inativo(self):
        perfil = {
            "ativo": False,
            "agendamento": {
                "tipo": "intervalo",
                "intervalo_minutos": 10,
                "ultima_execucao": None,
            },
        }

        self.assertFalse(scheduler._deve_executar_por_intervalo(perfil))

    def test_obter_estado_atual_arquivos(self):
        with tempfile.TemporaryDirectory() as pasta:
            arquivo = Path(pasta) / "arquivo.txt"
            arquivo.write_text("conteudo", encoding="utf-8")
            perfil = {"origens": [pasta]}

            estado = scheduler._obter_estado_atual_arquivos(perfil)

            self.assertIn(str(arquivo), estado)
            self.assertEqual(estado[str(arquivo)]["tamanho"], len("conteudo"))

    def test_obter_estado_atual_arquivos_usa_origens_configuradas_ativas(self):
        with tempfile.TemporaryDirectory() as origem_ativa:
            with tempfile.TemporaryDirectory() as origem_inativa:
                arquivo_ativo = Path(origem_ativa) / "ativo.txt"
                arquivo_inativo = Path(origem_inativa) / "inativo.txt"
                arquivo_ativo.write_text("ativo", encoding="utf-8")
                arquivo_inativo.write_text("inativo", encoding="utf-8")
                perfil = {
                    "origens_configuradas": [
                        {"caminho": origem_ativa, "ativo": True},
                        {"caminho": origem_inativa, "ativo": False},
                    ]
                }

                estado = scheduler._obter_estado_atual_arquivos(perfil)

                self.assertIn(str(arquivo_ativo), estado)
                self.assertNotIn(str(arquivo_inativo), estado)

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

            self.assertTrue(scheduler._deve_executar_por_alteracao(perfil))
            scheduler.atualizar_estado_arquivos(perfil)
            self.assertFalse(scheduler._deve_executar_por_alteracao(perfil))

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
        scheduler._INTERVALO_VERIFICACAO_SEGUNDOS = 0.01

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

