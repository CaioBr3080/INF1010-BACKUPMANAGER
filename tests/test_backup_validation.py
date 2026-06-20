from backupmanager.domain import backup_validation
from backupmanager.return_codes import (
    OK,
    ERRO_DADOS_INVALIDOS,
    ERRO_DESTINO_INVALIDO,
    ERRO_OPERACAO_INVALIDA,
    ERRO_ORIGEM_INVALIDA,
)
from tests.assertions import assert_equal


def test_validar_perfil_rejeita_formato_antigo():
    perfil = {
        "origens": ["C:/Origem"],
        "destinos": ["D:/Backup"],
        "operacao": "copiar",
    }

    assert_equal(backup_validation.validar_perfil_para_backup(perfil), ERRO_ORIGEM_INVALIDA)

def test_validar_perfil_rejeita_dados_invalidos():
    assert_equal(backup_validation.validar_perfil_para_backup(None), ERRO_DADOS_INVALIDOS)

def test_validar_perfil_configurado_valido():
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

    assert_equal(backup_validation.validar_perfil_para_backup(perfil), OK)

def test_validar_perfil_configurado_rejeita_sem_origem():
    assert_equal(
        backup_validation.validar_perfil_configurado_para_backup({"origens_configuradas": []}),
        ERRO_ORIGEM_INVALIDA,
    )

def test_validar_destinos_do_tipo_rejeita_destino_invalido():
    assert_equal(
        backup_validation.validar_destinos_do_tipo({"destinos": [{"operacao": "copiar"}]}),
        ERRO_DESTINO_INVALIDO,
    )

def test_validar_destinos_do_tipo_rejeita_operacao_invalida():
    assert_equal(
        backup_validation.validar_destinos_do_tipo({"destinos": [{"caminho": "D:/", "operacao": "zip"}]}),
        ERRO_OPERACAO_INVALIDA,
    )

def test_validar_destinos_do_tipo_rejeita_mover_com_multiplos_destinos():
    tipo = {
        "destinos": [
            {"caminho": "D:/A", "operacao": "mover"},
            {"caminho": "D:/B", "operacao": "copiar"},
        ]
    }

    assert_equal(backup_validation.validar_destinos_do_tipo(tipo), ERRO_OPERACAO_INVALIDA)
