import React, { useState, useEffect } from 'react';
import { Table, Button, Card, Space, Modal, message, Tooltip, Input, Popconfirm, Form } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined, CopyOutlined, ExportOutlined } from '@ant-design/icons';
import ExperimentForm from '../ExperimentConfig/components/ExperimentForm';
import storageService, { STORAGE_KEYS, ConfigItem } from '../../services/storageService';

const WorkflowList: React.FC = () => {
  const [workflows, setWorkflows] = useState<ConfigItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [searchText, setSearchText] = useState('');
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [currentWorkflow, setCurrentWorkflow] = useState<ConfigItem | null>(null);
  const [formValues, setFormValues] = useState<Record<string, unknown>>({});
  const [metaForm] = Form.useForm();
  const [environmentConfig, setEnvironmentConfig] = useState<Record<string, unknown>>({});
  const [agentConfig, setAgentConfig] = useState<Record<string, unknown>>({});

  // 加载工作流配置
  const loadWorkflows = async () => {
    setLoading(true);
    try {
      const data = await storageService.getConfigs<ConfigItem>(STORAGE_KEYS.WORKFLOWS);
      setWorkflows(data);
      
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
      message.error('Failed to load workflows');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  // 初始化数据
  useEffect(() => {
    const init = async () => {
      await storageService.initializeExampleData();
      await loadWorkflows();
    };
    init();
  }, []);

  const handleSearch = (value: string) => {
    setSearchText(value);
  };

  const filteredWorkflows = workflows.filter(workflow => 
    workflow.name.toLowerCase().includes(searchText.toLowerCase()) || 
    (workflow.description && workflow.description.toLowerCase().includes(searchText.toLowerCase()))
  );

  const handleCreate = () => {
    setCurrentWorkflow(null);
    setFormValues({});
    metaForm.resetFields();
    setIsModalVisible(true);
  };

  const handleEdit = (record: ConfigItem) => {
    setCurrentWorkflow(record);
    setFormValues(record.config);
    metaForm.setFieldsValue({
      name: record.name,
      description: record.description || ''
    });
    setIsModalVisible(true);
  };

  const handleDuplicate = (record: ConfigItem) => {
    setCurrentWorkflow(null);
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
      message.success('Workflow deleted successfully');
      await loadWorkflows();
    } catch {
      message.error('Failed to delete workflow');
      setLoading(false);
    }
  };

  const handleExport = (record: ConfigItem) => {
    const dataStr = JSON.stringify(record.config, null, 2);
    const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);
    
    const exportFileDefaultName = `${record.name.replace(/\s+/g, '_')}_workflow.json`;
    
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
      
      const configToSave: ConfigItem = currentWorkflow 
        ? { 
            ...currentWorkflow, 
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
      
      message.success(currentWorkflow 
        ? 'Workflow updated successfully' 
        : 'Workflow created successfully'
      );
      
      setIsModalVisible(false);
      await loadWorkflows();
    } catch (error) {
      if (error instanceof Error) {
        message.error(`Failed to save workflow: ${error.message}`);
      } else {
        message.error('Failed to save workflow');
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
              title="Are you sure you want to delete this workflow?"
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
    <Card title="Workflow Configurations" extra={
      <Space>
        <Input.Search
          placeholder="Search workflows"
          onSearch={handleSearch}
          onChange={(e) => handleSearch(e.target.value)}
          style={{ width: 250 }}
        />
        <Button 
          type="primary" 
          icon={<PlusOutlined />} 
          onClick={handleCreate}
        >
          Create Workflow
        </Button>
      </Space>
    }>
      <Table 
        columns={columns} 
        dataSource={filteredWorkflows} 
        rowKey="id"
        loading={loading}
        pagination={{ pageSize: 10 }}
      />

      <Modal
        title={currentWorkflow ? "Edit Workflow" : "Create Workflow"}
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
              rules={[{ required: true, message: 'Please enter a name for this workflow' }]}
            >
              <Input placeholder="Enter workflow name" />
            </Form.Item>
            <Form.Item
              name="description"
              label="Description"
            >
              <Input.TextArea 
                rows={2} 
                placeholder="Enter a description for this workflow" 
              />
            </Form.Item>
          </Form>
        </Card>
        
        <Card title="Workflow Settings">
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

export default WorkflowList; 
