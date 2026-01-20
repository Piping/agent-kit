import os
from typing import List

from .templates import get_slash_command_body, SKILL_TEMPLATES
from .types import ManagedFile


class ToolAdapter:
    tool_id = ""

    def command_files(self, project_root: str) -> List[ManagedFile]:
        return []

    def skill_files(self, project_root: str) -> List[ManagedFile]:
        return []

    def hook_files(self, project_root: str) -> List[ManagedFile]:
        return []


class OpenCodeAdapter(ToolAdapter):
    tool_id = "opencode"

    def command_files(self, project_root: str) -> List[ManagedFile]:
        files = []
        base_dir = os.path.join(project_root, ".opencode", "command")
        frontmatter = {
            "proposal": """---
description: Scaffold a new OpenSpec change and validate strictly.
---
The user has requested the following change proposal. Use the openspec instructions to create their change proposal.
<UserRequest>
  $ARGUMENTS
</UserRequest>
""",
            "apply": """---
description: Implement an approved OpenSpec change and keep tasks in sync.
---
The user has requested to implement the following change proposal. Find the change proposal and follow the instructions below. If you're not sure or if ambiguous, ask for clarification from the user.
<UserRequest>
  $ARGUMENTS
</UserRequest>
""",
            "archive": """---
description: Archive a deployed OpenSpec change and update specs.
---
<ChangeId>
  $ARGUMENTS
</ChangeId>
""",
        }

        for command_id in ("proposal", "apply", "archive"):
            path = os.path.join(base_dir, f"openspec-{command_id}.md")
            body = get_slash_command_body(command_id).strip()
            files.append(ManagedFile(path=path, body=body, frontmatter=frontmatter[command_id]))
        return files

    def hook_files(self, project_root: str) -> List[ManagedFile]:
        hook_path = os.path.join(project_root, ".opencode", "hooks.jsonc")
        body = """  \"experimental\": {\n    \"hook\": {\n      \"file_edited\": {},\n      \"session_completed\": []\n    }\n  }"""
        return [
            ManagedFile(
                path=hook_path,
                body=body,
                frontmatter="{",
                marker_prefix="  // ",
                suffix="}",
            )
        ]


class CodexAdapter(ToolAdapter):
    tool_id = "codex"

    def command_files(self, project_root: str) -> List[ManagedFile]:
        home = os.environ.get("CODEX_HOME")
        if home:
            home = home.strip()
        if not home:
            home = os.path.join(os.path.expanduser("~"), ".codex")
        prompts_dir = os.path.join(home, "prompts")
        files = []
        frontmatter = {
            "proposal": """---
description: Scaffold a new OpenSpec change and validate strictly.
argument-hint: request or feature description
---

$ARGUMENTS
""",
            "apply": """---
description: Implement an approved OpenSpec change and keep tasks in sync.
argument-hint: change-id
---

$ARGUMENTS
""",
            "archive": """---
description: Archive a deployed OpenSpec change and update specs.
argument-hint: change-id
---

$ARGUMENTS
""",
        }

        for command_id in ("proposal", "apply", "archive"):
            path = os.path.join(prompts_dir, f"openspec-{command_id}.md")
            body = get_slash_command_body(command_id).strip()
            files.append(ManagedFile(path=path, body=body, frontmatter=frontmatter[command_id]))
        return files


class AgentSkillsAdapter(ToolAdapter):
    tool_id = "claudecode"

    def skill_files(self, project_root: str) -> List[ManagedFile]:
        files = []
        base_dir = os.path.join(project_root, ".claude", "skills")
        for key, template in SKILL_TEMPLATES.items():
            skill_dir = os.path.join(base_dir, key)
            path = os.path.join(skill_dir, "SKILL.md")
            frontmatter = f"---\nname: {template.name}\ndescription: {template.description}\n---\n"
            files.append(ManagedFile(path=path, body=template.instructions.strip(), frontmatter=frontmatter))
        return files
