import React, { useState, useEffect } from 'react';
import { Table, Button, Card, Space, Modal, message, Tooltip, Input, Popconfirm } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined, CopyOutlined, ExportOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { fetchCustom } from '../../components/fetch';
import dayjs from 'dayjs';
import { useTranslation } from 'react-i18next';
import { ApiAgentTemplate } from '../../types/agentTemplate';


const AgentTemplateList: React.FC = () => {
  const [templates, setTemplates] = useState<ApiAgentTemplate[]>([]);
  const [loading, setLoading] = useState(false);
  const [searchText, setSearchText] = useState('');
  const navigate = useNavigate();
  const { t } = useTranslation();

  // Load templates
  const loadTemplates = async () => {
    try {
      setLoading(true);
      const res = await fetchCustom('/api/agent-templates');
      console.log('API response for template list:', await res.clone().json());

      if (!res.ok) {
        throw new Error('Failed to load templates');
      }

      const data = await res.json();
      console.log('Processed template data:', data);
      setTemplates(data.data);
    } catch (error) {
      console.error('Error loading templates:', error);
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

  // Duplicate template
  const handleDuplicate = async (template: ApiAgentTemplate) => {
    try {
      console.log('Duplicating template:', template);
      const duplicateData = {
        ...template,
        name: `${template.name} (Copy)`,
        id: undefined,
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
        console.error('Duplicate API error response:', errorData);
        throw new Error(errorData.detail || 'Failed to duplicate template');
      }

      message.success('Template duplicated successfully');
      loadTemplates();
    } catch (error) {
      console.error('Error duplicating template:', error);
      message.error(error.message || 'Failed to duplicate template');
    }
  };

  // Delete template
  const handleDelete = async (id: string) => {
    try {
      console.log('Attempting to delete template:', id);
      const res = await fetchCustom(`/api/agent-templates/${id}`, {
        method: 'DELETE'
      });

      if (!res.ok) {
        const errorData = await res.json();
        console.error('Delete API error response:', errorData);
        throw new Error(errorData.detail || 'Failed to delete template');
      }

      message.success('Template deleted successfully');
      loadTemplates();
    } catch (error) {
      console.error('Error deleting template:', error);
      message.error(error.message || 'Failed to delete template');
    }
  };

  // Export template
  const handleExport = (template: ApiAgentTemplate) => {
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
      title: t('common.name'),
      dataIndex: 'name',
      key: 'name',
    },
    {
      title: t('common.description'),
      dataIndex: 'description',
      key: 'description',
      ellipsis: true
    },
    {
      title: t('common.lastUpdated'),
      dataIndex: 'updated_at',
      key: 'updated_at',
      render: (text: string) => dayjs(text).format('YYYY-MM-DD HH:mm:ss')
    },
    {
      title: t('common.actions'),
      key: 'action',
      render: (_: any, record: ApiAgentTemplate) => (
        <Space size="small">
          {
            (record.tenant_id ?? '') !== '' && (
              <Tooltip title={t('common.edit')}>
                <Button icon={<EditOutlined />} size="small" onClick={() => navigate(`/agent-templates/edit/${record.id}`)} />
              </Tooltip>
            )
          }
          <Tooltip title={t('common.duplicate')}>
            <Button icon={<CopyOutlined />} size="small" onClick={() => handleDuplicate(record)} />
          </Tooltip>
          <Tooltip title={t('common.export')}>
            <Button icon={<ExportOutlined />} size="small" onClick={() => handleExport(record)} />
          </Tooltip>
          {
            (record.tenant_id ?? '') !== '' && (
              <Tooltip title={t('common.delete')}>
                <Popconfirm
                  title={t('common.deleteConfirm')}
                  onConfirm={() => handleDelete(record.id)}
                  okText={t('common.submit')}
                  cancelText={t('common.cancel')}
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
      title={t('template.title')}
      extra={<Button type="primary" icon={<PlusOutlined />} onClick={() => navigate('/agent-templates/create')}>{t('template.createNew')}</Button>}
    >
      <Input.Search
        placeholder={t('template.searchPlaceholder')}
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