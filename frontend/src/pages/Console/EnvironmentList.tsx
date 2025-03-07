import React, { useState, useEffect } from 'react';
import { Table, Button, Card, Space, Modal, message, Tooltip, Input, Popconfirm } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined, CopyOutlined, ExportOutlined } from '@ant-design/icons';
import EnvironmentForm from '../ExperimentConfig/components/EnvironmentForm';
import storageService, { STORAGE_KEYS, ConfigItem } from '../../services/storageService';

const EnvironmentList: React.FC = () => {
  const [environments, setEnvironments] = useState<ConfigItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [searchText, setSearchText] = useState('');
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [currentEnvironment, setCurrentEnvironment] = useState<ConfigItem | null>(null);
  const [formValues, setFormValues] = useState<Record<string, unknown>>({});

  // 加载环境配置
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

  // 初始化数据
  useEffect(() => {
    const init = async () => {
      await storageService.initializeExampleData();
      await loadEnvironments();
    };
    init();
  }, []);

  const handleSearch = (value: string) => {
    setSearchText(value);
  };

  const filteredEnvironments = environments.filter(env => 
    env.name.toLowerCase().includes(searchText.toLowerCase()) || 
    (env.description && env.description.toLowerCase().includes(searchText.toLowerCase()))
  );

  const handleCreate = () => {
    setCurrentEnvironment(null);
    setFormValues({});
    setIsModalVisible(true);
  };

  const handleEdit = (record: ConfigItem) => {
    setCurrentEnvironment(record);
    setFormValues(record.config);
    setIsModalVisible(true);
  };

  const handleDuplicate = (record: ConfigItem) => {
    setCurrentEnvironment(null);
    setFormValues({
      ...record.config,
      name: `Copy of ${record.name}`
    });
    setIsModalVisible(true);
  };

  const handleDelete = async (id: string) => {
    try {
      setLoading(true);
      await storageService.deleteConfig(STORAGE_KEYS.ENVIRONMENTS, id);
      message.success('Environment deleted successfully');
      await loadEnvironments();
    } catch {
      message.error('Failed to delete environment');
      setLoading(false);
    }
  };

  const handleExport = (record: ConfigItem) => {
    const dataStr = JSON.stringify(record.config, null, 2);
    const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);
    
    const exportFileDefaultName = `${record.name.replace(/\s+/g, '_')}_environment.json`;
    
    const linkElement = document.createElement('a');
    linkElement.setAttribute('href', dataUri);
    linkElement.setAttribute('download', exportFileDefaultName);
    linkElement.click();
  };

  const handleModalOk = async () => {
    try {
      setLoading(true);
      
      const configToSave: ConfigItem = currentEnvironment 
        ? { 
            ...currentEnvironment, 
            config: formValues,
            updatedAt: new Date().toISOString()
          } 
        : {
            id: Date.now().toString(),
            name: (formValues.name as string) || 'New Environment',
            description: (formValues.description as string) || '',
            createdAt: new Date().toISOString(),
            updatedAt: new Date().toISOString(),
            config: formValues
          };
      
      await storageService.saveConfig(STORAGE_KEYS.ENVIRONMENTS, configToSave);
      
      message.success(currentEnvironment 
        ? 'Environment updated successfully' 
        : 'Environment created successfully'
      );
      
      setIsModalVisible(false);
      await loadEnvironments();
    } catch {
      message.error('Failed to save environment');
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
              title="Are you sure you want to delete this environment?"
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
    <Card title="Environment Configurations" extra={
      <Space>
        <Input.Search
          placeholder="Search environments"
          onSearch={handleSearch}
          onChange={(e) => handleSearch(e.target.value)}
          style={{ width: 250 }}
        />
        <Button 
          type="primary" 
          icon={<PlusOutlined />} 
          onClick={handleCreate}
        >
          Create Environment
        </Button>
      </Space>
    }>
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
        confirmLoading={loading}
      >
        <EnvironmentForm 
          value={formValues} 
          onChange={setFormValues} 
        />
      </Modal>
    </Card>
  );
};

export default EnvironmentList; 
