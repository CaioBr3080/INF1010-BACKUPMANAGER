"""Fluxo visual origem -> tipo -> destino da interface."""

import os
import tkinter as tk
from tkinter import filedialog, messagebox

import customtkinter as ctk

from backupmanager.return_codes import OK, ERRO_DADOS_INVALIDOS
from backupmanager.ui_restrictions import (
    criar_restricoes_da_interface,
    limpar_area_tipo_destino,
    preencher_formulario_com_tipo,
)
from backupmanager.ui_theme import (
    COR_AZUL,
    COR_BORDA,
    COR_TEXTO,
    FONTE_PADRAO,
    FONTE_SELECAO,
    adicionar_tooltip,
    criar_botao,
    criar_entry,
    criar_label,
    criar_listbox,
    criar_painel,
)

__all__ = [
    "criar_area_origens_destinos",
    "atualizar_lista_origens_configuradas",
    "selecionar_origem_por_indice",
    "salvar_tipo_selecionado_em_memoria",
]


def criar_area_origens_destinos(janela, estado_interface):
    """Cria a area visual do fluxo origem -> tipo -> destino.

    Monta as tres colunas principais do modelo atual: origens, tipos da
    origem selecionada e destinos do tipo selecionado. Registra listboxes e
    variaveis de operacao em `estado_interface`.
    """
    frame = criar_painel(janela, "Fluxo de backup")
    frame.pack(fill="both", expand=True, side="left", padx=(0, 4), pady=8)

    conteudo = ctk.CTkFrame(frame, fg_color="transparent")
    conteudo.pack(fill="both", expand=True, padx=8, pady=(0, 8))
    conteudo.columnconfigure(0, weight=1)
    conteudo.columnconfigure(1, weight=1)
    conteudo.columnconfigure(2, weight=1)
    conteudo.rowconfigure(0, weight=1)

    _criar_coluna_origens(conteudo, estado_interface)
    _criar_coluna_tipos(conteudo, estado_interface)
    _criar_coluna_destinos(conteudo, estado_interface)
    return frame


def _criar_coluna_origens(container, estado_interface):
    """Cria a coluna de origens do fluxo de backup."""
    coluna_origens = ctk.CTkFrame(container, fg_color="transparent")
    coluna_origens.grid(row=0, column=0, sticky="nsew", padx=(0, 4))
    coluna_origens.columnconfigure(0, weight=1)
    coluna_origens.rowconfigure(1, weight=1)
    criar_label(coluna_origens, "Origens").grid(row=0, column=0, sticky="w")
    estado_interface["lista_origens"] = criar_listbox(coluna_origens, 10)
    estado_interface["lista_origens"].grid(row=1, column=0, sticky="nsew", pady=4)
    estado_interface["lista_origens"].bind(
        "<<ListboxSelect>>",
        lambda evento: _selecionar_origem_configurada_interface(estado_interface),
    )

    linha_origens = ctk.CTkFrame(coluna_origens, fg_color="transparent")
    linha_origens.grid(row=2, column=0, sticky="ew")
    criar_botao(linha_origens, "Adicionar origem", lambda: _adicionar_origem_interface(estado_interface), COR_AZUL).pack(
        side="left"
    )
    criar_botao(linha_origens, "Remover origem", lambda: _remover_origem_configurada_interface(estado_interface)).pack(
        side="left", padx=6
    )
    criar_botao(
        linha_origens,
        "On/Off",
        lambda: _alternar_origem_ativa_interface(estado_interface),
        largura=72,
    ).pack(side="left")
    botao_abrir_origem = criar_botao(
        linha_origens,
        "\U0001F4C1",
        lambda: _abrir_origem_selecionada_interface(estado_interface),
        largura=42,
    )
    botao_abrir_origem.pack(side="left")
    adicionar_tooltip(botao_abrir_origem, "Abrir pasta de origem")
    return coluna_origens


def _criar_coluna_tipos(container, estado_interface):
    """Cria a coluna de tipos da origem selecionada."""
    coluna_tipos = ctk.CTkFrame(container, fg_color="transparent")
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
        lambda evento: _selecionar_tipo_arquivo_interface(estado_interface),
    )
    linha_tipos = ctk.CTkFrame(coluna_tipos, fg_color="transparent")
    linha_tipos.grid(row=3, column=0, sticky="ew")
    criar_botao(linha_tipos, "Adicionar tipo", lambda: _adicionar_tipo_arquivo_interface(estado_interface), COR_AZUL).pack(
        side="left"
    )
    criar_botao(linha_tipos, "Remover tipo", lambda: _remover_tipo_arquivo_interface(estado_interface)).pack(
        side="left", padx=6
    )
    criar_botao(
        linha_tipos,
        "On/Off",
        lambda: _alternar_tipo_ativo_interface(estado_interface),
        largura=72,
    ).pack(side="left")
    return coluna_tipos


def _criar_coluna_destinos(container, estado_interface):
    """Cria a coluna de destinos e operacao do tipo selecionado."""
    coluna_destinos = ctk.CTkFrame(container, fg_color="transparent")
    coluna_destinos.grid(row=0, column=2, sticky="nsew", padx=(4, 0))
    coluna_destinos.columnconfigure(0, weight=1)
    coluna_destinos.rowconfigure(1, weight=1)
    criar_label(coluna_destinos, "Destinos do tipo").grid(row=0, column=0, sticky="w")
    estado_interface["lista_destinos"] = criar_listbox(coluna_destinos, 10)
    estado_interface["lista_destinos"].grid(row=1, column=0, sticky="nsew", pady=4)
    estado_interface["lista_destinos"].bind(
        "<<ListboxSelect>>",
        lambda evento: _selecionar_destino_tipo_interface(estado_interface),
    )

    linha_destinos = ctk.CTkFrame(coluna_destinos, fg_color="transparent")
    linha_destinos.grid(row=2, column=0, sticky="ew")
    criar_botao(linha_destinos, "Adicionar destino", lambda: _adicionar_destino_interface(estado_interface), COR_AZUL).pack(
        side="left"
    )
    criar_botao(
        linha_destinos,
        "Remover destino",
        lambda: _remover_destino_tipo_interface(estado_interface),
    ).pack(side="left", padx=6)
    botao_abrir_destino = criar_botao(
        linha_destinos,
        "\U0001F4C1",
        lambda: _abrir_destino_selecionado_interface(estado_interface),
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
        command=lambda: _atualizar_operacao_destino_interface(estado_interface),
        text_color=COR_TEXTO,
        fg_color=COR_AZUL,
        hover_color="#1d4ed8",
        font=FONTE_PADRAO,
    ).pack(side="left", padx=8)
    ctk.CTkRadioButton(
        linha_operacao,
        text="Mover",
        variable=estado_interface["operacao_var"],
        value="mover",
        command=lambda: _atualizar_operacao_destino_interface(estado_interface),
        text_color=COR_TEXTO,
        fg_color=COR_AZUL,
        hover_color="#1d4ed8",
        font=FONTE_PADRAO,
    ).pack(side="left")
    ctk.CTkRadioButton(
        linha_operacao,
        text="Recortar",
        variable=estado_interface["operacao_var"],
        value="recortar",
        command=lambda: _atualizar_operacao_destino_interface(estado_interface),
        text_color=COR_TEXTO,
        fg_color=COR_AZUL,
        hover_color="#1d4ed8",
        font=FONTE_SELECAO,
    ).pack(side="left", padx=8)
    return coluna_destinos


def _adicionar_origem_interface(estado_interface):
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


def _adicionar_destino_interface(estado_interface):
    """Adiciona uma pasta de destino ao tipo selecionado."""
    salvar_tipo_selecionado_em_memoria(estado_interface)
    tipo = _obter_tipo_selecionado(estado_interface)
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
        _atualizar_lista_destinos_tipo(estado_interface)
        _selecionar_destino_por_indice(estado_interface, len(tipo["destinos"]) - 1)
    return OK


def _adicionar_tipo_arquivo_interface(estado_interface):
    """Adiciona tipo de arquivo a origem selecionada."""
    salvar_tipo_selecionado_em_memoria(estado_interface)
    origem = _obter_origem_selecionada(estado_interface)
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
    _atualizar_lista_tipos_origem(estado_interface)
    _selecionar_tipo_por_indice(estado_interface, len(origem["tipos_arquivo"]) - 1)
    return OK


def _remover_origem_configurada_interface(estado_interface):
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


def _remover_tipo_arquivo_interface(estado_interface):
    """Remove tipo de arquivo selecionado."""
    origem = _obter_origem_selecionada(estado_interface)
    indice = estado_interface.get("tipo_selecionado_indice")
    if origem is None or indice is None:
        return ERRO_DADOS_INVALIDOS

    tipos = origem.get("tipos_arquivo", [])
    if 0 <= indice < len(tipos):
        tipos.pop(indice)
    estado_interface["tipo_selecionado_indice"] = None
    estado_interface["destino_selecionado_indice"] = None
    _atualizar_lista_tipos_origem(estado_interface)
    limpar_area_tipo_destino(estado_interface)
    return OK


def _remover_destino_tipo_interface(estado_interface):
    """Remove destino selecionado do tipo atual."""
    tipo = _obter_tipo_selecionado(estado_interface)
    selecao = estado_interface["lista_destinos"].curselection()
    if tipo is None or not selecao:
        return ERRO_DADOS_INVALIDOS

    destinos = tipo.get("destinos", [])
    indice = selecao[0]
    if 0 <= indice < len(destinos):
        destinos.pop(indice)
    estado_interface["destino_selecionado_indice"] = None
    _atualizar_lista_destinos_tipo(estado_interface)
    return OK


def _alternar_origem_ativa_interface(estado_interface):
    """Liga ou desliga a origem selecionada."""
    origem = _obter_origem_selecionada(estado_interface)
    if origem is None:
        return ERRO_DADOS_INVALIDOS

    origem["ativo"] = not origem.get("ativo", True)
    indice = estado_interface.get("origem_selecionada_indice")
    atualizar_lista_origens_configuradas(estado_interface)
    selecionar_origem_por_indice(estado_interface, indice)
    return OK


def _alternar_tipo_ativo_interface(estado_interface):
    """Liga ou desliga o tipo selecionado."""
    tipo = _obter_tipo_selecionado(estado_interface)
    if tipo is None:
        return ERRO_DADOS_INVALIDOS

    tipo["ativo"] = not tipo.get("ativo", True)
    indice = estado_interface.get("tipo_selecionado_indice")
    _atualizar_lista_tipos_origem(estado_interface)
    _selecionar_tipo_por_indice(estado_interface, indice)
    return OK


def _abrir_pasta_selecionada(lista, tipo):
    """Abre a pasta selecionada em uma listbox."""
    selecao = lista.curselection()
    if not selecao:
        messagebox.showwarning("BackupManager", "Selecione uma pasta de " + tipo + ".")
        return ERRO_DADOS_INVALIDOS

    caminho = lista.get(selecao[0]).split(" | ")[0]
    if caminho.startswith("[x] ") or caminho.startswith("[ ] "):
        caminho = caminho[4:]
    return _abrir_pasta_por_caminho(caminho, tipo)


def _abrir_pasta_por_caminho(caminho, tipo):
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


def _abrir_origem_selecionada_interface(estado_interface):
    """Abre a pasta da origem selecionada."""
    origem = _obter_origem_selecionada(estado_interface)
    if origem is None:
        messagebox.showwarning("BackupManager", "Selecione uma pasta de origem.")
        return ERRO_DADOS_INVALIDOS
    return _abrir_pasta_por_caminho(origem.get("caminho", ""), "origem")


def _abrir_destino_selecionado_interface(estado_interface):
    """Abre a pasta do destino selecionado."""
    destino = _obter_destino_selecionado(estado_interface)
    if destino is None:
        messagebox.showwarning("BackupManager", "Selecione uma pasta de destino.")
        return ERRO_DADOS_INVALIDOS
    return _abrir_pasta_por_caminho(destino.get("caminho", ""), "destino")


def atualizar_lista_origens_configuradas(estado_interface):
    """Atualiza a listbox de origens configuradas no estado visual.

    Usa `origens_configuradas` em memoria, exibe marcador ativo/inativo e nao
    consulta o controller. Deve ser chamada sempre que a lista de origens for
    alterada.
    """
    lista = estado_interface["lista_origens"]
    lista.delete(0, tk.END)
    for origem in estado_interface["origens_configuradas"]:
        marcador = "[x] " if origem.get("ativo", True) else "[ ] "
        lista.insert(tk.END, marcador + origem.get("caminho", ""))
    return OK


def _atualizar_lista_tipos_origem(estado_interface):
    """Atualiza tipos da origem selecionada."""
    lista = estado_interface["lista_tipos"]
    lista.delete(0, tk.END)
    origem = _obter_origem_selecionada(estado_interface)
    if origem is None:
        return ERRO_DADOS_INVALIDOS

    for tipo in origem.get("tipos_arquivo", []):
        marcador = "[x] " if tipo.get("ativo", True) else "[ ] "
        lista.insert(tk.END, marcador + tipo.get("nome", "Sem nome"))
    return OK


def _atualizar_lista_destinos_tipo(estado_interface):
    """Atualiza destinos do tipo selecionado."""
    lista = estado_interface["lista_destinos"]
    lista.delete(0, tk.END)
    estado_interface["destino_selecionado_indice"] = None
    tipo = _obter_tipo_selecionado(estado_interface)
    if tipo is None:
        return ERRO_DADOS_INVALIDOS

    for destino in tipo.get("destinos", []):
        lista.insert(tk.END, destino.get("caminho", "") + " | " + destino.get("operacao", "copiar"))
    return OK


def _selecionar_destino_tipo_interface(estado_interface):
    """Seleciona destino do tipo atual e carrega sua operacao."""
    selecao = estado_interface["lista_destinos"].curselection()
    if not selecao:
        return ERRO_DADOS_INVALIDOS

    estado_interface["destino_selecionado_indice"] = selecao[0]
    destino = _obter_destino_selecionado(estado_interface)
    if destino is not None:
        estado_interface["operacao_var"].set(destino.get("operacao", "copiar"))
    return OK


def _selecionar_destino_por_indice(estado_interface, indice):
    """Seleciona destino visualmente por indice."""
    lista = estado_interface["lista_destinos"]
    if indice < 0 or indice >= lista.size():
        return ERRO_DADOS_INVALIDOS
    lista.selection_clear(0, tk.END)
    lista.selection_set(indice)
    lista.activate(indice)
    return _selecionar_destino_tipo_interface(estado_interface)


def _obter_destino_selecionado(estado_interface):
    """Retorna destino selecionado do tipo atual."""
    tipo = _obter_tipo_selecionado(estado_interface)
    indice = estado_interface.get("destino_selecionado_indice")
    if tipo is None or indice is None:
        return None
    destinos = tipo.get("destinos", [])
    if indice < 0 or indice >= len(destinos):
        return None
    return destinos[indice]


def _atualizar_operacao_destino_interface(estado_interface):
    """Atualiza operacao do destino selecionado."""
    destino = _obter_destino_selecionado(estado_interface)
    if destino is None:
        return OK

    destino["operacao"] = estado_interface["operacao_var"].get()
    indice = estado_interface.get("destino_selecionado_indice")
    _atualizar_lista_destinos_tipo(estado_interface)
    _selecionar_destino_por_indice(estado_interface, indice)
    return OK


def _selecionar_origem_configurada_interface(estado_interface):
    """Seleciona origem e atualiza tipos relacionados."""
    salvar_tipo_selecionado_em_memoria(estado_interface)
    selecao = estado_interface["lista_origens"].curselection()
    if not selecao:
        return ERRO_DADOS_INVALIDOS

    estado_interface["origem_selecionada_indice"] = selecao[0]
    estado_interface["tipo_selecionado_indice"] = None
    estado_interface["destino_selecionado_indice"] = None
    _atualizar_lista_tipos_origem(estado_interface)
    limpar_area_tipo_destino(estado_interface)

    origem = _obter_origem_selecionada(estado_interface)
    if origem and origem.get("tipos_arquivo"):
        _selecionar_tipo_por_indice(estado_interface, 0)
    return OK


def _selecionar_tipo_arquivo_interface(estado_interface):
    """Seleciona tipo e carrega filtros e destinos."""
    salvar_tipo_selecionado_em_memoria(estado_interface)
    selecao = estado_interface["lista_tipos"].curselection()
    if not selecao:
        return ERRO_DADOS_INVALIDOS

    estado_interface["tipo_selecionado_indice"] = selecao[0]
    estado_interface["destino_selecionado_indice"] = None
    preencher_formulario_com_tipo(
        estado_interface,
        _obter_tipo_selecionado(estado_interface),
        lambda: _atualizar_lista_destinos_tipo(estado_interface),
    )
    return OK


def selecionar_origem_por_indice(estado_interface, indice):
    """Seleciona visualmente uma origem pelo indice da listbox.

    Limpa selecoes anteriores, ativa o item e executa o fluxo de carregamento
    dos tipos relacionados a origem. Retorna erro para indices fora da lista.
    """
    lista = estado_interface["lista_origens"]
    if indice < 0 or indice >= lista.size():
        return ERRO_DADOS_INVALIDOS
    lista.selection_clear(0, tk.END)
    lista.selection_set(indice)
    lista.activate(indice)
    return _selecionar_origem_configurada_interface(estado_interface)


def _selecionar_tipo_por_indice(estado_interface, indice):
    """Seleciona tipo visualmente por indice."""
    lista = estado_interface["lista_tipos"]
    if indice < 0 or indice >= lista.size():
        return ERRO_DADOS_INVALIDOS
    lista.selection_clear(0, tk.END)
    lista.selection_set(indice)
    lista.activate(indice)
    return _selecionar_tipo_arquivo_interface(estado_interface)


def _obter_origem_selecionada(estado_interface):
    """Retorna origem selecionada."""
    indice = estado_interface.get("origem_selecionada_indice")
    origens = estado_interface.get("origens_configuradas", [])
    if indice is None or indice < 0 or indice >= len(origens):
        return None
    return origens[indice]


def _obter_tipo_selecionado(estado_interface):
    """Retorna tipo selecionado."""
    origem = _obter_origem_selecionada(estado_interface)
    indice = estado_interface.get("tipo_selecionado_indice")
    if origem is None or indice is None:
        return None
    tipos = origem.get("tipos_arquivo", [])
    if indice < 0 or indice >= len(tipos):
        return None
    return tipos[indice]


def salvar_tipo_selecionado_em_memoria(estado_interface):
    """Grava no tipo selecionado os campos editados na tela.

    Atualiza nome e restricoes do tipo atualmente selecionado dentro de
    `origens_configuradas`. Nao chama o controller; a persistencia em memoria
    do perfil acontece depois via sincronizacao do formulario.
    """
    tipo = _obter_tipo_selecionado(estado_interface)
    if tipo is None:
        return OK

    nome = estado_interface["entrada_tipo_nome"].get().strip()
    if nome:
        tipo["nome"] = nome
    tipo["restricoes"] = criar_restricoes_da_interface(estado_interface)
    return OK

