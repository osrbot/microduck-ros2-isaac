"""Behavioral acceptance tests: rocking, reset jumps and sideways motion fail."""

import importlib.util
import math
from pathlib import Path
import unittest

try:
    import torch
except ModuleNotFoundError as error:
    raise unittest.SkipTest("Roll tensor tests require the Isaac Python/Torch runtime") from error

MODULE = Path(__file__).resolve().parents[1] / "source/microduck_isaac_lab/microduck_isaac_lab/roll_metrics.py"
spec = importlib.util.spec_from_file_location("roll_metrics", MODULE)
roll_metrics = importlib.util.module_from_spec(spec)
spec.loader.exec_module(roll_metrics)


class RollMetricsTests(unittest.TestCase):
    def advance(self, counter, angles, sideways=0.0, reset=False):
        for angle in angles:
            norm = math.sqrt(1 - sideways**2)
            gravity = torch.tensor([[norm * math.sin(angle), sideways, -norm * math.cos(angle)]])
            counter.update(gravity, torch.tensor([reset]))
        return counter

    def test_three_forward_turns(self):
        counter = self.advance(roll_metrics.ForwardTurnCounter(1), torch.linspace(0, 6 * math.pi, 1000))
        self.assertEqual(counter.total_turns.item(), 3)
        self.assertEqual(counter.max_consecutive.item(), 3)

    def test_rocking_does_not_count(self):
        angles = [2.5 * math.sin(step * 0.03) for step in range(10000)]
        counter = self.advance(roll_metrics.ForwardTurnCounter(1), angles)
        self.assertEqual(counter.total_turns.item(), 0)

    def test_backward_turns_do_not_count(self):
        counter = self.advance(roll_metrics.ForwardTurnCounter(1), torch.linspace(0, -8 * math.pi, 1000))
        self.assertEqual(counter.total_turns.item(), 0)

    def test_reset_does_not_join_partial_turns(self):
        counter = roll_metrics.ForwardTurnCounter(1)
        for _ in range(10):
            self.advance(counter, [0], reset=True)
            self.advance(counter, torch.linspace(0, 1.9 * math.pi, 100))
        self.assertEqual(counter.total_turns.item(), 0)

    def test_sideways_rotation_does_not_count(self):
        counter = self.advance(roll_metrics.ForwardTurnCounter(1), torch.linspace(0, 10 * math.pi, 1000), sideways=0.8)
        self.assertEqual(counter.total_turns.item(), 0)

    def test_reverse_excursion_breaks_consecutive_chain(self):
        counter = roll_metrics.ForwardTurnCounter(1)
        self.advance(counter, torch.linspace(0, 2.2 * math.pi, 200))
        self.advance(counter, torch.linspace(2.2 * math.pi, 0.0, 200))
        self.advance(counter, torch.linspace(0, 2.2 * math.pi, 200))
        self.assertEqual(counter.max_consecutive.item(), 1)

    def test_independent_environments_and_resets(self):
        counter = roll_metrics.ForwardTurnCounter(2)
        for step in range(1001):
            angles = (step * 6 * math.pi / 1000, 2 * math.sin(step * 0.02))
            gravity = torch.tensor([[math.sin(angle), 0, -math.cos(angle)] for angle in angles])
            counter.update(gravity, torch.tensor([False, step % 80 == 0]))
        self.assertEqual(counter.total_turns.tolist(), [3, 0])
        self.assertEqual(counter.max_consecutive.tolist(), [3, 0])


if __name__ == "__main__":
    unittest.main()
