import React from 'react';
import { Form, Input, Select, InputNumber, Switch, Card, Tabs } from 'antd';

interface EnvironmentFormProps {
  value: Record<string, unknown>;
  onChange: (value: Record<string, unknown>) => void;
}

const { TabPane } = Tabs;

const EnvironmentForm: React.FC<EnvironmentFormProps> = ({ value, onChange }) => {
  const [form] = Form.useForm();

  // Update parent component state when form values change
  const handleValuesChange = (_: unknown, allValues: Record<string, unknown>) => {
    onChange(allValues);
  };

  // Set initial values
  React.useEffect(() => {
    form.setFieldsValue(value);
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
            <Form.Item
              name={['llm_config', 'provider']}
              label="Provider"
              rules={[{ required: true, message: 'Please select provider' }]}
            >
              <Select
                placeholder="Select provider"
                options={[
                  { value: 'zhipuai', label: 'ZhipuAI' },
                  { value: 'openai', label: 'OpenAI' },
                  { value: 'azure', label: 'Azure OpenAI' },
                  { value: 'anthropic', label: 'Anthropic' },
                ]}
              />
            </Form.Item>

            <Form.Item
              name={['llm_config', 'base_url']}
              label="Base URL"
            >
              <Input placeholder="Enter base URL (optional)" />
            </Form.Item>

            <Form.Item
              name={['llm_config', 'api_key']}
              label="API Key"
              rules={[{ required: true, message: 'Please enter API key' }]}
            >
              <Input.Password placeholder="Enter your API key" />
            </Form.Item>

            <Form.Item
              name={['llm_config', 'model']}
              label="Model"
              rules={[{ required: true, message: 'Please select model' }]}
            >
              <Select
                placeholder="Select model"
                options={[
                  { value: 'GLM-4-Flash', label: 'GLM-4-Flash' },
                  { value: 'GLM-4', label: 'GLM-4' },
                  { value: 'gpt-4', label: 'GPT-4' },
                  { value: 'gpt-3.5-turbo', label: 'GPT-3.5 Turbo' },
                  { value: 'claude-3-opus', label: 'Claude 3 Opus' },
                  { value: 'claude-3-sonnet', label: 'Claude 3 Sonnet' },
                ]}
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

        <TabPane tab="Map Configuration" key="4">
          <Card bordered={false}>
            <Form.Item
              name={['map_config', 'file_path']}
              label="Map File Path"
              rules={[{ required: true, message: 'Please enter map file path' }]}
            >
              <Input placeholder="Enter map file path" />
            </Form.Item>
          </Card>
        </TabPane>

        <TabPane tab="Metrics Configuration" key="5">
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

        <TabPane tab="Database Configuration" key="6">
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

            <Form.Item
              name={['avro', 'path']}
              label="Avro Path"
              rules={[{ required: true, message: 'Please enter Avro path' }]}
            >
              <Input placeholder="Enter Avro path" />
            </Form.Item>
          </Card>
        </TabPane>
      </Tabs>
    </Form>
  );
};

export default EnvironmentForm; 