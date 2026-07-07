# Perguntas Técnicas Prováveis — com respostas curtas

Respostas em tom de conversa, curtas para ensaiar. Estão ancoradas no **seu** código, então
você pode sempre apontar para um arquivo.

---

## Sobre memória e histórico conversacional

**P: Como o agente "lembra" das coisas?**
> Duas camadas. **Histórico de sessão**: as últimas interações voltam no contexto a cada turno
> (`add_history_to_context=True`, `num_history_runs=5` no `agente.py`) — é o que faz ele não
> pedir meu CPF duas vezes. E **memória persistente**: o Agno grava sessão e fatos do usuário em
> **SQLite**, então o contexto sobrevive mesmo se eu fechar o app.

**P: Qual a diferença entre memória e histórico?**
> Histórico é a transcrição literal da conversa. Memória é um resumo/fato destilado do usuário
> (ex.: "tem um Civic 2020 segurado") que persiste entre conversas diferentes. Histórico cresce
> e você trunca; memória é curada.

**P: O histórico não estoura o limite de contexto?**
> Sim, se você mandar tudo. Por isso limito a uma janela (`num_history_runs`) e, em produção,
> usaria resumo das interações antigas. É um trade-off entre custo/latência de tokens e memória.

---

## Sobre tool calling / function calling

**P: Como o modelo chama uma função?**
> Eu descrevo cada ferramenta pro modelo (nome, descrição, schema dos argumentos). Quando o
> Claude decide usar uma, ele não executa nada — ele **retorna um pedido** (`stop_reason:
> tool_use`) com o nome e os argumentos. **Meu código** executa a função Python e devolve o
> resultado num bloco `tool_result`, casando pelo `tool_use_id`. O loop repete até ele dar a
> resposta final. Isso está explícito no `core_demo.py`.

**P: Por que suas ferramentas são funções puras?**
> Testabilidade e clareza. A lógica de negócio não sabe que existe um LLM — recebe argumentos,
> retorna um dict. Testo com pytest sem gastar API, e o mesmo conjunto de funções serve tanto ao
> Agno quanto ao loop manual. É separação de responsabilidades.

**P: E se a ferramenta falhar ou não achar o dado?**
> Elas nunca lançam exceção pro modelo — retornam `{"erro": "..."}`. O agente lê isso e comunica
> em linguagem natural. Assim uma apólice inexistente vira uma resposta educada, não um crash.

---

## Sobre evitar alucinação (crítico em seguros)

**P: Como você garante que o agente não inventa uma cobertura?**
> Duas defesas. Primeira, **grounding**: a informação vem sempre de uma ferramenta que consulta o
> dado real, nunca da "memória" do modelo. Segunda, **regra explícita no system prompt**: "nunca
> invente; se a cobertura não está na apólice, diga que não está". Na demo eu mostro a apólice
> AUTO-1002, que não tem roubo, e ele nega corretamente.

**P: Isso é garantia de 100%?**
> Não existe 100% com LLM. Reduzo o risco com grounding e prompt, mas em produção eu adicionaria
> **validação pós-resposta** (checar se a cobertura citada existe mesmo na apólice) e métricas de
> homologação com o cliente — que é parte do que a vaga descreve.

---

## Sobre escolha de ferramentas e modelo

**P: Por que Agno e não LangChain ou CrewAI?**
> Agno é leve, tem memória e histórico embutidos — que era exatamente o requisito — e suporta
> Claude nativamente. LangChain é mais popular mas mais pesado; CrewAI brilha em multi-agente,
> que aqui seria over-engineering. Escolhi a ferramenta pelo problema, não pela moda. E como
> montei o núcleo no SDK direto, migrar de framework é barato.

**P: Por que Claude Haiku e não um modelo maior?**
> Custo e latência. Para um atendimento com ferramentas bem definidas, o Haiku 4.5 é rápido e
> barato e dá conta. Trocar por um Sonnet é **uma linha** (a constante `MODELO`). Eu começaria
> pequeno e subiria só se a qualidade exigisse — decisão guiada por métricas.

**P: Quando usaria SDK direto vs framework?**
> Framework quando quero velocidade e recursos prontos (memória, retries). SDK direto quando
> preciso de controle fino do loop ou quero eliminar dependências. Ter feito os dois me deixa
> escolher com consciência, não por hábito.

---

## Sobre produção, monitoramento e sustentação (bate com a vaga)

**P: Como você levaria isso pra produção com dados reais?**
> Trocaria só a camada `data/seguros.py` por integrações reais (API da seguradora ou banco) —
> as ferramentas e o agente não mudam, porque a fronteira está bem definida. Adicionaria
> autenticação, logging estruturado e tratamento de timeout/retry nas chamadas externas.

**P: Que métricas você monitoraria?**
> Taxa de resolução sem humano, latência por turno, custo de tokens por conversa, frequência de
> uso de cada ferramenta, e taxa de erro/fallback. E logs das conversas para homologação e
> ajuste de prompt — a "evolução contínua" que a vaga cita.

**P: Como você depura quando o agente se comporta mal?**
> Olho o **trace do turno**: qual ferramenta ele chamou, com quais argumentos, qual resultado
> voltou. Na maioria das vezes o problema é prompt (instrução ambígua) ou dado (ferramenta
> retornou algo confuso). Reproduzo com um teste, ajusto, e verifico.

---

## Sobre segurança e dados sensíveis

**P: Seguros lidam com dado sensível. Como você trata isso?**
> Nunca coloco segredo no código — a `ANTHROPIC_API_KEY` fica em `.env`, fora do Git. Inclusive,
> durante o desenvolvimento, uma chave real acabou colada no `.env.example` versionado e eu
> movi pro `.env` antes de qualquer commit. Em produção, pensaria em mascaramento de PII (CPF)
> nos logs e em conformidade com a LGPD.

---

## Perguntas "pega-ratão" (fundamentos)

**P: O que acontece se o modelo pedir uma ferramenta que não existe?**
> No loop manual, seria um erro de dispatch — por isso só anuncio ao modelo as ferramentas que
> realmente existem; ele não tem como pedir outra. Em produção, um `.get()` com mensagem amigável
> em vez de deixar quebrar.

**P: Seu loop de agente pode rodar pra sempre?**
> Coloquei um teto de iterações no `core_demo.py` justamente pra isso — se o modelo entrar num
> ciclo de tool-calling, ele para em vez de faturar tokens infinitamente. É defesa em
> profundidade.

**P: Por que o histórico vai como "mensagens" e não num campo à parte?**
> Porque a API de LLM é stateless: cada chamada precisa receber todo o contexto relevante. O
> "estado" da conversa é reconstruído a cada turno a partir do que eu mando em `messages`. Quem
> guarda esse estado entre chamadas é a minha camada de memória, não o modelo.

---

## Se travar numa pergunta

Seja honesto e mostre raciocínio:
> "Não tenho certeza da resposta exata, mas meu palpite é X porque Y — e eu confirmaria testando
> Z." Isso demonstra autonomia e honestidade, que a vaga lista como soft skills essenciais.
