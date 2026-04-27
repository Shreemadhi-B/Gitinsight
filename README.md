GitInsight

GitInsight is an AI-powered GitHub repository analysis tool that enables users to ask natural language questions about any public repository and receive answers grounded in actual commit history. It combines retrieval-augmented generation with agent-based workflows to deliver meaningful, context-aware insights into codebases.

Overview

Understanding a new or large repository can be time-consuming. GitInsight simplifies this process by allowing users to interact with repositories conversationally. Instead of manually browsing commits and files, users can ask questions and receive precise answers derived directly from repository data.

Key Features
Natural language querying of GitHub repositories
Answers grounded in commit history and repository data
Retrieval-Augmented Generation (RAG) to reduce hallucination
Agent-based workflow powered by LangGraph
Fast semantic search using vector embeddings (ChromaDB)
Context-aware reasoning using Gemini
Architecture

The system follows a retrieval-augmented pipeline:

User Query
   ↓
LangGraph Agent
   ↓
Retriever (ChromaDB)
   ↓
Relevant Repository Data
   ↓
Gemini LLM
   ↓
Final Answer
Project Structure
Gitinsight/
│── agent.py        # Agent workflow logic
│── app.py          # Application entry point
│── ingest.py       # GitHub data ingestion
│── loader.py       # Data loading and preprocessing
│── retriever.py    # Retrieval and vector search
│── tools.py        # Tool integrations
│── requirements.txt
│── .gitignore
Installation
1. Clone the repository
git clone https://github.com/Shreemadhi-B/Gitinsight.git
cd Gitinsight
2. Create a virtual environment
python -m venv venv
source venv/bin/activate      # macOS/Linux
venv\Scripts\activate         # Windows
3. Install dependencies
pip install -r requirements.txt
Environment Variables

Create a .env file in the root directory and add:

GITHUB_TOKEN=your_github_token
GOOGLE_API_KEY=your_gemini_api_key
Usage

Run the application:

python app.py

Then provide a GitHub repository URL and ask questions such as:

What is the purpose of this repository?
Who are the main contributors?
What changes were made recently?
Which parts of the codebase are most active?
Use Cases
Developers exploring unfamiliar repositories
Recruiters evaluating candidate contributions
Project managers analyzing development activity
Students learning from open-source projects
Tech Stack
Python
LangGraph
ChromaDB
Gemini (Google Generative AI)
GitHub API
Limitations
Designed primarily for public repositories
Large repositories may require additional ingestion time
Subject to GitHub and API rate limits
License

This project is licensed under the MIT License.

Author

Shreemadhi Babu Rajendra Prasad
