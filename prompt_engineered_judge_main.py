import streamlit as st
from groq import Groq

def clear_chat_history():
    st.session_state["messages"] = [{"role": "system", "content": "You are Kimi, an AI assistant created by Moonshot AI."}]

# Setup 
client = Groq(api_key=st.secrets["GROQ_API_KEY"])
model_types = ["moonshotai/kimi-k2-instruct"]

# Streamlit App
st.set_page_config(page_title="Chatbot", page_icon="🤖")

with st.sidebar:
    st.title('Translation Judge')
    st.write('This chatbot was created by Joel Ethan Batac and Boris Victoria')
    st.button('Clear Chat History', on_click=clear_chat_history)

if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "system", "content": "You are Kimi, an AI assistant created by Moonshot AI."}]

for message in st.session_state["messages"]:
    if message["role"] == "system":
        with st.chat_message(message["role"], avatar="🦖"):
            st.markdown(message["content"])
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

user_input = st.chat_input("Type your message here...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("user"):
        st.markdown(user_input)

    completion = client.chat.completions.create(
        model=model_types[0],
        messages=st.session_state["messages"],
        temperature=0.6,
        max_completion_tokens=4096,
        top_p=1,
        stream=False
    )

    model_reply = completion.choices[0].message.content

    st.session_state.messages.append({"role": "assistant", "content": model_reply})

    with st.chat_message("assistant"):
        st.markdown(model_reply)