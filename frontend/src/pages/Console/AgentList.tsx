import React, { useState, useEffect } from 'react';
import { Table, Button, Card, Space, Modal, message, Tooltip, Input, Popconfirm } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined, CopyOutlined, ExportOutlined } from '@ant-design/icons';
import AgentForm from '../ExperimentConfig/components/AgentForm';

interface AgentConfig {
  id: string;
  name: string;
  description?: string;
  createdAt: string;
  updatedAt: string;
  config: Record<string, unknown>;
}

const AgentList: React.FC = () => {
  const [agents, setAgents] = useState<AgentConfig[]>([]);
  const [loading, setLoading] = useState(false);
  const [searchText, setSearchText] = useState('');
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [currentAgent, setCurrentAgent] = useState<AgentConfig | null>(null);
  const [formValues, setFormValues] = useState<Record<string, unknown>>({});

  // Mock data for demonstration
  useEffect(() => {
    setLoading(true);
    // In a real application, this would be an API call
    setTimeout(() => {
      const mockData: AgentConfig[] = [
        {
          id: '1',
          name: 'Default Citizen Agent',
          description: 'Standard citizen agent configuration',
          createdAt: '2023-06-01T10:00:00Z',
          updatedAt: '2023-06-02T14:30:00Z',
          config: {
            agent_config: {
              number_of_citizen: 100
            },
            agentType: 'llm',
            profile: {
              name: 'random',
              gender: 'equal',
              age: { min: 18, max: 65 }
            }
          }
        },
        {
          id: '2',
          name: 'Business Agent',
          description: 'Business owner agent configuration',
          createdAt: '2023-06-03T09:15:00Z',
          updatedAt: '2023-06-03T09:15:00Z',
          config: {
            agent_config: {
              number_of_citizen: 50
            },
            agentType: 'rule',
            profile: {
              occupation: ['Businessman', 'Manager'],
              income: { min: 5000, max: 20000 }
            }
          }
        }
      ];
      setAgents(mockData);
      setLoading(false);
    }, 1000);
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
    setIsModalVisible(true);
  };

  const handleEdit = (record: AgentConfig) => {
    setCurrentAgent(record);
    setFormValues(record.config);
    setIsModalVisible(true);
  };

  const handleDuplicate = (record: AgentConfig) => {
    setCurrentAgent(null);
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
        setAgents(agents.filter(agent => agent.id !== id));
        message.success('Agent configuration deleted successfully');
        setLoading(false);
      }, 500);
    } catch {
      message.error('Failed to delete agent configuration');
      setLoading(false);
    }
  };

  const handleExport = (record: AgentConfig) => {
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
      setLoading(true);
      // In a real application, this would be an API call to save the agent
      setTimeout(() => {
        if (currentAgent) {
          // Update existing agent
          const updatedAgents = agents.map(agent => 
            agent.id === currentAgent.id 
              ? { 
                  ...agent, 
                  config: formValues,
                  updatedAt: new Date().toISOString()
                } 
              : agent
          );
          setAgents(updatedAgents);
          message.success('Agent configuration updated successfully');
        } else {
          // Create new agent
          const newAgent: AgentConfig = {
            id: Date.now().toString(),
            name: (formValues.name as string) || 'New Agent',
            description: (formValues.description as string) || '',
            createdAt: new Date().toISOString(),
            updatedAt: new Date().toISOString(),
            config: formValues
          };
          setAgents([...agents, newAgent]);
          message.success('Agent configuration created successfully');
        }
        setIsModalVisible(false);
        setLoading(false);
      }, 500);
    } catch {
      message.error('Failed to save agent configuration');
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
      sorter: (a: AgentConfig, b: AgentConfig) => a.name.localeCompare(b.name)
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
      sorter: (a: AgentConfig, b: AgentConfig) => 
        new Date(a.updatedAt).getTime() - new Date(b.updatedAt).getTime()
    },
    {
      title: 'Actions',
      key: 'actions',
      render: (_: unknown, record: AgentConfig) => (
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
        <AgentForm 
          value={formValues} 
          onChange={setFormValues}
          environmentConfig={{}}
        />
      </Modal>
    </Card>
  );
};

export default AgentList; 
