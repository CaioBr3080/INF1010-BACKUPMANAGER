"""Area de restricoes e filtros da UI."""

import tkinter as tk
from tkinter import messagebox

import customtkinter as ctk

from backupmanager import controller
from backupmanager.domain import perfil_manager
from backupmanager.return_codes import OK, ERRO_DADOS_INVALIDOS, obter_mensagem
from backupmanager.ui.converters import converter_data_opcional, converter_inteiro_opcional
from backupmanager.ui.theme import (
    COR_AZUL,
    COR_BORDA,
    COR_CAMPO,
    COR_PAINEL,
    COR_PAINEL_2,
    COR_TEXTO,
    FONTE_PADRAO,
    FONTE_SELECAO,
    criar_botao,
    criar_entry,
    criar_label,
    criar_listbox,
    criar_painel,
)

__all__ = [
    "criar_area_restricoes",
    "atualizar_checkboxes_extensoes",
    "atualizar_lista_regras_nome",
    "criar_restricoes_da_interface",
    "preencher_formulario_com_tipo",
    "limpar_area_tipo_destino",
    "formulario_tipo_possui_valor_invalido",
]


def criar_area_restricoes(janela, estado_interface, ao_alterar_restricoes=None):
    """Cria o painel de restricoes de arquivos.

    Monta controles de extensao, regras de nome, tamanho e datas. Registra os
    widgets em `estado_interface` e aceita callback opcional para salvar
    alteracoes do tipo selecionado.
    """
    frame = criar_painel(janela, "Restrições")
    frame.grid(row=0, column=1, sticky="nsew", padx=(4, 0), pady=8)

    conteudo = ctk.CTkScrollableFrame(
        frame,
        fg_color="transparent",
        scrollbar_button_color=COR_PAINEL_2,
        scrollbar_button_hover_color=COR_AZUL,
    )
    conteudo.pack(fill="both", expand=True, padx=6, pady=(0, 8))

    _criar_area_extensoes(conteudo, estado_interface)
    _criar_area_regras_nome(conteudo, estado_interface, ao_alterar_restricoes)
    _criar_area_tamanho(conteudo, estado_interface)
    _criar_area_datas(conteudo, estado_interface)
    return frame


def _criar_area_extensoes(container, estado_interface):
    """Cria a selecao de extensoes disponiveis por checkbox."""
    criar_label(container, "Extensões permitidas").pack(anchor="w", padx=8, pady=(8, 0))

    linha_adicionar = ctk.CTkFrame(container, fg_color="transparent")
    linha_adicionar.pack(fill="x", padx=8, pady=(4, 4))
    estado_interface["entrada_nova_extensao"] = criar_entry(linha_adicionar)
    estado_interface["entrada_nova_extensao"].pack(side="left", fill="x", expand=True)
    criar_botao(
        linha_adicionar,
        "Adicionar",
        lambda: _adicionar_extensao_interface(estado_interface),
        COR_AZUL,
        largura=92,
    ).pack(side="left", padx=(6, 0))

    estado_interface["frame_extensoes"] = ctk.CTkScrollableFrame(
        container,
        height=112,
        fg_color=COR_CAMPO,
        border_color=COR_BORDA,
        border_width=1,
        corner_radius=6,
    )
    estado_interface["frame_extensoes"].pack(fill="x", padx=8, pady=(0, 4))
    atualizar_checkboxes_extensoes(estado_interface, [])
    return estado_interface["frame_extensoes"]


def _criar_area_regras_nome(container, estado_interface, ao_alterar_restricoes=None):
    """Cria o formulario e a lista de regras por nome de arquivo."""
    criar_label(container, "Filtro por nome").pack(anchor="w", padx=8, pady=(8, 0))

    linha_adicionar = ctk.CTkFrame(container, fg_color="transparent")
    linha_adicionar.pack(fill="x", padx=8, pady=(4, 4))
    estado_interface["entrada_regra_nome"] = criar_entry(linha_adicionar)
    estado_interface["entrada_regra_nome"].pack(side="left", fill="x", expand=True)
    estado_interface["entrada_regra_nome"].bind(
        "<Return>",
        lambda evento: _adicionar_regra_nome_interface(estado_interface, ao_alterar_restricoes),
    )
    estado_interface["modo_regra_nome_var"] = tk.StringVar(value="Contém no nome")
    combo_modo = ctk.CTkComboBox(
        linha_adicionar,
        variable=estado_interface["modo_regra_nome_var"],
        values=("Contém no nome", "Nome completo"),
        fg_color=COR_CAMPO,
        border_color=COR_BORDA,
        button_color=COR_PAINEL_2,
        button_hover_color=COR_AZUL,
        dropdown_fg_color=COR_PAINEL,
        dropdown_hover_color=COR_AZUL,
        text_color=COR_TEXTO,
        dropdown_text_color=COR_TEXTO,
        width=128,
        height=34,
        corner_radius=6,
        font=FONTE_SELECAO,
    )
    combo_modo.pack(side="left", padx=(6, 0))
    criar_botao(
        linha_adicionar,
        "Adicionar",
        lambda: _adicionar_regra_nome_interface(estado_interface, ao_alterar_restricoes),
        COR_AZUL,
        largura=86,
    ).pack(side="left", padx=(6, 0))

    estado_interface["lista_regras_nome"] = criar_listbox(container, 4)
    estado_interface["lista_regras_nome"].pack(fill="x", padx=8, pady=(0, 4))
    criar_botao(
        container,
        "Remover regra",
        lambda: _remover_regra_nome_interface(estado_interface, ao_alterar_restricoes),
        largura=112,
    ).pack(anchor="w", padx=8, pady=(0, 4))
    atualizar_lista_regras_nome(estado_interface, [])
    return estado_interface["lista_regras_nome"]


def _criar_area_tamanho(container, estado_interface):
    """Cria os campos de tamanho minimo e maximo."""
    linha_tamanhos = ctk.CTkFrame(container, fg_color="transparent")
    linha_tamanhos.pack(fill="x", padx=8, pady=4)
    criar_label(linha_tamanhos, "Tamanho min").grid(row=0, column=0, sticky="w")
    criar_label(linha_tamanhos, "Tamanho max").grid(row=0, column=1, sticky="w", padx=(8, 0))
    estado_interface["entrada_tamanho_min"] = criar_entry(linha_tamanhos, 16)
    estado_interface["entrada_tamanho_min"].grid(row=1, column=0, sticky="ew")
    estado_interface["entrada_tamanho_max"] = criar_entry(linha_tamanhos, 16)
    estado_interface["entrada_tamanho_max"].grid(row=1, column=1, sticky="ew", padx=(8, 0))
    linha_tamanhos.columnconfigure(0, weight=1)
    linha_tamanhos.columnconfigure(1, weight=1)
    return linha_tamanhos


def _criar_area_datas(container, estado_interface):
    """Cria os campos de data minima e maxima de modificacao."""
    linha_datas = ctk.CTkFrame(container, fg_color="transparent")
    linha_datas.pack(fill="x", padx=8, pady=4)
    criar_label(linha_datas, "Data mod. min").grid(row=0, column=0, sticky="w")
    criar_label(linha_datas, "Data mod. max").grid(row=0, column=1, sticky="w", padx=(8, 0))
    estado_interface["entrada_data_min"] = criar_entry(linha_datas, 16)
    estado_interface["entrada_data_min"].grid(row=1, column=0, sticky="ew")
    estado_interface["entrada_data_max"] = criar_entry(linha_datas, 16)
    estado_interface["entrada_data_max"].grid(row=1, column=1, sticky="ew", padx=(8, 0))
    linha_datas.columnconfigure(0, weight=1)
    linha_datas.columnconfigure(1, weight=1)
    return linha_datas


def atualizar_checkboxes_extensoes(estado_interface, extensoes_marcadas=None):
    """Recria a lista de checkboxes de extensoes disponiveis."""
    frame = estado_interface.get("frame_extensoes")
    if frame is None:
        return ERRO_DADOS_INVALIDOS

    if extensoes_marcadas is None:
        extensoes_marcadas = _obter_extensoes_marcadas(estado_interface)

    for widget in frame.winfo_children():
        widget.destroy()

    codigo, extensoes = controller.obter_extensoes_disponiveis()
    if codigo != OK:
        _mostrar_mensagem_resultado(codigo)
        return codigo

    estado_interface["extensoes_vars"] = {}
    extensoes_marcadas = set(extensoes_marcadas)

    for indice, extensao in enumerate(extensoes):
        var = tk.BooleanVar(value=extensao in extensoes_marcadas)
        estado_interface["extensoes_vars"][extensao] = var
        checkbox = ctk.CTkCheckBox(
            frame,
            text=extensao,
            variable=var,
            text_color=COR_TEXTO,
            fg_color=COR_AZUL,
            hover_color="#1d4ed8",
            border_color=COR_BORDA,
            font=FONTE_PADRAO,
        )
        checkbox.grid(row=indice // 3, column=indice % 3, sticky="w", padx=8, pady=4)

    for coluna in range(3):
        frame.columnconfigure(coluna, weight=1)
    return OK


def _adicionar_extensao_interface(estado_interface):
    """Adiciona uma extensao customizada a lista disponivel e a marca."""
    entrada = estado_interface.get("entrada_nova_extensao")
    if entrada is None:
        return ERRO_DADOS_INVALIDOS

    extensao = entrada.get()
    extensoes_marcadas = _obter_extensoes_marcadas(estado_interface)
    codigo = controller.adicionar_extensao_disponivel(extensao)
    if codigo != OK:
        _mostrar_mensagem_resultado(codigo)
        return codigo

    extensao_normalizada = controller.normalizar_extensao(extensao)
    if extensao_normalizada and extensao_normalizada not in extensoes_marcadas:
        extensoes_marcadas.append(extensao_normalizada)

    entrada.delete(0, tk.END)
    atualizar_checkboxes_extensoes(estado_interface, extensoes_marcadas)
    return OK


def _adicionar_regra_nome_interface(estado_interface, ao_alterar_restricoes=None):
    """Adiciona uma regra de nome na memoria visual do tipo atual."""
    entrada = estado_interface.get("entrada_regra_nome")
    if entrada is None:
        return ERRO_DADOS_INVALIDOS

    valor = entrada.get().strip()
    if not valor:
        return ERRO_DADOS_INVALIDOS

    regras = _obter_regras_nome_interface(estado_interface)
    regra = perfil_manager.criar_regra_nome(valor, _obter_modo_regra_nome_interface(estado_interface))
    if regra not in regras:
        regras.append(regra)

    entrada.delete(0, tk.END)
    atualizar_lista_regras_nome(estado_interface, regras)
    _executar_callback(ao_alterar_restricoes)
    return OK


def _remover_regra_nome_interface(estado_interface, ao_alterar_restricoes=None):
    """Remove a regra de nome selecionada da memoria visual."""
    lista = estado_interface.get("lista_regras_nome")
    if lista is None:
        return ERRO_DADOS_INVALIDOS

    selecao = lista.curselection()
    if not selecao:
        return ERRO_DADOS_INVALIDOS

    regras = _obter_regras_nome_interface(estado_interface)
    indice = selecao[0]
    if 0 <= indice < len(regras):
        regras.pop(indice)

    atualizar_lista_regras_nome(estado_interface, regras)
    _executar_callback(ao_alterar_restricoes)
    return OK


def atualizar_lista_regras_nome(estado_interface, regras):
    """Atualiza a listbox de regras de nome e o estado correspondente."""
    regras = _normalizar_regras_nome_interface(regras)
    estado_interface["regras_nome"] = regras
    lista = estado_interface.get("lista_regras_nome")
    if lista is None:
        return ERRO_DADOS_INVALIDOS

    lista.delete(0, tk.END)
    for regra in regras:
        lista.insert(tk.END, _formatar_regra_nome_interface(regra))
    return OK


def _obter_regras_nome_interface(estado_interface):
    """Retorna uma copia normalizada das regras de nome em memoria."""
    return _normalizar_regras_nome_interface(estado_interface.get("regras_nome", []))


def _normalizar_regras_nome_interface(regras):
    """Normaliza regras de nome para persistencia no perfil."""
    if not isinstance(regras, list):
        return []

    normalizadas = []
    for regra in regras:
        valor = perfil_manager.obter_valor_regra_nome(regra)
        if not isinstance(valor, str) or not valor.strip():
            continue
        normalizadas.append(
            perfil_manager.criar_regra_nome(
                valor.strip(),
                perfil_manager.obter_modo_regra_nome(regra),
            )
        )
    return normalizadas


def _obter_regras_nome_das_restricoes(restricoes):
    """Extrai regras de nome salvas no formato atual."""
    return _normalizar_regras_nome_interface(perfil_manager.obter_regras_nome_restricoes(restricoes))


def _obter_modo_regra_nome_interface(estado_interface):
    """Retorna o modo selecionado para uma nova regra de nome."""
    modo = estado_interface.get("modo_regra_nome_var")
    if modo is not None and modo.get() == "Nome completo":
        return "exato"
    return "contem"


def _formatar_regra_nome_interface(regra):
    """Formata uma regra de nome para exibicao em listbox."""
    rotulo = "Nome completo" if perfil_manager.obter_modo_regra_nome(regra) == "exato" else "Contém"
    return rotulo + ": " + perfil_manager.obter_valor_regra_nome(regra)


def criar_restricoes_da_interface(estado_interface):
    """Monta o dicionario de restricoes a partir dos campos da tela."""
    tamanho_min = converter_inteiro_opcional(estado_interface["entrada_tamanho_min"].get(), 0)
    tamanho_max = converter_inteiro_opcional(estado_interface["entrada_tamanho_max"].get(), None)
    data_min = converter_data_opcional(estado_interface["entrada_data_min"].get())
    data_max = converter_data_opcional(estado_interface["entrada_data_max"].get())
    return perfil_manager.criar_restricoes(
        _obter_extensoes_marcadas(estado_interface),
        _obter_regras_nome_interface(estado_interface),
        0 if tamanho_min == "invalido" else tamanho_min,
        None if tamanho_max == "invalido" else tamanho_max,
        None if data_min == "invalido" else data_min,
        None if data_max == "invalido" else data_max,
    )


def _obter_restricoes_do_tipo(tipo):
    """Retorna restricoes do tipo no formato atual."""
    return perfil_manager.obter_restricoes_tipo(tipo)


def preencher_formulario_com_tipo(estado_interface, tipo, atualizar_destinos_callback=None):
    """Carrega no painel de restricoes os dados de um tipo selecionado."""
    if tipo is None:
        return ERRO_DADOS_INVALIDOS
    _preencher_entry(estado_interface["entrada_tipo_nome"], perfil_manager.obter_nome_tipo(tipo))
    restricoes = _obter_restricoes_do_tipo(tipo)
    atualizar_checkboxes_extensoes(estado_interface, perfil_manager.obter_extensoes_restricoes(restricoes))
    atualizar_lista_regras_nome(estado_interface, _obter_regras_nome_das_restricoes(restricoes))
    _preencher_entry(estado_interface["entrada_tamanho_min"], str(perfil_manager.obter_tamanho_min_restricoes(restricoes)))
    tamanho_max = perfil_manager.obter_tamanho_max_restricoes(restricoes)
    _preencher_entry(estado_interface["entrada_tamanho_max"], "" if tamanho_max is None else str(tamanho_max))
    _preencher_entry(estado_interface["entrada_data_min"], perfil_manager.obter_data_min_restricoes(restricoes) or "")
    _preencher_entry(estado_interface["entrada_data_max"], perfil_manager.obter_data_max_restricoes(restricoes) or "")
    _executar_callback(atualizar_destinos_callback)
    return OK


def limpar_area_tipo_destino(estado_interface):
    """Limpa campos relacionados ao tipo e seus destinos."""
    _preencher_entry(estado_interface["entrada_tipo_nome"], "")
    atualizar_checkboxes_extensoes(estado_interface, [])
    atualizar_lista_regras_nome(estado_interface, [])
    _preencher_entry(estado_interface["entrada_tamanho_min"], "")
    _preencher_entry(estado_interface["entrada_tamanho_max"], "")
    _preencher_entry(estado_interface["entrada_data_min"], "")
    _preencher_entry(estado_interface["entrada_data_max"], "")
    estado_interface["lista_destinos"].delete(0, tk.END)
    return OK


def formulario_tipo_possui_valor_invalido(estado_interface):
    """Indica se algum filtro numerico ou de data do tipo atual e invalido."""
    tamanho_min = converter_inteiro_opcional(estado_interface["entrada_tamanho_min"].get(), 0)
    tamanho_max = converter_inteiro_opcional(estado_interface["entrada_tamanho_max"].get(), None)
    data_min = converter_data_opcional(estado_interface["entrada_data_min"].get())
    data_max = converter_data_opcional(estado_interface["entrada_data_max"].get())
    return (
        tamanho_min == "invalido"
        or tamanho_max == "invalido"
        or data_min == "invalido"
        or data_max == "invalido"
    )


def _obter_extensoes_marcadas(estado_interface):
    """Retorna as extensoes marcadas no painel de checkboxes."""
    extensoes = []
    for extensao, var in estado_interface.get("extensoes_vars", {}).items():
        if var.get():
            extensoes.append(extensao)
    return extensoes


def _preencher_entry(entrada, valor):
    entrada.delete(0, tk.END)
    entrada.insert(0, valor)
    return OK


def _executar_callback(callback):
    if callable(callback):
        return callback()
    return OK


def _mostrar_mensagem_resultado(codigo):
    mensagem = obter_mensagem(codigo)
    if codigo == OK:
        messagebox.showinfo("BackupManager", mensagem)
    else:
        messagebox.showerror("BackupManager", mensagem)
    return codigo
