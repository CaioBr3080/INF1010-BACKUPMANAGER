from backupmanager.domain import perfil_manager
from backupmanager.return_codes import OK, ERRO_NOME_INVALIDO, ERRO_PERFIL_NAO_ENCONTRADO
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


def test_criar_perfil_valido():
    codigo, perfil = perfil_manager.criar_perfil("Backup Faculdade")

    assert_equal(codigo, OK)
    assert_equal(perfil["nome"], "Backup Faculdade")
    assert_equal(perfil["origens_configuradas"], [])
    assert_equal(set(perfil.keys()), {"id", "nome", "origens_configuradas", "ativo"})

def test_criar_perfil_nome_vazio():
    codigo, perfil = perfil_manager.criar_perfil("")

    assert_equal(codigo, ERRO_NOME_INVALIDO)
    assert_is_none(perfil)

def test_consultar_perfil_existente():
    _, perfil = perfil_manager.criar_perfil("Projetos")
    codigo, encontrado = perfil_manager.consultar_perfil([perfil], perfil["id"])

    assert_equal(codigo, OK)
    assert_equal(encontrado["id"], perfil["id"])

def test_consultar_perfil_inexistente():
    codigo, perfil = perfil_manager.consultar_perfil([], "perfil_x")

    assert_equal(codigo, ERRO_PERFIL_NAO_ENCONTRADO)
    assert_is_none(perfil)

def test_criar_origem_tipo_e_destino_configurados():
    origem = perfil_manager.criar_origem_configurada("C:/Documentos")
    destino = perfil_manager.criar_destino_tipo("D:/Backup", "recortar")
    tipo = perfil_manager.criar_tipo_arquivo("PDFs", {"extensoes_permitidas": [".pdf"]}, [destino])

    assert_equal(origem["caminho"], "C:/Documentos")
    assert_equal(tipo["nome"], "PDFs")
    assert_equal(tipo["destinos"][0]["operacao"], "recortar")
