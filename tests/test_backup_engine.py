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

from backupmanager.domain import backup_result, backup_validation
from backupmanager.engine import backup_engine
from backupmanager.return_codes import (
OK,
ERRO_ARQUIVO_NAO_ENCONTRADO,
ERRO_BACKUP_SEM_ARQUIVOS,
ERRO_DADOS_INVALIDOS,
ERRO_DESTINO_INVALIDO,
ERRO_OPERACAO_INVALIDA,
ERRO_ORIGEM_INVALIDA,
)


def test_montar_resultado_backup():
    resultado = backup_result.montar_resultado_backup("perfil_001")

    assert_equal(resultado["perfil_id"], "perfil_001")
    assert_equal(resultado["arquivos_processados"], 0)

def test_executar_backup_base_sem_arquivos():
    codigo, resultado = backup_engine.executar_backup({
        "id": "perfil_001",
        "origens_configuradas": [
            {
                "id": "origem_001",
                "caminho": "C:/origem",
                "tipos_arquivo": [
                    {
                        "id": "tipo_001",
                        "nome": "Todos",
                        "restricoes": {"regras_nome": []},
                        "destinos": [{"caminho": "D:/destino", "operacao": "copiar"}],
                    }
                ],
            }
        ],
    })

    assert_equal(codigo, ERRO_BACKUP_SEM_ARQUIVOS)
    assert_equal(resultado["perfil_id"], "perfil_001")

def test_validar_perfil_para_backup_valido():
    perfil = {
        "id": "perfil_001",
        "origens_configuradas": [
            {
                "id": "origem_001",
                "caminho": "C:/origem",
                "tipos_arquivo": [
                    {"destinos": [{"caminho": "D:/destino", "operacao": "copiar"}]}
                ],
            }
        ],
    }

    assert_equal(backup_validation.validar_perfil_para_backup(perfil), OK)

def test_validar_perfil_para_backup_rejeita_dados_invalidos():
    assert_equal(
        backup_validation.validar_perfil_para_backup(None),
        ERRO_DADOS_INVALIDOS,
    )

def test_validar_perfil_para_backup_rejeita_sem_origem():
    perfil = {
        "id": "perfil_001",
        "origens_configuradas": [],
    }

    assert_equal(
        backup_validation.validar_perfil_para_backup(perfil),
        ERRO_ORIGEM_INVALIDA,
    )

def test_validar_perfil_para_backup_rejeita_sem_destino():
    perfil = {
        "id": "perfil_001",
        "origens_configuradas": [
            {
                "id": "origem_001",
                "caminho": "C:/origem",
                "tipos_arquivo": [{"destinos": []}],
            }
        ],
    }

    assert_equal(
        backup_validation.validar_perfil_para_backup(perfil),
        ERRO_DESTINO_INVALIDO,
    )

def test_validar_perfil_para_backup_rejeita_operacao_invalida():
    perfil = {
        "id": "perfil_001",
        "origens_configuradas": [
            {
                "id": "origem_001",
                "caminho": "C:/origem",
                "tipos_arquivo": [
                    {"destinos": [{"caminho": "D:/destino", "operacao": "compactar"}]}
                ],
            }
        ],
    }

    assert_equal(
        backup_validation.validar_perfil_para_backup(perfil),
        ERRO_OPERACAO_INVALIDA,
    )

def test_executar_backup_retorna_erro_de_validacao():
    codigo, resultado = backup_engine.executar_backup({
        "id": "perfil_001",
        "origens_configuradas": [],
    })

    assert_equal(codigo, ERRO_ORIGEM_INVALIDA)
    assert_equal(resultado["status"], "erro")
    assert_equal(resultado["perfil_id"], "perfil_001")
    assert_true(resultado["erros"])

def test_gerar_caminho_destino_com_nome():
    arquivo = {"nome": "relatorio.txt", "caminho": "C:/origem/relatorio.txt"}

    caminho = backup_engine._gerar_caminho_destino(arquivo, "D:/backup")

    assert_equal(caminho, str(Path("D:/backup") / "relatorio.txt"))

def test_gerar_caminho_destino_com_caminho_sem_nome():
    arquivo = {"caminho": "C:/origem/relatorio.txt"}

    caminho = backup_engine._gerar_caminho_destino(arquivo, "D:/backup")

    assert_equal(caminho, str(Path("D:/backup") / "relatorio.txt"))

def test_gerar_caminho_destino_rejeita_dados_invalidos():
    assert_is_none(backup_engine._gerar_caminho_destino(None, "D:/backup"))
    assert_is_none(backup_engine._gerar_caminho_destino({}, "D:/backup"))
    assert_is_none(backup_engine._gerar_caminho_destino({"nome": "a.txt"}, ""))

def test_criar_pasta_destino_se_necessario_cria_diretorio():
    with tempfile.TemporaryDirectory() as pasta:
        caminho_destino = Path(pasta) / "backup" / "subpasta" / "arquivo.txt"

        codigo = backup_engine._criar_pasta_destino_se_necessario(caminho_destino)

        assert_equal(codigo, OK)
        assert_true(caminho_destino.parent.is_dir())

def test_criar_pasta_destino_se_necessario_aceita_diretorio_existente():
    with tempfile.TemporaryDirectory() as pasta:
        caminho_destino = Path(pasta) / "arquivo.txt"

        codigo = backup_engine._criar_pasta_destino_se_necessario(caminho_destino)

        assert_equal(codigo, OK)
        assert_true(Path(pasta).is_dir())

def test_criar_pasta_destino_se_necessario_rejeita_caminho_invalido():
    assert_equal(
        backup_engine._criar_pasta_destino_se_necessario(None),
        ERRO_DESTINO_INVALIDO,
    )
    assert_equal(
        backup_engine._criar_pasta_destino_se_necessario(""),
        ERRO_DESTINO_INVALIDO,
    )

def test_copiar_arquivo_copia_conteudo_e_mantem_original():
    with tempfile.TemporaryDirectory() as pasta:
        origem = Path(pasta) / "origem.txt"
        destino = Path(pasta) / "backup" / "origem.txt"
        origem.write_text("conteudo original", encoding="utf-8")

        codigo = backup_engine.copiar_arquivo(origem, destino)

        assert_equal(codigo, OK)
        assert_true(origem.is_file())
        assert_true(destino.is_file())
        assert_equal(destino.read_text(encoding="utf-8"), "conteudo original")

def test_copiar_arquivo_retorna_erro_sem_quebrar():
    with tempfile.TemporaryDirectory() as pasta:
        origem = Path(pasta) / "inexistente.txt"
        destino = Path(pasta) / "backup" / "inexistente.txt"

        codigo = backup_engine.copiar_arquivo(origem, destino)

        assert_equal(codigo, ERRO_ARQUIVO_NAO_ENCONTRADO)

def test_copiar_arquivo_rejeita_dados_invalidos():
    assert_equal(backup_engine.copiar_arquivo(None, "destino.txt"), ERRO_DADOS_INVALIDOS)
    assert_equal(backup_engine.copiar_arquivo("origem.txt", ""), ERRO_DADOS_INVALIDOS)

def test_mover_arquivo_move_conteudo_e_remove_original():
    with tempfile.TemporaryDirectory() as pasta:
        origem = Path(pasta) / "origem.txt"
        destino = Path(pasta) / "backup" / "origem.txt"
        origem.write_text("conteudo movido", encoding="utf-8")

        codigo = backup_engine.mover_arquivo(origem, destino)

        assert_equal(codigo, OK)
        assert_false(origem.exists())
        assert_true(destino.is_file())
        assert_equal(destino.read_text(encoding="utf-8"), "conteudo movido")

def test_mover_arquivo_retorna_erro_sem_quebrar():
    with tempfile.TemporaryDirectory() as pasta:
        origem = Path(pasta) / "inexistente.txt"
        destino = Path(pasta) / "backup" / "inexistente.txt"

        codigo = backup_engine.mover_arquivo(origem, destino)

        assert_equal(codigo, ERRO_ARQUIVO_NAO_ENCONTRADO)

def test_mover_arquivo_rejeita_dados_invalidos():
    assert_equal(backup_engine.mover_arquivo(None, "destino.txt"), ERRO_DADOS_INVALIDOS)
    assert_equal(backup_engine.mover_arquivo("origem.txt", ""), ERRO_DADOS_INVALIDOS)

def test_executar_backup_retorna_sem_arquivos_quando_filtro_rejeita_todos():
    with tempfile.TemporaryDirectory() as origem:
        with tempfile.TemporaryDirectory() as destino:
            arquivo = Path(origem) / "nota.txt"
            arquivo.write_text("texto", encoding="utf-8")
            perfil = {
                "id": "perfil_001",
                "origens_configuradas": [
                    {
                        "id": "origem_001",
                        "caminho": origem,
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
                                "destinos": [{"caminho": destino, "operacao": "copiar"}],
                            }
                        ],
                    }
                ],
            }

            codigo, resultado = backup_engine.executar_backup(perfil)

            assert_equal(codigo, ERRO_BACKUP_SEM_ARQUIVOS)
            assert_equal(resultado["status"], "sem_arquivos")
            assert_false((Path(destino) / "nota.txt").exists())

def test_executar_backup_configurado_envia_tipos_para_destinos_distintos():
    with tempfile.TemporaryDirectory() as origem:
        with tempfile.TemporaryDirectory() as destino_pdf:
            with tempfile.TemporaryDirectory() as destino_img:
                pdf = Path(origem) / "relatorio.pdf"
                imagem = Path(origem) / "foto.png"
                pdf.write_text("pdf", encoding="utf-8")
                imagem.write_text("png", encoding="utf-8")
                perfil = {
                    "id": "perfil_001",
                    "origens_configuradas": [
                        {
                            "id": "origem_001",
                            "caminho": origem,
                            "tipos_arquivo": [
                                {
                                    "id": "tipo_pdf",
                                    "nome": "PDFs",
                                    "restricoes": {"extensoes_permitidas": [".pdf"]},
                                    "destinos": [{"caminho": destino_pdf, "operacao": "copiar"}],
                                },
                                {
                                    "id": "tipo_img",
                                    "nome": "Imagens",
                                    "restricoes": {"extensoes_permitidas": [".png"]},
                                    "destinos": [{"caminho": destino_img, "operacao": "copiar"}],
                                },
                            ],
                        }
                    ],
                }

                codigo, resultado = backup_engine.executar_backup(perfil)

                assert_equal(codigo, OK)
                assert_equal(resultado["status"], "sucesso")
                assert_equal(resultado["arquivos_processados"], 2)
                assert_equal(len(resultado["arquivos"]), 2)
                assert_equal(resultado["arquivos"][0]["tipo"], "PDFs")
                assert_equal(resultado["arquivos"][0]["tamanho"], 3)
                assert_true((Path(destino_pdf) / "relatorio.pdf").exists())
                assert_true((Path(destino_img) / "foto.png").exists())
                assert_false((Path(destino_pdf) / "foto.png").exists())
                assert_false((Path(destino_img) / "relatorio.pdf").exists())

def test_executar_backup_configurado_ignora_arquivos_em_subpastas_da_origem():
    with tempfile.TemporaryDirectory() as origem:
        with tempfile.TemporaryDirectory() as destino:
            subpasta = Path(origem) / "sub"
            subpasta.mkdir()
            arquivo_raiz = Path(origem) / "raiz.pdf"
            arquivo_subpasta = subpasta / "interno.pdf"
            arquivo_raiz.write_text("raiz", encoding="utf-8")
            arquivo_subpasta.write_text("interno", encoding="utf-8")
            perfil = {
                "id": "perfil_001",
                "origens_configuradas": [
                    {
                        "id": "origem_001",
                        "caminho": origem,
                        "tipos_arquivo": [
                            {
                                "id": "tipo_pdf",
                                "nome": "PDFs",
                                "restricoes": {"extensoes_permitidas": [".pdf"]},
                                "destinos": [{"caminho": destino, "operacao": "copiar"}],
                            }
                        ],
                    }
                ],
            }

            codigo, resultado = backup_engine.executar_backup(perfil)

            assert_equal(codigo, OK)
            assert_equal(resultado["arquivos_processados"], 1)
            assert_true((Path(destino) / "raiz.pdf").exists())
            assert_false((Path(destino) / "interno.pdf").exists())

def test_executar_backup_configurado_recorta_para_destino_unico():
    with tempfile.TemporaryDirectory() as origem:
        with tempfile.TemporaryDirectory() as destino:
            arquivo = Path(origem) / "arquivo.txt"
            arquivo.write_text("recortar", encoding="utf-8")
            perfil = {
                "id": "perfil_001",
                "origens_configuradas": [
                    {
                        "id": "origem_001",
                        "caminho": origem,
                        "tipos_arquivo": [
                            {
                                "id": "tipo_txt",
                                "nome": "Textos",
                                "restricoes": {"extensoes_permitidas": [".txt"]},
                                "destinos": [{"caminho": destino, "operacao": "recortar"}],
                            }
                        ],
                    }
                ],
            }

            codigo, resultado = backup_engine.executar_backup(perfil)

            assert_equal(codigo, OK)
            assert_equal(resultado["arquivos_recortados"], 1)
            assert_equal(resultado["arquivos"][0]["nome"], "arquivo.txt")
            assert_equal(resultado["arquivos"][0]["operacao"], "recortar")
            assert_equal(resultado["arquivos"][0]["tamanho"], 8)
            assert_false(arquivo.exists())
            assert_true((Path(destino) / "arquivo.txt").exists())

def test_validar_perfil_configurado_rejeita_mover_para_multiplos_destinos():
    perfil = {
        "id": "perfil_001",
        "origens_configuradas": [
            {
                "id": "origem_001",
                "caminho": "C:/origem",
                "tipos_arquivo": [
                    {
                        "id": "tipo_pdf",
                        "nome": "PDFs",
                        "restricoes": {"extensoes_permitidas": [".pdf"]},
                        "destinos": [
                            {"caminho": "D:/destino_1", "operacao": "mover"},
                            {"caminho": "D:/destino_2", "operacao": "copiar"},
                        ],
                    }
                ],
            }
        ],
    }

    assert_equal(backup_validation.validar_perfil_para_backup(perfil), ERRO_OPERACAO_INVALIDA)

def test_executar_backup_configurado_ignora_origem_inativa():
    with tempfile.TemporaryDirectory() as origem_ativa:
        with tempfile.TemporaryDirectory() as origem_inativa:
            with tempfile.TemporaryDirectory() as destino:
                arquivo_ativo = Path(origem_ativa) / "ativo.txt"
                arquivo_inativo = Path(origem_inativa) / "inativo.txt"
                arquivo_ativo.write_text("ativo", encoding="utf-8")
                arquivo_inativo.write_text("inativo", encoding="utf-8")
                tipo = {
                    "id": "tipo_txt",
                    "nome": "Textos",
                    "restricoes": {"extensoes_permitidas": [".txt"]},
                    "destinos": [{"caminho": destino, "operacao": "copiar"}],
                }
                perfil = {
                    "id": "perfil_001",
                    "origens_configuradas": [
                        {
                            "id": "origem_inativa",
                            "caminho": origem_inativa,
                            "ativo": False,
                            "tipos_arquivo": [tipo],
                        },
                        {
                            "id": "origem_ativa",
                            "caminho": origem_ativa,
                            "ativo": True,
                            "tipos_arquivo": [tipo],
                        },
                    ],
                }

                codigo, resultado = backup_engine.executar_backup(perfil)

                assert_equal(codigo, OK)
                assert_equal(resultado["arquivos_processados"], 1)
                assert_true((Path(destino) / "ativo.txt").exists())
                assert_false((Path(destino) / "inativo.txt").exists())

def test_executar_backup_configurado_ignora_tipo_inativo():
    with tempfile.TemporaryDirectory() as origem:
        with tempfile.TemporaryDirectory() as destino:
            arquivo = Path(origem) / "arquivo.txt"
            arquivo.write_text("texto", encoding="utf-8")
            perfil = {
                "id": "perfil_001",
                "origens_configuradas": [
                    {
                        "id": "origem_001",
                        "caminho": origem,
                        "ativo": True,
                        "tipos_arquivo": [
                            {
                                "id": "tipo_txt",
                                "nome": "Textos",
                                "ativo": False,
                                "restricoes": {"extensoes_permitidas": [".txt"]},
                                "destinos": [{"caminho": destino, "operacao": "copiar"}],
                            }
                        ],
                    }
                ],
            }

            codigo, resultado = backup_engine.executar_backup(perfil)

            assert_equal(codigo, ERRO_BACKUP_SEM_ARQUIVOS)
            assert_equal(resultado["status"], "sem_arquivos")
            assert_false((Path(destino) / "arquivo.txt").exists())

def test_validar_perfil_configurado_ignora_conflito_de_tipo_inativo():
    perfil = {
        "id": "perfil_001",
        "origens_configuradas": [
            {
                "id": "origem_001",
                "caminho": "C:/origem",
                "ativo": True,
                "tipos_arquivo": [
                    {
                        "id": "tipo_pdf",
                        "nome": "PDFs",
                        "ativo": False,
                        "restricoes": {"extensoes_permitidas": [".pdf"]},
                        "destinos": [
                            {"caminho": "D:/destino_1", "operacao": "mover"},
                            {"caminho": "D:/destino_2", "operacao": "copiar"},
                        ],
                    }
                ],
            }
        ],
    }

    assert_equal(backup_validation.validar_perfil_para_backup(perfil), OK)
