# bmad_core/agent_loader.py

import os


class BMADAgentLoader:

    BMAD_AGENTS_PATH = "_bmad/core/agents"

    def __init__(self):
        self.agents = {}
        self._load_all_agents()

    def _load_all_agents(self):

        path = self.BMAD_AGENTS_PATH

        if not os.path.exists(path):
            print(f"⚠️ BMAD agents folder not found: {path}")
            return

        for filename in os.listdir(path):
            if filename.endswith(".md"):
                agent_name = filename.replace(".md", "")
                filepath = os.path.join(path, filename)

                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()

                self.agents[agent_name] = content
                print(f"✅ BMAD Agent loaded: {agent_name}")

    def get_agent_prompt(self, agent_name: str) -> str:

        if agent_name in self.agents:
            return self.agents[agent_name]

        if "woo-pm" in self.agents:
            return self.agents["woo-pm"]

        return "You are a helpful WooCommerce PM assistant."

    def list_agents(self):
        return list(self.agents.keys())