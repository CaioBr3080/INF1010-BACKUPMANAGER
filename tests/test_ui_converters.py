import unittest

from backupmanager import ui_converters


class FakeVar:
    def __init__(self, valor):
        self.valor = valor

    def get(self):
        return self.valor


class TestUiConverters(unittest.TestCase):
    def test_obter_unidade_intervalo_interface(self):
        self.assertEqual(
            ui_converters.obter_unidade_intervalo_interface({"intervalo_unidade_var": FakeVar("segundos")}),
            "segundos",
        )
        self.assertEqual(
            ui_converters.obter_unidade_intervalo_interface({"intervalo_unidade_var": FakeVar("dias")}),
            "minutos",
        )
        self.assertEqual(ui_converters.obter_unidade_intervalo_interface({}), "minutos")

    def test_converter_intervalo_para_minutos(self):
        self.assertEqual(ui_converters.converter_intervalo_para_minutos(120, "segundos"), 2)
        self.assertIsNone(ui_converters.converter_intervalo_para_minutos(30, "segundos"))
        self.assertEqual(ui_converters.converter_intervalo_para_minutos(2, "horas"), 120)
        self.assertEqual(ui_converters.converter_intervalo_para_minutos(15, "minutos"), 15)
        self.assertIsNone(ui_converters.converter_intervalo_para_minutos(None, "minutos"))

    def test_obter_intervalo_para_interface_prefere_valor_e_unidade_salvos(self):
        agendamento = {
            "intervalo_valor": 5,
            "intervalo_unidade": "horas",
            "intervalo_minutos": 300,
        }

        self.assertEqual(ui_converters.obter_intervalo_para_interface(agendamento), (5, "horas"))

    def test_obter_intervalo_para_interface_usa_minutos_legados(self):
        self.assertEqual(
            ui_converters.obter_intervalo_para_interface({"intervalo_minutos": 20}),
            (20, "minutos"),
        )

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
