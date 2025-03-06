import React, { useState } from 'react';
import { Steps, Button, message, Card, Flex } from 'antd';
import EnvironmentForm from './components/EnvironmentForm';
import AgentForm from './components/AgentForm';
import ExperimentForm from './components/ExperimentForm';
import { useNavigate } from 'react-router-dom';

const ExperimentConfig: React.FC = () => {
  const [current, setCurrent] = useState(0);
  const [environmentConfig, setEnvironmentConfig] = useState({});
  const [agentConfig, setAgentConfig] = useState({});
  const [experimentConfig, setExperimentConfig] = useState({});
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const steps = [
    {
      title: 'Environment Configuration',
      content: <EnvironmentForm 
                 value={environmentConfig} 
                 onChange={setEnvironmentConfig} 
               />,
    },
    {
      title: 'Agent Configuration',
      content: <AgentForm 
                 value={agentConfig} 
                 onChange={setAgentConfig}
                 environmentConfig={environmentConfig}
               />,
    },
    {
      title: 'Experiment Configuration',
      content: <ExperimentForm 
                 value={experimentConfig} 
                 onChange={setExperimentConfig}
                 environmentConfig={environmentConfig}
                 agentConfig={agentConfig}
               />,
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
    <Card title="Create New Experiment" style={{ margin: 20 }}>
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