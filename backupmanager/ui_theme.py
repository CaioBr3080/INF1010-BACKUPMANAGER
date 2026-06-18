"""Tema visual e helpers de janelas da interface."""

import tkinter as tk

import customtkinter as ctk

from backupmanager.return_codes import OK

__all__ = [
    "COR_FUNDO",
    "COR_PAINEL",
    "COR_PAINEL_2",
    "COR_CAMPO",
    "COR_BORDA",
    "COR_TEXTO",
    "COR_TEXTO_FRACO",
    "COR_AZUL",
    "COR_VERDE",
    "COR_VERMELHO",
    "FONTE_FAMILIA",
    "FONTE_PADRAO",
    "FONTE_SELECAO",
    "FONTE_TITULO",
    "FONTE_SECAO",
    "configurar_estilo_visual",
    "configurar_frame",
    "criar_painel",
    "criar_label",
    "criar_entry",
    "criar_botao",
    "adicionar_tooltip",
    "criar_listbox",
    "widgets_existem",
    "trazer_janela_para_frente",
    "manter_janela_acima_da_principal",
]

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
FONTE_PADRAO = (FONTE_FAMILIA, 13)
FONTE_SELECAO = (FONTE_FAMILIA, 13)
FONTE_TITULO = (FONTE_FAMILIA, 28, "bold")
FONTE_SECAO = (FONTE_FAMILIA, 13, "bold")


def configurar_estilo_visual():
    """Configura o tema global usado pelos widgets CustomTkinter.

    Deve ser chamada antes de criar a janela principal. Define modo escuro e
    tema base azul para manter consistencia visual em todos os paineis.
    """
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    return OK


def configurar_frame(frame):
    """Aplica a configuracao visual neutra usada em frames de layout.

    Recebe um frame ja criado, torna seu fundo transparente e retorna o mesmo
    objeto para permitir encadeamento na montagem da interface.
    """
    frame.configure(fg_color="transparent")
    return frame


def criar_painel(container, titulo):
    """Cria um painel padronizado com borda, fundo e titulo de secao.

    Usado como bloco visual principal da interface. Retorna o frame para que
    quem chama posicione widgets internos e controle `pack`/`grid` externo.
    """
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
    """Cria um label auxiliar com cor e fonte padrao da interface.

    Aplica a cor secundaria e a fonte comum do tema. O widget e retornado sem
    posicionamento para que o painel chamador escolha o layout adequado.
    """
    return ctk.CTkLabel(container, text=texto, text_color=COR_TEXTO_FRACO, font=FONTE_PADRAO)


def criar_entry(container, largura=None):
    """Cria um campo de texto consistente para formularios da interface.

    Aplica cores, borda, altura e fonte comuns. `largura` e opcional para
    campos compactos; quando omitida, o layout decide a expansao.
    """
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
    """Cria um botao padronizado com hover coerente com a cor base.

    Recebe texto, callback e cores opcionais. Retorna o widget sem posicionar,
    permitindo que cada painel escolha `pack` ou `grid`.
    """
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
        font=FONTE_SELECAO,
    )


def adicionar_tooltip(widget, texto):
    """Adiciona um tooltip simples controlado por eventos de mouse.

    Cria uma pequena janela flutuante ao passar o mouse sobre `widget` e a
    remove ao sair ou clicar. Retorna o proprio widget para manter o uso
    fluido na construcao da UI.
    """
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
    """Cria uma listbox com cores e fonte alinhadas ao tema do app.

    Configura selecao, borda, fonte e exportacao de selecao. Retorna o widget
    bruto do tkinter para uso com `curselection`, `insert`, `delete` e eventos.
    """
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


def widgets_existem(*widgets):
    """Indica se todos os widgets informados ainda existem no Tk.

    Evita erros quando callbacks de janelas secundarias tentam atualizar
    widgets ja destruidos. Retorna `True` somente quando todos existem.
    """
    try:
        return all(widget is not None and widget.winfo_exists() for widget in widgets)
    except tk.TclError:
        return False


def trazer_janela_para_frente(janela):
    """Traz a janela principal para frente ao iniciar sem fixa-la no topo.

    Usa `lift`, foco e `-topmost` temporario para destacar a janela criada,
    removendo a superioridade logo em seguida.
    """
    janela.lift()
    janela.focus_force()
    janela.attributes("-topmost", True)
    janela.after(700, lambda: janela.attributes("-topmost", False))
    return OK


def manter_janela_acima_da_principal(janela_filha, janela_principal):
    """Mantem uma janela secundaria acima da principal ate ela ser minimizada.

    Configura eventos para ajustar `topmost` conforme minimizacao/restauracao,
    permitindo um meio termo entre prioridade visual e liberdade para reduzir
    a janela.
    """
    try:
        janela_filha.attributes("-toolwindow", False)
    except tk.TclError:
        pass

    def atualizar_superioridade(evento=None):
        del evento
        if not widgets_existem(janela_filha):
            return
        try:
            janela_filha.attributes("-topmost", janela_filha.state() != "iconic")
        except tk.TclError:
            return

    janela_filha.bind("<Unmap>", atualizar_superioridade, add="+")
    janela_filha.bind("<Map>", atualizar_superioridade, add="+")
    janela_filha.bind("<FocusIn>", atualizar_superioridade, add="+")

    if janela_principal is not None:
        janela_filha.lift(janela_principal)
    else:
        janela_filha.lift()
    janela_filha.focus_force()
    atualizar_superioridade()
    return OK
