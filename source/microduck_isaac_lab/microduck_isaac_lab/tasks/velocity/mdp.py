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


def split_feet_flight_time_biped(
    env,
    command_name: str,
    threshold: float,
    minimum_command_speed: float,
    sensor_names: tuple[str, str],
) -> torch.Tensor:
    """Reward short two-foot flight phases only for high-speed commands."""

    air_time = _single_body_scalar_values(
        env, sensor_names, "current_air_time"
    )
    contact_time = _single_body_scalar_values(
        env, sensor_names, "current_contact_time"
    )
    both_airborne = torch.sum(contact_time > 0.0, dim=1) == 0
    flight_time = torch.min(air_time, dim=1)[0].clamp(max=threshold)
    commanded_speed = torch.linalg.norm(
        env.command_manager.get_command(command_name)[:, :2], dim=1
    )
    sprinting = commanded_speed >= minimum_command_speed
    return flight_time * both_airborne * sprinting


class TurnInPlaceVelocityCommand(UniformVelocityCommand):
    """Uniform commands with explicit turn-in-place and sprint buckets."""

    cfg: "TurnInPlaceVelocityCommandCfg"

    def _resample_command(self, env_ids: Sequence[int]) -> None:
        if isinstance(env_ids, slice):
            env_id_tensor = torch.arange(self.num_envs, device=self.device)[env_ids]
        else:
            env_id_tensor = torch.as_tensor(
                env_ids, dtype=torch.long, device=self.device
            )
        super()._resample_command(env_id_tensor)
        bucket = torch.rand(len(env_id_tensor), device=self.device)
        turn_mask = bucket < self.cfg.rel_turn_in_place_envs
        sprint_mask = (
            bucket >= self.cfg.rel_turn_in_place_envs
        ) & (
            bucket
            < self.cfg.rel_turn_in_place_envs + self.cfg.rel_sprint_envs
        )
        turn_env_ids = env_id_tensor[turn_mask]
        if len(turn_env_ids) > 0:
            yaw_magnitude = torch.empty(
                len(turn_env_ids), device=self.device
            ).uniform_(*self.cfg.turn_in_place_yaw_range)
            yaw_sign = torch.where(
                torch.rand(len(turn_env_ids), device=self.device) < 0.5,
                -torch.ones_like(yaw_magnitude),
                torch.ones_like(yaw_magnitude),
            )
            self.vel_command_b[turn_env_ids, :2] = 0.0
            self.vel_command_b[turn_env_ids, 2] = yaw_sign * yaw_magnitude

        sprint_env_ids = env_id_tensor[sprint_mask]
        if len(sprint_env_ids) > 0:
            sprint_speed = torch.empty(
                len(sprint_env_ids), device=self.device
            ).uniform_(*self.cfg.sprint_speed_range)
            reverse = (
                torch.rand(len(sprint_env_ids), device=self.device)
                < self.cfg.sprint_reverse_fraction
            )
            sprint_sign = torch.where(
                reverse,
                -torch.ones_like(sprint_speed),
                torch.ones_like(sprint_speed),
            )
            self.vel_command_b[sprint_env_ids, 0] = sprint_sign * sprint_speed
            self.vel_command_b[sprint_env_ids, 1].uniform_(
                *self.cfg.sprint_lateral_range
            )
            self.vel_command_b[sprint_env_ids, 2].uniform_(
                *self.cfg.sprint_yaw_range
            )


@configclass
class TurnInPlaceVelocityCommandCfg(UniformVelocityCommandCfg):
    """Configuration for explicit turn-in-place and sprint training buckets."""

    class_type: type[CommandTerm] = TurnInPlaceVelocityCommand
    rel_turn_in_place_envs: float = 0.15
    turn_in_place_yaw_range: tuple[float, float] = (0.4, 1.0)
    rel_sprint_envs: float = 0.0
    sprint_speed_range: tuple[float, float] = (0.55, 0.85)
    sprint_lateral_range: tuple[float, float] = (-0.10, 0.10)
    sprint_yaw_range: tuple[float, float] = (-0.45, 0.45)
    sprint_reverse_fraction: float = 0.0

    def __post_init__(self) -> None:
        if not 0.0 <= self.rel_turn_in_place_envs <= 1.0:
            raise ValueError("turn-in-place fraction must be between zero and one")
        if not 0.0 <= self.rel_sprint_envs <= 1.0:
            raise ValueError("sprint fraction must be between zero and one")
        if self.rel_turn_in_place_envs + self.rel_sprint_envs > 1.0:
            raise ValueError("turn-in-place and sprint fractions must not exceed one")
        if not 0.0 <= self.sprint_reverse_fraction <= 1.0:
            raise ValueError("sprint reverse fraction must be between zero and one")
        lower, upper = self.turn_in_place_yaw_range
        if (
            not math.isfinite(lower)
            or not math.isfinite(upper)
            or lower < 0.0
            or lower > upper
        ):
            raise ValueError("turn-in-place yaw range must be non-negative and ordered")
        for name, value_range in (
            ("sprint speed", self.sprint_speed_range),
            ("sprint lateral", self.sprint_lateral_range),
            ("sprint yaw", self.sprint_yaw_range),
        ):
            lower, upper = value_range
            if (
                not math.isfinite(lower)
                or not math.isfinite(upper)
                or lower > upper
            ):
                raise ValueError(f"{name} range must be finite and ordered")
        if self.sprint_speed_range[0] < 0.0:
            raise ValueError("sprint speed range must be non-negative")


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


def forward_pitch_rate_progress(
    env,
    target_rate: float,
    asset_cfg: SceneEntityCfg,
) -> torch.Tensor:
    """Reward forward pitch accumulation while rejecting reverse rotation."""
    if target_rate <= 0.0:
        raise ValueError("target pitch rate must be positive")
    asset: Articulation = env.scene[asset_cfg.name]
    pitch_rate = asset.data.root_ang_vel_b.torch[:, 1]
    return torch.clamp(pitch_rate / target_rate, min=0.0, max=1.5)


def forward_pitch_rate_tracking(
    env,
    target_rate: float,
    std: float,
    asset_cfg: SceneEntityCfg,
) -> torch.Tensor:
    """Track a positive body-pitch rate for repeated forward rolls."""
    if target_rate <= 0.0 or std <= 0.0:
        raise ValueError("pitch-rate target and standard deviation must be positive")
    asset: Articulation = env.scene[asset_cfg.name]
    pitch_rate = asset.data.root_ang_vel_b.torch[:, 1]
    return torch.exp(-torch.square(pitch_rate - target_rate) / std**2)


def reverse_pitch_rate_l1(
    env,
    asset_cfg: SceneEntityCfg,
) -> torch.Tensor:
    """Penalize backward pitch so consecutive rolls keep one direction."""
    asset: Articulation = env.scene[asset_cfg.name]
    return torch.relu(-asset.data.root_ang_vel_b.torch[:, 1])


def forward_world_velocity_tracking(
    env,
    target_speed: float,
    std: float,
    asset_cfg: SceneEntityCfg,
) -> torch.Tensor:
    """Track forward world velocity so the policy rolls across the floor."""
    if target_speed < 0.0 or std <= 0.0:
        raise ValueError("forward target must be non-negative and std must be positive")
    asset: Articulation = env.scene[asset_cfg.name]
    forward_speed = asset.data.root_lin_vel_w.torch[:, 0]
    return torch.exp(-torch.square(forward_speed - target_speed) / std**2)


def lateral_world_velocity_l2(
    env,
    asset_cfg: SceneEntityCfg,
) -> torch.Tensor:
    """Penalize sideways drift during repeated forward rolls."""
    asset: Articulation = env.scene[asset_cfg.name]
    return torch.square(asset.data.root_lin_vel_w.torch[:, 1])


def off_axis_angular_velocity_l2(
    env,
    asset_cfg: SceneEntityCfg,
) -> torch.Tensor:
    """Penalize roll and yaw rates while leaving desired pitch free."""
    asset: Articulation = env.scene[asset_cfg.name]
    angular_velocity = asset.data.root_ang_vel_b.torch
    return torch.square(angular_velocity[:, 0]) + torch.square(angular_velocity[:, 2])


def root_height_soft_band(
    env,
    minimum_height: float,
    maximum_height: float,
    std: float,
    asset_cfg: SceneEntityCfg,
) -> torch.Tensor:
    """Return one inside a broad floor-contact band and decay outside it."""
    if minimum_height >= maximum_height or std <= 0.0:
        raise ValueError("root-height band must be ordered and std must be positive")
    asset: Articulation = env.scene[asset_cfg.name]
    height = asset.data.root_pos_w.torch[:, 2]
    distance = torch.relu(minimum_height - height) + torch.relu(
        height - maximum_height
    )
    return torch.exp(-torch.square(distance) / std**2)


def root_state_out_of_bounds(
    env,
    maximum_forward_distance: float,
    maximum_lateral_distance: float,
    maximum_height: float,
    asset_cfg: SceneEntityCfg,
) -> torch.Tensor:
    """Stop only runaway or invalid roll episodes, not ordinary inversion."""
    asset: Articulation = env.scene[asset_cfg.name]
    position = asset.data.root_pos_w.torch
    relative = position - env.scene.env_origins
    invalid = ~torch.isfinite(position).all(dim=1)
    return (
        invalid
        | (relative[:, 0].abs() > maximum_forward_distance)
        | (relative[:, 1].abs() > maximum_lateral_distance)
        | (position[:, 2] > maximum_height)
        | (position[:, 2] < -0.02)
    )


def _full_roll_counter(env, asset_cfg):
    """Update once per environment step, shared by all full-roll terms."""
    from ...roll_metrics import ForwardTurnCounter

    if not hasattr(env, "_full_roll_counter"):
        env._full_roll_counter = ForwardTurnCounter(env.num_envs, env.device)
        env._full_roll_counter_step = -1
    if env._full_roll_counter_step != env.common_step_counter:
        asset = env.scene[asset_cfg.name]
        env._full_roll_counter.update(
            asset.data.projected_gravity_b.torch,
            env.episode_length_buf <= 1,
        )
        env._full_roll_counter_step = env.common_step_counter
    return env._full_roll_counter


def full_roll_frontier_progress(env, asset_cfg):
    """Pay only new net rotation, never repeatedly pay the same rocking arc."""
    counter = _full_roll_counter(env, asset_cfg)
    return torch.clamp(counter.new_progress / env.step_dt, max=6.0) / (2 * math.pi)


def full_roll_completion(env, asset_cfg):
    """One discrete bonus for each newly completed full forward revolution."""
    counter = _full_roll_counter(env, asset_cfg)
    return counter.new_turns.float() / env.step_dt


def roll_flatness_l2(env, asset_cfg):
    """Discourage collapsing sideways while permitting complete inversion."""
    return torch.square(env.scene[asset_cfg.name].data.projected_gravity_b.torch[:, 1])


def roll_axis_alignment_error(env, asset_cfg):
    """Keep body pitch axis parallel to world Y throughout all roll phases."""
    from isaaclab.utils.math import quat_apply

    asset = env.scene[asset_cfg.name]
    axis = torch.zeros((env.num_envs, 3), device=env.device)
    axis[:, 1] = 1.0
    world_axis = quat_apply(asset.data.root_quat_w.torch, axis)
    return 1.0 - world_axis[:, 1].clamp(-1.0, 1.0)


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


def set_reward_float_param_schedule(
    env,
    env_ids: Sequence[int],
    term_name: str,
    param_name: str,
    stages: tuple[tuple[int, float], ...],
) -> float:
    """Update one numeric reward parameter from an ordered curriculum."""
    del env_ids
    if not stages:
        raise ValueError("reward-parameter curriculum requires at least one stage")
    selected_value = stages[0][1]
    for step, value in stages:
        if env.common_step_counter >= step:
            selected_value = value
    if not math.isfinite(selected_value):
        raise ValueError("reward-parameter curriculum values must be finite")
    term_cfg = env.reward_manager.get_term_cfg(term_name)
    if term_cfg.params.get(param_name) != selected_value:
        term_cfg.params[param_name] = float(selected_value)
        env.reward_manager.set_term_cfg(term_name, term_cfg)
    return float(selected_value)


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


def set_aggressive_velocity_command_schedule(
    env,
    env_ids: Sequence[int],
    command_name: str,
    stages: tuple[
        tuple[
            int,
            tuple[float, float],
            tuple[float, float],
            tuple[float, float],
            float,
            tuple[float, float],
        ],
        ...,
    ],
) -> float:
    """Widen velocity commands and introduce sprint episodes progressively."""

    if not stages:
        raise ValueError("aggressive velocity curriculum requires at least one stage")
    selected = stages[0]
    for stage in stages:
        if env.common_step_counter >= stage[0]:
            selected = stage
    _, lin_vel_x, lin_vel_y, ang_vel_z, sprint_fraction, sprint_speed = selected
    for name, value_range in (
        ("lin_vel_x", lin_vel_x),
        ("lin_vel_y", lin_vel_y),
        ("ang_vel_z", ang_vel_z),
        ("sprint_speed", sprint_speed),
    ):
        lower, upper = value_range
        if (
            not math.isfinite(lower)
            or not math.isfinite(upper)
            or lower > upper
        ):
            raise ValueError(f"invalid {name} curriculum range: {value_range}")
    if not 0.0 <= sprint_fraction <= 1.0:
        raise ValueError("sprint curriculum fraction must be between zero and one")

    term = env.command_manager.get_term(command_name)
    changed = (
        tuple(term.cfg.ranges.lin_vel_x) != tuple(lin_vel_x)
        or tuple(term.cfg.ranges.lin_vel_y) != tuple(lin_vel_y)
        or tuple(term.cfg.ranges.ang_vel_z) != tuple(ang_vel_z)
        or term.cfg.rel_sprint_envs != sprint_fraction
        or tuple(term.cfg.sprint_speed_range) != tuple(sprint_speed)
    )
    if changed:
        term.cfg.ranges.lin_vel_x = tuple(lin_vel_x)
        term.cfg.ranges.lin_vel_y = tuple(lin_vel_y)
        term.cfg.ranges.ang_vel_z = tuple(ang_vel_z)
        term.cfg.rel_sprint_envs = float(sprint_fraction)
        term.cfg.sprint_speed_range = tuple(sprint_speed)
        if isinstance(env_ids, slice):
            resample_ids = torch.arange(env.num_envs, device=env.device)
        else:
            resample_ids = torch.as_tensor(env_ids, device=env.device)
        term._resample_command(resample_ids)
    return float(sprint_speed[1])
