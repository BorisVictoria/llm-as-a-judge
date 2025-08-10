import streamlit as st
from groq import Groq
import json
import time

def clear_chat_history():
    st.session_state["messages"] = [{"role": "assistant", "content": "How may I assist you today?"}]

# Tools
def get_weather(city: str) -> dict:
    # Simulate some processing time
    time.sleep(0.5)
    # Mock weather data
    weather_data = {
        "city": city,
        "temperature": "72°F",
        "condition": "Sunny",
        "humidity": "45%",
        "wind": "5 mph"
    }
    return weather_data

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
    
    # Add streaming toggle
    streaming_enabled = st.checkbox("Enable Streaming", value=True)
    show_tool_calls = st.checkbox("Show Tool Calls", value=True)

if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "How may I assist you today?"}]

# Display chat history
for message in st.session_state["messages"]:
    # Skip tool messages in the main display (we'll show them specially)
    if message["role"] == "tool":
        continue
    
    with st.chat_message(message["role"]):
        # Check if this is a tool call message
        if message["role"] == "assistant" and message.get("tool_calls"):
            # Show tool call indicator
            if show_tool_calls:
                with st.expander("🔧 Tool Call", expanded=False):
                    for tool_call in message["tool_calls"]:
                        st.code(f"Function: {tool_call['function']['name']}\nArguments: {tool_call['function']['arguments']}", language="json")
            # If there's also content, show it
            if message.get("content"):
                st.markdown(message["content"])
        else:
            # Regular message
            if message.get("content"):
                st.markdown(message["content"])

# Chat input
user_input = st.chat_input("Type your message here...")

if user_input:
    # Add user message to session state and display
    st.session_state["messages"].append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)
    
    # Assistant response container
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        tool_status_placeholder = st.empty()
        
        # Process the conversation
        full_response = ""
        tool_processing = False
        
        while True:
            try:
                if streaming_enabled:
                    # Streaming completion
                    stream = client.chat.completions.create(
                        model=model_types[0],
                        messages=st.session_state["messages"],
                        temperature=0.6,
                        max_completion_tokens=4096,
                        top_p=1,
                        stream=True,
                        tools=tools,
                        tool_choice="auto"
                    )
                    
                    # Collect the streaming response
                    full_response = ""
                    tool_calls = []
                    current_tool_call = None
                    
                    for chunk in stream:
                        if chunk.choices[0].delta.tool_calls:
                            tool_processing = True
                            for tool_call_chunk in chunk.choices[0].delta.tool_calls:
                                if tool_call_chunk.index is not None:
                                    # New tool call or update existing
                                    while len(tool_calls) <= tool_call_chunk.index:
                                        tool_calls.append({
                                            "id": "",
                                            "type": "function",
                                            "function": {"name": "", "arguments": ""}
                                        })
                                    
                                    current_tool_call = tool_calls[tool_call_chunk.index]
                                    
                                    if tool_call_chunk.id:
                                        current_tool_call["id"] = tool_call_chunk.id
                                    if tool_call_chunk.function:
                                        if tool_call_chunk.function.name:
                                            current_tool_call["function"]["name"] = tool_call_chunk.function.name
                                        if tool_call_chunk.function.arguments:
                                            current_tool_call["function"]["arguments"] += tool_call_chunk.function.arguments
                                    
                                    # Show tool call status
                                    if show_tool_calls:
                                        tool_status_placeholder.info(f"🔧 Calling function: {current_tool_call['function']['name']}...")
                        
                        elif chunk.choices[0].delta.content:
                            # Regular content streaming
                            full_response += chunk.choices[0].delta.content
                            message_placeholder.markdown(full_response + "▌")
                        
                        # Check finish reason
                        if chunk.choices[0].finish_reason:
                            finish_reason = chunk.choices[0].finish_reason
                            break
                    
                    # Remove cursor
                    if full_response:
                        message_placeholder.markdown(full_response)
                    
                else:
                    # Non-streaming completion
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
                    full_response = choice.message.content or ""
                    tool_calls = []
                    
                    if choice.message.tool_calls:
                        for tc in choice.message.tool_calls:
                            tool_calls.append({
                                "id": tc.id,
                                "type": "function",
                                "function": {
                                    "name": tc.function.name,
                                    "arguments": tc.function.arguments
                                }
                            })
                    
                    if full_response:
                        message_placeholder.markdown(full_response)
                
                # Handle tool calls if needed
                if finish_reason == "tool_calls" and tool_calls:
                    # Save assistant message with tool calls
                    assistant_msg = {"role": "assistant", "content": full_response}
                    if tool_calls:
                        assistant_msg["tool_calls"] = tool_calls
                    st.session_state["messages"].append(assistant_msg)
                    
                    # Process each tool call
                    for tool_call in tool_calls:
                        tool_call_name = tool_call["function"]["name"]
                        tool_call_args = json.loads(tool_call["function"]["arguments"])
                        
                        # Show tool execution
                        if show_tool_calls:
                            with tool_status_placeholder.container():
                                st.info(f"🔧 Executing: {tool_call_name}({tool_call_args})")
                        
                        # Execute the tool
                        tool_function = tool_map[tool_call_name]
                        tool_result = tool_function(**tool_call_args)
                        
                        # Show tool result
                        if show_tool_calls:
                            with st.expander(f"📊 Tool Result: {tool_call_name}", expanded=True):
                                st.json(tool_result)
                        
                        # Add tool response to messages
                        st.session_state["messages"].append({
                            "tool_call_id": tool_call["id"],
                            "role": "tool",
                            "name": tool_call_name,
                            "content": json.dumps(tool_result),
                        })
                    
                    # Clear tool status
                    tool_status_placeholder.empty()
                    
                    # Continue the conversation to get final response
                    continue
                    
                else:
                    # Regular message, save and exit loop
                    if full_response:
                        st.session_state["messages"].append({"role": "assistant", "content": full_response})
                    break
                    
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
                break