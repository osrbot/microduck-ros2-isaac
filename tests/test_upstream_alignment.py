"""Offline safeguards for pinned policy downloads and model selection."""

import hashlib
import json
from pathlib import Path
import sys
import tempfile
import tomllib
import unittest
import re

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from fetch_policies import checked_filename, fetch_file
from generate_ros_description import upstream_sha


class PolicyDownloadTests(unittest.TestCase):
    def test_rejects_path_traversal(self):
        for name in ["../weights", "/etc/passwd", "a/b", "a\\b", ".", "..", "", ".hidden"]:
            with self.subTest(name=name), self.assertRaises(ValueError):
                checked_filename(name)
        self.assertEqual(checked_filename("velstand.onnx"), "velstand.onnx")

    def test_atomic_checked_download_and_idempotency(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source"
            source.write_bytes(b"policy-fixture")
            target = root / "set/policy.onnx"
            expected = hashlib.sha256(source.read_bytes()).hexdigest()
            self.assertTrue(fetch_file(source.as_uri(), target, expected))
            self.assertFalse(fetch_file("not-a-url", target, expected))
            self.assertEqual(target.read_bytes(), b"policy-fixture")
            self.assertEqual(list(target.parent.glob(".download-*")), [])

    def test_rejects_bad_download_without_install(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source"
            source.write_bytes(b"bad")
            target = root / "set/policy.onnx"
            with self.assertRaises(ValueError):
                fetch_file(source.as_uri(), target, "0" * 64)
            self.assertFalse(target.exists())
            self.assertEqual(list(target.parent.iterdir()), [])

    def test_preserves_existing_mismatched_file(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "policy.onnx"
            target.write_bytes(b"user-data")
            with self.assertRaises(ValueError):
                fetch_file("not-a-url", target, "0" * 64)
            self.assertEqual(target.read_bytes(), b"user-data")

    def test_new_lock_keeps_models_and_policies_separate(self):
        with (ROOT / "upstream.lock").open("rb") as stream:
            lock = tomllib.load(stream)
        self.assertEqual(lock["microduck_rl"]["model"], "robot_groundcontact.xml")
        self.assertEqual(lock["policies"]["version"], "v7")
        self.assertEqual(len(lock["policies"]["revision"]), 40)
        self.assertIn("velstand.onnx", lock["policies"]["files"])
        self.assertIn("manifest.json", lock["policies"]["files"])

    def test_historical_roulade_input_remains_identical(self):
        baseline = json.loads((ROOT / "artifacts/baseline/upstream_inventory.json").read_text())
        old = next(p for p in baseline["policies"] if p["path"].endswith("/roulade.onnx"))
        with (ROOT / "upstream.lock").open("rb") as stream:
            config = tomllib.load(stream)
        self.assertEqual(old["sha256"], config["policies"]["files"]["roulade.onnx"])

    def test_playground_preserves_every_historical_default_policy(self):
        baseline = json.loads((ROOT / "artifacts/baseline/upstream_inventory.json").read_text())
        old = {Path(p["path"]).name: p["sha256"] for p in baseline["policies"]}
        with (ROOT / "upstream.lock").open("rb") as stream:
            lock = tomllib.load(stream)
        self.assertEqual(lock["playground_sitstand"]["sha256"],
                         "c6c40e35e726eabd803d633e090d112994f469921152448367953fbaf9799bc8")
        self.assertEqual(lock["playground_sitstand"]["revision"],
                         "590b986bd8c0d50ae02cb3ea2f59c463b6828168")
        self.assertNotEqual(lock["playground_sitstand"]["sha256"], lock["policies"]["files"]["alpha_sitstand.onnx"])
        for name in ["alpha_walking.onnx", "alpha_stand.onnx", "alpha_ground_pick.onnx",
                     "ball_kick_left.onnx", "ball_kick_right.onnx", "roulade.onnx"]:
            with self.subTest(policy=name):
                self.assertEqual(lock["policies"]["files"][name], old[name])
        source = (ROOT / "scripts/run_isaac_playground.py").read_text()
        self.assertIn('DEFAULT_SITSTAND_POLICY = PROJECT_ROOT / "reference/policies/isaac-legacy/alpha_sitstand.onnx"', source)
        self.assertIn('"--sitstand-policy", type=Path, default=DEFAULT_SITSTAND_POLICY', source)

    def test_symlink_destination_is_never_followed(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "user-data"
            source.write_bytes(b"keep")
            target = root / "policy.onnx"
            target.symlink_to(source)
            expected = hashlib.sha256(source.read_bytes()).hexdigest()
            with self.assertRaises(ValueError):
                fetch_file("not-a-url", target, expected)
            self.assertEqual(source.read_bytes(), b"keep")

    def test_non_git_snapshot_does_not_borrow_parent_project_sha(self):
        self.assertEqual(upstream_sha(ROOT / "work/fixture-non-git/robot.xml"), "unknown")

    def test_conversion_keeps_historical_usd_separate(self):
        source = (ROOT / "scripts/convert_mjcf_to_usd.sh").read_text()
        self.assertIn('/microduck/robot_groundcontact.xml"', source)
        self.assertIn('canonical_dir="$project_dir/assets/isaac/robot_groundcontact"', source)
        self.assertNotIn('rm -rf -- "$canonical_dir"', source)

    def test_alignment_commands_match_in_both_languages(self):
        pages = [ROOT / "docs" / locale / "reference/upstream-alignment.md" for locale in ("", "zh")]
        blocks = [re.findall(r"```bash\n(.*?)\n```", p.read_text(), re.S) for p in pages]
        self.assertEqual(blocks[0], blocks[1])


if __name__ == "__main__":
    unittest.main()
