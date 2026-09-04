"""Read-only tutorial contracts; never start Isaac or training from a docs test."""

import ast
import json
import math
from pathlib import Path
import re
import shlex
import subprocess
import unittest


ROOT = Path(__file__).resolve().parents[1]
SLUGS = ("continuous-roll", "roll-parameters", "roll-debugging", "roll-validation")
PAGES = [ROOT / "docs" / locale / f"{slug}.md" for locale in ("zh/isaac", "isaac") for slug in SLUGS]
RESULT = ROOT / "docs/.vitepress/theme/roll-case.json"


def parser_options(filename):
    tree = ast.parse((ROOT / "scripts" / filename).read_text())
    return {
        arg.value
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "add_argument"
        for arg in node.args
        if isinstance(arg, ast.Constant)
        and isinstance(arg.value, str)
        and arg.value.startswith("--")
    }


class RollTutorialTests(unittest.TestCase):
    def test_video_precedes_setup_and_has_base_aware_controls(self):
        for directory in ("zh/isaac", "isaac"):
            source = (ROOT / "docs" / directory / "continuous-roll.md").read_text()
            self.assertLess(source.index("<RollShowcase />"), source.index("{#setup}"))
        component = (ROOT / "docs/.vitepress/theme/RollShowcase.vue").read_text()
        self.assertIn("controls", component)
        self.assertIn("playsinline", component)
        self.assertIn("withBase('/media/continuous-roll/", component)
        self.assertNotIn("autoplay", component)

    def test_sidebar_order_and_language_destinations(self):
        config = (ROOT / "docs/.vitepress/config.mts").read_text()
        for locale in ("zh/isaac", "isaac"):
            offsets = [config.index(f"'/{locale}/{slug}'") for slug in SLUGS]
            self.assertEqual(offsets, sorted(offsets))
            route = ("training",) + SLUGS + ("custom-environment",)
            for index, slug in enumerate(SLUGS):
                page = (ROOT / "docs" / locale / f"{slug}.md").read_text()
                frontmatter = page.split("---", 2)[1]
                self.assertIn("prev:", frontmatter)
                self.assertIn(f"link: /{locale}/{route[index]}\n", frontmatter)
                self.assertIn("next:", frontmatter)
                self.assertIn(f"link: /{locale}/{route[index + 2]}\n", frontmatter)

    def test_english_chapters_are_complete_and_localized(self):
        for slug in SLUGS:
            english = (ROOT / "docs/isaac" / f"{slug}.md").read_text()
            with self.subTest(page=slug):
                self.assertNotRegex(english, r"[\u4e00-\u9fff]")
                self.assertNotIn("../zh/", english)
                self.assertNotIn("will follow", english)
                self.assertGreaterEqual(english.count("\n## "), 6)
                self.assertGreater(len(english.split()), 900)
        for name in ("RollShowcase.vue", "RollPhaseChart.vue"):
            component = (ROOT / "docs/.vitepress/theme" / name).read_text()
            self.assertIn("useData()", component)
            self.assertIn("lang.value.startsWith('zh')", component)

    def test_bilingual_commands_match_except_translated_placeholders(self):
        replacements = {
            "替换为实际运行时间目录": "RUN_TIMESTAMP",
            "替换为本次roll-tutorial目录": "YOUR_ROLL_TUTORIAL_DIRECTORY",
            "本次目录：%s\\n总截止时间：%s\\n": "Experiment directory: %s\\nOverall deadline: %s\\n",
        }
        for slug in SLUGS:
            chinese = (ROOT / "docs/zh/isaac" / f"{slug}.md").read_text()
            english = (ROOT / "docs/isaac" / f"{slug}.md").read_text()
            for old, new in replacements.items():
                chinese = chinese.replace(old, new)
            with self.subTest(page=slug):
                self.assertEqual(
                    re.findall(r"```bash\n(.*?)\n```", chinese, re.S),
                    re.findall(r"```bash\n(.*?)\n```", english, re.S),
                )

    def test_all_bash_blocks_parse_without_executing(self):
        for page in PAGES:
            for index, block in enumerate(re.findall(r"```bash\n(.*?)\n```", page.read_text(), re.S)):
                with self.subTest(page=page.name, block=index):
                    result = subprocess.run(["bash", "-n"], input=block, text=True, capture_output=True)
                    self.assertEqual(result.returncode, 0, result.stderr)
                    for python_code in re.findall(r"<<'PY'\n(.*?)\nPY", block, re.S):
                        ast.parse(python_code)

    def test_documented_runner_flags_exist_and_runs_are_bounded(self):
        checked = 0
        for page in PAGES:
            for block in re.findall(r"```bash\n(.*?)\n```", page.read_text(), re.S):
                flattened = block.replace("\\\n", " ")
                for stem in ("train_isaac_velocity", "play_isaac_velocity"):
                    match = re.search(rf"bash scripts/{stem}\.sh([^\n]*)", flattened)
                    if match is None:
                        continue
                    checked += 1
                    flags = {t for t in shlex.split(match[1]) if t.startswith("--")}
                    self.assertFalse(flags - parser_options(stem + ".py") - {"--viz"})
                    self.assertIn("--full-roll-v2", flags)
                    self.assertIn("--profile continuous_roll", match[1])
                    self.assertIn(' --deadline "$roll_deadline"', flattened)
                    self.assertIn("--max-seconds", block)
                    if stem.startswith("train"):
                        self.assertIn("MICRODUCK_TRAIN_ITERATIONS=", block)
                    else:
                        self.assertTrue({"--checkpoint", "--policy-onnx"} & flags)
        self.assertGreaterEqual(checked, 14)

    def test_saved_metrics_and_phase_series_are_consistent(self):
        data = json.loads(RESULT.read_text())
        batch = data["batch"]
        self.assertEqual(batch["complete_turns_each"], [39] * 8)
        self.assertEqual(batch["consecutive_turns_each"], [39] * 8)
        self.assertEqual(batch["resets"], 0)
        self.assertEqual(batch["seed"], 109)
        mean_abs = sum(abs(x) for x in batch["lateralDisplacementM"]) / 8
        self.assertAlmostEqual(mean_abs, batch["mean_absolute_lateral_displacement_m"], places=5)
        self.assertAlmostEqual(data["video"]["maximum_full_turn_gap_seconds"], 1.42)
        phase = data["phaseFirstSixSeconds"]
        self.assertLess(max(y for _, y in phase["baseline"]), 1)
        self.assertGreater(phase["selected"][-1][1], 4)
        for name in ("baseline", "selected"):
            self.assertEqual(len(phase[name]), 60)
            self.assertTrue(all(math.isfinite(x) for pair in phase[name] for x in pair))

    def test_metrics_match_original_records_when_present(self):
        source = ROOT / "output/continuous-roll-training/roll120-20260904-073725/session-summary.json"
        if not source.exists():
            self.skipTest("Private local experiment archive is not distributed with docs")
        session = json.loads(source.read_text())
        data = json.loads(RESULT.read_text())
        self.assertEqual(data["checkpointSha256"], session["selected_checkpoint_sha256"])
        self.assertEqual(data["originalVideoSha256"], session["video_sha256"])
        self.assertEqual(data["video"], session["video_validation"])
        for key, value in session["batch_validation"].items():
            self.assertEqual(data["batch"][key], value)

    def test_public_content_omits_machine_addresses_and_paths(self):
        files = PAGES + [RESULT, ROOT / "docs/public/media/continuous-roll/README.md"]
        for path in files:
            text = path.read_text()
            with self.subTest(path=path.name):
                self.assertNotRegex(text, r"/Users/|/home/osrbot|192\.168\.|sshpass|osrbot@")

    def test_media_files_exist(self):
        for name in ("continuous-forward-roll.mp4", "first-rolls.mp4", "poster.jpg"):
            path = ROOT / "docs/public/media/continuous-roll" / name
            self.assertGreater(path.stat().st_size, 1000)


if __name__ == "__main__":
    unittest.main()
