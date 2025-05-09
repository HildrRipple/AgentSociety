import random
import time

import jsonc
from typing import Optional

from pydantic import Field
from ..agent import AgentToolbox, Block, CitizenAgentBase, AgentParams
from ..logger import get_logger
from ..memory import Memory
from .blocks import (CognitionBlock, NeedsBlock, PlanBlock)
from .blocks.economy_block import MonthEconomyPlanBlock
from .blocks.needs_block import INITIAL_NEEDS_PROMPT, EVALUATION_PROMPT, REFLECTION_PROMPT
from .blocks.plan_block import DETAILED_PLAN_PROMPT


class SocialAgentConfig(AgentParams):
    """Configuration for social agent."""
    enable_cognition: bool = Field(default=True, description="Whether to enable cognition")
    UBI: float = Field(default=0, description="Universal Basic Income")
    num_labor_hours: int = Field(default=168, description="Number of labor hours per month")
    productivity_per_labor: float = Field(default=1, description="Productivity per labor hour")
    time_diff: int = Field(default=30 * 24 * 60 * 60, description="Time difference between two triggers")

    # Maxlow's Needs
    need_initialization_prompt: str = Field(default=INITIAL_NEEDS_PROMPT, description="Initial needs prompt")
    need_evaluation_prompt: str = Field(default=EVALUATION_PROMPT, description="Need evaluation prompt")
    need_reflection_prompt: str = Field(default=REFLECTION_PROMPT, description="Need reflection prompt")

    # Planned-Behavior
    max_plan_steps: int = Field(default=6, description="Maximum number of steps in a plan")
    plan_generation_prompt: str = Field(default=DETAILED_PLAN_PROMPT, description="Plan generation prompt")


class SocietyAgent(CitizenAgentBase):
    ParamsType = SocialAgentConfig
    description: str = """
A social agent that can interact with other agents and the environment.
The main workflow includes:
1. Agent needs determination (based on Maxlow's Hierarchy Needs) —— including hunger needs, safety needs, social needs and emergency needs)
2. Plan generation (The citizen generate a detailed plan based on the needs)
3. Step execution (The citizen execute the action based on the generated plan)

Notice: The capability of citizen is controled by the BLOCKS (defaultly, it contains 4 blocks:
1). MobilityBlock: endow the citizen with the ability to move around the city
2). EconomyBlock: endow the citizen with the ability to shoping and working
3). SocialBlock: endow the citizen with the ability to socializing with other citizens
4). OtherBlocks: handle other intentions (e.g., cooking, sleeping, etc.)

You can add more blocks to the citizen as you wish to adapt to the different scenarios. We strongly recommend you keep the default blocks as they are.
"""

    """Agent implementation with configurable cognitive/behavioral modules and social interaction capabilities."""
    def __init__(
        self,
        id: int,
        name: str,
        toolbox: AgentToolbox,
        memory: Memory,
        agent_params: Optional[SocialAgentConfig] = None,
        blocks: Optional[list[Block]] = None,
    ) -> None:
        """Initialize agent with core components and configuration."""
        super().__init__(
            id=id,
            name=name,
            toolbox=toolbox,
            memory=memory,
            agent_params=agent_params,
            blocks=blocks,
        )

        self.month_plan_block = MonthEconomyPlanBlock(
            llm=self.llm, 
            environment=self.environment, 
            agent_memory=self.memory,
            ubi=self.params.UBI,
            num_labor_hours=self.params.num_labor_hours,
            productivity_per_labor=self.params.productivity_per_labor,
            time_diff=self.params.time_diff,
        )

        self.needs_block = NeedsBlock(
            llm=self.llm, 
            environment=self.environment, 
            agent_memory=self.memory,
            evaluation_prompt=self.params.need_evaluation_prompt,
            reflection_prompt=self.params.need_reflection_prompt,
            initial_prompt=self.params.need_initialization_prompt,
        )

        self.plan_block = PlanBlock(
            llm=self.llm, 
            environment=self.environment, 
            agent_memory=self.memory,
            max_plan_steps=self.params.max_plan_steps,
            detailed_plan_prompt=self.params.plan_generation_prompt,
        )

        self.cognition_block = CognitionBlock(
            llm=self.llm, agent_memory=self.memory, environment=self.environment
        )
        self.step_count = -1
        self.cognition_update = -1

    async def reset(self):
        """Reset the agent."""
        # reset position to home
        await self.reset_position()

        # reset needs
        await self.memory.status.update("current_need", "none")

        # reset plans and actions
        await self.memory.status.update("current_plan", {})
        await self.memory.status.update("execution_context", {})

        # reset initial flag
        await self.needs_block.reset()

    async def plan_generation(self):
        """Generate a new plan if no current plan exists in memory."""
        cognition = None
        current_plan = await self.memory.status.get("current_plan")
        if current_plan is None or not current_plan:
            cognition = (
                await self.plan_block.forward()
            )  # Delegate to PlanBlock for plan creation
        return cognition

    # Main workflow
    async def forward(self):
        """Main agent loop coordinating status updates, plan execution, and cognition."""
        start_time = time.time()
        self.step_count += 1

        # check last step
        ifpass = await self.check_and_update_step()
        if not ifpass:
            return
        get_logger().debug(
            f"Agent {self.id}: Finished main workflow - check and update step"
        )

        # month plan
        await self.month_plan_block.forward()

        # Maxlow's Needs
        cognition = await self.needs_block.forward()
        if self.params.enable_cognition and cognition:
            await self.save_agent_thought(cognition)

        # Planned-Behavior
        cognition = await self.plan_generation()
        if cognition:
            await self.save_agent_thought(cognition)
        get_logger().debug(f"Agent {self.id}: Finished main workflow - plan")

        # step execution - dispatch to different blocks
        await self.step_execution()
        get_logger().debug(f"Agent {self.id}: Finished main workflow - step execution")

        # cognition
        if self.params.enable_cognition:
            await self.cognition_block.forward()
        get_logger().debug(f"Agent {self.id}: Finished main workflow - cognition")

        return time.time() - start_time

    async def check_and_update_step(self):
        """Check if the previous step has been completed"""
        status = await self.memory.status.get("status")
        if status == 2:
            # Agent is moving
            return False

        # Get the previous step information
        current_plan = await self.memory.status.get("current_plan")
        # If there is no current plan, return True
        if current_plan is None or not current_plan:
            return True
        step_index = current_plan.get("index", 0)
        current_step = current_plan.get("steps", [])[step_index]
        time_now = self.environment.get_tick()
        step_start_time = current_step["start_time"]
        step_consumed_time = current_step["evaluation"]["consumed_time"]
        try:
            time_end_plan = step_start_time + int(step_consumed_time) * 60
        except Exception as e:
            get_logger().warning(f"Error in check_and_update_step: {str(e)}")
            time_end_plan = time_now
        if time_now >= time_end_plan:
            # The previous step has been completed
            current_step["evaluation"]["consumed_time"] = (
                time_now - step_start_time
            ) / 60
            current_plan["stream_nodes"].append(current_step["evaluation"]["node_id"])
            if current_step["evaluation"]["success"]:
                # last step is completed
                current_plan["steps"][step_index] = current_step
                if step_index + 1 < len(current_plan["steps"]):
                    # Last step is completed
                    current_plan["index"] = step_index + 1
                    await self.memory.status.update("current_plan", current_plan)
                else:
                    # Whole plan is completed
                    current_plan["completed"] = True
                    _, current_plan["end_time"] = self.environment.get_datetime(
                        format_time=True
                    )
                    related_memories = None
                    if self.params.enable_cognition:
                        try:
                            # Update emotion for the plan
                            related_memories = await self.memory.stream.get_by_ids(
                                current_plan["stream_nodes"]
                            )
                            incident = f"You have successfully completed the plan: {related_memories}"
                            conclusion = (
                                await self.cognition_block.emotion_update(
                                    incident
                                )
                            )
                            await self.save_agent_thought(conclusion)
                            await self.memory.stream.add_cognition_to_memory(
                                current_plan["stream_nodes"], conclusion
                            )
                        except Exception as e:
                            get_logger().warning(
                                f"Error in check_and_update_step (emotion_update): {str(e)}\nrelated_memories: {related_memories}"
                            )
                    await self.memory.status.update("current_plan", current_plan)
                return True
            else:
                # last step is failed
                current_plan["failed"] = True
                _, current_plan["end_time"] = self.environment.get_datetime(
                    format_time=True
                )
                if self.params.enable_cognition:
                    related_memories = None
                    try:
                        # Update emotion for the plan
                        related_memories = await self.memory.stream.get_by_ids(
                            current_plan["stream_nodes"]
                        )
                        incident = (
                            f"You have failed to complete the plan: {related_memories}"
                        )
                        conclusion = (
                            await self.cognition_block.emotion_update(
                                incident
                            )
                        )
                        await self.save_agent_thought(conclusion)
                        await self.memory.stream.add_cognition_to_memory(
                            current_plan["stream_nodes"], conclusion
                        )
                    except Exception as e:
                        get_logger().warning(
                            f"Error in check_and_update_step (emotion_update): {str(e)}\nrelated_memories: {related_memories}"
                        )
                await self.memory.status.update("current_plan", current_plan)
                return True
        # The previous step has not been completed
        return False

    async def process_agent_chat_response(self, payload: dict) -> str:
        """Process incoming social/economic messages and generate responses."""
        if payload["type"] == "social":
            resp = f"Agent {self.id} received agent chat response: {payload}"
            try:
                # Extract basic info
                sender_id = payload.get("from")
                if not sender_id:
                    return ""

                raw_content = payload.get("content", "")

                # Parse message content
                try:
                    message_data = jsonc.loads(raw_content)
                    content = message_data["content"]
                    propagation_count = message_data.get("propagation_count", 1)
                except (jsonc.JSONDecodeError, TypeError, KeyError):
                    content = raw_content
                    propagation_count = 1

                if not content:
                    return ""

                # add social memory
                description = f"You received a social message: {content}"
                await self.memory.stream.add_social(description=description)
                if self.params.enable_cognition:
                    # update emotion
                    await self.cognition_block.emotion_update(description)

                # Get chat histories and ensure proper format
                chat_histories = await self.memory.status.get("chat_histories") or {}
                if not isinstance(chat_histories, dict):
                    chat_histories = {}

                # Update chat history with received message
                if sender_id not in chat_histories:
                    chat_histories[sender_id] = ""
                if chat_histories[sender_id]:
                    chat_histories[sender_id] += "，"
                chat_histories[sender_id] += f"them: {content}"

                # Check propagation limit
                if propagation_count > 5:
                    await self.memory.status.update("chat_histories", chat_histories)
                    return ""

                # Get relationship score
                relationships = await self.memory.status.get("relationships") or {}
                relationship_score = relationships.get(sender_id, 50)

                # Decision prompt
                should_respond_prompt = f"""Based on:
        - Received message: "{content}"
        - Our relationship score: {relationship_score}/100
        - My profile: {{
            "gender": "{await self.memory.status.get("gender") or ""}",
            "education": "{await self.memory.status.get("education") or ""}",
            "personality": "{await self.memory.status.get("personality") or ""}",
            "occupation": "{await self.memory.status.get("occupation") or ""}"
        }}
        - My current emotion: {await self.memory.status.get("emotion_types")}
        - Recent chat history: {chat_histories.get(sender_id, "")}

        Should I respond to this message? Consider:
        1. Is this a message that needs/deserves a response?
        2. Would it be natural for someone with my personality to respond?
        3. Is our relationship close enough to warrant a response?

        Answer only YES or NO, in JSON format, e.g. {{"should_respond": "YES"}}"""

                should_respond = await self.llm.atext_request(
                    dialog=[
                        {
                            "role": "system",
                            "content": "You are helping decide whether to respond to a message.",
                        },
                        {"role": "user", "content": should_respond_prompt},
                    ],
                    response_format={"type": "json_object"},
                )
                should_respond = jsonc.loads(should_respond)["should_respond"]
                if should_respond == "NO":
                    return ""

                response_prompt = f"""Based on:
        - Received message: "{content}"
        - Our relationship score: {relationship_score}/100
        - My profile: {{
            "gender": "{await self.memory.status.get("gender") or ""}",
            "education": "{await self.memory.status.get("education") or ""}",
            "personality": "{await self.memory.status.get("personality") or ""}",
            "occupation": "{await self.memory.status.get("occupation") or ""}"
        }}
        - My current emotion: {await self.memory.status.get("emotion_types")}
        - Recent chat history: {chat_histories.get(sender_id, "")}

        Generate an appropriate response that:
        1. Matches my personality and background
        2. Maintains natural conversation flow
        3. Is concise (under 100 characters)
        4. Reflects our relationship level

        Response should be ONLY the message text, no explanations."""

                response = await self.llm.atext_request(
                    [
                        {
                            "role": "system",
                            "content": "You are helping generate a chat response.",
                        },
                        {"role": "user", "content": response_prompt},
                    ]
                )

                if response:
                    # Update chat history with response
                    chat_histories[sender_id] += f"，me: {response}"
                    await self.memory.status.update("chat_histories", chat_histories)

                    # Send response
                    serialized_response = jsonc.dumps(
                        {
                            "content": response,
                            "propagation_count": propagation_count + 1,
                        },
                        ensure_ascii=False,
                    )
                    await self.send_message_to_agent(sender_id, serialized_response)
                return response

            except Exception as e:
                get_logger().warning(f"Error in process_agent_chat_response: {str(e)}")
                return ""
        else:
            content = payload["content"]
            key, value = content.split("@")
            if "." in value:
                value = float(value)
            else:
                value = int(value)
            description = f"You received a economic message: Your {key} has changed from {await self.memory.status.get(key)} to {value}"
            await self.memory.status.update(key, value)
            await self.memory.stream.add_economy(description=description)
            if self.params.enable_cognition:
                await self.cognition_block.emotion_update(description)
            return ""

    async def react_to_intervention(self, intervention_message: str):
        """React to an intervention"""
        # cognition
        conclusion = await self.cognition_block.emotion_update(
            intervention_message
        )
        await self.save_agent_thought(conclusion)
        await self.memory.stream.add_cognition(description=conclusion)
        # needs
        await self.needs_block.reflect_to_intervention(
            intervention_message
        )

    async def reset_position(self):
        """Reset the position of the agent."""
        home = await self.status.get("home")
        home = home["aoi_position"]["aoi_id"]
        await self.environment.reset_person_position(person_id=self.id, aoi_id=home)

    async def step_execution(self):
        """Execute the current step in the active plan based on step type."""
        current_plan = await self.memory.status.get("current_plan")
        if (
            current_plan is None
            or not current_plan
            or len(current_plan.get("steps", [])) == 0
        ):
            return  # No plan, no execution
        step_index = current_plan.get("index", 0)
        execution_context = await self.memory.status.get("execution_context")
        current_step = current_plan.get("steps", [])[step_index]
        # check current_step is valid (not empty)
        if current_step:
            position = await self.memory.status.get("position")
            if "aoi_position" in position:
                current_step["position"] = position["aoi_position"]["aoi_id"]
            current_step["start_time"] = self.environment.get_tick()
            result = None
            selected_block = await self.dispatcher.dispatch(current_step["intention"])
            if selected_block:
                result = await selected_block.forward(current_step, execution_context)
                if "message" in result:
                    await self.send_message_to_agent(result["target"], result["message"])
            else:
                result = {
                    "success": False,
                    "evaluation": f"Failed to {current_step['intention']}",
                    "consumed_time": 0,
                    "node_id": None,
                }
            if result != None:
                current_step["evaluation"] = result

            # Update current_step, plan, and execution_context information
            current_plan["steps"][step_index] = current_step
            await self.memory.status.update("current_plan", current_plan)
            await self.memory.status.update("execution_context", execution_context)
