"""Offline contracts for the optional guide; never download or start training."""

import ast
from pathlib import Path
import re
import subprocess
import tomllib
import unittest


ROOT = Path(__file__).resolve().parents[1]
PAGES = [
    ROOT / "docs" / locale / "guide/velstand-v8.md"
    for locale in ("", "zh")
]
SOURCE_SHA = "b02fdea4902c2b93b7d34a83a6f05da4ececb7d3"
POLICY_SHA = "665ae4eb20bfe13bca1ef4ea6d4bb6b4a096e448"
WEIGHT_SHA256 = "2fc7f8ee6acd7d0d3f66a99927b5d5a56589aeed02ec714de329b252d5ccf492"


class VelStandV8DocsTests(unittest.TestCase):
    def test_translations_keep_commands_and_anchors_identical(self):
        texts = [path.read_text() for path in PAGES]
        blocks = [re.findall(r"```bash\n(.*?)\n```", text, re.S) for text in texts]
        self.assertEqual(len(blocks[0]), 8)
        self.assertEqual(blocks[0], blocks[1])
        anchors = [re.findall(r"\{#([\w-]+)\}", text) for text in texts]
        self.assertEqual(anchors[0], anchors[1])
        self.assertEqual(len(anchors[0]), 6)

    def test_examples_are_syntax_checked_without_running(self):
        for code in re.findall(r"```bash\n(.*?)\n```", PAGES[0].read_text(), re.S):
            result = subprocess.run(
                ["/bin/bash", "-n", "-c", code], capture_output=True, text=True
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            for python in re.findall(r"<<'PY'\n(.*?)\nPY", code, re.S):
                ast.parse(python)

    def test_pins_and_stage_inputs_are_explicit(self):
        for path in PAGES:
            text = path.read_text()
            for expected in (
                SOURCE_SHA, POLICY_SHA, WEIGHT_SHA256,
                "333ef7b03c0463bdebfcd6e2be0592de76c2bbcc",
                "3750776761ecfaa5671b36972087cafba45b8527",
                "model_1250.pt", "model_1750.pt", "model_9750.pt",
                "model_3750.pt", "reference/policies/v8/velstand.onnx",
                "reference/microduck_rl-v8",
                "env -u MICRODUCK_WARM_START uv run train",
            ):
                with self.subTest(page=path, expected=expected):
                    self.assertIn(expected, text)

    def test_local_links_resolve(self):
        for page in PAGES:
            text = page.read_text()
            for target in re.findall(r"\]\(([^)]+)\)", text):
                if "://" in target or target.startswith("#"):
                    continue
                target = target.split("#")[0]
                resolved = page.parent / target
                self.assertTrue(
                    resolved.is_file() or resolved.with_suffix(".md").is_file()
                    or (resolved / "index.md").is_file(),
                    f"{page}: {target}",
                )

    def test_default_lock_and_runtime_inputs_are_not_promoted(self):
        with (ROOT / "upstream.lock").open("rb") as stream:
            lock = tomllib.load(stream)
        self.assertEqual(lock["policies"]["version"], "v7")
        self.assertEqual(
            lock["policies"]["revision"],
            "6677ec007142bbaf05123a468f6ae58d13808786",
        )
        self.assertEqual(
            lock["microduck_rl"]["commit"],
            "ceca01706143d729305baa94cbd8ab990979e325",
        )
        self.assertEqual(
            lock["policies"]["files"]["velstand.onnx"],
            "ce894d30b3343036d499bfac1102bdaa58d59a21c1b58401ecb70fb6a2f63e0a",
        )
        for relative in (
            "scripts/fetch_upstream.sh",
            "scripts/run_isaac_playground.py",
            "scripts/run_isaac_policy.py",
            "scripts/run_mujoco_baseline.py",
        ):
            text = (ROOT / relative).read_text()
            self.assertNotIn("reference/policies/v8", text, relative)

    def test_no_commands_depend_on_unpublished_evaluators(self):
        for page in PAGES:
            text = page.read_text()
            self.assertIn("claude_experiments/velstand_rise_battery.py", text)
            for code in re.findall(r"```bash\n(.*?)\n```", text, re.S):
                self.assertNotIn("claude_experiments/", code)
                self.assertNotIn("git push", code)
                self.assertNotIn("uv run publish", code)


if __name__ == "__main__":
    unittest.main()
