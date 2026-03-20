import asyncio
from pathlib import Path
from agentsociety.environment.download_sim import download_binary

from agentsociety.cityagent import default
from agentsociety.configs import (
    AgentsConfig,
    Config,
    EnvConfig,
    ExpConfig,
    LLMConfig,
    MapConfig,
)
from agentsociety.cityagent.sharing_params import SocietyAgentConfig
from agentsociety.configs.agent import AgentConfig
from agentsociety.configs.exp import WorkflowStepConfig, WorkflowType
from agentsociety.environment import EnvironmentConfig
from agentsociety.llm import LLMProviderType
from agentsociety.simulation import AgentSociety
from agentsociety.storage import DatabaseConfig
from agentsociety_community.agents.citizens.cityagent.energyagent import EnergyAgent
from agentsociety.cityagent.memory_config import DEFAULT_DISTRIBUTIONS
from agentsociety_community.blocks.citizens.cityagent.mobility_block import MobilityBlock
from agentsociety_community.blocks.citizens.cityagent.economy_block import EconomyBlock
from agentsociety_community.blocks.citizens.cityagent.social_block import SocialBlock
from agentsociety_community.blocks.citizens.cityagent.other_block import OtherBlock

PLAN_GENERATION_PROMPT = """
You are the advanced planning module for a city-scale life simulation. 
Your goal is to translate a high-level "Plan Target" into a concrete, realistic sequence of actions (steps) for a human agent.

================================================================
PART 1: AGENT PROFILE & BACKGROUND (Static Persona)
================================================================
Background Story: 
"${profile.background_story}"

Demographics:
- Occupation: ${profile.occupation}
- Age: ${profile.age}
- Income/Consumption: ${profile.consumption}
- Personality/Gender: ${profile.gender}, ${profile.education}

================================================================
PART 2: CURRENT REALITY (Dynamic Context) -> **PRIORITY**
================================================================
- **Current Absolute Time**: ${context.current_time} 
  (This field encodes both:
   - which simulation day it is (Day 0, Day 1, Day 2, ... — each is an independent 24-hour cycle),
   - and the local clock time within that day (from 00:00 to 23:59).)

- **Is Workday Today?**: ${context.is_workday}
  - If this value is `True`, today is a **normal working weekday**.
  - If this value is `False`, today is a **weekend or official rest day**.
  - You must treat this flag as the **single source of truth** for whether today is a working day or a rest day.
    Do NOT guess from the simulation day index or from your own assumptions.
  - When it is a weekend (`False`), use the *weekend* portion of the Background Story
    (sentences such as "On weekends, she ...") as the main template for behavior.
  - When it is a workday (`True`), use the *weekday* routine as the main template.

- Current Location: ${context.current_position}
- Weather: ${context.weather} (Temperature: ${context.temperature})
- **Current Plan Target**: "${context.plan_target}"
- **Authorized Meal Type**: "${context.meal_type}" (Options: breakfast, lunch, dinner, snack, none)
- Recent Thought/Status: "${context.current_thought}"

================================================================
PART 3: PLANNING RULES (STRICTLY FOLLOW)
================================================================
Rule 0: [CRITICAL] CALENDAR MODE + OCCUPATION & TIME PROTOCOLS
   - **STEP 0: Calendar Mode from Context**
     - Read `${context.is_workday}`:
       - If `True`: today is a **working weekday**.
       - If `False`: today is a **weekend / official rest day**.
     - Never override this flag. Never infer weekday/weekend from the simulation day index.

   - **STEP 1: Classify Schedule Type from "${profile.occupation}"**
     - **Classification priority (must follow):**
       1) If occupation contains "disabled" or "partially disabled" -> Case B2
       2) Else if occupation contains "part-time" OR mixed label like "Part-time ...; Retired" -> Case A2
       3) Else if occupation indicates clear fixed-duty job/student -> Case A
       4) Else -> Case B

     - **Case A: FIXED / DUTY-BASED SCHEDULE**  
       This includes any occupation where a person normally has to show up at a workplace or follow fixed hours, e.g.:
       - "full-time employee", "office worker", "engineer", "teacher", "clerk",
         "cashier", "nurse", "doctor", "driver", "technician", "service staff", "receptionist",
         "manager", "assistant", "student", etc.
       - If it is unclear, you should **default to Case A** (assume they have a job with obligations).
       - Only treat as Case B if the occupation clearly says: "retired", "unemployed", "homemaker",
         "housewife/househusband", "full-time caregiver", "child not yet in school", etc.

       **Calendar rule for Case A:**
       - If `${context.is_workday}` is `True`, treat today as a **normal working weekday**.
       - If `${context.is_workday}` is `False`, treat today as a **weekend / rest day**:
         - By default the agent does **not** go to the workplace/school and does **not**
           follow a full 09:00–17:00 work shift.
         - They may still do short, optional job-related tasks at home (e.g., checking email)
           if this fits the Background Story, but commuting to the office or spending long
           continuous hours on job tasks is **forbidden** unless the Background Story explicitly
           says they have a specific weekend duty or shift **today**.
       - Each simulation day comes with its own `${context.is_workday}` value; do not infer weekday/weekend from
         the day index, and do not override this flag.

       **Time-based behavior for Case A on a working weekday (`${context.is_workday}` == True):**
       - **06:00 - 08:00 (Pre-work Morning)**:
         - Focus on waking up, hygiene, simple breakfast, and getting ready.
         - You **must not** schedule going back to bed or long naps.
       - **08:00 - 09:30 (Commute Window)**:
         - If Location is HOME (or not at workplace/school): you **MUST** plan "Commute to workplace/school".
           - FORBIDDEN in this window: "watch TV", "relax on sofa", "do house chores", "take a nap".
         - If already at workplace/school: stay there and prepare for work/study.
       - **09:30 - 12:00 (Morning Work Block)** and **13:00 - 17:00 (Afternoon Work Block)**:
         - If Location is NOT workplace/school: plan "Commute" immediately.
         - If Location is AT workplace/school:
           - **Stay there**. Plan realistic "Work/Study tasks" and **short breaks at the workplace**.
           - **Anti-Exit Lock**: If at Work/School and Time < 17:00,
             **DO NOT** plan "Go Home", "Leave early", or "spend the rest of the day at home".
         - During these windows, "rest" must be interpreted as:
           - Micro-break at the office (stand up, stretch, get water, short walk),
             **not** going home to sleep.
       - **12:00 - 13:00 (Lunch)**:
         - Plan lunch and light rest **near work**, not going home unless explicitly justified.
       - **After 17:00 (Off-work)**:
         - It becomes valid to plan "Go home", "Commute back", "Do groceries", "Cook dinner",
           "Meet friends", etc.
    
     - **Case A2: PART-TIME / SHIFT / MIXED STATUS (still has obligations, but not full-day)**
       Trigger examples in "${profile.occupation}":
       - contains "part-time", "shift", "casual", "contract", or mixed labels like "Part-time employment; Retired".
       - Default interpretation: they work SOME days or SOME hours, but not a full 09:00–17:00 block.

       **Calendar rule for Case A2:**
       - If `${context.is_workday}` is `True`:
         - The agent MAY have a work shift today, but it is typically 3–6 hours.
         - Choose ONE realistic shift window and stick to it (e.g., 09:00–13:00 OR 13:00–17:00),
           unless the Background Story explicitly states their shift.
         - Outside the shift window, treat them like Case B (errands, leisure, social, appointments).
       - If `${context.is_workday}` is `False`:
         - Treat as weekend/rest day (no mandatory commuting), unless Background Story explicitly says weekend duty.

       **Constraint note for Case A2:**
       - Do NOT apply the strong "Anti-Exit Lock" for the entire 09:30–17:00 period.
         Apply it ONLY during the chosen shift window if they are supposed to be at work.


     - **Case B: FLEXIBLE / NO FORMAL SCHEDULE**  
       (e.g., clearly Retired, Unemployed, Homemaker, etc.)
       - You are exempt from the strict 09:00–17:00 work lock.
       - You may follow the "Plan Target" more freely, while still respecting realistic time-of-day behavior
         (no "sleep all morning every day" unless illness is explicitly present).
    
     - **Case B2: LIMITED MOBILITY / HEALTH CONSTRAINT (e.g., disabled/partially disabled)**
       - The agent may need more rest and shorter trips, but should NOT be homebound by default.
       - Prefer short, low-effort outings (nearby grocery, short walk, pharmacy, clinic/therapy, visit family),
         with more breaks and slower pacing.


   - **STEP 2: General Time Checks (For All Agents)**
     - **06:00 - 11:00 (MORNING)**:
       - This is the period to be awake, start the day, have breakfast, commute,
         or do morning activities.
       - Strongly discourage: going back to bed for long naps, or staying in pyjamas for hours.
       - If you absolutely must schedule "rest" during this window (e.g. sickness),
         describe it as "sit and rest quietly" rather than full "sleep", and keep it short.
     - **12:00 - 17:00 (AFTERNOON)**:
       - No "night sleep". Do not describe actions as "go to bed for the night" in this window.

Rule 1: PLANNING GRANULARITY (ANTI-COMPRESSION)
   - **One Plan ≠ One Day**. Do NOT try to schedule the entire rest of the day in a single JSON response.
   - **Focus on the NOW**: Plan only for the next 1–3 hours based on the Current Plan Target and obligations.
   - **Forbidden phrases**: Do NOT use vague phrases like "spend the rest of the day doing X"
     or "for the whole day". Always break the day into smaller realistic segments.
   - **Example**:
     - If Target is "Work" and it is 10:00 AM, generate steps for *working* at the office.
       Do NOT append "Commute home" and "Eat Dinner" at the end.
       Wait until the simulation time actually moves close to evening before planning commute/dinner.

Rule 1.5: [REALISM] OUT-OF-HOME ANCHORS FOR NON-FULL-TIME AGENTS
  - Problem to avoid: For agents who are NOT full-time office-bound, the plan must not default to staying at HOME all day.
  - Applies to: Case B, Case B2, and Case A2 outside their shift window.

  - Default expectation (unless Background Story explicitly says homebound, illness, or severe weather):
    - On MOST days, include at least ONE short out-of-home episode during daytime (roughly 10:00–18:00),
      such as: grocery/pharmacy, park walk, cafe, library, community center, visiting family/friends,
      doctor/therapy appointment, volunteering, hobby class, religious/community activity.
    - On weekends, it is especially common to go out for leisure or social contact.

  - How to implement in short-horizon planning (next 1–3 hours):
    - If `Current Location` is HOME and current time is between 10:00–17:30,
      and the Plan Target is vague ("Relax", "Stay home", "Free time", "Household chores"):
        -> reinterpret it as "mostly at home BUT include a short outing soon",
           and plan a mobility step to a nearby place (park/shop/cafe) within the next 1–3 hours.
    - Keep trips realistic and short for B2 (e.g., 15–60 minutes outside + rest).

  - Diversity requirement:
    - Do not repeat the exact same outing every day; vary destinations and purposes across days.

Rule 2: [CRITICAL] REALITY OVERRIDES STORY AND DESIRE
   - The "Background Story" defines general habits, BUT "Current Reality" defines the **now**:
     - Current time window (morning/working hours/evening),
     - Current location,
     - Occupational duties from Rule 0,
     - And whether today is a workday (`${context.is_workday}` == True) or a weekend/rest day (`False`).
   - **Conflict Resolution Examples**:
     - If the Story says "She spends hours eating lunch" but the Current Time is 13:30 on a **working weekday**
       (`${context.is_workday}` == True) and Rule 0 requires Work → you MUST plan **Work at the office**, not more lunch.
     - If the high-level Plan Target says "Relax at home" but it is 10:30 on a **working weekday**
       (`${context.is_workday}` == True) and the agent
       is Case A (fixed schedule) and still not at work → you must ignore this desire and send them to work.
     - If `${context.is_workday}` is `False` (weekend), you must **not** force the agent to commute or work
       just because the Plan Target is vague. Prefer realistic weekend activities based on the Background Story
       (sleep a bit later, household chores, family time, leisure, etc.), while still respecting time-of-day logic.
   - **Loop Prevention**:
     - Check "Recent Thought". If the agent has *just* finished a meal, DO NOT schedule another full meal.
     - If they just "went to bed", do not immediately plan a new "prepare for bed" sequence.
   - For Case B / Case A2-off-shift:
      - If the Plan Target is generic and home-centered, you must still satisfy Rule 1.5 (out-of-home anchors),
       unless a strong constraint exists (illness, explicit homebound story, severe weather).


Rule 3: [ADAPTIVE] DAILY ROUTINE RESET (LONG-HORIZON CONSISTENCY)
   - **Treat each simulation day as a Fresh Realistic Day**:
     - Ignore any feeling of "I already worked yesterday so I deserve to rest all day".
     - Use `${context.is_workday}` to decide whether **today** is a working weekday or a weekend/rest day.
       Do not copy the previous day's status.
   - **No Weekly Compression by the LLM**:
     - Do NOT infer weekend/holiday status from the simulation day index.
     - Never override `${context.is_workday}` based on your own reasoning.
     - Across different days:
       - If `${context.is_workday}` is True, Case A agents should follow a normal workday pattern.
       - If `${context.is_workday}` is False, even Case A agents should **not** commute to work or
         run a full work shift (unless the Background Story explicitly states a specific duty on that day).

Rule 4: ADHERE TO PLAN TARGET **WITH WORK DISCIPLINE OVERRIDE**
   - In general, the detailed steps should help achieve the "${context.plan_target}".
   - However, **for Case A agents during working hours on a working weekday, JOB DUTIES OVERRIDE THE PLAN TARGET**.

   - **Work Discipline Override (strong version)**:
     - **Trigger Condition** (ALL must be true):
       1. Agent is **Case A (Fixed / Duty-based Schedule)**.
       2. Current Time is **08:00 - 16:30**.
       3. `${context.is_workday}` is **True** (today is a working weekday).
       4. The day is not explicitly described in the Background Story as vacation or public holiday.
     - **Action (when the above are satisfied)**:
       - Your first responsibility is to ensure the agent is commuting to or staying at the workplace/school
         and actually working/studying.
       - If the agent is **not at work/school**, you MUST ignore any non-work Plan Target
         (e.g., "Relax", "Sleep", "Clean house", "Stay home", "Watch TV") and instead:
         - Plan "Commute to workplace/school" and then "Start working/studying".
       - If the agent **is already at work/school**, you MUST:
         - Generate realistic work/study tasks and short on-site breaks.
         - Treat non-work Plan Targets as *micro-adjustments* at the workplace (e.g., stretch, get coffee),
           not as reasons to go home or sleep.
     - **On weekends (`${context.is_workday}` == False)**:
       - This override is **disabled**.
       - You must NOT automatically send the agent to work or school.
       - Even if the Plan Target or Background Story mentions "work", interpret it as
         short, optional tasks (ideally at home) rather than a full 09:00–17:00 shift.
       - For Case B / Case A2-off-shift on weekends:
        - Prefer at least one optional outing (walk/visit/leisure/errands) during daytime per Rule 1.5.
     - **Work Discipline Override (Case A2 shift version)**:
      - If the agent is Case A2 AND current time is within the chosen shift window on a workday:
       - Apply the same commute/work enforcement as Case A.
      - If the agent is Case A2 AND current time is outside the shift window:
       - Do NOT enforce workplace stay; treat as flexible and satisfy Rule 1.5 when appropriate.



Rule 5: EATING & MEAL LOGIC
   - Use "${context.meal_type}" to decide the allowed meal:
     - "breakfast", "lunch", "dinner" = main meals.
     - "snack" = only light food, not a full meal.
     - "none" = do not start a new eating episode unless there is a very strong reason.
   - Time constraints:
     - No Lunch after 15:00.
     - No Dinner before 17:00.
   - Location:
     - If at work/school, eat at "canteen", "office kitchen", or "nearby restaurant".
       Do NOT go home just for lunch unless the Background Story explicitly says so.

Rule 6: SLEEP & NAP MAINTENANCE
   - **Night-time (22:00–06:00)**:
     - When the agent has already started night sleep:
       - Generate ONLY ONE step such as "Continue sleeping soundly until morning".
       - DO NOT generate repeated cycles of "get up / walk around / go back to bed" during night.
     - Only when first switching to night sleep (typically after 21:00) should you generate
       steps like "prepare for bed", "change into pyjamas", "lie down and fall asleep".
   - **Daytime naps (for Case A on weekdays)**:
     - Short naps are allowed only around lunch break (roughly 12:00–14:00) and should be brief,
       preferably at home on weekends or quietly at the workplace on weekdays.
     - You must NOT schedule long "go back to bed and sleep for hours" naps at 09:00, 10:00, 15:00, etc.

Rule 7: REALISTIC MOVEMENT
   - For any location change, you must include at least one step with type "mobility".
   - Do not teleport. Clearly describe how the agent moves (walk, bus, tram, car, bike, etc.).
   - Max steps allowed in this plan: ${context.max_plan_steps}.

Rule 8: STEP TYPES
   - "mobility": Moving between places (walk, bus, tram, car, bike).
   - "social": Talking, calling, texting, meeting people.
   - "economy": Working, shopping, financial or job-related tasks.
   - "other": Eating, sleeping, relaxing, hygiene, entertainment, household chores.

================================================================
PART 4: OUTPUT FORMAT
================================================================
Respond ONLY in valid JSON format. Do not add markdown or conversational text.

Example Structure:
{{
    "plan": {{
        "target": "Commute to work (Auto-Override due to Work Hours)",
        "steps": [
            {{
                "intention": "Walk from home to bus station",
                "type": "mobility"
            }},
            {{
                "intention": "Take bus to office",
                "type": "mobility"
            }}
        ]
    }}
}}
"""




NEED_INITIALIZATION_PROMPT = """
You are an intelligent agent satisfaction initialization system. Based on the profile information below, please initialize the agent's satisfaction levels and related parameters.

Profile Information:
- Gender: ${profile.gender}
- Education Level: ${profile.education}
- Consumption Level: ${profile.consumption}
- Occupation: ${profile.occupation}
- Age: ${profile.age}
- Monthly Income: ${profile.income}

Current Time: ${context.current_time}

Your task:
Using the profile and current time, set realistic initial satisfaction levels for a normal adult with this background. Use a 0–1 float scale where:
- 0.0 means extremely unsatisfied,
- 0.5 means neutral / moderate,
- 1.0 means fully satisfied.

General rules:
- In normal situations, values should usually stay between 0.3 and 0.9.
- Only use values below 0.3 or above 0.9 when the text clearly describes extreme states (for example, very hungry, exhausted, very unsafe).
- Make sure the four needs are mutually consistent with the daily routine implied by the profile.

Guidelines for each need:

1) hunger_satisfaction
- Interpret ${context.current_time} as local time.
- For a typical working adult on a normal weekday morning (for example between 07:00 and 10:00) with no explicit description of food shortage, skipped meals or night shifts:
  - Assume they have already eaten breakfast or will very soon.
  - hunger_satisfaction in this case should usually be between 0.6 and 0.9.
  - DO NOT set hunger_satisfaction below 0.5 in this situation.
- Only set hunger_satisfaction below 0.4 if the profile or background story clearly suggests that the agent often skips meals, is currently hungry, or has not eaten since the previous day.
- Right after a main meal (breakfast, lunch or dinner), typical values are 0.8–1.0.
- For people who eat at regular times, hunger_satisfaction should start relatively high at the beginning of the workday and decrease gradually as time passes until the next meal.

2) energy_satisfaction
- After a normal night of sleep and at the beginning of the morning, energy_satisfaction should usually be between 0.6 and 0.9, unless the profile mentions chronic fatigue, illness or very poor sleep.
- Late at night, close to bedtime, energy_satisfaction should be lower (for example 0.2–0.5).
- For older adults or people with heavy physical jobs, you may use slightly lower values to reflect easier tiredness, but still avoid extreme values without a clear reason.

3) safety_satisfaction
- People with higher income and stable housing can have higher safety_satisfaction (for example 0.7–0.9).
- People with low income, unstable jobs or unsafe living conditions can have lower values (for example 0.3–0.6).
- Only use extremely low values (below 0.3) if the description clearly indicates danger, violence or extreme instability.

4) social_satisfaction
- Consider whether the profile suggests rich family / social connections or loneliness.
- People living with partners or family and having normal social contacts can have moderate to high social_satisfaction (0.6–0.9).
- People living alone with few contacts may start lower (0.3–0.6).

Return format:
Please initialize the agent's satisfaction levels and parameters based on the profile above. Return ONLY a JSON object with the following structure:

{{
  "current_satisfaction": {{
    "hunger_satisfaction": 0.8,
    "energy_satisfaction": 0.7,
    "safety_satisfaction": 0.8,
    "social_satisfaction": 0.6
  }}
}}

Do not add explanations, comments or extra keys. Respond only with JSON.
"""





society_params = {
    "enable_cognition": True,
    "max_plan_steps": 6,
    "plan_generation_prompt": PLAN_GENERATION_PROMPT,
    "need_initialization_prompt": NEED_INITIALIZATION_PROMPT,
}


llm_config = LLMConfig(
    provider="deepseek",
    api_key="YOUR_API_KEY",
    model="deepseek-chat",
    concurrency=200,
    timeout=60,
)

env_config = EnvConfig(
    db=DatabaseConfig(
        enabled=True,
        db_type="sqlite",
    ),
    home_dir="../agentsociety_data",
)

map_config = MapConfig(
    file_path="../data/map_with_poi_fixed2.pb",
)

agents_config = AgentsConfig(
    citizens=[
        AgentConfig(
            agent_class=EnergyAgent,
            number=500,
            memory_config_func=EnergyAgent.with_energy_memory_config,
            memory_from_file="agentsV3.json",
            agent_params=society_params,   
            blocks={
                MobilityBlock: {},   
                EconomyBlock: {},    
                SocialBlock: {},     
                OtherBlock: {},  
            },           
        )
    ],
)

exp_config = ExpConfig(
    name="Test1_500AgentWork",
    workflow=[
        WorkflowStepConfig(
               type=WorkflowType.ENVIRONMENT_INTERVENE,
               key="workday",
               value=True,
           ),
        WorkflowStepConfig(
            type=WorkflowType.STEP,
            steps=288,
            ticks_per_step=600,
        ),
    ],
    environment=EnvironmentConfig(
        start_tick=8 * 60 * 60,
    ),
)

config = Config(
    llm=[llm_config],
    env=env_config,
    map=map_config,
    agents=agents_config,
    exp=exp_config,
)

config = default(config)

def ensure_sim_binary() -> None:
    """
    Ensure that the simulator binary (agentsociety-sim-oss) exists
    for the current platform (macOS on laptop, Linux on RCP).
    It downloads the correct binary into env_config.home_dir if needed.
    """

    home_dir = Path(env_config.home_dir).resolve()
    home_dir.mkdir(parents=True, exist_ok=True)
    # This will download the proper binary for the current OS into home_dir
    download_binary(str(home_dir))


async def main():
    ensure_sim_binary()

    society = AgentSociety.create(config)

    try:
        await society.init()
        await society.run()
    finally:
        await society.close()


if __name__ == "__main__":
    asyncio.run(main())
