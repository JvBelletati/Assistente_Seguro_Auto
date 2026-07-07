"""Fonte de dados fictícia em memória para o agente de seguros.

Simula o "sistema" da seguradora: apólices cadastradas e sinistros abertos.
Nenhuma dependência de LLM ou I/O externo — só estruturas Python.
"""

# Estado inicial imutável usado para (re)inicializar os dados.
_APOLICES_INICIAIS = [
    {
        "apolice_id": "AUTO-1001",
        "cliente": "Maria Silva",
        "cpf": "123.456.789-00",
        "veiculo": "Honda Civic 2020",
        "coberturas": ["roubo", "colisao", "incendio", "terceiros"],
        "franquia": 2500.00,
        "vigencia": "2026-01-01 a 2026-12-31",
    },
    {
        "apolice_id": "AUTO-1002",
        "cliente": "Joao Souza",
        "cpf": "987.654.321-00",
        "veiculo": "Toyota Corolla 2019",
        "coberturas": ["colisao", "terceiros"],  # sem cobertura de roubo (bom p/ demo)
        "franquia": 3000.00,
        "vigencia": "2026-03-01 a 2027-02-28",
    },
]

_SINISTROS_INICIAIS = [
    {
        "protocolo": "SIN-5001",
        "apolice_id": "AUTO-1001",
        "tipo_evento": "colisao",
        "descricao": "Colisao em cruzamento",
        "status": "em analise",
    },
]

# Estado mutável de runtime.
_apolices: list[dict] = []
_sinistros: list[dict] = []
# Deve começar acima do maior protocolo semeado (SIN-5001) para não colidir.
# Se adicionar novos sinistros iniciais, ajuste este valor.
_proximo_num: int = 5002


def resetar_dados() -> None:
    """Restaura o estado inicial. Usado por testes e ao subir o app."""
    global _apolices, _sinistros, _proximo_num
    _apolices = [dict(a) for a in _APOLICES_INICIAIS]
    _sinistros = [dict(s) for s in _SINISTROS_INICIAIS]
    _proximo_num = 5002


def buscar_apolice(identificador: str) -> dict | None:
    """Busca uma apólice por número (ex.: 'AUTO-1001') ou por CPF."""
    alvo = identificador.strip()
    for ap in _apolices:
        if ap["apolice_id"].lower() == alvo.lower() or ap["cpf"] == alvo:
            return ap
    return None


def buscar_sinistro(protocolo: str) -> dict | None:
    """Busca um sinistro pelo número de protocolo."""
    alvo = protocolo.strip().lower()
    for sin in _sinistros:
        if sin["protocolo"].lower() == alvo:
            return sin
    return None


def salvar_sinistro(apolice_id: str, tipo_evento: str, descricao: str) -> str:
    """Cria e grava um novo sinistro. Retorna o protocolo gerado."""
    global _proximo_num
    protocolo = f"SIN-{_proximo_num}"
    _proximo_num += 1
    _sinistros.append({
        "protocolo": protocolo,
        "apolice_id": apolice_id,
        "tipo_evento": tipo_evento,
        "descricao": descricao,
        "status": "aberto",
    })
    return protocolo


# Inicializa o estado ao importar o módulo.
resetar_dados()
