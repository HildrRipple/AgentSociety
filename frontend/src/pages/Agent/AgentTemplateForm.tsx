import React, { useState, useEffect } from 'react';
import { Form, Input, Card, Row, Col, Button, Switch, InputNumber, Select, Space, message, Tooltip, Table } from 'antd';
import { useNavigate, useParams } from 'react-router-dom';
import { fetchCustom } from '../../components/fetch';
import { QuestionCircleOutlined } from '@ant-design/icons';

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
  name: {
    type: 'choice',
    choices: ["Alice", "Bob", "Charlie", "David", "Eve", "Frank", "Grace", "Helen", "Ivy", "Jack"],
    weights: [0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1]
  },
  gender: {
    type: 'choice',
    choices: ["male", "female"],
    weights: [0.5, 0.5]
  },
  age: {
    type: 'uniform_int',
    min_value: 18,
    max_value: 65
  },
  education: {
    type: 'choice',
    choices: ["Doctor", "Master", "Bachelor", "College", "High School"],
    weights: [0.1, 0.2, 0.4, 0.2, 0.1]
  },
  skill: {
    type: 'choice',
    choices: ["Good at problem-solving", "Good at communication", "Good at creativity"],
    weights: [0.33, 0.34, 0.33]
  },
  occupation: {
    type: 'choice',
    choices: ["Student", "Teacher", "Doctor", "Engineer", "Manager"],
    weights: [0.2, 0.2, 0.2, 0.2, 0.2]
  },
  family_consumption: {
    type: 'choice',
    choices: ["low", "medium", "high"],
    weights: [0.3, 0.4, 0.3]
  },
  consumption: {
    type: 'choice',
    choices: ["low", "slightly low", "medium", "slightly high", "high"],
    weights: [0.2, 0.2, 0.2, 0.2, 0.2]
  },
  personality: {
    type: 'choice',
    choices: ["outgoing", "introvert", "ambivert", "extrovert"],
    weights: [0.25, 0.25, 0.25, 0.25]
  },
  income: {
    type: 'uniform_int',
    min_value: 1000,
    max_value: 20000
  },
  currency: {
    type: 'uniform_int',
    min_value: 1000,
    max_value: 100000
  },
  residence: {
    type: 'choice',
    choices: ["city", "suburb", "rural"],
    weights: [0.4, 0.4, 0.2]
  },
  city: {
    type: 'choice',
    choices: ["New York", "Los Angeles", "London", "Paris", "Tokyo"],
    weights: [0.2, 0.2, 0.2, 0.2, 0.2]
  },
  race: {
    type: 'choice',
    choices: ["Chinese", "American", "British", "French", "German"],
    weights: [0.2, 0.2, 0.2, 0.2, 0.2]
  },
  religion: {
    type: 'choice',
    choices: ["none", "Christian", "Muslim", "Buddhist", "Hindu"],
    weights: [0.2, 0.2, 0.2, 0.2, 0.2]
  },
  marital_status: {
    type: 'choice',
    choices: ["not married", "married", "divorced", "widowed"],
    weights: [0.4, 0.4, 0.1, 0.1]
  }
};

const defaultBaseFields = {
  home: {
    aoi_position: {
      aoi_id: 0
    }
  },
  work: {
    aoi_position: {
      aoi_id: 0
    }
  }
};

// 首先定义字段类型
interface ProfileField {
  label: string;
  type: 'discrete' | 'continuous';
  options?: string[];  // 用于离散型
  defaultParams?: {
    min_value?: number;  // 用于连续型
    max_value?: number;  // 用于连续型
    mean?: number;      // 用于正态分布
    std?: number;       // 用于正态分布
  };
}

// 修改 profileOptions 定义
const profileOptions: Record<string, ProfileField> = {
  name: {
    label: "Name",
    type: 'discrete',
    options: ["Alice", "Bob", "Charlie", "David", "Eve", "Frank", "Grace", "Helen", "Ivy", "Jack"],
  },
  gender: {
    label: "Gender",
    type: 'discrete',
    options: ["male", "female"]
  },
  age: {
    label: "Age",
    type: 'continuous',
    defaultParams: { min_value: 18, max_value: 65 }
  },
  education: {
    label: "Education",
    type: 'discrete',
    options: ["Doctor", "Master", "Bachelor", "College", "High School"],
  },
  skill: {
    label: "Skill",
    type: 'discrete',
    options: ["Good at problem-solving", "Good at communication", "Good at creativity"],
  },
  occupation: {
    label: "Occupation",
    type: 'discrete',
    options: ["Student", "Teacher", "Doctor", "Engineer", "Manager"],
  },
  family_consumption: {
    label: "Family Consumption",
    type: 'discrete',
    options: ["low", "medium", "high"],
  },
  consumption: {
    label: "Consumption",
    type: 'discrete',
    options: ["low", "slightly low", "medium", "slightly high", "high"],
  },
  personality: {
    label: "Personality",
    type: 'discrete',
    options: ["outgoing", "introvert", "ambivert", "extrovert"],
  },
  income: {
    label: "Income",
    type: 'continuous',
    defaultParams: { 
      min_value: 1000, 
      max_value: 20000,
      mean: 5000,
      std: 1000
    }
  },
  currency: {
    label: "Currency",
    type: 'continuous',
    defaultParams: {
      min_value: 1000,
      max_value: 100000,
      mean: 50000,
      std: 10000
    }
  },
  residence: {
    label: "Residence",
    type: 'discrete',
    options: ["city", "suburb", "rural"],
  },
  race: {
    label: "Race",
    type: 'discrete',
    options: ["Chinese", "American", "British", "French", "German"],
  },
  religion: {
    label: "Religion",
    type: 'discrete',
    options: ["none", "Christian", "Muslim", "Buddhist", "Hindu"],
  },
  marital_status: {
    label: "Marital Status",
    type: 'discrete',
    options: ["not married", "married", "divorced", "widowed"],
  },
  city: {
    label: "City",
    type: 'discrete',
    options: ["New York", "Los Angeles", "London", "Paris", "Tokyo"],
  }
};

// Add block types based on BLOCK_MAPPING
const BLOCK_TYPES = [
  {
    label: "Mobility Block",
    value: "mobilityblock",
    description: "移动模块用于控制代理的移动行为，包括路径规划、速度控制等功能。"
  },
  {
    label: "Economy Block",
    value: "economyblock",
    description: "经济模块处理代理的经济活动，如收入、支出、交易等行为。"
  },
  {
    label: "Social Block",
    value: "socialblock",
    description: "社交模块管理代理之间的社交互动，包括社交关系网络和交流行为。"
  },
  {
    label: "Other Block",
    value: "otherblock",
    description: "其他功能模块，可用于扩展代理的特定行为。"
  },
];

// 修改分布类型定义
const DISCRETE_DISTRIBUTIONS = [
  { label: 'Random Choice', value: 'choice' }
];

const CONTINUOUS_DISTRIBUTIONS = [
  { label: 'Uniform Distribution', value: 'uniform_int' },
  { label: 'Normal Distribution', value: 'normal' }
];

// 首先添加新的类型定义
interface Distribution {
  type: 'choice' | 'uniform_int' | 'normal';
  params: {
    choices?: string[];
    weights?: number[];
    min_value?: number;
    max_value?: number;
    mean?: number;
    std?: number;
  };
}

interface DistributionConfig {
  type: 'choice' | 'uniform_int' | 'normal';
  choices?: string[];
  min_value?: number;
  max_value?: number;
  mean?: number;
  std?: number;
}

// Modify the distribution form rendering function
const renderDistributionFields = (fieldName: string, fieldConfig: ProfileField, form: FormInstance) => {
  const distributionType = Form.useWatch(['profile', fieldName, 'type'], form);

  // 当分布类型改变时，初始化对应的参数
  const handleDistributionTypeChange = (value: string) => {
    if (value === 'uniform_int') {
      form.setFieldsValue({
        profile: {
          [fieldName]: {
            type: value,
            min_value: fieldConfig.defaultParams?.min_value,
            max_value: fieldConfig.defaultParams?.max_value
          }
        }
      });
    } else if (value === 'normal') {
      form.setFieldsValue({
        profile: {
          [fieldName]: {
            type: value,
            mean: fieldConfig.defaultParams?.mean,
            std: fieldConfig.defaultParams?.std
          }
        }
      });
    }
  };

  if (fieldConfig.type === 'discrete') {
    return (
      <div style={{ marginTop: 8 }}>
        <Form.Item
          label="Choice Weights"
          required
          tooltip="Sum of weights should be 1"
        >
          <Table
            size="small"
            pagination={false}
            dataSource={fieldConfig.options?.map((option, index) => ({
              key: index,
              option: option,
              weight: (
                <Form.Item
                  name={['profile', fieldName, 'weights', index]}
                  rules={[{ required: true, message: 'Required' }]}
                  style={{ margin: 0 }}
                >
                  <InputNumber
                    min={0}
                    max={1}
                    step={0.1}
                    style={{ width: '100%' }}
                    placeholder="0-1"
                  />
                </Form.Item>
              )
            }))}
            columns={[
              {
                title: 'Option',
                dataIndex: 'option',
                width: '60%'
              },
              {
                title: 'Weight',
                dataIndex: 'weight',
                width: '40%'
              }
            ]}
          />
        </Form.Item>
      </div>
    );
  } else {
    return (
      <div style={{ marginTop: 8 }}>
        <Form.Item
          name={['profile', fieldName, 'type']}
          label="Distribution Type"
          initialValue="uniform_int"
        >
          <Select
            options={[
              { label: 'Uniform Distribution', value: 'uniform_int' },
              { label: 'Normal Distribution', value: 'normal' }
            ]}
            onChange={handleDistributionTypeChange}
          />
        </Form.Item>

        {distributionType === 'uniform_int' && (
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                label="Minimum Value"
                name={['profile', fieldName, 'min_value']}
                rules={[{ required: true, message: 'Required' }]}
                initialValue={fieldConfig.defaultParams?.min_value}
              >
                <InputNumber style={{ width: '100%' }} />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                label="Maximum Value"
                name={['profile', fieldName, 'max_value']}
                rules={[{ required: true, message: 'Required' }]}
                initialValue={fieldConfig.defaultParams?.max_value}
              >
                <InputNumber style={{ width: '100%' }} />
              </Form.Item>
            </Col>
          </Row>
        )}

        {distributionType === 'normal' && (
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                label="Mean"
                name={['profile', fieldName, 'mean']}
                rules={[{ required: true, message: 'Required' }]}
                initialValue={fieldConfig.defaultParams?.mean}
              >
                <InputNumber style={{ width: '100%' }} />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                label="Standard Deviation"
                name={['profile', fieldName, 'std']}
                rules={[{ required: true, message: 'Required' }]}
                initialValue={fieldConfig.defaultParams?.std}
              >
                <InputNumber style={{ width: '100%' }} min={0} />
              </Form.Item>
            </Col>
          </Row>
        )}
      </div>
    );
  }
};

// Modify Profile card section rendering
const renderProfileSection = (form: FormInstance) => (
  <Card title="Profile" bordered={false} style={{ marginBottom: '24px' }}>
    <Row gutter={[16, 16]}>
      {Object.entries(profileOptions).map(([key, config]) => (
        <Col span={12} key={key}>
          <Card size="small" title={config.label}>
            {config.type === 'discrete' ? (
              <>
                <Form.Item
                  name={['profile', key, 'type']}
                  label="Distribution Type"
                  initialValue="choice"
                >
                  <Select
                    options={[{ label: 'Discrete Choice', value: 'choice' }]}
                    disabled
                  />
                </Form.Item>
                <Form.Item
                  name={['profile', key, 'choices']}
                  hidden
                  initialValue={config.options}
                >
                  <Input />
                </Form.Item>
                {renderDistributionFields(key, config, form)}
              </>
            ) : (
              renderDistributionFields(key, config, form)
            )}
          </Card>
        </Col>
      ))}
    </Row>
  </Card>
);

// Modify Base Location card
const renderBaseLocation = () => (
  <Card title="Base Location" bordered={false}>
    <Row gutter={16}>
      <Col span={12}>
        <Form.Item
          name={['base', 'home', 'aoi_position', 'aoi_id']}
          label="Home Area ID"
          rules={[{ required: true }]}
          initialValue={0}
        >
          <InputNumber style={{ width: '100%' }} />
        </Form.Item>
      </Col>
      <Col span={12}>
        <Form.Item
          name={['base', 'work', 'aoi_position', 'aoi_id']}
          label="Work Area ID"
          rules={[{ required: true }]}
          initialValue={0}
        >
          <InputNumber style={{ width: '100%' }} />
        </Form.Item>
      </Col>
    </Row>
  </Card>
);

// 在 Agent Configuration 部分添加 prompt 输入框
const renderAgentConfiguration = () => (
  <Card title="Agent Configuration" bordered={false}>
    <Row gutter={[16, 16]}>
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
          label="UBI"
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
          label="Productivity per Labor"
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
      <Col span={24}>
        <Form.Item
          name={['agent_params', 'need_initialization_prompt']}
          label="Need Initialization Prompt"
        >
          <Input.TextArea rows={4} placeholder="Enter prompt for need initialization" />
        </Form.Item>
      </Col>
      <Col span={24}>
        <Form.Item
          name={['agent_params', 'need_evaluation_prompt']}
          label="Need Evaluation Prompt"
        >
          <Input.TextArea rows={4} placeholder="Enter prompt for need evaluation" />
        </Form.Item>
      </Col>
      <Col span={24}>
        <Form.Item
          name={['agent_params', 'need_reflection_prompt']}
          label="Need Reflection Prompt"
        >
          <Input.TextArea rows={4} placeholder="Enter prompt for need reflection" />
        </Form.Item>
      </Col>
      <Col span={24}>
        <Form.Item
          name={['agent_params', 'plan_generation_prompt']}
          label="Plan Generation Prompt"
        >
          <Input.TextArea rows={4} placeholder="Enter prompt for plan generation" />
        </Form.Item>
      </Col>
    </Row>
  </Card>
);

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

      // 转换表单数据为期望的格式
      const profile: Record<string, Distribution | DistributionConfig> = {};
      
      Object.entries(values.profile).forEach(([key, value]: [string, any]) => {
        if (value.type === 'choice') {
          profile[key] = {
            type: 'choice',
            params: {
              choices: value.choices,
              weights: value.weights
            }
          };
        } else if (value.type === 'uniform_int') {
          profile[key] = {
            type: 'uniform_int',
            min_value: value.min_value,
            max_value: value.max_value
          };
        } else if (value.type === 'normal') {
          profile[key] = {
            type: 'normal',
            mean: value.mean,
            std: value.std
          };
        }
      });

      // 构造模板数据
      const templateData = {
        name: values.name,
        description: values.description,
        profile,
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
              {renderProfileSection(form)}
              {/* Left column: Base */}
              {renderBaseLocation()}
            </Col>

            <Col span={16}>
              {/* Right column: Agent Configuration */}
              {renderAgentConfiguration()}

              {/* Right column: Block Configuration */}
              <Card title="Block Configuration" bordered={false}>
                <Form.Item
                  label="Select Block Types"
                  name="blockTypes"
                >
                  <Select
                    mode="multiple"
                    placeholder="Select block types"
                    style={{ width: '100%' }}
                    onChange={handleBlockTypeChange}
                    options={BLOCK_TYPES.map(block => ({
                      label: (
                        <Space>
                          {block.label}
                          <Tooltip title={block.description}>
                            <QuestionCircleOutlined style={{ cursor: 'pointer' }} />
                          </Tooltip>
                        </Space>
                      ),
                      value: block.value
                    }))}
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
                              {/* 暂时注释掉 name 和 description 字段
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
                              */}

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