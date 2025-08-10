import streamlit as st
from groq import Groq
import json

def clear_chat_history():
    st.session_state["messages"] = [{"role": "assistant", "content": "How may I assist you today?"}]

# Tools
def get_weather(city: str) -> dict:
    return {"weather": "Sunny"}

tools = [{
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "Retrieve current weather information. Call this when the user asks about the weather.",
        "parameters": {
            "type": "object",
            "required": ["city"],
            "properties": {
                "city": {
                    "type": "string",
                    "description": "Name of the city"
                }
            }
        }
    }
}]

tool_map = {
    "get_weather": get_weather
}

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
    st.session_state["messages"] = [{"role": "assistant", "content": "How may I assist you today?"}]

user_input = st.chat_input("Type your message here...")

for message in st.session_state["messages"]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if user_input:
    st.session_state["messages"].append({"role": "user", "content": user_input})

    with st.chat_message("user"):
        st.markdown(user_input)
    
    while True:
        completion = client.chat.completions.create(
            model=model_types[0],
            messages=st.session_state["messages"],
            temperature=0.6,
            max_completion_tokens=4096,
            top_p=1,
            stream=False,
            tools=tools,
            tool_choice="auto"
        )

        choice = completion.choices[0]
        finish_reason = choice.finish_reason

        if finish_reason == "tool_calls":
            st.session_state["messages"].append({"role": choice.message.role, "content": choice.message.content})
            tool_calls = choice.message.tool_calls or []

            for tool_call in tool_calls:
                tool_call_name = tool_call.function.name
                tool_call_args = json.loads(tool_call.function.arguments)
                tool_function = tool_map[tool_call_name] 
                tool_result = tool_function(**tool_call_args)

                st.session_state["messages"].append(
                    {
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": tool_call_name,
                        "content": json.dumps(tool_result),
                    }
                )
            continue
        else:
            st.session_state["messages"].append({"role": choice.message.role, "content": choice.message.content})
            break

