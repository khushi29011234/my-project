# bmad_integration.py
# BMAD Multi-Agent Chain — Reddit workflow
# BA → Planner → PM → QA
# Self-Improvement: Lessons context use kare

import os
from dotenv import load_dotenv
from llama_index.llms.openrouter import OpenRouter
from rag_system.rag_tool import RAGTool
from rag_system.memory_manager import MemoryManager
from bmad_core.agent_loader import BMADAgentLoader

load_dotenv()


class BMADPMAgent:

    def __init__(self):

        self.llm = OpenRouter(
            model="meta-llama/llama-3.3-70b-instruct",
            api_key=os.getenv("OPENROUTER_API_KEY"),
            temperature=0.1,
            max_tokens=1500
        )

        self.bmad_loader = BMADAgentLoader()

        self.pm_prompt = \
            self.bmad_loader.get_agent_prompt("woo-pm")
        self.ba_prompt = \
            self.bmad_loader.get_agent_prompt("woo-ba")
        self.planner_prompt = \
            self.bmad_loader.get_agent_prompt(
                "woo-planner"
            )
        self.qa_prompt = \
            self.bmad_loader.get_agent_prompt("woo-qa")

        print("✅ BMAD PM Agent ready")
        print("✅ BMAD BA Agent ready")
        print("✅ BMAD Planner Agent ready")
        print("✅ BMAD QA Agent ready")

        self.rag_tool = RAGTool()
        self.memory = MemoryManager()

    # ─────────────────────────────────────────
    # AGENT 1 — BA
    # ─────────────────────────────────────────

    def _ba_analyze(
        self, original_query, module, query_type
    ) -> str:
        prompt = f"""
{self.ba_prompt}

User Query: {original_query}
Module: {module}
Query Type: {query_type}

Analyze from business perspective. Max 5 lines.
"""
        try:
            return self.llm.complete(prompt).text
        except Exception:
            return f"Module: {module}, Issue: {original_query}"

    # ─────────────────────────────────────────
    # AGENT 2 — Planner
    # ─────────────────────────────────────────

    def _planner_breakdown(
        self, original_query, module, ba_analysis
    ) -> str:
        prompt = f"""
{self.planner_prompt}

Module: {module}
Issue: {original_query}
BA Analysis: {ba_analysis}

Break into 3-4 specific tasks. Keep concise.
"""
        try:
            return self.llm.complete(prompt).text
        except Exception:
            return ""

    # ─────────────────────────────────────────
    # AGENT 3 — PM (Main)
    # ─────────────────────────────────────────

    def _pm_analyze(
        self,
        bmad_query, rag_query,
        original_query, module,
        query_type, ba_analysis,
        task_plan, memory_context
    ) -> str:

        source_context = \
            self.rag_tool.search_source_code(bmad_query)
        doc_context = \
            self.rag_tool.search_docs(rag_query)

        if source_context and \
                "not available" not in source_context:
            self.memory.save_finding(
                original_query, source_context[:200]
            )

        if query_type == "howto":
            type_instruction = (
                "QUERY TYPE: HOW-TO / FEATURE\n"
                "- Emergency checklist NEVER\n"
                "- Flow + files + URL structure\n"
                "- Team confirmation ALWAYS"
            )
        else:
            type_instruction = (
                "QUERY TYPE: ISSUE / ERROR\n"
                "- Emergency checklist FIRST\n"
                "- Source code thi root cause\n"
                "- Specific file + fix"
            )

        memory_section = ""
        if memory_context:
            memory_section = f"""
━━━ MEMORY + PAST LESSONS ━━━━━━━━━━━
{memory_context}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
IMPORTANT: Past lessons thi LEARN karo —
same mistakes repeat na karo
"""

        agent_context = ""
        if ba_analysis:
            agent_context += (
                f"\n━━━ BA ANALYSIS ━━━━━━━━━━━━━━━━━\n"
                f"{ba_analysis}\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            )
        if task_plan:
            agent_context += (
                f"\n━━━ TASK PLAN ━━━━━━━━━━━━━━━━━━━\n"
                f"{task_plan}\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            )

        prompt = f"""
{self.pm_prompt}

═══════════════════════════════════════
{type_instruction}
═══════════════════════════════════════

━━━ SOURCE CODE (BMAD) ━━━━━━━━━━━━━━
{source_context}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

━━━ DOCUMENTATION (RAG) ━━━━━━━━━━━━━
{doc_context}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{agent_context}{memory_section}
Query: {original_query}
{f"Module: {module}" if module else ""}

STRICT:
1. File → source code context thi ONLY
2. Root cause → context thi ONLY
3. Gujarati+English Roman script — Hindi ZERO
4. Gujarati Unicode script NEVER
5. Urgency → ONLY demo/urgent/deadline exact words
6. Generic → NEVER
7. "better" single 't'
8. Past lessons → APPLY karo
"""

        try:
            return self.llm.complete(prompt).text
        except Exception as e:
            return f"❌ PM Analysis failed: {e}"

    # ─────────────────────────────────────────
    # AGENT 4 — QA
    # ─────────────────────────────────────────

    def _qa_verify(
        self, pm_answer, original_query, query_type
    ) -> str:
        prompt = f"""
{self.qa_prompt}

Original Query: {original_query}
Query Type: {query_type}

PM Agent Answer:
{pm_answer}

Silently verify. Return clean answer only.
No QA headers. No commentary.
"""
        try:
            return self.llm.complete(prompt).text
        except Exception:
            return pm_answer

    # ─────────────────────────────────────────
    # ORCHESTRATOR
    # ─────────────────────────────────────────

    def analyze_issue(
        self,
        bmad_query=None, rag_query=None,
        original_query=None, module=None,
        query_type="issue", query=None
    ) -> str:

        if bmad_query is None:
            bmad_query = query or ""
        if rag_query is None:
            rag_query = query or ""
        if original_query is None:
            original_query = query or ""

        # Memory — lessons FIRST (self-improvement)
        memory_context = self.memory.read_all_context()

        # HOW-TO — BA + Planner skip
        if query_type == "howto":
            print("🔍 Scanning source code (BMAD)...")
            print("📚 Searching documentation (RAG)...")
            return self._pm_analyze(
                bmad_query, rag_query,
                original_query, module, "howto",
                "", "", memory_context
            )

        # ISSUE — Full chain
        print("🧠 BA Agent: Analyzing problem...")
        ba = self._ba_analyze(
            original_query, module, query_type
        )

        print("📝 Planner: Breaking into tasks...")
        plan = self._planner_breakdown(
            original_query, module, ba
        )

        print("🔍 Scanning source code (BMAD)...")
        print("📚 Searching documentation (RAG)...")
        pm = self._pm_analyze(
            bmad_query, rag_query,
            original_query, module, query_type,
            ba, plan, memory_context
        )

        print("✅ QA Agent: Verifying answer...")
        return self._qa_verify(
            pm, original_query, query_type
        )
