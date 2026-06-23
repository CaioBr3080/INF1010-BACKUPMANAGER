"""Acoes principais, sincronizacao e mensagens da interface."""

import threading
import tkinter as tk
from tkinter import messagebox

import customtkinter as ctk

from backupmanager import controller
from backupmanager.domain import backup_result, perfil_manager
from backupmanager.return_codes import OK, ERRO_DADOS_INVALIDOS, obter_mensagem
from backupmanager.ui import ui_state
from backupmanager.ui.backup_flow import (
    atualizar_lista_origens_configuradas,
    salvar_tipo_selecionado_em_memoria,
    selecionar_origem_por_indice,
)
from backupmanager.ui.converters import (
    converter_data_opcional,
    converter_inteiro_opcional,
)
from backupmanager.ui.restrictions import (
    atualizar_checkboxes_extensoes,
    atualizar_lista_regras_nome,
    formulario_tipo_possui_valor_invalido,
    limpar_area_tipo_destino,
)
from backupmanager.ui.theme import COR_VERDE, criar_botao

__all__ = [
    "criar_area_botoes",
    "executar_backup_interface",
    "sincronizar_perfil_atual_interface",
    "preencher_formulario_com_perfil",
    "limpar_formulario",
    "mostrar_mensagem_resultado",
]


def criar_area_botoes(janela, estado_interface):
    """Cria os botoes globais do cabecalho da interface.

    Registra no estado o botao de backup, conecta comandos para backup e saida,
    e retorna o frame criado. Nao executa nenhuma acao no momento da criacao.
    """
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
    criar_botao(frame, "Sair", estado_interface["acao_fechar"], "#e5e7eb", "#111827", largura=76).pack(
        side="left", padx=(6, 0)
    )
    return frame


def executar_backup_interface(estado_interface):
    """Inicia a execucao de backup do perfil selecionado pela interface.

    Primeiro sincroniza os dados atuais do formulario com o controller, valida
    se ha perfil selecionado e impede execucoes simultaneas. Quando tudo esta
    valido, dispara uma thread para nao travar a janela.
    """
    codigo_salvar, perfil = sincronizar_perfil_atual_interface(estado_interface, True)
    if codigo_salvar != OK:
        return codigo_salvar

    perfil_id = perfil_manager.obter_id_perfil(perfil)
    if not perfil_id:
        mostrar_mensagem_resultado(ERRO_DADOS_INVALIDOS)
        return ERRO_DADOS_INVALIDOS

    if estado_interface.get("backup_em_execucao"):
        return OK

    estado_interface["backup_em_execucao"] = True
    _definir_estado_botao_backup(estado_interface, False)

    thread = threading.Thread(
        target=_executar_backup_em_thread,
        args=(estado_interface, perfil_id),
        daemon=True,
    )
    thread.start()
    return OK


def sincronizar_perfil_atual_interface(estado_interface, exibir_erros):
    """Sincroniza o formulario atual com o perfil em memoria.

    Coleta dados da tela, valida campos obrigatorios e chama
    `controller.salvar_perfil_editado`. Quando `exibir_erros` e verdadeiro,
    mostra mensagens de validacao ao usuario. Retorna `(codigo, perfil)`.
    """
    if not estado_interface.get("perfil_selecionado_id"):
        return ERRO_DADOS_INVALIDOS, None

    perfil = _obter_dados_formulario(estado_interface)
    if perfil is None:
        if exibir_erros:
            _mostrar_erro_validacao_formulario(estado_interface)
        return ERRO_DADOS_INVALIDOS, None

    codigo = controller.salvar_perfil_editado(perfil)
    if codigo != OK and exibir_erros:
        mostrar_mensagem_resultado(codigo)
    return codigo, perfil


def preencher_formulario_com_perfil(estado_interface, perfil):
    """Carrega os dados de um perfil nos widgets da interface.

    Atualiza nome, ativo, origens configuradas, selecao inicial e restricoes
    usando somente o modelo atual da aplicacao.
    """
    estado_interface["perfil_selecionado_id"] = perfil_manager.obter_id_perfil(perfil)
    _preencher_entry(estado_interface["entrada_nome"], perfil_manager.obter_nome_perfil(perfil))
    estado_interface["ativo_var"].set(perfil_manager.perfil_esta_ativo(perfil))
    estado_interface["operacao_var"].set("copiar")

    ui_state.definir_origens_configuradas(estado_interface, _montar_origens_configuradas_para_interface(perfil))
    ui_state.definir_origem_selecionada_indice(estado_interface, None)
    estado_interface["tipo_selecionado_indice"] = None
    atualizar_lista_origens_configuradas(estado_interface)
    limpar_area_tipo_destino(estado_interface)
    if ui_state.total_origens_configuradas(estado_interface):
        selecionar_origem_por_indice(estado_interface, 0)

    return perfil


def limpar_formulario(estado_interface):
    """Limpa todos os campos visuais ligados ao perfil selecionado.

    Remove listas de origem/tipo/destino, filtros e marcadores de selecao do
    estado da interface. Nao altera o controller diretamente.
    """
    _preencher_entry(estado_interface["entrada_nome"], "")
    ui_state.definir_origens_configuradas(estado_interface, [])
    ui_state.definir_origem_selecionada_indice(estado_interface, None)
    estado_interface["tipo_selecionado_indice"] = None
    _preencher_lista(estado_interface["lista_origens"], [])
    _preencher_lista(estado_interface["lista_tipos"], [])
    _preencher_lista(estado_interface["lista_destinos"], [])
    estado_interface["operacao_var"].set("copiar")
    estado_interface["ativo_var"].set(True)
    atualizar_checkboxes_extensoes(estado_interface, [])
    atualizar_lista_regras_nome(estado_interface, [])
    _preencher_entry(estado_interface["entrada_tamanho_min"], "")
    _preencher_entry(estado_interface["entrada_tamanho_max"], "")
    _preencher_entry(estado_interface["entrada_data_min"], "")
    _preencher_entry(estado_interface["entrada_data_max"], "")
    return OK


def mostrar_mensagem_resultado(codigo):
    """Mostra ao usuario a mensagem associada a um codigo de retorno.

    Usa `messagebox.showinfo` para `OK` e `messagebox.showerror` para erros.
    Retorna o proprio codigo para permitir encadeamento simples nos callbacks.
    """
    mensagem = obter_mensagem(codigo)
    if codigo == OK:
        messagebox.showinfo("BackupManager", mensagem)
    else:
        messagebox.showerror("BackupManager", mensagem)
    return codigo


def _executar_backup_em_thread(estado_interface, perfil_id):
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
        janela.after(0, lambda: _finalizar_backup_interface(estado_interface, codigo, resultado, erro))
    except tk.TclError:
        return


def _finalizar_backup_interface(estado_interface, codigo, resultado, erro):
    """Atualiza a interface apos o termino do backup."""
    estado_interface["backup_em_execucao"] = False
    _definir_estado_botao_backup(estado_interface, True)

    if erro is not None:
        messagebox.showerror("BackupManager", "Falha inesperada ao executar backup:\n" + str(erro))
        return ERRO_DADOS_INVALIDOS

    if resultado:
        mensagem = (
            obter_mensagem(codigo)
            + "\n\nArquivos processados: "
            + str(backup_result.obter_contador_resultado(resultado, "arquivos_processados"))
            + "\nCopiados: "
            + str(backup_result.obter_contador_resultado(resultado, "arquivos_copiados"))
            + "\nMovidos: "
            + str(backup_result.obter_contador_resultado(resultado, "arquivos_movidos"))
            + "\nRecortados: "
            + str(backup_result.obter_contador_resultado(resultado, "arquivos_recortados"))
        )
        if codigo == OK:
            messagebox.showinfo("BackupManager", mensagem)
        else:
            messagebox.showwarning("BackupManager", mensagem)
        return codigo

    mostrar_mensagem_resultado(codigo)
    return codigo


def _definir_estado_botao_backup(estado_interface, habilitado):
    """Habilita ou desabilita o botao de backup."""
    botao = estado_interface.get("botao_backup")
    if botao is None:
        return OK

    if habilitado:
        botao.configure(text="Backup", state="normal")
    else:
        botao.configure(text="Executando", state="disabled")
    return OK


def _obter_dados_formulario(estado_interface):
    """Coleta dados do formulario para um dicionario de perfil."""
    perfil_id = estado_interface.get("perfil_selecionado_id")
    if not perfil_id:
        return None

    salvar_tipo_selecionado_em_memoria(estado_interface)

    if (
        formulario_tipo_possui_valor_invalido(estado_interface)
        or not ui_state.total_origens_configuradas(estado_interface)
        or _existe_conflito_operacao_interface(estado_interface)
    ):
        return None

    return perfil_manager.criar_edicao_perfil(
        perfil_id,
        estado_interface["entrada_nome"].get(),
        ui_state.obter_origens_configuradas(estado_interface),
        estado_interface["ativo_var"].get(),
    )


def _montar_origens_configuradas_para_interface(perfil):
    """Copia as origens configuradas do perfil para uso seguro na interface."""
    origens_configuradas = perfil_manager.obter_origens_configuradas(perfil)
    if isinstance(origens_configuradas, list):
        return _copiar_lista_dicionarios(origens_configuradas)
    return []


def _copiar_lista_dicionarios(lista):
    """Copia lista simples de dicionarios aninhados."""
    copia = []
    for item in lista:
        if isinstance(item, dict):
            novo = {}
            for chave, valor in item.items():
                if isinstance(valor, list):
                    novo[chave] = _copiar_lista_dicionarios(valor)
                elif isinstance(valor, dict):
                    novo[chave] = valor.copy()
                else:
                    novo[chave] = valor
            copia.append(novo)
    return copia


def _preencher_lista(lista, itens):
    """Substitui os itens de uma listbox."""
    lista.delete(0, tk.END)
    for item in itens:
        lista.insert(tk.END, item)
    return OK


def _preencher_entry(entrada, valor):
    """Substitui o conteudo de um campo de texto."""
    entrada.delete(0, tk.END)
    entrada.insert(0, valor)
    return OK


def _mostrar_erro_validacao_formulario(estado_interface):
    """Mostra mensagem especifica para dados invalidos do formulario."""
    if not estado_interface.get("perfil_selecionado_id"):
        messagebox.showerror("BackupManager", "Selecione um perfil antes de aplicar alterações.")
        return ERRO_DADOS_INVALIDOS

    if not estado_interface["entrada_nome"].get().strip():
        messagebox.showerror("BackupManager", "Informe um nome para o perfil.")
        return ERRO_DADOS_INVALIDOS

    if not ui_state.total_origens_configuradas(estado_interface):
        messagebox.showerror("BackupManager", "Adicione pelo menos uma origem.")
        return ERRO_DADOS_INVALIDOS

    tamanho_min = converter_inteiro_opcional(estado_interface["entrada_tamanho_min"].get(), 0)
    tamanho_max = converter_inteiro_opcional(estado_interface["entrada_tamanho_max"].get(), None)
    if tamanho_min == "invalido" or tamanho_max == "invalido":
        messagebox.showerror("BackupManager", "Informe tamanhos validos usando numeros inteiros positivos.")
        return ERRO_DADOS_INVALIDOS

    data_min = converter_data_opcional(estado_interface["entrada_data_min"].get())
    data_max = converter_data_opcional(estado_interface["entrada_data_max"].get())
    if data_min == "invalido" or data_max == "invalido":
        messagebox.showerror("BackupManager", "Use datas no formato AAAA-MM-DD HH:MM:SS.")
        return ERRO_DADOS_INVALIDOS

    if _existe_conflito_operacao_interface(estado_interface):
        messagebox.showerror(
            "BackupManager",
            "Mover ou recortar so pode ser usado com um destino para o mesmo tipo de arquivo.",
        )
        return ERRO_DADOS_INVALIDOS

    messagebox.showerror("BackupManager", "Verifique os dados do formulario.")
    return ERRO_DADOS_INVALIDOS


def _existe_conflito_operacao_interface(estado_interface):
    """Verifica conflito visual de mover/recortar em multiplos destinos."""
    for origem in ui_state.obter_origens_configuradas(estado_interface):
        for tipo in perfil_manager.obter_tipos_origem(origem):
            destinos = perfil_manager.obter_destinos_tipo(tipo)
            if len(destinos) <= 1:
                continue
            for destino in destinos:
                if perfil_manager.obter_operacao_destino(destino) in ("mover", "recortar"):
                    return True
    return False
