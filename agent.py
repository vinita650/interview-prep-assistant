import json
import streamlit as st
from openai import OpenAI
from tools import search_docs, save_weak_spot, list_weak_spots

SYSTEM = """You are an interview prep assistant. Answer questions about RAG and MCP only from search_docs results.
Always cite sources like [filename p.X].
When search_docs returns no strong match, say plainly: "I don't have a strong match in my notes for that."
Help track weak spots when the user flags something they got wrong.
Keep responses concise and focused."""

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_docs",
            "description": "Search the interview cheat sheets for passages related to a query. Returns up to 3 closest passages with file name and page number. Use this when answering any question about RAG, MCP, or AI engineering concepts.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query"
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "save_weak_spot",
            "description": "Save a topic to the revision list with optional notes. Returns a confirmation message. Use this when the user says they got something wrong or wants to mark a topic for revision.",
            "parameters": {
                "type": "object",
                "properties": {
                    "topic": {
                        "type": "string",
                        "description": "The topic to add to the revision list"
                    },
                    "note": {
                        "type": "string",
                        "description": "Optional note about why this is a weak spot"
                    }
                },
                "required": ["topic", "note"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_weak_spots",
            "description": "Retrieve the full revision list of topics to study. Returns a formatted list of weak spots. Use this when the user asks what they should revise or want to see their revision list.",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    }
]


def run_turn(messages, on_tool=print, max_rounds=5):
    """
    Run one turn of the tool-calling loop.

    Args:
        messages: List of messages, with SYSTEM already added by caller as first message
        on_tool: Callback function for tool execution (default: print)
        max_rounds: Maximum number of rounds before stopping

    Returns:
        The final text response from the model
    """
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

    for round_num in range(max_rounds):
        # Call the model
        response = client.chat.completions.create(
            model="gpt-5.4-mini",
            messages=messages,
            tools=TOOLS
        )

        # Check if we have tool calls
        if response.choices[0].message.tool_calls:
            # Append the assistant message with tool calls as plain dicts
            messages.append({
                "role": "assistant",
                "content": response.choices[0].message.content,
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {"name": tc.function.name, "arguments": tc.function.arguments}
                    }
                    for tc in response.choices[0].message.tool_calls
                ]
            })

            # Process each tool call
            for tool_call in response.choices[0].message.tool_calls:
                tool_name = tool_call.function.name
                tool_args = json.loads(tool_call.function.arguments)

                # Log the tool call
                on_tool(f"-> {tool_name}({tool_args})")

                # Execute the tool
                if tool_name == "search_docs":
                    result = search_docs(tool_args["query"])
                elif tool_name == "save_weak_spot":
                    result = save_weak_spot(tool_args["topic"], tool_args["note"])
                elif tool_name == "list_weak_spots":
                    result = list_weak_spots()
                else:
                    result = f"Unknown tool: {tool_name}"

                # Append the tool result
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result
                })
        else:
            # No tool calls, append the response and return
            messages.append({
                "role": "assistant",
                "content": response.choices[0].message.content
            })
            return response.choices[0].message.content

    # Max rounds reached
    return "Stopped"


if __name__ == "__main__":
    print("Interview Prep Assistant")
    print("Type your questions or commands. Press Ctrl+C or enter an empty line to quit.\n")

    messages = [
        {"role": "system", "content": SYSTEM}
    ]

    while True:
        user_input = input("You: ").strip()

        if not user_input:
            print("Goodbye!")
            break

        messages.append({"role": "user", "content": user_input})

        response = run_turn(messages)
        print(f"\nAssistant: {response}\n")
