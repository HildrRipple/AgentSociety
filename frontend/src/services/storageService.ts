import localforage from 'localforage';

// 初始化 localForage
localforage.config({
    name: 'agentsociety',
    storeName: 'configurations',
    description: 'Agent Society Configuration Storage'
});

// 存储键名
export const STORAGE_KEYS = {
    ENVIRONMENTS: 'environments',
    MAPS: 'maps',
    AGENTS: 'agents',
    WORKFLOWS: 'workflows',
};

// 配置项接口
export interface ConfigItem {
    id: string;
    name: string;
    description?: string;
    createdAt: string;
    updatedAt: string;
    config: Record<string, unknown>;
}

// 保存配置列表
export const saveConfigs = async <T extends ConfigItem>(key: string, configs: T[]): Promise<void> => {
    try {
        await localforage.setItem(key, configs);
        console.log(`Saved ${configs.length} items to ${key}`);
    } catch (error) {
        console.error(`Error saving to ${key}:`, error);
        throw error;
    }
};

// 获取配置列表
export const getConfigs = async <T extends ConfigItem>(key: string): Promise<T[]> => {
    try {
        const configs = await localforage.getItem<T[]>(key);
        return configs || [];
    } catch (error) {
        console.error(`Error getting from ${key}:`, error);
        return [];
    }
};

// 添加或更新单个配置
export const saveConfig = async <T extends ConfigItem>(key: string, config: T): Promise<void> => {
    try {
        const configs = await getConfigs<T>(key);
        const index = configs.findIndex(item => item.id === config.id);

        if (index >= 0) {
            // 更新现有配置
            configs[index] = {
                ...config,
                updatedAt: new Date().toISOString()
            };
        } else {
            // 添加新配置
            configs.push({
                ...config,
                createdAt: config.createdAt || new Date().toISOString(),
                updatedAt: new Date().toISOString()
            });
        }

        await saveConfigs(key, configs);
    } catch (error) {
        console.error(`Error saving config to ${key}:`, error);
        throw error;
    }
};

// 删除单个配置
export const deleteConfig = async <T extends ConfigItem>(key: string, id: string): Promise<void> => {
    try {
        const configs = await getConfigs<T>(key);
        const filteredConfigs = configs.filter(config => config.id !== id);
        await saveConfigs(key, filteredConfigs);
    } catch (error) {
        console.error(`Error deleting config from ${key}:`, error);
        throw error;
    }
};

// 清除所有配置
export const clearAllConfigs = async (): Promise<void> => {
    try {
        await localforage.clear();
        console.log('All configurations cleared');
    } catch (error) {
        console.error('Error clearing configurations:', error);
        throw error;
    }
};

// 初始化示例数据（仅在首次使用时）
export const initializeExampleData = async (): Promise<void> => {
    try {
        // 分别检查并初始化每个部分
        const environments = await getConfigs(STORAGE_KEYS.ENVIRONMENTS);
        const maps = await getConfigs(STORAGE_KEYS.MAPS);
        const agents = await getConfigs(STORAGE_KEYS.AGENTS);
        const workflows = await getConfigs(STORAGE_KEYS.WORKFLOWS);

        // 环境示例数据
        if (environments.length === 0) {
            const exampleEnvironments: ConfigItem[] = [
                {
                    id: '1',
                    name: 'Default Environment',
                    description: 'Default Configuration',
                    createdAt: new Date().toISOString(),
                    updatedAt: new Date().toISOString(),
                    config: {
                        llm_request: {
                            request_type: 'zhipuai',
                            model: 'GLM-4-Flash'
                        },
                        simulator_request: {
                            task_name: 'citysim',
                            max_day: 1
                        }
                    }
                },
            ];
            await saveConfigs(STORAGE_KEYS.ENVIRONMENTS, exampleEnvironments);
            console.log('Initialized environment data');
        }

        // 地图示例数据
        if (maps.length === 0) {
            const exampleMaps: ConfigItem[] = [
                {
                    id: '1',
                    name: 'Beijing Map',
                    description: 'Map of Beijing city center',
                    createdAt: new Date().toISOString(),
                    updatedAt: new Date().toISOString(),
                    config: {
                        filePath: 'data/beijing_map.pb',
                        fileSize: 1024000,
                        fileType: 'pb'
                    }
                },
                {
                    id: '2',
                    name: 'New York Map',
                    description: 'Map of New York city center',
                    createdAt: new Date().toISOString(),
                    updatedAt: new Date().toISOString(),
                    config: {
                        filePath: 'data/newyork_map.pb',
                        fileSize: 1536000,
                        fileType: 'pb'
                    }
                }
            ];
            await saveConfigs(STORAGE_KEYS.MAPS, exampleMaps);
            console.log('Initialized maps data');
        }

        // 智能体示例数据
        if (agents.length === 0) {
            const exampleAgents: ConfigItem[] = [
                {
                    id: '1',
                    name: 'Default Citizen Agent',
                    description: 'Standard citizen agent configuration',
                    createdAt: new Date().toISOString(),
                    updatedAt: new Date().toISOString(),
                    config: {
                        agent_config: {
                            number_of_citizen: 100
                        },
                        agentType: 'llm',
                        profile: {
                            name: 'random',
                            gender: 'equal',
                            age: { min: 18, max: 65 }
                        }
                    }
                },
            ];
            await saveConfigs(STORAGE_KEYS.AGENTS, exampleAgents);
            console.log('Initialized agents data');
        }

        // 工作流示例数据
        if (workflows.length === 0) {
            const exampleWorkflows: ConfigItem[] = [
                {
                    id: '1',
                    name: 'Workflow Test',
                    description: 'Simulation Workflow Template',
                    createdAt: new Date().toISOString(),
                    updatedAt: new Date().toISOString(),
                    config: {
                        experimentName: 'City Simulation',
                        runMode: 'fast',
                        timeScale: 10,
                        maxSteps: 1000,
                        workflow: [
                            { type: 'run', days: 1 }
                        ]
                    }
                },
            ];
            await saveConfigs(STORAGE_KEYS.WORKFLOWS, exampleWorkflows);
            console.log('Initialized workflows data');
        }

    } catch (error) {
        console.error('Error initializing example data:', error);
    }
};

// 导出默认对象
const storageService = {
    saveConfigs,
    getConfigs,
    saveConfig,
    deleteConfig,
    clearAllConfigs,
    initializeExampleData,
};

export default storageService; 