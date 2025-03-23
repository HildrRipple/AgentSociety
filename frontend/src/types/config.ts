/**
 * Configuration type definitions for AgentSociety
 * These types match the backend configuration structures
 */

import { LLMProviderType, WorkflowType, MetricType, DistributionType } from '../utils/enums';

// Simulator Configuration Types
export interface LLMConfig {
  provider: LLMProviderType;
  base_url?: string;
  api_key: string;
  model: string;
}

export interface RedisConfig {
  server: string;
  port: number;
  password?: string;
  db: string;
}

export interface SimulatorConfig {
  task_name: string;
  max_day: number;
  start_step: number;
  total_step: number;
  log_dir: string;
  steps_per_simulation_step: number;
  steps_per_simulation_day: number;
  primary_node_ip: string;
}

export interface MapConfig {
  file_path: string;
  cache_path?: string;
}

export interface MlflowConfig {
  username?: string;
  password?: string;
  mlflow_uri: string;
}

export interface PostgreSQLConfig {
  enabled?: boolean;
  dsn: string;
}

export interface AvroConfig {
  enabled?: boolean;
  path: string;
}

export interface MetricConfig {
  mlflow?: MlflowConfig;
}

export interface SimStatus {
  simulator_activated: boolean;
}

export interface SimConfig {
  llm_configs: LLMConfig[];
  simulator_config?: SimulatorConfig;
  redis?: RedisConfig;
  map_config?: MapConfig;
  metric_config?: MetricConfig;
  pgsql?: PostgreSQLConfig;
  avro?: AvroConfig;
  simulator_server_address?: string;
  status?: SimStatus;
}

// Experiment Configuration Types
export interface WorkflowStep {
  type: WorkflowType;
  func?: any;
  days: number;
  times: number;
  target_agent?: any[];
  interview_message?: string;
  survey?: any;
  key?: string;
  value?: any;
  intervene_message?: string;
  description: string;
}

export interface MetricExtractor {
  type: MetricType;
  func?: any;
  step_interval: number;
  target_agent?: any[];
  key?: string;
  method?: 'mean' | 'sum' | 'max' | 'min';
  extract_time: number;
  description: string;
}

export interface DistributionConfig {
  dist_type: DistributionType;
  choices?: any[];
  weights?: number[];
  min_value?: number;
  max_value?: number;
  mean?: number;
  std?: number;
  value?: any;
}

export interface MemoryConfig {
  memory_config_func?: Record<string, any>;
  memory_from_file?: Record<string, string>;
  memory_distributions?: Record<string, DistributionConfig>;
}

export interface AgentConfig {
  number_of_citizen: number;
  number_of_firm: number;
  number_of_government: number;
  number_of_bank: number;
  number_of_nbs: number;
  group_size: number;
  embedding_model?: any;
  extra_agent_class?: Record<string, number>;
  agent_class_configs?: Record<string, Record<string, any>>;
  memory_config?: MemoryConfig;
  init_func?: any[];
}

export interface EnvironmentConfig {
  weather: string;
  temperature: string;
  workday: boolean;
  other_information: string;
}

export interface MessageInterceptConfig {
  mode?: 'point' | 'edge';
  max_violation_time: number;
  message_interceptor_blocks?: any[];
  message_listener?: any;
}

export interface ExpConfig {
  exp_name: string;
  llm_semaphore: number;
  logging_level: number;
  agent_config?: AgentConfig;
  environment?: EnvironmentConfig;
  message_intercept?: MessageInterceptConfig;
  metric_extractors?: MetricExtractor[];
  workflow?: WorkflowStep[];
}

// Combined configuration for API requests
export interface ExperimentRequestConfig {
  sim_config: SimConfig;
  exp_config: ExpConfig;
} 