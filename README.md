# Career AI Agent

> A modular, production-ready AI-powered career assistant built with a clean layered architecture.

---

## Architecture Overview

```
career-ai-agent/
│
├── app.py                  # Application entry point
│
├── src/
│   ├── agent/              # LangGraph agent graph, nodes, and tools
│   ├── rag/                # Retrieval-Augmented Generation pipeline
│   ├── mcp/                # Model Context Protocol server and tools
│   ├── sql/                # Relational database models and queries
│   ├── ui/                 # Conversational UI (Streamlit chat interface)
│   ├── prompts/            # Prompt templates and management
│   ├── config/             # Application configuration and settings
│   └── utils/              # Shared helper utilities
│
├── tests/                  # Unit and integration tests
├── data/                   # Raw and processed data assets
└── docs/                   # Project documentation
```

### Layer Responsibilities

| Layer | Package | Responsibility |
|-------|---------|----------------|
| **Orchestration** | `agent/` | Defines the LangGraph state machine, agent nodes, and bound tools |
| **Retrieval** | `rag/` | Document loading, chunking, embedding, vector storage, and retrieval |
| **Protocol** | `mcp/` | Exposes agent capabilities as MCP-compliant server tools |
| **Persistence** | `sql/` | SQLAlchemy models, session management, and reusable queries |
| **Interface** | `ui/` | Streamlit chat UI and user interaction loop |
| **Prompts** | `prompts/` | Centralised prompt templates, versioning, and rendering |
| **Config** | `config/` | Pydantic settings loaded from environment variables |
| **Utilities** | `utils/` | Cross-cutting helpers (logging, formatting, validation) |

---

## Installation

> _Coming soon._

```bash
# 1. Clone the repository
git clone https://github.com/your-org/career-ai-agent.git
cd career-ai-agent

# 2. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment variables
cp .env.example .env
# Edit .env and fill in your API keys and settings
```

---

## Usage

> _Coming soon._

```bash
python app.py
```

---

## Running Tests

> _Coming soon._

```bash
pytest tests/
```

---

## Contributing

> _Coming soon._

---

## License

> _Coming soon._
