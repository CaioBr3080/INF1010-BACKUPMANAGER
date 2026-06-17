import unittest

from backupmanager import perfil_manager
from backupmanager.return_codes import OK, ERRO_NOME_INVALIDO, ERRO_PERFIL_NAO_ENCONTRADO


class TestPerfilManager(unittest.TestCase):
    def test_criar_perfil_valido(self):
        codigo, perfil = perfil_manager.criar_perfil("Backup Faculdade")

        self.assertEqual(codigo, OK)
        self.assertEqual(perfil["nome"], "Backup Faculdade")
        self.assertEqual(perfil["operacao"], "copiar")
        self.assertEqual(perfil["origens_configuradas"], [])
        self.assertEqual(perfil["restricoes"]["regras_nome"], [])

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


if __name__ == "__main__":
    unittest.main()
