# energy_logger_block.py  — drop-in replacement
from __future__ import annotations
import random
import re
from typing import Optional

from pydantic import Field
from agentsociety.agent import AgentToolbox, Block, BlockParams, BlockContext, BlockOutput
from agentsociety.logger import get_logger
from agentsociety.memory import Memory


def _randn_pos(mean: float, std: float, fallback_min: float = 1.0) -> float:
    mean = float(mean); std = max(1e-6, float(std))
    for _ in range(10):
        v = random.normalvariate(mean, std)
        if v > 0:
            return v
    return max(fallback_min, mean)


class EnergyLoggerParams(BlockParams):
    # ---------- Activity keywords (home) ----------
    keyword_map: dict[str, list[str]] = Field(
        default={
            "rest":   ["sleep", "nap"],
            "leisure":["read", "music", "tv", "movie", "game"],
            "wfh":    ["work from home", "working from home", "wfh", "remote meeting", "email", "coding"],
        },
        description="Activity category -> list of keywords to match from context text.",
    )

    # Power sampling for at-home activities
    distributions: dict[str, dict] = Field(
        default={
            "rest":   {"mean": 28.0,  "std": 6.0},
            "leisure":{"mean": 130.0, "std": 30.0},
            "wfh":    {"mean": 240.0, "std": 55.0},
        },
        description="Normal distributions for power (W) when at home and a keyword is matched.",
    )

    # ---------- Always-on / standby baseline models (used EVERY tick) ----------
    away_appliance_idle_models: dict[str, dict] = Field(
        default={
            "refrigerator":    {"type": "always_on", "mean": 55.0, "std": 12.0, "w_per_unit": True},
            "freezer":         {"type": "always_on", "mean": 50.0, "std": 10.0, "w_per_unit": True},
            "television":      {"type": "standby",   "mean": 2.0,  "std": 0.8, "w_per_unit": True},
            "microwave":       {"type": "standby",   "mean": 3.0,  "std": 1.0, "w_per_unit": True},
            "desktop_laptop":  {"type": "standby",   "mean": 4.0,  "std": 2.0, "w_per_unit": True},
            "electric_stove":  {"type": "standby",   "mean": 1.0,  "std": 0.5, "w_per_unit": True},
            "oven":            {"type": "standby",   "mean": 1.2,  "std": 0.6, "w_per_unit": True},
            "dishwasher":      {"type": "standby",   "mean": 1.0,  "std": 0.5, "w_per_unit": True},
            "washer":          {"type": "standby",   "mean": 0.8,  "std": 0.4, "w_per_unit": True},
            "dryer":           {"type": "standby",   "mean": 0.8,  "std": 0.4, "w_per_unit": True},
            "air_conditioner": {"type": "standby",   "mean": 1.0,  "std": 0.5, "w_per_unit": True},
            "cooling_fans":    {"type": "standby",   "mean": 0.5,  "std": 0.3, "w_per_unit": True},
            "kettle":          {"type": "standby",   "mean": 0.3,  "std": 0.2, "w_per_unit": True},
            "vacuum_cleaner":  {"type": "standby",   "mean": 0.2,  "std": 0.1, "w_per_unit": True},
        },
        description="Idle/always-on power models (W); interpreted per unit if w_per_unit=True. Used every tick.",
    )
    away_baseload_fallback_w: dict = Field(
        default={"mean": 20.0, "std": 5.0},
        description="Fallback baseload (W) when no always-on devices are present.",
    )
    enable_base_idle_logging: bool = Field(default=True, description="Log baseline idle (base_idle) every tick.")
    enable_away_delta_logging: bool = Field(
        default=False,
        description="If True, additionally log away-only delta = max(0, away_idle - base_idle) as 'away_idle_delta'.",
    )

    # ---------- Misc / timing ----------
    home_location_alias: list[str] = Field(default=["at home"])
    step_minutes_default: float = Field(default=10.0)
    daily_auto_reset: bool = Field(default=True)
    skip_first_tick: bool = Field(default=True)
    clamp_minutes_to_step: bool = Field(default=True)
    require_aoi_for_home: bool = Field(default=True)


class EnergyLoggerContext(BlockContext):
    last_step: Optional[dict] = Field(default=None)
    status_summary: str = Field(default="")
    current_position: str = Field(default="")
    matched_category: str = Field(default="")
    sampled_power_w: float = Field(default=0.0)
    sampled_energy_wh: float = Field(default=0.0)
    used_minutes: float = Field(default=0.0)


class EnergyLoggerOutput(BlockOutput):
    success: bool = True
    evaluation: str = ""
    consumed_time: float = 0.0
    node_id: Optional[int] = None
    category: Optional[str] = None
    power_w: Optional[float] = None
    energy_wh: Optional[float] = None
    minutes: Optional[float] = None


class EnergyLoggerBlock(Block):
    """
    New behavior:
      (A) base_idle: ALWAYS recorded every tick from appliances (fridge/freezer/standby etc.), at home or away.
      (B) at-home activity: keyword-driven incremental loads on top of base_idle (only when at_home & keyword matched).
      (C) Optional away_idle_delta: when away, log the positive difference (away_idle - base_idle) to be backward-compatible.
    """
    ParamsType = EnergyLoggerParams
    ContextType = EnergyLoggerContext
    OutputType = EnergyLoggerOutput

    name = "EnergyLoggerBlock"
    description = "Record base idle every tick + at-home activity loads; optional away-only delta."

    def __init__(self, toolbox: AgentToolbox, agent_memory: Memory, block_params: Optional[EnergyLoggerParams] = None):
        super().__init__(toolbox=toolbox, agent_memory=agent_memory, block_params=block_params)

    # ---------- helpers ----------
    def _tick_minutes(self) -> float:
        try:
            sec = getattr(self.environment, "ticks_per_step", None)
            if sec is not None:
                return float(sec) / 60.0
        except Exception:
            pass
        return float(self.params.step_minutes_default)

    # ---------- Determine if the agent is at home ----------
    async def _is_at_home(self, agent_context: EnergyLoggerContext) -> bool:
        try:
            position = await self.memory.status.get("position")
            home = await self.memory.status.get("home")
            pos_id  = (((position or {}).get("aoi_position") or {}).get("aoi_id"))
            home_id = (((home     or {}).get("aoi_position") or {}).get("aoi_id"))
            if pos_id is not None and home_id is not None:
                return pos_id == home_id

            def _name(d):
                if not isinstance(d, dict): return ""
                ap = d.get("aoi_position") or {}
                return (ap.get("name") or d.get("name") or "").strip().lower()

            pos_name = _name(position)
            home_name = _name(home)
            if pos_name and home_name:
                return pos_name == home_name

            if self.params.require_aoi_for_home:
                return False
        except Exception as e:
            get_logger().warning(f"[EnergyLogger] AOI check failed: {e}")
            if self.params.require_aoi_for_home:
                return False

        pieces = [
            agent_context.current_position or "",
            agent_context.status_summary or "",
        ]
        if isinstance(agent_context.last_step, dict):
            pieces.append(agent_context.last_step.get("intention") or "")
            pieces.append(((agent_context.last_step.get("evaluation") or {}).get("evaluation")) or "")
        text_pool = " ".join(pieces).lower()

        not_home = re.compile(
            r"\b(?:leave|left|leaving|depart|departing|commute|commuting|go|going)\s+(?:to|from)\s+home\b"
            r"|\bfrom\s+home\b|\bto\s+home\b"
        )
        if not_home.search(text_pool):
            return False

        if ("working from home" in text_pool) or ("work from home" in text_pool) or (" wfh" in text_pool):
            return True
        at_home = re.compile(r"\bat\s+home\b")
        return bool(at_home.search(text_pool))

    # ---------- Activity classification & sampling (at home) ----------
    def _classify_activity(self, text: str) -> Optional[str]:
        t = (text or "").lower()
        for act, kws in self.params.keyword_map.items():
            for kw in kws:
                if kw.lower() in t:
                    return act
        return None

    def _sample_power_w(self, category: str) -> float:
        dist = self.params.distributions.get(category, {"mean": 60.0, "std": 20.0})
        return _randn_pos(dist.get("mean", 60.0), dist.get("std", 20.0), fallback_min=5.0)

    # ---------- Appliances sourcing (status first, fallback profile); NO alias mapping ----------
    async def _get_appliances(self) -> dict:
        apps = {}
        try:
            a = await self.memory.status.get("appliances")
            if isinstance(a, dict):
                apps = a
        except Exception as e:
            get_logger().warning(f"[EnergyLogger] read status appliances failed: {e}")

        if not apps:
            # fallback to profile if available
            try:
                prof = await self.memory.profile.get_all()
            except Exception:
                prof = {}
            if isinstance(prof, dict):
                a = prof.get("appliances")
                if isinstance(a, dict):
                    apps = a

        # normalize counts to non-negative ints; DO NOT rename keys
        norm = {}
        for k, v in (apps or {}).items():
            if not isinstance(v, dict):
                continue
            try:
                c = int(v.get("count", 0))
            except Exception:
                c = 0
            norm[k] = {"count": max(0, c)}
        return norm

    # ---------- Idle power sampling (shared by base & away estimation) ----------
    def _sample_idle_power_w(self, appliances: dict) -> tuple[float, bool]:
        """
        Returns (power_w, seen_always_on)
        """
        models = self.params.away_appliance_idle_models or {}
        total_w = 0.0
        seen_always_on = False

        for key, meta in models.items():
            dev = appliances.get(key)
            if not isinstance(dev, dict):
                continue
            count = int(dev.get("count") or 0)
            if count <= 0:
                continue

            mtype = (meta.get("type") or "standby").lower()
            mean = float(meta.get("mean", 1.0))
            std  = float(meta.get("std",  0.5))
            w = _randn_pos(mean, std, fallback_min=0.1)
            if bool(meta.get("w_per_unit", True)):
                w *= count

            total_w += w
            if mtype == "always_on":
                seen_always_on = True

        if not seen_always_on:
            fb = self.params.away_baseload_fallback_w or {"mean": 20.0, "std": 5.0}
            total_w += _randn_pos(fb.get("mean", 20.0), fb.get("std", 5.0), fallback_min=5.0)

        return max(1.0, total_w), seen_always_on

    # ---------- Init keys & daily reset ----------
    async def _ensure_energy_keys(self, current_day: int) -> None:
        def _safe(val, default):
            return val if val is not None else default

        try:
            total   = _safe(await self.memory.status.get("energy_wh_total"), 0.0)
            day_val = _safe(await self.memory.status.get("energy_wh_day"), 0.0)
            by_cat  = _safe(await self.memory.status.get("energy_by_category"), {})
            logs    = _safe(await self.memory.status.get("energy_logs"), [])
            history = _safe(await self.memory.status.get("energy_daily_history"), {})
            try:
                day_marker = await self.memory.status.get("energy_day_marker")
            except Exception:
                day_marker = None

            await self.memory.status.update("energy_wh_total", float(total))
            await self.memory.status.update("energy_wh_day", float(day_val))
            await self.memory.status.update("energy_by_category", by_cat)
            await self.memory.status.update("energy_logs", logs)
            await self.memory.status.update("energy_daily_history", history)
            if day_marker is None:
                await self.memory.status.update("energy_day_marker", current_day)
                day_marker = current_day

            if self.params.daily_auto_reset and day_marker != current_day:
                prev_day_value = float(_safe(await self.memory.status.get("energy_wh_day"), 0.0))
                history = _safe(await self.memory.status.get("energy_daily_history"), {})
                history[str(day_marker)] = prev_day_value
                await self.memory.status.update("energy_daily_history", history)
                await self.memory.status.update("energy_wh_day", 0.0)
                await self.memory.status.update("energy_day_marker", current_day)
        except Exception as e:
            get_logger().warning(f"[EnergyLogger] ensure keys failed: {e}")

    # ---------- Main forward ----------
    async def forward(self, agent_context) -> EnergyLoggerOutput:
        self.context = self.ContextType(**{
            "last_step": agent_context.get("last_step") or agent_context.get("current_step"),
            "status_summary": agent_context.get("status_summary", "") or "",
            "current_position": agent_context.get("current_position", "") or "",
        })

        # --- Occupancy (home) tracking: update every tick, even if energy logging is skipped ---
        try:
            at_home_now = await self._is_at_home(self.context)

            # ensure integer counter
            try:
                cur = await self.memory.status.get("home_occupancy_steps")
            except Exception:
                cur = 0
            try:
                cur_i = int(cur)
            except Exception:
                # tolerate weird types like "0" or 0.0
                cur_i = int(float(cur)) if cur is not None else 0

            if at_home_now:
                cur_i += 1

            await self.memory.status.update("home_occupancy_steps", cur_i)
            await self.memory.status.update("is_at_home", bool(at_home_now))
        except Exception as e:
            get_logger().warning(f"[EnergyLogger] occupancy update failed: {e}")


        # 0) Skip first tick (compatibility)
        if self.params.skip_first_tick:
            try:
                skipped = await self.memory.status.get("energy_first_tick_skipped")
            except Exception:
                skipped = False
            if not skipped:
                await self.memory.status.update("energy_first_tick_skipped", True)
                return self.OutputType(success=True, evaluation="EnergyLogger: first tick skipped", consumed_time=0.0)

        # 1) Ensure keys & rollover
        day, _ = self.environment.get_datetime(format_time=True) if self.environment else (0, "")
        await self._ensure_energy_keys(current_day=day)

        # 2) Determine minutes
        tick_minutes = self._tick_minutes()
        minutes = tick_minutes
        try:
            if isinstance(self.context.last_step, dict):
                m = (self.context.last_step.get("evaluation") or {}).get("consumed_time")
                if m is not None:
                    minutes = float(m)
        except Exception:
            pass
        if self.params.clamp_minutes_to_step:
            minutes = min(minutes, tick_minutes)
        self.context.used_minutes = minutes

        # 3) BASELINE: record base_idle every tick
        latest_node_id = None
        latest_eval = ""
        latest_category = None
        latest_pw = None
        latest_wh = None

        if self.params.enable_base_idle_logging:
            appliances = await self._get_appliances()
            base_power_w, _ = self._sample_idle_power_w(appliances)
            base_energy_wh = base_power_w * (minutes / 60.0)

            total = (await self.memory.status.get("energy_wh_total")) or 0.0
            daily = (await self.memory.status.get("energy_wh_day")) or 0.0
            by_cat = (await self.memory.status.get("energy_by_category")) or {}
            logs   = (await self.memory.status.get("energy_logs")) or []

            total += base_energy_wh
            daily += base_energy_wh
            by_cat["base_idle"] = float(by_cat.get("base_idle", 0.0) + base_energy_wh)
            logs.append({
                "day": day, "minutes": minutes, "category": "base_idle",
                "power_w": float(base_power_w), "energy_wh": float(base_energy_wh),
            })

            await self.memory.status.update("energy_wh_total", float(total))
            await self.memory.status.update("energy_wh_day", float(daily))
            await self.memory.status.update("energy_by_category", by_cat)
            await self.memory.status.update("energy_logs", logs)

            latest_eval = f"Energy logging: base_idle {base_energy_wh:.1f}Wh (P≈{base_power_w:.0f}W, {minutes:.0f}min)"
            latest_node_id = await self.memory.stream.add(topic="energy", description=latest_eval)
            latest_category, latest_pw, latest_wh = "base_idle", float(base_power_w), float(base_energy_wh)

        # 4) HOME / AWAY context
        at_home = await self._is_at_home(self.context)

        # (optional) AWAY delta (for backward compatibility without double counting)
        if (not at_home) and self.params.enable_away_delta_logging:
            appliances = await self._get_appliances()
            away_power_w, _ = self._sample_idle_power_w(appliances)  # same model; delta vs base == 0 in most setups


        # 5) AT-HOME activity on top of baseline
        if at_home:
            candidate_text = self.context.status_summary
            if isinstance(self.context.last_step, dict):
                intention = self.context.last_step.get("intention", "")
                eval_obj  = self.context.last_step.get("evaluation", {}) or {}
                eval_text = eval_obj.get("evaluation", "")
                candidate_text = f"{candidate_text}\n{intention}\n{eval_text}".strip()

            category = self._classify_activity(candidate_text)
            if category:
                power_w   = self._sample_power_w(category)
                energy_wh = power_w * (minutes / 60.0)
                self.context.sampled_power_w   = power_w
                self.context.sampled_energy_wh = energy_wh

                total = (await self.memory.status.get("energy_wh_total")) or 0.0
                daily = (await self.memory.status.get("energy_wh_day")) or 0.0
                by_cat = (await self.memory.status.get("energy_by_category")) or {}
                logs   = (await self.memory.status.get("energy_logs")) or []

                total += energy_wh
                daily += energy_wh
                by_cat[category] = float(by_cat.get(category, 0.0) + energy_wh)
                logs.append({
                    "day": day, "minutes": minutes, "category": category,
                    "power_w": float(power_w), "energy_wh": float(energy_wh),
                })

                await self.memory.status.update("energy_wh_total", float(total))
                await self.memory.status.update("energy_wh_day", float(daily))
                await self.memory.status.update("energy_by_category", by_cat)
                await self.memory.status.update("energy_logs", logs)

                latest_eval = f"Energy logging @home: act={category}, {energy_wh:.1f}Wh (P≈{power_w:.0f}W, {minutes:.0f}min)"
                latest_node_id = await self.memory.stream.add(topic="energy", description=latest_eval)
                latest_category, latest_pw, latest_wh = category, float(power_w), float(energy_wh)

        return self.OutputType(
            success=True,
            evaluation=latest_eval,
            consumed_time=0.0,
            node_id=latest_node_id,
            category=latest_category,
            power_w=latest_pw,
            energy_wh=latest_wh,
            minutes=float(minutes),
        )
