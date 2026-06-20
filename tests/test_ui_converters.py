import unittest

from backupmanager import ui_converters


class TestUiConverters(unittest.TestCase):
    def test_converter_inteiro_opcional(self):
        self.assertEqual(ui_converters.converter_inteiro_opcional("", None), None)
        self.assertEqual(ui_converters.converter_inteiro_opcional("10", None), 10)
        self.assertEqual(ui_converters.converter_inteiro_opcional("-1", None), "invalido")
        self.assertEqual(ui_converters.converter_inteiro_opcional("abc", None), "invalido")

    def test_converter_data_opcional(self):
        self.assertIsNone(ui_converters.converter_data_opcional(""))
        self.assertEqual(ui_converters.converter_data_opcional("2026-06-18"), "2026-06-18")
        self.assertEqual(ui_converters.converter_data_opcional("data"), "invalido")


if __name__ == "__main__":
    unittest.main()
