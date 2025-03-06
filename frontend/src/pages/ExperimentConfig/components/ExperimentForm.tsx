import React from 'react';
import { Form, Input, InputNumber, DatePicker, Select, Card, Switch, Radio, Space, Divider, Button } from 'antd';
import type { RadioChangeEvent } from 'antd';
import { InfoCircleOutlined, PlusOutlined, MinusCircleOutlined } from '@ant-design/icons';

const { RangePicker } = DatePicker;
const { TextArea } = Input;

interface ExperimentFormProps {
  value: any;
  onChange: (value: any) => void;
  environmentConfig: any;
  agentConfig: any;
}

const ExperimentForm: React.FC<ExperimentFormProps> = ({ 
  value, 
  onChange, 
  environmentConfig, 
  agentConfig 
}) => {
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
      <Card title="Experiment Basic Information" bordered={false}>
        <Form.Item
          name="experimentName"
          label="Experiment Name"
          rules={[{ required: true, message: 'Please enter experiment name' }]}
        >
          <Input placeholder="Enter experiment name" />
        </Form.Item>

        <Form.Item
          name="experimentDescription"
          label="Experiment Description"
        >
          <TextArea rows={4} placeholder="Enter experiment description" />
        </Form.Item>

        <Form.Item
          name="tags"
          label="Tags"
        >
          <Select
            mode="tags"
            style={{ width: '100%' }}
            placeholder="Enter tags"
            options={[
              { value: 'urban', label: 'Urban' },
              { value: 'transportation', label: 'Transportation' },
              { value: 'social', label: 'Social' },
              { value: 'economic', label: 'Economic' },
            ]}
          />
        </Form.Item>
      </Card>

      <Card title="Workflow Configuration" bordered={false} style={{ marginTop: 16 }}>
        <Form.List name="workflow">
          {(fields, { add, remove }) => (
            <>
              {fields.map(({ key, name, ...restField }) => (
                <Space key={key} style={{ display: 'flex', marginBottom: 16 }} align="baseline">
                  <Form.Item
                    {...restField}
                    name={[name, 'type']}
                    rules={[{ required: true, message: 'Please select workflow type' }]}
                  >
                    <Select
                      placeholder="Select type"
                      style={{ width: 120 }}
                      options={[
                        { value: 'run', label: 'Run' },
                        { value: 'pause', label: 'Pause' },
                        { value: 'checkpoint', label: 'Checkpoint' },
                      ]}
                    />
                  </Form.Item>
                  <Form.Item
                    {...restField}
                    name={[name, 'days']}
                    rules={[{ required: true, message: 'Please enter days' }]}
                  >
                    <InputNumber min={0.1} step={0.1} placeholder="Days" />
                  </Form.Item>
                  <MinusCircleOutlined onClick={() => remove(name)} />
                </Space>
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

    </Form>
  );
};

export default ExperimentForm; 