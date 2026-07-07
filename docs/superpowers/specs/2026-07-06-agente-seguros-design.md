# Agente de Atendimento de Seguro Auto — Design

**Data:** 2026-07-06
**Objetivo:** Construir um agente de IA em Python, para apresentar em entrevista da vaga
"Desenvolvedor(a) de Agentes de IA Júnior", demonstrando domínio de Python, LLMs (Claude),
prompt engineering, ferramentas/APIs, memória de agente e histórico conversacional.

## Contexto e motivação

A empresa constrói agentes de IA para seguradoras (Porto Seguro, Mapfre, Allianz, Caixa).
Um demo alinhado ao domínio (seguros) comunica melhor do que um agente genérico. O projeto
também serve de artefato de conversa técnica: mostra fundamentos (loop de agente escrito à mão)
e fluência em framework (Agno), atacando diretamente os "conhecimentos desejáveis" da vaga.

## Escopo

Um **agente de atendimento de seguro auto** que conversa em português e é capaz de:

1. Consultar apólice de um cliente.
2. Verificar se um evento (roubo, colisão, etc.) está coberto.
3. Abrir um sinistro, gerando protocolo.
4. Acompanhar o status de um sinistro por protocolo.

Transversal a tudo: **memória** — o agente lembra o contexto do cliente durante a conversa
e entre sessões.

### Fora de escopo (YAGNI)

- Autenticação real de usuários.
- Banco de dados de produção / APIs externas reais (usamos dados fictícios em memória).
- Múltiplos ramos de seguro (só auto).
- Deploy em nuvem.
- Dois motores de agente completos (decisão: um agente Agno + um script didático).

## Decisões de design

- **LLM:** Claude via API da Anthropic. Modelo padrão **Claude Haiku 4.5**
  (`claude-haiku-4-5-20251001`) — rápido e barato para demo; trocável por modelo maior
  numa linha.
- **Framework principal:** **Agno** — leve, suporta Claude nativamente e traz memória +
  histórico de sessão embutidos (item destacado pela vaga).
- **Fundamentos:** um script `core_demo.py` (~40 linhas) mostra o loop cru de tool-calling
  com o SDK oficial da Anthropic. É artefato didático, não um segundo app.
- **Interface:** chat web em **Streamlit** — impacto visual e memória visível na tela.
- **Segredos:** `ANTHROPIC_API_KEY` em `.env` (fora do Git via `.gitignore`); `.env.example`
  versionado como referência. Demonstra boa prática de segredos, relevante para seguros.

## Arquitetura

```
seguro_agent/
├── .env                    # ANTHROPIC_API_KEY (NÃO versionado)
├── .env.example            # modelo versionado
├── .gitignore
├── requirements.txt
├── README.md               # como rodar + roteiro da demo + falas para a entrevista
├── data/
│   └── seguros.py          # dados fictícios em memória: clientes, apólices, sinistros
├── tools/
│   └── seguro_tools.py     # 4 funções Python puras (lógica de negócio, sem LLM)
├── prompts/
│   └── system.py           # persona/instruções do agente (compartilhado)
├── agente.py               # o agente: Agno + Claude + memória (coração do projeto)
├── core_demo.py            # loop cru do Anthropic SDK (artefato didático, standalone)
├── app.py                  # interface Streamlit de chat
└── tests/
    └── test_tools.py       # testes pytest das 4 ferramentas
```

**Princípio central — separação de responsabilidades:** a lógica de negócio vive em funções
Python puras (`tools/seguro_tools.py`) que não sabem nada de LLM. Tanto o agente Agno quanto
o `core_demo.py` apenas embrulham essas mesmas funções. Isso permite testá-las isoladamente e
sustenta a narrativa de entrevista: "mesma lógica, o motor por cima é intercambiável".

### Unidades e responsabilidades

- **`data/seguros.py`** — fonte de dados fictícia em memória. O quê: dicionários com clientes,
  apólices e sinistros; helpers de leitura/escrita. Depende de: nada. Sinistros abertos são
  gravados aqui em runtime (estado em memória do processo).
- **`tools/seguro_tools.py`** — as 4 ferramentas como funções puras. O quê: recebem argumentos
  simples, consultam/alteram `data/seguros.py`, retornam dicionários claros. Depende de:
  `data/seguros.py`. Sem LLM, sem I/O externo.
- **`prompts/system.py`** — a persona e as instruções do agente como string. Depende de: nada.
- **`agente.py`** — monta o agente Agno com o modelo Claude, registra as ferramentas, configura
  memória/histórico (SQLite). Expõe uma função para criar/obter o agente. Depende de: Agno,
  tools, prompts, `.env`.
- **`core_demo.py`** — script standalone que faz uma interação com o SDK Anthropic cru:
  define o JSON schema das tools, roda o loop de tool-calling manualmente. Depende de:
  `anthropic`, tools, prompts. Executável direto: `python core_demo.py`.
- **`app.py`** — UI Streamlit de chat que conversa com o agente e mostra o histórico.
  Depende de: Streamlit, `agente.py`.

## Fluxo de dados

1. Usuário digita mensagem na UI Streamlit (`app.py`).
2. `app.py` repassa ao agente (`agente.py`), junto com o id de sessão/usuário.
3. Agno envia a mensagem ao Claude com o system prompt e as ferramentas disponíveis, incluindo
   o histórico recuperado da memória.
4. Se o Claude decide chamar uma ferramenta, o Agno executa a função pura correspondente em
   `tools/seguro_tools.py` e devolve o resultado ao Claude.
5. O Claude gera a resposta final em português; o Agno persiste histórico/memória no SQLite.
6. `app.py` exibe a resposta e atualiza o chat.

## As 4 ferramentas

- `consultar_apolice(identificador: str) -> dict` — busca por CPF ou número de apólice; retorna
  coberturas, vigência e franquia, ou erro se não encontrada.
- `verificar_cobertura(apolice_id: str, tipo_evento: str) -> dict` — informa se o evento
  (ex.: "roubo", "colisao", "incendio") está coberto naquela apólice.
- `abrir_sinistro(apolice_id: str, tipo_evento: str, descricao: str) -> dict` — cria um sinistro,
  gera um protocolo único, grava em `data/seguros.py` e retorna o protocolo e status inicial.
- `acompanhar_sinistro(protocolo: str) -> dict` — retorna o status atual do sinistro, ou erro se
  o protocolo não existe.

Cada função retorna um dicionário com chave clara de sucesso/erro para o LLM interpretar.

## Memória e histórico conversacional

Gerenciados pelo Agno com persistência em **SQLite** (arquivo local `.db`):

- **Histórico de sessão:** o agente lembra o que foi dito na conversa (ex.: depois de o cliente
  se identificar, não pede o CPF de novo).
- **Memória de usuário:** fatos sobre o cliente persistem entre sessões (ex.: veículo segurado).

Efeito de demonstração: fechar o app, reabrir e o agente ainda lembra do cliente.

## Persona do agente

Atendente de seguros cordial e objetivo que:

- Sempre confirma dados sensíveis antes de agir (confirma o sinistro antes de abrir protocolo).
- Nunca inventa cobertura — se não está na apólice, diz que não está.
- Responde em português do Brasil, tom profissional e acolhedor.

Reflete a consciência de operar num domínio regulado.

## Tratamento de erros

- **Chave de API ausente/ inválida:** `agente.py` e `core_demo.py` verificam a presença de
  `ANTHROPIC_API_KEY` no start e exibem mensagem clara orientando configurar o `.env`.
- **Ferramenta com dado inexistente:** as funções retornam dicionário de erro (ex.: apólice não
  encontrada) em vez de lançar exceção; o agente comunica isso ao usuário em linguagem natural.
- **Falha de rede/API do Claude:** capturada na camada da UI, com mensagem amigável ao usuário.

## Estratégia de testes

`pytest` sobre `tools/seguro_tools.py` (a lógica de negócio determinística):

- Consultar apólice existente e inexistente.
- Verificar evento coberto e não coberto.
- Abrir sinistro e depois acompanhá-lo pelo protocolo retornado.
- Acompanhar protocolo inexistente.

As ferramentas são puras, então os testes rodam sem chamar o LLM — rápidos e determinísticos.

## Entregáveis para a entrevista

- Projeto rodável com `streamlit run app.py`.
- `core_demo.py` executável para mostrar os fundamentos.
- `README.md` com passo a passo de setup, roteiro da demo e "falas" que conectam cada parte do
  código aos requisitos da vaga.
