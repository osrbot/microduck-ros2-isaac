"""Offline checks for the optional Hub checkpoint guide; no GPU or downloads."""

import ast
import contextlib
import hashlib
import io
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import types
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
PAGES = [ROOT / "docs" / locale / "guide/training-checkpoints.md" for locale in ("", "zh")]
SOURCE = "bae39f5900b318f7e87fc485c30a31213cfa14eb"
REVISION = "64d28ce092253c509b51031ec7ccb53790a00d0d"
STUDENT_SHA = "2c185f1e6982a0a43d41403239bc0c5b0a9d654e4840d25572200c16abe2aa6b"
BUNDLES = (
    "velstand/0045i2si_2749",
    "microduck_stand/69u48n8l_9750",
    "velocity2/441tzs6d_3750",
)


def blocks(text, language="bash"):
    return re.findall(rf"```{language}\n(.*?)\n```", text, re.S)


class TrainingCheckpointDocsTests(unittest.TestCase):
    def test_translations_keep_commands_and_section_anchors_identical(self):
        en, zh = [page.read_text() for page in PAGES]
        self.assertEqual(len(blocks(en)), 5)
        self.assertEqual(blocks(en), blocks(zh))
        self.assertEqual(blocks(en, "python"), blocks(zh, "python"))
        self.assertEqual(re.findall(r"\{#([\w-]+)\}", en), re.findall(r"\{#([\w-]+)\}", zh))
        self.assertEqual(len(re.findall(r"\{#([\w-]+)\}", en)), 8)

    def test_command_syntax_without_running_training(self):
        for code in blocks(PAGES[0].read_text()):
            result = subprocess.run(["/bin/bash", "-n", "-c", code], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            for python in re.findall(r"<<'PY'\n(.*?)\nPY", code, re.S):
                ast.parse(python)

    def test_student_and_both_teachers_are_pinned(self):
        for page in PAGES:
            text = page.read_text()
            self.assertIn(f"git checkout --detach {SOURCE}", text)
            self.assertIn(STUDENT_SHA, text)
            for bundle in BUNDLES:
                self.assertIn(f"hf://pollen-robotics/microduck-training@{REVISION}/bundles/{bundle}", text)
            teacher_edit = blocks(text, "python")[0]
            self.assertIn('"wandb_run_path": None', teacher_edit)
            self.assertIn('"anchor_wandb_run_path": None', teacher_edit)

    def test_examples_do_not_publish_or_reset_the_curriculum(self):
        for page in PAGES:
            code = "\n".join(blocks(page.read_text()))
            for forbidden in ("git push", "git apply", "uv run publish", "uv run share-training",
                              "--hf-jobs", "--agent.resume", "--wandb-run-path", "MICRODUCK_WARM_START=1"):
                self.assertNotIn(forbidden, code)
            self.assertIn("env -u MICRODUCK_WARM_START", code)
            self.assertIn("--agent.logger tensorboard", code)
            self.assertIn("--agent.seed 20261030", code)
            self.assertIn("--agent.max-iterations 5", code)
            self.assertIn("--agent.save-interval 1", code)

    def test_limits_and_original_lineage_remain_visible(self):
        for page in PAGES:
            text = page.read_text()
            for expected in ("j4i6yoq2_1250", "qz5g3bwi_1750", "microduck_roulade/blrqbcit_750",
                             "3750776761ecfaa5671b36972087cafba45b8527", "uncommitted.diff",
                             "claude_experiments/velstand_rise_battery.py", "velstand_yaw_probe.py",
                             "export_dirty=true", "upstream.lock"):
                self.assertIn(expected, text)
            for code in blocks(text):
                self.assertNotIn("claude_experiments/", code)

    def test_navigation_and_links_resolve(self):
        config = (ROOT / "docs/.vitepress/config.mts").read_text()
        for locale in ("", "zh/"):
            self.assertIn(f"/{locale}guide/training-checkpoints", config)
            for relative in ("guide/velstand-v8.md", "isaac/training.md", "reference/upstream-alignment.md"):
                self.assertIn("guide/training-checkpoints" if not relative.startswith("guide/") else "./training-checkpoints",
                              (ROOT / "docs" / locale / relative).read_text())
        for page in PAGES:
            for target in re.findall(r"\]\(([^)]+)\)", page.read_text()):
                if "://" in target or target.startswith("#"):
                    continue
                resolved = page.parent / target.split("#")[0]
                self.assertTrue(resolved.is_file() or resolved.with_suffix(".md").is_file()
                                or (resolved / "index.md").is_file(), f"{page}: {target}")

    def run_download_example(self, corrupt_teacher=False):
        """Exercise the documentation's downloader against local fake Hub files."""
        text = PAGES[0].read_text()
        code = re.findall(r"<<'PY'\n(.*?)\nPY", "\n".join(blocks(text)), re.S)[0]
        payload = b"offline-documentation-fixture"
        fixture_sha = hashlib.sha256(payload).hexdigest()
        # The real student's pinned SHA cannot match a tiny fixture. Only substitute
        # that expected constant in this test, not in the tutorial itself.
        code = code.replace(STUDENT_SHA, fixture_sha)
        calls = []
        with tempfile.TemporaryDirectory(prefix="microduck-checkpoint-doc-test-") as directory:
            root = Path(directory)
            for bundle in BUNDLES:
                target = root / "bundles" / bundle
                target.mkdir(parents=True)
                metadata = {"id": bundle, "checkpoint_file": "model.pt",
                            "checkpoint_sha256": fixture_sha, "code": {"uncommitted_diff": None}}
                (target / "bundle.json").write_text(json.dumps(metadata))
                bad = corrupt_teacher and bundle == BUNDLES[1]
                (target / "model.pt").write_bytes(b"corrupted" if bad else payload)
                (target / "README.md").write_text("Fixture")
                (target / "wandb_config.yaml").write_text("{}")

            def fake_download(repo, filename, revision):
                self.assertEqual(repo, "pollen-robotics/microduck-training")
                self.assertEqual(revision, REVISION)
                calls.append(filename)
                return str(root / filename)

            hub = types.ModuleType("huggingface_hub")
            hub.hf_hub_download = fake_download
            stdout = io.StringIO()
            with patch.dict(sys.modules, {"huggingface_hub": hub}), contextlib.redirect_stdout(stdout):
                if corrupt_teacher:
                    with self.assertRaisesRegex(ValueError, "hash mismatch"):
                        exec(compile(code, "<documented-download-example>", "exec"), {})
                else:
                    exec(compile(code, "<documented-download-example>", "exec"), {})
            return stdout.getvalue(), calls

    def test_download_example_verifies_all_three_with_offline_fixtures(self):
        stdout, calls = self.run_download_example()
        self.assertEqual(stdout.count("verified "), 3)
        self.assertEqual(sum(name.endswith("model.pt") for name in calls), 3)

    def test_download_example_stops_on_teacher_hash_mismatch(self):
        stdout, calls = self.run_download_example(corrupt_teacher=True)
        self.assertEqual(stdout.count("verified "), 1)
        self.assertFalse(any(BUNDLES[2] in name for name in calls))


if __name__ == "__main__":
    unittest.main()
