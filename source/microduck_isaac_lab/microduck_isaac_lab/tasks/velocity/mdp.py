"""MicroDuck-specific command, observation, reward, and curriculum terms."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import MISSING
import math

import torch

from isaaclab.assets import Articulation
from isaaclab.envs.mdp.commands import UniformVelocityCommand, UniformVelocityCommandCfg
from isaaclab.managers import CommandTerm, CommandTermCfg, SceneEntityCfg
from isaaclab.utils.configclass import configclass


def _single_body_scalar_values(env, sensor_names, field_name: str) -> torch.Tensor:
    """Stack one scalar column from each exact nested-body sensor."""

    values = []
    for sensor_name in sensor_names:
        sensor = env.scene.sensors[sensor_name]
        field = getattr(sensor.data, field_name).torch
        if field.ndim != 2 or field.shape[1] != 1:
            raise RuntimeError(
                f"{sensor_name} must expose one scalar body column, got {field.shape}"
            )
        values.append(field)
    return torch.cat(values, dim=1)


def _single_body_history_values(env, sensor_names, field_name: str) -> torch.Tensor:
    """Stack history vectors from exact nested-body sensors on the body axis."""

    values = []
    for sensor_name in sensor_names:
        sensor = env.scene.sensors[sensor_name]
        field = getattr(sensor.data, field_name).torch
        if field.ndim != 4 or field.shape[-2] != 1:
            raise RuntimeError(
                f"{sensor_name} must expose one history body column, got {field.shape}"
            )
        values.append(field)
    return torch.cat(values, dim=-2)


def split_feet_air_time_positive_biped(
    env,
    command_name: str,
    threshold: float,
    sensor_names: tuple[str, str],
) -> torch.Tensor:
    """Reward single-foot stance using two exact sensors on a nested USD rig."""

    air_time = _single_body_scalar_values(
        env, sensor_names, "current_air_time"
    )
    contact_time = _single_body_scalar_values(
        env, sensor_names, "current_contact_time"
    )
    in_contact = contact_time > 0.0
    in_mode_time = torch.where(in_contact, contact_time, air_time)
    single_stance = torch.sum(in_contact.int(), dim=1) == 1
    reward = torch.min(
        torch.where(single_stance.unsqueeze(-1), in_mode_time, 0.0), dim=1
    )[0]
    reward = torch.clamp(reward, max=threshold)
    moving = (
        torch.linalg.norm(env.command_manager.get_command(command_name)[:, :2], dim=1)
        > 0.1
    )
    return reward * moving


def split_feet_slide(
    env,
    sensor_names: tuple[str, str],
    asset_cfg: SceneEntityCfg,
) -> torch.Tensor:
    """Penalize planar foot speed while either exact foot sensor is loaded."""

    forces = _single_body_history_values(
        env, sensor_names, "net_forces_w_history"
    )
    contacts = forces.norm(dim=-1).max(dim=1)[0] > 1.0
    asset: Articulation = env.scene[asset_cfg.name]
    body_vel = asset.data.body_lin_vel_w.torch[:, asset_cfg.body_ids, :2]
    return torch.sum(body_vel.norm(dim=-1) * contacts, dim=1)


class TurnInPlaceVelocityCommand(UniformVelocityCommand):
    """Uniform velocity commands with an explicit turn-in-place bucket."""

    cfg: "TurnInPlaceVelocityCommandCfg"

    def _resample_command(self, env_ids: Sequence[int]) -> None:
        if isinstance(env_ids, slice):
            env_id_tensor = torch.arange(self.num_envs, device=self.device)[env_ids]
        else:
            env_id_tensor = torch.as_tensor(
                env_ids, dtype=torch.long, device=self.device
            )
        super()._resample_command(env_id_tensor)
        turn_mask = (
            torch.rand(len(env_id_tensor), device=self.device)
            < self.cfg.rel_turn_in_place_envs
        )
        turn_env_ids = env_id_tensor[turn_mask]
        if len(turn_env_ids) == 0:
            return
        yaw_magnitude = torch.empty(len(turn_env_ids), device=self.device).uniform_(
            *self.cfg.turn_in_place_yaw_range
        )
        yaw_sign = torch.where(
            torch.rand(len(turn_env_ids), device=self.device) < 0.5,
            -torch.ones_like(yaw_magnitude),
            torch.ones_like(yaw_magnitude),
        )
        self.vel_command_b[turn_env_ids, :2] = 0.0
        self.vel_command_b[turn_env_ids, 2] = yaw_sign * yaw_magnitude


@configclass
class TurnInPlaceVelocityCommandCfg(UniformVelocityCommandCfg):
    """Configuration for an explicit turn-in-place training bucket."""

    class_type: type[CommandTerm] = TurnInPlaceVelocityCommand
    rel_turn_in_place_envs: float = 0.15
    turn_in_place_yaw_range: tuple[float, float] = (0.4, 1.0)

    def __post_init__(self) -> None:
        if not 0.0 <= self.rel_turn_in_place_envs <= 1.0:
            raise ValueError("turn-in-place fraction must be between zero and one")
        lower, upper = self.turn_in_place_yaw_range
        if (
            not math.isfinite(lower)
            or not math.isfinite(upper)
            or lower < 0.0
            or lower > upper
        ):
            raise ValueError("turn-in-place yaw range must be non-negative and ordered")


class UniformVectorCommand(CommandTerm):
    """Uniformly sample an arbitrary command vector without scene coupling."""

    cfg: "UniformVectorCommandCfg"

    def __init__(self, cfg: "UniformVectorCommandCfg", env) -> None:
        super().__init__(cfg, env)
        self._command = torch.zeros(
            (self.num_envs, len(cfg.ranges)), dtype=torch.float32, device=self.device
        )

    @property
    def command(self) -> torch.Tensor:
        return self._command

    def _update_metrics(self) -> None:
        return None

    def _resample_command(self, env_ids: Sequence[int]) -> None:
        for index, (lower, upper) in enumerate(self.cfg.ranges):
            self._command[env_ids, index].uniform_(lower, upper)

    def _update_command(self) -> None:
        return None


@configclass
class UniformVectorCommandCfg(CommandTermCfg):
    """Configuration for :class:`UniformVectorCommand`."""

    class_type: type[CommandTerm] = UniformVectorCommand
    ranges: tuple[tuple[float, float], ...] = MISSING

    def __post_init__(self) -> None:
        if not self.ranges:
            raise ValueError("UniformVectorCommandCfg requires at least one range")
        for lower, upper in self.ranges:
            if not math.isfinite(lower) or not math.isfinite(upper) or lower > upper:
                raise ValueError(f"Invalid command range: {(lower, upper)}")


def head_pose_tracking(
    env,
    command_name: str,
    std: float,
    asset_cfg: SceneEntityCfg,
) -> torch.Tensor:
    """Track four commanded head-joint deltas from the configured home pose."""
    asset: Articulation = env.scene[asset_cfg.name]
    joint_pos = asset.data.joint_pos.torch[:, asset_cfg.joint_ids]
    default_pos = asset.data.default_joint_pos.torch[:, asset_cfg.joint_ids]
    target = default_pos + env.command_manager.get_command(command_name)
    squared_error = torch.square(joint_pos - target)
    return torch.mean(torch.exp(-squared_error / std**2), dim=1)


def joint_pose_tracking(
    env,
    std: float,
    asset_cfg: SceneEntityCfg,
) -> torch.Tensor:
    """Keep the compact biped near its stable home pose while a gait emerges."""
    asset: Articulation = env.scene[asset_cfg.name]
    joint_pos = asset.data.joint_pos.torch[:, asset_cfg.joint_ids]
    default_pos = asset.data.default_joint_pos.torch[:, asset_cfg.joint_ids]
    squared_error = torch.mean(torch.square(joint_pos - default_pos), dim=1)
    return torch.exp(-squared_error / std**2)


def set_vector_command_range_schedule(
    env,
    env_ids: Sequence[int],
    command_name: str,
    stages: tuple[tuple[int, tuple[tuple[float, float], ...]], ...],
) -> float:
    """Select and apply one command-range stage without repeated resampling."""
    if not stages:
        raise ValueError("command-range curriculum requires at least one stage")
    selected_ranges = stages[0][1]
    for step, ranges in stages:
        if env.common_step_counter >= step:
            selected_ranges = ranges
    term = env.command_manager.get_term(command_name)
    if tuple(term.cfg.ranges) != tuple(selected_ranges):
        term.cfg.ranges = tuple(selected_ranges)
        if isinstance(env_ids, slice):
            resample_ids = torch.arange(env.num_envs, device=env.device)
        else:
            resample_ids = torch.as_tensor(env_ids, device=env.device)
        term._resample_command(resample_ids)
    return float(max(abs(value) for item in term.cfg.ranges for value in item))


def set_reward_weight_schedule(
    env,
    env_ids: Sequence[int],
    term_name: str,
    stages: tuple[tuple[int, float], ...],
) -> float:
    """Apply one reward-weight stage at a time."""
    del env_ids
    if not stages:
        raise ValueError("reward-weight curriculum requires at least one stage")
    selected_weight = stages[0][1]
    for step, weight in stages:
        if env.common_step_counter >= step:
            selected_weight = weight
    term_cfg = env.reward_manager.get_term_cfg(term_name)
    if term_cfg.weight != selected_weight:
        term_cfg.weight = selected_weight
        env.reward_manager.set_term_cfg(term_name, term_cfg)
    return float(selected_weight)


def set_velocity_standing_fraction(
    env,
    env_ids: Sequence[int],
    command_name: str,
    stages: tuple[tuple[int, float], ...],
) -> float:
    """Increase the fraction of zero-velocity episodes after gait bootstrap."""
    del env_ids
    if not stages:
        raise ValueError("standing-fraction curriculum requires at least one stage")
    selected_fraction = stages[0][1]
    for step, fraction in stages:
        if env.common_step_counter >= step:
            selected_fraction = fraction
    if not 0.0 <= selected_fraction <= 1.0:
        raise ValueError("standing fraction must be between zero and one")
    term = env.command_manager.get_term(command_name)
    term.cfg.rel_standing_envs = selected_fraction
    return float(selected_fraction)
