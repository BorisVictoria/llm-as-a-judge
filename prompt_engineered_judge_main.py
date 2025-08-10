import streamlit as st
from groq import Groq

judge_prompt = """
You are a translation quality judge for ENGLISH → FILIPINO translations.

TASK:
Evaluate one translation pair using the six criteria below:
1. Accuracy – Does the translation preserve the original meaning?
2. Fluency – Is it grammatically correct and natural in Filipino?
3. Coherence – Is the flow and structure logical in Filipino?
4. Cultural Appropriateness – Does it fit the cultural and social context?
5. Guideline Adherence – Does it follow any provided domain-specific rules?
6. Completeness – Does it retain all important details from the source?

SCORING RULE:
- Each criterion: 0 points (fails) or 1 point (meets standard)
- Add up the points (0–6 total)
- Map the sum to a final score:
    - 5–6 → Score = 5 (Excellent)
    - 3–4 → Score = 3 (Good)
    - 0–2 → Score = 1 (Poor)

OUTPUT:
- Present your evaluation in a clear, well-structured way
- You may format the result as a table
- Include:
    • Final score (1–5) and label ("excellent", "good", or "poor")
    • The score and explanation for each criterion
    • Any notable highlights (problematic phrases or strong points)
    • A suggested fix if there are serious errors
    • Your confidence level (optional, 0–100)

Be thorough but concise.
"""

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
    
    streaming_enabled = st.checkbox("Enable Streaming", value=True)
    append_judge_prompt = st.checkbox("Append Judge Prompt", value=False)

if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "system", "content": "You are Kimi, an AI assistant created by Moonshot AI."}]

for message in st.session_state["messages"]:
    print(message)
    if message["role"] == "system":
        with st.chat_message(message["role"], avatar="🦖"):
            st.markdown(message["content"])
            continue
    
    with st.chat_message(message["role"]):
        if message.get("content"):
            st.markdown(message["content"])

# Chat input
user_input = st.chat_input("Type your message here...")

if user_input:
    # Add user message to session state and display
    if append_judge_prompt:
        st.session_state["messages"].append({"role": "user", "content": judge_prompt + user_input})
        with st.chat_message("user"):
            st.markdown(judge_prompt + user_input)
    else:
        st.session_state["messages"].append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

    
    # Assistant response container
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        
        # Process the conversation
        full_response = ""
        
        if streaming_enabled:
            # Streaming completion
            stream = client.chat.completions.create(
                model=model_types[0],
                messages=st.session_state["messages"],
                temperature=0.6,
                max_completion_tokens=4096,
                top_p=1,
                stream=True,
            )
            
            # Collect the streaming response
            full_response = ""
            
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    # Regular content streaming
                    full_response += chunk.choices[0].delta.content
                    message_placeholder.markdown(full_response + "▌")
            
            if full_response:
                message_placeholder.markdown(full_response)
                st.session_state["messages"].append({"role": "assistant", "content": full_response})

        else:
            # Non-streaming completion
            completion = client.chat.completions.create(
                model=model_types[0],
                messages=st.session_state["messages"],
                temperature=0.6,
                max_completion_tokens=4096,
                top_p=1,
                stream=False,
            )
            
            choice = completion.choices[0]
            full_response = choice.message.content or ""
            
            if full_response:
                message_placeholder.markdown(full_response)
                st.session_state["messages"].append({"role": "assistant", "content": full_response})
            