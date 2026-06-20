"""Ponto de entrada do BackupManager."""

from backupmanager.ui.interface import iniciar_interface

__all__ = ["main"]


def main():
    """Ponto de entrada executavel da aplicacao.

    Chama `iniciar_interface` e entrega o controle ao loop grafico. Mantem o
    arquivo `main.py` como fachada minima para execucao com `python -m`.
    """
    iniciar_interface()


if __name__ == "__main__":
    main()
