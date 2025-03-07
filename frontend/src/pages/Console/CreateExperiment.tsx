import React, { useState, useEffect } from 'react';
import { Card, Button, Select, Space, Typography, Divider, message, Row, Col } from 'antd';
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

  const handleStartExperiment = () => {
    if (!selectedEnvironment || !selectedAgent || !selectedWorkflow || !selectedMap) {
      message.error('Please select all required configurations');
      return;
    }

    setLoading(true);
    
    // 获取选中的配置
    const selectedEnvConfig = environments.find(env => env.id === selectedEnvironment);
    const selectedAgentConfig = agents.find(agent => agent.id === selectedAgent);
    const selectedWorkflowConfig = workflows.find(workflow => workflow.id === selectedWorkflow);
    const selectedMapConfig = maps.find(map => map.id === selectedMap);
    
    // 组合配置
    const experimentConfig = {
      environment: selectedEnvConfig?.config || {},
      agent: selectedAgentConfig?.config || {},
      workflow: selectedWorkflowConfig?.config || {},
      map: selectedMapConfig?.config || {},
      name: `${selectedEnvConfig?.name || 'Unknown'} - ${selectedWorkflowConfig?.name || 'Unknown'}`,
      createdAt: new Date().toISOString()
    };
    
    // 在实际应用中，这里会发送请求到后端启动实验
    console.log('Starting experiment with config:', experimentConfig);
    
    setTimeout(() => {
      message.success('Experiment started successfully!');
      // 导航到实验详情页面
      navigate('/');
      setLoading(false);
    }, 1000);
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
              >
                {environments.map(env => (
                  <Option key={env.id} value={env.id}>
                    <Space direction="vertical" style={{ width: '100%' }}>
                      <Text strong>{env.name}</Text>
                      {env.description && <Text type="secondary">{env.description}</Text>}
                    </Space>
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
              >
                {maps.map(map => (
                  <Option key={map.id} value={map.id}>
                    <Space direction="vertical" style={{ width: '100%' }}>
                      <Text strong>{map.name}</Text>
                      {map.description && <Text type="secondary">{map.description}</Text>}
                    </Space>
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
              >
                {agents.map(agent => (
                  <Option key={agent.id} value={agent.id}>
                    <Space direction="vertical" style={{ width: '100%' }}>
                      <Text strong>{agent.name}</Text>
                      {agent.description && <Text type="secondary">{agent.description}</Text>}
                    </Space>
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
              >
                {workflows.map(workflow => (
                  <Option key={workflow.id} value={workflow.id}>
                    <Space direction="vertical" style={{ width: '100%' }}>
                      <Text strong>{workflow.name}</Text>
                      {workflow.description && <Text type="secondary">{workflow.description}</Text>}
                    </Space>
                  </Option>
                ))}
              </Select>
            </Space>
          </Card>
        </Col>
      </Row>
      
      <Divider />
      
      <div style={{ textAlign: 'center' }}>
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
      </div>
    </Card>
  );
};

export default CreateExperiment; 