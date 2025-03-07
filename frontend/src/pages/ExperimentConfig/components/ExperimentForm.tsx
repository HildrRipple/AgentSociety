import React from 'react';
import { Form, Input, InputNumber, DatePicker, Select, Card, Switch, Radio, Space, Divider, Button, Tabs } from 'antd';
import type { RadioChangeEvent } from 'antd';
import { InfoCircleOutlined, PlusOutlined, MinusCircleOutlined } from '@ant-design/icons';

const { RangePicker } = DatePicker;
const { TextArea } = Input;
const { TabPane } = Tabs;

interface ExperimentFormProps {
  value: Record<string, unknown>;
  onChange: (value: Record<string, unknown>) => void;
  environmentConfig: Record<string, unknown>;
  agentConfig: Record<string, unknown>;
}

const ExperimentForm: React.FC<ExperimentFormProps> = ({ 
  value, 
  onChange
}) => {
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
        <TabPane tab="Basic Information" key="1">
          <Card bordered={false}>
            <Form.Item
              name="exp_name"
              label="Experiment Name"
              rules={[{ required: true, message: 'Please enter experiment name' }]}
            >
              <Input placeholder="Enter experiment name" defaultValue="default_experiment" />
            </Form.Item>

            <Form.Item
              name="description"
              label="Experiment Description"
            >
              <TextArea rows={4} placeholder="Enter experiment description" />
            </Form.Item>

            <Form.Item
              name="llm_semaphore"
              label="LLM Semaphore"
              tooltip="Maximum number of concurrent LLM requests"
              rules={[{ required: true, message: 'Please enter LLM semaphore value' }]}
            >
              <InputNumber min={1} max={1000} defaultValue={200} style={{ width: '100%' }} />
            </Form.Item>

            <Form.Item
              name="logging_level"
              label="Logging Level"
              rules={[{ required: true, message: 'Please select logging level' }]}
            >
              <Select
                placeholder="Select logging level"
                options={[
                  { value: 10, label: 'DEBUG' },
                  { value: 20, label: 'INFO' },
                  { value: 30, label: 'WARNING' },
                  { value: 40, label: 'ERROR' },
                  { value: 50, label: 'CRITICAL' },
                ]}
                defaultValue={30}
              />
            </Form.Item>
          </Card>
        </TabPane>

        <TabPane tab="Workflow Configuration" key="2">
          <Card bordered={false}>
            <Form.List name="workflow">
              {(fields, { add, remove }) => (
                <>
                  {fields.map(({ key, name, ...restField }) => (
                    <Card 
                      key={key} 
                      title={`Step ${name + 1}`} 
                      style={{ marginBottom: 16 }} 
                      extra={
                        <Button 
                          type="text" 
                          danger 
                          icon={<MinusCircleOutlined />} 
                          onClick={() => remove(name)}
                        />
                      }
                    >
                      <Form.Item
                        {...restField}
                        name={[name, 'type']}
                        label="Step Type"
                        rules={[{ required: true, message: 'Please select step type' }]}
                      >
                        <Select
                          placeholder="Select step type"
                          options={[
                            { value: 'run', label: 'Run Simulation' },
                            { value: 'function', label: 'Execute Function' },
                            { value: 'intervene', label: 'Intervene' },
                            { value: 'interview', label: 'Interview' },
                            { value: 'survey', label: 'Survey' },
                            { value: 'environment_intervene', label: 'Environment Intervention' },
                            { value: 'update_state_intervene', label: 'Update State Intervention' },
                            { value: 'message_intervene', label: 'Message Intervention' },
                          ]}
                        />
                      </Form.Item>

                      <Form.Item
                        {...restField}
                        name={[name, 'days']}
                        label="Duration (days)"
                        tooltip="Duration in days for which this step lasts (for RUN type)"
                      >
                        <InputNumber min={0.1} step={0.1} defaultValue={1.0} style={{ width: '100%' }} />
                      </Form.Item>

                      <Form.Item
                        {...restField}
                        name={[name, 'times']}
                        label="Repetitions"
                        tooltip="Number of repetitions for this step (for RUN type)"
                      >
                        <InputNumber min={1} defaultValue={1} style={{ width: '100%' }} />
                      </Form.Item>

                      <Form.Item
                        {...restField}
                        name={[name, 'interview_message']}
                        label="Interview Message"
                        tooltip="Message used for interviews (for INTERVIEW type)"
                      >
                        <Input placeholder="Enter interview message" />
                      </Form.Item>

                      <Form.Item
                        {...restField}
                        name={[name, 'key']}
                        label="Key"
                        tooltip="Key identifier for the step (for ENVIRONMENT_INTERVENE, UPDATE_STATE_INTERVENE types)"
                      >
                        <Input placeholder="Enter key" />
                      </Form.Item>

                      <Form.Item
                        {...restField}
                        name={[name, 'value']}
                        label="Value"
                        tooltip="Value associated with the step (for ENVIRONMENT_INTERVENE, UPDATE_STATE_INTERVENE types)"
                      >
                        <Input placeholder="Enter value" />
                      </Form.Item>

                      <Form.Item
                        {...restField}
                        name={[name, 'intervene_message']}
                        label="Intervention Message"
                        tooltip="Message used for interventions (for MESSAGE_INTERVENE type)"
                      >
                        <Input placeholder="Enter intervention message" />
                      </Form.Item>

                      <Form.Item
                        {...restField}
                        name={[name, 'description']}
                        label="Description"
                      >
                        <Input placeholder="Enter step description" defaultValue="None" />
                      </Form.Item>
                    </Card>
                  ))}
                  <Form.Item>
                    <Button type="dashed" onClick={() => add()} block icon={<PlusOutlined />}>
                      Add Workflow Step
                    </Button>
                  </Form.Item>
                </>
              )}
            </Form.List>
          </Card>
        </TabPane>

        <TabPane tab="Environment Configuration" key="3">
          <Card bordered={false}>
            <Form.Item
              name={['environment', 'weather']}
              label="Weather"
            >
              <Input placeholder="Enter weather condition" defaultValue="The weather is normal" />
            </Form.Item>

            <Form.Item
              name={['environment', 'temperature']}
              label="Temperature"
            >
              <Input placeholder="Enter temperature" defaultValue="The temperature is normal" />
            </Form.Item>

            <Form.Item
              name={['environment', 'workday']}
              label="Workday"
              valuePropName="checked"
            >
              <Switch defaultChecked />
            </Form.Item>

            <Form.Item
              name={['environment', 'other_information']}
              label="Other Information"
            >
              <TextArea rows={4} placeholder="Enter other environment information" defaultValue="" />
            </Form.Item>
          </Card>
        </TabPane>

        <TabPane tab="Message Intercept" key="4">
          <Card bordered={false}>
            <Form.Item
              name={['message_intercept', 'mode']}
              label="Intercept Mode"
            >
              <Select
                placeholder="Select intercept mode"
                options={[
                  { value: 'point', label: 'Point' },
                  { value: 'edge', label: 'Edge' },
                ]}
              />
            </Form.Item>

            <Form.Item
              name={['message_intercept', 'max_violation_time']}
              label="Max Violation Time"
            >
              <InputNumber min={1} defaultValue={3} style={{ width: '100%' }} />
            </Form.Item>
          </Card>
        </TabPane>

        <TabPane tab="Metrics Configuration" key="5">
          <Card bordered={false}>
            <Form.List name="metric_extractors">
              {(fields, { add, remove }) => (
                <>
                  {fields.map(({ key, name, ...restField }) => (
                    <Card 
                      key={key} 
                      title={`Metric Extractor ${name + 1}`} 
                      style={{ marginBottom: 16 }} 
                      extra={
                        <Button 
                          type="text" 
                          danger 
                          icon={<MinusCircleOutlined />} 
                          onClick={() => remove(name)}
                        />
                      }
                    >
                      <Form.Item
                        {...restField}
                        name={[name, 'type']}
                        label="Metric Type"
                        rules={[{ required: true, message: 'Please select metric type' }]}
                      >
                        <Select
                          placeholder="Select metric type"
                          options={[
                            { value: 'function', label: 'Function' },
                            { value: 'state', label: 'State' },
                          ]}
                          defaultValue="function"
                        />
                      </Form.Item>

                      <Form.Item
                        {...restField}
                        name={[name, 'step_interval']}
                        label="Step Interval"
                        tooltip="Frequency interval (in simulation steps) for metric extraction"
                      >
                        <InputNumber min={1} defaultValue={10} style={{ width: '100%' }} />
                      </Form.Item>

                      <Form.Item
                        {...restField}
                        name={[name, 'key']}
                        label="Key"
                        tooltip="Key to store or identify the extracted metric (for STATE type)"
                      >
                        <Input placeholder="Enter key" />
                      </Form.Item>

                      <Form.Item
                        {...restField}
                        name={[name, 'method']}
                        label="Aggregation Method"
                        tooltip="Aggregation method applied to the metric values (for STATE type)"
                      >
                        <Select
                          placeholder="Select aggregation method"
                          options={[
                            { value: 'sum', label: 'Sum' },
                            { value: 'mean', label: 'Mean' },
                            { value: 'max', label: 'Max' },
                            { value: 'min', label: 'Min' },
                          ]}
                          defaultValue="sum"
                        />
                      </Form.Item>

                      <Form.Item
                        {...restField}
                        name={[name, 'extract_time']}
                        label="Extract Time"
                        tooltip="The simulation time or step at which extraction occurs"
                      >
                        <InputNumber min={0} defaultValue={0} style={{ width: '100%' }} />
                      </Form.Item>

                      <Form.Item
                        {...restField}
                        name={[name, 'description']}
                        label="Description"
                      >
                        <Input placeholder="Enter metric description" defaultValue="None" />
                      </Form.Item>
                    </Card>
                  ))}
                  <Form.Item>
                    <Button type="dashed" onClick={() => add()} block icon={<PlusOutlined />}>
                      Add Metric Extractor
                    </Button>
                  </Form.Item>
                </>
              )}
            </Form.List>
          </Card>
        </TabPane>
      </Tabs>
    </Form>
  );
};

export default ExperimentForm; 