# Roteiro de Apresentação — Agente de Seguro Auto

Guia passo a passo para demonstrar o projeto ao vivo. Tempo alvo: **6–8 minutos**.

> **Antes de começar (checklist):**
> - [ ] `.venv` ativado: `.venv\Scripts\Activate.ps1`
> - [ ] `.env` com a `ANTHROPIC_API_KEY` real preenchida
> - [ ] Testado uma vez antes: `streamlit run app.py` abre e responde
> - [ ] Terminal e navegador já abertos, editor com os arquivos-chave em abas
> - [ ] Se possível, apague o `seguro_agent.db` antes de começar (memória limpa para a demo)

---

## 1. Abertura — o pitch (30s)

> "Construí um agente de IA de atendimento de seguro auto, em Python, usando Claude com o
> framework Agno. Ele consulta apólices, verifica coberturas e abre sinistros conversando em
> português, e **lembra do contexto do cliente**. Escolhi o domínio de seguros porque é
> exatamente o que vocês fazem com Porto Seguro, Mapfre e Allianz."

Deixe claro o diferencial: **construí o núcleo do zero para entender os fundamentos e usei o
Agno para a parte de produção.**

## 2. A arquitetura em 60s (mostre a estrutura de pastas)

> "A ideia central é **separação de responsabilidades**. A lógica de negócio — os dados e as
> quatro ferramentas — são funções Python puras, sem nenhum acoplamento com LLM. O 'motor' do
> agente só embrulha essas funções."

Aponte para:
- `tools/seguro_tools.py` → "4 funções puras, testáveis isoladamente."
- `agente.py` → "aqui elas viram tools do Agno."
- `core_demo.py` → "e aqui está o mesmo loop escrito à mão, sem framework."

> "Isso me dá uma frase forte: **mesma lógica, motor intercambiável.**"

## 3. Prove que funciona — rode os testes (30s)

```powershell
pytest -v
```

> "14 testes cobrindo as ferramentas e os dados. Testo a lógica de negócio sem chamar o LLM —
> rápido e determinístico."

## 4. A demo principal — Streamlit (3–4 min)

```powershell
streamlit run app.py
```

Siga esta sequência (a barra lateral tem os dados de teste):

**a) Identificação + consulta**
> Digite: *"Olá, meu CPF é 123.456.789-00. Quais são minhas coberturas?"*

Comente enquanto responde: "Ele chamou a ferramenta `consultar_apolice` e trouxe os dados reais
do sistema — não inventou."

**b) Memória em ação (o momento-chave)**
> Digite: *"Meu carro foi roubado, estou coberto?"*

> "Repare: **eu não repeti o CPF**. Ele lembrou quem eu sou pela memória de sessão. E confirmou
> que roubo está coberto porque consultou a apólice de verdade."

**c) O agente não alucina (mostre o caso negativo)**
> Digite: *"E se fosse a apólice AUTO-1002, roubo estaria coberto?"*

> "A AUTO-1002 não tem cobertura de roubo, e o agente diz isso claramente. Num domínio regulado
> como seguros, **não inventar cobertura** é uma regra de segurança que coloquei no prompt."

**d) Ação com confirmação**
> Digite: *"Quero abrir o sinistro do roubo."*

> "Antes de abrir, ele confirma os dados comigo — não executa uma ação sensível às cegas."
> Confirme, e mostre o protocolo `SIN-XXXX` gerado.

**e) Memória persistente (o fecho de efeito)**
> Feche a aba do navegador, rode `streamlit run app.py` de novo, e pergunte:
> *"Você lembra do meu caso?"*

> "A memória persiste em SQLite entre sessões. Fechei e reabri, e ele ainda tem o contexto."

## 5. Os fundamentos — core_demo.py (1 min)

Abra `core_demo.py` no editor e rode:

```powershell
python core_demo.py
```

> "Isto é o que o Agno faz por baixo dos panos, mas escrito na mão: eu descrevo as ferramentas
> em JSON schema, chamo o Claude, e quando ele pede uma ferramenta (`stop_reason == tool_use`),
> eu executo a função e devolvo o resultado com o `tool_use_id` casado. O loop repete até a
> resposta final. **Eu entendo o mecanismo, não só o framework.**"

## 6. Fechamento — conecte à vaga (30s)

> "Resumindo o que isso demonstra do que vocês pediram: Python limpo e testado; integração com
> LLM tanto via framework quanto via SDK; prompt engineering com regras de segurança; memória e
> histórico conversacional; e boas práticas como segredos fora do Git. E foi tudo construído do
> requisito ao código, que é a jornada que a vaga descreve."

---

## Plano B (se a internet/API falhar ao vivo)

- Rode `pytest -v` — funciona **offline** e prova a lógica.
- Abra `core_demo.py` e `agente.py` e **explique o fluxo lendo o código** (não precisa executar).
- Tenha um print/gravação da demo funcionando como backup no celular.
