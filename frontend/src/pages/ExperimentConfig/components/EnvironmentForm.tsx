import React, { useState, useEffect } from 'react';
import { Form, Input, Select, InputNumber, Switch, Card, Tabs, Button, Space } from 'antd';
import { PlusOutlined, MinusCircleOutlined } from '@ant-design/icons';

interface EnvironmentFormProps {
  value: Record<string, unknown>;
  onChange: (value: Record<string, unknown>) => void;
}

const { TabPane } = Tabs;

// 定义不同提供商的模型选项
const providerModels = {
  deepseek: [
    { value: 'deepseek-reasoner', label: 'DeepSeek-R1' },
    { value: 'deepseek-chat', label: 'DeepSeek-V3' },
  ],
  openai: [
    { value: 'gpt-4.5', label: 'GPT-4.5 Preview' },
    { value: 'gpt-4o', label: 'GPT-4o' },
    { value: 'gpt-4o-mini', label: 'GPT-4o mini' },
    { value: 'gpt-4-turbo', label: 'GPT-4 Turbo' },
    { value: 'gpt-4', label: 'GPT-4' },
    { value: 'gpt-3.5-turbo', label: 'GPT-3.5 Turbo' },
  ],
  qwen: [
    { value: 'qwen-max', label: 'Qwen Max' },
    { value: 'qwen-plus', label: 'Qwen Plus' },
    { value: 'qwen-turbo', label: 'Qwen Turbo' },
    { value: 'qwen2.5-72b-instruct', label: 'qwen2.5-72b-instruct' },
    { value: 'qwen2.5-32b-instruct', label: 'qwen2.5-32b-instruct' },
    { value: 'qwen2.5-14b-instruct-1m', label: 'qwen2.5-14b-instruct-1m' },
    { value: 'qwen2.5-14b-instruct', label: 'qwen2.5-14b-instruct' },
    { value: 'qwen2.5-7b-instruct-1m', label: 'qwen2.5-7b-instruct-1m' },
    { value: 'qwen2.5-7b-instruct', label: 'qwen2.5-7b-instruct' },
    { value: 'qwen2-72b-instruct', label: 'qwen2-72b-instruct' },
    { value: 'qwen2-57b-a14b-instruct', label: 'qwen2-57b-a14b-instruct' },
    { value: 'qwen2-7b-instruct', label: 'qwen2-7b-instruct' },

  ],
  siliconflow: [
    { value: 'Pro/deepseek-ai/DeepSeek-V3', label: 'Pro/deepseek-ai/DeepSeek-V3' },
    { value: 'deepseek-ai/DeepSeek-V3', label: 'deepseek-ai/DeepSeek-V3' },
    { value: 'deepseek-ai/DeepSeek-R1-Distill-Qwen-32B', label: 'deepseek-ai/DeepSeek-R1-Distill-Qwen-32B' },
    { value: 'deepseek-ai/DeepSeek-R1-Distill-Qwen-14B', label: 'deepseek-ai/DeepSeek-R1-Distill-Qwen-14B' },
    { value: 'Qwen/QwQ-32B', label: 'Qwen/QwQ-32B' },
    { value: 'Qwen/QVQ-72B-Preview', label: 'Qwen/QVQ-72B-Preview' },
  ],
  zhipuai: [
    { value: 'glm-4-air', label: 'GLM-4-Air' },
    { value: 'glm-4-flash', label: 'GLM-4-Flash' },
    { value: 'glm-4-plus', label: 'GLM-4-Plus' },
  ],
};

const EnvironmentForm: React.FC<EnvironmentFormProps> = ({ value, onChange }) => {
  const [form] = Form.useForm();
  const [selectedProvider, setSelectedProvider] = useState<string>('');

  // 处理表单值变化
  const handleValuesChange = (changedValues: Record<string, unknown>, allValues: Record<string, unknown>) => {
    // 检查是否更改了 provider
    if (changedValues.llm_config && typeof changedValues.llm_config === 'object') {
      const llmConfig = changedValues.llm_config as Record<string, unknown>;
      
      if ('provider' in llmConfig && typeof llmConfig.provider === 'string') {
        const newProvider = llmConfig.provider;
        
        // 只有当提供商真正改变时才重置模型
        if (newProvider !== selectedProvider) {
          setSelectedProvider(newProvider);
          
          // 清除当前选择的模型
          const updatedValues = { ...allValues };
          if (typeof updatedValues.llm_config === 'object') {
            const updatedLlmConfig = { ...(updatedValues.llm_config as Record<string, unknown>) };
            delete updatedLlmConfig.model;
            updatedValues.llm_config = updatedLlmConfig;
            
            // 更新表单值
            form.setFieldsValue(updatedValues);
            
            // 调用 onChange 传递更新后的值
            onChange(updatedValues);
            return;
          }
        }
      }
    }
    
    // 对于其他变化，直接传递所有值
    onChange(allValues);
  };

  // 设置初始值
  useEffect(() => {
    form.setFieldsValue(value);
    
    // 从 value 中获取 provider
    if (value && typeof value.llm_config === 'object') {
      const llmConfig = value.llm_config as Record<string, unknown>;
      if (llmConfig && typeof llmConfig.provider === 'string') {
        setSelectedProvider(llmConfig.provider);
      }
    }
  }, [form, value]);

  // 获取当前提供商的模型选项
  const getModelOptions = () => {
    if (!selectedProvider) return [];
    return providerModels[selectedProvider as keyof typeof providerModels] || [];
  };

  return (
    <Form
      form={form}
      layout="vertical"
      onValuesChange={handleValuesChange}
      initialValues={value}
    >
      <Tabs defaultActiveKey="1">
        <TabPane tab="LLM Configuration" key="1">
          <Card bordered={false}>
            <Form.Item
              name={['llm_config', 'provider']}
              label="Provider"
              rules={[{ required: true, message: 'Please select provider' }]}
            >
              <Select
                placeholder="Select provider"
                options={[
                  { value: 'deepseek', label: 'DeepSeek' },
                  { value: 'openai', label: 'OpenAI' },
                  { value: 'qwen', label: 'Qwen' },
                  { value: 'siliconflow', label: 'SiliconFlow' },
                  { value: 'zhipuai', label: 'ZhipuAI' },
                ]}
                onChange={(value) => {
                  // 当直接通过 Select 组件更改时，确保更新 selectedProvider
                  if (value !== selectedProvider) {
                    setSelectedProvider(value);
                    // 清除模型选择
                    form.setFieldValue(['llm_config', 'model'], undefined);
                  }
                }}
              />
            </Form.Item>

            <Form.Item
              name={['llm_config', 'base_url']}
              label="Base URL"
            >
              <Input placeholder="Enter base URL (optional)" />
            </Form.Item>

            <Form.List name={['llm_config', 'api_keys']}>
              {(fields, { add, remove }) => (
                <>
                  {fields.map(({ key, name, ...restField }) => (
                    <Space key={key} style={{ display: 'flex', marginBottom: 8 }} align="baseline">
                      <Form.Item
                        {...restField}
                        name={name}
                        rules={[{ required: true, message: 'Please enter API key' }]}
                        style={{ width: '100%', marginBottom: 0 }}
                      >
                        <Input.Password placeholder="Enter API key" />
                      </Form.Item>
                      <MinusCircleOutlined onClick={() => remove(name)} />
                    </Space>
                  ))}
                  <Form.Item>
                    <Button type="dashed" onClick={() => add()} block icon={<PlusOutlined />}>
                      Add API Key
                    </Button>
                  </Form.Item>
                </>
              )}
            </Form.List>

            <Form.Item
              name={['llm_config', 'model']}
              label="Model"
              rules={[{ required: true, message: 'Please select model' }]}
            >
              <Select
                placeholder={selectedProvider ? `Select ${selectedProvider} model` : "Please select a provider first"}
                options={getModelOptions()}
                disabled={!selectedProvider}
              />
            </Form.Item>
          </Card>
        </TabPane>

        <TabPane tab="Simulator Configuration" key="2">
          <Card bordered={false}>
            <Form.Item
              name={['simulator_config', 'task_name']}
              label="Task Name"
              rules={[{ required: true, message: 'Please enter task name' }]}
            >
              <Input placeholder="Enter task name" defaultValue="citysim" />
            </Form.Item>

            <Form.Item
              name={['simulator_config', 'max_day']}
              label="Maximum Days"
              rules={[{ required: true, message: 'Please enter maximum days' }]}
            >
              <InputNumber min={1} max={1000} defaultValue={1000} style={{ width: '100%' }} />
            </Form.Item>

            <Form.Item
              name={['simulator_config', 'start_step']}
              label="Start Step (seconds)"
              rules={[{ required: true, message: 'Please enter start step' }]}
            >
              <InputNumber min={0} defaultValue={28800} style={{ width: '100%' }} />
            </Form.Item>

            <Form.Item
              name={['simulator_config', 'total_step']}
              label="Total Steps (seconds)"
              rules={[{ required: true, message: 'Please enter total steps' }]}
            >
              <InputNumber min={1} defaultValue={86400} style={{ width: '100%' }} />
            </Form.Item>

            <Form.Item
              name={['simulator_config', 'log_dir']}
              label="Log Directory"
              rules={[{ required: true, message: 'Please enter log directory' }]}
            >
              <Input placeholder="Enter log directory" defaultValue="./log" />
            </Form.Item>

            <Form.Item
              name={['simulator_config', 'steps_per_simulation_step']}
              label="Steps Per Simulation Step (seconds)"
              rules={[{ required: true, message: 'Please enter steps per simulation step' }]}
            >
              <InputNumber min={1} defaultValue={300} style={{ width: '100%' }} />
            </Form.Item>

            <Form.Item
              name={['simulator_config', 'steps_per_simulation_day']}
              label="Steps Per Simulation Day (seconds)"
              rules={[{ required: true, message: 'Please enter steps per simulation day' }]}
            >
              <InputNumber min={1} defaultValue={3600} style={{ width: '100%' }} />
            </Form.Item>

            <Form.Item
              name={['simulator_config', 'primary_node_ip']}
              label="Primary Node IP"
              rules={[{ required: true, message: 'Please enter primary node IP' }]}
            >
              <Input placeholder="Enter primary node IP" defaultValue="localhost" />
            </Form.Item>
          </Card>
        </TabPane>

        <TabPane tab="Redis Configuration" key="3">
          <Card bordered={false}>
            <Form.Item
              name={['redis', 'server']}
              label="Server"
              rules={[{ required: true, message: 'Please enter Redis server' }]}
            >
              <Input placeholder="Enter Redis server address" />
            </Form.Item>

            <Form.Item
              name={['redis', 'port']}
              label="Port"
              rules={[{ required: true, message: 'Please enter Redis port' }]}
            >
              <InputNumber min={1} max={65535} defaultValue={6379} style={{ width: '100%' }} />
            </Form.Item>

            <Form.Item
              name={['redis', 'username']}
              label="Username"
            >
              <Input placeholder="Enter Redis username (optional)" />
            </Form.Item>

            <Form.Item
              name={['redis', 'password']}
              label="Password"
            >
              <Input.Password placeholder="Enter Redis password (optional)" />
            </Form.Item>
          </Card>
        </TabPane>

        <TabPane tab="Metrics Configuration" key="4">
          <Card bordered={false}>
            <Form.Item
              name={['metric_config', 'mlflow', 'username']}
              label="MLflow Username"
            >
              <Input placeholder="Enter MLflow username" />
            </Form.Item>

            <Form.Item
              name={['metric_config', 'mlflow', 'password']}
              label="MLflow Password"
            >
              <Input.Password placeholder="Enter MLflow password" />
            </Form.Item>

            <Form.Item
              name={['metric_config', 'mlflow', 'mlflow_uri']}
              label="MLflow URI"
              rules={[{ required: true, message: 'Please enter MLflow URI' }]}
            >
              <Input placeholder="Enter MLflow URI" />
            </Form.Item>
          </Card>
        </TabPane>

        <TabPane tab="Database Configuration" key="5">
          <Card bordered={false}>
            <Form.Item
              name={['pgsql', 'enabled']}
              label="Enable PostgreSQL"
              valuePropName="checked"
            >
              <Switch defaultChecked />
            </Form.Item>

            <Form.Item
              name={['pgsql', 'dsn']}
              label="PostgreSQL DSN"
              rules={[{ required: true, message: 'Please enter PostgreSQL DSN' }]}
            >
              <Input placeholder="Enter PostgreSQL DSN" />
            </Form.Item>

            <Form.Item
              name={['avro', 'enabled']}
              label="Enable Avro"
              valuePropName="checked"
            >
              <Switch />
            </Form.Item>
          </Card>
        </TabPane>
      </Tabs>
    </Form>
  );
};

export default EnvironmentForm; 