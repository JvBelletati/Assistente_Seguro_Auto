"""Demonstração DIDÁTICA: o loop de um agente escrito à mão com o SDK da Anthropic.

O agente Agno (agente.py) faz tudo isto automaticamente. Aqui o loop de
tool-calling é explícito, para mostrar que entendemos os fundamentos.
Para manter curto, ligamos só 2 das 4 ferramentas — o padrão é idêntico para as demais.

Rode:  python core_demo.py   (requer ANTHROPIC_API_KEY no .env)
"""

import os
import json

from dotenv import load_dotenv
import anthropic

from prompts.system import SYSTEM_PROMPT
from tools import seguro_tools

load_dotenv()

MODELO = "claude-haiku-4-5-20251001"

# 1) Descrevemos as ferramentas ao Claude via JSON schema (no Agno isto é automático).
TOOLS = [
    {
        "name": "consultar_apolice",
        "description": "Consulta uma apólice de seguro auto por número ou CPF.",
        "input_schema": {
            "type": "object",
            "properties": {"identificador": {"type": "string"}},
            "required": ["identificador"],
        },
    },
    {
        "name": "verificar_cobertura",
        "description": "Verifica se um evento está coberto por uma apólice.",
        "input_schema": {
            "type": "object",
            "properties": {
                "apolice_id": {"type": "string"},
                "tipo_evento": {"type": "string"},
            },
            "required": ["apolice_id", "tipo_evento"],
        },
    },
]

# Mapa nome-da-tool -> função Python que a executa.
DISPATCH = {
    "consultar_apolice": seguro_tools.consultar_apolice,
    "verificar_cobertura": seguro_tools.verificar_cobertura,
}


def main() -> None:
    if not os.getenv("ANTHROPIC_API_KEY"):
        raise SystemExit("Configure ANTHROPIC_API_KEY no .env (veja .env.example).")

    client = anthropic.Anthropic()
    pergunta = "Meu CPF é 123.456.789-00. O roubo do meu carro está coberto?"
    messages = [{"role": "user", "content": pergunta}]
    print(f"Usuário: {pergunta}\n")

    # 2) Loop do agente: chama o modelo, executa tools que ele pedir, repete até a resposta final.
    while True:
        resp = client.messages.create(
            model=MODELO,
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            tools=TOOLS,
            messages=messages,
        )

        if resp.stop_reason == "tool_use":
            messages.append({"role": "assistant", "content": resp.content})
            resultados = []
            for bloco in resp.content:
                if bloco.type == "tool_use":
                    print(f"[tool] {bloco.name}({bloco.input})")
                    funcao = DISPATCH[bloco.name]
                    resultado = funcao(**bloco.input)
                    resultados.append({
                        "type": "tool_result",
                        "tool_use_id": bloco.id,
                        "content": json.dumps(resultado, ensure_ascii=False),
                    })
            messages.append({"role": "user", "content": resultados})
            continue

        texto = "".join(b.text for b in resp.content if b.type == "text")
        print(f"\nAgente: {texto}")
        break


if __name__ == "__main__":
    main()
