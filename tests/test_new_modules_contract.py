from backupmanager.domain import backup_result, backup_validation
from backupmanager.ui import actions, backup_flow, converters, profiles, restrictions, theme
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


def test_modulos_novos_declararam_api_publica():
    modulos = [
        backup_result,
        backup_validation,
        actions,
        backup_flow,
        converters,
        profiles,
        restrictions,
        theme,
    ]

    for modulo in modulos:
        assert_true(hasattr(modulo, "__all__"), modulo.__name__)
        assert_true(modulo.__all__, modulo.__name__)
        for nome in modulo.__all__:
            assert_false(nome.startswith("_"), nome)
            assert_true(hasattr(modulo, nome), nome)
