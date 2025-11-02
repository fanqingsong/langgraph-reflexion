# Reflexion Agent with LangGraph 🦜🕸️

Implementation of a sophisticated Reflexion agent using LangGraph and LangChain, designed to generate high-quality responses through self-reflection and iterative improvement.

This project demonstrates advanced AI agent capabilities using LangGraph's state-of-the-art control flow mechanisms for self-reflection and response refinement.

![Logo](graph.png)

## Features

- **Self-Reflection**: Implements sophisticated reflection mechanisms for response improvement
- **Iterative Refinement**: Uses a graph-based approach to iteratively enhance responses
- **Production-Ready**: Built with scalability and real-world applications in mind
- **Integrated Search**: Leverages Tavily search for enhanced response accuracy
- **Structured Output**: Uses Pydantic models for reliable data handling
- **Docker Support**: Complete Docker setup for easy deployment
- **LangGraph Dev Server**: Supports LangGraph Studio for visualization and debugging

## Architecture

The agent uses a graph-based architecture with the following components:

- **Entry Point**: `draft` node for initial response generation
- **Processing Nodes**: `execute_tools` and `revise` for refinement
- **Maximum Iterations**: 2 (configurable)
- **Chain Components**: First responder and revisor using GPT-4
- **Tool Integration**: Tavily Search for web research

## Project Structure

```
.
├── src/
│   └── reflexion_agent/
│       ├── __init__.py
│       ├── infra/             # Infrastructure 模块
│       │   ├── config.py      # Azure OpenAI 配置
│       │   ├── llm.py         # LLM 管理
│       │   ├── prompts.py    # 提示模板
│       │   └── schema.py     # Pydantic schemas
│       ├── nodes/             # 节点模块
│       │   ├── draft.py      # 初始答案生成节点
│       │   ├── execute_tools.py  # 工具执行节点
│       │   ├── revise.py     # 答案修订节点
│       │   └── event_loop.py # 事件循环条件函数
│       ├── graph.py          # Graph 定义
│       └── main.py           # Entry point
├── examples/
│   └── basic_example.py       # Example usage
├── Dockerfile                 # Docker configuration
├── docker-compose.yml         # Docker Compose configuration
├── langgraph.json            # LangGraph dev server config
├── requirements.txt          # Python dependencies
├── pyproject.toml            # Project metadata
├── start.sh                  # Start script
└── stop.sh                   # Stop script
```

## Environment Variables

### Azure OpenAI Configuration (Recommended)

To use Azure OpenAI, add the following environment variables to your `.env` file:

```bash
AZURE_OPENAI_API_KEY=your_azure_openai_api_key_here
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_VERSION=2024-02-15-preview  # Optional, defaults to "2024-02-15-preview"
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4            # Optional, defaults to "gpt-4"
TAVILY_API_KEY=your_tavily_api_key_here
LANGCHAIN_API_KEY=your_langchain_api_key_here  # Optional, for tracing
LANGCHAIN_TRACING_V2=true                      # Optional
LANGCHAIN_PROJECT=reflexion agent               # Optional
```

### Standard OpenAI Configuration (Alternative)

Alternatively, you can use standard OpenAI API:

```bash
OPENAI_API_KEY=your_openai_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here
LANGCHAIN_API_KEY=your_langchain_api_key_here  # Optional, for tracing
LANGCHAIN_TRACING_V2=true                      # Optional
LANGCHAIN_PROJECT=reflexion agent               # Optional
```

> **Important Notes**: 
> - The project **defaults to Azure OpenAI** if `AZURE_OPENAI_API_KEY` and `AZURE_OPENAI_ENDPOINT` are set. Otherwise, it falls back to standard OpenAI.
> - If you enable tracing by setting `LANGCHAIN_TRACING_V2=true`, you must have a valid LangSmith API key set in `LANGCHAIN_API_KEY`. Without a valid API key, the application will throw an error. If you don't need tracing, simply remove or comment out these environment variables.

## Installation

### Using Poetry (Recommended)

```bash
poetry install
```

### Using pip

```bash
pip install -r requirements.txt
```

## Run Locally

### Option 1: Using Python directly

```bash
# Run the main script
poetry run python -m reflexion_agent.main

# Or run an example
poetry run python examples/basic_example.py
```

### Option 2: Using Docker (Recommended for Production)

1. Create a `.env` file with your API keys (see Environment Variables above)

2. Start the application:
   ```bash
   ./start.sh
   ```

3. Access the application:
   - API: http://localhost:2024
   - API Docs: http://localhost:2024/docs
   - LangGraph Studio: https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2024

4. Stop the application:
   ```bash
   ./stop.sh
   ```

### Option 3: Using LangGraph Dev Server

```bash
# Install LangGraph CLI if not already installed
pip install langgraph-cli[inmem]

# Start the dev server
langgraph dev
```

The server will start on http://localhost:2024 and you can access the API documentation at http://localhost:2024/docs.

## Development Setup

1. Get your API keys:
   - **Azure OpenAI** (recommended): 
     - [Azure Portal](https://portal.azure.com/) - Create an Azure OpenAI resource
     - Get your API key, endpoint URL, and deployment name
   - **Standard OpenAI** (alternative):
     - [OpenAI Platform](https://platform.openai.com/) for GPT-4 access
   - [Tavily](https://tavily.com/) for search functionality
   - [LangSmith](https://smith.langchain.com/) (optional) for tracing

2. Create a `.env` file with your API keys:
   ```bash
   # For Azure OpenAI (recommended)
   AZURE_OPENAI_API_KEY=your_key_here
   AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
   AZURE_OPENAI_API_VERSION=2024-02-15-preview
   AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4
   TAVILY_API_KEY=your_key_here
   
   # Or for standard OpenAI
   # OPENAI_API_KEY=your_key_here
   # TAVILY_API_KEY=your_key_here
   ```

3. Install dependencies:
   ```bash
   poetry install
   # or
   pip install -r requirements.txt
   ```

## Using as a Package

You can also use this as a Python package:

```python
from reflexion_agent.graph import create_reflexion_graph

# Create the graph
graph = create_reflexion_graph(max_iterations=3)

# Invoke with a query
result = graph.invoke("Your question here")
```

## Docker Development

For development with hot-reloading:

```bash
docker compose up
```

The source code is mounted as volumes, so changes to the code will be reflected immediately.

## Running Tests

To run tests, use the following command:

```bash
poetry run pytest . -s -v
```

## Project Improvements

This project has been optimized with the following improvements:

- ✅ **Standard Python Package Structure**: Code organized in `src/` directory
- ✅ **Docker Support**: Complete Docker setup with docker-compose
- ✅ **LangGraph Dev Server**: Support for LangGraph Studio
- ✅ **Modular Design**: Separated concerns (models, chains, tools, graph)
- ✅ **Examples**: Ready-to-use examples in `examples/` directory
- ✅ **Production Ready**: Health checks, proper error handling, and restart policies

## Acknowledgements

This project builds upon:
- [LangGraph](https://langchain-ai.github.io/langgraph/tutorials/reflexion/reflexion/) for agent control flow
- [LangChain](https://github.com/langchain-ai/langchain) for LLM interactions
- [Tavily API](https://tavily.com/) for web search capabilities

## 🔗 Links
[![portfolio](https://img.shields.io/badge/my_portfolio-000?style=for-the-badge&logo=ko-fi&logoColor=white)](https://www.udemy.com/course/langgraph/?referralCode=FEA50E8CBA24ECD48212)
[![linkedin](https://img.shields.io/badge/linkedin-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/eden-marco/)
[![twitter](https://img.shields.io/badge/twitter-1DA1F2?style=for-the-badge&logo=twitter&logoColor=white)](https://www.udemy.com/user/eden-marco/)
