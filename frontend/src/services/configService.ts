/**
 * Service for handling configuration operations
 */

import { SimConfig, ExpConfig, ExperimentRequestConfig, LLMConfig, AgentConfig, MapConfig, SimulatorConfig, RedisConfig, PostgreSQLConfig, AvroConfig, EnvironmentConfig, MessageInterceptConfig } from '../types/config';
import { LLMProviderType, WorkflowType } from '../utils/enums';
import storageService, { STORAGE_KEYS, ConfigItem } from './storageService';

class ConfigService {
  /**
   * Builds a complete experiment configuration from selected components
   */
  async buildExperimentConfig(
    environmentId: string,
    agentId: string,
    workflowId: string,
    mapId: string,
    experimentName: string
  ): Promise<ExperimentRequestConfig | null> {
    try {
      // Load all required configurations
      const environments = await storageService.getConfigs<ConfigItem>(STORAGE_KEYS.ENVIRONMENTS);
      const agents = await storageService.getConfigs<ConfigItem>(STORAGE_KEYS.AGENTS);
      const workflows = await storageService.getConfigs<ConfigItem>(STORAGE_KEYS.WORKFLOWS);
      const maps = await storageService.getConfigs<ConfigItem>(STORAGE_KEYS.MAPS);
      
      // Find selected configurations
      const environment = environments.find(env => env.id === environmentId);
      const agent = agents.find(a => a.id === agentId);
      const workflow = workflows.find(w => w.id === workflowId);
      const map = maps.find(m => m.id === mapId);
      
      if (!environment || !agent || !workflow || !map) {
        console.error('One or more required configurations not found');
        return null;
      }
      
      // Build simulator configuration
      const simConfig: SimConfig = {
        llm_configs: (environment.config.llm_configs || []) as LLMConfig[],
        simulator_config: (environment.config.simulator_config || {
          task_name: "citysim",
          max_day: 1000,
          start_step: 28800,
          total_step: 86400,
          log_dir: "./logs",
          steps_per_simulation_step: 1,
          steps_per_simulation_day: 86400,
          primary_node_ip: "localhost"
        }) as SimulatorConfig,
        redis: (environment.config.redis || {
          server: "localhost",
          port: 6379,
          db: "0"
        }) as RedisConfig,
        map_config: {
          file_path: map.config.file_path as string,
          cache_path: map.config.cache_path as string
        },
        metric_config: environment.config.metric_config || {
          mlflow: {
            mlflow_uri: "http://localhost:5000"
          }
        },
        pgsql: (environment.config.pgsql || {
          enabled: true,
          dsn: "postgresql://postgres:postgres@localhost:5432/agentsociety"
        }) as PostgreSQLConfig,
        avro: (environment.config.avro || {
          enabled: false,
          path: "./output/avro"
        }) as AvroConfig,
        simulator_server_address: environment.config.simulator_server_address as string || "localhost:50051"
      };
      
      // Build experiment configuration
      const expConfig: ExpConfig = {
        exp_name: experimentName || workflow.name,
        llm_semaphore: (workflow.config.llm_semaphore as number) || 200,
        logging_level: (workflow.config.logging_level as number) || 20,
        agent_config: agent.config.agent_config as AgentConfig || {
          number_of_citizen: 10,
          number_of_firm: 5,
          number_of_government: 1,
          number_of_bank: 1,
          number_of_nbs: 0,
          group_size: 100
        },
        environment: (workflow.config.environment || {
          weather: "The weather is normal",
          temperature: "The temperature is normal",
          workday: true,
          other_information: ""
        }) as EnvironmentConfig,
        message_intercept: (workflow.config.message_intercept || {
          max_violation_time: 3
        }) as MessageInterceptConfig,
        metric_extractors: (workflow.config.metric_extractors || []) as any[],
        workflow: (workflow.config.workflow || []) as any[]
      };
      
      return {
        sim_config: simConfig,
        exp_config: expConfig
      };
    } catch (error) {
      console.error('Error building experiment configuration:', error);
      return null;
    }
  }
  
  /**
   * Validates a configuration object against required fields
   */
  validateConfig(config: any, requiredFields: string[]): boolean {
    for (const field of requiredFields) {
      if (config[field] === undefined || config[field] === null) {
        return false;
      }
    }
    return true;
  }
  
  /**
   * Returns default configurations for new items
   */
  getDefaultConfigs() {
    return {
      environment: {
        llm_configs: [{
          provider: LLMProviderType.OPENAI,
          api_key: "",
          model: "gpt-4o"
        }],
        simulator_config: {
          task_name: "citysim",
          max_day: 1000,
          start_step: 28800,
          total_step: 86400,
          log_dir: "./logs",
          steps_per_simulation_step: 1,
          steps_per_simulation_day: 86400,
          primary_node_ip: "localhost"
        },
        redis: {
          server: "localhost",
          port: 6379,
          db: "0"
        },
        metric_config: {
          mlflow: {
            mlflow_uri: "http://localhost:5000"
          }
        },
        pgsql: {
          enabled: true,
          dsn: "postgresql://postgres:postgres@localhost:5432/agentsociety"
        },
        avro: {
          enabled: false,
          path: "./output/avro"
        },
        simulator_server_address: "localhost:50051"
      },
      agent: {
        number_of_citizen: 10,
        number_of_firm: 5,
        number_of_government: 1,
        number_of_bank: 1,
        number_of_nbs: 0,
        group_size: 100
      },
      workflow: {
        llm_semaphore: 200,
        logging_level: 20,
        environment: {
          weather: "The weather is normal",
          temperature: "The temperature is normal",
          workday: true,
          other_information: ""
        },
        message_intercept: {
          max_violation_time: 3
        },
        workflow: [{
          type: WorkflowType.RUN,
          days: 1.0,
          times: 1,
          description: "Run simulation for 1 day"
        }]
      },
      map: {
        file_path: './maps/default_map.pb',
        cache_path: './maps/cache/default_map.cache'
      }
    };
  }
}

export default new ConfigService(); 