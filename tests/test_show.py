import io
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from agent_kit.cli import cmd_show
from agent_kit.store import build_candidate, import_candidates, suggest_asset_selectors


class ShowSelectorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmpdir = tempfile.TemporaryDirectory()
        self.store_root = Path(self.tmpdir.name) / "store"
        self.source_root = Path(self.tmpdir.name) / "source"
        self.source_root.mkdir(parents=True)

    def tearDown(self) -> None:
        self.tmpdir.cleanup()

    def test_cmd_show_uses_exact_match_before_fuzzy_suggestions(self) -> None:
        self._write_prompt("socratic.md", "# Socratic\n\nPrompt body.\n")
        self._import("socratic.md")

        stdout = io.StringIO()
        with redirect_stdout(stdout):
            result = cmd_show(self.store_root, "socratic", body_only=False)

        self.assertEqual(result, 0)
        self.assertIn("selector: prompt:socratic", stdout.getvalue())
        self.assertNotIn("Did you mean", stdout.getvalue())

    def test_cmd_show_reports_fuzzy_selector_suggestions(self) -> None:
        self._write_prompt("socratic.md", "# Socratic\n\nPrompt body.\n")
        self._write_prompt("doc-cleanup.md", "# Doc Cleanup\n\nPrompt body.\n")
        self._import("socratic.md")
        self._import("doc-cleanup.md")

        with self.assertRaises(FileNotFoundError) as exc_info:
            cmd_show(self.store_root, "socrat", body_only=False)

        self.assertEqual(
            str(exc_info.exception),
            "Asset not found: socrat. Did you mean: prompt:socratic",
        )

    def test_suggest_asset_selectors_returns_matching_selectors(self) -> None:
        self._write_prompt("doc-cleanup.md", "# Doc Cleanup\n\nPrompt body.\n")
        self._write_prompt("design-review.md", "# Design Review\n\nPrompt body.\n")
        self._import("doc-cleanup.md")
        self._import("design-review.md")

        self.assertEqual(
            suggest_asset_selectors(self.store_root, "doc clean"),
            ["prompt:doc-cleanup"],
        )

    def test_suggest_asset_selectors_returns_keyword_matches(self) -> None:
        self._write_prompt("star-batch-iterplan.md", "# STAR Batch Iterplan\n\nPrompt body.\n")
        self._write_prompt("batch-iterplan.md", "# Batch Iterplan\n\nPrompt body.\n")
        self._import("star-batch-iterplan.md")
        self._import("batch-iterplan.md")

        self.assertEqual(
            suggest_asset_selectors(self.store_root, "star"),
            ["prompt:star-batch-iterplan"],
        )

    def test_cmd_show_reports_keyword_match_suggestions(self) -> None:
        self._write_prompt("star-batch-iterplan.md", "# STAR Batch Iterplan\n\nPrompt body.\n")
        self._import("star-batch-iterplan.md")

        with self.assertRaises(FileNotFoundError) as exc_info:
            cmd_show(self.store_root, "star", body_only=False)

        self.assertEqual(
            str(exc_info.exception),
            "Asset not found: star. Did you mean: prompt:star-batch-iterplan",
        )

    def _write_prompt(self, name: str, content: str) -> None:
        (self.source_root / name).write_text(content, encoding="utf-8")

    def _import(self, name: str) -> None:
        candidate = build_candidate(self.source_root / name)
        import_candidates(self.store_root, [candidate])


if __name__ == "__main__":
    unittest.main()
