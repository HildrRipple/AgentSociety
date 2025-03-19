import React, { useState, useEffect } from 'react';
import { Card, Button, Select, Space, Typography, Divider, message, Row, Col, Spin } from 'antd';
import { useNavigate } from 'react-router-dom';
import { ExperimentOutlined, EnvironmentOutlined, TeamOutlined, GlobalOutlined, RocketOutlined, NodeIndexOutlined } from '@ant-design/icons';
import storageService, { STORAGE_KEYS, ConfigItem } from '../../services/storageService';

const { Text } = Typography;
const { Option } = Select;

// Add these interfaces at the top of the file
interface EnvironmentConfig {
  weather?: string;
  temperature?: string;
  workday?: boolean;
  other_information?: string;
}

interface WorkflowConfig extends ConfigItem {
  config: {
    environment?: EnvironmentConfig;
    [key: string]: any;
  }
}

const CreateExperiment: React.FC = () => {
  // State declarations
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

  // Load all configurations
  useEffect(() => {
    const loadConfigurations = async () => {
      setLoading(true);
      try {
        // Initialize example data
        await storageService.initializeExampleData();
        
        // Load all configurations
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

  const handleSubmit = async () => {
    setLoading(true);
    try {
      // Get selected configurations
      const environment = environments.find(env => env.id === selectedEnvironment);
      const agent = agents.find(agent => agent.id === selectedAgent);
      const workflow = workflows.find(workflow => workflow.id === selectedWorkflow) as WorkflowConfig;  // Add type assertion here
      const map = maps.find(map => map.id === selectedMap);

      if (!environment || !agent || !workflow || !map) {
        message.error('Please select all required configurations');
        return;
      }

      // Combine configurations
      const fullConfig = {
        environment: {
          ...environment.config,
        },
        agent: {
          ...agent.config,
        },
        experiment: {
          ...workflow.config,
          environment: {
            weather: workflow.config.environment?.weather ?? "Normal Weather",
            temperature: workflow.config.environment?.temperature ?? "Normal Temperature",
            workday: workflow.config.environment?.workday ?? true,
            other_information: workflow.config.environment?.other_information ?? ""
          }
        }
      };
      
      // Send request to start experiment
      const response = await fetch('/api/experiments', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(fullConfig),
      });
      
      const data = await response.json();
      
      if (response.ok) {
        message.success('Experiment started successfully!');
        navigate(`/exp/${data.experimentId}`);
      } else {
        message.error(`Start failed: ${data.message || 'Unknown error'}`);
      }
    } catch (error) {
      message.error('Error starting experiment');
      console.error(error);
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
            onClick={handleSubmit}
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