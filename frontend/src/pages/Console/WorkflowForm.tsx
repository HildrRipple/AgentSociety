import React from 'react';
import { Form, Input, InputNumber, Select, Card, Tabs, Button, Space, Switch } from 'antd';
import { PlusOutlined, MinusCircleOutlined } from '@ant-design/icons';
import { ExpConfig, WorkflowStep, MetricExtractor } from '../../types/config';
import { WorkflowType, MetricType } from '../../utils/enums';

const { TabPane } = Tabs;

interface WorkflowFormProps {
  value: Partial<ExpConfig>;
  onChange: (value: Partial<ExpConfig>) => void;
}

const WorkflowForm: React.FC<WorkflowFormProps> = ({ value, onChange }) => {
  const [form] = Form.useForm();

  // Update parent component state when form values change
  const handleValuesChange = (changedValues: any, allValues: any) => {
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
        <TabPane tab="Basic Settings" key="1">
          <Card bordered={false}>
            <Form.Item
              name="llm_semaphore"
              label="LLM Semaphore"
              tooltip="Maximum number of concurrent LLM requests"
              initialValue={200}
            >
              <InputNumber min={1} style={{ width: '100%' }} />
            </Form.Item>

            <Form.Item
              name="logging_level"
              label="Logging Level"
              initialValue={20}
            >
              <Select
                options={[
                  { value: 10, label: 'DEBUG' },
                  { value: 20, label: 'INFO' },
                  { value: 30, label: 'WARNING' },
                  { value: 40, label: 'ERROR' },
                  { value: 50, label: 'CRITICAL' },
                ]}
              />
            </Form.Item>
          </Card>
        </TabPane>

        <TabPane tab="Environment Settings" key="2">
          <Card bordered={false}>
            <Form.Item
              name={['environment', 'weather']}
              label="Weather"
              initialValue="The weather is normal"
            >
              <Input placeholder="Enter weather description" />
            </Form.Item>

            <Form.Item
              name={['environment', 'temperature']}
              label="Temperature"
              initialValue="The temperature is normal"
            >
              <Input placeholder="Enter temperature description" />
            </Form.Item>

            <Form.Item
              name={['environment', 'workday']}
              label="Is Workday"
              valuePropName="checked"
              initialValue={true}
            >
              <Switch />
            </Form.Item>

            <Form.Item
              name={['environment', 'other_information']}
              label="Other Information"
              initialValue=""
            >
              <Input.TextArea rows={3} placeholder="Enter additional environment information" />
            </Form.Item>
          </Card>
        </TabPane>

        <TabPane tab="Message Intercept" key="3">
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
              initialValue={3}
            >
              <InputNumber min={1} style={{ width: '100%' }} />
            </Form.Item>
          </Card>
        </TabPane>

        <TabPane tab="Workflow Steps" key="4">
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
                            { value: WorkflowType.RUN, label: 'Run Simulation' },
                            { value: WorkflowType.FUNCTION, label: 'Execute Function' },
                            { value: WorkflowType.INTERVIEW, label: 'Interview Agents' },
                            { value: WorkflowType.SURVEY, label: 'Survey Agents' },
                            { value: WorkflowType.ENVIRONMENT_INTERVENE, label: 'Environment Intervention' },
                            { value: WorkflowType.UPDATE_STATE_INTERVENE, label: 'Update State Intervention' },
                            { value: WorkflowType.MESSAGE_INTERVENE, label: 'Message Intervention' },
                            { value: WorkflowType.INTERVENE, label: 'General Intervention' },
                          ]}
                        />
                      </Form.Item>

                      <Form.Item
                        {...restField}
                        name={[name, 'days']}
                        label="Days"
                        tooltip="Duration in days (for RUN type)"
                        initialValue={1.0}
                      >
                        <InputNumber min={0.1} step={0.1} style={{ width: '100%' }} />
                      </Form.Item>

                      <Form.Item
                        {...restField}
                        name={[name, 'times']}
                        label="Times"
                        tooltip="Number of repetitions (for RUN type)"
                        initialValue={1}
                      >
                        <InputNumber min={1} style={{ width: '100%' }} />
                      </Form.Item>

                      <Form.Item
                        {...restField}
                        name={[name, 'description']}
                        label="Description"
                      >
                        <Input placeholder="Enter step description" />
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

        <TabPane tab="Metrics" key="5">
          <Card bordered={false}>
            <Form.List name="metric_extractors">
              {(fields, { add, remove }) => (
                <>
                  {fields.map(({ key, name, ...restField }) => (
                    <Card 
                      key={key} 
                      title={`Metric ${name + 1}`} 
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
                            { value: MetricType.FUNCTION, label: 'Function' },
                            { value: MetricType.STATE, label: 'State' },
                          ]}
                        />
                      </Form.Item>

                      <Form.Item
                        {...restField}
                        name={[name, 'step_interval']}
                        label="Step Interval"
                        tooltip="Interval between metric extractions"
                        initialValue={1}
                      >
                        <InputNumber min={1} style={{ width: '100%' }} />
                      </Form.Item>

                      <Form.Item
                        {...restField}
                        name={[name, 'key']}
                        label="Metric Key"
                        tooltip="Key to identify this metric"
                      >
                        <Input placeholder="Enter metric key" />
                      </Form.Item>

                      <Form.Item
                        {...restField}
                        name={[name, 'method']}
                        label="Aggregation Method"
                      >
                        <Select
                          placeholder="Select aggregation method"
                          options={[
                            { value: 'mean', label: 'Mean' },
                            { value: 'sum', label: 'Sum' },
                            { value: 'max', label: 'Maximum' },
                            { value: 'min', label: 'Minimum' },
                          ]}
                        />
                      </Form.Item>

                      <Form.Item
                        {...restField}
                        name={[name, 'extract_time']}
                        label="Extract Time"
                        tooltip="The simulation time or step at which extraction occurs"
                        initialValue={0}
                      >
                        <InputNumber min={0} style={{ width: '100%' }} />
                      </Form.Item>

                      <Form.Item
                        {...restField}
                        name={[name, 'description']}
                        label="Description"
                      >
                        <Input placeholder="Enter metric description" />
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

export default WorkflowForm; 