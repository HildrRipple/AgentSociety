import React, { useState, useEffect } from 'react';
import { Table, Button, Card, Space, Modal, message, Tooltip, Input, Popconfirm, Form } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined, CopyOutlined, ExportOutlined } from '@ant-design/icons';
import AgentForm from '../ExperimentConfig/components/AgentForm';
import storageService, { STORAGE_KEYS, ConfigItem } from '../../services/storageService';

const AgentList: React.FC = () => {
  const [agents, setAgents] = useState<ConfigItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [searchText, setSearchText] = useState('');
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [currentAgent, setCurrentAgent] = useState<ConfigItem | null>(null);
  const [formValues, setFormValues] = useState<Record<string, unknown>>({});
  const [metaForm] = Form.useForm();

  // 加载智能体配置
  const loadAgents = async () => {
    setLoading(true);
    try {
      const data = await storageService.getConfigs<ConfigItem>(STORAGE_KEYS.AGENTS);
      setAgents(data);
    } catch (error) {
      message.error('Failed to load agents');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  // 初始化数据
  useEffect(() => {
    const init = async () => {
      await storageService.initializeExampleData();
      await loadAgents();
    };
    init();
  }, []);

  const handleSearch = (value: string) => {
    setSearchText(value);
  };

  const filteredAgents = agents.filter(agent => 
    agent.name.toLowerCase().includes(searchText.toLowerCase()) || 
    (agent.description && agent.description.toLowerCase().includes(searchText.toLowerCase()))
  );

  const handleCreate = () => {
    setCurrentAgent(null);
    setFormValues({});
    metaForm.resetFields();
    setIsModalVisible(true);
  };

  const handleEdit = (record: ConfigItem) => {
    setCurrentAgent(record);
    setFormValues(record.config);
    metaForm.setFieldsValue({
      name: record.name,
      description: record.description || ''
    });
    setIsModalVisible(true);
  };

  const handleDuplicate = (record: ConfigItem) => {
    setCurrentAgent(null);
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
      await storageService.deleteConfig(STORAGE_KEYS.AGENTS, id);
      message.success('Agent configuration deleted successfully');
      await loadAgents();
    } catch {
      message.error('Failed to delete agent configuration');
      setLoading(false);
    }
  };

  const handleExport = (record: ConfigItem) => {
    const dataStr = JSON.stringify(record.config, null, 2);
    const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);
    
    const exportFileDefaultName = `${record.name.replace(/\s+/g, '_')}_agent.json`;
    
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
      
      const configToSave: ConfigItem = currentAgent 
        ? { 
            ...currentAgent, 
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
      
      await storageService.saveConfig(STORAGE_KEYS.AGENTS, configToSave);
      
      message.success(currentAgent 
        ? 'Agent configuration updated successfully' 
        : 'Agent configuration created successfully'
      );
      
      setIsModalVisible(false);
      await loadAgents();
    } catch (error) {
      if (error instanceof Error) {
        message.error(`Failed to save agent configuration: ${error.message}`);
      } else {
        message.error('Failed to save agent configuration');
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
              title="Are you sure you want to delete this agent configuration?"
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
    <Card title="Agent Configurations" extra={
      <Space>
        <Input.Search
          placeholder="Search agents"
          onSearch={handleSearch}
          onChange={(e) => handleSearch(e.target.value)}
          style={{ width: 250 }}
        />
        <Button 
          type="primary" 
          icon={<PlusOutlined />} 
          onClick={handleCreate}
        >
          Create Agent
        </Button>
      </Space>
    }>
      <Table 
        columns={columns} 
        dataSource={filteredAgents} 
        rowKey="id"
        loading={loading}
        pagination={{ pageSize: 10 }}
      />

      <Modal
        title={currentAgent ? "Edit Agent Configuration" : "Create Agent Configuration"}
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
              rules={[{ required: true, message: 'Please enter a name for this configuration' }]}
            >
              <Input placeholder="Enter configuration name" />
            </Form.Item>
            <Form.Item
              name="description"
              label="Description"
            >
              <Input.TextArea 
                rows={2} 
                placeholder="Enter a description for this configuration" 
              />
            </Form.Item>
          </Form>
        </Card>
        
        <Card title="Agent Settings">
          <AgentForm 
            value={formValues} 
            onChange={setFormValues}
            environmentConfig={{}}
          />
        </Card>
      </Modal>
    </Card>
  );
};

export default AgentList; 
