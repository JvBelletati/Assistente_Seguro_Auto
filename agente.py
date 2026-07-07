"""Agente de atendimento de seguros: Claude + Agno, com memória em SQLite.

As ferramentas (funções puras) são registradas no Agno, que cuida do loop de
tool-calling e do histórico conversacional automaticamente.
"""

import os

from dotenv import load_dotenv
from agno.agent import Agent
from agno.models.anthropic import Claude
from agno.db.sqlite import SqliteDb

from prompts.system import SYSTEM_PROMPT
from tools.seguro_tools import (
    consultar_apolice,
    verificar_cobertura,
    abrir_sinistro,
    acompanhar_sinistro,
)

load_dotenv()

MODELO = "claude-haiku-4-5-20251001"  # trocável por um modelo maior numa linha
DB_FILE = "seguro_agent.db"


def criar_agente() -> Agent:
    """Cria o agente Agno configurado com Claude, as ferramentas e memória.

    Levanta RuntimeError com mensagem clara se a ANTHROPIC_API_KEY não estiver definida.
    """
    if not os.getenv("ANTHROPIC_API_KEY"):
        raise RuntimeError(
            "ANTHROPIC_API_KEY não encontrada. Crie um arquivo .env na raiz com "
            "ANTHROPIC_API_KEY=sk-ant-... (use .env.example como modelo)."
        )

    db = SqliteDb(db_file=DB_FILE)
    return Agent(
        model=Claude(id=MODELO),
        db=db,
        tools=[consultar_apolice, verificar_cobertura, abrir_sinistro, acompanhar_sinistro],
        instructions=SYSTEM_PROMPT,
        add_history_to_context=True,   # inclui o histórico da sessão no contexto
        num_history_runs=5,            # últimas 5 interações
        markdown=True,
    )


def responder(agente: Agent, mensagem: str,
              session_id: str = "demo", user_id: str = "cliente-demo") -> str:
    """Envia uma mensagem ao agente e retorna o texto da resposta."""
    resposta = agente.run(mensagem, session_id=session_id, user_id=user_id)
    return resposta.content


if __name__ == "__main__":
    # Smoke test manual pela linha de comando (requer ANTHROPIC_API_KEY no .env).
    ag = criar_agente()
    print(responder(ag, "Olá! Meu CPF é 123.456.789-00. Quais são minhas coberturas?"))
