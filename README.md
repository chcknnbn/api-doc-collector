# API Document Collector 🤖

A generalized pipeline that automatically crawls an API documentation website, parses its structure using an LLM, extracts clean Markdown content, and optionally builds a local RAG Vector Database for agent-based pipelines.

## ⭐ Features
1. **Intelligent Config Generation**: Give it a URL, and an LLM (local Ollama or remote API) analyzes the HTML to generate dynamic CSS selectors and a crawling config.
2. **Robust Scraping**: Recursively traverses the API documentation and converts complex HTML nodes into clean, LLM-friendly Markdown syntax (`.md`), retaining YAML frontmatter metadata.
3. **Quality Validation**: Automatically samples the generated markdowns and validates the presence of parameters, endpoints, and code samples using an LLM.
4. **Instant RAG Building**: Includes a built-in module to chunk markdown headers and generate a local ChromaDB vector store using HuggingFace embeddings (`all-MiniLM-L6-v2`).

## 📋 Prerequisites
- Python 3.10+
- (Optional) [Ollama](https://ollama.com/) running locally for free LLM integrations.

## 🚀 Installation
```bash
# Clone the repository
git clone https://github.com/your-username/api-doc-collector.git
cd api-doc-collector

# Install dependencies
pip install -r requirements.txt
```

## 💻 Usage

Run the main pipeline by supplying a documentation base URL.

### 1. Basic (Scrape to Markdown only)
This collects the HTMLs and extracts clean markdowns into the `./docs` folder.
```bash
python main.py https://docs.example.com/api
```

### 2. Using Local LLM (Ollama)
Automatically configures the crawler and validates the output using Llama 3.
```bash
# Ensure Ollama is running in the background
export OLLAMA_HOST=localhost
python main.py https://docs.example.com/api --llm local:ollama/llama3.2
```

### 3. Using OpenAI & Building RAG Vector DB
Builds the `./rag_db` vector database automatically after successfully pulling the documents.
```bash
export OPENAI_API_KEY="sk-..."
python main.py https://docs.example.com/api --llm api:openai:gpt-4o --rag
```

## 📁 Project Structure
```text
api-doc-collector/
├── configs/           # Generated JSON crawler configs
├── docs/              # Extracted Markdown files (Git ignored)
├── rag_db/            # Generated Chroma Vector DB (Git ignored)
├── src/
│   ├── llm_config.py  # LLM Web HTML analyzer
│   ├── collector.py   # Recursive Scraper & Markdown converter
│   ├── validator.py   # LLM Quality Gate
│   └── rag_builder.py # LangChain RAG pipeline
├── requirements.txt
└── main.py            # CLI Entrypoint
```

## 🤝 Contributing
Contributions, issues, and feature requests are welcome!
