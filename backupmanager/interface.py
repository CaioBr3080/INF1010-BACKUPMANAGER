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
        "lista_destinos": None,
        "operacao_var": None,
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
    """Cria a area de origens e destinos."""
    frame = criar_painel(janela, "Origens e destinos")
    frame.pack(fill="both", expand=True, side="left", padx=(0, 4), pady=8)

    criar_label(frame, "Origens").pack(anchor="w", padx=8, pady=(8, 0))
    estado_interface["lista_origens"] = criar_listbox(frame, 7)
    estado_interface["lista_origens"].pack(fill="both", expand=True, padx=8, pady=4)

    linha_origens = ctk.CTkFrame(frame, fg_color="transparent")
    linha_origens.pack(fill="x", padx=8, pady=(0, 8))
    criar_botao(linha_origens, "Adicionar origem", lambda: adicionar_origem_interface(estado_interface), COR_AZUL).pack(
        side="left"
    )
    criar_botao(linha_origens, "Remover origem", lambda: remover_item_lista(estado_interface["lista_origens"])).pack(
        side="left", padx=6
    )
    botao_abrir_origem = criar_botao(
        linha_origens,
        "\U0001F4C1",
        lambda: abrir_pasta_selecionada(estado_interface["lista_origens"], "origem"),
        largura=42,
    )
    botao_abrir_origem.pack(side="left")
    adicionar_tooltip(botao_abrir_origem, "Abrir pasta de origem")

    criar_label(frame, "Destinos").pack(anchor="w", padx=8)
    estado_interface["lista_destinos"] = criar_listbox(frame, 7)
    estado_interface["lista_destinos"].pack(fill="both", expand=True, padx=8, pady=4)

    linha_destinos = ctk.CTkFrame(frame, fg_color="transparent")
    linha_destinos.pack(fill="x", padx=8, pady=(0, 8))
    criar_botao(linha_destinos, "Adicionar destino", lambda: adicionar_destino_interface(estado_interface), COR_AZUL).pack(
        side="left"
    )
    criar_botao(
        linha_destinos,
        "Remover destino",
        lambda: remover_item_lista(estado_interface["lista_destinos"]),
    ).pack(side="left", padx=6)
    botao_abrir_destino = criar_botao(
        linha_destinos,
        "\U0001F4C1",
        lambda: abrir_pasta_selecionada(estado_interface["lista_destinos"], "destino"),
        largura=42,
    )
    botao_abrir_destino.pack(side="left")
    adicionar_tooltip(botao_abrir_destino, "Abrir pasta de destino")

    estado_interface["operacao_var"] = tk.StringVar(value="copiar")
    linha_operacao = ctk.CTkFrame(frame, fg_color="transparent")
    linha_operacao.pack(fill="x", padx=8, pady=(0, 8))
    criar_label(linha_operacao, "Operacao").pack(side="left")
    ctk.CTkRadioButton(
        linha_operacao,
        text="Copiar",
        variable=estado_interface["operacao_var"],
        value="copiar",
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
        text_color=COR_TEXTO,
        fg_color=COR_AZUL,
        hover_color="#1d4ed8",
        font=FONTE_PADRAO,
    ).pack(
        side="left"
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

    criar_botao(
        frame,
        "Aplicar",
        lambda: aplicar_alteracoes_interface(estado_interface),
        COR_AZUL,
        largura=92,
    ).pack(
        side="left", padx=(0, 6)
    )
    estado_interface["botao_backup"] = criar_botao(
        frame,
        "Backup",
        lambda: executar_backup_interface(estado_interface),
        COR_VERDE,
        largura=92,
    )
    estado_interface["botao_backup"].pack(side="left", padx=6)
    criar_botao(
        frame,
        "Historico",
        lambda: mostrar_historico_interface(estado_interface),
        largura=92,
    ).pack(
        side="left", padx=6
    )
    criar_botao(
        frame,
        "Arquivos",
        lambda: visualizar_arquivos_interface(estado_interface),
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
    caminho = filedialog.askdirectory(title="Escolha a pasta de origem")
    if caminho:
        estado_interface["lista_origens"].insert(tk.END, caminho)
    return OK


def adicionar_destino_interface(estado_interface):
    """Adiciona uma pasta de destino na lista visual."""
    caminho = filedialog.askdirectory(title="Escolha a pasta de destino")
    if caminho:
        estado_interface["lista_destinos"].insert(tk.END, caminho)
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

    caminho = lista.get(selecao[0])
    if not os.path.isdir(caminho):
        messagebox.showerror("BackupManager", "Pasta de " + tipo + " nao encontrada.")
        return ERRO_DADOS_INVALIDOS

    try:
        os.startfile(caminho)
    except OSError:
        messagebox.showerror("BackupManager", "Nao foi possivel abrir a pasta de " + tipo + ".")
        return ERRO_DADOS_INVALIDOS

    return OK


def aplicar_alteracoes_interface(estado_interface):
    """Aplica alteracoes do formulario ao estado em memoria."""
    perfil = obter_dados_formulario(estado_interface)
    if perfil is None:
        mostrar_erro_validacao_formulario(estado_interface)
        return ERRO_DADOS_INVALIDOS

    codigo = controller.salvar_perfil_editado(perfil)
    if codigo == OK:
        atualizar_lista_perfis(estado_interface)
        selecionar_perfil_por_id(estado_interface, perfil["id"])
    mostrar_mensagem_resultado(codigo)
    return codigo


def executar_backup_interface(estado_interface):
    """Executa o backup do perfil selecionado."""
    perfil_id = estado_interface.get("perfil_selecionado_id")
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
            + "\nErros: "
            + str(len(erros))
        )
        if erros:
            conteudo += "\n\nDetalhes dos erros:\n" + "\n".join(str(erro) for erro in erros)

        detalhes.configure(state="normal")
        detalhes.delete("1.0", tk.END)
        detalhes.insert("end", conteudo)
        detalhes.configure(state="disabled")

    def ao_selecionar(evento):
        del evento
        selecao = lista.curselection()
        if selecao:
            atualizar_detalhes(selecao[0])

    def limpar_historico():
        codigo_limpar = controller.limpar_historico_do_perfil(perfil_id)
        mostrar_mensagem_resultado(codigo_limpar)
        preencher_historico()

    lista.bind("<<ListboxSelect>>", ao_selecionar)
    preencher_historico()

    linha_botoes = ctk.CTkFrame(janela, fg_color="transparent")
    linha_botoes.pack(fill="x", padx=14, pady=(0, 14))
    criar_botao(linha_botoes, "Limpar historico do perfil", limpar_historico, COR_VERMELHO).pack(side="left")
    criar_botao(linha_botoes, "Fechar", janela.destroy).pack(side="right")
    return OK


def visualizar_arquivos_interface(estado_interface):
    """Mostra os arquivos encontrados nas origens do perfil."""
    perfil = obter_dados_formulario(estado_interface)
    if perfil is None:
        mostrar_erro_validacao_formulario(estado_interface)
        return ERRO_DADOS_INVALIDOS

    codigo = controller.salvar_perfil_editado(perfil)
    if codigo != OK:
        mostrar_mensagem_resultado(codigo)
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


def obter_dados_formulario(estado_interface):
    """Coleta dados do formulario para um dicionario de perfil."""
    perfil_id = estado_interface.get("perfil_selecionado_id")
    if not perfil_id:
        return None

    tamanho_min = converter_inteiro_opcional(estado_interface["entrada_tamanho_min"].get(), 0)
    tamanho_max = converter_inteiro_opcional(estado_interface["entrada_tamanho_max"].get(), None)
    intervalo = converter_inteiro_opcional(estado_interface["entrada_intervalo"].get(), None)
    data_min = converter_data_opcional(estado_interface["entrada_data_min"].get())
    data_max = converter_data_opcional(estado_interface["entrada_data_max"].get())

    if (
        tamanho_min == "invalido"
        or tamanho_max == "invalido"
        or intervalo == "invalido"
        or data_min == "invalido"
        or data_max == "invalido"
    ):
        return None

    return {
        "id": perfil_id,
        "nome": estado_interface["entrada_nome"].get(),
        "origens": obter_itens_lista(estado_interface["lista_origens"]),
        "destinos": obter_itens_lista(estado_interface["lista_destinos"]),
        "operacao": estado_interface["operacao_var"].get(),
        "restricoes": {
            "extensoes_permitidas": obter_extensoes_marcadas(estado_interface),
            "nome_contem": estado_interface["entrada_nome_contem"].get().strip(),
            "tamanho_min": tamanho_min,
            "tamanho_max": tamanho_max,
            "data_modificacao_min": data_min,
            "data_modificacao_max": data_max,
        },
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

    preencher_lista(estado_interface["lista_origens"], perfil.get("origens", []))
    preencher_lista(estado_interface["lista_destinos"], perfil.get("destinos", []))

    restricoes = perfil.get("restricoes", {})
    atualizar_checkboxes_extensoes(estado_interface, restricoes.get("extensoes_permitidas", []))
    preencher_entry(estado_interface["entrada_nome_contem"], restricoes.get("nome_contem", ""))
    preencher_entry(estado_interface["entrada_tamanho_min"], str(restricoes.get("tamanho_min", 0)))

    tamanho_max = restricoes.get("tamanho_max")
    preencher_entry(estado_interface["entrada_tamanho_max"], "" if tamanho_max is None else str(tamanho_max))
    preencher_entry(estado_interface["entrada_data_min"], restricoes.get("data_modificacao_min") or "")
    preencher_entry(estado_interface["entrada_data_max"], restricoes.get("data_modificacao_max") or "")

    agendamento = perfil.get("agendamento", {})
    estado_interface["agendamento_tipo_var"].set(agendamento.get("tipo", "manual"))
    intervalo = agendamento.get("intervalo_minutos")
    preencher_entry(estado_interface["entrada_intervalo"], "" if intervalo is None else str(intervalo))
    return perfil


def limpar_formulario(estado_interface):
    """Limpa os campos do formulario."""
    preencher_entry(estado_interface["entrada_nome"], "")
    preencher_lista(estado_interface["lista_origens"], [])
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

    messagebox.showerror("BackupManager", "Verifique os dados do formulario.")
    return ERRO_DADOS_INVALIDOS


def mostrar_mensagem_resultado(codigo):
    """Exibe mensagem correspondente a um codigo de retorno."""
    mensagem = obter_mensagem(codigo)
    if codigo == OK:
        messagebox.showinfo("BackupManager", mensagem)
    else:
        messagebox.showerror("BackupManager", mensagem)
    return codigo
