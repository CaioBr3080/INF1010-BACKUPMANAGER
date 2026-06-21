from backupmanager.domain import backup_validation, perfil_manager
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
        backup_validation.validar_lista_destinos([perfil_manager.criar_destino_tipo("", "copiar")]),
        ERRO_DESTINO_INVALIDO,
    )

def test_validar_destinos_do_tipo_rejeita_operacao_invalida():
    assert_equal(
        backup_validation.validar_lista_destinos([perfil_manager.criar_destino_tipo("D:/", "zip")]),
        ERRO_OPERACAO_INVALIDA,
    )

def test_validar_lista_destinos_rejeita_mover_com_multiplos_destinos():
    destinos = [
        perfil_manager.criar_destino_tipo("D:/A", "mover"),
        perfil_manager.criar_destino_tipo("D:/B", "copiar"),
    ]

    assert_equal(backup_validation.validar_lista_destinos(destinos), ERRO_OPERACAO_INVALIDA)

def test_validar_destinos_do_tipo_delega_para_lista_do_tipo():
    tipo = perfil_manager.criar_tipo_arquivo(
        "PDF",
        destinos=[perfil_manager.criar_destino_tipo("D:/Backup", "copiar")],
    )

    assert_equal(backup_validation.validar_destinos_do_tipo(tipo), OK)
