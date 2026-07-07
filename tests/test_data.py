from data import seguros


def setup_function():
    seguros.resetar_dados()


def test_buscar_apolice_por_numero():
    ap = seguros.buscar_apolice("AUTO-1001")
    assert ap is not None
    assert ap["cliente"] == "Maria Silva"
    assert "roubo" in ap["coberturas"]


def test_buscar_apolice_por_cpf():
    ap = seguros.buscar_apolice("123.456.789-00")
    assert ap is not None
    assert ap["apolice_id"] == "AUTO-1001"


def test_buscar_apolice_inexistente_retorna_none():
    assert seguros.buscar_apolice("AUTO-9999") is None


def test_salvar_e_buscar_sinistro():
    protocolo = seguros.salvar_sinistro("AUTO-1001", "colisao", "Batida traseira")
    assert protocolo.startswith("SIN-")
    sin = seguros.buscar_sinistro(protocolo)
    assert sin is not None
    assert sin["apolice_id"] == "AUTO-1001"
    assert sin["status"] == "aberto"


def test_buscar_sinistro_inexistente_retorna_none():
    assert seguros.buscar_sinistro("SIN-0000") is None
