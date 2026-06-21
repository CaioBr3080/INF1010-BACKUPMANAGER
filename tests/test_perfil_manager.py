from backupmanager.domain import perfil_manager
from backupmanager.return_codes import (
    OK,
    ERRO_DADOS_INVALIDOS,
    ERRO_NOME_INVALIDO,
    ERRO_PERFIL_NAO_ENCONTRADO,
)
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

def test_funcoes_de_acesso_do_perfil():
    codigo, perfil = perfil_manager.criar_perfil("Backup Aulas")

    assert_equal(codigo, OK)
    assert_true(perfil_manager.obter_id_perfil(perfil).startswith("perfil_"))
    assert_equal(perfil_manager.obter_nome_perfil(perfil), "Backup Aulas")
    assert_true(perfil_manager.perfil_esta_ativo(perfil))
    assert_equal(perfil_manager.obter_origens_configuradas(perfil), [])
    assert_false(perfil_manager.perfil_possui_origens_configuradas(perfil))

def test_aplicar_edicao_perfil_altera_campos_por_funcoes_do_tad():
    codigo, perfil = perfil_manager.criar_perfil("Backup Original")
    origem = perfil_manager.criar_origem_configurada("C:/origem")
    perfis = [perfil]

    codigo = perfil_manager.aplicar_edicao_perfil(
        perfis,
        {
            "id": perfil_manager.obter_id_perfil(perfil),
            "nome": "Backup Editado",
            "origens_configuradas": [origem],
            "ativo": False,
        },
    )

    assert_equal(codigo, OK)
    assert_equal(perfil_manager.obter_nome_perfil(perfil), "Backup Editado")
    assert_equal(perfil_manager.obter_origens_configuradas(perfil), [origem])
    assert_false(perfil_manager.perfil_esta_ativo(perfil))

def test_aplicar_edicao_perfil_rejeita_origens_invalidas():
    codigo, perfil = perfil_manager.criar_perfil("Backup Original")

    codigo = perfil_manager.aplicar_edicao_perfil(
        [perfil],
        {
            "id": perfil_manager.obter_id_perfil(perfil),
            "origens_configuradas": "C:/origem",
        },
    )

    assert_equal(codigo, ERRO_DADOS_INVALIDOS)
    assert_equal(perfil_manager.obter_origens_configuradas(perfil), [])

def test_alterar_origem_tipo_destino_e_restricoes_por_funcoes_do_tad():
    origem = perfil_manager.criar_origem_configurada("C:/origem")
    tipo = perfil_manager.criar_tipo_arquivo("PDF")
    destino = perfil_manager.criar_destino_tipo("D:/backup")
    restricoes = perfil_manager.criar_restricoes([".pdf"], [], 0, None, None, None)

    assert_equal(perfil_manager.alterar_origem_ativa(origem, False), OK)
    assert_false(perfil_manager.origem_esta_ativa(origem))

    assert_equal(perfil_manager.adicionar_tipo_origem(origem, tipo), OK)
    assert_equal(perfil_manager.obter_tipos_origem(origem), [tipo])

    assert_equal(perfil_manager.alterar_nome_tipo(tipo, "PDFs"), OK)
    assert_equal(perfil_manager.obter_nome_tipo(tipo), "PDFs")

    assert_equal(perfil_manager.alterar_restricoes_tipo(tipo, restricoes), OK)
    assert_equal(perfil_manager.obter_extensoes_restricoes(perfil_manager.obter_restricoes_tipo(tipo)), [".pdf"])

    assert_equal(perfil_manager.alterar_tipo_ativo(tipo, False), OK)
    assert_false(perfil_manager.tipo_esta_ativo(tipo))

    assert_equal(perfil_manager.adicionar_destino_tipo_configurado(tipo, destino), OK)
    assert_equal(perfil_manager.obter_destinos_tipo(tipo), [destino])

    assert_equal(perfil_manager.alterar_operacao_destino(destino, "recortar"), OK)
    assert_equal(perfil_manager.obter_operacao_destino(destino), "recortar")

    assert_equal(perfil_manager.remover_destino_tipo_por_indice(tipo, 0), OK)
    assert_equal(perfil_manager.obter_destinos_tipo(tipo), [])

    assert_equal(perfil_manager.remover_tipo_origem_por_indice(origem, 0), OK)
    assert_equal(perfil_manager.obter_tipos_origem(origem), [])
