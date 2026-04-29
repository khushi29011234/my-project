# bmad_integration.py
# BMAD Multi-Agent Chain — Reddit workflow
# BA → Planner → PM → QA
# Self-Improvement: Lessons MANDATORY apply

import os
import sys
import json
import re
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
            max_tokens=500,
        )

        self.bmad_loader = BMADAgentLoader()

        self.pm_prompt = self.bmad_loader.get_agent_prompt("woo-pm")
        self.ba_prompt = self.bmad_loader.get_agent_prompt("woo-ba")
        self.planner_prompt = self.bmad_loader.get_agent_prompt("woo-planner")
        self.qa_prompt = self.bmad_loader.get_agent_prompt("woo-qa")

        print("✅ BMAD PM Agent ready")
        print("✅ BMAD BA Agent ready")
        print("✅ BMAD Planner Agent ready")
        print("✅ BMAD QA Agent ready")

        self.rag_tool = RAGTool()
        self.memory = MemoryManager()

    # ─────────────────────────────────────────
    # AGENT 1 — BA
    # ─────────────────────────────────────────

    def _ba_analyze(self, original_query, module, query_type) -> str:
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

    def _planner_breakdown(self, original_query, module, ba_analysis) -> str:
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
        bmad_query,
        rag_query,
        original_query,
        module,
        query_type,
        ba_analysis,
        task_plan,
        memory_context,
    ) -> str:
        source_context = self.rag_tool.search_source_code(bmad_query)
        doc_context = self.rag_tool.search_docs(rag_query)

        if source_context and "not available" not in source_context:
            self.memory.save_finding(original_query, source_context[:200])

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

        # UPDATED: Lessons MANDATORY apply
        memory_section = ""
        if memory_context:
            memory_section = f"""
━━━ PAST LESSONS — MANDATORY APPLY ━━━
{memory_context}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CRITICAL: Past lessons ma jo specific
technical points lakhela hoy —
JSON mismatch, PHP memory, cron jobs,
Advadd_Info.php, backup restore,
WooCommerce Settings paths,
localStorage, Elementor widget,
privacy plugin etc.
e BADHA current answer ma include KARO.
Past feedback IGNORE NEVER karvo.
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
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

━━━ DOCUMENTATION (RAG) ━━━━━━━━━━━━━
{doc_context}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
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
8. Past lessons → MANDATORY APPLY
9. Specific UI paths → ALWAYS include
   (WooCommerce > Settings > ...)
"""

        try:
            return self.llm.complete(prompt).text
        except Exception as e:
            return f"❌ PM Analysis failed: {e}"

    # ─────────────────────────────────────────
    # AGENT 4 — QA
    # ─────────────────────────────────────────

    def _qa_verify(self, pm_answer, original_query, query_type) -> str:
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
        bmad_query=None,
        rag_query=None,
        original_query=None,
        module=None,
        query_type="issue",
        query=None,
        query_intent=None,
    ) -> str:
        if bmad_query is None:
            bmad_query = query or ""
        if rag_query is None:
            rag_query = query or ""
        if original_query is None:
            original_query = query or ""

        # NEW: GUIDANCE MODE — Skip BA/Planner, give short answer
        if query_intent == "guidance":
            print("📖 Guidance Mode: Quick answer only...")

            # Check knowledge base first for known queries
            kb_path = os.getenv("KB_PATH", "knowledge_base.json")

            try:
                with open(kb_path, "r", encoding="utf-8") as f:
                    kb = json.load(f)

                # Normalize query - remove "as an admin" prefix and extra spaces
                query_clean = original_query.lower()
                if "as an admin" in query_clean:
                    query_clean = query_clean.replace("as an admin", "").strip()
                # Remove quotes
                query_clean = query_clean.replace('"', "").replace("'", "").strip()
                # Remove common query patterns
                query_clean = (
                    query_clean.replace("mane guide karo:", "")
                    .replace("short answer aapjo.", "")
                    .replace(", mane guide karo:", "")
                    .strip()
                )
                # Remove special characters but keep spaces
                query_clean = re.sub(r"[—–-]", " ", query_clean)
                query_clean = re.sub(r"[^\w\s]", "", query_clean)
                query_clean = re.sub(r"\s+", " ", query_clean).strip()

                # KB lookup
                stop_words = {
                    "na",
                    "ma",
                    "kya",
                    "kay",
                    "ku",
                    "ko",
                    "aapjo",
                    "karva",
                    "select",
                    "the",
                    "a",
                    "with",
                    "view",
                    "configure",
                    "tab",
                    "size",
                }
                for kb_key, kb_answer in kb.get("guidance_answers", {}).items():
                    kb_key_lower = kb_key.lower()
                    kb_words = set(kb_key_lower.split()) - stop_words
                    query_words = set(query_clean.split()) - stop_words
                    # Check if most important KB words are in query (at least 50%)
                    if kb_words and len(kb_words & query_words) >= len(kb_words) * 0.5:
                        return kb_answer

            except Exception as e:
                pass  # Silent fail for KB

            # If no KB match, search RAG
            source_context = self.rag_tool.search_source_code(bmad_query)
            doc_context = self.rag_tool.search_docs(rag_query)

            guidance_prompt = f"""
{self.pm_prompt}

GUIDANCE MODE: Short 1-2 sentence answer about BEST PRACTICE or AVAILABLE OPTIONS.
Do NOT provide Action Plan, Tasks, Risk Assessment, or detailed steps.
Just give direct answer.

IMPORTANT: 
1. If query asks about "options", "kontu", "choices", "valid values" - LIST the available options/choices.
2. If query asks about "best practice", "recommended", "kevo" - state the RECOMMENDED choice.
3. Focus on what is OPTIMAL for business/conversion.
4. For admin settings, mention both available options AND recommended choice.

Source Code: {source_context}
Documentation: {doc_context}
Query: {original_query}
Module: {module}

STRICT: Keep answer under 3 lines. Direct and simple.
"""
            try:
                return self.llm.complete(guidance_prompt).text
            except Exception as e:
                return f"Answer: {doc_context[:200] if doc_context else 'Check documentation'}"

        # Memory — lessons FIRST
        memory_context = self.memory.read_all_context()

        # MODE 3 — FASTER: txtai retrieval + LLM synthesis
        if query_intent == "faster":
            print("⚡ Faster Mode: txtai + LLM synthesis...")

            # Step 1: txtai fast retrieval
            result = self.rag_tool.answer_from_docs(original_query)
            context = result.get("answer", "")
            sources = result.get("sources", [])

            if not context or "No relevant" in context:
                return "❌ No relevant documentation found for this query."

            # Step 2: LLM synthesis over retrieved chunks only
            fast_prompt = f"""
{self.pm_prompt}

FAST MODE: Answer from retrieved documentation ONLY.
Do NOT use external knowledge. Synthesize from context.

Context from documentation:
{context}

User Query: {original_query}

STRICT:
1. Answer ONLY from provided context above
2. Keep under 10 lines, direct
3. Include specific steps/file paths if available in context
4. Mention source files at end
5. Gujarati+English Roman only
6. NO Action Plan, NO Tasks, NO Risk Assessment
"""
            try:
                answer = self.llm.complete(fast_prompt).text
                output = f"⚡ FAST ANSWER:\n\n{answer}"
                if sources:
                    output += f"\n\n📚 Sources: {', '.join(sources[:3])}"
                    if len(sources) > 3:
                        output += f" (+{len(sources)-3} more)"
                return output
            except Exception as e:
                return f"❌ Fast mode error: {e}"

        # HOW-TO — BA + Planner skip
        if query_type == "howto":
            print("🔍 Scanning source code (BMAD)...")
            print("📚 Searching documentation (RAG)...")
            return self._pm_analyze(
                bmad_query,
                rag_query,
                original_query,
                module,
                "howto",
                "",
                "",
                memory_context,
            )

        # ISSUE — Full chain
        print("🧠 BA Agent: Analyzing problem...")
        ba = self._ba_analyze(original_query, module, query_type)

        print("📝 Planner: Breaking into tasks...")
        plan = self._planner_breakdown(original_query, module, ba)

        print("🔍 Scanning source code (BMAD)...")
        print("📚 Searching documentation (RAG)...")
        pm = self._pm_analyze(
            bmad_query,
            rag_query,
            original_query,
            module,
            query_type,
            ba,
            plan,
            memory_context,
        )

        print("✅ QA Agent: Verifying answer...")
        return self._qa_verify(pm, original_query, query_type)
