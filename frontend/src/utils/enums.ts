/**
 * Enums used in the application
 */

export enum LLMProviderType {
  OPENAI = 'openai',
  DEEPSEEK = 'deepseek',
  QWEN = 'qwen',
  ZHIPUAI = 'zhipuai',
  SILICONFLOW = 'siliconflow'
}

export enum WorkflowType {
  RUN = 'run',
  FUNCTION = 'function',
  INTERVIEW = 'interview',
  SURVEY = 'survey',
  ENVIRONMENT_INTERVENE = 'environment_intervene',
  UPDATE_STATE_INTERVENE = 'update_state_intervene',
  MESSAGE_INTERVENE = 'message_intervene',
  INTERVENE = 'intervene'
}

export enum MetricType {
  FUNCTION = 'function',
  STATE = 'state'
}

export enum DistributionType {
  CHOICE = 'choice',
  UNIFORM_INT = 'uniform_int',
  UNIFORM_FLOAT = 'uniform_float',
  NORMAL = 'normal',
  CONSTANT = 'constant'
} 