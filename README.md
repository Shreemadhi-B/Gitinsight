# GitInsight

AI-powered GitHub repository analysis using retrieval-augmented generation and agent-based workflows.

---

## Overview

GitInsight enables users to interact with GitHub repositories using natural language. Instead of manually browsing commits, files, and contributors, users can ask questions and receive answers grounded in actual repository data.

The system combines retrieval mechanisms with large language models to provide context-aware insights into codebases.

---

## Motivation

Understanding unfamiliar or large repositories is often slow and inefficient. Developers must manually inspect commits, trace file changes, and interpret project structure.

GitInsight addresses this problem by allowing users to query repositories conversationally and obtain precise, data-backed answers derived from commit history.

---

## Key Features

- Natural language querying of GitHub repositories  
- Answers grounded in commit history and repository data  
- Retrieval-Augmented Generation (RAG) to reduce hallucination  
- Agent-based workflow using LangGraph  
- Fast semantic search with ChromaDB  
- Context-aware reasoning using Gemini  

---

## System Architecture

```
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
```

---

## Example Usage

### Input
```
What does this repository do?
```

### Output
```
This repository focuses on [project purpose], with key contributions in [modules/features]. 
Recent commits indicate development in [specific area].
```

---

## Project Structure

```
Gitinsight/
│── agent.py        # Agent workflow logic
│── app.py          # Application entry point
│── ingest.py       # GitHub data ingestion
│── loader.py       # Data preprocessing
│── retriever.py    # Retrieval and vector search
│── tools.py        # Tool integrations
│── requirements.txt
│── .gitignore
```

---

## Installation

### Clone repository

```bash
git clone https://github.com/Shreemadhi-B/Gitinsight.git
cd Gitinsight
```

### Setup environment

```bash
python -m venv venv
source venv/bin/activate      # macOS/Linux
venv\Scripts\activate         # Windows
```

### Install dependencies

```bash
pip install -r requirements.txt
```

---

## Environment Variables

Create a `.env` file:

```
GITHUB_TOKEN=your_github_token
GOOGLE_API_KEY=your_gemini_api_key
```

---

## Running the Application

```bash
python app.py
```

Provide a GitHub repository URL and begin querying.

---

## Use Cases

- Exploring unfamiliar repositories  
- Evaluating developer contributions  
- Understanding project evolution  
- Learning from open-source codebases  

---

## Tech Stack

- Python  
- LangGraph  
- ChromaDB  
- Gemini (Google Generative AI)  
- GitHub API  

---

## Limitations

- Designed for public repositories  
- Performance depends on repository size  
- Subject to API rate limits  

---

## License

MIT License

---

## Author

Shreemadhi Babu Rajendra Prasad
