import React, { useEffect, useState } from 'react';
import { Form, Input, InputNumber, Select, Card, Tabs, Button, Space, Radio, message, Row, Col } from 'antd';
import { AgentConfig, AgentsConfig } from '../../types/config';
import { PlusOutlined, MinusCircleOutlined } from '@ant-design/icons';
import { fetchCustom } from '../../components/fetch';

const { TabPane } = Tabs;
const { Option } = Select;

interface AgentTemplate {
  id: string;
  name: string;
  description: string;
  // ... 其他字段
}

interface AgentFormProps {
  value: Partial<AgentsConfig>;
  onChange: (value: Partial<AgentsConfig>) => void;
}

const AgentForm: React.FC<AgentFormProps> = ({ value, onChange }) => {
  const [form] = Form.useForm();
  const [activeTab, setActiveTab] = React.useState('1');
  const [citizenConfigMode, setCitizenConfigMode] = React.useState('manual');
  const [selectedProfile, setSelectedProfile] = React.useState('');
  const [distributionsState, setDistributionsState] = React.useState({});
  const addDistributionRef = React.useRef(null);
  const [manualDistributions, setManualDistributions] = React.useState({});
  const [templates, setTemplates] = useState<AgentTemplate[]>([]);
  const [loading, setLoading] = useState(false);

  // Define agent type options
  const agentClassOptions = [
    { label: 'Citizen', value: 'citizen' },
    { label: 'Firm', value: 'firm' },
    { label: 'Government', value: 'government' },
    { label: 'Bank', value: 'bank' },
    { label: 'NBS', value: 'nbs' },
  ];

  // Define distribution type options
  const distributionTypeOptions = [
    { label: 'Choice', value: 'choice' },
    { label: 'Uniform Integer', value: 'uniform_int' },
    { label: 'Uniform Float', value: 'uniform_float' },
    { label: 'Normal', value: 'normal' },
    { label: 'Constant', value: 'constant' },
  ];

  // Initialize distributionsState when component mounts
  React.useEffect(() => {
    const formValues = form.getFieldsValue();
    
    if (formValues.citizenGroups) {
      const newDistributionsState = {};
      
      formValues.citizenGroups.forEach((group, index) => {
        if (group.memory_distributions) {
          // Ensure each distribution item has a unique ID
          newDistributionsState[index] = group.memory_distributions.map(dist => ({
            ...dist,
            id: dist.id || Date.now() + Math.random()
          }));
        } else {
          // If no distribution items, initialize as empty array
          newDistributionsState[index] = [];
        }
      });
      
      setDistributionsState(newDistributionsState);
    }
  }, []);

  // Load templates
  useEffect(() => {
    const loadTemplates = async () => {
      setLoading(true);
      try {
        const response = await fetchCustom('/api/agent-templates');
        if (response.ok) {
          const data = await response.json();
          setTemplates(data.data);
        } else {
          message.error('Failed to load templates');
        }
      } catch (error) {
        message.error('Error loading templates');
      } finally {
        setLoading(false);
      }
    };

    loadTemplates();
  }, []);

  // Handle profile selection
  const handleProfileSelect = (profileId) => {
    setSelectedProfile(profileId);
    
    // Update form values based on selected profile
    const formValues = form.getFieldsValue();
    if (!formValues.citizenGroups) {
      formValues.citizenGroups = [{}];
    }
    
    formValues.citizenGroups[0].profile_id = profileId;
    form.setFieldsValue(formValues);
    
    // Update parent component
    onChange(formValues);
  };

  // Render distribution form based on type
  const renderDistributionForm = (type, basePath) => {
    switch (type) {
      case 'choice':
        return (
          <Form.Item
            name={[...basePath, 'params', 'choices']}
            label="Choices (comma separated)"
            rules={[{ required: true, message: 'Please enter choices' }]}
          >
            <Input placeholder="e.g. option1, option2, option3" />
          </Form.Item>
        );
      case 'uniform_int':
      case 'uniform_float':
        return (
          <>
            <Form.Item
              name={[...basePath, 'params', 'low']}
              label="Minimum Value"
              rules={[{ required: true, message: 'Please enter minimum value' }]}
              initialValue={0}
            >
              <InputNumber style={{ width: '100%' }} step={0.1} />
            </Form.Item>
            <Form.Item
              name={[...basePath, 'params', 'high']}
              label="Maximum Value"
              rules={[{ required: true, message: 'Please enter maximum value' }]}
              initialValue={1}
            >
              <InputNumber style={{ width: '100%' }} step={0.1} />
            </Form.Item>
          </>
        );
      case 'normal':
        return (
          <>
            <Form.Item
              name={[...basePath, 'params', 'loc']}
              label="Mean"
              rules={[{ required: true, message: 'Please enter mean value' }]}
              initialValue={0}
            >
              <InputNumber style={{ width: '100%' }} step={0.1} />
            </Form.Item>
            <Form.Item
              name={[...basePath, 'params', 'scale']}
              label="Standard Deviation"
              rules={[{ required: true, message: 'Please enter standard deviation' }]}
              initialValue={1}
            >
              <InputNumber style={{ width: '100%' }} step={0.1} min={0} />
            </Form.Item>
          </>
        );
      case 'constant':
        return (
          <Form.Item
            name={[...basePath, 'params', 'val']}
            label="Value"
            rules={[{ required: true, message: 'Please enter constant value' }]}
            initialValue=""
          >
            <Input />
          </Form.Item>
        );
      default:
        return null;
    }
  };

  return (
    <>
      <Card bordered={false}>
        <Form
          form={form}
          layout="vertical"
          initialValues={value}
          onValuesChange={(_, allValues) => {
            onChange(allValues);
          }}
        >
          <Tabs activeKey={activeTab} onChange={setActiveTab}>
            <TabPane tab="Citizens" key="1">
              <Card bordered={false}>
                <Form.Item label="Configuration Mode">
                  <Radio.Group
                    value={citizenConfigMode}
                    onChange={(e) => setCitizenConfigMode(e.target.value)}
                  >
                    <Radio.Button value="manual">Manual</Radio.Button>
                    <Radio.Button value="profile">Use Profile</Radio.Button>
                  </Radio.Group>
                </Form.Item>
                
                {citizenConfigMode === 'profile' ? (
                  <Form.List name="citizenGroups" initialValue={[{}]}>
                    {(fields, { add, remove }) => (
                      <>
                        {fields.map(({ key, name, ...restField }) => (
                          <Card
                            key={key}
                            title={`Citizen Group ${name + 1}`}
                            style={{ marginBottom: 16 }}
                            extra={
                              fields.length > 1 ? (
                                <MinusCircleOutlined onClick={() => remove(name)} />
                              ) : null
                            }
                          >
                            <Form.Item
                              {...restField}
                              name={[name, 'profile_id']}
                              label="Select Profile"
                              rules={[{ required: true, message: 'Please select a profile' }]}
                            >
                              <Select
                                placeholder="Select a profile"
                                loading={false}
                                onChange={(value) => handleProfileSelect(value)}
                              >
                                {/* Profile options will be populated here */}
                              </Select>
                            </Form.Item>
                          </Card>
                        ))}
                        <Button
                          type="dashed"
                          onClick={() => add({})}
                          block
                          icon={<PlusOutlined />}
                        >
                          Add Citizen Group
                        </Button>
                      </>
                    )}
                  </Form.List>
                ) : (
                  <Form.List name="citizenGroups" initialValue={[{ number: 10 }]}>
                    {(fields, { add, remove }) => (
                      <>
                        {fields.map(({ key, name, ...restField }) => (
                          <Card
                            key={key}
                            title={`Citizen Group ${name + 1}`}
                            style={{ marginBottom: 16 }}
                            extra={
                              fields.length > 1 ? (
                                <MinusCircleOutlined onClick={() => remove(name)} />
                              ) : null
                            }
                          >
                            <Form.Item
                              {...restField}
                              name={[name, 'number']}
                              label="Number of Citizens"
                              rules={[{ required: true, message: 'Please enter number of citizens' }]}
                            >
                              <InputNumber min={1} style={{ width: '100%' }} />
                            </Form.Item>
                            
                            <Form.List
                              name={[name, 'memory_distributions']}
                              initialValue={[{
                                name: '',
                                distribution: {
                                  type: 'constant',
                                  params: { val: '' }
                                }
                              }]}
                            >
                              {(fields, { add, remove }) => (
                                <>
                                  {fields.map(({ key, name: distName, ...restField }) => (
                                    <Card
                                      key={key}
                                      title={`Distribution ${distName + 1}`}
                                      style={{ marginBottom: 8 }}
                                      size="small"
                                      extra={
                                        <Button
                                          icon={<MinusCircleOutlined />}
                                          onClick={() => remove(distName)}
                                          size="small"
                                          danger
                                        />
                                      }
                                    >
                                      <Form.Item
                                        {...restField}
                                        name={[distName, 'name']}
                                        label="Attribute Name"
                                        rules={[{ required: true, message: 'Please enter attribute name' }]}
                                      >
                                        <Input placeholder="e.g. age, income" />
                                      </Form.Item>
                                      
                                      <Form.Item
                                        {...restField}
                                        name={[distName, 'distribution', 'type']}
                                        label="Distribution Type"
                                        rules={[{ required: true, message: 'Please select distribution type' }]}
                                        initialValue="constant"
                                      >
                                        <Select
                                          options={distributionTypeOptions}
                                          onChange={(value) => {
                                            // Reset params when distribution type changes
                                            const currentValues = form.getFieldsValue();
                                            let defaultParams = {};
                                            
                                            switch (value) {
                                              case 'choice':
                                                defaultParams = { choices: '' };
                                                break;
                                              case 'uniform_int':
                                              case 'uniform_float':
                                                defaultParams = { low: 0, high: 10 };
                                                break;
                                              case 'normal':
                                                defaultParams = { loc: 0, scale: 1 };
                                                break;
                                              case 'constant':
                                                defaultParams = { val: '' };
                                                break;
                                            }
                                            
                                            if (currentValues.citizenGroups && 
                                              currentValues.citizenGroups[name] && 
                                              currentValues.citizenGroups[name].memory_distributions) {
                                              currentValues.citizenGroups[name].memory_distributions[distName].distribution.params = defaultParams;
                                              form.setFieldsValue(currentValues);
                                            }
                                          }}
                                        />
                                      </Form.Item>
                                      
                                      {renderDistributionForm(
                                        form.getFieldValue(['citizenGroups', name, 'memory_distributions', distName, 'distribution', 'type']),
                                        ['citizenGroups', name, 'memory_distributions', distName, 'distribution']
                                      )}
                                    </Card>
                                  ))}
                                  <Button
                                    type="dashed"
                                    onClick={() => {
                                      console.log('Adding new distribution');
                                      add({
                                        name: '',
                                        distribution: {
                                          type: 'constant',
                                          params: { val: '' }
                                        }
                                      });
                                    }}
                                    block
                                    icon={<PlusOutlined />}
                                    size="small"
                                    style={{ marginBottom: 16 }}
                                  >
                                    Add Distribution
                                  </Button>
                                </>
                              )}
                            </Form.List>
                          </Card>
                        ))}
                        <Button
                          type="dashed"
                          onClick={() => add({ number: 10 })}
                          block
                          icon={<PlusOutlined />}
                        >
                          Add Citizen Group
                        </Button>
                      </>
                    )}
                  </Form.List>
                )}
              </Card>
            </TabPane>

            <TabPane tab="Firms" key="2">
              <Card bordered={false}>
                <Form.List name="firmGroups" initialValue={[{ number: 1 }]}>
                  {(fields, { add, remove }) => (
                    <>
                      {fields.map(({ key, name, ...restField }) => (
                        <Card
                          key={key}
                          title={`Firm Group ${name + 1}`}
                          style={{ marginBottom: 16 }}
                          extra={
                            fields.length > 1 ? (
                              <MinusCircleOutlined onClick={() => remove(name)} />
                            ) : null
                          }
                        >
                          <Form.Item
                            {...restField}
                            name={[name, 'number']}
                            label="Number of Firms"
                            rules={[{ required: true, message: 'Please enter number of firms' }]}
                          >
                            <InputNumber min={1} style={{ width: '100%' }} />
                          </Form.Item>
                        </Card>
                      ))}
                      <Button
                        type="dashed"
                        onClick={() => add({ number: 1 })}
                        block
                        icon={<PlusOutlined />}
                      >
                        Add Firm Group
                      </Button>
                    </>
                  )}
                </Form.List>
              </Card>
            </TabPane>

            <TabPane tab="Government" key="3">
              <Card bordered={false}>
                <Form.List name="governmentGroups" initialValue={[{ number: 1 }]}>
                  {(fields, { add, remove }) => (
                    <>
                      {fields.map(({ key, name, ...restField }) => (
                        <Card
                          key={key}
                          title={`Government Group ${name + 1}`}
                          style={{ marginBottom: 16 }}
                          extra={
                            fields.length > 1 ? (
                              <MinusCircleOutlined onClick={() => remove(name)} />
                            ) : null
                          }
                        >
                          <Form.Item
                            {...restField}
                            name={[name, 'number']}
                            label="Number of Government Agents"
                            rules={[{ required: true, message: 'Please enter number of government agents' }]}
                          >
                            <InputNumber min={1} style={{ width: '100%' }} />
                          </Form.Item>
                        </Card>
                      ))}
                      <Button
                        type="dashed"
                        onClick={() => add({ number: 1 })}
                        block
                        icon={<PlusOutlined />}
                      >
                        Add Government Group
                      </Button>
                    </>
                  )}
                </Form.List>
              </Card>
            </TabPane>

            <TabPane tab="Banks" key="4">
              <Card bordered={false}>
                <Form.List name="bankGroups" initialValue={[{ number: 1 }]}>
                  {(fields, { add, remove }) => (
                    <>
                      {fields.map(({ key, name, ...restField }) => (
                        <Card
                          key={key}
                          title={`Bank Group ${name + 1}`}
                          style={{ marginBottom: 16 }}
                          extra={
                            fields.length > 1 ? (
                              <MinusCircleOutlined onClick={() => remove(name)} />
                            ) : null
                          }
                        >
                          <Form.Item
                            {...restField}
                            name={[name, 'number']}
                            label="Number of Banks"
                            rules={[{ required: true, message: 'Please enter number of banks' }]}
                          >
                            <InputNumber min={1} style={{ width: '100%' }} />
                          </Form.Item>
                        </Card>
                      ))}
                      <Button
                        type="dashed"
                        onClick={() => add({ number: 1 })}
                        block
                        icon={<PlusOutlined />}
                      >
                        Add Bank Group
                      </Button>
                    </>
                  )}
                </Form.List>
              </Card>
            </TabPane>

            <TabPane tab="NBS" key="5">
              <Card bordered={false}>
                <Form.List name="nbsGroups" initialValue={[{ number: 1 }]}>
                  {(fields, { add, remove }) => (
                    <>
                      {fields.map(({ key, name, ...restField }) => (
                        <Card
                          key={key}
                          title={`NBS Group ${name + 1}`}
                          style={{ marginBottom: 16 }}
                          extra={
                            fields.length > 1 ? (
                              <MinusCircleOutlined onClick={() => remove(name)} />
                            ) : null
                          }
                        >
                          <Form.Item
                            {...restField}
                            name={[name, 'number']}
                            label="Number of NBS"
                            rules={[{ required: true, message: 'Please enter number of NBS' }]}
                          >
                            <InputNumber min={1} style={{ width: '100%' }} />
                          </Form.Item>
                        </Card>
                      ))}
                      <Button
                        type="dashed"
                        onClick={() => add({ number: 1 })}
                        block
                        icon={<PlusOutlined />}
                      >
                        Add NBS Group
                      </Button>
                    </>
                  )}
                </Form.List>
              </Card>
            </TabPane>

            <TabPane tab="Custom" key="6">
              <Card bordered={false}>
                <Form.List name="customGroups" initialValue={[{}]}>
                  {(fields, { add, remove }) => (
                    <>
                      {fields.map(({ key, name, ...restField }) => (
                        <Card
                          key={key}
                          title={`Custom Group ${name + 1}`}
                          style={{ marginBottom: 16 }}
                          extra={
                            fields.length > 1 ? (
                              <MinusCircleOutlined onClick={() => remove(name)} />
                            ) : null
                          }
                        >
                          <Form.Item
                            {...restField}
                            name={[name, 'templateId']}
                            label="Agent Template"
                            rules={[{ required: true, message: 'Please select a template' }]}
                          >
                            <Select
                              loading={loading}
                              placeholder="Select a template"
                              style={{ width: '100%' }}
                            >
                              {templates.map(template => (
                                <Option key={template.id} value={template.id}>
                                  {template.name}
                                  <span style={{ color: '#999', marginLeft: 8 }}>
                                    {template.description}
                                  </span>
                                </Option>
                              ))}
                            </Select>
                          </Form.Item>
                        </Card>
                      ))}
                      <Button
                        type="dashed"
                        onClick={() => add({})}
                        block
                        icon={<PlusOutlined />}
                      >
                        Add Custom Group
                      </Button>
                    </>
                  )}
                </Form.List>
              </Card>
            </TabPane>
          </Tabs>
        </Form>
      </Card>
    </>
  );
};

export default AgentForm; 