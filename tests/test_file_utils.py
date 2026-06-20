import tempfile
from datetime import datetime
from pathlib import Path
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

from backupmanager.engine import file_utils


def test_caminho_existe_para_arquivo_e_diretorio():
    with tempfile.TemporaryDirectory() as pasta:
        arquivo = Path(pasta) / "arquivo.txt"
        arquivo.write_text("conteudo", encoding="utf-8")

        assert_true(file_utils.caminho_existe(pasta))
        assert_true(file_utils.caminho_existe(arquivo))

def test_caminho_existe_retorna_false_para_invalido():
    with tempfile.TemporaryDirectory() as pasta:
        inexistente = Path(pasta) / "nao_existe"

        assert_false(file_utils.caminho_existe(inexistente))
        assert_false(file_utils.caminho_existe(None))

def test_caminho_e_diretorio():
    with tempfile.TemporaryDirectory() as pasta:
        arquivo = Path(pasta) / "arquivo.txt"
        arquivo.write_text("conteudo", encoding="utf-8")

        assert_true(file_utils.caminho_e_diretorio(pasta))
        assert_false(file_utils.caminho_e_diretorio(arquivo))
        assert_false(file_utils.caminho_e_diretorio(None))

def test_verificar_permissao_leitura():
    with tempfile.TemporaryDirectory() as pasta:
        arquivo = Path(pasta) / "arquivo.txt"
        arquivo.write_text("conteudo", encoding="utf-8")

        assert_true(file_utils.verificar_permissao_leitura(arquivo))
        assert_false(file_utils.verificar_permissao_leitura(None))

def test_verificar_permissao_escrita():
    with tempfile.TemporaryDirectory() as pasta:
        assert_true(file_utils.verificar_permissao_escrita(pasta))
        assert_false(file_utils.verificar_permissao_escrita(None))

def test_listar_arquivos_em_origem_ignora_subpastas():
    with tempfile.TemporaryDirectory() as pasta:
        arquivo_1 = Path(pasta) / "a.txt"
        subpasta = Path(pasta) / "sub"
        arquivo_2 = subpasta / "b.txt"
        subpasta.mkdir()
        arquivo_1.write_text("a", encoding="utf-8")
        arquivo_2.write_text("b", encoding="utf-8")

        arquivos = file_utils.listar_arquivos_em_origem(pasta)

        assert_equal(set(arquivos), {str(arquivo_1)})

def test_listar_arquivos_em_origem_invalida():
    with tempfile.TemporaryDirectory() as pasta:
        arquivo = Path(pasta) / "arquivo.txt"
        arquivo.write_text("conteudo", encoding="utf-8")

        assert_equal(file_utils.listar_arquivos_em_origem(None), [])
        assert_equal(file_utils.listar_arquivos_em_origem(arquivo), [])
        assert_equal(file_utils.listar_arquivos_em_origem(Path(pasta) / "inexistente"), [])

def test_listar_arquivos_de_origens():
    with tempfile.TemporaryDirectory() as pasta_1:
        with tempfile.TemporaryDirectory() as pasta_2:
            arquivo_1 = Path(pasta_1) / "a.txt"
            arquivo_2 = Path(pasta_2) / "b.txt"
            arquivo_1.write_text("a", encoding="utf-8")
            arquivo_2.write_text("b", encoding="utf-8")

            arquivos = file_utils.listar_arquivos_de_origens([pasta_1, pasta_2, None])

            assert_equal(set(arquivos), {str(arquivo_1), str(arquivo_2)})

def test_listar_arquivos_de_origens_rejeita_tipo_invalido():
    assert_equal(file_utils.listar_arquivos_de_origens(None), [])
    assert_equal(file_utils.listar_arquivos_de_origens("C:/origem"), [])

def test_obter_extensao():
    assert_equal(file_utils.obter_extensao("arquivo.TXT"), ".txt")
    assert_equal(file_utils.obter_extensao("arquivo"), "")
    assert_equal(file_utils.obter_extensao(None), "")

def test_obter_metadados_arquivo():
    with tempfile.TemporaryDirectory() as pasta:
        arquivo = Path(pasta) / "Relatorio.TXT"
        conteudo = "abc"
        arquivo.write_text(conteudo, encoding="utf-8")

        metadados = file_utils.obter_metadados_arquivo(arquivo)

        assert_equal(metadados["caminho"], str(arquivo))
        assert_equal(metadados["nome"], "Relatorio.TXT")
        assert_equal(metadados["extensao"], ".txt")
        assert_equal(metadados["tamanho"], len(conteudo))
        assert_is_instance(metadados["data_modificacao"], float)

def test_obter_metadados_arquivo_invalido():
    with tempfile.TemporaryDirectory() as pasta:
        assert_is_none(file_utils.obter_metadados_arquivo(None))
        assert_is_none(file_utils.obter_metadados_arquivo(pasta))
        assert_is_none(file_utils.obter_metadados_arquivo(Path(pasta) / "inexistente.txt"))

def test_filtrar_por_extensao():
    arquivo = {"extensao": ".py", "nome": "main.py", "tamanho": 10}
    restricoes = {"extensoes_permitidas": [".py"]}

    assert_true(file_utils._atende_restricao_extensao(arquivo, restricoes))

def test_filtrar_por_extensao_aceita_lista_vazia():
    arquivo = {"extensao": ".zip", "nome": "backup.zip", "tamanho": 10}
    restricoes = {"extensoes_permitidas": []}

    assert_true(file_utils._atende_restricao_extensao(arquivo, restricoes))

def test_filtrar_por_extensao_normaliza_ponto_e_maiusculas():
    arquivo = {"extensao": ".py", "nome": "main.py", "tamanho": 10}
    restricoes = {"extensoes_permitidas": ["PY"]}

    assert_true(file_utils._atende_restricao_extensao(arquivo, restricoes))

def test_filtrar_por_extensao_rejeita_extensao_nao_permitida():
    arquivo = {"extensao": ".txt", "nome": "nota.txt", "tamanho": 10}
    restricoes = {"extensoes_permitidas": [".py"]}

    assert_false(file_utils._atende_restricao_extensao(arquivo, restricoes))

def test_filtrar_por_nome():
    arquivo = {"extensao": ".txt", "nome": "relatorio_final.txt", "tamanho": 10}
    restricoes = {"regras_nome": [{"valor": "relatorio", "modo": "contem"}]}

    assert_true(file_utils._atende_restricao_nome(arquivo, restricoes))

def test_filtrar_por_nome_aceita_sem_regras():
    arquivo = {"extensao": ".txt", "nome": "qualquer.txt", "tamanho": 10}
    restricoes = {"regras_nome": []}

    assert_true(file_utils._atende_restricao_nome(arquivo, restricoes))

def test_filtrar_por_nome_ignora_maiusculas():
    arquivo = {"extensao": ".txt", "nome": "Relatorio_Final.txt", "tamanho": 10}
    restricoes = {"regras_nome": [{"valor": "relatorio", "modo": "contem"}]}

    assert_true(file_utils._atende_restricao_nome(arquivo, restricoes))

def test_filtrar_por_nome_rejeita_trecho_ausente():
    arquivo = {"extensao": ".txt", "nome": "notas.txt", "tamanho": 10}
    restricoes = {"regras_nome": [{"valor": "relatorio", "modo": "contem"}]}

    assert_false(file_utils._atende_restricao_nome(arquivo, restricoes))

def test_filtrar_por_regras_nome_contem():
    arquivo = {"extensao": ".txt", "nome": "ficha_ab_final.txt", "tamanho": 10}
    restricoes = {"regras_nome": [{"valor": "_ab", "modo": "contem"}]}

    assert_true(file_utils._atende_restricao_nome(arquivo, restricoes))

def test_filtrar_por_regras_nome_exato():
    arquivo = {"extensao": ".txt", "nome": "ficha_ab_final.txt", "tamanho": 10}
    restricoes = {"regras_nome": [{"valor": "ficha_ab_final.txt", "modo": "exato"}]}

    assert_true(file_utils._atende_restricao_nome(arquivo, restricoes))

def test_filtrar_por_regras_nome_exato_rejeita_nome_parcial():
    arquivo = {"extensao": ".txt", "nome": "ficha_ab_final.txt", "tamanho": 10}
    restricoes = {"regras_nome": [{"valor": "_ab", "modo": "exato"}]}

    assert_false(file_utils._atende_restricao_nome(arquivo, restricoes))

def test_filtrar_por_regras_nome_usa_qualquer_regra():
    arquivo = {"extensao": ".txt", "nome": "ficha_ab_final.txt", "tamanho": 10}
    restricoes = {
        "regras_nome": [
            {"valor": "relatorio.pdf", "modo": "exato"},
            {"valor": "_ab", "modo": "contem"},
        ]
    }

    assert_true(file_utils._atende_restricao_nome(arquivo, restricoes))

def test_filtrar_por_tamanho_minimo():
    arquivo = {"extensao": ".txt", "nome": "a.txt", "tamanho": 100}
    restricoes = {"tamanho_min": 50, "tamanho_max": None}

    assert_true(file_utils._atende_restricao_tamanho(arquivo, restricoes))

def test_filtrar_por_tamanho_maximo():
    arquivo = {"extensao": ".txt", "nome": "a.txt", "tamanho": 100}
    restricoes = {"tamanho_min": 0, "tamanho_max": 150}

    assert_true(file_utils._atende_restricao_tamanho(arquivo, restricoes))

def test_filtrar_por_tamanho_rejeita_menor_que_minimo():
    arquivo = {"extensao": ".txt", "nome": "a.txt", "tamanho": 20}
    restricoes = {"tamanho_min": 50, "tamanho_max": None}

    assert_false(file_utils._atende_restricao_tamanho(arquivo, restricoes))

def test_filtrar_por_tamanho_rejeita_maior_que_maximo():
    arquivo = {"extensao": ".txt", "nome": "a.txt", "tamanho": 200}
    restricoes = {"tamanho_min": 0, "tamanho_max": 150}

    assert_false(file_utils._atende_restricao_tamanho(arquivo, restricoes))

def test_filtrar_por_data_sem_limites():
    arquivo = {"data_modificacao": datetime(2026, 5, 11, 14, 30, 0).timestamp()}
    restricoes = {"data_modificacao_min": None, "data_modificacao_max": None}

    assert_true(file_utils._atende_restricao_data_modificacao(arquivo, restricoes))

def test_filtrar_por_data_minima_e_maxima():
    arquivo = {"data_modificacao": datetime(2026, 5, 11, 14, 30, 0).timestamp()}
    restricoes = {
        "data_modificacao_min": "2026-05-11 14:00:00",
        "data_modificacao_max": "2026-05-11 15:00:00",
    }

    assert_true(file_utils._atende_restricao_data_modificacao(arquivo, restricoes))

def test_filtrar_por_data_rejeita_antes_da_minima():
    arquivo = {"data_modificacao": datetime(2026, 5, 11, 13, 0, 0).timestamp()}
    restricoes = {"data_modificacao_min": "2026-05-11 14:00:00"}

    assert_false(file_utils._atende_restricao_data_modificacao(arquivo, restricoes))

def test_filtrar_por_data_rejeita_depois_da_maxima():
    arquivo = {"data_modificacao": datetime(2026, 5, 11, 16, 0, 0).timestamp()}
    restricoes = {"data_modificacao_max": "2026-05-11 15:00:00"}

    assert_false(file_utils._atende_restricao_data_modificacao(arquivo, restricoes))

def test_arquivo_atende_restricoes_combinadas():
    arquivo = {
        "extensao": ".py",
        "nome": "relatorio.py",
        "tamanho": 100,
        "data_modificacao": datetime(2026, 5, 11, 14, 30, 0).timestamp(),
    }
    restricoes = {
        "extensoes_permitidas": [".py"],
        "regras_nome": [{"valor": "relatorio", "modo": "contem"}],
        "tamanho_min": 50,
        "tamanho_max": 150,
        "data_modificacao_min": "2026-05-11 14:00:00",
        "data_modificacao_max": "2026-05-11 15:00:00",
    }

    assert_true(file_utils.arquivo_atende_restricoes(arquivo, restricoes))

def test_arquivo_atende_restricoes_rejeita_quando_um_filtro_falha():
    arquivo = {
        "extensao": ".txt",
        "nome": "relatorio.txt",
        "tamanho": 100,
        "data_modificacao": datetime(2026, 5, 11, 14, 30, 0).timestamp(),
    }
    restricoes = {
        "extensoes_permitidas": [".py"],
        "regras_nome": [{"valor": "relatorio", "modo": "contem"}],
        "tamanho_min": 50,
        "tamanho_max": 150,
        "data_modificacao_min": None,
        "data_modificacao_max": None,
    }

    assert_false(file_utils.arquivo_atende_restricoes(arquivo, restricoes))

def test_arquivo_atende_restricoes_aceita_restricoes_vazias():
    arquivo = {
        "extensao": ".zip",
        "nome": "backup.zip",
        "tamanho": 100,
        "data_modificacao": datetime(2026, 5, 11, 14, 30, 0).timestamp(),
    }
    restricoes = {
        "extensoes_permitidas": [],
        "regras_nome": [],
        "tamanho_min": 0,
        "tamanho_max": None,
        "data_modificacao_min": None,
        "data_modificacao_max": None,
    }

    assert_true(file_utils.arquivo_atende_restricoes(arquivo, restricoes))

def test_arquivo_atende_restricoes_rejeita_dados_invalidos():
    arquivo = {
        "extensao": ".py",
        "nome": "relatorio.py",
        "tamanho": 100,
        "data_modificacao": datetime(2026, 5, 11, 14, 30, 0).timestamp(),
    }
    restricoes = {
        "extensoes_permitidas": [],
        "regras_nome": [],
        "tamanho_min": 0,
        "tamanho_max": None,
        "data_modificacao_min": None,
        "data_modificacao_max": None,
    }

    assert_false(file_utils.arquivo_atende_restricoes(None, restricoes))
    assert_false(file_utils.arquivo_atende_restricoes(arquivo, None))
