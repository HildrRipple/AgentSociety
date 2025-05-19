import React, { useState, useEffect } from 'react';
import { Table, Button, Card, Space, Modal, message, Tooltip, Input, Popconfirm, Form, Tabs, Row, Col, Tag, Switch, InputNumber, Select } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined, CopyOutlined, ExportOutlined, BulbOutlined, CloseCircleOutlined } from '@ant-design/icons';
import { Link, useNavigate } from 'react-router-dom';
import { fetchCustom } from '../../components/fetch';
import dayjs from 'dayjs';
import { useTranslation } from 'react-i18next';

const { TabPane } = Tabs;

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
    fields: Record<string, string>; // name: type
  };
  base: {
    fields: Record<string, string>; // name: type
  };
  states: {
    fields: Record<string, string>; // name: type
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

// Add default profile fields based on memory_config.py
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

// 预设选项
const profileOptions = {
  name: ["Alice", "Bob", "Charlie", "David", "Eve", "Frank", "Grace",
    "Helen", "Ivy", "Jack", "Kelly", "Lily", "Mike", "Nancy",
    "Oscar", "Peter", "Queen", "Rose", "Sam", "Tom", "Ulysses",
    "Vicky", "Will", "Xavier", "Yvonne", "Zack"],
  gender: ["male", "female"],
  education: ["Doctor", "Master", "Bachelor", "College", "High School"],
  skill: ["Good at problem-solving", "Good at communication", "Good at creativity", "Good at teamwork", "Other"],
  occupation: ["Student", "Teacher", "Doctor", "Engineer", "Manager", "Businessman", "Artist", "Athlete", "Other"],
  family_consumption: ["low", "medium", "high"],
  consumption: ["low", "slightly low", "medium", "slightly high", "high"],
  personality: ["outgoint", "introvert", "ambivert", "extrovert"],
  residence: ["city", "suburb", "rural"],
  race: ["Chinese", "American", "British", "French", "German", "Japanese", "Korean", "Russian", "Other"],
  religion: ["none", "Christian", "Muslim", "Buddhist", "Hindu", "Other"],
  marital_status: ["not married", "married", "divorced", "widowed"]
};

// Add default base fields
const defaultBaseFields = {
  home: {
    aoi_position: {
      aoi_id: 'id'
    }
  },
  work: {
    aoi_position: {
      aoi_id: 'id'
    }
  }
};

// 添加 block 类型常量
const BLOCK_TYPES = {
  MOBILITYBLOCK: "mobilityblock",
  ECONOMYBLOCK: "economyblock",
  SOCIALBLOCK: "socialblock",
  OTHERBLOCK: "otherblock"
} as const;

// 添加 block 参数配置
const BLOCK_PARAMS_CONFIG = {
  [BLOCK_TYPES.MOBILITYBLOCK]: {
    search_limit: {
      type: 'number',
      default: 50,
      min: 1,
      description: "Number of POIs to retrieve from map service"
    }
  }
} as const;

const AgentTemplateList: React.FC = () => {
  const [templates, setTemplates] = useState<AgentTemplate[]>([]);
  const [loading, setLoading] = useState(false);
  const [searchText, setSearchText] = useState('');
  const [activeTab, setActiveTab] = useState('1');
  const navigate = useNavigate();
  const { t } = useTranslation();

  // Load templates
  const loadTemplates = async () => {
    try {
      setLoading(true);
      const res = await fetchCustom('/api/agent-templates');
      console.log('API response for template list:', await res.clone().json());  // 添加日志
      
      if (!res.ok) {
        throw new Error('Failed to load templates');
      }
      
      const data = await res.json();
      console.log('Processed template data:', data);  // 添加日志
      setTemplates(data.data);
    } catch (error) {
      console.error('Error loading templates:', error);  // 添加日志
      message.error('Failed to load templates');
    } finally {
      setLoading(false);
    }
  };

  // Initialize data
  useEffect(() => {
    loadTemplates();
  }, []);

  // Handle search
  const handleSearch = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchText(e.target.value);
  };

  // Filter templates based on search text
  const filteredTemplates = templates.filter(template =>
    template.name.toLowerCase().includes(searchText.toLowerCase()) ||
    (template.description && template.description.toLowerCase().includes(searchText.toLowerCase()))
  );

  // Create a new template
  const handleCreate = () => {
    navigate('/agent-templates/create');
  };

  // Duplicate template
  const handleDuplicate = async (template: AgentTemplate) => {
    try {
      console.log('Duplicating template:', template);  // 添加日志
      const duplicateData = {
        ...template,
        name: `${template.name} (Copy)`,
        id: undefined,  // 让服务器生成新ID
      };
      
      const res = await fetchCustom('/api/agent-templates', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(duplicateData),
      });

      if (!res.ok) {
        const errorData = await res.json();
        console.error('Duplicate API error response:', errorData);  // 添加日志
        throw new Error(errorData.detail || 'Failed to duplicate template');
      }

      message.success('Template duplicated successfully');
      loadTemplates();
    } catch (error) {
      console.error('Error duplicating template:', error);  // 添加日志
      message.error(error.message || 'Failed to duplicate template');
    }
  };

  // Delete template
  const handleDelete = async (id: string) => {
    try {
      console.log('Attempting to delete template:', id);  // 添加日志
      const res = await fetchCustom(`/api/agent-templates/${id}`, {
        method: 'DELETE'
      });
      
      if (!res.ok) {
        const errorData = await res.json();
        console.error('Delete API error response:', errorData);  // 添加日志
        throw new Error(errorData.detail || 'Failed to delete template');
      }

      message.success('Template deleted successfully');
      loadTemplates();
    } catch (error) {
      console.error('Error deleting template:', error);  // 添加日志
      message.error(error.message || 'Failed to delete template');
    }
  };

  // Export template
  const handleExport = (template: AgentTemplate) => {
    const dataStr = JSON.stringify(template, null, 2);
    const dataUri = `data:application/json;charset=utf-8,${encodeURIComponent(dataStr)}`;
    const exportFileDefaultName = `${template.name.replace(/\s+/g, '_')}_template.json`;
    
    const linkElement = document.createElement('a');
    linkElement.setAttribute('href', dataUri);
    linkElement.setAttribute('download', exportFileDefaultName);
    linkElement.click();
  };

  // Table columns
  const columns = [
    {
      title: t('form.common.name'),
      dataIndex: 'name',
      key: 'name',
    },
    {
      title: t('form.common.description'),
      dataIndex: 'description',
      key: 'description',
      ellipsis: true
    },
    {
      title: t('form.common.lastUpdated'),
      dataIndex: 'updated_at',
      key: 'updated_at',
      render: (text: string) => dayjs(text).format('YYYY-MM-DD HH:mm:ss')
    },
    {
      title: t('form.common.actions'),
      key: 'action',
      render: (_: any, record: AgentTemplate) => (
        <Space size="small">
          {
            (record.tenant_id ?? '') !== '' && (
              <Tooltip title={t('form.common.edit')}>
                <Button icon={<EditOutlined />} size="small" onClick={() => navigate(`/agent-templates/edit/${record.id}`)} />
              </Tooltip>
            )
          }
          <Tooltip title={t('form.common.duplicate')}>
            <Button icon={<CopyOutlined />} size="small" onClick={() => handleDuplicate(record)} />
          </Tooltip>
          <Tooltip title={t('form.common.export')}>
            <Button icon={<ExportOutlined />} size="small" onClick={() => handleExport(record)} />
          </Tooltip>
          {
            (record.tenant_id ?? '') !== '' && (
              <Tooltip title={t('form.common.delete')}>
                <Popconfirm
                  title={t('form.common.deleteConfirm')}
                  onConfirm={() => handleDelete(record.id)}
                  okText={t('form.common.submit')}
                  cancelText={t('form.common.cancel')}
                >
                  <Button icon={<DeleteOutlined />} size="small" danger />
                </Popconfirm>
              </Tooltip>
            )
          }
        </Space>
      )
    }
  ];

  return (
    <Card
      title={t('form.template.title')}
      extra={<Button type="primary" icon={<PlusOutlined />} onClick={() => navigate('/agent-templates/create')}>{t('form.template.createNew')}</Button>}
    >
      <Input.Search
        placeholder={t('form.template.searchPlaceholder')}
        onChange={handleSearch}
        style={{ marginBottom: 16 }}
      />
      
      <Table
        columns={columns}
        dataSource={filteredTemplates}
        rowKey="id"
        loading={loading}
        pagination={{ pageSize: 10 }}
      />
    </Card>
  );
};

export default AgentTemplateList; 