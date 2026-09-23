import streamlit as st
from src.the_digital_twin.chat import chat

st.set_page_config(page_title="AI Digital Twin", page_icon="🤖", layout="wide")

st.title("🤖 AI Digital Twin")
st.caption("Ask about my LinkedIn profile. Powered by OpenRouter + Streamlit.")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if user_input := st.chat_input("Type your question..."):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            reply = chat(user_input, st.session_state.messages[:-1])
        st.markdown(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})