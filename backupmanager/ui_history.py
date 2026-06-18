"""Janela e formatadores do historico de execucoes."""

import tkinter as tk
from tkinter import messagebox

import customtkinter as ctk

from backupmanager import controller
from backupmanager.return_codes import OK, ERRO_DADOS_INVALIDOS, obter_mensagem
from backupmanager.ui_theme import (
    COR_BORDA,
    COR_CAMPO,
    COR_FUNDO,
    COR_TEXTO,
    COR_VERMELHO,
    FONTE_SECAO,
    criar_botao,
    criar_listbox,
    manter_janela_acima_da_principal,
    widgets_existem,
)

__all__ = ["mostrar_historico_interface"]


def mostrar_historico_interface(estado_interface):
    """Abre a janela de historico do perfil selecionado.

    Consulta o controller, cria uma janela secundaria acima da principal,
    exibe lista de execucoes e detalhes formatados de arquivos/erros. Tambem
    oferece acao para limpar o historico do perfil em memoria.
    """
    perfil_id = estado_interface.get("perfil_selecionado_id")
    if not perfil_id:
        _mostrar_mensagem_resultado(ERRO_DADOS_INVALIDOS)
        return ERRO_DADOS_INVALIDOS

    codigo, _historico = controller.consultar_historico_do_perfil(perfil_id)
    if codigo != OK:
        _mostrar_mensagem_resultado(codigo)
        return codigo

    janela = ctk.CTkToplevel(estado_interface["janela"])
    janela.title("Historico do perfil")
    janela.geometry("980x560")
    janela.minsize(820, 440)
    janela.configure(fg_color=COR_FUNDO)
    manter_janela_acima_da_principal(janela, estado_interface["janela"])

    ctk.CTkLabel(
        janela,
        text="Historico do perfil",
        text_color=COR_TEXTO,
        font=FONTE_SECAO,
    ).pack(anchor="w", padx=14, pady=(14, 4))

    corpo = ctk.CTkFrame(janela, fg_color="transparent")
    corpo.pack(fill="both", expand=True, padx=14, pady=(4, 10))
    corpo.columnconfigure(0, weight=1)
    corpo.columnconfigure(1, weight=2)
    corpo.rowconfigure(0, weight=1)

    lista = criar_listbox(corpo, 16)
    lista.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

    detalhes = ctk.CTkTextbox(
        corpo,
        fg_color=COR_CAMPO,
        border_color=COR_BORDA,
        border_width=1,
        text_color=COR_TEXTO,
        font=ctk.CTkFont(family="Consolas", size=10),
    )
    detalhes.grid(row=0, column=1, sticky="nsew")

    def preencher_historico():
        if not widgets_existem(janela, lista, detalhes):
            return

        codigo_atualizar, historico_atualizado = controller.consultar_historico_do_perfil(perfil_id)
        if codigo_atualizar != OK:
            _mostrar_mensagem_resultado(codigo_atualizar)
            return
        lista.delete(0, tk.END)
        detalhes.configure(state="normal")
        detalhes.delete("1.0", tk.END)
        if not historico_atualizado:
            lista.insert(tk.END, "Nenhum historico para este perfil")
            detalhes.insert("end", "Nenhuma execucao registrada.")
        else:
            for registro in historico_atualizado:
                lista.insert(
                    tk.END,
                    registro.get("data_hora", "")
                    + " | "
                    + registro.get("status", "")
                    + " | "
                    + str(registro.get("arquivos_processados", 0))
                    + " processados",
                )
        detalhes.configure(state="disabled")

    def atualizar_detalhes(indice):
        if not widgets_existem(janela, detalhes):
            return

        codigo_atualizar, historico_atualizado = controller.consultar_historico_do_perfil(perfil_id)
        if codigo_atualizar != OK or indice < 0 or indice >= len(historico_atualizado):
            return
        registro = historico_atualizado[indice]
        erros = registro.get("erros", [])
        conteudo = _formatar_resumo_historico(registro, erros)
        arquivos = registro.get("arquivos", [])
        if arquivos:
            conteudo += "\n\nArquivos processados\n"
            conteudo += "--------------------\n"
            for indice_arquivo, arquivo in enumerate(arquivos, start=1):
                conteudo += _formatar_arquivo_historico(arquivo, indice_arquivo) + "\n"
        if erros:
            conteudo += "\n\nErros\n"
            conteudo += "-----\n"
            conteudo += "\n".join(_formatar_erro_historico(erro) for erro in erros)

        detalhes.configure(state="normal")
        detalhes.delete("1.0", tk.END)
        detalhes.insert("end", conteudo)
        detalhes.configure(state="disabled")

    def ao_selecionar(evento):
        del evento
        if not widgets_existem(lista):
            return

        selecao = lista.curselection()
        if selecao:
            atualizar_detalhes(selecao[0])

    def limpar_historico():
        codigo_limpar = controller.limpar_historico_do_perfil(perfil_id)
        if codigo_limpar == OK:
            preencher_historico()
        _mostrar_mensagem_resultado(codigo_limpar)

    lista.bind("<<ListboxSelect>>", ao_selecionar)
    preencher_historico()

    linha_botoes = ctk.CTkFrame(janela, fg_color="transparent")
    linha_botoes.pack(fill="x", padx=14, pady=(0, 14))
    criar_botao(linha_botoes, "Limpar historico do perfil", limpar_historico, COR_VERMELHO).pack(side="left")
    criar_botao(linha_botoes, "Fechar", janela.destroy).pack(side="right")
    return OK


def _formatar_resumo_historico(registro, erros):
    """Formata os totais e metadados de uma execucao do historico."""
    linhas = [
        "Resumo da execucao",
        "------------------",
        _formatar_campo_historico("Data", registro.get("data_hora", "")),
        _formatar_campo_historico("Status", registro.get("status", "")),
        "",
        "Totais",
        "------",
        _formatar_campo_historico("Processados", registro.get("arquivos_processados", 0)),
        _formatar_campo_historico("Copiados", registro.get("arquivos_copiados", 0)),
        _formatar_campo_historico("Movidos", registro.get("arquivos_movidos", 0)),
        _formatar_campo_historico("Recortados", registro.get("arquivos_recortados", 0)),
        _formatar_campo_historico("Erros", len(erros)),
    ]
    return "\n".join(linhas)


def _formatar_campo_historico(rotulo, valor):
    """Formata um campo chave/valor alinhado para leitura em monoespaco."""
    return rotulo.ljust(12) + ": " + str(valor)


def _formatar_arquivo_historico(arquivo, indice):
    """Formata detalhes de um arquivo processado para a janela de historico."""
    nome = arquivo.get("nome", "")
    tipo = arquivo.get("tipo") or arquivo.get("extensao") or "(sem tipo)"
    tamanho = str(arquivo.get("tamanho", 0))
    operacao = arquivo.get("operacao", "")
    status = arquivo.get("status", "")
    origem = arquivo.get("origem", "")
    destino = arquivo.get("destino", "")
    linhas = [
        str(indice) + ". " + nome,
        "   " + _formatar_campo_historico("Tipo", tipo).strip(),
        "   " + _formatar_campo_historico("Tamanho", tamanho + " bytes").strip(),
        "   " + _formatar_campo_historico("Operacao", operacao).strip(),
        "   " + _formatar_campo_historico("Status", status).strip(),
        "   " + _formatar_campo_historico("Origem", origem).strip(),
        "   " + _formatar_campo_historico("Destino", destino).strip(),
    ]
    return "\n".join(linhas) + "\n"


def _formatar_erro_historico(erro):
    """Formata um erro do historico preservando arquivo, destino e codigo."""
    if not isinstance(erro, dict):
        return "- " + str(erro)

    linhas = [
        "- " + str(erro.get("arquivo", "Arquivo nao informado")),
        "  " + _formatar_campo_historico("Destino", erro.get("destino", "")).strip(),
        "  " + _formatar_campo_historico("Codigo", erro.get("codigo", "")).strip(),
    ]
    return "\n".join(linhas)


def _mostrar_mensagem_resultado(codigo):
    """Mostra retorno do controller dentro de modulos auxiliares de UI."""
    mensagem = obter_mensagem(codigo)
    if codigo == OK:
        messagebox.showinfo("BackupManager", mensagem)
    else:
        messagebox.showerror("BackupManager", mensagem)
    return codigo
