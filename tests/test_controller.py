import tempfile
from pathlib import Path

import pytest

from backupmanager import controller
from backupmanager.return_codes import (
    OK,
    ERRO_BACKUP_SEM_ARQUIVOS,
    ERRO_DADOS_INVALIDOS,
    ERRO_ORIGEM_INVALIDA,
    ERRO_PERFIL_INATIVO,
)
from tests.assertions import (
    assert_equal,
    assert_false,
    assert_in,
    assert_is_none,
    assert_is_not_none,
    assert_not_equal,
    assert_true,
)


def resetar_estado():
    """Reinicia o estado global usado pelo controller nos testes."""
    controller._ESTADO["perfis"] = []
    controller._ESTADO["config"] = {}
    controller._ESTADO["alterado"] = False


def criar_gravador(retorno=None):
    """Cria uma funcao fake que registra chamadas e devolve um retorno fixo."""
    chamadas = []

    def gravador(*args, **kwargs):
        chamadas.append((args, kwargs))
        return retorno

    return gravador, chamadas


@pytest.fixture(autouse=True)
def resetar_controller_antes_de_cada_teste():
    """Garante que cada teste comece com o controller em memoria limpa."""
    resetar_estado()


def test_criar_perfil_altera_apenas_memoria():
    codigo, perfil = controller.criar_novo_perfil("Backup Teste")

    assert_equal(codigo, OK)
    assert_is_not_none(perfil)
    assert_equal(controller._ESTADO["perfis"], [perfil])
    assert_true(controller._ESTADO["alterado"])

def test_criar_perfil_nao_salva_json_imediatamente(monkeypatch):
    salvar_perfis, chamadas = criar_gravador()
    monkeypatch.setattr(controller.storage, "salvar_perfis", salvar_perfis)

    codigo, perfil = controller.criar_novo_perfil("Backup Teste")

    assert_equal(codigo, OK)
    assert_is_not_none(perfil)
    assert_equal(chamadas, [])


def test_finalizar_aplicacao_salva_json_quando_estado_foi_alterado(monkeypatch):
    controller._ESTADO["perfis"] = [{"id": "perfil_001", "nome": "Teste"}]
    controller._ESTADO["config"] = {"tema": "padrao"}
    controller._ESTADO["alterado"] = True
    salvar_perfis, chamadas_perfis = criar_gravador(OK)
    salvar_configuracoes, chamadas_config = criar_gravador(OK)
    monkeypatch.setattr(controller.storage, "salvar_perfis", salvar_perfis)
    monkeypatch.setattr(controller.storage, "salvar_configuracoes", salvar_configuracoes)

    codigo = controller.finalizar_aplicacao()

    assert_equal(codigo, OK)
    assert_equal(chamadas_perfis, [((controller._ESTADO["perfis"],), {})])
    assert_equal(chamadas_config, [((controller._ESTADO["config"],), {})])
    assert_false(controller._ESTADO["alterado"])


def test_finalizar_aplicacao_sem_alteracao_nao_salva_json(monkeypatch):
    controller._ESTADO["alterado"] = False
    salvar_perfis, chamadas_perfis = criar_gravador()
    salvar_configuracoes, chamadas_config = criar_gravador()
    monkeypatch.setattr(controller.storage, "salvar_perfis", salvar_perfis)
    monkeypatch.setattr(controller.storage, "salvar_configuracoes", salvar_configuracoes)

    codigo = controller.finalizar_aplicacao()

    assert_equal(codigo, OK)
    assert_equal(chamadas_perfis, [])
    assert_equal(chamadas_config, [])


def test_inicializar_aplicacao_carrega_estado_em_memoria(monkeypatch):
    perfis = [
        {
            "id": "perfil_001",
            "nome": "Backup",
            "origens_configuradas": [],
            "ativo": True,
        }
    ]
    config = {"versao": 1}
    controller._ESTADO["alterado"] = True
    def criar_arquivos_padrao():
        raise AssertionError("inicializacao nao deve gravar JSON")

    monkeypatch.setattr(controller.storage, "criar_arquivos_padrao", criar_arquivos_padrao)
    monkeypatch.setattr(controller.storage, "carregar_perfis", lambda: (OK, perfis))
    monkeypatch.setattr(controller.storage, "carregar_configuracoes", lambda: (OK, config))

    codigo = controller.inicializar_aplicacao()

    assert_equal(codigo, OK)
    assert_equal(controller._ESTADO["perfis"], perfis)
    assert_equal(controller._ESTADO["config"], config)
    assert_false(controller._ESTADO["alterado"])

def test_executar_backup_nao_altera_estado_quando_falha_validacao():
    codigo, perfil = controller.criar_novo_perfil("Backup Teste")
    assert_equal(codigo, OK)
    controller._ESTADO["alterado"] = False

    codigo_backup, resultado = controller.executar_backup_do_perfil(perfil["id"])

    assert_equal(codigo_backup, ERRO_ORIGEM_INVALIDA)
    assert_equal(resultado["perfil_id"], perfil["id"])
    assert_false(controller._ESTADO["alterado"])

def test_salvar_perfil_editado_aplica_dados_em_memoria(monkeypatch):
    codigo, perfil = controller.criar_novo_perfil("Backup Teste")
    assert_equal(codigo, OK)
    controller._ESTADO["alterado"] = False

    origens_configuradas = [
        {
            "id": "origem_001",
            "caminho": "C:/origem",
            "tipos_arquivo": [],
        }
    ]
    perfil_editado = {
        "id": perfil["id"],
        "nome": "Backup Editado",
        "origens_configuradas": origens_configuradas,
        "ativo": False,
    }
    salvar_perfis, chamadas = criar_gravador()
    monkeypatch.setattr(controller.storage, "salvar_perfis", salvar_perfis)

    codigo = controller.salvar_perfil_editado(perfil_editado)

    assert_equal(codigo, OK)
    assert_equal(perfil["nome"], "Backup Editado")
    assert_equal(perfil["origens_configuradas"], origens_configuradas)
    assert_equal(set(perfil.keys()), {"id", "nome", "origens_configuradas", "ativo"})
    assert_false(perfil["ativo"])
    assert_true(controller._ESTADO["alterado"])
    assert_equal(chamadas, [])

def test_salvar_perfil_editado_aplica_origens_configuradas():
    codigo, perfil = controller.criar_novo_perfil("Backup Teste")
    assert_equal(codigo, OK)
    origens_configuradas = [
        {
            "id": "origem_001",
            "caminho": "C:/origem",
            "tipos_arquivo": [
                {
                    "id": "tipo_pdf",
                    "nome": "PDFs",
                    "restricoes": {"extensoes_permitidas": [".pdf"]},
                    "destinos": [{"caminho": "D:/backup", "operacao": "copiar"}],
                }
            ],
        }
    ]

    codigo = controller.salvar_perfil_editado({
        "id": perfil["id"],
        "origens_configuradas": origens_configuradas,
    })

    assert_equal(codigo, OK)
    assert_equal(perfil["origens_configuradas"], origens_configuradas)

def test_salvar_perfil_editado_rejeita_dados_invalidos():
    codigo, perfil = controller.criar_novo_perfil("Backup Teste")
    assert_equal(codigo, OK)
    controller._ESTADO["alterado"] = False

    codigo = controller.salvar_perfil_editado({
        "id": perfil["id"],
        "origens_configuradas": "C:/origem",
    })

    assert_equal(codigo, ERRO_DADOS_INVALIDOS)
    assert_equal(perfil["origens_configuradas"], [])
    assert_false(controller._ESTADO["alterado"])

def test_ativar_e_desativar_perfil_alteram_memoria():
    codigo, perfil = controller.criar_novo_perfil("Backup Teste")
    assert_equal(codigo, OK)

    controller._ESTADO["alterado"] = False
    codigo = controller.desativar_perfil_por_id(perfil["id"])
    assert_equal(codigo, OK)
    assert_false(perfil["ativo"])
    assert_true(controller._ESTADO["alterado"])

    controller._ESTADO["alterado"] = False
    codigo = controller.ativar_perfil_por_id(perfil["id"])
    assert_equal(codigo, OK)
    assert_true(perfil["ativo"])
    assert_true(controller._ESTADO["alterado"])

def test_obter_arquivos_do_perfil_lista_arquivos_com_status_incluido():
    with tempfile.TemporaryDirectory() as pasta:
        arquivo_py = Path(pasta) / "main.py"
        arquivo_txt = Path(pasta) / "nota.txt"
        arquivo_py.write_text("print('ok')", encoding="utf-8")
        arquivo_txt.write_text("texto", encoding="utf-8")

        codigo, perfil = controller.criar_novo_perfil("Backup Teste")
        assert_equal(codigo, OK)
        codigo = controller.salvar_perfil_editado({
            "id": perfil["id"],
            "nome": perfil["nome"],
            "origens_configuradas": [
                {
                    "id": "origem_001",
                    "caminho": pasta,
                    "tipos_arquivo": [
                        {
                            "id": "tipo_py",
                            "nome": "Python",
                            "restricoes": {
                                "extensoes_permitidas": [".py"],
                                "regras_nome": [],
                                "tamanho_min": 0,
                                "tamanho_max": None,
                                "data_modificacao_min": None,
                                "data_modificacao_max": None,
                            },
                            "destinos": [{"caminho": "D:/backup", "operacao": "copiar"}],
                        }
                    ],
                }
            ],
        })
        assert_equal(codigo, OK)

        codigo, arquivos = controller.obter_arquivos_do_perfil(perfil["id"])

        assert_equal(codigo, OK)
        arquivos_por_nome = {arquivo["nome"]: arquivo for arquivo in arquivos}
        assert_true(arquivos_por_nome["main.py"]["incluido"])
        assert_false(arquivos_por_nome["nota.txt"]["incluido"])

def test_obter_arquivos_do_perfil_inexistente():
    codigo, arquivos = controller.obter_arquivos_do_perfil("perfil_inexistente")

    assert_not_equal(codigo, OK)
    assert_is_none(arquivos)

def test_obter_arquivos_do_perfil_configurado_lista_tipos_incluidos():
    with tempfile.TemporaryDirectory() as pasta:
        arquivo_pdf = Path(pasta) / "relatorio.pdf"
        arquivo_txt = Path(pasta) / "nota.txt"
        arquivo_pdf.write_text("pdf", encoding="utf-8")
        arquivo_txt.write_text("txt", encoding="utf-8")
        codigo, perfil = controller.criar_novo_perfil("Backup Teste")
        assert_equal(codigo, OK)
        codigo = controller.salvar_perfil_editado({
            "id": perfil["id"],
            "origens_configuradas": [
                {
                    "id": "origem_001",
                    "caminho": pasta,
                    "tipos_arquivo": [
                        {
                            "id": "tipo_pdf",
                            "nome": "PDFs",
                            "restricoes": {"extensoes_permitidas": [".pdf"]},
                            "destinos": [{"caminho": "D:/backup", "operacao": "copiar"}],
                        }
                    ],
                }
            ],
        })
        assert_equal(codigo, OK)

        codigo, arquivos = controller.obter_arquivos_do_perfil(perfil["id"])

        assert_equal(codigo, OK)
        arquivos_por_nome = {arquivo["nome"]: arquivo for arquivo in arquivos}
        assert_true(arquivos_por_nome["relatorio.pdf"]["incluido"])
        assert_equal(arquivos_por_nome["relatorio.pdf"]["tipos_incluidos"], ["PDFs"])
        assert_false(arquivos_por_nome["nota.txt"]["incluido"])

def test_executar_backup_bloqueia_perfil_inativo():
    codigo, perfil = controller.criar_novo_perfil("Backup Teste")
    assert_equal(codigo, OK)
    codigo = controller.desativar_perfil_por_id(perfil["id"])
    assert_equal(codigo, OK)
    controller._ESTADO["alterado"] = False

    codigo_backup, resultado = controller.executar_backup_do_perfil(perfil["id"])

    assert_equal(codigo_backup, ERRO_PERFIL_INATIVO)
    assert_is_none(resultado)
    assert_false(controller._ESTADO["alterado"])

def test_configuracoes_gerais_alteram_apenas_memoria():
    controller._ESTADO["config"] = {"tema": "escuro"}
    controller._ESTADO["alterado"] = False

    codigo, config = controller.obter_configuracoes()
    assert_equal(codigo, OK)
    assert_equal(config, {"tema": "escuro"})

    codigo = controller.salvar_configuracoes({"tema": "claro"})

    assert_equal(codigo, OK)
    assert_equal(controller._ESTADO["config"], {"tema": "claro"})
    assert_true(controller._ESTADO["alterado"])

def test_salvar_configuracoes_rejeita_dados_invalidos():
    controller._ESTADO["alterado"] = False

    codigo = controller.salvar_configuracoes(["tema"])

    assert_equal(codigo, ERRO_DADOS_INVALIDOS)
    assert_false(controller._ESTADO["alterado"])

def test_obter_extensoes_disponiveis_une_padrao_e_config():
    controller._ESTADO["config"] = {"extensoes_disponiveis": ["log", ".TXT"]}

    codigo, extensoes = controller.obter_extensoes_disponiveis()

    assert_equal(codigo, OK)
    assert_in(".txt", extensoes)
    assert_in(".log", extensoes)
    assert_equal(extensoes.count(".txt"), 1)

def test_adicionar_extensao_disponivel_normaliza_e_altera_memoria():
    controller._ESTADO["config"] = {}
    controller._ESTADO["alterado"] = False

    codigo = controller.adicionar_extensao_disponivel("LOG")

    assert_equal(codigo, OK)
    assert_equal(controller._ESTADO["config"]["extensoes_disponiveis"], [".log"])
    assert_true(controller._ESTADO["alterado"])

def test_adicionar_extensao_disponivel_rejeita_invalida():
    controller._ESTADO["alterado"] = False

    codigo = controller.adicionar_extensao_disponivel("")

    assert_equal(codigo, ERRO_DADOS_INVALIDOS)
    assert_false(controller._ESTADO["alterado"])
