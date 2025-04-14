import React, { useState, useEffect } from 'react';
import { Card, Button, Select, Space, Typography, Divider, message, Row, Col, Spin, Form, Input } from 'antd';
import { useNavigate } from 'react-router-dom';
import { ExperimentOutlined, ApiOutlined, TeamOutlined, GlobalOutlined, RocketOutlined, NodeIndexOutlined } from '@ant-design/icons';
import { ConfigItem } from '../../services/storageService';
import { fetchCustom } from '../../components/fetch';

const { Text } = Typography;
const { Option } = Select;

// Add these interfaces at the top of the file
interface LLMConfig {
    provider?: string;
    model?: string;
    api_key?: string;
    base_url?: string;
}

interface WorkflowConfig extends ConfigItem {
    config: {
        llm?: LLMConfig;
        [key: string]: any;
    }
}

const CreateExperiment: React.FC = () => {
    // State declarations
    const [llms, setLLMs] = useState<ConfigItem[]>([]);
    const [agents, setAgents] = useState<ConfigItem[]>([]);
    const [workflows, setWorkflows] = useState<ConfigItem[]>([]);
    const [maps, setMaps] = useState<ConfigItem[]>([]);
    const [loading, setLoading] = useState(false);
    const [selectedLLM, setSelectedLLM] = useState<string>('');
    const [selectedAgent, setSelectedAgent] = useState<string>('');
    const [selectedWorkflow, setSelectedWorkflow] = useState<string>('');
    const [selectedMap, setSelectedMap] = useState<string>('');
    const [experimentName, setExperimentName] = useState<string>('');
    const [experimentRunning, setExperimentRunning] = useState(false);
    const [experimentId, setExperimentId] = useState<string | null>(null);
    const [statusCheckInterval, setStatusCheckInterval] = useState<NodeJS.Timeout | null>(null);
    const [experimentStatus, setExperimentStatus] = useState<string | null>(null);
    const navigate = useNavigate();
    const [form] = Form.useForm();

    // Load all configurations
    useEffect(() => {
        const loadConfigurations = async () => {
            setLoading(true);
            try {
                // Load all configurations
                const llmConfigsRes = await fetchCustom('/api/llm-configs');
                if (!llmConfigsRes.ok) {
                    throw new Error('Failed to fetch LLM configurations');
                }
                const llmConfigs = (await llmConfigsRes.json()).data;
                const agtsRes = await fetchCustom('/api/agent-configs');
                if (!agtsRes.ok) {
                    throw new Error('Failed to fetch agent configurations');
                }
                const agts = (await agtsRes.json()).data;
                const wkfsRes = await fetchCustom('/api/workflow-configs');
                if (!wkfsRes.ok) {
                    throw new Error('Failed to fetch workflow configurations');
                }
                const wkfs = (await wkfsRes.json()).data;
                const mpsRes = await fetchCustom('/api/map-configs');
                if (!mpsRes.ok) {
                    throw new Error('Failed to fetch map configurations');
                }
                const mps = (await mpsRes.json()).data;

                setLLMs(llmConfigs);
                setAgents(agts);
                setWorkflows(wkfs);
                setMaps(mps);

                // Set defaults if available
                if (llmConfigs.length > 0) setSelectedLLM(llmConfigs[0].id);
                if (agts.length > 0) setSelectedAgent(agts[0].id);
                if (wkfs.length > 0) setSelectedWorkflow(wkfs[0].id);
                if (mps.length > 0) setSelectedMap(mps[0].id);
            } catch (error) {
                message.error('Failed to load configurations');
                console.error(error);
            } finally {
                setLoading(false);
            }
        };

        loadConfigurations();
    }, []);

    // Clean up interval timer
    useEffect(() => {
        return () => {
            if (statusCheckInterval) {
                clearInterval(statusCheckInterval);
            }
        };
    }, [statusCheckInterval]);

    // Handle navigation to create new configuration pages
    const handleCreateNew = (type: 'llm' | 'agent' | 'workflow' | 'map') => {
        switch (type) {
            case 'llm':
                navigate('/llms');
                break;
            case 'agent':
                navigate('/agents');
                break;
            case 'workflow':
                navigate('/workflows');
                break;
            case 'map':
                navigate('/maps');
                break;
        }
    };

    // Render option content with name and description
    const renderOptionContent = (item: ConfigItem) => (
        <div>
            <div>{item.name}</div>
            {item.description && <Text type="secondary">{item.description}</Text>}
        </div>
    );

    // Handle form submission to start experiment
    const handleSubmit = async () => {
        setLoading(true);
        try {
            // Validate form
            await form.validateFields();

            // Build configuration from selected components
            const llm = llms.find(llm => llm.id === selectedLLM);
            if (!llm) {
                throw new Error('LLM not found');
            }
            const map = maps.find(map => map.id === selectedMap);
            if (!map) {
                throw new Error('Map not found');
            }
            const agent = agents.find(agent => agent.id === selectedAgent);
            if (!agent) {
                throw new Error('Agent not found');
            }
            const workflow = workflows.find(workflow => workflow.id === selectedWorkflow);
            if (!workflow) {
                throw new Error('Workflow not found');
            }
            const config = {
                exp_name: experimentName,
                llm: {
                    tenant_id: llm.tenant_id,
                    id: llm.id,
                },
                map: {
                    tenant_id: map.tenant_id,
                    id: map.id,
                },
                agents: {
                    tenant_id: agent.tenant_id,
                    id: agent.id,
                },
                workflow: {
                    tenant_id: workflow.tenant_id,
                    id: workflow.id,
                },
            }

            // Send request to start experiment
            const response = await fetchCustom('/api/run-experiments', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(config),
            });

            if (!response.ok) {
                throw new Error(await response.text());
            }

            const data = await response.json();
            const newExperimentId = data.data.id;

            setExperimentId(newExperimentId);
            setExperimentRunning(true);
            message.success(`Experiment started successfully! ExperimentId: ${newExperimentId}`);

            // Start polling for pod status
            const interval = setInterval(async () => {
                try {
                    const statusResponse = await fetchCustom(`/api/run-experiments/${newExperimentId}/status`);
                    if (!statusResponse.ok) {
                        throw new Error('Failed to fetch experiment status');
                    }
                    const statusData = await statusResponse.json();
                    const status = statusData.data;
                    if (status !== 'Running') {
                        setExperimentStatus(status);
                    }

                    if (status === 'Running') {
                        try {
                            // Pod is running, now check experiment initialization
                            const experimentResponse = await fetchCustom(`/api/experiments/${newExperimentId}`);
                            
                            if (experimentResponse.status === 404) {
                                // 404 is expected during initialization, continue waiting
                                setExperimentStatus('Initializing experiment data...');
                                return;
                            }
                            
                            if (!experimentResponse.ok) {
                                throw new Error('Failed to fetch experiment details');
                            }

                            const experimentData = await experimentResponse.json();
                            const experiment = experimentData.data;

                            // Check if experiment is fully initialized
                            if (experiment.status === 1) {
                                clearInterval(interval);
                                message.success('Experiment initialized successfully!');
                                navigate('/console');
                            } else {
                                setExperimentStatus('Initializing experiment data...');
                            }
                        } catch (error) {
                            if (error.response?.status === 404) {
                                // 404 error is expected during initialization, continue waiting
                                setExperimentStatus('Initializing experiment data...');
                                return;
                            }
                            throw error;
                        }
                    } else if (status === 'Failed' || status === 'Error') {
                        clearInterval(interval);
                        message.error('Experiment failed to start');
                        setExperimentRunning(false);
                    }
                } catch (error) {
                    // Only handle non-404 errors as failures
                    if (error.response?.status !== 404) {
                        console.error('Error checking experiment status:', error);
                        message.error('Failed to check experiment status');
                        clearInterval(interval);
                        setExperimentRunning(false);
                    }
                }
            }, 2000);

            setStatusCheckInterval(interval);
        } catch (error) {
            message.error(`Failed to start experiment: ${error.message}`, 3);
            console.error(error);
            setExperimentRunning(false);
        } finally {
            setLoading(false);
        }
    };

    return (
        <Form
            form={form}
            layout="vertical"
            onFinish={handleSubmit}
            initialValues={{
                experimentName: '',
            }}
        >
            <Card title="Create New Experiment" extra={
                <Button
                    type="primary"
                    htmlType="submit"
                    loading={loading}
                    disabled={experimentRunning}
                >
                    Start Experiment
                </Button>
            }>
                <Form.Item
                    name="experimentName"
                    label="Experiment Name"
                    rules={[{ required: true, message: 'Please enter an experiment name' }]}
                >
                    <Input
                        placeholder="Enter experiment name"
                        onChange={(e) => setExperimentName(e.target.value)}
                        disabled={experimentRunning}
                    />
                </Form.Item>

                <Divider orientation="left">Configuration Components</Divider>

                <Row gutter={[16, 16]}>
                    <Col span={12}>
                        <Card
                            title={<Space><ApiOutlined /> LLM</Space>}
                            extra={<Button type="link" onClick={() => handleCreateNew('llm')}>Create New</Button>}
                        >
                            <Space direction="vertical" style={{ width: '100%' }}>
                                <Text>Select a LLM configuration:</Text>
                                <Form.Item
                                    name="llm"
                                    rules={[{ required: true, message: 'Please select a LLM' }]}
                                    initialValue={selectedLLM}
                                >
                                    <Select
                                        placeholder="Select LLM"
                                        style={{ width: '100%' }}
                                        loading={loading}
                                        value={selectedLLM || undefined}
                                        onChange={setSelectedLLM}
                                        optionLabelProp="label"
                                        disabled={experimentRunning}
                                    >
                                        {llms.map(llm => (
                                            <Option key={llm.id} value={llm.id} label={llm.name}>
                                                {renderOptionContent(llm)}
                                            </Option>
                                        ))}
                                    </Select>
                                </Form.Item>
                            </Space>
                        </Card>
                    </Col>

                    <Col span={12}>
                        <Card
                            title={<Space><GlobalOutlined /> Map</Space>}
                            extra={<Button type="link" onClick={() => handleCreateNew('map')}>Create New</Button>}
                        >
                            <Space direction="vertical" style={{ width: '100%' }}>
                                <Text>Select a map:</Text>
                                <Form.Item
                                    name="map"
                                    rules={[{ required: true, message: 'Please select a map' }]}
                                    initialValue={selectedMap}
                                >
                                    <Select
                                        placeholder="Select map"
                                        style={{ width: '100%' }}
                                        loading={loading}
                                        value={selectedMap || undefined}
                                        onChange={setSelectedMap}
                                        optionLabelProp="label"
                                        disabled={experimentRunning}
                                    >
                                        {maps.map(map => (
                                            <Option key={map.id} value={map.id} label={map.name}>
                                                {renderOptionContent(map)}
                                            </Option>
                                        ))}
                                    </Select>
                                </Form.Item>
                            </Space>
                        </Card>
                    </Col>

                    <Col span={12}>
                        <Card
                            title={<Space><TeamOutlined /> Agent</Space>}
                            extra={<Button type="link" onClick={() => handleCreateNew('agent')}>Create New</Button>}
                        >
                            <Space direction="vertical" style={{ width: '100%' }}>
                                <Text>Select an agent configuration:</Text>
                                <Form.Item
                                    name="agent"
                                    rules={[{ required: true, message: 'Please select an agent configuration' }]}
                                    initialValue={selectedAgent}
                                >
                                    <Select
                                        placeholder="Select agent"
                                        style={{ width: '100%' }}
                                        loading={loading}
                                        value={selectedAgent || undefined}
                                        onChange={setSelectedAgent}
                                        optionLabelProp="label"
                                        disabled={experimentRunning}
                                    >
                                        {agents.map(agent => (
                                            <Option key={agent.id} value={agent.id} label={agent.name}>
                                                {renderOptionContent(agent)}
                                            </Option>
                                        ))}
                                    </Select>
                                </Form.Item>
                            </Space>
                        </Card>
                    </Col>

                    <Col span={12}>
                        <Card
                            title={<Space><NodeIndexOutlined /> Workflow</Space>}
                            extra={<Button type="link" onClick={() => handleCreateNew('workflow')}>Create New</Button>}
                        >
                            <Space direction="vertical" style={{ width: '100%' }}>
                                <Text>Select a workflow:</Text>
                                <Form.Item
                                    name="workflow"
                                    rules={[{ required: true, message: 'Please select a workflow' }]}
                                    initialValue={selectedWorkflow}
                                >
                                    <Select
                                        placeholder="Select workflow"
                                        style={{ width: '100%' }}
                                        loading={loading}
                                        value={selectedWorkflow || undefined}
                                        onChange={setSelectedWorkflow}
                                        optionLabelProp="label"
                                        disabled={experimentRunning}
                                    >
                                        {workflows.map(workflow => (
                                            <Option key={workflow.id} value={workflow.id} label={workflow.name}>
                                                {renderOptionContent(workflow)}
                                            </Option>
                                        ))}
                                    </Select>
                                </Form.Item>
                            </Space>
                        </Card>
                    </Col>
                </Row>

                <Divider />

                {experimentRunning && (
                    <div style={{ textAlign: 'center', marginTop: 16 }}>
                        <Spin size="large" />
                        <div style={{ marginTop: 16 }}>
                            <Text>
                                Experiment Status: {' '}
                                <Text strong type={
                                    experimentStatus === 'Running' ? 'warning' :
                                    experimentStatus?.includes('Initializing') ? 'warning' :
                                    experimentStatus === 'Failed' || experimentStatus === 'Error' ? 'danger' :
                                    'warning'
                                }>
                                    {experimentStatus === 'Running' ? 'Starting Services...' :
                                     experimentStatus === 'Failed' ? 'Start-up Failed' :
                                     experimentStatus === 'Error' ? 'Error Occurred' :
                                     experimentStatus || 'Preparing Environment...'}
                                </Text>
                            </Text>
                        </div>
                        <div style={{ marginTop: 8 }}>
                            <Text type="secondary">
                                {experimentStatus === 'Running' ? 'Services started, initializing experiment data...' :
                                 experimentStatus?.includes('Initializing') ? 'Setting up experiment environment...' :
                                 experimentStatus === 'Failed' || experimentStatus === 'Error' ? 'Please check your configuration and try again' :
                                 'Starting experiment services. This may take a few minutes...'}
                            </Text>
                        </div>
                    </div>
                )}
            </Card>
        </Form>
    );
};

export default CreateExperiment; 