import React, { useState } from 'react';
import { Form, Input, InputNumber, Select, Card, Space, Button, Collapse, Upload, message, Tabs, Divider, Typography, Radio } from 'antd';
import { InboxOutlined, UploadOutlined } from '@ant-design/icons';
import type { UploadProps, UploadFile } from 'antd';

const { Panel } = Collapse;
const { TabPane } = Tabs;
const { Dragger } = Upload;
const { Title, Text } = Typography;

interface AgentFormProps {
  value: Record<string, unknown>;
  onChange: (value: Record<string, unknown>) => void;
  environmentConfig: Record<string, unknown>;
}

const AgentForm: React.FC<AgentFormProps> = ({ value, onChange }) => {
  const [form] = Form.useForm();
  const [fileList, setFileList] = useState<UploadFile[]>([]);
  const [uploadMode, setUploadMode] = useState<'form' | 'file'>('form');

  // Update parent component state when form values change
  const handleValuesChange = (_: unknown, allValues: Record<string, unknown>) => {
    onChange(allValues);
  };

  // Set initial values
  React.useEffect(() => {
    form.setFieldsValue(value);
  }, [form, value]);

  // File upload configuration for agent script
  const scriptUploadProps: UploadProps = {
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

  // Configuration file upload props
  const configUploadProps: UploadProps = {
    name: 'file',
    multiple: false,
    maxCount: 1,
    accept: '.json,.yaml,.yml',
    fileList: fileList,
    beforeUpload: (file) => {
      const isJsonOrYaml = file.type === 'application/json' ||
        file.name.endsWith('.yaml') ||
        file.name.endsWith('.yml');
      if (!isJsonOrYaml) {
        message.error('You can only upload JSON or YAML files!');
        return Upload.LIST_IGNORE;
      }

      setFileList([file]);

      // Read file content
      const reader = new FileReader();
      reader.onload = (e) => {
        try {
          let configData;
          if (file.type === 'application/json' || file.name.endsWith('.json')) {
            configData = JSON.parse(e.target?.result as string);
          } else {
            // For YAML files, we would need a YAML parser
            // This is a simplified version - in production, you'd use a proper YAML parser
            message.info('YAML parsing would be implemented in production');
            return;
          }

          // Update form with the loaded configuration
          form.setFieldsValue(configData);
          onChange(configData);
          message.success(`${file.name} configuration loaded successfully`);
        } catch (error) {
          message.error('Failed to parse configuration file');
          console.error(error);
        }
      };
      reader.readAsText(file);

      // Prevent default upload behavior
      return false;
    },
    onRemove: () => {
      setFileList([]);
      return true;
    },
  };

  const toggleMode = () => {
    setUploadMode(uploadMode === 'form' ? 'file' : 'form');
  };

  return (
    <>
      <Card style={{ marginBottom: 16 }}>
        <Space direction="vertical" style={{ width: '100%' }}>
          <Title level={5}>Configuration Method</Title>
          <Text>Choose how you want to configure agent profiles:</Text>
          <Radio.Group value={uploadMode} onChange={(e) => setUploadMode(e.target.value)}>
            <Radio.Button value="form">Form Input</Radio.Button>
            <Radio.Button value="file">Upload Configuration File</Radio.Button>
          </Radio.Group>
        </Space>
      </Card>

      {uploadMode === 'file' ? (
        <Card title="Upload Agent Configuration File" bordered={false}>
          <Dragger {...configUploadProps}>
            <p className="ant-upload-drag-icon">
              <InboxOutlined />
            </p>
            <p className="ant-upload-text">Click or drag file to this area to upload</p>
            <p className="ant-upload-hint">
              Support for a single JSON or YAML file upload. The file should contain the complete agent configuration.
            </p>
          </Dragger>
          <Divider />
          <Button type="primary" onClick={toggleMode}>
            Switch to Form Input
          </Button>
        </Card>
      ) : (
        <Form
          form={form}
          layout="vertical"
          onValuesChange={handleValuesChange}
          initialValues={value}
        >
          <Card title="Basic Agent Configuration" bordered={false}>
            <Form.Item
              name={['agent_config', 'number_of_citizen']}
              label="Number of Citizens"
              rules={[{ required: true, message: 'Please enter number of citizens' }]}
            >
              <InputNumber min={1} max={10000} style={{ width: '100%' }} />
            </Form.Item>

            <Form.Item
              name={['agent_config', 'number_of_firm']}
              label="Number of Firms"
              rules={[{ required: true, message: 'Please enter number of firms' }]}
            >
              <InputNumber min={1} max={1000} style={{ width: '100%' }} />
            </Form.Item>

            <Form.Item
              name={['agent_config', 'number_of_government']}
              label="Number of Government Agencies"
              rules={[{ required: true, message: 'Please enter number of government agencies' }]}
            >
              <InputNumber min={1} max={100} style={{ width: '100%' }} />
            </Form.Item>

            <Form.Item
              name={['agent_config', 'number_of_bank']}
              label="Number of Banks"
              rules={[{ required: true, message: 'Please enter number of banks' }]}
            >
              <InputNumber min={1} max={100} style={{ width: '100%' }} />
            </Form.Item>

            <Form.Item
              name={['agent_config', 'number_of_nbs']}
              label="Number of NBS"
              rules={[{ required: true, message: 'Please enter number of NBs' }]}
            >
              <InputNumber min={1} max={100} style={{ width: '100%' }} />
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

            </Collapse>
            <Divider />
            <Button type="primary" onClick={toggleMode}>
              Switch to File Upload
            </Button>
          </Card>
        </Form>
      )}
    </>
  );
};

export default AgentForm; 