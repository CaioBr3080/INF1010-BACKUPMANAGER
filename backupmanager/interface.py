"""Interface grafica do BackupManager usando tkinter e customtkinter."""

import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
from datetime import datetime

import customtkinter as ctk

from backupmanager import controller
from backupmanager.return_codes import OK, ERRO_DADOS_INVALIDOS, obter_mensagem

COR_FUNDO = "#0b1120"
COR_PAINEL = "#111827"
COR_PAINEL_2 = "#172033"
COR_CAMPO = "#0f172a"
COR_BORDA = "#273449"
COR_TEXTO = "#e5e7eb"
COR_TEXTO_FRACO = "#94a3b8"
COR_AZUL = "#2563eb"
COR_VERDE = "#059669"
COR_VERMELHO = "#dc2626"

FONTE_FAMILIA = "Segoe UI"
FONTE_PADRAO = (FONTE_FAMILIA, 10)
FONTE_TITULO = (FONTE_FAMILIA, 28, "bold")
FONTE_SECAO = (FONTE_FAMILIA, 13, "bold")


def iniciar_interface():
    """Inicia a interface grafica."""
    codigo = controller.inicializar_aplicacao()
    if codigo != OK:
        mostrar_mensagem_resultado(codigo)

    estado_interface = criar_estado_interface()
    janela = criar_janela_principal()
    estado_interface["janela"] = janela
    trazer_janela_para_frente(janela)

    def ao_fechar():
        sincronizar_perfil_atual_interface(estado_interface, False)
        codigo_finalizar = controller.finalizar_aplicacao()
        if codigo_finalizar != OK:
            mostrar_mensagem_resultado(codigo_finalizar)
            return
        janela.destroy()

    estado_interface["acao_fechar"] = ao_fechar
    janela.protocol("WM_DELETE_WINDOW", ao_fechar)

    cabecalho = ctk.CTkFrame(janela, fg_color="transparent")
    cabecalho.pack(fill="x", padx=18, pady=(16, 0))
    cabecalho.columnconfigure(0, weight=1)
    cabecalho.columnconfigure(1, weight=0)

    bloco_titulo = ctk.CTkFrame(cabecalho, fg_color="transparent")
    bloco_titulo.grid(row=0, column=0, sticky="w")
    ctk.CTkLabel(bloco_titulo, text="BackupManager", text_color=COR_TEXTO, font=FONTE_TITULO).pack(anchor="w")
    ctk.CTkLabel(
        bloco_titulo,
        text="Perfis, rotinas locais e persistencia em memoria",
        text_color=COR_TEXTO_FRACO,
        font=ctk.CTkFont(family=FONTE_FAMILIA, size=12),
    ).pack(anchor="w", pady=(2, 0))
    criar_area_botoes(cabecalho, estado_interface)

    criar_area_perfis(janela, estado_interface)

    frame_central = ctk.CTkFrame(janela, fg_color="transparent")
    configurar_frame(frame_central)
    frame_central.pack(fill="both", expand=True, padx=18)

    criar_area_origens_destinos(frame_central, estado_interface)
    criar_area_restricoes(frame_central, estado_interface)
    atualizar_lista_perfis(estado_interface)

    janela.mainloop()


def criar_estado_interface():
    """Cria o dicionario de estado da interface."""
    return {
        "janela": None,
        "acao_fechar": None,
        "ids_perfis": [],
        "lista_perfis": None,
        "entrada_nome": None,
        "lista_origens": None,
        "lista_tipos": None,
        "lista_destinos": None,
        "entrada_tipo_nome": None,
        "operacao_var": None,
        "destino_selecionado_indice": None,
        "ativo_var": None,
        "frame_extensoes": None,
        "extensoes_vars": {},
        "entrada_nova_extensao": None,
        "entrada_nome_contem": None,
        "entrada_tamanho_min": None,
        "entrada_tamanho_max": None,
        "entrada_data_min": None,
        "entrada_data_max": None,
        "agendamento_tipo_var": None,
        "entrada_intervalo": None,
        "perfil_selecionado_id": None,
        "origens_configuradas": [],
        "origem_selecionada_indice": None,
        "tipo_selecionado_indice": None,
        "botao_backup": None,
        "backup_em_execucao": False,
    }


def criar_janela_principal():
    """Cria a janela principal."""
    configurar_estilo_visual()
    janela = ctk.CTk()
    janela.title("BackupManager")
    janela.geometry("1180x720")
    janela.minsize(980, 620)
    janela.configure(fg_color=COR_FUNDO)
    return janela


def trazer_janela_para_frente(janela):
    """Traz a janela principal para frente ao iniciar sem fixa-la no topo."""
    janela.lift()
    janela.focus_force()
    janela.attributes("-topmost", True)
    janela.after(700, lambda: janela.attributes("-topmost", False))
    return OK


def manter_janela_acima_da_principal(janela_filha, janela_principal):
    """Mantem uma janela secundaria acima da janela principal."""
    if janela_principal is not None:
        janela_filha.transient(janela_principal)

    janela_filha.lift(janela_principal)
    janela_filha.focus_force()
    janela_filha.attributes("-topmost", True)
    return OK


def configurar_estilo_visual():
    """Configura aparencia geral do customtkinter."""
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    return OK


def configurar_frame(frame):
    """Aplica cores padrao em um frame."""
    frame.configure(fg_color="transparent")
    return frame


def criar_painel(container, titulo):
    """Cria um painel visual padronizado."""
    frame = ctk.CTkFrame(
        container,
        fg_color=COR_PAINEL,
        border_color=COR_BORDA,
        border_width=1,
        corner_radius=8,
    )
    ctk.CTkLabel(frame, text=titulo, text_color=COR_TEXTO, font=FONTE_SECAO).pack(
        anchor="w", padx=14, pady=(12, 6)
    )
    return frame


def criar_label(container, texto):
    """Cria um label padronizado."""
    return ctk.CTkLabel(container, text=texto, text_color=COR_TEXTO_FRACO, font=FONTE_PADRAO)


def criar_entry(container, largura=None):
    """Cria um campo de texto padronizado."""
    return ctk.CTkEntry(
        container,
        width=largura or 140,
        height=34,
        fg_color=COR_CAMPO,
        border_color=COR_BORDA,
        text_color=COR_TEXTO,
        corner_radius=6,
        font=FONTE_PADRAO,
    )


def criar_botao(container, texto, comando, cor=COR_PAINEL_2, texto_cor=COR_TEXTO, largura=None):
    """Cria um botao padronizado."""
    hover = COR_AZUL if cor != COR_AZUL else "#1d4ed8"
    if cor == COR_VERDE:
        hover = "#047857"
    if cor == COR_VERMELHO:
        hover = "#b91c1c"
    if cor == "#e5e7eb":
        hover = "#d1d5db"

    return ctk.CTkButton(
        container,
        text=texto,
        command=comando,
        fg_color=cor,
        hover_color=hover,
        text_color=texto_cor,
        width=largura or 140,
        height=34,
        corner_radius=6,
        font=FONTE_PADRAO,
    )


def adicionar_tooltip(widget, texto):
    """Adiciona tooltip simples a um widget."""
    tooltip = {"janela": None}

    def mostrar(evento):
        del evento
        if tooltip["janela"] is not None:
            return

        janela = tk.Toplevel(widget)
        janela.wm_overrideredirect(True)
        janela.configure(bg=COR_BORDA)
        x = widget.winfo_rootx()
        y = widget.winfo_rooty() + widget.winfo_height() + 6
        janela.wm_geometry("+" + str(x) + "+" + str(y))
        tk.Label(
            janela,
            text=texto,
            bg=COR_PAINEL,
            fg=COR_TEXTO,
            relief="solid",
            bd=1,
            padx=8,
            pady=4,
            font=FONTE_PADRAO,
        ).pack()
        tooltip["janela"] = janela

    def ocultar(evento):
        del evento
        if tooltip["janela"] is not None:
            tooltip["janela"].destroy()
            tooltip["janela"] = None

    widget.bind("<Enter>", mostrar)
    widget.bind("<Leave>", ocultar)
    widget.bind("<ButtonPress>", ocultar)
    return widget


def criar_listbox(container, altura):
    """Cria uma listbox padronizada."""
    return tk.Listbox(
        container,
        height=altura,
        exportselection=False,
        bg=COR_CAMPO,
        fg=COR_TEXTO,
        selectbackground=COR_AZUL,
        selectforeground="#ffffff",
        relief="solid",
        bd=1,
        highlightthickness=1,
        highlightbackground=COR_BORDA,
        highlightcolor=COR_AZUL,
        font=FONTE_PADRAO,
    )


def criar_area_perfis(janela, estado_interface):
    """Cria a area de perfis."""
    frame = criar_painel(janela, "Perfis")
    frame.pack(fill="x", padx=8, pady=8)

    linha_nome = ctk.CTkFrame(frame, fg_color="transparent")
    linha_nome.pack(fill="x", padx=8, pady=(8, 4))

    criar_label(linha_nome, "Nome").pack(side="left")
    estado_interface["entrada_nome"] = criar_entry(linha_nome)
    estado_interface["entrada_nome"].pack(side="left", fill="x", expand=True, padx=8)

    criar_botao(linha_nome, "Criar perfil", lambda: criar_perfil_interface(estado_interface), COR_AZUL).pack(
        side="left"
    )

    estado_interface["lista_perfis"] = criar_listbox(frame, 6)
    estado_interface["lista_perfis"].pack(fill="x", padx=8, pady=4)
    estado_interface["lista_perfis"].bind(
        "<<ListboxSelect>>",
        lambda evento: selecionar_perfil_interface(estado_interface),
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
        lambda: excluir_perfil_interface(estado_interface),
        COR_VERMELHO,
    ).pack(
        side="right"
    )

    return frame


def criar_area_origens_destinos(janela, estado_interface):
    """Cria a area do fluxo origem -> tipo -> destino."""
    frame = criar_painel(janela, "Fluxo de backup")
    frame.pack(fill="both", expand=True, side="left", padx=(0, 4), pady=8)

    conteudo = ctk.CTkFrame(frame, fg_color="transparent")
    conteudo.pack(fill="both", expand=True, padx=8, pady=(0, 8))
    conteudo.columnconfigure(0, weight=1)
    conteudo.columnconfigure(1, weight=1)
    conteudo.columnconfigure(2, weight=1)
    conteudo.rowconfigure(0, weight=1)

    coluna_origens = ctk.CTkFrame(conteudo, fg_color="transparent")
    coluna_origens.grid(row=0, column=0, sticky="nsew", padx=(0, 4))
    coluna_origens.columnconfigure(0, weight=1)
    coluna_origens.rowconfigure(1, weight=1)
    criar_label(coluna_origens, "Origens").grid(row=0, column=0, sticky="w")
    estado_interface["lista_origens"] = criar_listbox(coluna_origens, 10)
    estado_interface["lista_origens"].grid(row=1, column=0, sticky="nsew", pady=4)
    estado_interface["lista_origens"].bind(
        "<<ListboxSelect>>",
        lambda evento: selecionar_origem_configurada_interface(estado_interface),
    )

    linha_origens = ctk.CTkFrame(coluna_origens, fg_color="transparent")
    linha_origens.grid(row=2, column=0, sticky="ew")
    criar_botao(linha_origens, "Adicionar origem", lambda: adicionar_origem_interface(estado_interface), COR_AZUL).pack(
        side="left"
    )
    criar_botao(linha_origens, "Remover origem", lambda: remover_origem_configurada_interface(estado_interface)).pack(
        side="left", padx=6
    )
    criar_botao(
        linha_origens,
        "On/Off",
        lambda: alternar_origem_ativa_interface(estado_interface),
        largura=72,
    ).pack(side="left")
    botao_abrir_origem = criar_botao(
        linha_origens,
        "\U0001F4C1",
        lambda: abrir_origem_selecionada_interface(estado_interface),
        largura=42,
    )
    botao_abrir_origem.pack(side="left")
    adicionar_tooltip(botao_abrir_origem, "Abrir pasta de origem")

    coluna_tipos = ctk.CTkFrame(conteudo, fg_color="transparent")
    coluna_tipos.grid(row=0, column=1, sticky="nsew", padx=4)
    coluna_tipos.columnconfigure(0, weight=1)
    coluna_tipos.rowconfigure(2, weight=1)
    criar_label(coluna_tipos, "Tipos da origem").grid(row=0, column=0, sticky="w")
    estado_interface["entrada_tipo_nome"] = criar_entry(coluna_tipos)
    estado_interface["entrada_tipo_nome"].grid(row=1, column=0, sticky="ew", pady=4)
    estado_interface["lista_tipos"] = criar_listbox(coluna_tipos, 10)
    estado_interface["lista_tipos"].grid(row=2, column=0, sticky="nsew", pady=(0, 4))
    estado_interface["lista_tipos"].bind(
        "<<ListboxSelect>>",
        lambda evento: selecionar_tipo_arquivo_interface(estado_interface),
    )
    linha_tipos = ctk.CTkFrame(coluna_tipos, fg_color="transparent")
    linha_tipos.grid(row=3, column=0, sticky="ew")
    criar_botao(linha_tipos, "Adicionar tipo", lambda: adicionar_tipo_arquivo_interface(estado_interface), COR_AZUL).pack(
        side="left"
    )
    criar_botao(linha_tipos, "Remover tipo", lambda: remover_tipo_arquivo_interface(estado_interface)).pack(
        side="left", padx=6
    )
    criar_botao(
        linha_tipos,
        "On/Off",
        lambda: alternar_tipo_ativo_interface(estado_interface),
        largura=72,
    ).pack(side="left")

    coluna_destinos = ctk.CTkFrame(conteudo, fg_color="transparent")
    coluna_destinos.grid(row=0, column=2, sticky="nsew", padx=(4, 0))
    coluna_destinos.columnconfigure(0, weight=1)
    coluna_destinos.rowconfigure(1, weight=1)
    criar_label(coluna_destinos, "Destinos do tipo").grid(row=0, column=0, sticky="w")
    estado_interface["lista_destinos"] = criar_listbox(coluna_destinos, 10)
    estado_interface["lista_destinos"].grid(row=1, column=0, sticky="nsew", pady=4)
    estado_interface["lista_destinos"].bind(
        "<<ListboxSelect>>",
        lambda evento: selecionar_destino_tipo_interface(estado_interface),
    )

    linha_destinos = ctk.CTkFrame(coluna_destinos, fg_color="transparent")
    linha_destinos.grid(row=2, column=0, sticky="ew")
    criar_botao(linha_destinos, "Adicionar destino", lambda: adicionar_destino_interface(estado_interface), COR_AZUL).pack(
        side="left"
    )
    criar_botao(
        linha_destinos,
        "Remover destino",
        lambda: remover_destino_tipo_interface(estado_interface),
    ).pack(side="left", padx=6)
    botao_abrir_destino = criar_botao(
        linha_destinos,
        "\U0001F4C1",
        lambda: abrir_destino_selecionado_interface(estado_interface),
        largura=42,
    )
    botao_abrir_destino.pack(side="left")
    adicionar_tooltip(botao_abrir_destino, "Abrir pasta de destino")

    estado_interface["operacao_var"] = tk.StringVar(value="copiar")
    linha_operacao = ctk.CTkFrame(coluna_destinos, fg_color="transparent")
    linha_operacao.grid(row=3, column=0, sticky="ew", pady=(8, 0))
    criar_label(linha_operacao, "Operacao").pack(side="left")
    ctk.CTkRadioButton(
        linha_operacao,
        text="Copiar",
        variable=estado_interface["operacao_var"],
        value="copiar",
        command=lambda: atualizar_operacao_destino_interface(estado_interface),
        text_color=COR_TEXTO,
        fg_color=COR_AZUL,
        hover_color="#1d4ed8",
        font=FONTE_PADRAO,
    ).pack(
        side="left", padx=8
    )
    ctk.CTkRadioButton(
        linha_operacao,
        text="Mover",
        variable=estado_interface["operacao_var"],
        value="mover",
        command=lambda: atualizar_operacao_destino_interface(estado_interface),
        text_color=COR_TEXTO,
        fg_color=COR_AZUL,
        hover_color="#1d4ed8",
        font=FONTE_PADRAO,
    ).pack(
        side="left"
    )
    ctk.CTkRadioButton(
        linha_operacao,
        text="Recortar",
        variable=estado_interface["operacao_var"],
        value="recortar",
        command=lambda: atualizar_operacao_destino_interface(estado_interface),
        text_color=COR_TEXTO,
        fg_color=COR_AZUL,
        hover_color="#1d4ed8",
        font=FONTE_PADRAO,
    ).pack(
        side="left", padx=8
    )

    return frame


def criar_area_extensoes(container, estado_interface):
    """Cria area de selecao de extensoes por checkbox."""
    criar_label(container, "Extensoes permitidas").pack(anchor="w", padx=8, pady=(8, 0))

    linha_adicionar = ctk.CTkFrame(container, fg_color="transparent")
    linha_adicionar.pack(fill="x", padx=8, pady=(4, 4))
    estado_interface["entrada_nova_extensao"] = criar_entry(linha_adicionar)
    estado_interface["entrada_nova_extensao"].pack(side="left", fill="x", expand=True)
    criar_botao(
        linha_adicionar,
        "Adicionar",
        lambda: adicionar_extensao_interface(estado_interface),
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


def atualizar_checkboxes_extensoes(estado_interface, extensoes_marcadas=None):
    """Atualiza checkboxes de extensoes disponiveis."""
    frame = estado_interface.get("frame_extensoes")
    if frame is None:
        return ERRO_DADOS_INVALIDOS

    if extensoes_marcadas is None:
        extensoes_marcadas = obter_extensoes_marcadas(estado_interface)

    for widget in frame.winfo_children():
        widget.destroy()

    codigo, extensoes = controller.obter_extensoes_disponiveis()
    if codigo != OK:
        mostrar_mensagem_resultado(codigo)
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


def criar_area_restricoes(janela, estado_interface):
    """Cria a area de restricoes e agendamento."""
    frame = criar_painel(janela, "Restricoes e agendamento")
    frame.pack(fill="both", expand=True, side="right", padx=(4, 0), pady=8)

    criar_area_extensoes(frame, estado_interface)

    criar_label(frame, "Nome contem").pack(anchor="w", padx=8)
    estado_interface["entrada_nome_contem"] = criar_entry(frame)
    estado_interface["entrada_nome_contem"].pack(fill="x", padx=8, pady=4)

    linha_tamanhos = ctk.CTkFrame(frame, fg_color="transparent")
    linha_tamanhos.pack(fill="x", padx=8, pady=4)
    criar_label(linha_tamanhos, "Tamanho min").grid(row=0, column=0, sticky="w")
    criar_label(linha_tamanhos, "Tamanho max").grid(row=0, column=1, sticky="w", padx=(8, 0))
    estado_interface["entrada_tamanho_min"] = criar_entry(linha_tamanhos, 16)
    estado_interface["entrada_tamanho_min"].grid(row=1, column=0, sticky="ew")
    estado_interface["entrada_tamanho_max"] = criar_entry(linha_tamanhos, 16)
    estado_interface["entrada_tamanho_max"].grid(row=1, column=1, sticky="ew", padx=(8, 0))
    linha_tamanhos.columnconfigure(0, weight=1)
    linha_tamanhos.columnconfigure(1, weight=1)

    linha_datas = ctk.CTkFrame(frame, fg_color="transparent")
    linha_datas.pack(fill="x", padx=8, pady=4)
    criar_label(linha_datas, "Data mod. min").grid(row=0, column=0, sticky="w")
    criar_label(linha_datas, "Data mod. max").grid(row=0, column=1, sticky="w", padx=(8, 0))
    estado_interface["entrada_data_min"] = criar_entry(linha_datas, 16)
    estado_interface["entrada_data_min"].grid(row=1, column=0, sticky="ew")
    estado_interface["entrada_data_max"] = criar_entry(linha_datas, 16)
    estado_interface["entrada_data_max"].grid(row=1, column=1, sticky="ew", padx=(8, 0))
    linha_datas.columnconfigure(0, weight=1)
    linha_datas.columnconfigure(1, weight=1)

    estado_interface["agendamento_tipo_var"] = tk.StringVar(value="manual")
    criar_label(frame, "Agendamento").pack(anchor="w", padx=8, pady=(8, 0))
    combo = ctk.CTkComboBox(
        frame,
        variable=estado_interface["agendamento_tipo_var"],
        values=("manual", "intervalo", "alteracao"),
        fg_color=COR_CAMPO,
        border_color=COR_BORDA,
        button_color=COR_PAINEL_2,
        button_hover_color=COR_AZUL,
        dropdown_fg_color=COR_PAINEL,
        dropdown_hover_color=COR_AZUL,
        text_color=COR_TEXTO,
        dropdown_text_color=COR_TEXTO,
        height=34,
        corner_radius=6,
        font=FONTE_PADRAO,
    )
    combo.pack(fill="x", padx=8, pady=4)

    criar_label(frame, "Intervalo em minutos").pack(anchor="w", padx=8)
    estado_interface["entrada_intervalo"] = criar_entry(frame)
    estado_interface["entrada_intervalo"].pack(fill="x", padx=8, pady=4)

    return frame


def criar_area_botoes(janela, estado_interface):
    """Cria os botoes principais da interface."""
    frame = ctk.CTkFrame(janela, fg_color="transparent")
    frame.grid(row=0, column=1, sticky="ne", padx=(12, 0), pady=(6, 0))

    estado_interface["botao_backup"] = criar_botao(
        frame,
        "Backup",
        lambda: executar_backup_interface(estado_interface),
        COR_VERDE,
        largura=92,
    )
    estado_interface["botao_backup"].pack(side="left", padx=(0, 6))
    criar_botao(
        frame,
        "Historico",
        lambda: mostrar_historico_interface(estado_interface),
        largura=92,
    ).pack(
        side="left", padx=6
    )
    criar_botao(frame, "Sair", estado_interface["acao_fechar"], "#e5e7eb", "#111827", largura=76).pack(
        side="left", padx=(6, 0)
    )
    return frame


def atualizar_lista_perfis(estado_interface):
    """Atualiza a lista visual de perfis."""
    codigo, perfis = controller.obter_perfis()
    if codigo != OK:
        mostrar_mensagem_resultado(codigo)
        return codigo

    lista = estado_interface["lista_perfis"]
    lista.delete(0, tk.END)
    estado_interface["ids_perfis"] = []

    for perfil in perfis:
        marcador = "ativo" if perfil.get("ativo", True) else "inativo"
        lista.insert(tk.END, perfil.get("nome", "Sem nome") + " (" + marcador + ")")
        estado_interface["ids_perfis"].append(perfil.get("id"))

    return codigo


def criar_perfil_interface(estado_interface):
    """Cria um perfil a partir do nome informado na interface."""
    nome = estado_interface["entrada_nome"].get()
    codigo, perfil = controller.criar_novo_perfil(nome)
    if codigo != OK:
        mostrar_mensagem_resultado(codigo)
        return codigo

    estado_interface["perfil_selecionado_id"] = perfil.get("id")
    atualizar_lista_perfis(estado_interface)
    selecionar_perfil_por_id(estado_interface, perfil.get("id"))
    mostrar_mensagem_resultado(codigo)
    return codigo


def selecionar_perfil_interface(estado_interface):
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


def selecionar_perfil_por_id(estado_interface, perfil_id):
    """Seleciona visualmente um perfil pelo id."""
    if perfil_id not in estado_interface["ids_perfis"]:
        return ERRO_DADOS_INVALIDOS

    indice = estado_interface["ids_perfis"].index(perfil_id)
    lista = estado_interface["lista_perfis"]
    lista.selection_clear(0, tk.END)
    lista.selection_set(indice)
    lista.activate(indice)
    return selecionar_perfil_interface(estado_interface)


def excluir_perfil_interface(estado_interface):
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


def adicionar_origem_interface(estado_interface):
    """Adiciona uma pasta de origem na lista visual."""
    salvar_tipo_selecionado_em_memoria(estado_interface)
    caminho = filedialog.askdirectory(title="Escolha a pasta de origem")
    if caminho:
        origem = {
            "id": "origem_" + str(len(estado_interface["origens_configuradas"]) + 1),
            "caminho": caminho,
            "ativo": True,
            "tipos_arquivo": [],
        }
        estado_interface["origens_configuradas"].append(origem)
        atualizar_lista_origens_configuradas(estado_interface)
        selecionar_origem_por_indice(estado_interface, len(estado_interface["origens_configuradas"]) - 1)
    return OK


def adicionar_destino_interface(estado_interface):
    """Adiciona uma pasta de destino ao tipo selecionado."""
    salvar_tipo_selecionado_em_memoria(estado_interface)
    tipo = obter_tipo_selecionado(estado_interface)
    if tipo is None:
        messagebox.showwarning("BackupManager", "Selecione um tipo de arquivo.")
        return ERRO_DADOS_INVALIDOS

    caminho = filedialog.askdirectory(title="Escolha a pasta de destino")
    if caminho:
        destino = {
            "caminho": caminho,
            "operacao": estado_interface["operacao_var"].get(),
        }
        tipo.setdefault("destinos", []).append(destino)
        atualizar_lista_destinos_tipo(estado_interface)
        selecionar_destino_por_indice(estado_interface, len(tipo["destinos"]) - 1)
    return OK


def adicionar_tipo_arquivo_interface(estado_interface):
    """Adiciona tipo de arquivo a origem selecionada."""
    salvar_tipo_selecionado_em_memoria(estado_interface)
    origem = obter_origem_selecionada(estado_interface)
    if origem is None:
        messagebox.showwarning("BackupManager", "Selecione uma origem.")
        return ERRO_DADOS_INVALIDOS

    tipo = {
        "id": "tipo_" + str(len(origem.get("tipos_arquivo", [])) + 1),
        "nome": "Novo tipo",
        "ativo": True,
        "restricoes": criar_restricoes_da_interface(estado_interface),
        "destinos": [],
    }
    origem.setdefault("tipos_arquivo", []).append(tipo)
    atualizar_lista_tipos_origem(estado_interface)
    selecionar_tipo_por_indice(estado_interface, len(origem["tipos_arquivo"]) - 1)
    return OK


def remover_origem_configurada_interface(estado_interface):
    """Remove origem configurada selecionada."""
    indice = estado_interface.get("origem_selecionada_indice")
    if indice is None:
        return ERRO_DADOS_INVALIDOS

    salvar_tipo_selecionado_em_memoria(estado_interface)
    origens = estado_interface["origens_configuradas"]
    if 0 <= indice < len(origens):
        origens.pop(indice)
    estado_interface["origem_selecionada_indice"] = None
    estado_interface["tipo_selecionado_indice"] = None
    estado_interface["destino_selecionado_indice"] = None
    atualizar_lista_origens_configuradas(estado_interface)
    limpar_area_tipo_destino(estado_interface)
    return OK


def remover_tipo_arquivo_interface(estado_interface):
    """Remove tipo de arquivo selecionado."""
    origem = obter_origem_selecionada(estado_interface)
    indice = estado_interface.get("tipo_selecionado_indice")
    if origem is None or indice is None:
        return ERRO_DADOS_INVALIDOS

    tipos = origem.get("tipos_arquivo", [])
    if 0 <= indice < len(tipos):
        tipos.pop(indice)
    estado_interface["tipo_selecionado_indice"] = None
    estado_interface["destino_selecionado_indice"] = None
    atualizar_lista_tipos_origem(estado_interface)
    limpar_area_tipo_destino(estado_interface)
    return OK


def remover_destino_tipo_interface(estado_interface):
    """Remove destino selecionado do tipo atual."""
    tipo = obter_tipo_selecionado(estado_interface)
    selecao = estado_interface["lista_destinos"].curselection()
    if tipo is None or not selecao:
        return ERRO_DADOS_INVALIDOS

    destinos = tipo.get("destinos", [])
    indice = selecao[0]
    if 0 <= indice < len(destinos):
        destinos.pop(indice)
    estado_interface["destino_selecionado_indice"] = None
    atualizar_lista_destinos_tipo(estado_interface)
    return OK


def alternar_origem_ativa_interface(estado_interface):
    """Liga ou desliga a origem selecionada."""
    origem = obter_origem_selecionada(estado_interface)
    if origem is None:
        return ERRO_DADOS_INVALIDOS

    origem["ativo"] = not origem.get("ativo", True)
    indice = estado_interface.get("origem_selecionada_indice")
    atualizar_lista_origens_configuradas(estado_interface)
    selecionar_origem_por_indice(estado_interface, indice)
    return OK


def alternar_tipo_ativo_interface(estado_interface):
    """Liga ou desliga o tipo selecionado."""
    tipo = obter_tipo_selecionado(estado_interface)
    if tipo is None:
        return ERRO_DADOS_INVALIDOS

    tipo["ativo"] = not tipo.get("ativo", True)
    indice = estado_interface.get("tipo_selecionado_indice")
    atualizar_lista_tipos_origem(estado_interface)
    selecionar_tipo_por_indice(estado_interface, indice)
    return OK


def adicionar_extensao_interface(estado_interface):
    """Adiciona extensao customizada a lista disponivel."""
    entrada = estado_interface.get("entrada_nova_extensao")
    if entrada is None:
        return ERRO_DADOS_INVALIDOS

    extensao = entrada.get()
    extensoes_marcadas = obter_extensoes_marcadas(estado_interface)
    codigo = controller.adicionar_extensao_disponivel(extensao)
    if codigo != OK:
        mostrar_mensagem_resultado(codigo)
        return codigo

    extensao_normalizada = controller.normalizar_extensao(extensao)
    if extensao_normalizada and extensao_normalizada not in extensoes_marcadas:
        extensoes_marcadas.append(extensao_normalizada)

    entrada.delete(0, tk.END)
    atualizar_checkboxes_extensoes(estado_interface, extensoes_marcadas)
    return OK


def remover_item_lista(lista):
    """Remove o item selecionado de uma listbox."""
    selecao = lista.curselection()
    if selecao:
        lista.delete(selecao[0])
    return OK


def abrir_pasta_selecionada(lista, tipo):
    """Abre a pasta selecionada em uma listbox."""
    selecao = lista.curselection()
    if not selecao:
        messagebox.showwarning("BackupManager", "Selecione uma pasta de " + tipo + ".")
        return ERRO_DADOS_INVALIDOS

    caminho = lista.get(selecao[0]).split(" | ")[0]
    if caminho.startswith("[x] ") or caminho.startswith("[ ] "):
        caminho = caminho[4:]
    return abrir_pasta_por_caminho(caminho, tipo)


def abrir_pasta_por_caminho(caminho, tipo):
    """Abre uma pasta pelo caminho informado."""
    if not os.path.isdir(caminho):
        messagebox.showerror("BackupManager", "Pasta de " + tipo + " nao encontrada.")
        return ERRO_DADOS_INVALIDOS

    try:
        os.startfile(caminho)
    except OSError:
        messagebox.showerror("BackupManager", "Nao foi possivel abrir a pasta de " + tipo + ".")
        return ERRO_DADOS_INVALIDOS

    return OK


def abrir_origem_selecionada_interface(estado_interface):
    """Abre a pasta da origem selecionada."""
    origem = obter_origem_selecionada(estado_interface)
    if origem is None:
        messagebox.showwarning("BackupManager", "Selecione uma pasta de origem.")
        return ERRO_DADOS_INVALIDOS
    return abrir_pasta_por_caminho(origem.get("caminho", ""), "origem")


def abrir_destino_selecionado_interface(estado_interface):
    """Abre a pasta do destino selecionado."""
    destino = obter_destino_selecionado(estado_interface)
    if destino is None:
        messagebox.showwarning("BackupManager", "Selecione uma pasta de destino.")
        return ERRO_DADOS_INVALIDOS
    return abrir_pasta_por_caminho(destino.get("caminho", ""), "destino")


def atualizar_lista_origens_configuradas(estado_interface):
    """Atualiza a listbox de origens configuradas."""
    lista = estado_interface["lista_origens"]
    lista.delete(0, tk.END)
    for origem in estado_interface["origens_configuradas"]:
        marcador = "[x] " if origem.get("ativo", True) else "[ ] "
        lista.insert(tk.END, marcador + origem.get("caminho", ""))
    return OK


def atualizar_lista_tipos_origem(estado_interface):
    """Atualiza tipos da origem selecionada."""
    lista = estado_interface["lista_tipos"]
    lista.delete(0, tk.END)
    origem = obter_origem_selecionada(estado_interface)
    if origem is None:
        return ERRO_DADOS_INVALIDOS

    for tipo in origem.get("tipos_arquivo", []):
        marcador = "[x] " if tipo.get("ativo", True) else "[ ] "
        lista.insert(tk.END, marcador + tipo.get("nome", "Sem nome"))
    return OK


def atualizar_lista_destinos_tipo(estado_interface):
    """Atualiza destinos do tipo selecionado."""
    lista = estado_interface["lista_destinos"]
    lista.delete(0, tk.END)
    estado_interface["destino_selecionado_indice"] = None
    tipo = obter_tipo_selecionado(estado_interface)
    if tipo is None:
        return ERRO_DADOS_INVALIDOS

    for destino in tipo.get("destinos", []):
        lista.insert(tk.END, destino.get("caminho", "") + " | " + destino.get("operacao", "copiar"))
    return OK


def selecionar_destino_tipo_interface(estado_interface):
    """Seleciona destino do tipo atual e carrega sua operacao."""
    selecao = estado_interface["lista_destinos"].curselection()
    if not selecao:
        return ERRO_DADOS_INVALIDOS

    estado_interface["destino_selecionado_indice"] = selecao[0]
    destino = obter_destino_selecionado(estado_interface)
    if destino is not None:
        estado_interface["operacao_var"].set(destino.get("operacao", "copiar"))
    return OK


def selecionar_destino_por_indice(estado_interface, indice):
    """Seleciona destino visualmente por indice."""
    lista = estado_interface["lista_destinos"]
    if indice < 0 or indice >= lista.size():
        return ERRO_DADOS_INVALIDOS
    lista.selection_clear(0, tk.END)
    lista.selection_set(indice)
    lista.activate(indice)
    return selecionar_destino_tipo_interface(estado_interface)


def obter_destino_selecionado(estado_interface):
    """Retorna destino selecionado do tipo atual."""
    tipo = obter_tipo_selecionado(estado_interface)
    indice = estado_interface.get("destino_selecionado_indice")
    if tipo is None or indice is None:
        return None
    destinos = tipo.get("destinos", [])
    if indice < 0 or indice >= len(destinos):
        return None
    return destinos[indice]


def atualizar_operacao_destino_interface(estado_interface):
    """Atualiza operacao do destino selecionado."""
    destino = obter_destino_selecionado(estado_interface)
    if destino is None:
        return OK

    destino["operacao"] = estado_interface["operacao_var"].get()
    indice = estado_interface.get("destino_selecionado_indice")
    atualizar_lista_destinos_tipo(estado_interface)
    selecionar_destino_por_indice(estado_interface, indice)
    return OK


def selecionar_origem_configurada_interface(estado_interface):
    """Seleciona origem e atualiza tipos relacionados."""
    salvar_tipo_selecionado_em_memoria(estado_interface)
    selecao = estado_interface["lista_origens"].curselection()
    if not selecao:
        return ERRO_DADOS_INVALIDOS

    estado_interface["origem_selecionada_indice"] = selecao[0]
    estado_interface["tipo_selecionado_indice"] = None
    estado_interface["destino_selecionado_indice"] = None
    atualizar_lista_tipos_origem(estado_interface)
    limpar_area_tipo_destino(estado_interface)

    origem = obter_origem_selecionada(estado_interface)
    if origem and origem.get("tipos_arquivo"):
        selecionar_tipo_por_indice(estado_interface, 0)
    return OK


def selecionar_tipo_arquivo_interface(estado_interface):
    """Seleciona tipo e carrega filtros e destinos."""
    salvar_tipo_selecionado_em_memoria(estado_interface)
    selecao = estado_interface["lista_tipos"].curselection()
    if not selecao:
        return ERRO_DADOS_INVALIDOS

    estado_interface["tipo_selecionado_indice"] = selecao[0]
    estado_interface["destino_selecionado_indice"] = None
    preencher_formulario_com_tipo(estado_interface, obter_tipo_selecionado(estado_interface))
    return OK


def selecionar_origem_por_indice(estado_interface, indice):
    """Seleciona origem visualmente por indice."""
    lista = estado_interface["lista_origens"]
    if indice < 0 or indice >= lista.size():
        return ERRO_DADOS_INVALIDOS
    lista.selection_clear(0, tk.END)
    lista.selection_set(indice)
    lista.activate(indice)
    return selecionar_origem_configurada_interface(estado_interface)


def selecionar_tipo_por_indice(estado_interface, indice):
    """Seleciona tipo visualmente por indice."""
    lista = estado_interface["lista_tipos"]
    if indice < 0 or indice >= lista.size():
        return ERRO_DADOS_INVALIDOS
    lista.selection_clear(0, tk.END)
    lista.selection_set(indice)
    lista.activate(indice)
    return selecionar_tipo_arquivo_interface(estado_interface)


def obter_origem_selecionada(estado_interface):
    """Retorna origem selecionada."""
    indice = estado_interface.get("origem_selecionada_indice")
    origens = estado_interface.get("origens_configuradas", [])
    if indice is None or indice < 0 or indice >= len(origens):
        return None
    return origens[indice]


def obter_tipo_selecionado(estado_interface):
    """Retorna tipo selecionado."""
    origem = obter_origem_selecionada(estado_interface)
    indice = estado_interface.get("tipo_selecionado_indice")
    if origem is None or indice is None:
        return None
    tipos = origem.get("tipos_arquivo", [])
    if indice < 0 or indice >= len(tipos):
        return None
    return tipos[indice]


def salvar_tipo_selecionado_em_memoria(estado_interface):
    """Salva campos de filtro no tipo selecionado."""
    tipo = obter_tipo_selecionado(estado_interface)
    if tipo is None:
        return OK

    nome = estado_interface["entrada_tipo_nome"].get().strip()
    if nome:
        tipo["nome"] = nome
    tipo["restricoes"] = criar_restricoes_da_interface(estado_interface)
    return OK


def criar_restricoes_da_interface(estado_interface):
    """Cria dicionario de restricoes a partir da interface."""
    tamanho_min = converter_inteiro_opcional(estado_interface["entrada_tamanho_min"].get(), 0)
    tamanho_max = converter_inteiro_opcional(estado_interface["entrada_tamanho_max"].get(), None)
    data_min = converter_data_opcional(estado_interface["entrada_data_min"].get())
    data_max = converter_data_opcional(estado_interface["entrada_data_max"].get())
    return {
        "extensoes_permitidas": obter_extensoes_marcadas(estado_interface),
        "nome_contem": estado_interface["entrada_nome_contem"].get().strip(),
        "tamanho_min": 0 if tamanho_min == "invalido" else tamanho_min,
        "tamanho_max": None if tamanho_max == "invalido" else tamanho_max,
        "data_modificacao_min": None if data_min == "invalido" else data_min,
        "data_modificacao_max": None if data_max == "invalido" else data_max,
    }


def preencher_formulario_com_tipo(estado_interface, tipo):
    """Preenche filtros e destinos com dados do tipo."""
    if tipo is None:
        return ERRO_DADOS_INVALIDOS
    preencher_entry(estado_interface["entrada_tipo_nome"], tipo.get("nome", ""))
    restricoes = tipo.get("restricoes", {})
    atualizar_checkboxes_extensoes(estado_interface, restricoes.get("extensoes_permitidas", []))
    preencher_entry(estado_interface["entrada_nome_contem"], restricoes.get("nome_contem", ""))
    preencher_entry(estado_interface["entrada_tamanho_min"], str(restricoes.get("tamanho_min", 0)))
    tamanho_max = restricoes.get("tamanho_max")
    preencher_entry(estado_interface["entrada_tamanho_max"], "" if tamanho_max is None else str(tamanho_max))
    preencher_entry(estado_interface["entrada_data_min"], restricoes.get("data_modificacao_min") or "")
    preencher_entry(estado_interface["entrada_data_max"], restricoes.get("data_modificacao_max") or "")
    atualizar_lista_destinos_tipo(estado_interface)
    return OK


def limpar_area_tipo_destino(estado_interface):
    """Limpa campos de tipo e destinos."""
    preencher_entry(estado_interface["entrada_tipo_nome"], "")
    atualizar_checkboxes_extensoes(estado_interface, [])
    preencher_entry(estado_interface["entrada_nome_contem"], "")
    preencher_entry(estado_interface["entrada_tamanho_min"], "")
    preencher_entry(estado_interface["entrada_tamanho_max"], "")
    preencher_entry(estado_interface["entrada_data_min"], "")
    preencher_entry(estado_interface["entrada_data_max"], "")
    estado_interface["lista_destinos"].delete(0, tk.END)
    return OK


def aplicar_alteracoes_interface(estado_interface):
    """Aplica alteracoes do formulario ao estado em memoria."""
    codigo, perfil = sincronizar_perfil_atual_interface(estado_interface, True)
    if codigo != OK:
        return codigo

    if codigo == OK:
        atualizar_lista_perfis(estado_interface)
        selecionar_perfil_por_id(estado_interface, perfil["id"])
    mostrar_mensagem_resultado(codigo)
    return codigo


def executar_backup_interface(estado_interface):
    """Executa o backup do perfil selecionado."""
    codigo_salvar, perfil = sincronizar_perfil_atual_interface(estado_interface, True)
    if codigo_salvar != OK:
        return codigo_salvar

    perfil_id = perfil.get("id")
    if not perfil_id:
        mostrar_mensagem_resultado(ERRO_DADOS_INVALIDOS)
        return ERRO_DADOS_INVALIDOS

    if estado_interface.get("backup_em_execucao"):
        return OK

    estado_interface["backup_em_execucao"] = True
    definir_estado_botao_backup(estado_interface, False)

    thread = threading.Thread(
        target=executar_backup_em_thread,
        args=(estado_interface, perfil_id),
        daemon=True,
    )
    thread.start()
    return OK


def executar_backup_em_thread(estado_interface, perfil_id):
    """Executa backup fora da thread da interface."""
    codigo = ERRO_DADOS_INVALIDOS
    resultado = None
    erro = None

    try:
        codigo, resultado = controller.executar_backup_do_perfil(perfil_id)
    except Exception as excecao:
        erro = excecao

    janela = estado_interface.get("janela")
    if janela is None:
        return

    try:
        janela.after(0, lambda: finalizar_backup_interface(estado_interface, codigo, resultado, erro))
    except tk.TclError:
        return


def finalizar_backup_interface(estado_interface, codigo, resultado, erro):
    """Atualiza a interface apos o termino do backup."""
    estado_interface["backup_em_execucao"] = False
    definir_estado_botao_backup(estado_interface, True)

    if erro is not None:
        messagebox.showerror("BackupManager", "Falha inesperada ao executar backup:\n" + str(erro))
        return ERRO_DADOS_INVALIDOS

    if resultado:
        mensagem = (
            obter_mensagem(codigo)
            + "\n\nArquivos processados: "
            + str(resultado.get("arquivos_processados", 0))
            + "\nCopiados: "
            + str(resultado.get("arquivos_copiados", 0))
            + "\nMovidos: "
            + str(resultado.get("arquivos_movidos", 0))
            + "\nRecortados: "
            + str(resultado.get("arquivos_recortados", 0))
        )
        if codigo == OK:
            messagebox.showinfo("BackupManager", mensagem)
        else:
            messagebox.showwarning("BackupManager", mensagem)
        return codigo

    mostrar_mensagem_resultado(codigo)
    return codigo


def definir_estado_botao_backup(estado_interface, habilitado):
    """Habilita ou desabilita o botao de backup."""
    botao = estado_interface.get("botao_backup")
    if botao is None:
        return OK

    if habilitado:
        botao.configure(text="Backup", state="normal")
    else:
        botao.configure(text="Executando", state="disabled")
    return OK


def mostrar_historico_interface(estado_interface):
    """Mostra o historico do perfil selecionado."""
    perfil_id = estado_interface.get("perfil_selecionado_id")
    if not perfil_id:
        mostrar_mensagem_resultado(ERRO_DADOS_INVALIDOS)
        return ERRO_DADOS_INVALIDOS

    codigo, historico = controller.consultar_historico_do_perfil(perfil_id)
    if codigo != OK:
        mostrar_mensagem_resultado(codigo)
        return codigo

    janela = ctk.CTkToplevel(estado_interface["janela"])
    janela.title("Historico do perfil")
    janela.geometry("860x480")
    janela.minsize(740, 380)
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
    corpo.columnconfigure(0, weight=2)
    corpo.columnconfigure(1, weight=1)
    corpo.rowconfigure(0, weight=1)

    lista = criar_listbox(corpo, 16)
    lista.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

    detalhes = ctk.CTkTextbox(
        corpo,
        fg_color=COR_CAMPO,
        border_color=COR_BORDA,
        border_width=1,
        text_color=COR_TEXTO,
        font=FONTE_PADRAO,
    )
    detalhes.grid(row=0, column=1, sticky="nsew")

    def preencher_historico():
        if not widgets_existem(janela, lista, detalhes):
            return

        codigo_atualizar, historico_atualizado = controller.consultar_historico_do_perfil(perfil_id)
        if codigo_atualizar != OK:
            mostrar_mensagem_resultado(codigo_atualizar)
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
        conteudo = (
            "Data: "
            + registro.get("data_hora", "")
            + "\nStatus: "
            + registro.get("status", "")
            + "\nProcessados: "
            + str(registro.get("arquivos_processados", 0))
            + "\nCopiados: "
            + str(registro.get("arquivos_copiados", 0))
            + "\nMovidos: "
            + str(registro.get("arquivos_movidos", 0))
            + "\nRecortados: "
            + str(registro.get("arquivos_recortados", 0))
            + "\nErros: "
            + str(len(erros))
        )
        arquivos = registro.get("arquivos", [])
        if arquivos:
            conteudo += "\n\nArquivos:\n"
            for arquivo in arquivos:
                conteudo += formatar_arquivo_historico(arquivo) + "\n"
        if erros:
            conteudo += "\n\nDetalhes dos erros:\n" + "\n".join(str(erro) for erro in erros)

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
        mostrar_mensagem_resultado(codigo_limpar)

    lista.bind("<<ListboxSelect>>", ao_selecionar)
    preencher_historico()

    linha_botoes = ctk.CTkFrame(janela, fg_color="transparent")
    linha_botoes.pack(fill="x", padx=14, pady=(0, 14))
    criar_botao(linha_botoes, "Limpar historico do perfil", limpar_historico, COR_VERMELHO).pack(side="left")
    criar_botao(linha_botoes, "Fechar", janela.destroy).pack(side="right")
    return OK


def widgets_existem(*widgets):
    """Indica se todos os widgets informados ainda existem no Tk."""
    try:
        return all(widget is not None and widget.winfo_exists() for widget in widgets)
    except tk.TclError:
        return False


def formatar_arquivo_historico(arquivo):
    """Formata um arquivo processado para exibicao no historico."""
    nome = arquivo.get("nome", "")
    tipo = arquivo.get("tipo") or arquivo.get("extensao") or "(sem tipo)"
    tamanho = str(arquivo.get("tamanho", 0))
    operacao = arquivo.get("operacao", "")
    status = arquivo.get("status", "")
    destino = arquivo.get("destino", "")
    return "- " + nome + " | " + tipo + " | " + tamanho + " bytes | " + operacao + " | " + status + " | " + destino


def visualizar_arquivos_interface(estado_interface):
    """Mostra os arquivos encontrados nas origens do perfil."""
    codigo, perfil = sincronizar_perfil_atual_interface(estado_interface, True)
    if codigo != OK:
        return codigo

    codigo, arquivos = controller.obter_arquivos_do_perfil(perfil["id"])
    if codigo != OK:
        mostrar_mensagem_resultado(codigo)
        return codigo

    janela = ctk.CTkToplevel(estado_interface["janela"])
    janela.title("Arquivos encontrados")
    janela.geometry("920x520")
    janela.minsize(760, 420)
    janela.configure(fg_color=COR_FUNDO)
    manter_janela_acima_da_principal(janela, estado_interface["janela"])

    ctk.CTkLabel(
        janela,
        text="Arquivos das origens",
        text_color=COR_TEXTO,
        font=FONTE_SECAO,
    ).pack(anchor="w", padx=14, pady=(14, 4))

    corpo = ctk.CTkFrame(janela, fg_color="transparent")
    corpo.pack(fill="both", expand=True, padx=14, pady=(4, 14))
    corpo.columnconfigure(0, weight=2)
    corpo.columnconfigure(1, weight=1)
    corpo.rowconfigure(0, weight=1)

    lista = criar_listbox(corpo, 18)
    lista.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

    painel = ctk.CTkFrame(
        corpo,
        fg_color=COR_PAINEL,
        border_color=COR_BORDA,
        border_width=1,
        corner_radius=8,
    )
    painel.grid(row=0, column=1, sticky="nsew")

    ctk.CTkLabel(
        painel,
        text="Detalhes",
        text_color=COR_TEXTO,
        font=FONTE_SECAO,
    ).pack(anchor="w", padx=12, pady=(12, 4))

    detalhes = ctk.CTkTextbox(
        painel,
        fg_color=COR_CAMPO,
        border_color=COR_BORDA,
        border_width=1,
        text_color=COR_TEXTO,
        font=FONTE_PADRAO,
    )
    detalhes.pack(fill="both", expand=True, padx=12, pady=(4, 12))

    if not arquivos:
        lista.insert(tk.END, "Nenhum arquivo encontrado")
        detalhes.insert("end", "Nenhum arquivo encontrado nas origens do perfil.")
    else:
        for arquivo in arquivos:
            extensao = arquivo.get("extensao") or "(sem extensao)"
            lista.insert(tk.END, arquivo.get("nome", "") + "    " + extensao)

    def atualizar_detalhes(indice):
        if not arquivos or indice < 0 or indice >= len(arquivos):
            return

        arquivo = arquivos[indice]
        status = "INCLUIDO" if arquivo.get("incluido") else "IGNORADO"
        conteudo = (
            "Nome: "
            + arquivo.get("nome", "")
            + "\nExtensao: "
            + (arquivo.get("extensao") or "(sem extensao)")
            + "\nStatus: "
            + status
            + "\nTamanho: "
            + str(arquivo.get("tamanho", 0))
            + " bytes\nData de modificacao: "
            + formatar_data_modificacao(arquivo.get("data_modificacao"))
            + "\n\nCaminho:\n"
            + arquivo.get("caminho", "")
        )

        detalhes.configure(state="normal")
        detalhes.delete("1.0", tk.END)
        detalhes.insert("end", conteudo)
        detalhes.configure(state="disabled")

    def ao_selecionar(evento):
        del evento
        selecao = lista.curselection()
        if selecao:
            atualizar_detalhes(selecao[0])

    def ao_mover_mouse(evento):
        indice = lista.nearest(evento.y)
        if arquivos and 0 <= indice < len(arquivos):
            lista.selection_clear(0, tk.END)
            lista.selection_set(indice)
            atualizar_detalhes(indice)

    lista.bind("<<ListboxSelect>>", ao_selecionar)
    lista.bind("<Motion>", ao_mover_mouse)

    if arquivos:
        lista.selection_set(0)
        atualizar_detalhes(0)
    detalhes.configure(state="disabled")
    return OK


def sincronizar_perfil_atual_interface(estado_interface, exibir_erros):
    """Salva em memoria a configuracao atual da tela quando ela estiver valida."""
    if not estado_interface.get("perfil_selecionado_id"):
        return ERRO_DADOS_INVALIDOS, None

    perfil = obter_dados_formulario(estado_interface)
    if perfil is None:
        if exibir_erros:
            mostrar_erro_validacao_formulario(estado_interface)
        return ERRO_DADOS_INVALIDOS, None

    codigo = controller.salvar_perfil_editado(perfil)
    if codigo != OK and exibir_erros:
        mostrar_mensagem_resultado(codigo)
    return codigo, perfil


def obter_dados_formulario(estado_interface):
    """Coleta dados do formulario para um dicionario de perfil."""
    perfil_id = estado_interface.get("perfil_selecionado_id")
    if not perfil_id:
        return None

    intervalo = converter_inteiro_opcional(estado_interface["entrada_intervalo"].get(), None)
    salvar_tipo_selecionado_em_memoria(estado_interface)

    if (
        intervalo == "invalido"
        or formulario_tipo_possui_valor_invalido(estado_interface)
        or not estado_interface.get("origens_configuradas")
        or existe_conflito_operacao_interface(estado_interface)
    ):
        return None

    return {
        "id": perfil_id,
        "nome": estado_interface["entrada_nome"].get(),
        "origens": obter_caminhos_origens_configuradas(estado_interface),
        "destinos": obter_caminhos_destinos_configurados(estado_interface),
        "operacao": estado_interface["operacao_var"].get(),
        "restricoes": criar_restricoes_da_interface(estado_interface),
        "origens_configuradas": estado_interface["origens_configuradas"],
        "agendamento": {
            "tipo": estado_interface["agendamento_tipo_var"].get(),
            "intervalo_minutos": intervalo,
            "executar_ao_detectar_mudanca": estado_interface["agendamento_tipo_var"].get() == "alteracao",
            "ultima_execucao": None,
        },
        "ativo": estado_interface["ativo_var"].get(),
    }


def preencher_formulario_com_perfil(estado_interface, perfil):
    """Preenche campos da interface com dados do perfil."""
    estado_interface["perfil_selecionado_id"] = perfil.get("id")
    preencher_entry(estado_interface["entrada_nome"], perfil.get("nome", ""))
    estado_interface["ativo_var"].set(perfil.get("ativo", True))
    estado_interface["operacao_var"].set(perfil.get("operacao", "copiar"))

    estado_interface["origens_configuradas"] = montar_origens_configuradas_para_interface(perfil)
    estado_interface["origem_selecionada_indice"] = None
    estado_interface["tipo_selecionado_indice"] = None
    atualizar_lista_origens_configuradas(estado_interface)
    limpar_area_tipo_destino(estado_interface)
    if estado_interface["origens_configuradas"]:
        selecionar_origem_por_indice(estado_interface, 0)

    agendamento = perfil.get("agendamento", {})
    estado_interface["agendamento_tipo_var"].set(agendamento.get("tipo", "manual"))
    intervalo = agendamento.get("intervalo_minutos")
    preencher_entry(estado_interface["entrada_intervalo"], "" if intervalo is None else str(intervalo))
    return perfil


def limpar_formulario(estado_interface):
    """Limpa os campos do formulario."""
    preencher_entry(estado_interface["entrada_nome"], "")
    estado_interface["origens_configuradas"] = []
    estado_interface["origem_selecionada_indice"] = None
    estado_interface["tipo_selecionado_indice"] = None
    preencher_lista(estado_interface["lista_origens"], [])
    preencher_lista(estado_interface["lista_tipos"], [])
    preencher_lista(estado_interface["lista_destinos"], [])
    estado_interface["operacao_var"].set("copiar")
    estado_interface["ativo_var"].set(True)
    atualizar_checkboxes_extensoes(estado_interface, [])
    preencher_entry(estado_interface["entrada_nome_contem"], "")
    preencher_entry(estado_interface["entrada_tamanho_min"], "")
    preencher_entry(estado_interface["entrada_tamanho_max"], "")
    preencher_entry(estado_interface["entrada_data_min"], "")
    preencher_entry(estado_interface["entrada_data_max"], "")
    estado_interface["agendamento_tipo_var"].set("manual")
    preencher_entry(estado_interface["entrada_intervalo"], "")
    return OK


def obter_itens_lista(lista):
    """Retorna todos os itens de uma listbox."""
    return list(lista.get(0, tk.END))


def montar_origens_configuradas_para_interface(perfil):
    """Monta origens configuradas para a interface, migrando perfil legado quando preciso."""
    origens_configuradas = perfil.get("origens_configuradas", [])
    if isinstance(origens_configuradas, list) and origens_configuradas:
        return copiar_lista_dicionarios(origens_configuradas)

    origens = perfil.get("origens", [])
    if not isinstance(origens, list):
        return []

    destinos = []
    for destino in perfil.get("destinos", []):
        destinos.append({
            "caminho": destino,
            "operacao": perfil.get("operacao", "copiar"),
        })

    configuradas = []
    for indice, origem in enumerate(origens):
        configuradas.append({
            "id": "origem_" + str(indice + 1),
            "caminho": origem,
            "ativo": True,
            "tipos_arquivo": [
                {
                    "id": "tipo_1",
                    "nome": "Todos os arquivos",
                    "ativo": True,
                    "restricoes": perfil.get("restricoes", {}),
                    "destinos": copiar_lista_dicionarios(destinos),
                }
            ],
        })
    return configuradas


def copiar_lista_dicionarios(lista):
    """Copia lista simples de dicionarios aninhados."""
    copia = []
    for item in lista:
        if isinstance(item, dict):
            novo = {}
            for chave, valor in item.items():
                if isinstance(valor, list):
                    novo[chave] = copiar_lista_dicionarios(valor)
                elif isinstance(valor, dict):
                    novo[chave] = valor.copy()
                else:
                    novo[chave] = valor
            copia.append(novo)
    return copia


def obter_caminhos_origens_configuradas(estado_interface):
    """Retorna caminhos de origens configuradas."""
    return [origem.get("caminho") for origem in estado_interface["origens_configuradas"] if origem.get("caminho")]


def obter_caminhos_destinos_configurados(estado_interface):
    """Retorna caminhos unicos de destinos configurados."""
    destinos = []
    for origem in estado_interface["origens_configuradas"]:
        for tipo in origem.get("tipos_arquivo", []):
            for destino in tipo.get("destinos", []):
                caminho = destino.get("caminho")
                if caminho and caminho not in destinos:
                    destinos.append(caminho)
    return destinos


def formulario_tipo_possui_valor_invalido(estado_interface):
    """Indica se filtros do tipo atual possuem valores invalidos."""
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


def preencher_lista(lista, itens):
    """Substitui os itens de uma listbox."""
    lista.delete(0, tk.END)
    for item in itens:
        lista.insert(tk.END, item)
    return OK


def preencher_entry(entrada, valor):
    """Substitui o conteudo de um campo de texto."""
    entrada.delete(0, tk.END)
    entrada.insert(0, valor)
    return OK


def obter_extensoes_marcadas(estado_interface):
    """Retorna extensoes marcadas no painel de checkboxes."""
    extensoes = []
    for extensao, var in estado_interface.get("extensoes_vars", {}).items():
        if var.get():
            extensoes.append(extensao)
    return extensoes


def obter_extensoes(texto):
    """Converte texto separado por virgula em lista de extensoes."""
    extensoes = []
    for extensao in texto.split(","):
        extensao = extensao.strip()
        if not extensao:
            continue
        if not extensao.startswith("."):
            extensao = "." + extensao
        extensoes.append(extensao.lower())
    return extensoes


def converter_inteiro_opcional(texto, padrao):
    """Converte texto para inteiro ou retorna padrao quando vazio."""
    texto = texto.strip()
    if not texto:
        return padrao
    try:
        valor = int(texto)
    except ValueError:
        return "invalido"
    if valor < 0:
        return "invalido"
    return valor


def converter_data_opcional(texto):
    """Valida data opcional e retorna texto normalizado."""
    texto = texto.strip()
    if not texto:
        return None
    try:
        datetime.fromisoformat(texto)
    except ValueError:
        return "invalido"
    return texto


def formatar_data_modificacao(valor):
    """Formata timestamp de modificacao para exibicao."""
    if not isinstance(valor, (int, float)):
        return ""
    return datetime.fromtimestamp(valor).strftime("%Y-%m-%d %H:%M:%S")


def mostrar_erro_validacao_formulario(estado_interface):
    """Mostra mensagem especifica para dados invalidos do formulario."""
    if not estado_interface.get("perfil_selecionado_id"):
        messagebox.showerror("BackupManager", "Selecione um perfil antes de aplicar alteracoes.")
        return ERRO_DADOS_INVALIDOS

    if not estado_interface["entrada_nome"].get().strip():
        messagebox.showerror("BackupManager", "Informe um nome para o perfil.")
        return ERRO_DADOS_INVALIDOS

    if not estado_interface.get("origens_configuradas"):
        messagebox.showerror("BackupManager", "Adicione pelo menos uma origem.")
        return ERRO_DADOS_INVALIDOS

    tamanho_min = converter_inteiro_opcional(estado_interface["entrada_tamanho_min"].get(), 0)
    tamanho_max = converter_inteiro_opcional(estado_interface["entrada_tamanho_max"].get(), None)
    intervalo = converter_inteiro_opcional(estado_interface["entrada_intervalo"].get(), None)
    if tamanho_min == "invalido" or tamanho_max == "invalido":
        messagebox.showerror("BackupManager", "Informe tamanhos validos usando numeros inteiros positivos.")
        return ERRO_DADOS_INVALIDOS
    if intervalo == "invalido":
        messagebox.showerror("BackupManager", "Informe um intervalo valido em minutos.")
        return ERRO_DADOS_INVALIDOS

    data_min = converter_data_opcional(estado_interface["entrada_data_min"].get())
    data_max = converter_data_opcional(estado_interface["entrada_data_max"].get())
    if data_min == "invalido" or data_max == "invalido":
        messagebox.showerror("BackupManager", "Use datas no formato AAAA-MM-DD HH:MM:SS.")
        return ERRO_DADOS_INVALIDOS

    if existe_conflito_operacao_interface(estado_interface):
        messagebox.showerror(
            "BackupManager",
            "Mover ou recortar so pode ser usado com um destino para o mesmo tipo de arquivo.",
        )
        return ERRO_DADOS_INVALIDOS

    messagebox.showerror("BackupManager", "Verifique os dados do formulario.")
    return ERRO_DADOS_INVALIDOS


def existe_conflito_operacao_interface(estado_interface):
    """Verifica conflito visual de mover/recortar em multiplos destinos."""
    for origem in estado_interface.get("origens_configuradas", []):
        for tipo in origem.get("tipos_arquivo", []):
            destinos = tipo.get("destinos", [])
            if len(destinos) <= 1:
                continue
            for destino in destinos:
                if destino.get("operacao") in ("mover", "recortar"):
                    return True
    return False


def mostrar_mensagem_resultado(codigo):
    """Exibe mensagem correspondente a um codigo de retorno."""
    mensagem = obter_mensagem(codigo)
    if codigo == OK:
        messagebox.showinfo("BackupManager", mensagem)
    else:
        messagebox.showerror("BackupManager", mensagem)
    return codigo
