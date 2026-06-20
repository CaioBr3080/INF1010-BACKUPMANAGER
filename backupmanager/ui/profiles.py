"""Painel de perfis da interface."""

import tkinter as tk
from tkinter import messagebox

import customtkinter as ctk

from backupmanager import controller
from backupmanager.domain import perfil_manager
from backupmanager.return_codes import OK, ERRO_DADOS_INVALIDOS
from backupmanager.ui.actions import (
    limpar_formulario,
    mostrar_mensagem_resultado,
    preencher_formulario_com_perfil,
    sincronizar_perfil_atual_interface,
)
from backupmanager.ui.theme import (
    COR_AZUL,
    COR_BORDA,
    COR_TEXTO,
    COR_VERMELHO,
    FONTE_PADRAO,
    criar_botao,
    criar_entry,
    criar_label,
    criar_listbox,
    criar_painel,
)

__all__ = [
    "criar_area_perfis",
    "atualizar_lista_perfis",
    "selecionar_perfil_por_id",
]


def criar_area_perfis(janela, estado_interface):
    """Cria o painel de gerenciamento de perfis.

    Monta entrada de nome, botao de criacao, listbox de perfis, checkbox de
    ativo e botao de exclusao. Registra os widgets necessarios em
    `estado_interface` para que outros callbacks possam atualizar a tela.
    """
    frame = criar_painel(janela, "Perfis")
    frame.pack(fill="x", padx=8, pady=8)

    linha_nome = ctk.CTkFrame(frame, fg_color="transparent")
    linha_nome.pack(fill="x", padx=8, pady=(8, 4))

    criar_label(linha_nome, "Nome").pack(side="left")
    estado_interface["entrada_nome"] = criar_entry(linha_nome)
    estado_interface["entrada_nome"].pack(side="left", fill="x", expand=True, padx=8)

    criar_botao(linha_nome, "Criar perfil", lambda: _criar_perfil_interface(estado_interface), COR_AZUL).pack(
        side="left"
    )

    estado_interface["lista_perfis"] = criar_listbox(frame, 6)
    estado_interface["lista_perfis"].pack(fill="x", padx=8, pady=4)
    estado_interface["lista_perfis"].bind(
        "<<ListboxSelect>>",
        lambda evento: _selecionar_perfil_interface(estado_interface),
    )

    linha_acoes = ctk.CTkFrame(frame, fg_color="transparent")
    linha_acoes.pack(fill="x", padx=8, pady=(4, 8))

    estado_interface["ativo_var"] = tk.BooleanVar(value=True)
    ctk.CTkCheckBox(
        linha_acoes,
        text="Perfil ativo",
        variable=estado_interface["ativo_var"],
        text_color=COR_TEXTO,
        fg_color=COR_AZUL,
        hover_color="#1d4ed8",
        border_color=COR_BORDA,
        font=FONTE_PADRAO,
    ).pack(side="left")
    criar_botao(
        linha_acoes,
        "Excluir perfil",
        lambda: _excluir_perfil_interface(estado_interface),
        COR_VERMELHO,
    ).pack(side="right")

    return frame


def atualizar_lista_perfis(estado_interface):
    """Recarrega a listbox de perfis a partir do controller.

    Atualiza tambem `ids_perfis`, que mapeia indice visual para id real do
    perfil. Retorna o codigo recebido do controller.
    """
    codigo, perfis = controller.obter_perfis()
    if codigo != OK:
        mostrar_mensagem_resultado(codigo)
        return codigo

    lista = estado_interface["lista_perfis"]
    lista.delete(0, tk.END)
    estado_interface["ids_perfis"] = []

    for perfil in perfis:
        marcador = "ativo" if perfil_manager.perfil_esta_ativo(perfil) else "inativo"
        lista.insert(tk.END, perfil_manager.obter_nome_perfil(perfil) + " (" + marcador + ")")
        estado_interface["ids_perfis"].append(perfil_manager.obter_id_perfil(perfil))

    return codigo


def selecionar_perfil_por_id(estado_interface, perfil_id):
    """Seleciona na interface o perfil identificado por `perfil_id`.

    Localiza o id em `ids_perfis`, move a selecao da listbox e dispara o mesmo
    fluxo usado por selecao manual. Retorna erro quando o id nao esta visivel.
    """
    if perfil_id not in estado_interface["ids_perfis"]:
        return ERRO_DADOS_INVALIDOS

    indice = estado_interface["ids_perfis"].index(perfil_id)
    lista = estado_interface["lista_perfis"]
    lista.selection_clear(0, tk.END)
    lista.selection_set(indice)
    lista.activate(indice)
    return _selecionar_perfil_interface(estado_interface)


def _criar_perfil_interface(estado_interface):
    """Cria um perfil a partir do nome informado na interface."""
    nome = estado_interface["entrada_nome"].get()
    codigo, perfil = controller.criar_novo_perfil(nome)
    if codigo != OK:
        mostrar_mensagem_resultado(codigo)
        return codigo

    perfil_id = perfil_manager.obter_id_perfil(perfil)
    estado_interface["perfil_selecionado_id"] = perfil_id
    atualizar_lista_perfis(estado_interface)
    selecionar_perfil_por_id(estado_interface, perfil_id)
    mostrar_mensagem_resultado(codigo)
    return codigo


def _selecionar_perfil_interface(estado_interface):
    """Seleciona o perfil destacado na lista."""
    selecao = estado_interface["lista_perfis"].curselection()
    if not selecao:
        return ERRO_DADOS_INVALIDOS

    indice = selecao[0]
    perfil_id = estado_interface["ids_perfis"][indice]
    if estado_interface.get("perfil_selecionado_id") and estado_interface.get("perfil_selecionado_id") != perfil_id:
        sincronizar_perfil_atual_interface(estado_interface, False)

    codigo, perfil = controller.obter_perfil_por_id(perfil_id)
    if codigo != OK:
        mostrar_mensagem_resultado(codigo)
        return codigo

    preencher_formulario_com_perfil(estado_interface, perfil)
    return OK


def _excluir_perfil_interface(estado_interface):
    """Exclui o perfil selecionado."""
    perfil_id = estado_interface.get("perfil_selecionado_id")
    if not perfil_id:
        return mostrar_mensagem_resultado(ERRO_DADOS_INVALIDOS)

    if not messagebox.askyesno("BackupManager", "Excluir o perfil selecionado?"):
        return OK

    codigo = controller.excluir_perfil_por_id(perfil_id)
    if codigo == OK:
        estado_interface["perfil_selecionado_id"] = None
        limpar_formulario(estado_interface)
        atualizar_lista_perfis(estado_interface)
    mostrar_mensagem_resultado(codigo)
    return codigo
