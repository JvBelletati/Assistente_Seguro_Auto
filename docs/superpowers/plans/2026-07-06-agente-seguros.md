# Agente de Atendimento de Seguro Auto — Plano de Implementação

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Construir um agente de IA de atendimento de seguro auto (Claude + Agno) com ferramentas puras, memória SQLite, interface Streamlit e um script didático do loop cru do SDK Anthropic, para apresentar em entrevista.

**Architecture:** Lógica de negócio em funções Python puras (`tools/`, `data/`) sem LLM, testáveis isoladamente. Um agente Agno (`agente.py`) embrulha essas funções e adiciona memória. Um script `core_demo.py` mostra o mesmo loop de tool-calling escrito à mão. UI de chat em Streamlit (`app.py`).

**Tech Stack:** Python 3.12, Agno 2.6+, Anthropic SDK, Streamlit, python-dotenv, pytest.

## Global Constraints

- Python 3.12 (já instalado).
- Modelo Claude: `claude-haiku-4-5-20251001` (constante `MODELO`), trocável numa linha.
- LLM: Claude via Agno (`from agno.models.anthropic import Claude`) e via SDK direto (`anthropic`) no `core_demo.py`.
- Agno v2 API: `from agno.agent import Agent`, `from agno.db.sqlite import SqliteDb`, ferramentas via `tools=[func, ...]`, resposta via `agente.run(msg, session_id=..., user_id=...).content`.
- Segredos: `ANTHROPIC_API_KEY` só em `.env` (nunca no código). `.env` no `.gitignore`; `.env.example` versionado.
- Idioma de todo texto voltado ao usuário: português do Brasil.
- Todos os comandos assumem execução a partir da raiz do projeto `C:\Users\jvbel\Downloads\Projetos\Agent_IA`, em PowerShell.
- Ferramentas do agente são funções puras: sem chamadas de LLM, sem I/O externo, retornam `dict` com sucesso ou `{"erro": "..."}`.

## Estrutura de arquivos

```
.env / .env.example          # chave da API (real fora do Git)
.gitignore
requirements.txt
README.md
data/__init__.py
data/seguros.py              # dados fictícios em memória + helpers de acesso
tools/__init__.py
tools/seguro_tools.py        # 4 ferramentas (funções puras)
prompts/__init__.py
prompts/system.py            # persona/instruções do agente
agente.py                    # agente Agno + Claude + memória (coração)
core_demo.py                 # loop cru do SDK Anthropic (didático)
app.py                       # interface Streamlit
tests/test_data.py           # testes dos helpers de dados
tests/test_tools.py          # testes das 4 ferramentas
```

---

### Task 1: Scaffolding e dependências

**Files:**
- Create: `requirements.txt`, `.gitignore`, `.env.example`
- Create: `data/__init__.py`, `tools/__init__.py`, `prompts/__init__.py` (vazios)

**Interfaces:**
- Consumes: nada.
- Produces: ambiente instalável e estrutura de pacotes; nenhum símbolo de código.

- [ ] **Step 1: Criar `requirements.txt`**

```
agno>=2.6,<3
anthropic>=0.40
streamlit>=1.40
python-dotenv>=1.0
pytest>=8.0
```

- [ ] **Step 2: Criar `.gitignore`**

```
.env
__pycache__/
*.pyc
*.db
.pytest_cache/
.venv/
venv/
```

- [ ] **Step 3: Criar `.env.example`**

```
ANTHROPIC_API_KEY=sk-ant-cole-sua-chave-aqui
```

- [ ] **Step 4: Criar os `__init__.py` vazios dos pacotes**

Criar três arquivos vazios: `data/__init__.py`, `tools/__init__.py`, `prompts/__init__.py`.

- [ ] **Step 5: Criar o ambiente virtual e instalar dependências**

Run:
```
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```
Expected: instalação conclui sem erro; `pip list` mostra `agno`, `anthropic`, `streamlit`, `pytest`.

- [ ] **Step 6: Verificar que os pacotes importam**

Run:
```
.venv\Scripts\python.exe -c "import agno, anthropic, streamlit, dotenv; print('imports OK')"
```
Expected: imprime `imports OK`.

- [ ] **Step 7: Commit**

```
git add requirements.txt .gitignore .env.example data/__init__.py tools/__init__.py prompts/__init__.py
git commit -m "chore: scaffolding do projeto e dependencias"
```

---

### Task 2: Dados fictícios (`data/seguros.py`)

**Files:**
- Create: `data/seguros.py`
- Test: `tests/test_data.py`

**Interfaces:**
- Consumes: nada.
- Produces:
  - `buscar_apolice(identificador: str) -> dict | None` — casa por número da apólice OU CPF.
  - `buscar_sinistro(protocolo: str) -> dict | None`.
  - `salvar_sinistro(apolice_id: str, tipo_evento: str, descricao: str) -> str` — cria e grava um sinistro, retorna o protocolo.
  - `resetar_dados() -> None` — restaura o estado inicial (uso em testes).
  - Estrutura de apólice: `{"apolice_id", "cliente", "cpf", "veiculo", "coberturas": list[str], "franquia": float, "vigencia": str}`.
  - Estrutura de sinistro: `{"protocolo", "apolice_id", "tipo_evento", "descricao", "status"}`.

- [ ] **Step 1: Escrever os testes que falham (`tests/test_data.py`)**

```python
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
```

- [ ] **Step 2: Rodar os testes e confirmar que falham**

Run: `.venv\Scripts\python.exe -m pytest tests/test_data.py -v`
Expected: FAIL (`ModuleNotFoundError: No module named 'data.seguros'` ou `AttributeError`).

- [ ] **Step 3: Implementar `data/seguros.py`**

```python
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
```

- [ ] **Step 4: Rodar os testes e confirmar que passam**

Run: `.venv\Scripts\python.exe -m pytest tests/test_data.py -v`
Expected: PASS (5 testes).

- [ ] **Step 5: Commit**

```
git add data/seguros.py tests/test_data.py
git commit -m "feat: dados ficticios de apolices e sinistros"
```

---

### Task 3: As 4 ferramentas (`tools/seguro_tools.py`)

**Files:**
- Create: `tools/seguro_tools.py`
- Test: `tests/test_tools.py`

**Interfaces:**
- Consumes: `data.seguros.buscar_apolice`, `buscar_sinistro`, `salvar_sinistro`, `resetar_dados`.
- Produces (estas assinaturas são registradas como tools no agente e no core_demo):
  - `consultar_apolice(identificador: str) -> dict`
  - `verificar_cobertura(apolice_id: str, tipo_evento: str) -> dict`
  - `abrir_sinistro(apolice_id: str, tipo_evento: str, descricao: str) -> dict`
  - `acompanhar_sinistro(protocolo: str) -> dict`

- [ ] **Step 1: Escrever os testes que falham (`tests/test_tools.py`)**

```python
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
```

- [ ] **Step 2: Rodar os testes e confirmar que falham**

Run: `.venv\Scripts\python.exe -m pytest tests/test_tools.py -v`
Expected: FAIL (`ModuleNotFoundError: No module named 'tools.seguro_tools'`).

- [ ] **Step 3: Implementar `tools/seguro_tools.py`**

```python
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
```

- [ ] **Step 4: Rodar todos os testes e confirmar que passam**

Run: `.venv\Scripts\python.exe -m pytest -v`
Expected: PASS (todos os testes de `test_data.py` e `test_tools.py`).

- [ ] **Step 5: Commit**

```
git add tools/seguro_tools.py tests/test_tools.py
git commit -m "feat: 4 ferramentas do agente (consultar, verificar, abrir, acompanhar)"
```

---

### Task 4: Persona e agente Agno (`prompts/system.py`, `agente.py`)

**Files:**
- Create: `prompts/system.py`
- Create: `agente.py`

**Interfaces:**
- Consumes: `SYSTEM_PROMPT` (de `prompts.system`); as 4 tools de `tools.seguro_tools`.
- Produces:
  - `SYSTEM_PROMPT: str`
  - `criar_agente() -> agno.agent.Agent`
  - `responder(agente, mensagem: str, session_id: str = "demo", user_id: str = "cliente-demo") -> str`
  - `MODELO: str` (constante com o id do modelo).

- [ ] **Step 1: Criar `prompts/system.py`**

```python
"""Persona e instruções do agente de atendimento de seguros."""

SYSTEM_PROMPT = """Você é um atendente virtual de uma seguradora de automóveis.
Fale sempre em português do Brasil, com tom profissional, cordial e objetivo.

Suas capacidades (via ferramentas):
- Consultar apólices por número ou CPF.
- Verificar se um evento está coberto por uma apólice.
- Abrir sinistros (gera um número de protocolo).
- Acompanhar o status de um sinistro pelo protocolo.

Regras importantes:
- NUNCA invente dados de apólice, cobertura ou sinistro. Use sempre as ferramentas.
- Se uma cobertura não estiver na apólice, diga claramente que NÃO está coberta.
- Antes de abrir um sinistro, confirme com o cliente os dados (apólice, tipo de evento
  e descrição). Só abra depois da confirmação.
- Se o cliente já se identificou na conversa, não peça o CPF novamente.
- Seja transparente sobre franquia e coberturas quando relevante.
"""
```

- [ ] **Step 2: Criar `agente.py`**

```python
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
```

- [ ] **Step 3: Verificar que o módulo importa sem a chave (não deve chamar a API na importação)**

Run: `.venv\Scripts\python.exe -c "import agente; print(agente.MODELO)"`
Expected: imprime `claude-haiku-4-5-20251001` sem erro (a importação não instancia o agente).

- [ ] **Step 4: Smoke test ao vivo (requer `.env` com a chave)**

Pré-requisito: criar `.env` a partir de `.env.example` e colar a `ANTHROPIC_API_KEY` real.
Run: `.venv\Scripts\python.exe agente.py`
Expected: o agente responde em português listando as coberturas da apólice AUTO-1001 (roubo, colisão, incêndio, terceiros), tendo chamado a ferramenta `consultar_apolice`.

Nota: este passo depende de rede e de crédito na conta Anthropic. Se a chave ainda não estiver disponível, marque o passo como pendente e siga; ele será validado ao ensaiar a demo.

- [ ] **Step 5: Commit**

```
git add prompts/system.py agente.py
git commit -m "feat: agente Agno com Claude, ferramentas e memoria"
```

---

### Task 5: Script didático do loop cru (`core_demo.py`)

**Files:**
- Create: `core_demo.py`

**Interfaces:**
- Consumes: `SYSTEM_PROMPT`; `tools.seguro_tools.consultar_apolice` e `verificar_cobertura`; SDK `anthropic`.
- Produces: script executável `python core_demo.py` (sem símbolos importados por outros módulos).

- [ ] **Step 1: Criar `core_demo.py`**

```python
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
```

- [ ] **Step 2: Verificar sintaxe/import sem chamar a API**

Run: `.venv\Scripts\python.exe -c "import core_demo; print('core_demo OK')"`
Expected: imprime `core_demo OK` (o código da API só roda dentro de `main()`).

- [ ] **Step 3: Smoke test ao vivo (requer `.env` com a chave)**

Run: `.venv\Scripts\python.exe core_demo.py`
Expected: imprime a pergunta, uma linha `[tool] consultar_apolice(...)` (e possivelmente `verificar_cobertura(...)`), e uma resposta final dizendo que o roubo ESTÁ coberto para a apólice AUTO-1001.

Nota: depende de rede/crédito. Se a chave não estiver disponível ainda, deixe pendente e valide no ensaio.

- [ ] **Step 4: Commit**

```
git add core_demo.py
git commit -m "feat: core_demo didatico do loop cru do SDK Anthropic"
```

---

### Task 6: Interface Streamlit (`app.py`)

**Files:**
- Create: `app.py`

**Interfaces:**
- Consumes: `agente.criar_agente`, `agente.responder`.
- Produces: app executável `streamlit run app.py`.

- [ ] **Step 1: Criar `app.py`**

```python
"""Interface web de chat para o agente de seguros (Streamlit)."""

import streamlit as st

from agente import criar_agente, responder

st.set_page_config(page_title="Assistente de Seguro Auto", page_icon="🚗")
st.title("🚗 Assistente de Seguro Auto")
st.caption("Agente de IA (Claude + Agno) — consulta apólices, coberturas e sinistros.")

# Cria o agente uma vez por sessão do navegador.
if "agente" not in st.session_state:
    try:
        st.session_state.agente = criar_agente()
    except RuntimeError as e:
        st.error(str(e))
        st.stop()
    st.session_state.mensagens = []

# Barra lateral com dados de teste, para facilitar a demonstração ao vivo.
with st.sidebar:
    st.subheader("Dados de teste")
    st.markdown(
        "- **Maria Silva** — CPF `123.456.789-00` — apólice `AUTO-1001` "
        "(roubo, colisão, incêndio, terceiros)\n"
        "- **João Souza** — CPF `987.654.321-00` — apólice `AUTO-1002` "
        "(colisão, terceiros — **sem roubo**)\n"
        "- Sinistro existente: protocolo `SIN-5001`"
    )

# Reexibe o histórico da conversa.
for m in st.session_state.mensagens:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# Campo de entrada do chat.
if pergunta := st.chat_input("Como posso ajudar com seu seguro?"):
    st.session_state.mensagens.append({"role": "user", "content": pergunta})
    with st.chat_message("user"):
        st.markdown(pergunta)

    with st.chat_message("assistant"):
        with st.spinner("Consultando..."):
            try:
                resposta = responder(st.session_state.agente, pergunta)
            except Exception as e:  # falha de rede/API — mensagem amigável
                resposta = f"Desculpe, tive um problema ao processar sua solicitação: {e}"
        st.markdown(resposta)

    st.session_state.mensagens.append({"role": "assistant", "content": resposta})
```

- [ ] **Step 2: Verificar que o app sobe sem erro de import**

Run (inicia o servidor; observe os logs, depois encerre com Ctrl+C):
```
.venv\Scripts\python.exe -m streamlit run app.py
```
Expected: o Streamlit imprime a URL local (ex.: `http://localhost:8501`) sem stack trace. Se `.env` não estiver configurado, a página mostra a mensagem de erro amigável pedindo a `ANTHROPIC_API_KEY` (comportamento correto).

- [ ] **Step 3: Verificação manual ao vivo (requer `.env` com a chave)**

Abrir a URL no navegador e testar o roteiro:
1. "Meu CPF é 123.456.789-00, quais minhas coberturas?" → lista as coberturas.
2. "Meu carro foi roubado, estou coberto?" → responde que SIM, sem pedir o CPF de novo (memória de sessão).
3. "Quero abrir o sinistro." → o agente confirma os dados antes; ao confirmar, retorna um protocolo `SIN-XXXX`.
Expected: as três interações funcionam e a memória de sessão evita repetir o CPF.

- [ ] **Step 4: Commit**

```
git add app.py
git commit -m "feat: interface Streamlit de chat do agente"
```

---

### Task 7: README com roteiro de demo e falas para a entrevista

**Files:**
- Create: `README.md`

**Interfaces:**
- Consumes: nada (documentação).
- Produces: `README.md`.

- [ ] **Step 1: Criar `README.md`**

````markdown
# Assistente de Seguro Auto — Agente de IA

Agente de IA de atendimento de seguro auto: consulta apólices, verifica coberturas,
abre e acompanha sinistros, com **memória conversacional**. Construído em **Python** com
**Claude (Anthropic)** e o framework **Agno**, com interface de chat em **Streamlit**.

## Arquitetura

- `data/seguros.py` — dados fictícios (apólices e sinistros) em memória.
- `tools/seguro_tools.py` — as 4 ferramentas do agente, como **funções Python puras** (sem LLM).
- `prompts/system.py` — persona e regras do agente.
- `agente.py` — o agente **Agno + Claude**, com memória em SQLite. É o coração do projeto.
- `core_demo.py` — o **mesmo loop de tool-calling escrito à mão** com o SDK da Anthropic
  (artefato didático: mostra o que o Agno faz por baixo dos panos).
- `app.py` — interface de chat em Streamlit.
- `tests/` — testes `pytest` das ferramentas e dos dados.

Ideia central: a lógica de negócio (ferramentas) é isolada e testável; o "motor" do agente
apenas a embrulha. Dá para trocar Agno pelo loop cru sem mexer nas ferramentas.

## Como rodar

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# configure a chave da API
copy .env.example .env
# edite .env e cole sua ANTHROPIC_API_KEY (https://console.anthropic.com/settings/keys)

# testes
pytest -v

# interface de chat
streamlit run app.py

# demonstração do loop cru do SDK
python core_demo.py
```

## Dados de teste

- **Maria Silva** — CPF `123.456.789-00` — apólice `AUTO-1001` (roubo, colisão, incêndio, terceiros).
- **João Souza** — CPF `987.654.321-00` — apólice `AUTO-1002` (colisão, terceiros — **sem roubo**).
- Sinistro pré-cadastrado: protocolo `SIN-5001`.

## Roteiro da demonstração

1. "Meu CPF é 123.456.789-00, quais são minhas coberturas?" → consulta a apólice.
2. "Meu carro foi roubado, estou coberto?" → responde **sim**, sem pedir o CPF de novo (memória).
3. "Quero abrir o sinistro." → confirma os dados e gera um protocolo.
4. Feche e reabra o app: o agente ainda lembra do cliente (memória persistente em SQLite).
5. Rode `python core_demo.py` para mostrar o loop de tool-calling escrito à mão.

## Como o projeto atende à vaga

- **Python forte** — código limpo, funções puras, testes, separação de responsabilidades.
- **LLMs (Claude)** — integração via Agno e via SDK direto.
- **Prompt engineering** — persona com regras de segurança (não inventar cobertura, confirmar
  antes de abrir sinistro) em `prompts/system.py`.
- **APIs e workflows de IA** — loop de tool-calling (automático no Agno, explícito no `core_demo.py`).
- **Memória e histórico conversacional** — memória de sessão e persistência em SQLite via Agno.
- **Framework desejável (Agno)** — usado como motor do agente.
- **Boas práticas** — segredos em `.env` fora do Git, testes automatizados, documentação.
````

- [ ] **Step 2: Commit**

```
git add README.md
git commit -m "docs: README com roteiro de demo e falas para a entrevista"
```

---

## Verificação final

- [ ] Rodar toda a suíte de testes: `.venv\Scripts\python.exe -m pytest -v` → todos passam.
- [ ] `streamlit run app.py` sobe sem erro; com `.env` configurado, o roteiro de demo funciona.
- [ ] `python core_demo.py` executa o loop e responde (com `.env` configurado).
- [ ] `.env` NÃO está versionado (`git status` não mostra `.env`).
