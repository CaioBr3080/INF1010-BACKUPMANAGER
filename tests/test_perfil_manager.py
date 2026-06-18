import unittest

from backupmanager import perfil_manager
from backupmanager.return_codes import OK, ERRO_NOME_INVALIDO, ERRO_PERFIL_NAO_ENCONTRADO


class TestPerfilManager(unittest.TestCase):
    def test_criar_perfil_valido(self):
        codigo, perfil = perfil_manager.criar_perfil("Backup Faculdade")

        self.assertEqual(codigo, OK)
        self.assertEqual(perfil["nome"], "Backup Faculdade")
        self.assertEqual(perfil["origens_configuradas"], [])
        self.assertEqual(perfil["agendamento"]["intervalo_unidade"], "minutos")
        self.assertIsNone(perfil["agendamento"]["intervalo_valor"])
        self.assertNotIn("origens", perfil)
        self.assertNotIn("destinos", perfil)
        self.assertNotIn("operacao", perfil)
        self.assertNotIn("restricoes", perfil)

    def test_criar_perfil_nome_vazio(self):
        codigo, perfil = perfil_manager.criar_perfil("")

        self.assertEqual(codigo, ERRO_NOME_INVALIDO)
        self.assertIsNone(perfil)

    def test_consultar_perfil_existente(self):
        _, perfil = perfil_manager.criar_perfil("Projetos")
        codigo, encontrado = perfil_manager.consultar_perfil([perfil], perfil["id"])

        self.assertEqual(codigo, OK)
        self.assertEqual(encontrado["id"], perfil["id"])

    def test_consultar_perfil_inexistente(self):
        codigo, perfil = perfil_manager.consultar_perfil([], "perfil_x")

        self.assertEqual(codigo, ERRO_PERFIL_NAO_ENCONTRADO)
        self.assertIsNone(perfil)

    def test_criar_origem_tipo_e_destino_configurados(self):
        origem = perfil_manager.criar_origem_configurada("C:/Documentos")
        destino = perfil_manager.criar_destino_tipo("D:/Backup", "recortar")
        tipo = perfil_manager.criar_tipo_arquivo("PDFs", {"extensoes_permitidas": [".pdf"]}, [destino])

        self.assertEqual(origem["caminho"], "C:/Documentos")
        self.assertEqual(tipo["nome"], "PDFs")
        self.assertEqual(tipo["destinos"][0]["operacao"], "recortar")

    def test_migrar_perfil_legado_para_modelo_atual(self):
        perfil = {
            "id": "perfil_001",
            "nome": "Legado",
            "origens": ["C:/Origem"],
            "destinos": ["D:/Backup"],
            "operacao": "copiar",
            "restricoes": {"extensoes_permitidas": [".pdf"]},
        }

        codigo, migrado = perfil_manager.migrar_perfil_para_modelo_atual(perfil)

        self.assertEqual(codigo, OK)
        self.assertTrue(migrado)
        self.assertNotIn("origens", perfil)
        self.assertNotIn("destinos", perfil)
        self.assertNotIn("operacao", perfil)
        self.assertNotIn("restricoes", perfil)
        origem = perfil["origens_configuradas"][0]
        tipo = origem["tipos_arquivo"][0]
        destino = tipo["destinos"][0]
        self.assertEqual(origem["caminho"], "C:/Origem")
        self.assertEqual(tipo["nome"], "Todos os arquivos")
        self.assertEqual(tipo["restricoes"]["extensoes_permitidas"], [".pdf"])
        self.assertEqual(destino["caminho"], "D:/Backup")
        self.assertEqual(destino["operacao"], "copiar")
        self.assertEqual(perfil["agendamento"]["tipo"], "manual")
        self.assertEqual(perfil["estado_arquivos"], {})
        self.assertTrue(perfil["ativo"])

    def test_migrar_perfil_atual_nao_altera(self):
        perfil = {
            "id": "perfil_001",
            "nome": "Atual",
            "origens_configuradas": [
                perfil_manager.criar_origem_configurada("C:/Origem")
            ],
            "agendamento": perfil_manager.criar_agendamento_padrao(),
            "estado_arquivos": {},
            "ativo": True,
        }

        codigo, migrado = perfil_manager.migrar_perfil_para_modelo_atual(perfil)

        self.assertEqual(codigo, OK)
        self.assertFalse(migrado)

    def test_migrar_lista_de_perfis(self):
        perfis = [
            {
                "id": "perfil_001",
                "nome": "Legado",
                "origens": ["C:/Origem"],
                "destinos": ["D:/Backup"],
            }
        ]

        codigo, migrado = perfil_manager.migrar_perfis_para_modelo_atual(perfis)

        self.assertEqual(codigo, OK)
        self.assertTrue(migrado)
        self.assertIn("origens_configuradas", perfis[0])


if __name__ == "__main__":
    unittest.main()
