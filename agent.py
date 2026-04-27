# LangGraph agent that uses Gemini and calls tools directly (no MCP).

import os
from typing import Annotated, TypedDict
from dotenv import load_dotenv

load_dotenv()

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from tools import ALL_TOOLS


class AgentState(TypedDict):
    messages: Annotated[list, add_messages]


def build_system_prompt(repo_name: str = "the repository") -> str:
    return f"""You are GitInsight, an AI assistant analyzing the GitHub repository: {repo_name}

You have access to these tools:
- search_commits: search commits by meaning or keywords
- fetch_commit: get full details of a commit by hash
- get_file_history: get all commits that touched a specific file

Rules:
1. Always use tools to find real data before answering.
2. Never invent commit hashes, file names, authors, or dates.
3. Always cite sources: [commit: hash] [file: name] [author: name] [date: YYYY-MM-DD]
4. For file questions use get_file_history.
5. For topic questions use search_commits.
6. For a known hash use fetch_commit.

Format your response as:
Summary: <one or two sentence answer>
Details: <findings>
Citations: [commit: hash] [file: name] [author: name] [date: YYYY-MM-DD]
"""


def build_agent(repo_name: str = "the repository"):
    """Assembles and compiles the LangGraph agent."""
    model = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=os.getenv("GEMINI_API_KEY"),
        temperature=0.3,
    ).bind_tools(ALL_TOOLS)

    tool_node = ToolNode(ALL_TOOLS)

    def agent_node(state: AgentState) -> dict:
        messages = state["messages"]
        if not any(isinstance(m, SystemMessage) for m in messages):
            messages = [SystemMessage(content=build_system_prompt(repo_name))] + messages
        return {"messages": [model.invoke(messages)]}

    def should_continue(state: AgentState) -> str:
        last = state["messages"][-1]
        if hasattr(last, "tool_calls") and last.tool_calls:
            return "tools"
        return "end"

    graph = StateGraph(AgentState)
    graph.add_node("agent", agent_node)
    graph.add_node("tools", tool_node)
    graph.set_entry_point("agent")
    graph.add_conditional_edges("agent", should_continue, {"tools": "tools", "end": END})
    graph.add_edge("tools", "agent")

    return graph.compile()


def ask_agent(question: str, agent, chat_history: list = None) -> str:
    """Sends a question to the agent with optional conversation history."""
    history = []
    if chat_history:
        for msg in chat_history[-6:]:
            if msg["role"] == "user":
                history.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                history.append(AIMessage(content=msg["content"]))

    history.append(HumanMessage(content=question))

    final_state = agent.invoke(
        {"messages": history},
        config={"recursion_limit": 10}
    )

    content = final_state["messages"][-1].content
    if isinstance(content, list):
        return "\n".join(
            b["text"] for b in content
            if isinstance(b, dict) and b.get("type") == "text"
        )
    return content