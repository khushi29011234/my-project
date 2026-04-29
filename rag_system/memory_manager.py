# rag_system/memory_manager.py
# File-Based Memory System — Reddit workflow
# task_plan, findings, progress, lessons
# Self-Improvement Loop added

import os
import re
from datetime import datetime

MEMORY_DIR = "bmad_memory"

TASK_PLAN = os.path.join(MEMORY_DIR, "task_plan.md")
FINDINGS  = os.path.join(MEMORY_DIR, "findings.md")
PROGRESS  = os.path.join(MEMORY_DIR, "progress.md")
LESSONS   = os.path.join(MEMORY_DIR, "lessons.md")


class MemoryManager:
    """
    File-based memory — Reddit workflow

    task_plan.md = Current tasks + status
    findings.md  = RAG search findings
    progress.md  = Conversation history
    lessons.md   = Past mistakes + improvements
                   ← Self-improvement loop
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._ensure_files_exist()
        self._initialized = True
        print("✅ Memory Manager initialized")

    def _ensure_files_exist(self):
        os.makedirs(MEMORY_DIR, exist_ok=True)

        defaults = {
            TASK_PLAN: (
                "# Task Plan\n"
                "<!-- Current session tasks -->\n\n"
            ),
            FINDINGS: (
                "# RAG Findings\n"
                "<!-- Query findings store -->\n\n"
            ),
            PROGRESS: (
                "# Conversation Progress\n"
                "<!-- Conversation log -->\n\n"
            ),
            LESSONS: (
                "# Lessons Learned\n"
                "<!-- Self-improvement loop -->\n"
                "<!-- Format: [DATE] Module | "
                "Issue | Problem | Improvement -->\n\n"
            ),
        }

        for filepath, default_content in \
                defaults.items():
            if not os.path.exists(filepath):
                with open(
                    filepath, "w", encoding="utf-8"
                ) as f:
                    f.write(default_content)

    # ─────────────────────────────────────────
    # READ FUNCTIONS
    # ─────────────────────────────────────────

    def read_file(self, filepath: str) -> str:
        try:
            with open(
                filepath, "r", encoding="utf-8"
            ) as f:
                return f.read().strip()
        except Exception:
            return ""

    def read_task_plan(self) -> str:
        return self.read_file(TASK_PLAN)

    def read_findings(self) -> str:
        return self.read_file(FINDINGS)

    def read_progress(self) -> str:
        return self.read_file(PROGRESS)

    def read_lessons(self) -> str:
        return self.read_file(LESSONS)

    def read_all_context(self) -> str:
        """
        Badhi memory files ek saath read kare
        LLM ne full context aape
        Lessons FIRST — most important
        """
        lessons   = self.read_lessons()
        progress  = self.read_progress()
        task_plan = self.read_task_plan()

        # Recent progress — last 10 lines
        progress_lines = progress.split("\n")
        recent = "\n".join(
            progress_lines[-10:]
        ) if len(progress_lines) > 10 else progress

        # Recent lessons — last 5
        lesson_lines = [
            l for l in lessons.split("\n")
            if l.strip() and "<!--" not in l
            and "# Lessons" not in l
        ]
        recent_lessons = "\n".join(
            lesson_lines[-5:]
        ) if lesson_lines else ""

        context = ""

        if recent_lessons:
            context += (
                f"\n### Past Lessons — Apply These:\n"
                f"{recent_lessons}\n"
            )

        if recent and "<!-- " not in recent:
            context += (
                f"\n### Recent Conversation:\n"
                f"{recent}\n"
            )

        if task_plan and "<!-- " not in task_plan:
            context += (
                f"\n### Current Tasks:\n"
                f"{task_plan}\n"
            )

        return context.strip()

    # ─────────────────────────────────────────
    # WRITE FUNCTIONS
    # ─────────────────────────────────────────

    def _append_to_file(
        self, filepath: str, content: str
    ):
        try:
            with open(
                filepath, "a", encoding="utf-8"
            ) as f:
                f.write(content + "\n")
        except Exception as e:
            print(f"⚠️ Memory write failed: {e}")

    def save_task(
        self,
        module: str,
        issue_type: str,
        status: str = "IN_PROGRESS"
    ):
        timestamp = datetime.now().strftime(
            "%Y-%m-%d %H:%M"
        )
        entry = (
            f"[{status}] [{timestamp}] "
            f"Module: {module} | "
            f"Issue: {issue_type}"
        )
        self._append_to_file(TASK_PLAN, entry)

    def save_finding(
        self,
        query: str,
        finding_summary: str
    ):
        timestamp = datetime.now().strftime(
            "%Y-%m-%d %H:%M"
        )
        summary = finding_summary[:200].replace(
            "\n", " "
        )
        entry = (
            f"[{timestamp}] "
            f"Query: {query[:100]} | "
            f"Finding: {summary}"
        )
        self._append_to_file(FINDINGS, entry)

    def save_progress(
        self,
        user_query: str,
        agent_summary: str
    ):
        timestamp = datetime.now().strftime(
            "%Y-%m-%d %H:%M"
        )
        summary = agent_summary[:300].replace(
            "\n", " "
        )
        entry = (
            f"[{timestamp}] "
            f"User: {user_query[:100]} | "
            f"Agent: {summary}"
        )
        self._append_to_file(PROGRESS, entry)

    def save_lesson(
        self,
        module: str,
        issue: str,
        problem: str,
        improvement: str
    ):
        """
        Self-improvement loop — lesson save kare
        User feedback aave tyare call thay
        Next query ma automatically apply thashe
        """
        date = datetime.now().strftime("%Y-%m-%d")
        entry = (
            f"[{date}] "
            f"Module: {module} | "
            f"Issue: {issue[:80]} | "
            f"Problem: {problem[:150]} | "
            f"Improvement: {improvement[:300]}"
        )
        self._append_to_file(LESSONS, entry)
        print(
            f"📚 Lesson saved — "
            f"Next response improved thashe"
        )

    def auto_save_lesson_from_feedback(
        self,
        module: str,
        query: str,
        feedback: str,
        agent_answer: str
    ):
        """
        User feedback thi automatic lesson save kare
        Full feedback as lesson store kare — exact
        Generic improvement nahi — exact feedback
        """
        # Full feedback j lesson banavo
        improvement = feedback[:300]

        # Score extract karo jo hoy to
        score_match = re.search(
            r'score[:\s]+(\d+)',
            feedback.lower()
        )
        if score_match:
            score = score_match.group(1)
            issue = (
                f"Score {score}% — "
                f"{query[:80]}"
            )
        else:
            issue = query[:80]

        self.save_lesson(
            module=module,
            issue=issue,
            problem=feedback[:150],
            improvement=improvement
        )

    def update_task_status(
        self,
        module: str,
        status: str = "DONE"
    ):
        try:
            with open(
                TASK_PLAN, "r", encoding="utf-8"
            ) as f:
                lines = f.readlines()

            updated_lines = []
            for line in lines:
                # Check: line ma IN_PROGRESS che AND module name che
                if "[IN_PROGRESS]" in line and f"Module: {module}" in line:
                    line = line.replace("[IN_PROGRESS]", f"[{status}]", 1)
                updated_lines.append(line)

            with open(
                TASK_PLAN, "w", encoding="utf-8"
            ) as f:
                f.writelines(updated_lines)

        except Exception as e:
            print(f"⚠️ Task update failed: {e}")

    def clear_session(self):
        """
        Session end — task_plan clear
        Lessons + progress — rakho (history mate)
        """
        try:
            with open(
                TASK_PLAN, "w", encoding="utf-8"
            ) as f:
                f.write(
                    "# Task Plan\n"
                    "<!-- Current session tasks -->\n\n"
                )
        except Exception:
            pass