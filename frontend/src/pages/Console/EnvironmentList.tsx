import React, { useState, useEffect } from 'react';
import { Table, Button, Card, Space, Modal, message, Tooltip, Input, Popconfirm, Form } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined, CopyOutlined, ExportOutlined } from '@ant-design/icons';
import EnvironmentForm from './EnvironmentForm';
import storageService, { STORAGE_KEYS, ConfigItem } from '../../services/storageService';
import configService from '../../services/configService';
import { SimConfig } from '../../types/config';

const EnvironmentList: React.FC = () => {
  const [environments, setEnvironments] = useState<ConfigItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [searchText, setSearchText] = useState('');
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [currentEnvironment, setCurrentEnvironment] = useState<ConfigItem | null>(null);
  const [formValues, setFormValues] = useState<Partial<SimConfig>>({});
  const [metaForm] = Form.useForm();

  // Load environment configurations
  const loadEnvironments = async () => {
    setLoading(true);
    try {
      const data = await storageService.getConfigs<ConfigItem>(STORAGE_KEYS.ENVIRONMENTS);
      setEnvironments(data);
    } catch (error) {
      message.error('Failed to load environments');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  // Initialize data
  useEffect(() => {
    const init = async () => {
      await storageService.initializeExampleData();
      await loadEnvironments();
    };
    init();
  }, []);

  // Handle search
  const handleSearch = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchText(e.target.value);
  };

  // Filter environments based on search text
  const filteredEnvironments = environments.filter(env => 
    env.name.toLowerCase().includes(searchText.toLowerCase()) || 
    (env.description && env.description.toLowerCase().includes(searchText.toLowerCase()))
  );

  // Handle create new environment
  const handleCreate = () => {
    setCurrentEnvironment(null);
    setFormValues(configService.getDefaultConfigs().environment);
    metaForm.setFieldsValue({
      name: `Environment ${environments.length + 1}`,
      description: ''
    });
    setIsModalVisible(true);
  };

  // Handle edit environment
  const handleEdit = (environment: ConfigItem) => {
    setCurrentEnvironment(environment);
    setFormValues(environment.config);
    metaForm.setFieldsValue({
      name: environment.name,
      description: environment.description
    });
    setIsModalVisible(true);
  };

  // Handle duplicate environment
  const handleDuplicate = (environment: ConfigItem) => {
    setCurrentEnvironment(null);
    setFormValues(environment.config);
    metaForm.setFieldsValue({
      name: `${environment.name} (Copy)`,
      description: environment.description
    });
    setIsModalVisible(true);
  };

  // Handle delete environment
  const handleDelete = async (id: string) => {
    try {
      await storageService.deleteConfig(STORAGE_KEYS.ENVIRONMENTS, id);
      message.success('Environment deleted successfully');
      loadEnvironments();
    } catch (error) {
      message.error('Failed to delete environment');
      console.error(error);
    }
  };

  // Handle export environment
  const handleExport = (environment: ConfigItem) => {
    const dataStr = JSON.stringify(environment, null, 2);
    const dataUri = `data:application/json;charset=utf-8,${encodeURIComponent(dataStr)}`;
    
    const exportFileDefaultName = `${environment.name.replace(/\s+/g, '_')}_environment.json`;
    
    const linkElement = document.createElement('a');
    linkElement.setAttribute('href', dataUri);
    linkElement.setAttribute('download', exportFileDefaultName);
    linkElement.click();
  };

  // Handle modal OK
  const handleModalOk = async () => {
    try {
      // Validate meta form
      const metaValues = await metaForm.validateFields();
      
      const configData: ConfigItem = {
        id: currentEnvironment?.id || `env_${Date.now()}`,
        name: metaValues.name,
        description: metaValues.description || '',
        config: formValues,
        createdAt: currentEnvironment?.createdAt || new Date().toISOString(),
        updatedAt: new Date().toISOString()
      };
      
      await storageService.saveConfig(STORAGE_KEYS.ENVIRONMENTS, configData);
      
      message.success(`Environment ${currentEnvironment ? 'updated' : 'created'} successfully`);
      setIsModalVisible(false);
      loadEnvironments();
    } catch (error) {
      console.error('Validation failed:', error);
    }
  };

  // Handle modal cancel
  const handleModalCancel = () => {
    setIsModalVisible(false);
  };

  // Table columns
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
      sorter: (a: ConfigItem, b: ConfigItem) => new Date(a.updatedAt).getTime() - new Date(b.updatedAt).getTime()
    },
    {
      title: 'Actions',
      key: 'actions',
      render: (_: any, record: ConfigItem) => (
        <Space size="small">
          <Tooltip title="Edit">
            <Button icon={<EditOutlined />} size="small" onClick={() => handleEdit(record)} />
          </Tooltip>
          <Tooltip title="Duplicate">
            <Button icon={<CopyOutlined />} size="small" onClick={() => handleDuplicate(record)} />
          </Tooltip>
          <Tooltip title="Export">
            <Button icon={<ExportOutlined />} size="small" onClick={() => handleExport(record)} />
          </Tooltip>
          <Tooltip title="Delete">
            <Popconfirm
              title="Are you sure you want to delete this environment?"
              onConfirm={() => handleDelete(record.id)}
              okText="Yes"
              cancelText="No"
            >
              <Button icon={<DeleteOutlined />} size="small" danger />
            </Popconfirm>
          </Tooltip>
        </Space>
      )
    }
  ];

  return (
    <Card 
      title="Environment Configurations" 
      extra={<Button type="primary" icon={<PlusOutlined />} onClick={handleCreate}>Create New</Button>}
    >
      <Input.Search
        placeholder="Search environments"
        onChange={handleSearch}
        style={{ marginBottom: 16 }}
      />
      
      <Table
        columns={columns}
        dataSource={filteredEnvironments}
        rowKey="id"
        loading={loading}
        pagination={{ pageSize: 10 }}
      />
      
      <Modal
        title={currentEnvironment ? "Edit Environment" : "Create Environment"}
        open={isModalVisible}
        onOk={handleModalOk}
        onCancel={handleModalCancel}
        width={800}
        destroyOnClose
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
        
        <Card title="Environment Settings">
          <EnvironmentForm 
            value={formValues} 
            onChange={setFormValues}
          />
        </Card>
      </Modal>
    </Card>
  );
};

export default EnvironmentList; 
