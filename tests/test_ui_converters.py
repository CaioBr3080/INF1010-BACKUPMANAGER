from backupmanager.ui import converters as ui_converters
from tests.assertions import (
    assert_equal,
    assert_false,
    assert_in,
    assert_is_instance,
    assert_is_none,
    assert_is_not_none,
    assert_not_equal,
    assert_not_in,
    assert_true,
)


def test_converter_inteiro_opcional():
    assert_equal(ui_converters.converter_inteiro_opcional("", None), None)
    assert_equal(ui_converters.converter_inteiro_opcional("10", None), 10)
    assert_equal(ui_converters.converter_inteiro_opcional("-1", None), "invalido")
    assert_equal(ui_converters.converter_inteiro_opcional("abc", None), "invalido")

def test_converter_data_opcional():
    assert_is_none(ui_converters.converter_data_opcional(""))
    assert_equal(ui_converters.converter_data_opcional("2026-06-18"), "2026-06-18")
    assert_equal(ui_converters.converter_data_opcional("data"), "invalido")
