# wrapper_agent.py
# Custom Wrapper Agent — BMAD + RAG + Memory
# Self-Improvement Loop — Reddit workflow

import os
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

    def reset(self):
        self.__init__()

    def is_complete(self) -> bool:
        return (
            self.raw_query is not None and
            self.module is not None and
            self.issue_type is not None
        )

    def build_refined_query(self) -> dict:
        location_str = (
            f", Location: {self.location}"
            if self.location else ""
        )

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
            "original": self.raw_query
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
                "Checkout issue"
            ]
        },
        {
            "field": "location",
            "question": "Kyaa page par issue aave che?",
            "options": [
                "Shop page",
                "Product page",
                "Checkout page",
                "Admin panel"
            ]
        }
    ],
    "ring building": [
        {
            "field": "issue_type",
            "question": "Ring building process ma kya issue che?",
            "options": [
                "Setting select issue",
                "Diamond selection issue",
                "URL/redirect issue",
                "Checkout issue"
            ]
        }
    ],
    "double pagination": [
        {
            "field": "issue_type",
            "question": "Pagination issue kyaa tab par che?",
            "options": [
                "Diamond tab",
                "Lab-Grown tab",
                "Banne tabs",
                "Other tab"
            ]
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
                "AJAX reload issue"
            ]
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
                "Slow loading"
            ]
        },
        {
            "field": "location",
            "question": "Kyaa page par filter issue aave che?",
            "options": [
                "Category page",
                "Shop page",
                "Lab-grown page",
                "Natural diamond page"
            ]
        }
    ],
    "bundle checkout": [
        {
            "field": "issue_type",
            "question": "Bundle checkout ma kya issue che?",
            "options": [
                "Payment fail",
                "Cart issue",
                "Product not found",
                "Order not placed"
            ]
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
                "Display issue"
            ]
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
                "Display issue"
            ]
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
                "Cart empty thay che"
            ]
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
                "Session issue"
            ]
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
                "Filter ma nathi aavta"
            ]
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
                "Functionality issue"
            ]
        }
    ]
}


# ─────────────────────────────────────────────────
# WRAPPER AGENT
# ─────────────────────────────────────────────────

class WrapperAgent:

    def __init__(self):
        print(
            f"{Fore.CYAN}🚀 Initializing BMAD "
            f"PM Agent...{Style.RESET_ALL}"
        )
        self.bmad = BMADPMAgent()

        self.modules = [
            "double pagination",
            "ring builder",
            "ring building",
            "ring build",
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

        self.direct_issue_keywords = [
            "fatal", "fatal error",
            "class not found",
            "sp_extensions_bootstrap",
            "sp_extensions",
            "not found error",
            "critical error",
            "white screen",
            "500 error",
            "activation error",
            "plugin conflict",
            "bootstrap error",
            
        ]

        self.howto_keywords = [
            "kevi rite", "kevi rite javaay",
            "process shu che", "flow shu che",
            "steps shu che", "kevi rite kaam kare",
            "how does", "how to",
            "thashe ke", "reflect thashe ke",
            "support kare che ke",
            "possible che ke",
            "javaay", "navigate", "redirect",
            "kevi rite karvaay",
        ]

        self.project_keywords = [
            "ring", "builder", "diamond",
            "filter", "bundle", "checkout",
            "pagination", "lab", "product",
            "attribute", "woo", "plugin",
            "kaam", "error", "issue", "problem",
            "nathi", "fail", "not working",
            "working", "broken", "demo",
            "payment", "cart", "order",
            "scroll", "load", "display",
            "show", "hide", "click", "button",
            "url", "eo_wbc", "step", "flow",
            "setting", "select", "category",
            "variation", "validate", "session",
            "redirect", "navigate", "javaay",
            "thashe", "karvaay", "process",
            "fatal", "bootstrap", "extension",
            "class", "debug", "stack", "ftp",
            "git", "upload", "activate",
            "shop", "page", "admin", "panel",
            "functionality", "double", "single",
            "wrong", "slow", "missing", "empty",
            "found", "activation", "variation",
            "display", "ajax", "reload",
            "shortcode", "shortflt",
        ]

        self.bypass_keywords = [
            "hello", "hi", "thanks",
            "bye", "thank you",
        ]

        # ── FIX 1: Updated feedback keywords ──
        # "hindi avyu", "hindi aavyu" both add karya
        self.negative_feedback_keywords = [
            "wrong", "incorrect", "bad answer",
            "generic", "hindi aavyu", "hindi avyu",
            "hindi", "format wrong", "galat",
            "nahi joitu", "improve", "saru nathi",
            "incomplete", "specific nathi", "vague",
            "chhe aavyu", "wrong format",
            "urgency wrong", "extra section",
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

        print(
            f"{Fore.GREEN}✅ Agent Ready"
            f"{Style.RESET_ALL}\n"
        )

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

    def is_direct_issue(self, query):
        q = query.lower().strip()
        for k in self.direct_issue_keywords:
            if k in q:
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
                agent_answer=self.last_answer or ""
            )
            print(
                f"\n{Fore.GREEN}📚 Feedback noted — "
                f"System improved!"
                f"{Style.RESET_ALL}\n"
            )
        else:
            print(
                f"\n{Fore.YELLOW}⚠️ No previous "
                f"answer to improve."
                f"{Style.RESET_ALL}\n"
            )

    # ─────────────────────────────────────────
    # CLARIFICATION
    # ─────────────────────────────────────────

    def _get_clarification_questions(
        self, module: str
    ) -> list:
        if module in CLARIFICATION_FLOW:
            return CLARIFICATION_FLOW[module]
        for key in CLARIFICATION_FLOW:
            if key in module or module in key:
                return CLARIFICATION_FLOW[key]
        return CLARIFICATION_FLOW.get("general", [])

    def _ask_next_clarification(self) -> bool:
        questions = self._get_clarification_questions(
            self.ctx.module or "general"
        )
        for q in questions:
            field = q["field"]
            if getattr(self.ctx, field, None) is None:
                self.ctx.pending_field = field
                print(
                    f"\n{Fore.YELLOW}🤖 "
                    f"{q['question']}"
                    f"{Style.RESET_ALL}"
                )
                for i, opt in enumerate(
                    q["options"], 1
                ):
                    print(f"   {i}. {opt}")
                print(
                    f"\n   {Fore.WHITE}"
                    f"(Number ya text type karo)"
                    f"{Style.RESET_ALL}\n"
                )
                return True
        return False

    def _fill_clarification(
        self, user_input: str
    ):
        if not self.ctx.pending_field:
            return

        field = self.ctx.pending_field
        questions = self._get_clarification_questions(
            self.ctx.module or "general"
        )

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

        print(
            f"{Fore.GREEN}✅ {field}: "
            f"{value}{Style.RESET_ALL}"
        )

    def ask_module_confirmation(self):
        print(
            f"\n{Fore.YELLOW}🤖 Which module is "
            f"this issue related to?"
            f"{Style.RESET_ALL}"
        )
        unique = [
            "ring builder", "lab-grown",
            "natural diamond", "filter",
            "pagination", "bundle checkout",
            "product attributes", "checkout",
            "payment"
        ]
        for i, m in enumerate(unique, 1):
            print(f"   {i}. {m}")
        print(f"\n   (Module name type karo)\n")

    # ─────────────────────────────────────────
    # ANALYSIS RUNNER
    # ─────────────────────────────────────────

    def _run_analysis(
        self, refined: dict,
        module: str,
        query_type: str
    ):
        self.memory.save_task(
            module,
            self.ctx.issue_type or query_type,
            "IN_PROGRESS"
        )

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
            query_type=query_type
        )

        print(
            f"\n{Fore.GREEN}{'─'*55}\n"
            f"📋 BMAD PM ANALYSIS\n"
            f"{'─'*55}{Style.RESET_ALL}"
        )
        print(result)
        print(
            f"{Fore.GREEN}{'─'*55}"
            f"{Style.RESET_ALL}\n"
        )

        self.memory.save_progress(
            refined["original"],
            result[:300]
        )
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
        print(f"{Fore.CYAN}{'='*55}")
        print(
            "   BMAD PM Agent — "
            "WooCommerce Bundle Support"
        )
        print(f"{'='*55}{Style.RESET_ALL}")
        print(
            f"{Fore.WHITE}Type 'exit' to quit\n"
            f"{Style.RESET_ALL}"
        )

        while True:
            print(
                f"{Fore.BLUE}💬 You:{Style.RESET_ALL} ",
                end=""
            )
            user_input = input().strip()

            if not user_input:
                continue

            if user_input.lower() in ["exit", "quit"]:
                self.memory.clear_session()
                print(
                    f"\n{Fore.YELLOW}👋 Agent offline"
                    f"{Style.RESET_ALL}"
                )
                break

            # ── FIX 2: Feedback PEHLA check ──
            # STEP 1: Self-improvement feedback
            # Reddit: "After correction update lessons"
            if self.is_negative_feedback(user_input):
                self.handle_feedback(user_input)
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
                    has_more = \
                        self._ask_next_clarification()
                    if not has_more:
                        refined = \
                            self.ctx.build_refined_query()
                        module = self.ctx.module
                        query_type = self.ctx.query_type
                        self._run_analysis(
                            refined, module, query_type
                        )
                        self.ctx.reset()
                else:
                    self._ask_next_clarification()
                continue

            # STEP 4: Module confirmation pending
            if self.ctx.raw_query and \
                    not self.ctx.module:
                detected = self.detect_module(
                    user_input
                )
                self.ctx.module = detected or user_input
                print(
                    f"\n{Fore.GREEN}✅ Module: "
                    f"{self.ctx.module}"
                    f"{Style.RESET_ALL}"
                )
                self._ask_next_clarification()
                continue

            # STEP 5: New query
            query_type = "howto" \
                if self.is_howto_query(user_input) \
                else "issue"

            # Direct issue
            if self.is_direct_issue(user_input):
                print(
                    f"\n{Fore.YELLOW}⚡ Direct issue "
                    f"detected{Style.RESET_ALL}"
                )
                self.ctx.reset()
                self.ctx.raw_query = user_input
                self.ctx.module = "general"
                self.ctx.query_type = "issue"
                self.ctx.issue_type = "fatal error"
                refined = self.ctx.build_refined_query()
                self._run_analysis(
                    refined, "general", "issue"
                )
                self.ctx.reset()
                continue

            # How-to
            if query_type == "howto":
                detected = self.detect_module(
                    user_input
                )
                module = detected or "general"
                self.ctx.reset()
                self.ctx.raw_query = user_input
                self.ctx.module = module
                self.ctx.query_type = "howto"
                self.ctx.issue_type = "howto"
                refined = self.ctx.build_refined_query()
                self._run_analysis(
                    refined, module, "howto"
                )
                self.ctx.reset()
                continue

            # Normal issue
            self.ctx.reset()
            self.ctx.raw_query = user_input
            self.ctx.query_type = query_type
            detected = self.detect_module(user_input)

            if detected:
                self.ctx.module = detected
                print(
                    f"\n{Fore.GREEN}✅ Module detected:"
                    f" {detected}{Style.RESET_ALL}"
                )
                self._ask_next_clarification()
            else:
                self.ask_module_confirmation()


if __name__ == "__main__":
    agent = WrapperAgent()
    agent.chat()