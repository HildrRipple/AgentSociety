import React from 'react';
import { Form, Input, Select, InputNumber, Switch, Card, Space, Button, Divider } from 'antd';
import { MinusCircleOutlined, PlusOutlined } from '@ant-design/icons';

interface EnvironmentFormProps {
  value: any;
  onChange: (value: any) => void;
}

const EnvironmentForm: React.FC<EnvironmentFormProps> = ({ value, onChange }) => {
  const [form] = Form.useForm();

  // Update parent component state when form values change
  const handleValuesChange = (_: any, allValues: any) => {
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
      <Card title="LLM Configuration" bordered={false}>
        <Form.Item
          name={['llm_request', 'request_type']}
          label="Request Type"
          rules={[{ required: true, message: 'Please select request type' }]}
        >
          <Select
            placeholder="Select request type"
            options={[
              { value: 'zhipuai', label: 'ZhipuAI' },
              { value: 'openai', label: 'OpenAI' },
              { value: 'azure', label: 'Azure OpenAI' },
            ]}
          />
        </Form.Item>

        <Form.Item
          name={['llm_request', 'api_key']}
          label="API Key"
          rules={[{ required: true, message: 'Please enter API key' }]}
        >
          <Input.Password placeholder="Enter your API key" />
        </Form.Item>

        <Form.Item
          name={['llm_request', 'model']}
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
            ]}
          />
        </Form.Item>
      </Card>

      <Card title="Simulator Configuration" bordered={false} style={{ marginTop: 16 }}>
        <Form.Item
          name={['simulator_request', 'task_name']}
          label="Task Name"
          rules={[{ required: true, message: 'Please enter task name' }]}
        >
          <Input placeholder="Enter task name" />
        </Form.Item>

        <Form.Item
          name={['simulator_request', 'max_day']}
          label="Maximum Days"
          rules={[{ required: true, message: 'Please enter maximum days' }]}
        >
          <InputNumber min={1} max={365} style={{ width: '100%' }} />
        </Form.Item>

        <Form.Item
          name={['simulator_request', 'start_step']}
          label="Start Step (seconds)"
          rules={[{ required: true, message: 'Please enter start step' }]}
        >
          <InputNumber min={0} style={{ width: '100%' }} />
        </Form.Item>

        <Form.Item
          name={['simulator_request', 'total_step']}
          label="Total Steps (seconds)"
          rules={[{ required: true, message: 'Please enter total steps' }]}
        >
          <InputNumber min={1} style={{ width: '100%' }} />
        </Form.Item>

        <Form.Item
          name={['simulator_request', 'log_dir']}
          label="Log Directory"
          rules={[{ required: true, message: 'Please enter log directory' }]}
        >
          <Input placeholder="Enter log directory" />
        </Form.Item>
      </Card>

      <Card title="Redis Configuration" bordered={false} style={{ marginTop: 16 }}>
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
          <Input placeholder="Enter Redis username" />
        </Form.Item>

        <Form.Item
          name={['redis', 'password']}
          label="Password"
        >
          <Input.Password placeholder="Enter Redis password" />
        </Form.Item>
      </Card>

      <Card title="Map Configuration" bordered={false} style={{ marginTop: 16 }}>
        <Form.Item
          name={['map_request', 'file_path']}
          label="Map File Path"
          rules={[{ required: true, message: 'Please enter map file path' }]}
        >
          <Input placeholder="Enter map file path" />
        </Form.Item>
      </Card>

      <Card title="Metrics Configuration" bordered={false} style={{ marginTop: 16 }}>
        <Form.Item
          name={['metric_request', 'mlflow', 'username']}
          label="MLflow Username"
        >
          <Input placeholder="Enter MLflow username" />
        </Form.Item>

        <Form.Item
          name={['metric_request', 'mlflow', 'password']}
          label="MLflow Password"
        >
          <Input.Password placeholder="Enter MLflow password" />
        </Form.Item>

        <Form.Item
          name={['metric_request', 'mlflow', 'mlflow_uri']}
          label="MLflow URI"
        >
          <Input placeholder="Enter MLflow URI" />
        </Form.Item>
      </Card>

      <Card title="Database Configuration" bordered={false} style={{ marginTop: 16 }}>
        <Form.Item
          name={['pgsql', 'enabled']}
          label="Enable PostgreSQL"
          valuePropName="checked"
        >
          <Switch />
        </Form.Item>

        <Form.Item
          name={['pgsql', 'dsn']}
          label="PostgreSQL DSN"
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
        >
          <Input placeholder="Enter Avro path" />
        </Form.Item>
      </Card>
    </Form>
  );
};

export default EnvironmentForm; 