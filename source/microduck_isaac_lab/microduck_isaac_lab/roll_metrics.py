"""Orientation-based roll accounting, independent of Isaac and reward scores.

The phase is atan2(gravity_body.x, -gravity_body.z). Unlike integrating only
positive angular velocity, forward/backward rocking cannot accumulate turns.
Resets and sideways singularities break the chain. A reverse excursion of
more than 90 degrees breaks consecutive-roll acceptance.
"""

import math

import torch


class ForwardTurnCounter:
    def __init__(self, num_envs, device="cpu"):
        self.phase = torch.zeros(num_envs, device=device)
        self.valid = torch.zeros(num_envs, dtype=torch.bool, device=device)
        self.net = torch.zeros_like(self.phase)
        self.peak = torch.zeros_like(self.phase)
        self.chain_start = torch.zeros_like(self.phase)
        self.chain_peak = torch.zeros_like(self.phase)
        self.max_consecutive = torch.zeros(num_envs, dtype=torch.long, device=device)
        self.total_turns = torch.zeros_like(self.max_consecutive)
        self.new_progress = torch.zeros_like(self.phase)
        self.new_turns = torch.zeros_like(self.max_consecutive)
        self.delta = torch.zeros_like(self.phase)

    def update(self, gravity_body, reset=None):
        phase = torch.atan2(gravity_body[:, 0], -gravity_body[:, 2])
        valid = torch.isfinite(gravity_body).all(dim=1) & (gravity_body[:, 1].abs() < 0.55)
        reset = torch.zeros_like(valid) if reset is None else reset.bool()
        wrapped = torch.remainder(phase - self.phase + math.pi, 2 * math.pi) - math.pi
        continuity = self.valid & valid & ~reset & (wrapped.abs() < 1.2)
        restart = ~continuity
        self.net[restart] = 0
        self.peak[restart] = 0
        self.chain_start[restart] = 0
        self.chain_peak[restart] = 0
        self.delta = torch.where(continuity, wrapped, 0.0)
        old_peak = self.peak.clone()
        self.net += self.delta
        self.peak = torch.maximum(self.peak, self.net)
        self.new_progress = self.peak - old_peak
        self.new_turns = (
            torch.floor((self.peak + 1e-5) / (2 * math.pi)).long()
            - torch.floor((old_peak + 1e-5) / (2 * math.pi)).long()
        )
        self.total_turns += self.new_turns
        self.chain_peak = torch.maximum(self.chain_peak, self.net)
        broken = (self.chain_peak - self.net) > math.pi / 2
        self.chain_start[broken] = self.net[broken]
        self.chain_peak[broken] = self.net[broken]
        consecutive = torch.floor(
            (self.chain_peak - self.chain_start + 1e-5) / (2 * math.pi)
        ).long()
        self.max_consecutive = torch.maximum(self.max_consecutive, consecutive)
        self.phase = phase
        self.valid = valid
        return self
