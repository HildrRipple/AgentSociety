from enum import Enum

class WorkflowType(str, Enum):
    """
    Defines the types of workflow steps in the simulation.
    - **Description**:
        - Enumerates different types of workflow steps that can be executed during simulation.

    - **Types**:
        - `STEP`: Execute on a step-by-step unit.
        - `RUN`: Execute on a daily unit (day-based execution).
        - `INTERVIEW`: Sends an interview message to the specified agent.
        - `SURVEY`: Sends a questionnaire to the specified agent.
        - `ENVIRONMENT_INTERVENE`: Changes the environment variables (global prompt).
        - `UPDATE_STATE_INTERVENE`: Directly updates the state information of the specified agent.
        - `MESSAGE_INTERVENE`: Influences the agent's behavior and state by sending a message.
        - `INTERVENE`: Represents other intervention methods driven by code.
        - `FUNCTION`: Represents function-based intervention methods.
    """
    STEP = "step"
    RUN = "run"
    INTERVIEW = "interview"
    SURVEY = "survey"
    ENVIRONMENT_INTERVENE = "environment"
    UPDATE_STATE_INTERVENE = "update_state"
    MESSAGE_INTERVENE = "message"
    INTERVENE = "other"
    FUNCTION = "function"


class LLMProviderType(str, Enum):
    """
    Defines the types of LLM providers.
    - **Description**:
        - Enumerates different types of LLM providers.

    - **Types**:
        - `OPENAI`: OpenAI and compatible providers (based on base_url).
        - `DEEPSEEK`: DeepSeek.
        - `QWEN`: Qwen.
        - `ZHIPU`: Zhipu.
        - `SILICONFLOW`: SiliconFlow.
        - `VLLM`: VLLM.
    """
    OpenAI = "openai"
    DeepSeek = "deepseek"
    Qwen = "qwen"
    ZhipuAI = "zhipuai"
    SiliconFlow = "siliconflow"
    VLLM = "vllm"


class DistributionType(str, Enum):
    """
    Defines the types of distribution types.
    - **Description**:
        - Enumerates different types of distribution types.

    - **Types**:
        - `CHOICE`: Choice distribution.
        - `UNIFORM_INT`: Uniform integer distribution.
        - `UNIFORM_FLOAT`: Uniform float distribution.
        - `NORMAL`: Normal distribution.
        - `CONSTANT`: Constant distribution.
    """
    CHOICE = "choice"
    UNIFORM_INT = "uniform_int"
    UNIFORM_FLOAT = "uniform_float"
    NORMAL = "normal"
    CONSTANT = "constant"


class MetricType(str, Enum):
    """
    Defines the types of metric types.
    - **Description**:
        - Enumerates different types of metric types.

    - **Types**:
        - `FUNCTION`: Function-based metric.
        - `STATE`: State-based metric.
    """
    FUNCTION = "function"
    STATE = "state"
