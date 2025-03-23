import React from 'react';
import { Form, Input, InputNumber, Select, Card, Tabs, Collapse, Switch } from 'antd';
import { AgentConfig } from '../../types/config';

const { TabPane } = Tabs;
const { Panel } = Collapse;

interface AgentFormProps {
  value: Partial<AgentConfig>;
  onChange: (value: Partial<AgentConfig>) => void;
}

const AgentForm: React.FC<AgentFormProps> = ({ value, onChange }) => {
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
        <TabPane tab="Basic Configuration" key="1">
          <Card bordered={false}>
            <Form.Item
              name="number_of_citizen"
              label="Number of Citizens"
              rules={[{ required: true, message: 'Please enter number of citizens' }]}
              initialValue={10}
            >
              <InputNumber min={0} style={{ width: '100%' }} />
            </Form.Item>

            <Form.Item
              name="number_of_firm"
              label="Number of Firms"
              rules={[{ required: true, message: 'Please enter number of firms' }]}
              initialValue={1}
            >
              <InputNumber min={0} style={{ width: '100%' }} />
            </Form.Item>

            <Form.Item
              name="number_of_government"
              label="Number of Government Entities"
              rules={[{ required: true, message: 'Please enter number of government entities' }]}
              initialValue={1}
            >
              <InputNumber min={0} style={{ width: '100%' }} />
            </Form.Item>

            <Form.Item
              name="number_of_bank"
              label="Number of Banks"
              rules={[{ required: true, message: 'Please enter number of banks' }]}
              initialValue={1}
            >
              <InputNumber min={0} style={{ width: '100%' }} />
            </Form.Item>

            <Form.Item
              name="number_of_nbs"
              label="Number of NBS"
              rules={[{ required: true, message: 'Please enter number of NBS' }]}
              initialValue={0}
            >
              <InputNumber min={0} style={{ width: '100%' }} />
            </Form.Item>

            <Form.Item
              name="group_size"
              label="Group Size"
              rules={[{ required: true, message: 'Please enter group size' }]}
              initialValue={100}
            >
              <InputNumber min={1} style={{ width: '100%' }} />
            </Form.Item>
          </Card>
        </TabPane>

        <TabPane tab="Agent Profiles" key="2">
          <Card bordered={false}>
            <Collapse defaultActiveKey={['1']}>
              <Panel header="Demographic Distribution" key="1">
                <Form.Item
                  name={['memory_distributions', 'age', 'dist_type']}
                  label="Age Distribution"
                  initialValue="uniform_int"
                >
                  <Select
                    options={[
                      { value: 'uniform_int', label: 'Uniform Integer' },
                      { value: 'normal', label: 'Normal' },
                      { value: 'constant', label: 'Constant' },
                    ]}
                  />
                </Form.Item>
                
                <Form.Item
                  name={['memory_distributions', 'age', 'min_value']}
                  label="Minimum Age"
                  initialValue={18}
                >
                  <InputNumber min={0} style={{ width: '100%' }} />
                </Form.Item>
                
                <Form.Item
                  name={['memory_distributions', 'age', 'max_value']}
                  label="Maximum Age"
                  initialValue={80}
                >
                  <InputNumber min={0} style={{ width: '100%' }} />
                </Form.Item>

                <Form.Item
                  name={['memory_distributions', 'gender', 'dist_type']}
                  label="Gender Distribution"
                  initialValue="choice"
                >
                  <Select
                    options={[
                      { value: 'choice', label: 'Choice' },
                    ]}
                  />
                </Form.Item>
                
                <Form.Item
                  name={['memory_distributions', 'gender', 'choices']}
                  label="Gender Choices"
                  initialValue={['male', 'female']}
                >
                  <Select
                    mode="tags"
                    placeholder="Enter gender choices"
                  />
                </Form.Item>
                
                <Form.Item
                  name={['memory_distributions', 'gender', 'weights']}
                  label="Gender Weights"
                  initialValue={[0.5, 0.5]}
                >
                  <Select
                    mode="tags"
                    placeholder="Enter weights (must sum to 1)"
                  />
                </Form.Item>
              </Panel>

              <Panel header="Economic Profile" key="2">
                <Form.Item
                  name={['memory_distributions', 'income', 'dist_type']}
                  label="Income Distribution"
                  initialValue="uniform_float"
                >
                  <Select
                    options={[
                      { value: 'uniform_float', label: 'Uniform Float' },
                      { value: 'normal', label: 'Normal' },
                      { value: 'constant', label: 'Constant' },
                    ]}
                  />
                </Form.Item>
                
                <Form.Item
                  name={['memory_distributions', 'income', 'min_value']}
                  label="Minimum Income"
                  initialValue={3000}
                >
                  <InputNumber min={0} style={{ width: '100%' }} />
                </Form.Item>
                
                <Form.Item
                  name={['memory_distributions', 'income', 'max_value']}
                  label="Maximum Income"
                  initialValue={30000}
                >
                  <InputNumber min={0} style={{ width: '100%' }} />
                </Form.Item>
              </Panel>
            </Collapse>
          </Card>
        </TabPane>

        <TabPane tab="Advanced Configuration" key="3">
          <Card bordered={false}>
            <Form.Item
              name="extra_agent_class"
              label="Extra Agent Classes"
            >
              <Input.TextArea rows={4} placeholder="Enter extra agent classes configuration (JSON format)" />
            </Form.Item>

            <Form.Item
              name="agent_class_configs"
              label="Agent Class Configurations"
            >
              <Input.TextArea rows={4} placeholder="Enter agent class configurations (JSON format)" />
            </Form.Item>
          </Card>
        </TabPane>
      </Tabs>
    </Form>
  );
};

export default AgentForm; 