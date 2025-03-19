import React, { useState, useRef, useEffect } from 'react';
import { Steps, Button, message, Card, Flex, Select, Space, Typography, Divider } from 'antd';
import EnvironmentForm from './components/EnvironmentForm';
import AgentForm from './components/AgentForm';
import ExperimentForm from './components/ExperimentForm';
import { useNavigate } from 'react-router-dom';

const { Title, Text } = Typography;
const { Option } = Select;

interface SavedConfig {
  id: string;
  name: string;
  config: Record<string, unknown>;
}

const ExperimentConfig: React.FC = () => {
  const [current, setCurrent] = useState(0);
  const [environmentConfig, setEnvironmentConfig] = useState({});
  const [agentConfig, setAgentConfig] = useState({});
  const [experimentConfig, setExperimentConfig] = useState({});
  const [loading, setLoading] = useState(false);
  const [savedEnvironments, setSavedEnvironments] = useState<SavedConfig[]>([]);
  const [savedAgents, setSavedAgents] = useState<SavedConfig[]>([]);
  const [savedExperiments, setSavedExperiments] = useState<SavedConfig[]>([]);
  const [loadingConfigs, setLoadingConfigs] = useState(false);
  const navigate = useNavigate();
  const containerRef = useRef<HTMLDivElement>(null);

  // Effect to scroll to top when current step changes
  useEffect(() => {
    if (containerRef.current) {
      containerRef.current.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  }, [current]);

  // Load saved configurations
  useEffect(() => {
    setLoadingConfigs(true);
    // In a real application, these would be API calls
    // Mock data for demonstration
    setTimeout(() => {
      setSavedEnvironments([
        { id: '1', name: 'Urban Environment', config: { llm_request: { request_type: 'zhipuai' } } },
        { id: '2', name: 'Rural Environment', config: { llm_request: { request_type: 'openai' } } }
      ]);
      
      setSavedAgents([
        { id: '1', name: 'Default Citizen Agent', config: { agent_config: { number_of_citizen: 100 } } },
        { id: '2', name: 'Business Agent', config: { agent_config: { number_of_citizen: 50 } } }
      ]);
      
      setSavedExperiments([
        { id: '1', name: 'Standard City Simulation', config: { experimentName: 'City Simulation' } },
        { id: '2', name: 'Long-term Simulation', config: { experimentName: 'Long-term Simulation' } }
      ]);
      
      setLoadingConfigs(false);
    }, 1000);
  }, []);

  const handleEnvironmentChange = (value: string) => {
    if (value) {
      const selected = savedEnvironments.find(env => env.id === value);
      if (selected) {
        setEnvironmentConfig(selected.config);
      }
    }
  };

  const handleAgentChange = (value: string) => {
    if (value) {
      const selected = savedAgents.find(agent => agent.id === value);
      if (selected) {
        setAgentConfig(selected.config);
      }
    }
  };

  const handleExperimentChange = (value: string) => {
    if (value) {
      const selected = savedExperiments.find(exp => exp.id === value);
      if (selected) {
        setExperimentConfig(selected.config);
      }
    }
  };

  const steps = [
    {
      title: 'Environment Configuration',
      content: (
        <div>
          <Space direction="vertical" style={{ width: '100%', marginBottom: 16 }}>
            <Title level={5}>Select Saved Environment</Title>
            <Select
              placeholder="Select a saved environment configuration"
              style={{ width: '100%' }}
              onChange={handleEnvironmentChange}
              loading={loadingConfigs}
              allowClear
            >
              {savedEnvironments.map(env => (
                <Option key={env.id} value={env.id}>{env.name}</Option>
              ))}
            </Select>
            <Text type="secondary">Or create a new environment configuration below</Text>
          </Space>
          <Divider />
          <EnvironmentForm 
            value={environmentConfig} 
            onChange={setEnvironmentConfig} 
          />
        </div>
      ),
    },
    {
      title: 'Agent Configuration',
      content: (
        <div>
          <Space direction="vertical" style={{ width: '100%', marginBottom: 16 }}>
            <Title level={5}>Select Saved Agent</Title>
            <Select
              placeholder="Select a saved agent configuration"
              style={{ width: '100%' }}
              onChange={handleAgentChange}
              loading={loadingConfigs}
              allowClear
            >
              {savedAgents.map(agent => (
                <Option key={agent.id} value={agent.id}>{agent.name}</Option>
              ))}
            </Select>
            <Text type="secondary">Or create a new agent configuration below</Text>
          </Space>
          <Divider />
          <AgentForm 
            value={agentConfig} 
            onChange={setAgentConfig}
            environmentConfig={environmentConfig}
          />
        </div>
      ),
    },
    {
      title: 'Experiment Configuration',
      content: (
        <div>
          <Space direction="vertical" style={{ width: '100%', marginBottom: 16 }}>
            <Title level={5}>Select Saved Experiment Template</Title>
            <Select
              placeholder="Select a saved experiment template"
              style={{ width: '100%' }}
              onChange={handleExperimentChange}
              loading={loadingConfigs}
              allowClear
            >
              {savedExperiments.map(exp => (
                <Option key={exp.id} value={exp.id}>{exp.name}</Option>
              ))}
            </Select>
            <Text type="secondary">Or create a new experiment configuration below</Text>
          </Space>
          <Divider />
          <ExperimentForm 
            value={experimentConfig} 
            onChange={setExperimentConfig}
            environmentConfig={environmentConfig}
            agentConfig={agentConfig}
          />
        </div>
      ),
    },
  ];

  const next = () => {
    setCurrent(current + 1);
  };

  const prev = () => {
    setCurrent(current - 1);
  };

  const handleSubmit = async () => {
    setLoading(true);
    try {
      // Combine all configurations
      const fullConfig = {
        environment: environmentConfig,
        agent: agentConfig,
        experiment: experimentConfig,
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
        // Navigate to experiment details page
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

  return (
    <Card title="Create New Experiment" style={{ margin: 20 }} ref={containerRef}>
      <Steps current={current} items={steps.map(item => ({ title: item.title }))} />
      
      <div style={{ marginTop: 24, marginBottom: 24, minHeight: 400 }}>
        {steps[current].content}
      </div>
      
      <Flex justify="space-between">
        {current > 0 && (
          <Button onClick={prev}>
            Previous
          </Button>
        )}
        
        {current < steps.length - 1 && (
          <Button type="primary" onClick={next}>
            Next
          </Button>
        )}
        
        {current === steps.length - 1 && (
          <Button type="primary" onClick={handleSubmit} loading={loading}>
            Start Experiment
          </Button>
        )}
      </Flex>
    </Card>
  );
};

export default ExperimentConfig; 