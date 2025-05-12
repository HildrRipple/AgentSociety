import React, { useState, useEffect } from 'react';
import { Form, Input, Card, Row, Col, Button, Switch, InputNumber, Select, Space, message } from 'antd';
import { useNavigate, useParams } from 'react-router-dom';
import { fetchCustom } from '../../components/fetch';

// Import required interfaces and constants
interface TemplateBlock {
  id: string;
  name: string;
  type: string;
  description: string;
  dependencies?: {
    needs?: string;
    satisfaction?: string;
  };
  params?: Record<string, any>;
}

interface AgentTemplate {
  id: string;
  name: string;
  description: string;
  profile: {
    fields: Record<string, string>;
  };
  base: {
    fields: Record<string, string>;
  };
  states: {
    fields: Record<string, string>;
    selfDefine?: string;
  };
  agent_params: {
    enable_cognition: boolean;
    UBI: number;
    num_labor_hours: number;
    productivity_per_labor: number;
    time_diff: number;
    max_plan_steps: number;
    need_initialization_prompt?: string;
    need_evaluation_prompt?: string;
    need_reflection_prompt?: string;
    plan_generation_prompt?: string;
  };
  blocks: TemplateBlock[];
  created_at: string;
  updated_at: string;
  tenant_id?: string;
}

// Add default configurations
const defaultProfileFields = {
  name: '',
  gender: '',
  age: '',
  education: '',
  skill: '',
  occupation: '',
  family_consumption: '',
  consumption: '',
  personality: '',
  income: '',
  currency: '',
  residence: '',
  city: '',
  race: '',
  religion: '',
  marital_status: ''
};

const defaultBaseFields = {
  home: {
    aoi_position: {
      aoi_id: ''
    }
  },
  work: {
    aoi_position: {
      aoi_id: ''
    }
  }
};

// Preset options
const profileOptions = {
  name: ["Alice", "Bob", "Charlie", "David", "Eve", "Frank", "Grace"],
  gender: ["male", "female"],
  education: ["Doctor", "Master", "Bachelor", "College", "High School"],
  skill: ["Good at problem-solving", "Good at communication", "Good at creativity"],
  occupation: ["Student", "Teacher", "Doctor", "Engineer", "Manager"],
  family_consumption: ["low", "medium", "high"],
  consumption: ["low", "slightly low", "medium", "slightly high", "high"],
  personality: ["outgoing", "introvert", "ambivert", "extrovert"],
  residence: ["city", "suburb", "rural"],
  race: ["Chinese", "American", "British", "French", "German"],
  religion: ["none", "Christian", "Muslim", "Buddhist", "Hindu"],
  marital_status: ["not married", "married", "divorced", "widowed"]
};

// Add block types based on BLOCK_MAPPING
const BLOCK_TYPES = [
  { label: "Mobility Block", value: "mobilityblock" },
  { label: "Economy Block", value: "economyblock" },
  { label: "Social Block", value: "socialblock" },
  { label: "Other Block", value: "otherblock" },
];

const AgentTemplateForm: React.FC = () => {
  const [form] = Form.useForm();
  const navigate = useNavigate();
  const { id } = useParams(); // Get template ID from URL
  const [currentTemplate, setCurrentTemplate] = useState<AgentTemplate | null>(null);
  const [selectedBlocks, setSelectedBlocks] = useState<string[]>([]);

  // Load template data
  useEffect(() => {
    if (id) {
      fetchCustom(`/api/agent-templates/${id}`).then(async (res) => {
        if (res.ok) {
          const template = (await res.json()).data;
          setCurrentTemplate(template);
          
          // Extract block types from template
          const blockTypes = template.blocks.map(block => block.type);
          setSelectedBlocks(blockTypes);
          
          form.setFieldsValue({
            name: template.name,
            description: template.description,
            profile: template.profile.fields,
            base: template.base.fields,
            states: {
              ...template.states.fields,
              selfDefine: template.states.selfDefine || ''
            },
            agent_params: template.agent_params,
            blocks: template.blocks
          });
        }
      });
    } else {
      // Default values for new template
      form.setFieldsValue({
        name: 'General Social Agent',
        description: '',
        profile: defaultProfileFields,
        base: defaultBaseFields,
        states: {
          needs: 'str',
          plan: 'dict',
          selfDefine: ''
        },
        agent_params: {
          enable_cognition: true,
          UBI: 1000,
          num_labor_hours: 168,
          productivity_per_labor: 1,
          time_diff: 2592000,
          max_plan_steps: 6
        },
        blocks: []
      });
    }
  }, [id]);

  const handleBlockTypeChange = (values: string[]) => {
    setSelectedBlocks(values);
    
    // Update form blocks based on selected types
    const existingBlocks = form.getFieldValue('blocks') || [];
    
    // Keep blocks that are still selected
    const remainingBlocks = existingBlocks.filter(block => values.includes(block.type));
    
    // Add new blocks for newly selected types
    const newBlockTypes = values.filter(type => 
      !existingBlocks.some(block => block.type === type)
    );
    
    const newBlocks = newBlockTypes.map(type => ({
      id: `${type}_${Date.now()}`,
      name: type.charAt(0).toUpperCase() + type.slice(1),
      type: type,
      description: `${type} for agent`,
      dependencies: {},
      params: type === 'mobilityblock' ? { speed: 1.0 } : {}
    }));
    
    form.setFieldsValue({
      blocks: [...remainingBlocks, ...newBlocks]
    });
  };

  const handleSubmit = async () => {
    try {
      const values = await form.validateFields();
      console.log('Form values before submission:', JSON.stringify(values, null, 2));

      // 构造模板数据
      const templateData = {
        name: values.name,
        description: values.description,
        profile: {
          fields: values.profile || {}
        },
        base: {
          fields: values.base || {}
        },
        states: {
          fields: values.states || {},
          selfDefine: values.states?.selfDefine || ''
        },
        agent_params: {
          enable_cognition: values.agent_params?.enable_cognition ?? true,
          UBI: values.agent_params?.UBI ?? 0,
          num_labor_hours: values.agent_params?.num_labor_hours ?? 8,
          productivity_per_labor: values.agent_params?.productivity_per_labor ?? 1.0,
          time_diff: values.agent_params?.time_diff ?? 1.0,
          max_plan_steps: values.agent_params?.max_plan_steps ?? 5,
          need_initialization_prompt: values.agent_params?.need_initialization_prompt,
          need_evaluation_prompt: values.agent_params?.need_evaluation_prompt,
          need_reflection_prompt: values.agent_params?.need_reflection_prompt,
          plan_generation_prompt: values.agent_params?.plan_generation_prompt
        },
        blocks: (values.blocks || []).map(block => ({
          id: block.id,
          name: block.name,
          type: block.type,
          description: block.description,
          dependencies: block.dependencies || {},
          params: block.params || {}
        }))
      };

      console.log('Template data to be sent:', JSON.stringify(templateData, null, 2));

      const res = await fetchCustom('/api/agent-templates', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(templateData),
      });

      if (!res.ok) {
        const errorData = await res.json();
        console.error('API error response:', JSON.stringify(errorData, null, 2));
        throw new Error(errorData.detail || 'Failed to create template');
      }

      const data = await res.json();
      console.log('API success response:', JSON.stringify(data, null, 2));
      message.success('Template created successfully');
      navigate('/agent-templates');
    } catch (error) {
      console.error('Error in handleSubmit:', error);
      message.error(error.message || 'Failed to create template');
    }
  };

  return (
    <div style={{ padding: '24px' }}>
      <Card
        title={id ? "Edit Template" : "Create Template"}
        extra={
          <Space>
            <Button onClick={() => navigate('/agent-templates')}>Cancel</Button>
            <Button type="primary" onClick={() => form.submit()}>
              Save
            </Button>
          </Space>
        }
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleSubmit}
        >
          <Row gutter={[24, 24]}>
            <Col span={24}>
              <Card title="Basic Information" bordered={false}>
                <Row gutter={16}>
                  <Col span={12}>
                    <Form.Item
                      name="name"
                      label="Template Name"
                      rules={[{ required: true }]}
                    >
                      <Input placeholder="General Social Agent" />
                    </Form.Item>
                  </Col>
                  <Col span={12}>
                    <Form.Item
                      name="description"
                      label="Description"
                    >
                      <Input.TextArea rows={2} />
                    </Form.Item>
                  </Col>
                </Row>
              </Card>
            </Col>

            {/* Two-column layout starts */}
            <Col span={8}>
              {/* Left column: Profile */}
              <Card title="Profile" bordered={false} style={{ marginBottom: '24px' }}>
                <Row gutter={[16, 8]}>
                  {Object.entries(profileOptions).map(([key, options]) => (
                    <Col span={12} key={key}>
                      <Form.Item
                        name={['profile', key]}
                        label={key.split('_').map(word => 
                          word.charAt(0).toUpperCase() + word.slice(1)
                        ).join(' ')}
                        rules={[{ required: true }]}
                      >
                        <Select
                          showSearch
                          allowClear
                          placeholder={`Select ${key}`}
                          options={options.map(v => ({ label: v, value: v }))}
                        />
                      </Form.Item>
                    </Col>
                  ))}
                </Row>
              </Card>

              {/* Left column: Base */}
              <Card title="Base Location" bordered={false}>
                <Row gutter={16}>
                  <Col span={12}>
                    <Form.Item
                      name={['base', 'home', 'aoi_position', 'aoi_id']}
                      label="Home Area ID"
                      rules={[{ required: true }]}
                    >
                      <InputNumber style={{ width: '100%' }} />
                    </Form.Item>
                  </Col>
                  <Col span={12}>
                    <Form.Item
                      name={['base', 'work', 'aoi_position', 'aoi_id']}
                      label="Work Area ID"
                      rules={[{ required: true }]}
                    >
                      <InputNumber style={{ width: '100%' }} />
                    </Form.Item>
                  </Col>
                </Row>
              </Card>
            </Col>

            <Col span={16}>
              {/* Right column: Agent Configuration */}
              <Card title="Agent Configuration" bordered={false} style={{ marginBottom: '24px' }}>
                <Row gutter={[16, 8]}>
                  <Col span={12}>
                    <Form.Item
                      name={['agent_params', 'enable_cognition']}
                      label="Enable Cognition"
                      valuePropName="checked"
                    >
                      <Switch />
                    </Form.Item>
                  </Col>
                  <Col span={12}>
                    <Form.Item
                      name={['agent_params', 'UBI']}
                      label="Basic Income"
                      rules={[{ required: true }]}
                    >
                      <InputNumber style={{ width: '100%' }} />
                    </Form.Item>
                  </Col>
                  <Col span={12}>
                    <Form.Item
                      name={['agent_params', 'num_labor_hours']}
                      label="Labor Hours"
                      rules={[{ required: true }]}
                    >
                      <InputNumber style={{ width: '100%' }} />
                    </Form.Item>
                  </Col>
                  <Col span={12}>
                    <Form.Item
                      name={['agent_params', 'productivity_per_labor']}
                      label="Labor Productivity"
                      rules={[{ required: true }]}
                    >
                      <InputNumber style={{ width: '100%' }} />
                    </Form.Item>
                  </Col>
                  <Col span={12}>
                    <Form.Item
                      name={['agent_params', 'time_diff']}
                      label="Time Difference"
                      rules={[{ required: true }]}
                    >
                      <InputNumber style={{ width: '100%' }} />
                    </Form.Item>
                  </Col>
                  <Col span={12}>
                    <Form.Item
                      name={['agent_params', 'max_plan_steps']}
                      label="Max Plan Steps"
                      rules={[{ required: true }]}
                    >
                      <InputNumber style={{ width: '100%' }} />
                    </Form.Item>
                  </Col>
                </Row>
              </Card>

              {/* Right column: Block Configuration */}
              <Card title="Block Configuration" bordered={false}>
                <Form.Item
                  label="Select Block Types"
                  name="blockTypes"
                  rules={[{ required: true, message: 'Please select at least one block type' }]}
                >
                  <Select
                    mode="multiple"
                    placeholder="Select block types"
                    options={BLOCK_TYPES}
                    onChange={handleBlockTypeChange}
                    style={{ width: '100%' }}
                  />
                </Form.Item>

                <Form.List name="blocks">
                  {(fields) => (
                    <div>
                      {fields.map(field => {
                        const blockType = form.getFieldValue(['blocks', field.name, 'type']);
                        return (
                          <Card 
                            key={field.key} 
                            title={`${blockType.charAt(0).toUpperCase() + blockType.slice(1)} Configuration`}
                            style={{ marginBottom: '16px' }}
                            size="small"
                          >
                            <Row gutter={16}>
                              <Col span={12}>
                                <Form.Item
                                  {...field}
                                  name={[field.name, 'name']}
                                  label="Block Name"
                                  rules={[{ required: true }]}
                                >
                                  <Input />
                                </Form.Item>
                              </Col>
                              <Col span={12}>
                                <Form.Item
                                  {...field}
                                  name={[field.name, 'description']}
                                  label="Description"
                                >
                                  <Input />
                                </Form.Item>
                              </Col>
                              
                              {/* Mobility Block specific parameters */}
                              {blockType === 'mobilityblock' && (
                                <Col span={12}>
                                  <Form.Item
                                    {...field}
                                    name={[field.name, 'params', 'search_limit']}
                                    label="Search Limit"
                                    rules={[{ required: true }]}
                                  >
                                    <InputNumber min={0.1} step={0.1} style={{ width: '100%' }} />
                                  </Form.Item>
                                </Col>
                              )}
                              
                              {/* Hidden fields to store block type and ID */}
                              <Form.Item
                                {...field}
                                name={[field.name, 'type']}
                                hidden
                              >
                                <Input />
                              </Form.Item>
                              <Form.Item
                                {...field}
                                name={[field.name, 'id']}
                                hidden
                              >
                                <Input />
                              </Form.Item>
                            </Row>
                          </Card>
                        );
                      })}
                    </div>
                  )}
                </Form.List>
              </Card>
            </Col>
          </Row>
        </Form>
      </Card>
    </div>
  );
};

export default AgentTemplateForm; 