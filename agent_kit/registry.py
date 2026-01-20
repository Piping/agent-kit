from typing import Dict

from .adapters import AgentSkillsAdapter, CodexAdapter, OpenCodeAdapter, ToolAdapter


def build_registry() -> Dict[str, ToolAdapter]:
    adapters = [OpenCodeAdapter(), CodexAdapter(), AgentSkillsAdapter()]
    return {adapter.tool_id: adapter for adapter in adapters}
