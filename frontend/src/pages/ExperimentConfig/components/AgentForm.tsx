import React from 'react';
import { Form, Input, InputNumber, Select, Card, Space, Button, Collapse, Upload, message, Tabs } from 'antd';
import { MinusCircleOutlined, PlusOutlined, UploadOutlined } from '@ant-design/icons';
import type { UploadProps } from 'antd';

const { Panel } = Collapse;
const { TabPane } = Tabs;

interface AgentFormProps {
  value: any;
  onChange: (value: any) => void;
  environmentConfig: any;
}

const AgentForm: React.FC<AgentFormProps> = ({ value, onChange, environmentConfig }) => {
  const [form] = Form.useForm();

  // Update parent component state when form values change
  const handleValuesChange = (_: any, allValues: any) => {
    onChange(allValues);
  };

  // Set initial values
  React.useEffect(() => {
    form.setFieldsValue(value);
  }, [form, value]);

  // File upload configuration
  const uploadProps: UploadProps = {
    name: 'file',
    action: '/api/upload',
    headers: {
      authorization: 'authorization-text',
    },
    onChange(info) {
      if (info.file.status !== 'uploading') {
        console.log(info.file, info.fileList);
      }
      if (info.file.status === 'done') {
        message.success(`${info.file.name} file uploaded successfully`);
        // Update script path in form
        const scriptPath = info.file.response.path;
        form.setFieldsValue({
          scriptPath,
        });
      } else if (info.file.status === 'error') {
        message.error(`${info.file.name} file upload failed`);
      }
    },
  };

  return (
    <Form
      form={form}
      layout="vertical"
      onValuesChange={handleValuesChange}
      initialValues={value}
    >
      <Card title="Basic Agent Configuration" bordered={false}>
        <Form.Item
          name={['agent_config', 'number_of_citizen']}
          label="Number of Agents"
          rules={[{ required: true, message: 'Please enter number of agents' }]}
        >
          <InputNumber min={1} max={10000} style={{ width: '100%' }} />
        </Form.Item>

        <Form.Item
          name="agentType"
          label="Agent Type"
          rules={[{ required: true, message: 'Please select agent type' }]}
        >
          <Select
            placeholder="Select agent type"
            options={[
              { value: 'llm', label: 'LLM-based Agent' },
              { value: 'rule', label: 'Rule-based Agent' },
              { value: 'hybrid', label: 'Hybrid Agent' },
            ]}
          />
        </Form.Item>

        <Form.Item
          name="scriptType"
          label="Script Type"
          rules={[{ required: true, message: 'Please select script type' }]}
        >
          <Select
            placeholder="Select script type"
            options={[
              { value: 'python', label: 'Python' },
              { value: 'javascript', label: 'JavaScript' },
              { value: 'custom', label: 'Custom' },
            ]}
          />
        </Form.Item>

        <Form.Item
          name="scriptPath"
          label="Agent Script"
          rules={[{ required: true, message: 'Please upload or enter script path' }]}
        >
          <Input placeholder="Script path" addonAfter={
            <Upload {...uploadProps}>
              <Button icon={<UploadOutlined />}>Upload</Button>
            </Upload>
          } />
        </Form.Item>
      </Card>

      <Card title="Agent Profile Configuration" bordered={false} style={{ marginTop: 16 }}>
        <Tabs defaultActiveKey="1">
          <TabPane tab="Demographics" key="1">
            <Form.Item
              name={['profile', 'name']}
              label="Name Generation"
            >
              <Select
                placeholder="Select name generation method"
                options={[
                  { value: 'random', label: 'Random from predefined list' },
                  { value: 'custom', label: 'Custom names' },
                ]}
              />
            </Form.Item>

            <Form.Item
              name={['profile', 'gender']}
              label="Gender Distribution"
            >
              <Select
                placeholder="Select gender distribution"
                options={[
                  { value: 'equal', label: 'Equal distribution' },
                  { value: 'custom', label: 'Custom distribution' },
                ]}
              />
            </Form.Item>

            <Form.Item
              name={['profile', 'age', 'min']}
              label="Minimum Age"
            >
              <InputNumber min={1} max={100} style={{ width: '100%' }} />
            </Form.Item>

            <Form.Item
              name={['profile', 'age', 'max']}
              label="Maximum Age"
            >
              <InputNumber min={1} max={100} style={{ width: '100%' }} />
            </Form.Item>

            <Form.Item
              name={['profile', 'education']}
              label="Education Distribution"
            >
              <Select
                mode="multiple"
                placeholder="Select education levels"
                options={[
                  { value: 'Doctor', label: 'Doctor' },
                  { value: 'Master', label: 'Master' },
                  { value: 'Bachelor', label: 'Bachelor' },
                  { value: 'College', label: 'College' },
                  { value: 'High School', label: 'High School' },
                ]}
              />
            </Form.Item>

            <Form.Item
              name={['profile', 'race']}
              label="Race Distribution"
            >
              <Select
                mode="multiple"
                placeholder="Select races"
                options={[
                  { value: 'Chinese', label: 'Chinese' },
                  { value: 'American', label: 'American' },
                  { value: 'British', label: 'British' },
                  { value: 'French', label: 'French' },
                  { value: 'German', label: 'German' },
                  { value: 'Japanese', label: 'Japanese' },
                  { value: 'Korean', label: 'Korean' },
                  { value: 'Russian', label: 'Russian' },
                  { value: 'Other', label: 'Other' },
                ]}
              />
            </Form.Item>

            <Form.Item
              name={['profile', 'religion']}
              label="Religion Distribution"
            >
              <Select
                mode="multiple"
                placeholder="Select religions"
                options={[
                  { value: 'none', label: 'None' },
                  { value: 'Christian', label: 'Christian' },
                  { value: 'Muslim', label: 'Muslim' },
                  { value: 'Buddhist', label: 'Buddhist' },
                  { value: 'Hindu', label: 'Hindu' },
                  { value: 'Other', label: 'Other' },
                ]}
              />
            </Form.Item>

            <Form.Item
              name={['profile', 'marital_status']}
              label="Marital Status Distribution"
            >
              <Select
                mode="multiple"
                placeholder="Select marital statuses"
                options={[
                  { value: 'not married', label: 'Not Married' },
                  { value: 'married', label: 'Married' },
                  { value: 'divorced', label: 'Divorced' },
                  { value: 'widowed', label: 'Widowed' },
                ]}
              />
            </Form.Item>
          </TabPane>

          <TabPane tab="Socioeconomic" key="2">
            <Form.Item
              name={['profile', 'occupation']}
              label="Occupation Distribution"
            >
              <Select
                mode="multiple"
                placeholder="Select occupations"
                options={[
                  { value: 'Student', label: 'Student' },
                  { value: 'Teacher', label: 'Teacher' },
                  { value: 'Doctor', label: 'Doctor' },
                  { value: 'Engineer', label: 'Engineer' },
                  { value: 'Manager', label: 'Manager' },
                  { value: 'Businessman', label: 'Businessman' },
                  { value: 'Artist', label: 'Artist' },
                  { value: 'Athlete', label: 'Athlete' },
                  { value: 'Other', label: 'Other' },
                ]}
              />
            </Form.Item>

            <Form.Item
              name={['profile', 'skill']}
              label="Skill Distribution"
            >
              <Select
                mode="multiple"
                placeholder="Select skills"
                options={[
                  { value: 'Good at problem-solving', label: 'Problem-solving' },
                  { value: 'Good at communication', label: 'Communication' },
                  { value: 'Good at creativity', label: 'Creativity' },
                  { value: 'Good at teamwork', label: 'Teamwork' },
                  { value: 'Other', label: 'Other' },
                ]}
              />
            </Form.Item>

            <Form.Item
              name={['profile', 'income', 'min']}
              label="Minimum Income"
            >
              <InputNumber min={0} style={{ width: '100%' }} />
            </Form.Item>

            <Form.Item
              name={['profile', 'income', 'max']}
              label="Maximum Income"
            >
              <InputNumber min={0} style={{ width: '100%' }} />
            </Form.Item>

            <Form.Item
              name={['profile', 'currency', 'min']}
              label="Minimum Currency"
            >
              <InputNumber min={0} style={{ width: '100%' }} />
            </Form.Item>

            <Form.Item
              name={['profile', 'currency', 'max']}
              label="Maximum Currency"
            >
              <InputNumber min={0} style={{ width: '100%' }} />
            </Form.Item>

            <Form.Item
              name={['profile', 'consumption']}
              label="Consumption Level Distribution"
            >
              <Select
                mode="multiple"
                placeholder="Select consumption levels"
                options={[
                  { value: 'low', label: 'Low' },
                  { value: 'slightly low', label: 'Slightly Low' },
                  { value: 'medium', label: 'Medium' },
                  { value: 'slightly high', label: 'Slightly High' },
                  { value: 'high', label: 'High' },
                ]}
              />
            </Form.Item>

            <Form.Item
              name={['profile', 'family_consumption']}
              label="Family Consumption Distribution"
            >
              <Select
                mode="multiple"
                placeholder="Select family consumption levels"
                options={[
                  { value: 'low', label: 'Low' },
                  { value: 'medium', label: 'Medium' },
                  { value: 'high', label: 'High' },
                ]}
              />
            </Form.Item>
          </TabPane>

          <TabPane tab="Personality & Location" key="3">
            <Form.Item
              name={['profile', 'personality']}
              label="Personality Distribution"
            >
              <Select
                mode="multiple"
                placeholder="Select personality types"
                options={[
                  { value: 'outgoint', label: 'Outgoing' },
                  { value: 'introvert', label: 'Introvert' },
                  { value: 'ambivert', label: 'Ambivert' },
                  { value: 'extrovert', label: 'Extrovert' },
                ]}
              />
            </Form.Item>

            <Form.Item
              name={['profile', 'residence']}
              label="Residence Distribution"
            >
              <Select
                mode="multiple"
                placeholder="Select residence types"
                options={[
                  { value: 'city', label: 'City' },
                  { value: 'suburb', label: 'Suburb' },
                  { value: 'rural', label: 'Rural' },
                ]}
              />
            </Form.Item>

            <Form.Item
              name={['profile', 'city']}
              label="City"
            >
              <Input placeholder="Enter city name" />
            </Form.Item>

            <Form.Item
              name={['base', 'home', 'aoi_position', 'aoi_id']}
              label="Home AOI ID Range"
              tooltip="Area of Interest ID for home locations"
            >
              <InputNumber min={1} style={{ width: '100%' }} />
            </Form.Item>

            <Form.Item
              name={['base', 'work', 'aoi_position', 'aoi_id']}
              label="Work AOI ID Range"
              tooltip="Area of Interest ID for work locations"
            >
              <InputNumber min={1} style={{ width: '100%' }} />
            </Form.Item>
          </TabPane>
        </Tabs>
      </Card>

      <Card title="Advanced Configuration" bordered={false} style={{ marginTop: 16 }}>
        <Collapse>
          <Panel header="Agent Distribution" key="1">
            <Form.Item
              name="distributionType"
              label="Distribution Type"
            >
              <Select
                placeholder="Select distribution type"
                options={[
                  { value: 'random', label: 'Random Distribution' },
                  { value: 'cluster', label: 'Cluster Distribution' },
                  { value: 'uniform', label: 'Uniform Distribution' },
                ]}
              />
            </Form.Item>

            <Form.Item
              name="distributionParams"
              label="Distribution Parameters"
            >
              <Input.TextArea rows={4} placeholder="Enter distribution parameters (JSON format)" />
            </Form.Item>
          </Panel>

          <Panel header="Agent Interaction Rules" key="2">
            <Form.Item
              name="interactionRules"
              label="Interaction Rules"
            >
              <Input.TextArea rows={4} placeholder="Enter interaction rules (JSON format)" />
            </Form.Item>
          </Panel>
        </Collapse>
      </Card>
    </Form>
  );
};

export default AgentForm; 