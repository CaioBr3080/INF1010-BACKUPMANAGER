"""Codigos de retorno padronizados do BackupManager."""

__all__ = [
    "OK",
    "ERRO_PERFIL_NAO_ENCONTRADO",
    "ERRO_NOME_INVALIDO",
    "ERRO_ORIGEM_INVALIDA",
    "ERRO_DESTINO_INVALIDO",
    "ERRO_SEM_PERMISSAO",
    "ERRO_ARQUIVO_NAO_ENCONTRADO",
    "ERRO_RESTRICAO_INVALIDA",
    "ERRO_OPERACAO_INVALIDA",
    "ERRO_FALHA_AO_COPIAR",
    "ERRO_FALHA_AO_MOVER",
    "ERRO_JSON_CORROMPIDO",
    "ERRO_BACKUP_SEM_ARQUIVOS",
    "ERRO_DESTINO_SEM_ESPACO",
    "ERRO_PERFIL_INATIVO",
    "ERRO_DADOS_INVALIDOS",
    "obter_mensagem",
]

OK = 0

ERRO_PERFIL_NAO_ENCONTRADO = 1
ERRO_NOME_INVALIDO = 2
ERRO_ORIGEM_INVALIDA = 3
ERRO_DESTINO_INVALIDO = 4
ERRO_SEM_PERMISSAO = 5
ERRO_ARQUIVO_NAO_ENCONTRADO = 6
ERRO_RESTRICAO_INVALIDA = 7
ERRO_OPERACAO_INVALIDA = 8
ERRO_FALHA_AO_COPIAR = 10
ERRO_FALHA_AO_MOVER = 11
ERRO_JSON_CORROMPIDO = 12
ERRO_BACKUP_SEM_ARQUIVOS = 13
ERRO_DESTINO_SEM_ESPACO = 14
ERRO_PERFIL_INATIVO = 15
ERRO_DADOS_INVALIDOS = 16

_MENSAGENS = {
    OK: "Operacao realizada com sucesso.",
    ERRO_PERFIL_NAO_ENCONTRADO: "Perfil nao encontrado.",
    ERRO_NOME_INVALIDO: "Nome de perfil invalido.",
    ERRO_ORIGEM_INVALIDA: "Origem invalida.",
    ERRO_DESTINO_INVALIDO: "Destino invalido.",
    ERRO_SEM_PERMISSAO: "Sem permissao para acessar o caminho.",
    ERRO_ARQUIVO_NAO_ENCONTRADO: "Arquivo nao encontrado.",
    ERRO_RESTRICAO_INVALIDA: "Restricao invalida.",
    ERRO_OPERACAO_INVALIDA: "Operacao invalida.",
    ERRO_FALHA_AO_COPIAR: "Falha ao copiar arquivo.",
    ERRO_FALHA_AO_MOVER: "Falha ao mover arquivo.",
    ERRO_JSON_CORROMPIDO: "Arquivo JSON corrompido.",
    ERRO_BACKUP_SEM_ARQUIVOS: "Nenhum arquivo encontrado para backup.",
    ERRO_DESTINO_SEM_ESPACO: "Destino sem espaco disponivel.",
    ERRO_PERFIL_INATIVO: "Perfil inativo.",
    ERRO_DADOS_INVALIDOS: "Dados invalidos.",
}


def obter_mensagem(codigo):
    """Retorna a mensagem de usuario associada a um codigo de retorno.

    Recebe um inteiro padronizado pelos modulos da aplicacao e devolve texto
    legivel para interface/logs. Codigos desconhecidos retornam mensagem
    generica, sem levantar excecao.
    """
    return _MENSAGENS.get(codigo, "Codigo de retorno desconhecido.")
