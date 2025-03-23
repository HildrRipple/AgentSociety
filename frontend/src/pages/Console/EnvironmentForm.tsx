import React, { useState, useEffect } from 'react';
import { Form, Input, Select, InputNumber, Switch, Card, Tabs, Button, Space, Upload, message } from 'antd';
import { UploadOutlined, PlusOutlined, MinusCircleOutlined } from '@ant-design/icons';
import type { UploadProps } from 'antd';
import { SimConfig, LLMConfig } from '../../types/config';
import { LLMProviderType } from '../../utils/enums';

const { TabPane } = Tabs;

interface EnvironmentFormProps {
  value: Partial<SimConfig>;
  onChange: (value: Partial<SimConfig>) => void;
}

// Define provider model options
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
  const [selectedProviders, setSelectedProviders] = useState<Record<number, LLMProviderType>>({});

  // Handle form value changes
  const handleValuesChange = (changedValues: any, allValues: any) => {
    onChange(allValues);
    
    // Track provider changes to update model options
    if (changedValues.llm_configs) {
      const newSelectedProviders: Record<number, LLMProviderType> = { ...selectedProviders };
      
      changedValues.llm_configs.forEach((config: Partial<LLMConfig>, index: number) => {
        if (config && config.provider) {
          newSelectedProviders[index] = config.provider as LLMProviderType;
        }
      });
      
      setSelectedProviders(newSelectedProviders);
    }
  };

  // Set initial values
  useEffect(() => {
    form.setFieldsValue(value);
    
    // Initialize selected providers from value
    if (value.llm_configs) {
      const initialProviders: Record<number, LLMProviderType> = {};
      value.llm_configs.forEach((config, index) => {
        if (config.provider) {
          initialProviders[index] = config.provider;
        }
      });
      setSelectedProviders(initialProviders);
    }
  }, [form, value]);

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
            <Form.List name="llm_configs" initialValue={[{}]}>
              {(fields, { add, remove }) => (
                <>
                  {fields.map(({ key, name, ...restField }) => (
                    <Card 
                      key={key} 
                      title={`LLM Provider ${name + 1}`} 
                      style={{ marginBottom: 16 }}
                      extra={
                        fields.length > 1 ? 
                        <Button 
                          type="text" 
                          danger 
                          icon={<MinusCircleOutlined />} 
                          onClick={() => remove(name)}
                        /> : null
                      }
                    >
                      <Form.Item
                        {...restField}
                        name={[name, 'provider']}
                        label="Provider"
                        rules={[{ required: true, message: 'Please select a provider' }]}
                      >
                        <Select
                          placeholder="Select LLM provider"
                          options={[
                            { value: 'openai', label: 'OpenAI' },
                            { value: 'deepseek', label: 'DeepSeek' },
                            { value: 'qwen', label: 'Qwen' },
                            { value: 'zhipuai', label: 'Zhipu AI' },
                            { value: 'siliconflow', label: 'Silicon Flow' },
                          ]}
                        />
                      </Form.Item>

                      <Form.Item
                        {...restField}
                        name={[name, 'base_url']}
                        label="Base URL (Optional)"
                      >
                        <Input placeholder="Enter base URL if using a custom endpoint" />
                      </Form.Item>

                      <Form.Item
                        {...restField}
                        name={[name, 'api_key']}
                        label="API Key"
                        rules={[{ required: true, message: 'Please enter API key' }]}
                      >
                        <Input.Password placeholder="Enter API key" />
                      </Form.Item>

                      <Form.Item
                        {...restField}
                        name={[name, 'model']}
                        label="Model"
                        rules={[{ required: true, message: 'Please select a model' }]}
                      >
                        <Select
                          placeholder="Select model"
                          options={
                            selectedProviders[name] && providerModels[selectedProviders[name]] 
                              ? providerModels[selectedProviders[name]] 
                              : []
                          }
                        />
                      </Form.Item>
                    </Card>
                  ))}
                  <Form.Item>
                    <Button 
                      type="dashed" 
                      onClick={() => add()} 
                      block 
                      icon={<PlusOutlined />}
                    >
                      Add LLM Provider
                    </Button>
                  </Form.Item>
                </>
              )}
            </Form.List>
          </Card>
        </TabPane>

        <TabPane tab="Simulator Configuration" key="2">
          <Card bordered={false}>
            <Form.Item
              name={['simulator_config', 'task_name']}
              label="Task Name"
              initialValue="citysim"
            >
              <Input placeholder="Enter task name" />
            </Form.Item>

            <Form.Item
              name={['simulator_config', 'max_day']}
              label="Maximum Days"
              initialValue={1000}
            >
              <InputNumber min={1} style={{ width: '100%' }} />
            </Form.Item>

            <Form.Item
              name={['simulator_config', 'start_step']}
              label="Start Step"
              initialValue={28800}
            >
              <InputNumber min={0} style={{ width: '100%' }} />
            </Form.Item>

            <Form.Item
              name={['simulator_config', 'steps_per_simulation_step']}
              label="Steps Per Simulation Step"
              initialValue={300}
            >
              <InputNumber min={1} style={{ width: '100%' }} />
            </Form.Item>

            <Form.Item
              name={['simulator_config', 'steps_per_simulation_day']}
              label="Steps Per Simulation Day"
              initialValue={3600}
            >
              <InputNumber min={1} style={{ width: '100%' }} />
            </Form.Item>

            <Form.Item
              name={['simulator_config', 'primary_node_ip']}
              label="Primary Node IP"
              initialValue="localhost"
            >
              <Input placeholder="Enter primary node IP" />
            </Form.Item>
          </Card>
        </TabPane>

        <TabPane tab="Redis Configuration" key="3">
          <Card bordered={false}>
            <Form.Item
              name={['redis', 'server']}
              label="Redis Server"
              rules={[{ required: true, message: 'Please enter Redis server' }]}
            >
              <Input placeholder="Enter Redis server address" />
            </Form.Item>

            <Form.Item
              name={['redis', 'port']}
              label="Redis Port"
              rules={[{ required: true, message: 'Please enter Redis port' }]}
              initialValue={6379}
            >
              <InputNumber min={1} max={65535} style={{ width: '100%' }} />
            </Form.Item>

            <Form.Item
              name={['redis', 'password']}
              label="Redis Password (Optional)"
            >
              <Input.Password placeholder="Enter Redis password if required" />
            </Form.Item>

            <Form.Item
              name={['redis', 'db']}
              label="Redis Database"
              initialValue="0"
            >
              <Input placeholder="Enter Redis database number" />
            </Form.Item>
          </Card>
        </TabPane>

        <TabPane tab="Metrics Configuration" key="4">
          <Card bordered={false}>
            <Form.Item
              name={['metric_config', 'mlflow', 'mlflow_uri']}
              label="MLflow URI"
              rules={[{ required: true, message: 'Please enter MLflow URI' }]}
            >
              <Input placeholder="Enter MLflow URI" />
            </Form.Item>

            <Form.Item
              name={['metric_config', 'mlflow', 'username']}
              label="MLflow Username (Optional)"
            >
              <Input placeholder="Enter MLflow username" />
            </Form.Item>

            <Form.Item
              name={['metric_config', 'mlflow', 'password']}
              label="MLflow Password (Optional)"
            >
              <Input.Password placeholder="Enter MLflow password" />
            </Form.Item>
          </Card>
        </TabPane>

        <TabPane tab="Database Configuration" key="5">
          <Card bordered={false}>
            <Form.Item
              name={['pgsql', 'enabled']}
              label="Enable PostgreSQL"
              valuePropName="checked"
              initialValue={true}
            >
              <Switch />
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
              initialValue={false}
            >
              <Switch />
            </Form.Item>

            <Form.Item
              name={['avro', 'path']}
              label="Avro Path"
              initialValue="./output/avro"
            >
              <Input placeholder="Enter Avro path" />
            </Form.Item>
          </Card>
        </TabPane>

        <TabPane tab="Server Configuration" key="6">
          <Card bordered={false}>
            <Form.Item
              name="simulator_server_address"
              label="Simulator Server Address"
            >
              <Input placeholder="Enter simulator server address" />
            </Form.Item>
          </Card>
        </TabPane>
      </Tabs>
    </Form>
  );
};

export default EnvironmentForm; 