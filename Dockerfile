# ─────────────────────────────────────────
# WooAssist Pro — Private Docker Image
# Base: Ubuntu 22.04 (Lightweight)
# ─────────────────────────────────────────

FROM ubuntu:22.04

# Metadata
LABEL maintainer="D InfoTech"
LABEL project="WooAssist Pro"
LABEL version="1.0"

# Avoid interactive prompts
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# ─────────────────────────────────────────
# STEP 1: System dependencies install
# ─────────────────────────────────────────
RUN apt-get update && apt-get install -y \
    python3.11 \
    python3.11-dev \
    python3-pip \
    python3.11-venv \
    curl \
    wget \
    git \
    nodejs \
    npm \
    build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Python 3.11 as default
RUN update-alternatives --install \
    /usr/bin/python python /usr/bin/python3.11 1 && \
    update-alternatives --install \
    /usr/bin/pip pip /usr/bin/pip3 1

# ─────────────────────────────────────────
# STEP 2: Working directory set karo
# ─────────────────────────────────────────
WORKDIR /app

# ─────────────────────────────────────────
# STEP 3: Requirements copy + install
# ─────────────────────────────────────────
COPY requirements.txt .

RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ─────────────────────────────────────────
# STEP 4: Project files copy
# ─────────────────────────────────────────
COPY . .

# ─────────────────────────────────────────
# STEP 5: BMAD Method install
# ─────────────────────────────────────────
RUN npm install -g npx && \
    npx bmad-method@latest install \
    --yes \
    --output-dir /app/_bmad || true

# ─────────────────────────────────────────
# STEP 6: Required folders banavo
# ─────────────────────────────────────────
RUN mkdir -p \
    /app/data/extensions_source_code \
    /app/data/extensions_docx \
    /app/bmad_memory \
    /app/storage/chroma_db \
    /app/storage/txtai_index

# ─────────────────────────────────────────
# STEP 7: Environment
# ─────────────────────────────────────────
ENV OPENROUTER_API_KEY=""
ENV HF_HUB_DISABLE_SYMLINKS_WARNING=1

# ─────────────────────────────────────────
# STEP 8: Entry point
# ─────────────────────────────────────────
CMD ["python", "wrapper_agent.py"]