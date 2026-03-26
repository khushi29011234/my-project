# 🤖 WooAssist Pro
### AI-Powered WooCommerce PM Agent
**D InfoTech — Private Repository**

---

## 🚀 Quick Start

### Prerequisites
- Docker installed
- Docker Compose installed
- OpenRouter API Key
- Git

---

## 📦 Setup Steps

### Step 1 — Repo Clone Karo
```bash
git clone https://github.com/khushi29011234/my-project.git
cd wooassist-pro
```

### Step 2 — Setup Script Run Karo
```bash
# Linux/Mac
chmod +x setup.sh
./setup.sh

# Windows (Git Bash)
bash setup.sh
```

Setup script automatically:
- ✅ Prerequisites check kare
- ✅ .env file banave
- ✅ Docker image build kare
- ✅ Documents index kare

### Step 3 — API Key Set Karo
`.env` file ma:
```
OPENROUTER_API_KEY=sk-or-v1-xxxxx
```

### Step 4 — Agent Start Karo
```bash
docker-compose run --rm -it wooassist-pro
```

---

## 📁 Data Setup

Source code ane docs add karva:
```
data/
├── woo-bundle-choice/          ← Main plugin source
├── extensions_source_code/     ← Extension source codes
├── woo_project.docx            ← Main documentation
└── extensions_docx/            ← Extension docs
```

Data add karya pachhi index karo:
```bash
docker-compose run --rm wooassist-pro \
    python -m rag_system.index_docs
```

---

## 🔧 Common Commands

```bash
# Agent start
docker-compose run --rm -it wooassist-pro

# Documents reindex
docker-compose run --rm wooassist-pro \
    python -m rag_system.index_docs

# Image rebuild
docker-compose build

# Container stop
docker-compose down
```

---

## 🔒 Privacy

- ✅ GitHub repo — **Private**
- ✅ Docker image — **Private**
- ✅ Source code — **Never public**
- ✅ API keys — **`.env` file (never committed)**

---

## 🏗️ Architecture

```
wrapper_agent.py          ← Entry point
    ↓
bmad_integration.py       ← Multi-agent chain
    ├── BA Agent           ← Problem analyze
    ├── Planner Agent      ← Tasks break
    ├── PM Agent           ← Source code + RAG
    └── QA Agent           ← Verify answer
    ↓
RAG Tool
    ├── LlamaIndex         ← Document processing
    ├── ChromaDB           ← Vector storage
    └── txtai              ← Fast semantic search
```

---

**D InfoTech — Internal Use Only**
