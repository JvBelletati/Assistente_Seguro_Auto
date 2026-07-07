from data import seguros
from tools import seguro_tools


def setup_function():
    seguros.resetar_dados()


def test_consultar_apolice_por_numero():
    r = seguro_tools.consultar_apolice("AUTO-1001")
    assert r["cliente"] == "Maria Silva"
    assert "erro" not in r


def test_consultar_apolice_por_cpf():
    r = seguro_tools.consultar_apolice("123.456.789-00")
    assert r["apolice_id"] == "AUTO-1001"


def test_consultar_apolice_inexistente():
    r = seguro_tools.consultar_apolice("AUTO-9999")
    assert "erro" in r


def test_verificar_cobertura_coberto():
    r = seguro_tools.verificar_cobertura("AUTO-1001", "roubo")
    assert r["coberto"] is True


def test_verificar_cobertura_nao_coberto():
    r = seguro_tools.verificar_cobertura("AUTO-1002", "roubo")
    assert r["coberto"] is False


def test_verificar_cobertura_apolice_inexistente():
    r = seguro_tools.verificar_cobertura("AUTO-9999", "roubo")
    assert "erro" in r


def test_abrir_e_acompanhar_sinistro():
    aberto = seguro_tools.abrir_sinistro("AUTO-1001", "colisao", "Batida no estacionamento")
    assert "protocolo" in aberto
    protocolo = aberto["protocolo"]

    status = seguro_tools.acompanhar_sinistro(protocolo)
    assert status["protocolo"] == protocolo
    assert status["status"] == "aberto"


def test_abrir_sinistro_apolice_inexistente():
    r = seguro_tools.abrir_sinistro("AUTO-9999", "colisao", "x")
    assert "erro" in r


def test_acompanhar_sinistro_inexistente():
    r = seguro_tools.acompanhar_sinistro("SIN-0000")
    assert "erro" in r
