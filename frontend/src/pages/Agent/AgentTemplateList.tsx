import React, { useState, useEffect } from 'react';
import { Table, Button, Card, Space, Modal, message, Tooltip, Input, Popconfirm, Form, Tabs, Row, Col, Tag, Switch, InputNumber, Select } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined, CopyOutlined, ExportOutlined, BulbOutlined, CloseCircleOutlined } from '@ant-design/icons';
import { Link, useNavigate } from 'react-router-dom';
import { fetchCustom } from '../../components/fetch';
import dayjs from 'dayjs';

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

const AgentTemplate: React.FC = () => {
  const [templates, setTemplates] = useState<AgentTemplate[]>([]);
  const [loading, setLoading] = useState(false);
  const [searchText, setSearchText] = useState('');
  const [activeTab, setActiveTab] = useState('1');
  const navigate = useNavigate();

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
      title: 'Name',
      dataIndex: 'name',
      key: 'name',
      render: (text: string) => <strong>{text}</strong>
    },
    {
      title: 'Description',
      dataIndex: 'description',
      key: 'description',
      ellipsis: true
    },
    {
      title: 'Created At',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (text: string) => dayjs(text).format('YYYY-MM-DD HH:mm:ss')
    },
    {
      title: 'Updated At',
      dataIndex: 'updated_at',
      key: 'updated_at',
      render: (text: string) => dayjs(text).format('YYYY-MM-DD HH:mm:ss')
    },
    {
      title: 'Actions',
      key: 'actions',
      render: (_, record: AgentTemplate) => (
        <Space>
          <Button 
            icon={<EditOutlined />} 
            onClick={() => navigate(`/agent-templates/edit/${record.id}`)}
            size="small"
          />
          <Button 
            icon={<CopyOutlined />} 
            onClick={() => handleDuplicate(record)}
            size="small"
          />
          <Button 
            icon={<ExportOutlined />} 
            onClick={() => handleExport(record)}
            size="small"
          />
          <Popconfirm
            title="Are you sure you want to delete this template?"
            onConfirm={() => handleDelete(record.id)}
            okText="Yes"
            cancelText="No"
          >
            <Button 
              icon={<DeleteOutlined />} 
              danger 
              size="small"
            />
          </Popconfirm>
        </Space>
      )
    }
  ];

  return (
    <Card
      title="Agent Templates"
      extra={
        <Button type="primary" icon={<PlusOutlined />} onClick={handleCreate}>
          Create Template
        </Button>
      }
    >
      <Input.Search
        placeholder="Search templates"
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

export default AgentTemplate; 