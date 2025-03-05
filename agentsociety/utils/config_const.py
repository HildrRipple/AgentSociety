from enum import Enum

class WorkflowType(str, Enum):
    STEP = "step"
    RUN = "run"
    INTERVIEW = "interview"
    SURVEY = "survey"
    ENVIRONMENT_INTERVENE = "environment"
    UPDATE_STATE_INTERVENE = "update_state"
    MESSAGE_INTERVENE = "message"
    INTERVENE = "other"
    FUNCTION = "function"


class LLMRequestType(str, Enum):
    OpenAI = "openai"
    DeepSeek = "deepseek"
    Qwen = "qwen"
    ZhipuAI = "zhipuai"
    SiliconFlow = "siliconflow"


class DistributionType(str, Enum):
    CHOICE = "choice"
    UNIFORM_INT = "uniform_int"
    UNIFORM_FLOAT = "uniform_float"
    NORMAL = "normal"
    CONSTANT = "constant"


class MetricType(str, Enum):
    FUNCTION = "function"
    STATE = "state"
