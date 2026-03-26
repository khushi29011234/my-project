#!/bin/bash
# ─────────────────────────────────────────
# WooAssist Pro — Automated Setup Script
# Run this after GitHub repo clone
# D InfoTech — Private
# ─────────────────────────────────────────

set -e  # Exit on any error

echo ""
echo "╔══════════════════════════════════════╗"
echo "║     WooAssist Pro — Setup Script     ║"
echo "║          D InfoTech Private          ║"
echo "╚══════════════════════════════════════╝"
echo ""

# ─────────────────────────────────────────
# STEP 1: Check prerequisites
# ─────────────────────────────────────────
echo "📋 STEP 1: Prerequisites check karo..."

# Docker check
if ! command -v docker &> /dev/null; then
    echo "❌ Docker install nathi. Install karo:"
    echo "   https://docs.docker.com/get-docker/"
    exit 1
fi
echo "✅ Docker: $(docker --version)"

# Docker Compose check
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose install nathi."
    exit 1
fi
echo "✅ Docker Compose: $(docker-compose --version)"

# ─────────────────────────────────────────
# STEP 2: .env file check
# ─────────────────────────────────────────
echo ""
echo "📋 STEP 2: Environment setup..."

if [ ! -f ".env" ]; then
    echo "⚠️  .env file nathi. Banavi raha chu..."
    cat > .env << 'EOF'
# WooAssist Pro — Environment Variables
# Aa file private rakho — never commit to git

OPENROUTER_API_KEY=your_openrouter_api_key_here
EOF
    echo "✅ .env file banavi — API key add karo"
    echo "   Aa file ma taro OPENROUTER_API_KEY nakho"
    echo "   Pachhi setup.sh dobara run karo"
    exit 0
fi

# API key check
if grep -q "your_openrouter_api_key_here" .env; then
    echo "❌ .env file ma API key set nathi!"
    echo "   .env file kholo ane OPENROUTER_API_KEY set karo"
    exit 1
fi
echo "✅ Environment configured"

# ─────────────────────────────────────────
# STEP 3: Required folders banavo
# ─────────────────────────────────────────
echo ""
echo "📋 STEP 3: Folders banavo..."

mkdir -p data/extensions_source_code
mkdir -p data/extensions_docx
mkdir -p bmad_memory
mkdir -p storage/chroma_db
mkdir -p storage/txtai_index

echo "✅ Folders ready"

# ─────────────────────────────────────────
# STEP 4: Docker image build karo
# ─────────────────────────────────────────
echo ""
echo "📋 STEP 4: Docker image build karo..."
echo "   (Pehli vaar time lagshe — 5-10 minutes)"
echo ""

docker-compose build

echo "✅ Docker image ready"

# ─────────────────────────────────────────
# STEP 5: Documents index karo
# ─────────────────────────────────────────
echo ""
echo "📋 STEP 5: Documents index karo..."
echo "   (Source code + docs index thashe)"
echo ""

docker-compose run --rm wooassist-pro \
    python -m rag_system.index_docs

echo "✅ Documents indexed"

# ─────────────────────────────────────────
# STEP 6: Setup complete
# ─────────────────────────────────────────
echo ""
echo "╔══════════════════════════════════════╗"
echo "║       ✅ Setup Complete!             ║"
echo "╚══════════════════════════════════════╝"
echo ""
echo "Agent start karva maate:"
echo ""
echo "   docker-compose run --rm -it wooassist-pro"
echo ""
echo "Ya seedho:"
echo ""
echo "   docker-compose up"
echo ""
