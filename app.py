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
