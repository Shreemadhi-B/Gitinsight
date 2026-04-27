# Streamlit chat interface for GitInsight.
# Run with: streamlit run app.py

import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

from agent import build_agent, ask_agent
from loader import clone_repo, extract_commits
from ingest import get_chroma_client, get_collection, ingest_commits


st.set_page_config(page_title="GitInsight", page_icon="🔍", layout="wide")

st.markdown("""
<style>
    .main-header { font-size: 2rem; font-weight: 700; color: #1f77b4; }
    .sub-header { font-size: 0.95rem; color: #888; margin-bottom: 1.5rem; }
</style>
""", unsafe_allow_html=True)

# Session state persists data across Streamlit reruns
defaults = {
    "agent": None,
    "messages": [],
    "repo_loaded": False,
    "repo_name": "",
    "repo_url": "",
    "commit_count": 0,
}
for key, val in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val


# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## Repository Setup")
    st.markdown("---")

    repo_url = st.text_input(
        label="GitHub Repository URL",
        placeholder="https://github.com/user/repo",
        help="Enter any public GitHub repository URL",
    )

    max_commits = st.slider(
        label="Max commits to analyze",
        min_value=10, max_value=200, value=50, step=10,
        help="More commits = better answers but slower indexing",
    )

    st.markdown("---")

    if st.button("Analyze Repository", type="primary", use_container_width=True):
        if not repo_url or not repo_url.startswith("https://github.com"):
            st.error("Please enter a valid GitHub URL starting with https://github.com")
        else:
            with st.status("Analyzing repository...", expanded=True) as status:
                try:
                    st.write("Cloning repository...")
                    repo, repo_path = clone_repo(repo_url)
                    repo_name = repo_url.rstrip("/").split("/")[-1].replace(".git", "")

                    st.write(f"Extracting up to {max_commits} commits...")
                    commits = extract_commits(repo, max_commits=max_commits)

                    st.write("Indexing commits in ChromaDB...")
                    client = get_chroma_client()

                    # Clear old index when switching repos
                    if st.session_state["repo_url"] and st.session_state["repo_url"] != repo_url:
                        try:
                            client.delete_collection("commits")
                        except Exception:
                            pass

                    collection = get_collection(client)
                    ingest_commits(commits, collection)

                    st.write("Loading Gemini agent...")
                    agent = build_agent(repo_name=repo_name)

                    st.session_state.update({
                        "agent": agent,
                        "repo_loaded": True,
                        "repo_name": repo_name,
                        "repo_url": repo_url,
                        "commit_count": len(commits),
                        "messages": [],
                    })

                    status.update(
                        label=f"✅ {repo_name} analyzed successfully.",
                        state="complete",
                        expanded=False,
                    )

                except Exception as e:
                    status.update(label="Error occurred.", state="error")
                    st.error(f"Error: {str(e)}")

    if st.session_state["repo_loaded"]:
        st.markdown("---")
        st.markdown(f"**Repo:** `{st.session_state['repo_name']}`")
        st.markdown(f"**Commits indexed:** {st.session_state['commit_count']}")
        st.success("Ready to chat.")

        if st.button("Clear Chat History", use_container_width=True):
            st.session_state["messages"] = []
            st.rerun()

        if st.button("Load Different Repo", use_container_width=True):
            for key, val in defaults.items():
                st.session_state[key] = val
            st.rerun()
    else:
        st.markdown("---")
        st.info("Enter a GitHub URL and click Analyze to begin.")
        st.markdown("**Try these repos:**")
        st.code("https://github.com/pallets/flask")
        st.code("https://github.com/psf/requests")
        st.code("https://github.com/Textualize/rich")


# ── Main area ─────────────────────────────────────────────────────────────────
st.markdown('<p class="main-header">🔍 GitInsight</p>', unsafe_allow_html=True)
st.markdown(
    '<p class="sub-header">AI-powered GitHub repository analysis · LangGraph + ChromaDB + Gemini</p>',
    unsafe_allow_html=True,
)

if not st.session_state["repo_loaded"]:
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("### Step 1")
        st.markdown("Paste any public GitHub repo URL in the sidebar.")
    with col2:
        st.markdown("### Step 2")
        st.markdown("Click **Analyze Repository** to clone and index commits.")
    with col3:
        st.markdown("### Step 3")
        st.markdown("Ask questions in plain English and get cited answers.")

    st.markdown("---")
    st.markdown("### How It Works")
    st.markdown("""
Your question goes to a LangGraph agent powered by Gemini 2.5 Flash.
The agent decides which tool to call, calls it as a direct Python function,
reads the result, and returns a cited answer.

Tools available:
- `search_commits` — find commits by meaning using ChromaDB vector search
- `fetch_commit` — get full details of a specific commit by hash
- `get_file_history` — see every commit that touched a file
    """)

else:
    st.markdown(f"### Chat about `{st.session_state['repo_name']}`")
    st.markdown("---")

    for message in st.session_state["messages"]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if not st.session_state["messages"]:
        st.markdown("#### Try asking:")
        col1, col2 = st.columns(2)
        suggestions = [
            "What kind of bug fixes have been made?",
            "Who has been committing the most recently?",
            "Which files change the most often?",
            "What are the most recent changes?",
        ]
        for i, suggestion in enumerate(suggestions):
            col = col1 if i % 2 == 0 else col2
            with col:
                if st.button(suggestion, use_container_width=True, key=f"suggest_{i}"):
                    st.session_state["messages"].append({"role": "user", "content": suggestion})
                    st.rerun()

    user_input = st.chat_input(
        placeholder=f"Ask anything about {st.session_state['repo_name']}..."
    )

    if user_input:
        st.session_state["messages"].append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    response = ask_agent(
                        question=user_input,
                        agent=st.session_state["agent"],
                        chat_history=st.session_state["messages"][:-1],
                    )
                    st.markdown(response)
                    st.session_state["messages"].append(
                        {"role": "assistant", "content": response}
                    )
                except Exception as e:
                    err = f"Error: {str(e)}"
                    st.error(err)
                    st.session_state["messages"].append({"role": "assistant", "content": err})

st.markdown("---")
st.markdown(
    "<center><small>GitInsight · LangGraph + ChromaDB + Gemini 2.5 Flash</small></center>",
    unsafe_allow_html=True,
)