import React, { useState, useEffect } from 'react';
import { Table, Button, Card, Space, Modal, message, Tooltip, Input, Popconfirm, Form } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined, CopyOutlined, ExportOutlined } from '@ant-design/icons';
import ExperimentForm from '../ExperimentConfig/components/ExperimentForm';
import storageService, { STORAGE_KEYS, ConfigItem } from '../../services/storageService';

const ExperimentTemplateList: React.FC = () => {
  const [templates, setTemplates] = useState<ConfigItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [searchText, setSearchText] = useState('');
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [currentTemplate, setCurrentTemplate] = useState<ConfigItem | null>(null);
  const [formValues, setFormValues] = useState<Record<string, unknown>>({});
  const [metaForm] = Form.useForm();
  const [environmentConfig, setEnvironmentConfig] = useState<Record<string, unknown>>({});
  const [agentConfig, setAgentConfig] = useState<Record<string, unknown>>({});

  // 加载实验模板配置
  const loadTemplates = async () => {
    setLoading(true);
    try {
      const data = await storageService.getConfigs<ConfigItem>(STORAGE_KEYS.WORKFLOWS);
      setTemplates(data);
      
      // 加载环境和智能体配置，用于实验表单
      const environments = await storageService.getConfigs<ConfigItem>(STORAGE_KEYS.ENVIRONMENTS);
      const agents = await storageService.getConfigs<ConfigItem>(STORAGE_KEYS.AGENTS);
      
      if (environments.length > 0) {
        setEnvironmentConfig(environments[0].config);
      }
      
      if (agents.length > 0) {
        setAgentConfig(agents[0].config);
      }
    } catch (error) {
      message.error('Failed to load experiment templates');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  // 初始化数据
  useEffect(() => {
    const init = async () => {
      await storageService.initializeExampleData();
      await loadTemplates();
    };
    init();
  }, []);

  const handleSearch = (value: string) => {
    setSearchText(value);
  };

  const filteredTemplates = templates.filter(template => 
    template.name.toLowerCase().includes(searchText.toLowerCase()) || 
    (template.description && template.description.toLowerCase().includes(searchText.toLowerCase()))
  );

  const handleCreate = () => {
    setCurrentTemplate(null);
    setFormValues({});
    metaForm.resetFields();
    setIsModalVisible(true);
  };

  const handleEdit = (record: ConfigItem) => {
    setCurrentTemplate(record);
    setFormValues(record.config);
    metaForm.setFieldsValue({
      name: record.name,
      description: record.description || ''
    });
    setIsModalVisible(true);
  };

  const handleDuplicate = (record: ConfigItem) => {
    setCurrentTemplate(null);
    setFormValues({
      ...record.config
    });
    metaForm.setFieldsValue({
      name: `Copy of ${record.name}`,
      description: record.description || ''
    });
    setIsModalVisible(true);
  };

  const handleDelete = async (id: string) => {
    try {
      setLoading(true);
      await storageService.deleteConfig(STORAGE_KEYS.WORKFLOWS, id);
      message.success('Experiment template deleted successfully');
      await loadTemplates();
    } catch {
      message.error('Failed to delete experiment template');
      setLoading(false);
    }
  };

  const handleExport = (record: ConfigItem) => {
    const dataStr = JSON.stringify(record.config, null, 2);
    const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);
    
    const exportFileDefaultName = `${record.name.replace(/\s+/g, '_')}_experiment.json`;
    
    const linkElement = document.createElement('a');
    linkElement.setAttribute('href', dataUri);
    linkElement.setAttribute('download', exportFileDefaultName);
    linkElement.click();
  };

  const handleModalOk = async () => {
    try {
      // 验证元数据表单
      const metaValues = await metaForm.validateFields();
      
      setLoading(true);
      
      const configToSave: ConfigItem = currentTemplate 
        ? { 
            ...currentTemplate, 
            name: metaValues.name,
            description: metaValues.description,
            config: formValues,
            updatedAt: new Date().toISOString()
          } 
        : {
            id: Date.now().toString(),
            name: metaValues.name,
            description: metaValues.description,
            createdAt: new Date().toISOString(),
            updatedAt: new Date().toISOString(),
            config: formValues
          };
      
      await storageService.saveConfig(STORAGE_KEYS.WORKFLOWS, configToSave);
      
      message.success(currentTemplate 
        ? 'Experiment template updated successfully' 
        : 'Experiment template created successfully'
      );
      
      setIsModalVisible(false);
      await loadTemplates();
    } catch (error) {
      if (error instanceof Error) {
        message.error(`Failed to save experiment template: ${error.message}`);
      } else {
        message.error('Failed to save experiment template');
      }
      setLoading(false);
    }
  };

  const handleModalCancel = () => {
    setIsModalVisible(false);
  };

  const columns = [
    {
      title: 'Name',
      dataIndex: 'name',
      key: 'name',
      sorter: (a: ConfigItem, b: ConfigItem) => a.name.localeCompare(b.name)
    },
    {
      title: 'Description',
      dataIndex: 'description',
      key: 'description',
      ellipsis: true
    },
    {
      title: 'Last Updated',
      dataIndex: 'updatedAt',
      key: 'updatedAt',
      render: (text: string) => new Date(text).toLocaleString(),
      sorter: (a: ConfigItem, b: ConfigItem) => 
        new Date(a.updatedAt).getTime() - new Date(b.updatedAt).getTime()
    },
    {
      title: 'Actions',
      key: 'actions',
      render: (_: unknown, record: ConfigItem) => (
        <Space size="small">
          <Tooltip title="Edit">
            <Button 
              icon={<EditOutlined />} 
              onClick={() => handleEdit(record)} 
              type="text"
            />
          </Tooltip>
          <Tooltip title="Duplicate">
            <Button 
              icon={<CopyOutlined />} 
              onClick={() => handleDuplicate(record)} 
              type="text"
            />
          </Tooltip>
          <Tooltip title="Export">
            <Button 
              icon={<ExportOutlined />} 
              onClick={() => handleExport(record)} 
              type="text"
            />
          </Tooltip>
          <Tooltip title="Delete">
            <Popconfirm
              title="Are you sure you want to delete this experiment template?"
              onConfirm={() => handleDelete(record.id)}
              okText="Yes"
              cancelText="No"
            >
              <Button 
                icon={<DeleteOutlined />} 
                type="text"
                danger
              />
            </Popconfirm>
          </Tooltip>
        </Space>
      )
    }
  ];

  return (
    <Card title="Experiment Templates" extra={
      <Space>
        <Input.Search
          placeholder="Search templates"
          onSearch={handleSearch}
          onChange={(e) => handleSearch(e.target.value)}
          style={{ width: 250 }}
        />
        <Button 
          type="primary" 
          icon={<PlusOutlined />} 
          onClick={handleCreate}
        >
          Create Template
        </Button>
      </Space>
    }>
      <Table 
        columns={columns} 
        dataSource={filteredTemplates} 
        rowKey="id"
        loading={loading}
        pagination={{ pageSize: 10 }}
      />

      <Modal
        title={currentTemplate ? "Edit Experiment Template" : "Create Experiment Template"}
        open={isModalVisible}
        onOk={handleModalOk}
        onCancel={handleModalCancel}
        width={800}
        confirmLoading={loading}
      >
        <Card title="Configuration Metadata" style={{ marginBottom: 16 }}>
          <Form
            form={metaForm}
            layout="vertical"
          >
            <Form.Item
              name="name"
              label="Name"
              rules={[{ required: true, message: 'Please enter a name for this template' }]}
            >
              <Input placeholder="Enter template name" />
            </Form.Item>
            <Form.Item
              name="description"
              label="Description"
            >
              <Input.TextArea 
                rows={2} 
                placeholder="Enter a description for this template" 
              />
            </Form.Item>
          </Form>
        </Card>
        
        <Card title="Experiment Settings">
          <ExperimentForm 
            value={formValues} 
            onChange={setFormValues}
            environmentConfig={environmentConfig}
            agentConfig={agentConfig}
          />
        </Card>
      </Modal>
    </Card>
  );
};

export default ExperimentTemplateList; 
