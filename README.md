# FORGERY: Executive AI Agent System 🤖

**Scalable, Self-Improving Autonomous Agent Architecture**

Forgery is an advanced AI agent system designed to handle complex, multi-step executive tasks with high reliability. Unlike standard chatbots, it prioritizes **determinism**, **deep contextual memory**, and **cost control**.

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-61DAFB?style=for-the-badge&logo=react&logoColor=black)
![LangGraph](https://img.shields.io/badge/LangGraph-1C3C3C?style=for-the-badge&logo=chainlink&logoColor=white)

## 🧠 Core Architecture

The system is built on a sophisticated stack designed for agentic workflows:

- **Orchestration (LangGraph)**: Manages agent state and flow control, ensuring deterministic execution and allowing for "Human-in-the-Loop" checkpoints.
- **Memory (GraphRAG)**: Combines Neo4j (Graph DB) with Vector DBs to enable complex, multi-hop reasoning and persistent context.
- **Tool Management (RAG-on-Tools)**: Uses LlamaIndex to dynamically select the most relevant tools for a given task, scaling to hundreds of available tools.
- **Observability**: Integrated with **Langfuse** and **LangSmith** for tracing execution paths and monitoring costs.

## 🛠️ Tech Stack

### Backend
- **Language**: Python 3.10+
- **API**: FastAPI
- **Protocol**: Model Context Protocol (MCP) Server
- **Database**: Neo4j, ChromaDB/Qdrant

### Frontend
- **Framework**: Next.js (React)
- **Styling**: Tailwind CSS
- **State**: React Query

### Infrastructure
- **Containerization**: Docker & Docker Compose

## 🚀 Quick Start

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/brendon92/portfolio.git
    cd portfolio/reactjs/forgery
    ```

2.  **Start the infrastructure (Docker)**:
    ```bash
    docker-compose up -d
    ```

3.  **Run the Backend**:
    ```bash
    cd backend
    pip install -r requirements.txt
    uvicorn main:app --reload
    ```

4.  **Run the Frontend**:
    ```bash
    cd frontend
    npm install
    npm run dev
    ```

## 📸 Architecture Diagram

*(Placeholder for Architecture Diagram)*

![Architecture](docs/architecture_placeholder.png)

## 🔮 Roadmap

- [x] Core LangGraph Node Architecture
- [x] MCP Server Integration
- [x] Basic Frontend Dashboard
- [ ] GraphRAG Implementation
- [ ] Self-Improvement Loops (Reflection)
