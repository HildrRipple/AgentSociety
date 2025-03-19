import React, { useState, useEffect } from 'react';
import { Card, Button, Select, Space, Typography, Divider, message, Row, Col, Spin } from 'antd';
import { useNavigate } from 'react-router-dom';
import { ExperimentOutlined, EnvironmentOutlined, TeamOutlined, GlobalOutlined, RocketOutlined, NodeIndexOutlined } from '@ant-design/icons';
import storageService, { STORAGE_KEYS, ConfigItem } from '../../services/storageService';

const { Text } = Typography;
const { Option } = Select;

const CreateExperiment: React.FC = () => {
  const [environments, setEnvironments] = useState<ConfigItem[]>([]);
  const [agents, setAgents] = useState<ConfigItem[]>([]);
  const [workflows, setWorkflows] = useState<ConfigItem[]>([]);
  const [maps, setMaps] = useState<ConfigItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedEnvironment, setSelectedEnvironment] = useState<string>('');
  const [selectedAgent, setSelectedAgent] = useState<string>('');
  const [selectedWorkflow, setSelectedWorkflow] = useState<string>('');
  const [selectedMap, setSelectedMap] = useState<string>('');
  const [experimentRunning, setExperimentRunning] = useState(false);
  const [experimentId, setExperimentId] = useState<string | null>(null);
  const [statusCheckInterval, setStatusCheckInterval] = useState<NodeJS.Timeout | null>(null);
  const [experimentStatus, setExperimentStatus] = useState<string | null>(null);
  const navigate = useNavigate();

  // 加载所有配置
  useEffect(() => {
    const loadConfigurations = async () => {
      setLoading(true);
      try {
        // 确保示例数据已初始化
        await storageService.initializeExampleData();
        
        // 加载所有配置
        const envs = await storageService.getConfigs<ConfigItem>(STORAGE_KEYS.ENVIRONMENTS);
        const agts = await storageService.getConfigs<ConfigItem>(STORAGE_KEYS.AGENTS);
        const wkfs = await storageService.getConfigs<ConfigItem>(STORAGE_KEYS.WORKFLOWS);
        const mps = await storageService.getConfigs<ConfigItem>(STORAGE_KEYS.MAPS);
        
        setEnvironments(envs);
        setAgents(agts);
        setWorkflows(wkfs);
        setMaps(mps);
      } catch (error) {
        message.error('Failed to load configurations');
        console.error(error);
      } finally {
        setLoading(false);
      }
    };
    
    loadConfigurations();
  }, []);

  // 清理定时器
  useEffect(() => {
    return () => {
      if (statusCheckInterval) {
        clearInterval(statusCheckInterval);
      }
    };
  }, [statusCheckInterval]);

  // 检查实验状态
  const checkExperimentStatus = async () => {
    if (!experimentId) return;
    
    try {
      const response = await fetch(`/api/experiments/${experimentId}/status`);
      if (!response.ok) {
        throw new Error(`Failed to get experiment status: ${response.statusText}`);
      }
      
      const data = await response.json();
      const status = data.data.status;
      
      setExperimentStatus(status);
      
      if (status !== 'running') {
        // 实验已完成或失败，停止检查
        if (statusCheckInterval) {
          clearInterval(statusCheckInterval);
          setStatusCheckInterval(null);
        }
        
        if (status === 'completed') {
          message.success('Experiment completed successfully');
        } else if (status === 'failed') {
          message.error(`Experiment failed with return code ${data.data.returncode}`);
        }
        
        setExperimentRunning(false);
      }
    } catch (error) {
      console.error('Error checking experiment status:', error);
    }
  };

  const handleStartExperiment = async () => {
    if (!selectedEnvironment || !selectedAgent || !selectedWorkflow || !selectedMap) {
      message.error('请选择所有必需的配置');
      return;
    }
    
    setLoading(true);
    try {
      // 获取所有选中的配置详情
      const environment = environments.find(env => env.id === selectedEnvironment);
      const agent = agents.find(a => a.id === selectedAgent);
      const workflow = workflows.find(w => w.id === selectedWorkflow);
      const map = maps.find(m => m.id === selectedMap);
      
      if (!environment || !agent || !workflow || !map) {
        throw new Error('找不到选定的配置');
      }
      
      // 构建后端API所需的配置格式
      // 环境配置对应SimConfig
      const environmentConfig = {
        llm_config: environment.config.llm_config || {
          provider: "openai",
          api_key: "",
          model: "gpt-3.5-turbo"
        },
        simulator_config: environment.config.simulator_config || {
          task_name: "citysim",
          max_day: 1000,
          start_step: 28800,
          total_step: 24 * 60 * 60 * 365,
          log_dir: "./log",
          steps_per_simulation_step: 300,
          steps_per_simulation_day: 3600,
          primary_node_ip: "localhost"
        },
        redis: environment.config.redis,
        map_config: {
          file_path: map.config.file_path || "./map.pb"
        },
        metric_config: environment.config.metric_config,
        pgsql: environment.config.pgsql,
        avro: environment.config.avro,
        simulator_server_address: environment.config.simulator_server_address
      };
      
      // 实验配置对应ExpConfig
      const experimentConfig = {
        agent_config: {
          ...agent.config.agent_config,
          memory_config: agent.config.memory_config
        },
        workflow: workflow.config.workflow || [],
        environment: {
          weather: workflow.config.environment?.weather || "天气正常",
          temperature: workflow.config.environment?.temperature || "温度正常",
          workday: workflow.config.environment?.workday !== undefined ? workflow.config.environment.workday : true,
          other_information: workflow.config.environment?.other_information || ""
        },
        message_intercept: workflow.config.message_intercept,
        metric_extractors: workflow.config.metric_extractors || [],
        llm_semaphore: workflow.config.llm_semaphore || 200
      };
      
      // 发送请求到后端API
      const response = await fetch('/api/run-experiment', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name: `${workflow.name} with ${agent.name} in ${environment.name}`,
          environment: environmentConfig,
          agent: experimentConfig.agent_config,
          workflow: experimentConfig,
          map: map.config
        }),
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || '启动实验失败');
      }
      
      const result = await response.json();
      const expId = result.data.id;
      
      // 设置实验状态
      setExperimentId(expId);
      setExperimentRunning(true);
      setExperimentStatus('running');
      message.success('实验启动成功');
      
      // 设置定时检查实验状态
      const interval = setInterval(() => checkExperimentStatus(), 5000);
      setStatusCheckInterval(interval);
      
    } catch (error) {
      console.error('启动实验时出错:', error);
      message.error(`启动实验失败: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleStopExperiment = async () => {
    if (!experimentId) {
      return;
    }
    
    setLoading(true);
    try {
      const response = await fetch(`/api/experiments/${experimentId}/stop`, {
        method: 'DELETE',
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || 'Failed to stop experiment');
      }
      
      message.success('Experiment stopped successfully');
      
      // 清理定时器并重置状态
      if (statusCheckInterval) {
        clearInterval(statusCheckInterval);
        setStatusCheckInterval(null);
      }
      
      setExperimentRunning(false);
      setExperimentStatus('stopped');
      
    } catch (error) {
      console.error('Error stopping experiment:', error);
      message.error(`Failed to stop experiment: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateNew = (type: string) => {
    switch (type) {
      case 'environment':
        navigate('/environments');
        break;
      case 'agent':
        navigate('/agents');
        break;
      case 'workflow':
        navigate('/experiments');
        break;
      case 'map':
        navigate('/maps');
        break;
      default:
        break;
    }
  };

  // 自定义下拉框选项渲染
  const renderOptionContent = (item: ConfigItem) => (
    <Space direction="vertical" style={{ width: '100%' }}>
      <Text strong>{item.name}</Text>
      {item.description && <Text type="secondary">{item.description}</Text>}
    </Space>
  );

  return (
    <Card title={<Space><ExperimentOutlined /> Create New Experiment</Space>} style={{ margin: 20 }}>
      <Row gutter={[16, 16]}>
        <Col span={12}>
          <Card 
            title={<Space><EnvironmentOutlined /> Environment</Space>} 
            extra={<Button type="link" onClick={() => handleCreateNew('environment')}>Create New</Button>}
          >
            <Space direction="vertical" style={{ width: '100%' }}>
              <Text>Select an environment configuration:</Text>
              <Select
                placeholder="Select environment"
                style={{ width: '100%' }}
                loading={loading}
                value={selectedEnvironment || undefined}
                onChange={setSelectedEnvironment}
                optionLabelProp="label"
                disabled={experimentRunning}
              >
                {environments.map(env => (
                  <Option key={env.id} value={env.id} label={env.name}>
                    {renderOptionContent(env)}
                  </Option>
                ))}
              </Select>
            </Space>
          </Card>
        </Col>
        
        <Col span={12}>
          <Card 
            title={<Space><GlobalOutlined /> Map</Space>} 
            extra={<Button type="link" onClick={() => handleCreateNew('map')}>Create New</Button>}
          >
            <Space direction="vertical" style={{ width: '100%' }}>
              <Text>Select a map:</Text>
              <Select
                placeholder="Select map"
                style={{ width: '100%' }}
                loading={loading}
                value={selectedMap || undefined}
                onChange={setSelectedMap}
                optionLabelProp="label"
                disabled={experimentRunning}
              >
                {maps.map(map => (
                  <Option key={map.id} value={map.id} label={map.name}>
                    {renderOptionContent(map)}
                  </Option>
                ))}
              </Select>
            </Space>
          </Card>
        </Col>
        
        <Col span={12}>
          <Card 
            title={<Space><TeamOutlined /> Agent</Space>} 
            extra={<Button type="link" onClick={() => handleCreateNew('agent')}>Create New</Button>}
          >
            <Space direction="vertical" style={{ width: '100%' }}>
              <Text>Select an agent configuration:</Text>
              <Select
                placeholder="Select agent"
                style={{ width: '100%' }}
                loading={loading}
                value={selectedAgent || undefined}
                onChange={setSelectedAgent}
                optionLabelProp="label"
                disabled={experimentRunning}
              >
                {agents.map(agent => (
                  <Option key={agent.id} value={agent.id} label={agent.name}>
                    {renderOptionContent(agent)}
                  </Option>
                ))}
              </Select>
            </Space>
          </Card>
        </Col>
        
        <Col span={12}>
          <Card 
            title={<Space><NodeIndexOutlined /> Workflow</Space>} 
            extra={<Button type="link" onClick={() => handleCreateNew('workflow')}>Create New</Button>}
          >
            <Space direction="vertical" style={{ width: '100%' }}>
              <Text>Select a workflow:</Text>
              <Select
                placeholder="Select workflow"
                style={{ width: '100%' }}
                loading={loading}
                value={selectedWorkflow || undefined}
                onChange={setSelectedWorkflow}
                optionLabelProp="label"
                disabled={experimentRunning}
              >
                {workflows.map(workflow => (
                  <Option key={workflow.id} value={workflow.id} label={workflow.name}>
                    {renderOptionContent(workflow)}
                  </Option>
                ))}
              </Select>
            </Space>
          </Card>
        </Col>
      </Row>
      
      <Divider />
      
      <div style={{ textAlign: 'center' }}>
        {!experimentRunning ? (
          <Button 
            type="primary" 
            size="large" 
            icon={<RocketOutlined />} 
            onClick={handleStartExperiment}
            loading={loading}
            disabled={!selectedEnvironment || !selectedAgent || !selectedWorkflow || !selectedMap}
          >
            Start Experiment
          </Button>
        ) : (
          <Space direction="vertical" size="large">
            <Space>
              <Spin spinning={experimentStatus === 'running'} />
              <Text>
                Experiment is {experimentStatus}
                {experimentStatus === 'running' && '...'}
              </Text>
            </Space>
            <Button 
              type="primary" 
              danger
              size="large" 
              onClick={handleStopExperiment}
              loading={loading}
            >
              Stop Experiment
            </Button>
          </Space>
        )}
      </div>
    </Card>
  );
};

export default CreateExperiment; 