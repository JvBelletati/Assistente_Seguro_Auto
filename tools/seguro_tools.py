"""Ferramentas do agente de seguros — funções Python puras.

Cada função é uma "tool" que o LLM pode chamar. Não contêm lógica de LLM:
recebem argumentos simples, consultam/alteram os dados e retornam um dict claro.
As docstrings e type hints são lidos pelo Agno para descrever a tool ao modelo.
"""

from data import seguros


def consultar_apolice(identificador: str) -> dict:
    """Consulta uma apólice de seguro auto pelo número da apólice ou CPF do cliente.

    Args:
        identificador: número da apólice (ex.: 'AUTO-1001') ou CPF (ex.: '123.456.789-00').

    Returns:
        Dados da apólice, ou {'erro': ...} se não encontrada.
    """
    apolice = seguros.buscar_apolice(identificador)
    if apolice is None:
        return {"erro": f"Nenhuma apólice encontrada para '{identificador}'."}
    return apolice


def verificar_cobertura(apolice_id: str, tipo_evento: str) -> dict:
    """Verifica se um tipo de evento está coberto por uma apólice.

    Args:
        apolice_id: número da apólice (ex.: 'AUTO-1001').
        tipo_evento: evento a verificar (ex.: 'roubo', 'colisao', 'incendio', 'terceiros').

    Returns:
        {'coberto': bool, ...} ou {'erro': ...} se a apólice não existir.
    """
    apolice = seguros.buscar_apolice(apolice_id)
    if apolice is None:
        return {"erro": f"Apólice '{apolice_id}' não encontrada."}
    evento = tipo_evento.strip().lower()
    coberto = evento in [c.lower() for c in apolice["coberturas"]]
    return {
        "apolice_id": apolice["apolice_id"],
        "tipo_evento": evento,
        "coberto": coberto,
        "coberturas": apolice["coberturas"],
    }


def abrir_sinistro(apolice_id: str, tipo_evento: str, descricao: str) -> dict:
    """Abre um sinistro para uma apólice e gera um número de protocolo.

    Args:
        apolice_id: número da apólice (ex.: 'AUTO-1001').
        tipo_evento: tipo do sinistro (ex.: 'roubo', 'colisao').
        descricao: descrição livre do ocorrido.

    Returns:
        {'protocolo': ..., 'status': 'aberto', ...} ou {'erro': ...}.
    """
    apolice = seguros.buscar_apolice(apolice_id)
    if apolice is None:
        return {"erro": f"Apólice '{apolice_id}' não encontrada. Não foi possível abrir o sinistro."}
    protocolo = seguros.salvar_sinistro(apolice["apolice_id"], tipo_evento.strip().lower(), descricao)
    return {
        "protocolo": protocolo,
        "apolice_id": apolice["apolice_id"],
        "tipo_evento": tipo_evento.strip().lower(),
        "status": "aberto",
    }


def acompanhar_sinistro(protocolo: str) -> dict:
    """Consulta o status atual de um sinistro pelo número de protocolo.

    Args:
        protocolo: número do protocolo (ex.: 'SIN-5001').

    Returns:
        Dados do sinistro com o status, ou {'erro': ...} se não existir.
    """
    sinistro = seguros.buscar_sinistro(protocolo)
    if sinistro is None:
        return {"erro": f"Protocolo '{protocolo}' não encontrado."}
    return sinistro
