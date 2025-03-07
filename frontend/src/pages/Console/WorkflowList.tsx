import React, { useState, useEffect } from 'react';
import { Table, Button, Card, Space, Modal, message, Tooltip, Input, Popconfirm } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined, CopyOutlined, ExportOutlined } from '@ant-design/icons';
import ExperimentForm from '../ExperimentConfig/components/ExperimentForm';

interface WorkflowConfig {
  id: string;
  name: string;
  description?: string;
  createdAt: string;
  updatedAt: string;
  config: Record<string, unknown>;
}

const WorkflowList: React.FC = () => {
  const [workflows, setWorkflows] = useState<WorkflowConfig[]>([]);
  const [loading, setLoading] = useState(false);
  const [searchText, setSearchText] = useState('');
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [currentWorkflow, setCurrentWorkflow] = useState<WorkflowConfig | null>(null);
  const [formValues, setFormValues] = useState<Record<string, unknown>>({});

  // Mock data for demonstration
  useEffect(() => {
    setLoading(true);
    // In a real application, this would be an API call
    setTimeout(() => {
      const mockData: WorkflowConfig[] = [
        {
          id: '1',
          name: 'Standard City Simulation',
          description: 'Default city simulation workflow',
          createdAt: '2023-06-01T10:00:00Z',
          updatedAt: '2023-06-02T14:30:00Z',
          config: {
            experimentName: 'City Simulation',
            runMode: 'fast',
            timeScale: 10,
            maxSteps: 1000,
            workflow: [
              { type: 'run', days: 1 }
            ]
          }
        },
        {
          id: '2',
          name: 'Long-term Simulation',
          description: 'Extended simulation over multiple days',
          createdAt: '2023-06-03T09:15:00Z',
          updatedAt: '2023-06-03T09:15:00Z',
          config: {
            experimentName: 'Long-term Simulation',
            runMode: 'batch',
            timeScale: 100,
            maxSteps: 10000,
            workflow: [
              { type: 'run', days: 7 }
            ]
          }
        }
      ];
      setWorkflows(mockData);
      setLoading(false);
    }, 1000);
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
    setIsModalVisible(true);
  };

  const handleEdit = (record: WorkflowConfig) => {
    setCurrentWorkflow(record);
    setFormValues(record.config);
    setIsModalVisible(true);
  };

  const handleDuplicate = (record: WorkflowConfig) => {
    setCurrentWorkflow(null);
    setFormValues({
      ...record.config,
      name: `Copy of ${record.name}`
    });
    setIsModalVisible(true);
  };

  const handleDelete = async (id: string) => {
    try {
      setLoading(true);
      // In a real application, this would be an API call
      setTimeout(() => {
        setWorkflows(workflows.filter(workflow => workflow.id !== id));
        message.success('Workflow deleted successfully');
        setLoading(false);
      }, 500);
    } catch {
      message.error('Failed to delete workflow');
      setLoading(false);
    }
  };

  const handleExport = (record: WorkflowConfig) => {
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
      setLoading(true);
      // In a real application, this would be an API call to save the workflow
      setTimeout(() => {
        if (currentWorkflow) {
          // Update existing workflow
          const updatedWorkflows = workflows.map(workflow => 
            workflow.id === currentWorkflow.id 
              ? { 
                  ...workflow, 
                  config: formValues,
                  updatedAt: new Date().toISOString()
                } 
              : workflow
          );
          setWorkflows(updatedWorkflows);
          message.success('Workflow updated successfully');
        } else {
          // Create new workflow
          const newWorkflow: WorkflowConfig = {
            id: Date.now().toString(),
            name: (formValues.experimentName as string) || 'New Workflow',
            description: (formValues.experimentDescription as string) || '',
            createdAt: new Date().toISOString(),
            updatedAt: new Date().toISOString(),
            config: formValues
          };
          setWorkflows([...workflows, newWorkflow]);
          message.success('Workflow created successfully');
        }
        setIsModalVisible(false);
        setLoading(false);
      }, 500);
    } catch {
      message.error('Failed to save workflow');
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
      sorter: (a: WorkflowConfig, b: WorkflowConfig) => a.name.localeCompare(b.name)
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
      sorter: (a: WorkflowConfig, b: WorkflowConfig) => 
        new Date(a.updatedAt).getTime() - new Date(b.updatedAt).getTime()
    },
    {
      title: 'Actions',
      key: 'actions',
      render: (_: unknown, record: WorkflowConfig) => (
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
        <ExperimentForm 
          value={formValues} 
          onChange={setFormValues}
          environmentConfig={{}}
          agentConfig={{}}
        />
      </Modal>
    </Card>
  );
};

export default WorkflowList; 
