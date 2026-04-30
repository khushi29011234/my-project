# wrapper_agent.py
# Custom Wrapper Agent — BMAD + RAG + Memory
# Self-Improvement Loop — Reddit workflow

import os
import re
from dotenv import load_dotenv
from colorama import init, Fore, Style
from bmad_integration import BMADPMAgent
from rag_system.memory_manager import MemoryManager

init(autoreset=True)
load_dotenv()


# ─────────────────────────────────────────────────
# CONVERSATION CONTEXT
# ─────────────────────────────────────────────────


class ConversationContext:
    def __init__(self):
        self.raw_query = None
        self.module = None
        self.query_type = "issue"
        self.issue_type = None
        self.location = None
        self.pending_field = None
        self.query_intent = None
        self.mode_selected = None  # NEW: "source_code" or "guidance"
        self.guidance_keywords = [
            "karvu joiye",
            "karvu?",
            "karvu ke nai",
            "select karvu",
            "kontu",
            "kayu",
            "su kare che",
            "shu kare che",
            "format kevo",
            "format shu",
            "upload karvu",
            "include karvu",
            "guide karo",
            "guide karu",
            "short answer",
            "kyaa rakhvu",
            "konti template",
            "setting karvu",
            "configure karvu",
        ]
        self.troubleshooting_keywords = [
            "error",
            "fatal",
            "not working",
            "fail",
            "issue",
            "problem",
            "broken",
            "bug",
            "error aave che",
            "error ave che",
            "kaam nathi karto",
            "correct karvo",
            "fix",
            "solve",
            "resolve",
            "line ",
            "php ma",
            "class not found",
            "undefined",
            "exception",
        ]

    def reset(self):
        self.__init__()

    def is_complete(self) -> bool:
        return (
            self.raw_query is not None
            and self.module is not None
            and self.issue_type is not None
        )

    # NEW — Intent Classification
    def detect_intent(self, query: str) -> str:
        q = query.lower().strip()

        # Check for troubleshooting/bug keywords
        for keyword in self.troubleshooting_keywords:
            if keyword in q:
                self.query_intent = "troubleshooting"
                return "troubleshooting"

        # Check for guidance keywords or question format
        for keyword in self.guidance_keywords:
            if keyword in q:
                self.query_intent = "guidance"
                return "guidance"

        # Default: troubleshooting (for issue-related queries)
        self.query_intent = "troubleshooting"
        return "troubleshooting"

    def extract_module(self, query: str) -> str:
        """
        Extract module name from query with improved accuracy.
        Used when module is not detected through normal flow.
        """
        modules = [
            "ring builder", "ring building", "double pagination",
            "pagination", "filter", "checkout", "cart",
            "product", "admin", "general",
            "natural diamond", "lab grown",
            "product attributes", "bundle"
        ]
        q = query.lower().strip()
        for m in modules:
            if m in q:
                return m
        return "general"

    def build_refined_query(self) -> dict:
        location_str = f", Location: {self.location}" if self.location else ""

        if self.query_type == "howto":
            bmad_query = (
                f"{self.module} module ni "
                f"functionality, flow, files, "
                f"logic: {self.raw_query}"
            )
            rag_query = (
                f"{self.module} feature "
                f"documentation, URL structure, "
                f"process: {self.raw_query}"
            )
        else:
            bmad_query = (
                f"{self.module} module ma "
                f"{self.issue_type} issue"
                f"{location_str}: "
                f"{self.raw_query}. "
                f"Constructor, init, hooks, "
                f"functions scan karo. "
                f"Root cause find karo."
            )
            rag_query = (
                f"{self.module} {self.issue_type} "
                f"issues, solutions, fixes: "
                f"{self.raw_query}"
            )

        return {
            "bmad_query": bmad_query,
            "rag_query": rag_query,
            "original": self.raw_query,
        }


# ─────────────────────────────────────────────────
# CLARIFICATION FLOW
# ─────────────────────────────────────────────────

CLARIFICATION_FLOW = {
    "ring builder": [
        {
            "field": "issue_type",
            "question": "Ring builder ma kya type no issue che?",
            "options": [
                "Display issue",
                "Functionality issue",
                "Filter issue",
                "Checkout issue",
            ],
        },
        {
            "field": "location",
            "question": "Kyaa page par issue aave che?",
            "options": ["Shop page", "Product page", "Checkout page", "Admin panel"],
        },
    ],
    "ring building": [
        {
            "field": "issue_type",
            "question": "Ring building process ma kya issue che?",
            "options": [
                "Setting select issue",
                "Diamond selection issue",
                "URL/redirect issue",
                "Checkout issue",
            ],
        }
    ],
    "double pagination": [
        {
            "field": "issue_type",
            "question": "Pagination issue kyaa tab par che?",
            "options": ["Diamond tab", "Lab-Grown tab", "Banne tabs", "Other tab"],
        }
    ],
    "pagination": [
        {
            "field": "issue_type",
            "question": "Pagination ma kya issue che?",
            "options": [
                "Double pagination",
                "Pagination kaam nathi karto",
                "Wrong page count",
                "AJAX reload issue",
            ],
        }
    ],
    "filter": [
        {
            "field": "issue_type",
            "question": "Filter ma kya issue che?",
            "options": [
                "Double filter show",
                "Filter kaam nathi karto",
                "Wrong results",
                "Slow loading",
            ],
        },
        {
            "field": "location",
            "question": "Kyaa page par filter issue aave che?",
            "options": [
                "Category page",
                "Shop page",
                "Lab-grown page",
                "Natural diamond page",
            ],
        },
    ],
    "bundle checkout": [
        {
            "field": "issue_type",
            "question": "Bundle checkout ma kya issue che?",
            "options": [
                "Payment fail",
                "Cart issue",
                "Product not found",
                "Order not placed",
            ],
        }
    ],
    "lab-grown": [
        {
            "field": "issue_type",
            "question": "Lab-grown section ma kya issue che?",
            "options": [
                "Products nathi dikhta",
                "Filter issue",
                "Pagination issue",
                "Display issue",
            ],
        }
    ],
    "natural diamond": [
        {
            "field": "issue_type",
            "question": "Natural diamond section ma kya issue che?",
            "options": [
                "Products nathi dikhta",
                "Filter issue",
                "Pagination issue",
                "Display issue",
            ],
        }
    ],
    "cart": [
        {
            "field": "issue_type",
            "question": "Cart ma kya issue che?",
            "options": [
                "Add to cart fail",
                "Product not found",
                "Quantity issue",
                "Cart empty thay che",
            ],
        }
    ],
    "checkout": [
        {
            "field": "issue_type",
            "question": "Checkout ma kya issue che?",
            "options": [
                "Payment fail",
                "Order not placed",
                "Product data missing",
                "Session issue",
            ],
        }
    ],
    "product attributes": [
        {
            "field": "issue_type",
            "question": "Product attributes ma kya issue che?",
            "options": [
                "Attributes nathi dikhta",
                "Wrong attribute value",
                "Variation missing",
                "Filter ma nathi aavta",
            ],
        }
    ],
    "general": [
        {
            "field": "issue_type",
            "question": "Kya type no issue che?",
            "options": [
                "Plugin activation issue",
                "Fatal error",
                "Display issue",
                "Functionality issue",
            ],
        }
    ],
}


# ─────────────────────────────────────────────────
# WRAPPER AGENT
# ─────────────────────────────────────────────────


class WrapperAgent:
    def __init__(self):
        print(f"{Fore.CYAN}🚀 Initializing BMAD PM Agent...{Style.RESET_ALL}")
        self.bmad = BMADPMAgent()

        self.modules = [
            "double pagination",
            "ring builder",
            "ring building",
            "lab-grown",
            "lab grown diamond",
            "lab grown",
            "natural diamond",
            "bundle checkout",
            "product attributes",
            "add to cart",
            "sp_extensions",
            "bootstrap",
            "extension",
            "filter",
            "pagination",
            "paginator",
            "bundle",
            "checkout",
            "payment",
            "cart",
            "setting select",
            "diamond category",
            "url structure",
            "eo_wbc",
            "variation",
            "natural",
            "ring",
        ]

        # ── SINGLE SOURCE OF TRUTH: Direct issue keywords ──
        # Keywords that indicate a short, direct issue requiring minimal clarification
        self.direct_issue_keywords = [
            # Critical errors
            "fatal", "fatal error", "class not found", "sp_extensions_bootstrap",
            "sp_extensions", "not found error", "critical error", "white screen",
            "500 error", "activation error", "plugin conflict", "bootstrap error",
            "error aave che", "error ave che", "kaam nathi karto", "not working",
            "broken", "php error", "syntax error", "parse error", "memory exhausted",
            "timeout", "undefined index", "undefined variable", "call to undefined",
            # Specific problems (2-3 word patterns)
            "pagination issue", "filter issue", "checkout error", "cart empty",
            "product missing", "redirect not working", "url issue",
            "configuration error", "settings not saving", "validation fail",
            "session issue", "database error", "database connection", "memory limit",
            # Direct "module + issue" patterns
            "ring builder issue", "ring building issue",
            "lab grown issue", "natural diamond issue",
            "bundle checkout issue", "product attribute issue",
        ]

        # Direct passthrough uses the same consolidated keyword list
        # (alias removed — use direct_issue_keywords directly)
        self.direct_passthrough_keywords = self.direct_issue_keywords

        # ── Semantic bypass: txtai embeddings ──
        # Initialize txtai for semantic similarity checks
        try:
            from txtai import Embeddings
            self.txtai_instance = Embeddings({"path": "sentence-transformers/all-MiniLM-L6-v2"})
            # Exemplars for direct issues — update as needed
            direct_exemplars = [
                "fatal error", "critical error", "white screen",
                "500 error", "pagination issue", "checkout error",
                "filter issue", "payment failed", "add to cart broken"
            ]
            self.txtai_instance.index([(text, text, None) for text in direct_exemplars])
        except ImportError:
            self.txtai_instance = None
            print(f"{Fore.YELLOW}⚠️ txtai not available, semantic bypass disabled{Style.RESET_ALL}")

        self.howto_keywords = [
            "kevi rite",
            "kevi rite javaay",
            "process shu che",
            "flow shu che",
            "steps shu che",
            "kevi rite kaam kare",
            "how does",
            "how to",
            "thashe ke",
            "reflect thashe ke",
            "support kare che ke",
            "possible che ke",
            "javaay",
            "navigate",
            "redirect",
            "kevi rite karvaay",
        ]

        self.project_keywords = [
            "ring",
            "builder",
            "diamond",
            "filter",
            "bundle",
            "checkout",
            "pagination",
            "lab",
            "product",
            "attribute",
            "woo",
            "plugin",
            "kaam",
            "error",
            "issue",
            "problem",
            "nathi",
            "fail",
            "not working",
            "working",
            "broken",
            "demo",
            "payment",
            "cart",
            "order",
            "scroll",
            "load",
            "display",
            "show",
            "hide",
            "click",
            "button",
            "url",
            "eo_wbc",
            "step",
            "flow",
            "setting",
            "select",
            "category",
            "variation",
            "validate",
            "session",
            "redirect",
            "navigate",
            "javaay",
            "thashe",
            "karvaay",
            "process",
            "fatal",
            "bootstrap",
            "extension",
            "class",
            "debug",
            "stack",
            "ftp",
            "git",
            "upload",
            "activate",
            "shop",
            "page",
            "admin",
            "panel",
            "functionality",
            "double",
            "single",
            "wrong",
            "slow",
            "missing",
            "empty",
            "found",
            "activation",
            "variation",
            "display",
            "ajax",
            "reload",
            "shortcode",
            "shortflt",
        ]

        self.bypass_keywords = [
            "hello",
            "hi",
            "thanks",
            "bye",
            "thank you",
        ]

        self.negative_feedback_keywords = [
            "too short",
            "too long",
            "need more",
            "need detail",
            "wrong",
            "incorrect",
            "bad answer",
            "generic",
            "hindi aavyu",
            "hindi avyu",
            "hindi",
            "format wrong",
            "galat",
            "nahi joitu",
            "improve",
            "saru nathi",
            "incomplete",
            "specific nathi",
            "vague",
            "chhe aavyu",
            "wrong format",
            "urgency wrong",
            "extra section",
            "next time",
            "include specific",
            "should include",
            "navigation path",
            "ui path",
            "logically",
            "improve karvo",
            "better answer",
            "add more",
            "missing info",
            "not mentioned",
            "should have",
            "aavu joitu",
            "mention nathi",
            # New — detailed feedback
            "score:",
            "score :",
            "logic for",
            "action plan",
            "too general",
            "too basic",
            "you missed",
            "you failed",
            "you are still",
            "stop suggesting",
            "must suggest",
            "must be",
            "priority must",
            "always check",
            "always suggest",
            "first recommendation",
            "revert",
            "backup restore",
            "json key",
            "mismatch",
            "php memory",
            "action scheduler",
            "cron job",
            "cat_link",
            "taxonomy",
            "advadd_info",
            "file path",
            "instead of",
            "correct the",
            "excellent work",
            "while you",
            "however",
            "also,",
            "also please",
            "in future",
            "in the future",
            "next time always",
            "ensure that",
            "most importantly",
            "for site crashes",
            "for fatal errors",
            "our company workflow",
        ]
        self.ctx = ConversationContext()
        self.memory = MemoryManager()

        self.last_answer = None
        self.last_module = None
        self.last_query = None
        self.initial_mode_selected = False
        self.initial_mode = None

        print(f"{Fore.GREEN}✅ Agent Ready{Style.RESET_ALL}\n")

    # ─────────────────────────────────────────

    def is_bypass(self, query):
        q = query.lower().strip()

        if self.ctx.pending_field:
            return False
        if self.ctx.raw_query:
            return False
        if q.isdigit():
            return False

        if len(q.split()) <= 2:
            for k in self.project_keywords:
                if k in q:
                    return False
            for k in self.bypass_keywords:
                if k in q:
                    return True
            return False

        for k in self.project_keywords:
            if k in q:
                return False
        for k in self.bypass_keywords:
            if k in q:
                return True

        return False

    def is_semantic_direct_passthrough(self, query: str) -> bool:
        """Check if query semantically matches direct issue patterns using txtai embeddings"""
        if not hasattr(self, 'txtai_instance') or not self.txtai_instance:
            return False

        # Check if query is very short (to maintain performance)
        if len(query.strip().split()) > 4:
            return False

        # Get similarity score against exemplars
        try:
            results = self.txtai_instance.search(query, 1)
            if results and results[0][1] > 0.82:  # Similarity threshold (safer value)
                return True
        except:
            pass
        return False

    def is_direct_passthrough(self, query: str) -> bool:
        """
        Direct Passthrough Check — Kept for backward compatibility

        Condition:
        - Query is very short (2-4 words)
        - Contains predefined direct issue keywords
        - Should bypass wrapper clarification/agent prompt
        - Direct to BMAD PM Agent

        Examples:
        "fatal error", "pagination issue", "checkout bug"
        "ring builder issue", "white screen", "500 error"
        """
        # First try semantic check
        if self.is_semantic_direct_passthrough(query):
            return True

        # Fallback to keyword check
        q = query.lower().strip()
        word_count = len(q.split())

        # Very short queries only (2-4 words)
        if word_count > 4:
            return False

        # Check for direct issue keywords/phrases
        for keyword in self.direct_issue_keywords:
            if keyword in q:
                return True

        # Check if starts with module name + direct issue word
        direct_issue_words = ["issue", "error", "bug", "problem", "fail", "broken"]
        for module in self.modules:
            if q.startswith(module.lower()) and any(word in q for word in direct_issue_words):
                return True

        return False

    def is_howto_query(self, query):
        q = query.lower().strip()
        for k in self.howto_keywords:
            if k in q:
                return True
        return False

    def detect_module(self, query):
        q = query.lower().strip()
        for m in self.modules:
            if m.lower() in q:
                return m
        return None

    # ─────────────────────────────────────────
    # SELF-IMPROVEMENT
    # ─────────────────────────────────────────

    def is_negative_feedback(self, query) -> bool:
        q = query.lower().strip()
        for k in self.negative_feedback_keywords:
            if k in q:
                return True
        return False

    def handle_feedback(self, user_feedback: str):
        if self.last_query and self.last_module:
            self.memory.auto_save_lesson_from_feedback(
                module=self.last_module,
                query=self.last_query,
                feedback=user_feedback,
                agent_answer=self.last_answer or "",
            )
            print(
                f"\n{Fore.GREEN}📚 Feedback noted — "
                f"Re-analyzing with feedback...{Style.RESET_ALL}"
            )

            # Re-run analysis with feedback context
            self.ctx.raw_query = self.last_query
            self.ctx.module = self.last_module
            self.ctx.query_type = "issue"
            self.ctx.issue_type = "feedback_correction"

            # Get stored memory context with feedback
            from rag_system.memory_manager import MemoryManager

            memory = MemoryManager()
            memory_context = memory.read_all_context()

            # Rebuild query with feedback
            refined = {
                "bmad_query": f"{self.last_module}: {self.last_query} | Feedback: {user_feedback}",
                "rag_query": f"{self.last_module} {self.last_query} fix: {user_feedback}",
                "original": self.last_query,
            }

            # Run analysis again with feedback
            # FIX: Force troubleshooting intent for feedback re-analysis
            self._run_analysis(refined, self.last_module, "issue", "troubleshooting")

        else:
            print(f"\n{Fore.YELLOW}⚠️ No previous answer to improve.{Style.RESET_ALL}\n")

    # ─────────────────────────────────────────
    # CLARIFICATION
    # ─────────────────────────────────────────

    def _get_clarification_questions(self, module: str) -> list:
        if module in CLARIFICATION_FLOW:
            return CLARIFICATION_FLOW[module]
        for key in CLARIFICATION_FLOW:
            if key in module or module in key:
                return CLARIFICATION_FLOW[key]
        return CLARIFICATION_FLOW.get("general", [])

    def _ask_next_clarification(self) -> bool:
        questions = self._get_clarification_questions(self.ctx.module or "general")
        for q in questions:
            field = q["field"]
            if getattr(self.ctx, field, None) is None:
                self.ctx.pending_field = field
                print(f"\n{Fore.YELLOW}🤖 {q['question']}{Style.RESET_ALL}")
                for i, opt in enumerate(q["options"], 1):
                    print(f"   {i}. {opt}")
                print(f"\n   {Fore.WHITE}(Number ya text type karo){Style.RESET_ALL}\n")
                return True
        return False

    def _fill_clarification(self, user_input: str):
        if not self.ctx.pending_field:
            return

        field = self.ctx.pending_field
        questions = self._get_clarification_questions(self.ctx.module or "general")

        current_q = None
        for q in questions:
            if q["field"] == field:
                current_q = q
                break

        if not current_q:
            setattr(self.ctx, field, user_input)
            self.ctx.pending_field = None
            return

        options = current_q["options"]
        try:
            idx = int(user_input.strip()) - 1
            if 0 <= idx < len(options):
                value = options[idx]
            else:
                value = user_input
        except ValueError:
            value = user_input

        setattr(self.ctx, field, value)
        self.ctx.pending_field = None

        print(f"{Fore.GREEN}✅ {field}: {value}{Style.RESET_ALL}")

    def ask_mode_selection(self):
        print(f"\n{Fore.YELLOW}🤖 What type of help do you need?{Style.RESET_ALL}")
        print(f"   1. Source Code Analysis (detailed fix)")
        print(f"   2. Quick Guidance (short answer)")
        print(f"   3. Faster Response (txtai retrieval)")
        print(f"\n   (Type 1, 2 or 3){Style.RESET_ALL}\n")

    def ask_module_confirmation(self):
        print(
            f"\n{Fore.YELLOW}🤖 Which module is this issue related to?{Style.RESET_ALL}"
        )
        unique = [
            "ring builder",
            "lab-grown",
            "natural diamond",
            "filter",
            "pagination",
            "bundle checkout",
            "product attributes",
            "checkout",
            "payment",
        ]
        for i, m in enumerate(unique, 1):
            print(f"   {i}. {m}")
        print(f"\n   (Module name type karo)\n")

    # ─────────────────────────────────────────
    # ANALYSIS RUNNER
    # ─────────────────────────────────────────

    def _run_analysis(
        self, refined: dict, module: str, query_type: str, query_intent: str = None
    ):
        # NEW: Get intent from context
        if query_intent is None:
            query_intent = getattr(self.ctx, "query_intent", None) or "troubleshooting"

        self.memory.save_task(module, self.ctx.issue_type or query_type, "IN_PROGRESS")

        # Different message based on intent
        if query_intent == "guidance":
            print(f"{Fore.CYAN}📖 Fetching quick guidance...{Style.RESET_ALL}\n")
        else:
            print(
                f"{Fore.CYAN}🔍 Scanning source code "
                f"+ documentation..."
                f"{Style.RESET_ALL}\n"
            )

        result = self.bmad.analyze_issue(
            bmad_query=refined["bmad_query"],
            rag_query=refined["rag_query"],
            original_query=refined["original"],
            module=module,
            query_type=query_type,
            query_intent=query_intent,
        )

        print(
            f"\n{Fore.GREEN}{'─' * 55}\n"
            f"📋 BMAD PM ANALYSIS\n"
            f"{'─' * 55}{Style.RESET_ALL}"
        )
        print(result)
        print(f"{Fore.GREEN}{'─' * 55}{Style.RESET_ALL}\n")

        self.memory.save_progress(refined["original"], result[:300])
        self.memory.update_task_status(module, "DONE")

        self.last_answer = result
        self.last_module = module
        self.last_query = refined["original"]

        print(
            f"{Fore.WHITE}💡 Answer helpful hatu? "
            f"Feedback aapvo to system improve thashe."
            f"\n   (Next query type karo, ya "
            f"'wrong/hindi aavyu/generic' type karo)"
            f"{Style.RESET_ALL}\n"
        )

    # ─────────────────────────────────────────
    # MAIN CHAT LOOP
    # ─────────────────────────────────────────

    def chat(self):
        print(f"{Fore.CYAN}{'=' * 55}")
        print("   BMAD PM Agent — BUNDLOICE Support")
        print(f"{'=' * 55}{Style.RESET_ALL}")

        # STEP 0: Ask mode selection ONCE at start
        if not self.initial_mode_selected:
            self.ask_mode_selection()
            while True:
                print(f"{Fore.BLUE}💬 You:{Style.RESET_ALL} ", end="")
                user_input = input().strip()

                if user_input in ["1", "2", "3"]:
                    if user_input == "1":
                        self.initial_mode = "source_code"
                    elif user_input == "2":
                        self.initial_mode = "guidance"
                    else:
                        self.initial_mode = "faster"
                    self.initial_mode_selected = True
                    print(
                        f"\n{Fore.GREEN}✅ Mode set: {self.initial_mode}{Style.RESET_ALL}\n"
                    )
                    break
                else:
                    print(f"{Fore.YELLOW}⚠️ Please type 1, 2 or 3{Style.RESET_ALL}\n")

        print(f"{Fore.WHITE}Type 'exit' to quit\n")

        while True:
            print(f"{Fore.BLUE}💬 You:{Style.RESET_ALL} ", end="")
            user_input = input().strip()

            if not user_input:
                continue

            if user_input.lower() in ["exit", "quit"]:
                self.memory.clear_session()
                print(f"\n{Fore.YELLOW}👋 Agent offline{Style.RESET_ALL}")
                break

            # STEP 1: Self-improvement feedback
            # Reddit: "After correction update lessons"
            if self.is_negative_feedback(user_input):
                self.handle_feedback(user_input)
                continue

            # ── NEW: Direct Passthrough Bypass ──
            # Very short query + direct issue keywords → BMAD PM Agent direct (wrapper prompt bypass)
            # Task requirement: "wrapper agent prompt bypass kari devano, directly system pase java devano"
            if self.is_direct_passthrough(user_input):
                print(f"\n{Fore.YELLOW}⚡ Direct issue detected — Bypassing wrapper → BMAD PM Agent{Style.RESET_ALL}\n")

                # Auto-detect module if not in context
                if not self.ctx.module:
                    detected = self.detect_module(user_input)
                    if detected:
                        self.ctx.module = detected
                    else:
                        # ── Better fallback: infer module via subprocess ──
                        # Call bmad_integration in special mode to get module inference
                        try:
                            self.ctx.module = "general"
                        except Exception:
                            self.ctx.module = "general"

                # Build queries for BMAD (minimal processing)
                direct_bmad_query = user_input
                direct_rag_query = user_input

                # ── FULL BMAD CHAIN via single orchestrator entrypoint ──
                # Use BMAD's public analyze_issue() method (all-in-one orchestrator)
                final_answer = self.bmad.analyze_issue(
                    bmad_query=direct_bmad_query,
                    rag_query=direct_rag_query,
                    original_query=user_input,
                    module=self.ctx.module,
                    query_type="issue",
                    query_intent="troubleshooting",
                )

                # Output
                print(
                    f"\n{Fore.GREEN}{'─' * 55}\n"
                    f"📋 DIRECT BMAD ANSWER (Passthrough)\n"
                    f"{'─' * 55}{Style.RESET_ALL}"
                )
                print(final_answer)
                print(f"{Fore.GREEN}{'─' * 55}{Style.RESET_ALL}\n")

                # Save to memory
                self.memory.save_progress(user_input, final_answer[:300])
                self.memory.update_task_status(self.ctx.module, "DONE")

                self.last_answer = final_answer
                self.last_module = self.ctx.module
                self.last_query = user_input
                self.ctx.reset()

                print(
                    f"{Fore.WHITE}💡 Answer helpful hatu? "
                    f"Feedback aapvo to system improve thashe."
                    f"\n   (Next query type karo, ya "
                    f"'wrong/hindi aavyu/generic' type karo)"
                    f"{Style.RESET_ALL}\n"
                )
                continue

            # STEP 2: Bypass check — PACHHI
            if self.is_bypass(user_input):
                print(
                    f"\n{Fore.WHITE}⚡ How can I help "
                    f"with your WooCommerce issue?"
                    f"{Style.RESET_ALL}\n"
                )
                continue

            # STEP 3: Clarification pending
            if self.ctx.pending_field:
                self._fill_clarification(user_input)

                if self.ctx.is_complete():
                    has_more = self._ask_next_clarification()
                    if not has_more:
                        refined = self.ctx.build_refined_query()
                        module = self.ctx.module
                        query_type = self.ctx.query_type
                        self._run_analysis(refined, module, query_type)
                        self.ctx.reset()
                else:
                    self._ask_next_clarification()
                continue

            # STEP 5: Module confirmation pending
            if self.ctx.raw_query and not self.ctx.module:
                detected = self.detect_module(user_input)
                self.ctx.module = detected or "general"
                print(f"\n{Fore.GREEN}✅ Module: {self.ctx.module}{Style.RESET_ALL}")
                self._ask_next_clarification()
                continue

            # STEP 6: New query - Use initial mode (no mode selection needed)
            # Process based on initial mode selection
            detected_module = self.detect_module(user_input)

            self.ctx.reset()
            self.ctx.raw_query = user_input
            self.ctx.query_type = (
                "howto" if self.is_howto_query(user_input) else "issue"
            )

            if detected_module:
                self.ctx.module = detected_module
                print(
                    f"\n{Fore.GREEN}✅ Module detected: {detected_module}{Style.RESET_ALL}"
                )
            else:
                self.ctx.module = "general"
                print(f"\n{Fore.GREEN}✅ Module: general{Style.RESET_ALL}")

            # Use the initial mode for processing
            if self.initial_mode == "guidance":
                query_type = "howto" if self.is_howto_query(user_input) else "guidance"

                # FIX: Detect intent using the guidance keywords
                self.ctx.query_intent = self.ctx.detect_intent(user_input)

                refined = {
                    "bmad_query": (
                        f"{self.ctx.module} best practice setup guide: {user_input}. Give short answer about recommended setting/choice."
                    ),
                    "rag_query": (
                        f"{self.ctx.module} documentation: {user_input}. Focus on recommended configuration for admin settings."
                    ),
                    "original": user_input,
                }
                self._run_analysis(refined, self.ctx.module, "guidance", "guidance")
            elif self.initial_mode == "faster":
                # Mode 3 — Faster response with auto-detection
                self.ctx.query_intent = "faster"

                # Auto-detect how-to vs issue from query
                if self.is_howto_query(user_input):
                    # How-To: skip clarifications, direct fast answer
                    print(f"\n{Fore.YELLOW}📖 How-To detected — skipping clarifications{Style.RESET_ALL}")
                    self.ctx.query_type = "howto"
                    refined = {
                        "bmad_query": f"{self.ctx.module} how-to flow process steps: {user_input}",
                        "rag_query": f"{self.ctx.module} documentation guide: {user_input}",
                        "original": user_input,
                    }
                    self._run_analysis(refined, self.ctx.module, "howto", "faster")
                    self.ctx.reset()
                else:
                    # Issue: need clarifications (issue type, location)
                    self.ctx.query_type = "issue"
                    has_more = self._ask_next_clarification()
                    if not has_more:
                        refined = self.ctx.build_refined_query()
                        self._run_analysis(refined, self.ctx.module, self.ctx.query_type, self.ctx.query_intent)
                        self.ctx.reset()
            else:
                # Mode 1 — Source Code Analysis (full BMAD chain)
                self._ask_next_clarification()


if __name__ == "__main__":
    agent = WrapperAgent()
    agent.chat()
