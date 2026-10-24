import streamlit as st
from agent import SYSTEM, run_turn

st.set_page_config(page_title="Interview Prep", layout="centered")

st.title("Interview Prep Assistant")
st.caption("It answers interview questions from my RAG and MCP cheat sheets, with page citations, and keeps a revision list of the topics I got wrong.")

# Initialize session state with SYSTEM message
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": SYSTEM}
    ]

# Display chat history (only user and assistant text messages)
for message in st.session_state.messages:
    if message["role"] == "user":
        with st.chat_message("user"):
            st.write(message["content"])
    elif message["role"] == "assistant" and "content" in message and message["content"]:
        with st.chat_message("assistant"):
            st.write(message["content"])

# Chat input
user_input = st.chat_input("Ask me about RAG or MCP...")

if user_input:
    # Add user message to session state and display
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)

    # Get assistant response
    with st.chat_message("assistant"):
        # Create a container to capture tool calls
        tool_calls_container = st.container()
        response_container = st.container()

        def log_tool_call(line):
            with tool_calls_container:
                st.caption("🔧 " + line)

        # Run the turn to get response (this also updates st.session_state.messages)
        response_text = run_turn(st.session_state.messages, on_tool=log_tool_call)

        # Display the response
        with response_container:
            st.write(response_text)
