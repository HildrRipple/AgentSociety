import React, { useState, useEffect } from 'react';
import { Table, Button, Card, Space, Modal, message, Tooltip, Input, Popconfirm, Form, Row, Col } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined, CopyOutlined, ExportOutlined } from '@ant-design/icons';
import AgentForm from './AgentForm';
import { AgentsConfig, ConfigWrapper } from '../../types/config';
import { fetchCustom } from '../../components/fetch';
import dayjs from 'dayjs';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router-dom';

const AgentList: React.FC = () => {
    const navigate = useNavigate();
    const { t } = useTranslation();
    const [agents, setAgents] = useState<ConfigWrapper<AgentsConfig>[]>([]);
    const [loading, setLoading] = useState(false);
    const [searchText, setSearchText] = useState('');
    const [isModalVisible, setIsModalVisible] = useState(false);
    const [currentAgent, setCurrentAgent] = useState<ConfigWrapper<AgentsConfig> | null>(null);
    const [formValues, setFormValues] = useState<Partial<AgentsConfig>>({});
    const [metaForm] = Form.useForm();

    // Load agent configurations
    const loadAgents = async () => {
        setLoading(true);
        try {
            const res = await fetchCustom('/api/agent-configs');
            if (!res.ok) {
                throw new Error(await res.text());
            }
            const data = (await res.json()).data;
            setAgents(data);
        } catch (error) {
            message.error(t('agent.messages.loadFailed') + `: ${JSON.stringify(error.message)}`, 3);
            console.error(error);
        } finally {
            setLoading(false);
        }
    };

    // Initialize data
    useEffect(() => {
        const init = async () => {
            await loadAgents();
        };
        init();
    }, []);

    // Handle search
    const handleSearch = (e: React.ChangeEvent<HTMLInputElement>) => {
        setSearchText(e.target.value);
    };

    // Filter agents based on search text
    const filteredAgents = agents.filter(agent =>
        agent.name.toLowerCase().includes(searchText.toLowerCase()) ||
        (agent.description && agent.description.toLowerCase().includes(searchText.toLowerCase()))
    );

    // Handle create new agent
    const handleCreate = () => {
        setCurrentAgent(null);
        // Create a basic agent config based on config.json structure
        setFormValues({
            citizens: [
                {
                    agent_class: 'citizen',
                    number: 10,
                    memory_config_func: null,
                    memory_distributions: null
                }
            ],
            firms: [
                {
                    agent_class: 'firm',
                    number: 5,
                    memory_config_func: null,
                    memory_distributions: null
                }
            ],
            governments: [
                {
                    agent_class: 'government',
                    number: 1,
                    memory_config_func: null,
                    memory_distributions: null
                }
            ],
            banks: [
                {
                    agent_class: 'bank',
                    number: 1,
                    memory_config_func: null,
                    memory_distributions: null
                }
            ],
            nbs: [
                {
                    agent_class: 'nbs',
                    number: 1,
                    memory_config_func: null,
                    memory_distributions: null
                }
            ]
        });
        metaForm.setFieldsValue({
            name: `Agent ${agents.length + 1}`,
            description: ''
        });
        setIsModalVisible(true);
    };

    // Handle edit agent
    const handleEdit = (agent: ConfigWrapper<AgentsConfig>) => {
        setCurrentAgent(agent);
        setFormValues(agent.config);
        metaForm.setFieldsValue({
            name: agent.name,
            description: agent.description
        });
        setIsModalVisible(true);
    };

    // Handle duplicate agent
    const handleDuplicate = (agent: ConfigWrapper<AgentsConfig>) => {
        setCurrentAgent(null);
        setFormValues(agent.config);
        metaForm.setFieldsValue({
            name: `${agent.name} (Copy)`,
            description: agent.description
        });
        setIsModalVisible(true);
    };

    // Handle delete agent
    const handleDelete = async (id: string) => {
        try {
            const res = await fetchCustom(`/api/agent-configs/${id}`, {
                method: 'DELETE'
            });
            if (!res.ok) {
                throw new Error(await res.text());
            }
            message.success(t('agent.messages.deleteSuccess'));
            loadAgents();
        } catch (error) {
            message.error(t('agent.messages.deleteFailed') + `: ${JSON.stringify(error.message)}`, 3);
            console.error(error);
        }
    };

    // Handle export agent
    const handleExport = (agent: ConfigWrapper<AgentsConfig>) => {
        const dataStr = JSON.stringify(agent, null, 2);
        const dataUri = `data:application/json;charset=utf-8,${encodeURIComponent(dataStr)}`;

        const exportFileDefaultName = `${agent.name.replace(/\s+/g, '_')}_agent.json`;

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

            const configData = {
                name: metaValues.name,
                description: metaValues.description || '',
                config: formValues,
            };
            let res: Response;
            if (currentAgent) {
                res = await fetchCustom(`/api/agent-configs/${currentAgent.id}`, {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(configData),
                });
            } else {
                res = await fetchCustom('/api/agent-configs', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(configData),
                });
            }
            if (!res.ok) {
                throw new Error(await res.text());
            }
            message.success(currentAgent ? t('agent.messages.updateSuccess') : t('agent.messages.createSuccess'));
            setIsModalVisible(false);
            loadAgents();
        } catch (error) {
            message.error((currentAgent ? t('agent.messages.updateFailed') : t('agent.messages.createFailed')) + `: ${JSON.stringify(error.message)}`, 3);
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
            title: t('common.name'),
            dataIndex: 'name',
            key: 'name',
            sorter: (a: ConfigWrapper<AgentsConfig>, b: ConfigWrapper<AgentsConfig>) => a.name.localeCompare(b.name)
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
            render: (text: string) => dayjs(text).format('YYYY-MM-DD HH:mm:ss'),
            sorter: (a: ConfigWrapper<AgentsConfig>, b: ConfigWrapper<AgentsConfig>) => dayjs(a.updated_at).valueOf() - dayjs(b.updated_at).valueOf()
        },
        {
            title: t('common.actions'),
            key: 'actions',
            render: (_: any, record: ConfigWrapper<AgentsConfig>) => (
                <Space size="small">
                    {
                        (record.tenant_id ?? '') !== '' && (
                            <Tooltip title={t('common.edit')}>
                                <Button icon={<EditOutlined />} size="small" onClick={() => handleEdit(record)} />
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
            title={t('agent.title')}
            extra={
                <Space>
                    <Button onClick={() => navigate('/agent-templates')}>{t('agent.templates')}</Button>
                    <Button onClick={() => navigate('/profiles')}>{t('agent.profiles')}</Button>
                    <Button type="primary" icon={<PlusOutlined />} onClick={handleCreate}>{t('agent.createNew')}</Button>
                </Space>
            }
        >
            <Input.Search
                placeholder={t('agent.searchPlaceholder')}
                onChange={handleSearch}
                style={{ marginBottom: 16 }}
            />

            <Table
                columns={columns}
                dataSource={filteredAgents}
                rowKey="id"
                loading={loading}
                pagination={{ pageSize: 10 }}
            />

            <Modal
                title={currentAgent ? t('agent.editTitle') : t('agent.createTitle')}
                open={isModalVisible}
                onOk={handleModalOk}
                onCancel={handleModalCancel}
                width="80vw"
                destroyOnHidden
            >
                <Card title={t('common.metadataTitle')} style={{ marginBottom: 8 }}>
                    <Form
                        form={metaForm}
                        layout="vertical"
                    >
                        <Row gutter={16}>
                            <Col span={8}>
                                <Form.Item
                                    name="name"
                                    label={t('common.name')}
                                    rules={[{ required: true, message: t('common.nameRequired') }]}
                                    style={{ marginBottom: 8 }}
                                >
                                    <Input placeholder={t('common.namePlaceholder')} />
                                </Form.Item>
                            </Col>
                            <Col span={16}>
                                <Form.Item
                                    name="description"
                                    label={t('common.description')}
                                    style={{ marginBottom: 0 }}
                                >
                                    <Input.TextArea
                                        rows={1}
                                        placeholder={t('common.descriptionPlaceholder')}
                                    />
                                </Form.Item>
                            </Col>
                        </Row>
                    </Form>
                </Card>

                <Card title={t('agent.settingsTitle')}>
                    <AgentForm
                        value={formValues}
                        onChange={(newValues) => setFormValues(newValues)}
                    />
                </Card>
            </Modal>
        </Card>
    );
};

export default AgentList; 
