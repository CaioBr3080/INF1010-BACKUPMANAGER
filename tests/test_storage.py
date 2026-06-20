import tempfile
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

from backupmanager.infra import storage
from backupmanager.return_codes import OK, ERRO_DADOS_INVALIDOS, ERRO_JSON_CORROMPIDO


def test_salvar_e_carregar_json():
    with tempfile.TemporaryDirectory() as pasta:
        caminho = Path(pasta) / "dados.json"
        dados = [{"nome": "Backup"}]

        codigo_salvar = storage._salvar_json(caminho, dados)
        codigo_carregar, carregado = storage._carregar_json(caminho, [])

        assert_equal(codigo_salvar, OK)
        assert_equal(codigo_carregar, OK)
        assert_equal(carregado, dados)

def test_carregar_json_inexistente():
    with tempfile.TemporaryDirectory() as pasta:
        caminho = Path(pasta) / "inexistente.json"

        codigo, carregado = storage._carregar_json(caminho, [])

        assert_equal(codigo, OK)
        assert_equal(carregado, [])

def test_carregar_json_corrompido():
    with tempfile.TemporaryDirectory() as pasta:
        caminho = Path(pasta) / "dados.json"
        caminho.write_text("{json invalido", encoding="utf-8")

        codigo, carregado = storage._carregar_json(caminho, [])

        assert_equal(codigo, ERRO_JSON_CORROMPIDO)
        assert_equal(carregado, [])

def test_salvar_json_rejeita_dados_nao_serializaveis():
    with tempfile.TemporaryDirectory() as pasta:
        caminho = Path(pasta) / "dados.json"

        codigo = storage._salvar_json(caminho, {"valores": {1, 2}})

        assert_equal(codigo, ERRO_DADOS_INVALIDOS)

def test_criar_arquivos_padrao():
    data_dir_original = storage._DATA_DIR
    perfis_path_original = storage._PERFIS_PATH
    config_path_original = storage._CONFIG_PATH

    try:
        with tempfile.TemporaryDirectory() as pasta:
            storage._DATA_DIR = Path(pasta) / "data"
            storage._PERFIS_PATH = storage._DATA_DIR / "perfis.json"
            storage._CONFIG_PATH = storage._DATA_DIR / "config.json"

            codigo = storage.criar_arquivos_padrao()

            assert_equal(codigo, OK)
            assert_true(storage._PERFIS_PATH.exists())
            assert_true(storage._CONFIG_PATH.exists())
            assert_equal(storage._carregar_json(storage._PERFIS_PATH, None), (OK, []))
            assert_equal(storage._carregar_json(storage._CONFIG_PATH, None), (OK, {}))
    finally:
        storage._DATA_DIR = data_dir_original
        storage._PERFIS_PATH = perfis_path_original
        storage._CONFIG_PATH = config_path_original
