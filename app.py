import streamlit as st
from agent import SYSTEM, RoundLimitReached, run_turn

LIMIT_MESSAGE = (
    "I looked things up several times but ran out of steps before I could write an answer. "
    "Try a simpler, narrower question, such as one topic at a time."
)

st.set_page_config(page_title="Interview Prep", layout="centered")

st.title("Interview Prep Assistant")
st.caption("It answers interview questions from my RAG and MCP cheat sheets, with page citations, and keeps a revision list of the topics I got wrong.")

# Initialize session state with SYSTEM message
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": SYSTEM}
    ]

# Display list: one entry per user or assistant turn, with the 🔧 lines saved for each assistant turn
if "display" not in st.session_state:
    st.session_state.display = []

# Replay chat history, including the saved 🔧 lines
for item in st.session_state.display:
    if item["role"] == "user":
        with st.chat_message("user"):
            st.write(item["content"])
    else:
        with st.chat_message("assistant"):
            if item["tools"]:
                with st.expander("🔧 Tool calls", expanded=True):
                    for line in item["tools"]:
                        st.caption("🔧 " + line)
            if item.get("warning"):
                st.warning(item["content"])
            else:
                st.write(item["content"])

# Chat input
user_input = st.chat_input("Ask me about RAG or MCP...")

if user_input:
    # Add user message to session state and display
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.session_state.display.append({"role": "user", "content": user_input, "tools": []})
    with st.chat_message("user"):
        st.write(user_input)

    # Get assistant response
    with st.chat_message("assistant"):
        tool_lines = []
        # The expander is created on the first tool call, so turns without tools show nothing
        tool_box = {"expander": None}

        def log_tool_call(line):
            tool_lines.append(line)
            if tool_box["expander"] is None:
                tool_box["expander"] = st.expander("🔧 Tool calls", expanded=True)
            with tool_box["expander"]:
                st.caption("🔧 " + line)

        # Run the turn to get response (this also updates st.session_state.messages)
        warned = False
        try:
            response_text = run_turn(st.session_state.messages, on_tool=log_tool_call)
            st.write(response_text)
        except RoundLimitReached:
            warned = True
            response_text = LIMIT_MESSAGE
            st.warning(response_text)

    # Save the answer with its tool lines so they show again on the next question
    st.session_state.display.append({"role": "assistant", "content": response_text, "tools": tool_lines, "warning": warned})
