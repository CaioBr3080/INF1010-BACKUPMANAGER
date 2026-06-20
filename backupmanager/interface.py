"""Interface grafica do BackupManager usando tkinter e customtkinter."""

import customtkinter as ctk

from backupmanager import controller
from backupmanager.return_codes import OK
from backupmanager.ui_actions import criar_area_botoes, mostrar_mensagem_resultado, sincronizar_perfil_atual_interface
from backupmanager.ui_backup_flow import criar_area_origens_destinos, salvar_tipo_selecionado_em_memoria
from backupmanager.ui_profiles import atualizar_lista_perfis, criar_area_perfis
from backupmanager.ui_restrictions import criar_area_restricoes
from backupmanager.ui_theme import (
    COR_FUNDO,
    COR_TEXTO,
    COR_TEXTO_FRACO,
    FONTE_FAMILIA,
    FONTE_TITULO,
    configurar_estilo_visual,
    configurar_frame,
    trazer_janela_para_frente,
)

__all__ = ["iniciar_interface"]


def iniciar_interface():
    """Inicia a interface grafica principal do BackupManager.

    Inicializa o controller, cria a janela, registra o fechamento seguro,
    monta cabecalho, painel de perfis, fluxo de backup e restricoes. Esta e a
    unica funcao publica do modulo de interface.
    """
    codigo = controller.inicializar_aplicacao()
    if codigo != OK:
        mostrar_mensagem_resultado(codigo)

    estado_interface = _criar_estado_interface()
    janela = _criar_janela_principal()
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
    criar_area_restricoes(
        frame_central,
        estado_interface,
        lambda: salvar_tipo_selecionado_em_memoria(estado_interface),
    )
    atualizar_lista_perfis(estado_interface)

    janela.mainloop()


def _criar_estado_interface():
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
        "entrada_regra_nome": None,
        "modo_regra_nome_var": None,
        "lista_regras_nome": None,
        "regras_nome": [],
        "entrada_tamanho_min": None,
        "entrada_tamanho_max": None,
        "entrada_data_min": None,
        "entrada_data_max": None,
        "perfil_selecionado_id": None,
        "origens_configuradas": [],
        "origem_selecionada_indice": None,
        "tipo_selecionado_indice": None,
        "botao_backup": None,
        "backup_em_execucao": False,
    }


def _criar_janela_principal():
    """Cria a janela principal."""
    configurar_estilo_visual()
    janela = ctk.CTk()
    janela.title("BackupManager")
    janela.geometry("1180x720")
    janela.minsize(980, 620)
    janela.configure(fg_color=COR_FUNDO)
    return janela


