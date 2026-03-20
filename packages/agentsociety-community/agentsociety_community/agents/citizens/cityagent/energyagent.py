# energyagent.py
from __future__ import annotations
from typing import Optional
import json

from agentsociety.agent import AgentToolbox, Block, MemoryAttribute, DotDict
from agentsociety.memory import Memory
from agentsociety.logger import get_logger

from agentsociety_community.agents.citizens.cityagent.societyagent import (
    SocietyAgent, SocietyAgentConfig, SocietyAgentBlockOutput, SocietyAgentContext
)

from agentsociety_community.blocks.citizens.cityagent.energy_logger_block import EnergyLoggerBlock

# Import default memory config
from agentsociety.cityagent.memory_config import memory_config_societyagent, DEFAULT_DISTRIBUTIONS  # :contentReference[oaicite:1]{index=1}
from agentsociety.agent.distribution import ChoiceDistribution

class EnergyAgent(SocietyAgent):
    """
    Simlar to SocietyAgent（Needs -> Plan -> Dispatch） actions，
    Additionally record residential energy consumption
    """
    ParamsType = SocietyAgentConfig
    BlockOutputType = SocietyAgentBlockOutput
    Context = SocietyAgentContext

    # Extend status attributes
    StatusAttributes = [
        *SocietyAgent.StatusAttributes,  
        MemoryAttribute(
            name="energy_wh_total", type=float, default_or_value=0.0,
            description="Cumulative household electricity use (Wh)"
        ),
        MemoryAttribute(
            name="energy_wh_day", type=float, default_or_value=0.0,
            description="Today's household electricity use (Wh)"
        ),
        MemoryAttribute(
            name="energy_by_category", type=dict, default_or_value={},
            description="Electricity use grouped by activity category (Wh)"
        ),
        MemoryAttribute(
            name="energy_logs", type=list, default_or_value=[],
            description="Per-step energy logging records"
        ),
        MemoryAttribute(
            name="energy_last_logged_node_id", type=int, default_or_value=-1,
            description="Dedup guard: node_id of the last step that was logged"
        ),
        MemoryAttribute(
            name="energy_day_marker", type=int, default_or_value=-1,
            description="Day index marker for per-day reset in energy logging"
        ),
        MemoryAttribute(
            name="energy_daily_history", type=dict, default_or_value={},
            description="Historical daily energy_wh_day by day index"
        ),
        MemoryAttribute(
            name="appliances",
            type=dict,
            default_or_value={},
            description="appliance ownership & usage for logger"
        ),
        MemoryAttribute(
            name="is_at_home", type=bool, default_or_value=False,
            description="Whether the agent is currently at home (evaluated each tick)."
        ),
        MemoryAttribute(
            name="home_occupancy_steps", type=int, default_or_value=0,
            description="Cumulative number of ticks the agent stays at home AOI."
        ),

    ]

    
    #   
    @staticmethod
    def with_energy_memory_config(distributions, class_config=None):
        """
        (distributions, class_config) -> MemoryConfig
        """

        base = distributions.copy() if distributions is not None else {}

        for k, v in DEFAULT_DISTRIBUTIONS.items():
            base.setdefault(k, v)

        merged = []
        if class_config:
            merged.extend(class_config)
        merged.extend(EnergyAgent.StatusAttributes)

        return memory_config_societyagent(
            distributions=base,
            class_config=merged,
        )

    def __init__(
        self,
        id: int,
        name: str,
        toolbox: AgentToolbox,
        memory: Memory,
        agent_params: Optional[SocietyAgentConfig] = None,
        blocks: Optional[list[Block]] = None,
    ) -> None:
        super().__init__(
            id=id, name=name, toolbox=toolbox, memory=memory,
            agent_params=agent_params, blocks=blocks
        )
        self._energy_logger = EnergyLoggerBlock(toolbox=self._toolbox, agent_memory=self.memory)
    
    async def status_summary(self):
        """
        Transform status for UI/DB into JSON，
        flatten energy related metrics to string for UI/DB to read,
        save the status_summary from super class to status_summary_text for EnergyLoggerBlock.
        """
        #Write in memory.status["status_summary"]
        try:
            await super().status_summary()
        except Exception:
            pass

        #Read the summary
        def _blank_or_nothing(x):
            return (x is None) or (isinstance(x, str) and x.strip().lower() in ("nothing", "null", "none", ""))

        try:
            brief = await self.memory.status.get("status_summary")
        except Exception:
            brief = ""

        if _blank_or_nothing(brief):
            try:
                cp = await self.memory.status.get("current_plan") or {}
                idx = int(cp.get("index", 0))
                steps = cp.get("steps", []) or []
                cur = steps[idx] if 0 <= idx < len(steps) else {}
                brief = (cur.get("intention") or
                         (cur.get("evaluation") or {}).get("evaluation") or
                         "I'm at home.")
            except Exception:
                brief = "I'm at home."

        await self.memory.status.update("status_summary_text", brief if isinstance(brief, str) else str(brief))

        #Collect energy metrics
        async def _safe(key, default):
            try:
                v = await self.memory.status.get(key)
                return default if v is None else v
            except Exception:
                return default

        total_wh = float(await _safe("energy_wh_total", 0.0) or 0.0)
        day_wh   = float(await _safe("energy_wh_day", 0.0) or 0.0)
        home_steps = int(await _safe("home_occupancy_steps", 0) or 0)
        is_home = bool(await _safe("is_at_home", False))

        by_cat   = await _safe("energy_by_category", {}) or {}
        logs     = await _safe("energy_logs", []) or []
        last_log = (logs[-1] if isinstance(logs, list) and len(logs) > 0 else None)

        #Flatten
        def to_primitive(v):
            if isinstance(v, (str, int, float, bool)) or v is None:
                return v
            return json.dumps(v, ensure_ascii=False, separators=(",", ":"))

        status_json = {                              
            "energy_wh_total":          to_primitive(total_wh),
            "energy_wh_day":            to_primitive(day_wh),
            "energy_by_category":       to_primitive(by_cat),                
            "last_energy_log":          to_primitive(last_log), 
            "is_at_home":               to_primitive(is_home),
            "home_occupancy_steps":     to_primitive(home_steps),
            
        }

        #Rewrite to DB
        await self.memory.status.update("status_summary", json.dumps(status_json, ensure_ascii=False))

    async def before_forward(self):
        await super().before_forward()

        for k, v in [
            ("current_plan", {}), ("execution_context", {}),
            ("status_summary_text", ""),
        ]:
            try:
                await self.memory.status.get(k)
            except KeyError:
                await self.memory.status.update(k, v)

    async def forward(self):
        """
        Call the EnergyLoggerBlock once per simulation tick.
        We deduplicate by a (day,time) stamp from the environment,
        instead of relying on node_id (which can be missing or unchanged).
        """
        runtime = await super().forward()

        try:
            try:
                status_text = await self.memory.status.get("status_summary_text")
                if not isinstance(status_text, str):
                    raise KeyError("status_summary_text is not a string")
            except Exception:
                try:
                    _ss = await self.memory.status.get("status_summary")
                    status_text = _ss if isinstance(_ss, str) else ""
                except Exception:
                    status_text = ""

            # Make a per-tick stamp from environment time
            # This uniquely identifies a simulation step for this agent.
            try:
                day, time_str = self.environment.get_datetime(format_time=True)
            except Exception:
                day, time_str = (0, "")
            stamp = f"{day}-{time_str}"

            # Read the last stamp we processed; if different -> log this tick
            try:
                last_stamp = await self.memory.status.get("energy_last_logged_stamp")
            except Exception:
                last_stamp = None

            if last_stamp != stamp:
                current_step = {}
                try:
                    current_plan = await self.memory.status.get("current_plan") or {}
                    idx = int(current_plan.get("index", 0))
                    steps = current_plan.get("steps", []) or []
                    if 0 <= idx < len(steps):
                        current_step = steps[idx]
                except Exception:
                    current_step = {}

                # Build the minimal context expected by EnergyLoggerBlock
                ctx = {
                    "last_step": current_step,     
                    "status_summary": status_text
                }

                # Call the energy logger once per tick
                _ = await self._energy_logger.forward(ctx)

                # Mark this tick as logged so repeated calls in the same tick won't double count
                await self.memory.status.update("energy_last_logged_stamp", stamp)

        except Exception as e:
            # Never let logging break the agent loop
            from agentsociety.logger import get_logger
            get_logger().warning(f"[EnergyAgent] energy logging skipped: {e}")

        return runtime

