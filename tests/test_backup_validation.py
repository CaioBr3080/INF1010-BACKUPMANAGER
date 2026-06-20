import unittest

from backupmanager import backup_validation
from backupmanager.return_codes import (
    OK,
    ERRO_DADOS_INVALIDOS,
    ERRO_DESTINO_INVALIDO,
    ERRO_OPERACAO_INVALIDA,
    ERRO_ORIGEM_INVALIDA,
)


class TestBackupValidation(unittest.TestCase):
    def test_validar_perfil_rejeita_formato_antigo(self):
        perfil = {
            "origens": ["C:/Origem"],
            "destinos": ["D:/Backup"],
            "operacao": "copiar",
        }

        self.assertEqual(backup_validation.validar_perfil_para_backup(perfil), ERRO_ORIGEM_INVALIDA)

    def test_validar_perfil_rejeita_dados_invalidos(self):
        self.assertEqual(backup_validation.validar_perfil_para_backup(None), ERRO_DADOS_INVALIDOS)

    def test_validar_perfil_configurado_valido(self):
        perfil = {
            "origens_configuradas": [
                {
                    "caminho": "C:/Origem",
                    "ativo": True,
                    "tipos_arquivo": [
                        {
                            "ativo": True,
                            "destinos": [{"caminho": "D:/Backup", "operacao": "copiar"}],
                        }
                    ],
                }
            ]
        }

        self.assertEqual(backup_validation.validar_perfil_para_backup(perfil), OK)

    def test_validar_perfil_configurado_rejeita_sem_origem(self):
        self.assertEqual(
            backup_validation.validar_perfil_configurado_para_backup({"origens_configuradas": []}),
            ERRO_ORIGEM_INVALIDA,
        )

    def test_validar_destinos_do_tipo_rejeita_destino_invalido(self):
        self.assertEqual(
            backup_validation.validar_destinos_do_tipo({"destinos": [{"operacao": "copiar"}]}),
            ERRO_DESTINO_INVALIDO,
        )

    def test_validar_destinos_do_tipo_rejeita_operacao_invalida(self):
        self.assertEqual(
            backup_validation.validar_destinos_do_tipo({"destinos": [{"caminho": "D:/", "operacao": "zip"}]}),
            ERRO_OPERACAO_INVALIDA,
        )

    def test_validar_destinos_do_tipo_rejeita_mover_com_multiplos_destinos(self):
        tipo = {
            "destinos": [
                {"caminho": "D:/A", "operacao": "mover"},
                {"caminho": "D:/B", "operacao": "copiar"},
            ]
        }

        self.assertEqual(backup_validation.validar_destinos_do_tipo(tipo), ERRO_OPERACAO_INVALIDA)


if __name__ == "__main__":
    unittest.main()
