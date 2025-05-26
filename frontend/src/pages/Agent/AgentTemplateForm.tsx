import React, { useState, useEffect } from 'react';
import { Form, Input, Card, Row, Col, Button, Switch, InputNumber, Select, Space, message, Tooltip, Table, Modal, Typography } from 'antd';
import type { FormInstance } from 'antd/es/form';
import { useNavigate, useParams } from 'react-router-dom';
import { fetchCustom } from '../../components/fetch';
import { QuestionCircleOutlined } from '@ant-design/icons';
import MonacoPromptEditor from '../../components/MonacoPromptEditor';
import { useTranslation } from 'react-i18next';

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
  memory_distributions: {
    [key: string]: {
      dist_type: 'choice' | 'uniform_int' | 'normal';
      choices?: string[];
      weights?: number[];
      min_value?: number;
      max_value?: number;
      mean?: number;
      std?: number;
    };
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
  blocks: {
    [key: string]: {
      params?: Record<string, any>;
    };
  };
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
        <Col span={24} key={key}>
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

// 首先添加一个接口定义
interface FunctionInfo {
  function_name: string;
  description: string;
}

// 在 renderAgentConfiguration 函数中添加 Usable Functions 部分
const renderAgentConfiguration = () => {
  const [functions, setFunctions] = useState<FunctionInfo[]>([]);

  useEffect(() => {
    // 获取函数列表
    fetchCustom('/api/agent-functions')
      .then(res => res.json())
      .then(response => {
        if (response.data && Array.isArray(response.data)) {
          setFunctions(response.data);
        }
      })
      .catch(err => {
        console.error('Failed to fetch functions:', err);
        setFunctions([]);
      });
  }, []);

  // 从 profile 选项中提取建议
  const profileSuggestions = Object.entries(profileOptions).map(([key, config]) => ({
    label: `${key}`,
    detail: `Agent's ${config.label.toLowerCase()}`
  }));

  // 从函数列表中提取建议
  const functionSuggestions = functions.map(func => ({
    label: func.function_name,
    detail: func.description
  }));

  // 合并所有建议
  const suggestions = [...profileSuggestions, ...functionSuggestions];

  return (
    <Card title="Agent Configuration" bordered={false}>
      <Row gutter={[16, 16]}>
        <Col span={12}>
          <Form.Item
            name={['agent_params', 'enable_cognition']}
            label={
              <Space>
                Enable Cognition
                <Tooltip title="Whether to enable cognition">
                  <QuestionCircleOutlined />
                </Tooltip>
              </Space>
            }
            valuePropName="checked"
          >
            <Switch />
          </Form.Item>
        </Col>
        <Col span={12}>
          <Form.Item
            name={['agent_params', 'UBI']}
            label={
              <Space>
                UBI
                <Tooltip title="Universal Basic Income">
                  <QuestionCircleOutlined />
                </Tooltip>
              </Space>
            }
            rules={[{ required: true }]}
          >
            <InputNumber style={{ width: '100%' }} />
          </Form.Item>
        </Col>
        <Col span={12}>
          <Form.Item
            name={['agent_params', 'num_labor_hours']}
            label={
              <span>
                Labor Hours&nbsp;
                <Tooltip title="Number of labor hours per month">
                  <QuestionCircleOutlined />
                </Tooltip>
              </span>
            }
            rules={[{ required: true }]}
          >
            <InputNumber style={{ width: '100%' }} />
          </Form.Item>
        </Col>
        <Col span={12}>
          <Form.Item
            name={['agent_params', 'productivity_per_labor']}
            label={
              <span>
                Productivity per Labor&nbsp;
                <Tooltip title="Productivity per labor hour">
                  <QuestionCircleOutlined />
                </Tooltip>
              </span>
            }
            rules={[{ required: true }]}
          >
            <InputNumber style={{ width: '100%' }} />
          </Form.Item>
        </Col>
        <Col span={12}>
          <Form.Item
            name={['agent_params', 'time_diff']}
            label={
              <span>
                Time Difference&nbsp;
                <Tooltip title="Time difference between two triggers">
                  <QuestionCircleOutlined />
                </Tooltip>
              </span>
            }
            rules={[{ required: true }]}
          >
            <InputNumber style={{ width: '100%' }} />
          </Form.Item>
        </Col>
        <Col span={12}>
          <Form.Item
            name={['agent_params', 'max_plan_steps']}
            label={
              <span>
                Max Plan Steps&nbsp;
                <Tooltip title="Maximum number of steps in a plan">
                  <QuestionCircleOutlined />
                </Tooltip>
              </span>
            }
            rules={[{ required: true }]}
          >
            <InputNumber style={{ width: '100%' }} />
          </Form.Item>
        </Col>

        {/* 添加 Usable Functions 部分 */}
        <Col span={24}>
          <Card title="Usable Functions" size="small" style={{ marginBottom: 16 }}>
            <Space wrap>
              {Array.isArray(functions) && functions.map((func, index) => (
                <span key={index}>
                  <code>{func.function_name}</code>
                  <Tooltip title={func.description}>
                    <QuestionCircleOutlined style={{ marginLeft: 4 }} />
                  </Tooltip>
                </span>
              ))}
            </Space>
          </Card>
        </Col>

        <Col span={24}>
          <Form.Item
            name={['agent_params', 'need_initialization_prompt']}
            label={
              <Space>
                Need Initialization Prompt
                <Tooltip title="Initial needs prompt">
                  <QuestionCircleOutlined />
                </Tooltip>
              </Space>
            }
          >
            <MonacoPromptEditor height="200px" suggestions={suggestions} editorId="need_initialization_prompt" />
          </Form.Item>
        </Col>
        <Col span={24}>
          <Form.Item
            name={['agent_params', 'environment_reflection_prompt']}
            label={
              <Space>
                Environment Reflection Prompt
                <Tooltip title="Environment reflection prompt">
                  <QuestionCircleOutlined />
                </Tooltip>
              </Space>
            }
          >
            <MonacoPromptEditor height="200px" suggestions={suggestions} editorId="environment_reflection_prompt" />
          </Form.Item>
        </Col>
        <Col span={24}>
          <Form.Item
            name={['agent_params', 'plan_generation_prompt']}
            label={
              <Space>
                Plan Generation Prompt
                <Tooltip title="Plan generation prompt">
                  <QuestionCircleOutlined />
                </Tooltip>
              </Space>
            }
          >
            <MonacoPromptEditor height="200px" suggestions={suggestions} editorId="plan_generation_prompt" />
          </Form.Item>
        </Col>
      </Row>
    </Card>
  );
};

// 添加参数相关的接口定义
interface BlockParam {
  description: string | null;
  default: any;
  type: string;
}

interface BlockFunction {
  function_name: string;
  description: string;
}

interface BlockInfo {
  block_name: string;
  description: string;
  functions: BlockFunction[];
  params: Record<string, BlockParam>;
}

// 渲染参数表单项的函数
const renderParamField = (param: BlockParam, blockName: string, paramName: string) => {
  switch (param.type) {
    case 'str':
      if (param.description?.toLowerCase().includes('prompt')) {
        return (
          <MonacoPromptEditor
            value={param.default}
            height="200px"
            editorId={`${blockName}_${paramName}`}
          />
        );
      }
      return (
        <Input
          placeholder={param.description || ''}
          defaultValue={param.default}
        />
      );
    case 'int':
    case 'float':
      return (
        <InputNumber
          style={{ width: '100%' }}
          placeholder={param.description || ''}
          defaultValue={param.default}
        />
      );
    case 'bool':
      return (
        <Switch
          defaultChecked={param.default}
        />
      );
    default:
      return (
        <Input
          placeholder={param.description || ''}
          defaultValue={param.default}
        />
      );
  }
};

// Block Configuration 组件
const BlockConfiguration: React.FC = () => {
  const [blocks, setBlocks] = useState<BlockInfo[]>([]);
  const [selectedBlocks, setSelectedBlocks] = useState<string[]>([]);
  const [form] = Form.useForm();

  useEffect(() => {
    // 获取所有可用的 blocks
    fetchCustom('/api/agent-blocks')
      .then(res => res.json())
      .then(response => {
        if (response.data && Array.isArray(response.data)) {
          setBlocks(response.data);
        }
      })
      .catch(err => {
        console.error('Failed to fetch blocks:', err);
        setBlocks([]);
      });
  }, []);

  const handleBlockSelect = (values: string[]) => {
    setSelectedBlocks(values);
  };

  return (
    <Card title="Block Configuration" bordered={false}>
      <Space direction="vertical" style={{ width: '100%' }}>
        {/* Block 选择框 */}
        <Form.Item
          label="Select Blocks"
          required
        >
          <Select
            mode="multiple"
            placeholder="Select blocks to configure"
            style={{ width: '100%' }}
            onChange={handleBlockSelect}
            options={blocks.map(block => ({
              label: (
                <Space>
                  {block.block_name}
                  <Tooltip title={block.description}>
                    <QuestionCircleOutlined />
                  </Tooltip>
                </Space>
              ),
              value: block.block_name
            }))}
          />
        </Form.Item>

        {/* 已选中 Block 的配置 */}
        {selectedBlocks.map(blockName => {
          const blockInfo = blocks.find(b => b.block_name === blockName);
          if (!blockInfo) return null;

          return (
            <Card
              key={blockName}
              title={blockInfo.block_name}
              size="small"
              style={{ marginBottom: 16 }}
            >
              {/* <Typography.Text type="secondary" style={{ display: 'block', marginBottom: 16 }}>
                {blockInfo.description}
              </Typography.Text> */}

              {/* 显示可用函数 */}
              <div style={{ marginBottom: 16 }}>
                <Typography.Text strong>Available Functions:</Typography.Text>
                <div style={{ marginTop: 8 }}>
                  <Space wrap>
                    {blockInfo.functions.map((func, index) => (
                      <span key={index}>
                        <code>{func.function_name}</code>
                        <Tooltip title={func.description}>
                          <QuestionCircleOutlined style={{ marginLeft: 4 }} />
                        </Tooltip>
                      </span>
                    ))}
                  </Space>
                </div>
              </div>

              {/* 参数配置 */}
              {blockInfo.params && Object.keys(blockInfo.params).length > 0 && (
                <div>
                  <Typography.Text strong>Parameters:</Typography.Text>
                  <div style={{ marginTop: 8 }}>
                    {Object.entries(blockInfo.params).map(([paramName, param]) => (
                        <Form.Item
                          key={paramName}
                          name={['blocks', blockName, 'params', paramName]}
                          label={
                            <Space>
                              {paramName}
                              {param.description && (
                                <Tooltip title={param.description}>
                                  <QuestionCircleOutlined />
                                </Tooltip>
                              )}
                            </Space>
                          }
                        initialValue={param.default}
                        >
                        {renderParamField(param, blockName, paramName)}
                        </Form.Item>
                    ))}
                  </div>
                </div>
              )}
            </Card>
          );
        })}
      </Space>
    </Card>
  );
};

const AgentTemplateForm: React.FC = () => {
  const { t } = useTranslation();
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
          const blockTypes = Object.keys(template.blocks);
          setSelectedBlocks(blockTypes);

          form.setFieldsValue({
            name: template.name,
            description: template.description,
            profile: template.memory_distributions,
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
        agent_params: {
          enable_cognition: true,
          UBI: 1000,
          num_labor_hours: 168,
          productivity_per_labor: 1,
          time_diff: 2592000,
          max_plan_steps: 6
        },
        blocks: {}
      });
    }
  }, [id]);

  const handleBlockTypeChange = (values: string[]) => {
    setSelectedBlocks(values);

    // Update form blocks based on selected types
    const existingBlocks = form.getFieldValue('blocks') || {};

    // Keep blocks that are still selected
    const remainingBlocks = Object.fromEntries(Object.entries(existingBlocks).filter(([key]) => values.includes(key)));

    // Add new blocks for newly selected types
    const newBlockTypes = values.filter(type => !Object.keys(existingBlocks).includes(type));

    const newBlocks = newBlockTypes.map(type => ({
      [type]: {}
    }));

    form.setFieldsValue({
      blocks: { ...remainingBlocks, ...newBlocks }
    });
  };

  const handleSubmit = async () => {
    try {
      const values = await form.validateFields();
      console.log('Original form data:', JSON.stringify(values, null, 2));

      // 转换profile数据为memory_distributions格式
      const memory_distributions: Record<string, any> = {};
      Object.entries(values.profile).forEach(([key, value]: [string, any]) => {
        if (value.type === 'choice') {
          memory_distributions[key] = {
            dist_type: 'choice',
            choices: value.choices,
            weights: value.weights
          };
        } else if (value.type === 'uniform_int') {
          memory_distributions[key] = {
            dist_type: 'uniform_int',
            min_value: value.min_value,
            max_value: value.max_value
          };
        } else if (value.type === 'normal') {
          memory_distributions[key] = {
            dist_type: 'normal',
            mean: value.mean,
            std: value.std
          };
        }
      });

      // 处理blocks数据
      const blocksData: Record<string, any> = {};
      if (values.blocks) {
        Object.entries(values.blocks).forEach(([key, block]: [string, any]) => {
          if (block.params) {
            blocksData[key] = block.params;
          } else {
            blocksData[key] = {};
          }
        });
      }
      console.log('Converted blocks data:', JSON.stringify(blocksData, null, 2));

      // 构造模板数据
      const templateData = {
        name: values.name || 'Default Template Name',
        description: values.description || '',
        memory_distributions,
        agent_params: {
          enable_cognition: values.agent_params?.enable_cognition ?? true,
          UBI: values.agent_params?.UBI ?? 0,
          num_labor_hours: values.agent_params?.num_labor_hours ?? 8,
          productivity_per_labor: values.agent_params?.productivity_per_labor ?? 1.0,
          time_diff: values.agent_params?.time_diff ?? 1.0,
          max_plan_steps: values.agent_params?.max_plan_steps ?? 5,
          environment_reflection_prompt: values.agent_params?.environment_reflection_prompt,
          need_initialization_prompt: values.agent_params?.need_initialization_prompt,
          need_evaluation_prompt: values.agent_params?.need_evaluation_prompt,
          need_reflection_prompt: values.agent_params?.need_reflection_prompt,
          plan_generation_prompt: values.agent_params?.plan_generation_prompt
        },
        blocks: blocksData
      };

      console.log('Final submission data:', JSON.stringify(templateData, null, 2));

      const res = await fetchCustom('/api/agent-templates', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(templateData),
      });

      if (!res.ok) {
        const errorData = await res.json();
        console.log('API error response:', JSON.stringify(errorData, null, 2));
        throw new Error(errorData.detail || 'Failed to create template');
      }

      const data = await res.json();
      console.log('API success response:', JSON.stringify(data, null, 2));
      message.success(t('form.template.messages.createSuccess'));
      navigate('/agent-templates');
    } catch (error) {
      console.log('Error occurred during form submission:', error);
      message.error(error.message || t('form.template.messages.createFailed'));
    }
  };

  return (
    <div style={{ padding: '24px' }}>
      <Card
        title={id ? t('form.template.editTitle') : t('form.template.createTitle')}
        extra={
          <Space>
            <Button onClick={() => navigate('/agent-templates')}>{t('form.common.cancel')}</Button>
            <Button type="primary" onClick={() => form.submit()}>
              {t('form.common.submit')}
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
              <Card title={t('form.template.basicInfo')} bordered={false}>
                <Row gutter={16}>
                  <Col span={12}>
                    <Form.Item
                      name="name"
                      label={t('form.common.name')}
                      rules={[{ required: true }]}
                    >
                      <Input placeholder={t('form.template.namePlaceholder')} />
                    </Form.Item>
                  </Col>
                  <Col span={12}>
                    <Form.Item
                      name="description"
                      label={t('form.common.description')}
                    >
                      <Input.TextArea rows={2} placeholder={t('form.template.descriptionPlaceholder')} />
                    </Form.Item>
                  </Col>
                </Row>
              </Card>
            </Col>

            {/* Two-column layout starts */}
            <Col span={8} style={{ position: 'sticky', top: 24, height: 'calc(100vh - 200px)', overflowY: 'auto' }}>
              <div style={{ paddingRight: '16px' }}>
                {renderProfileSection(form)}
                {/* Left column: Base */}
                {renderBaseLocation()}
              </div>
            </Col>

            <Col span={16}>
              {/* Right column: Agent Configuration */}
              {renderAgentConfiguration()}

              {/* Right column: Block Configuration */}
              <BlockConfiguration />
            </Col>
          </Row>
        </Form>
      </Card>
    </div>
  );
};

export default AgentTemplateForm; 