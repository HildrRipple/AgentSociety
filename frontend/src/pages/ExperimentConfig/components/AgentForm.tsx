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
          <Tabs defaultActiveKey="1">
            <TabPane tab="Basic Agent Configuration" key="1">
              <Card bordered={false}>
                <Form.Item
                  name={['agent_config', 'number_of_citizen']}
                  label="Number of Citizens"
                  rules={[{ required: true, message: 'Please enter number of citizens' }]}
                >
                  <InputNumber min={1} max={10000} defaultValue={1} style={{ width: '100%' }} />
                </Form.Item>

                <Form.Item
                  name={['agent_config', 'number_of_firm']}
                  label="Number of Firms"
                  rules={[{ required: true, message: 'Please enter number of firms' }]}
                >
                  <InputNumber min={1} max={1000} defaultValue={1} style={{ width: '100%' }} />
                </Form.Item>

                <Form.Item
                  name={['agent_config', 'number_of_government']}
                  label="Number of Government Agencies"
                  rules={[{ required: true, message: 'Please enter number of government agencies' }]}
                >
                  <InputNumber min={1} max={100} defaultValue={1} style={{ width: '100%' }} />
                </Form.Item>

                <Form.Item
                  name={['agent_config', 'number_of_bank']}
                  label="Number of Banks"
                  rules={[{ required: true, message: 'Please enter number of banks' }]}
                >
                  <InputNumber min={1} max={100} defaultValue={1} style={{ width: '100%' }} />
                </Form.Item>

                <Form.Item
                  name={['agent_config', 'number_of_nbs']}
                  label="Number of Neighborhood-based Services"
                  rules={[{ required: true, message: 'Please enter number of NBS' }]}
                >
                  <InputNumber min={1} max={100} defaultValue={1} style={{ width: '100%' }} />
                </Form.Item>

                <Form.Item
                  name={['agent_config', 'group_size']}
                  label="Group Size"
                  rules={[{ required: true, message: 'Please enter group size' }]}
                >
                  <InputNumber min={1} max={1000} defaultValue={100} style={{ width: '100%' }} />
                </Form.Item>
              </Card>
            </TabPane>

            <TabPane tab="Agent Profiles" key="2">
              <Card bordered={false}>
                <Form.Item
                  name="scriptPath"
                  label="Agent Script"
                >
                  <Input placeholder="Script path" addonAfter={
                    <Upload {...scriptUploadProps}>
                      <Button icon={<UploadOutlined />}>Upload</Button>
                    </Upload>
                  } />
                </Form.Item>

                <Collapse>
                  <Panel header="Memory Configuration" key="1">
                    <Form.Item
                      name={['agent_config', 'memory_config', 'memory_from_file']}
                      label="Memory From File"
                    >
                      <Input.TextArea rows={4} placeholder="Enter memory from file configuration (JSON format)" />
                    </Form.Item>

                    <Form.Item
                      name={['agent_config', 'memory_config', 'memory_distributions']}
                      label="Memory Distributions"
                    >
                      <Input.TextArea rows={4} placeholder="Enter memory distributions configuration (JSON format)" />
                    </Form.Item>
                  </Panel>
                </Collapse>
              </Card>
            </TabPane>

            <TabPane tab="Profile Distributions" key="3">
              <Card bordered={false}>
                <Collapse>
                  <Panel header="Name Distribution" key="name">
                    <Form.Item
                      name={['profile', 'name', 'dist_type']}
                      label="Distribution Type"
                    >
                      <Select
                        placeholder="Select distribution type"
                        options={[
                          { value: 'choice', label: 'Choice' },
                          { value: 'constant', label: 'Constant' },
                        ]}
                      />
                    </Form.Item>
                    <Form.Item
                      name={['profile', 'name', 'choices']}
                      label="Choices"
                    >
                      <Select
                        mode="tags"
                        placeholder="Enter name choices"
                        style={{ width: '100%' }}
                        options={[
                          { value: 'Alice', label: 'Alice' },
                          { value: 'Bob', label: 'Bob' },
                          { value: 'Charlie', label: 'Charlie' },
                          { value: 'David', label: 'David' },
                          { value: 'Eve', label: 'Eve' },
                        ]}
                      />
                    </Form.Item>
                  </Panel>

                  <Panel header="Gender Distribution" key="gender">
                    <Form.Item
                      name={['profile', 'gender', 'dist_type']}
                      label="Distribution Type"
                    >
                      <Select
                        placeholder="Select distribution type"
                        options={[
                          { value: 'choice', label: 'Choice' },
                          { value: 'constant', label: 'Constant' },
                        ]}
                      />
                    </Form.Item>
                    <Form.Item
                      name={['profile', 'gender', 'choices']}
                      label="Choices"
                    >
                      <Select
                        mode="tags"
                        placeholder="Enter gender choices"
                        style={{ width: '100%' }}
                        options={[
                          { value: 'male', label: 'Male' },
                          { value: 'female', label: 'Female' },
                        ]}
                      />
                    </Form.Item>
                    <Form.Item
                      name={['profile', 'gender', 'weights']}
                      label="Weights"
                    >
                      <Input placeholder="Enter weights as comma-separated values (e.g., 0.5,0.5)" />
                    </Form.Item>
                  </Panel>

                  <Panel header="Age Distribution" key="age">
                    <Form.Item
                      name={['profile', 'age', 'dist_type']}
                      label="Distribution Type"
                    >
                      <Select
                        placeholder="Select distribution type"
                        options={[
                          { value: 'uniform_int', label: 'Uniform Integer' },
                          { value: 'normal', label: 'Normal' },
                          { value: 'constant', label: 'Constant' },
                        ]}
                      />
                    </Form.Item>
                    <Form.Item
                      name={['profile', 'age', 'min_value']}
                      label="Minimum Value"
                    >
                      <InputNumber min={1} max={100} style={{ width: '100%' }} />
                    </Form.Item>
                    <Form.Item
                      name={['profile', 'age', 'max_value']}
                      label="Maximum Value"
                    >
                      <InputNumber min={1} max={100} style={{ width: '100%' }} />
                    </Form.Item>
                    <Form.Item
                      name={['profile', 'age', 'mean']}
                      label="Mean (for Normal distribution)"
                    >
                      <InputNumber style={{ width: '100%' }} />
                    </Form.Item>
                    <Form.Item
                      name={['profile', 'age', 'std']}
                      label="Standard Deviation (for Normal distribution)"
                    >
                      <InputNumber min={0} style={{ width: '100%' }} />
                    </Form.Item>
                  </Panel>

                  <Panel header="Education Distribution" key="education">
                    <Form.Item
                      name={['profile', 'education', 'dist_type']}
                      label="Distribution Type"
                    >
                      <Select
                        placeholder="Select distribution type"
                        options={[
                          { value: 'choice', label: 'Choice' },
                          { value: 'constant', label: 'Constant' },
                        ]}
                      />
                    </Form.Item>
                    <Form.Item
                      name={['profile', 'education', 'choices']}
                      label="Choices"
                    >
                      <Select
                        mode="tags"
                        placeholder="Enter education choices"
                        style={{ width: '100%' }}
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
                      name={['profile', 'education', 'weights']}
                      label="Weights"
                    >
                      <Input placeholder="Enter weights as comma-separated values" />
                    </Form.Item>
                  </Panel>

                  <Panel header="Occupation Distribution" key="occupation">
                    <Form.Item
                      name={['profile', 'occupation', 'dist_type']}
                      label="Distribution Type"
                    >
                      <Select
                        placeholder="Select distribution type"
                        options={[
                          { value: 'choice', label: 'Choice' },
                          { value: 'constant', label: 'Constant' },
                        ]}
                      />
                    </Form.Item>
                    <Form.Item
                      name={['profile', 'occupation', 'choices']}
                      label="Choices"
                    >
                      <Select
                        mode="tags"
                        placeholder="Enter occupation choices"
                        style={{ width: '100%' }}
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
                  </Panel>

                  <Panel header="Income Distribution" key="income">
                    <Form.Item
                      name={['profile', 'income', 'dist_type']}
                      label="Distribution Type"
                    >
                      <Select
                        placeholder="Select distribution type"
                        options={[
                          { value: 'uniform_float', label: 'Uniform Float' },
                          { value: 'normal', label: 'Normal' },
                          { value: 'constant', label: 'Constant' },
                        ]}
                      />
                    </Form.Item>
                    <Form.Item
                      name={['profile', 'income', 'min_value']}
                      label="Minimum Value"
                    >
                      <InputNumber min={0} style={{ width: '100%' }} />
                    </Form.Item>
                    <Form.Item
                      name={['profile', 'income', 'max_value']}
                      label="Maximum Value"
                    >
                      <InputNumber min={0} style={{ width: '100%' }} />
                    </Form.Item>
                  </Panel>
                </Collapse>
              </Card>
            </TabPane>

            <TabPane tab="Advanced Configuration" key="4">
              <Card bordered={false}>
                <Form.Item
                  name={['agent_config', 'extra_agent_class']}
                  label="Extra Agent Classes"
                >
                  <Input.TextArea rows={4} placeholder="Enter extra agent classes configuration (JSON format)" />
                </Form.Item>

                <Form.Item
                  name={['agent_config', 'agent_class_configs']}
                  label="Agent Class Configurations"
                >
                  <Input.TextArea rows={4} placeholder="Enter agent class configurations (JSON format)" />
                </Form.Item>
              </Card>
            </TabPane>
          </Tabs>

          <Divider />
          <Button type="primary" onClick={toggleMode}>
            Switch to File Upload
          </Button>
        </Form>
      )}
    </>
  );
};

export default AgentForm; 