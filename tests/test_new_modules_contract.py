import unittest

from backupmanager import (
    backup_result,
    backup_validation,
    ui_actions,
    ui_backup_flow,
    ui_converters,
    ui_history,
    ui_profiles,
    ui_restrictions,
    ui_theme,
)


class TestNewModulesContract(unittest.TestCase):
    def test_modulos_novos_declararam_api_publica(self):
        modulos = [
            backup_result,
            backup_validation,
            ui_actions,
            ui_backup_flow,
            ui_converters,
            ui_history,
            ui_profiles,
            ui_restrictions,
            ui_theme,
        ]

        for modulo in modulos:
            with self.subTest(modulo=modulo.__name__):
                self.assertTrue(hasattr(modulo, "__all__"))
                self.assertTrue(modulo.__all__)
                for nome in modulo.__all__:
                    self.assertFalse(nome.startswith("_"), nome)
                    self.assertTrue(hasattr(modulo, nome), nome)


if __name__ == "__main__":
    unittest.main()
