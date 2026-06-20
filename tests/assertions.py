"""Funcoes auxiliares de assercao usadas pela suite pytest."""


def assert_equal(valor_obtido, valor_esperado, mensagem=None):
    """Falha se os dois valores comparados forem diferentes."""
    assert valor_obtido == valor_esperado, mensagem or f"{valor_obtido!r} != {valor_esperado!r}"


def assert_not_equal(valor_obtido, valor_inesperado, mensagem=None):
    """Falha se os dois valores comparados forem iguais."""
    assert valor_obtido != valor_inesperado, mensagem or f"{valor_obtido!r} == {valor_inesperado!r}"


def assert_true(valor, mensagem=None):
    """Falha se o valor recebido nao for verdadeiro."""
    assert valor, mensagem or f"{valor!r} nao e verdadeiro"


def assert_false(valor, mensagem=None):
    """Falha se o valor recebido nao for falso."""
    assert not valor, mensagem or f"{valor!r} nao e falso"


def assert_is_none(valor, mensagem=None):
    """Falha se o valor recebido nao for None."""
    assert valor is None, mensagem or f"{valor!r} nao e None"


def assert_is_not_none(valor, mensagem=None):
    """Falha se o valor recebido for None."""
    assert valor is not None, mensagem or "valor inesperadamente None"


def assert_is_instance(valor, tipo_esperado, mensagem=None):
    """Falha se o valor recebido nao for instancia do tipo esperado."""
    assert isinstance(valor, tipo_esperado), mensagem or f"{valor!r} nao e instancia de {tipo_esperado!r}"


def assert_in(valor, colecao, mensagem=None):
    """Falha se o valor recebido nao existir na colecao."""
    assert valor in colecao, mensagem or f"{valor!r} nao encontrado em {colecao!r}"


def assert_not_in(valor, colecao, mensagem=None):
    """Falha se o valor recebido existir na colecao."""
    assert valor not in colecao, mensagem or f"{valor!r} encontrado em {colecao!r}"
