import React, { useState, useEffect } from 'react';
import { Form, Input, InputNumber, Select, Card, Button, Space, Radio, Upload, message } from 'antd';
import { PlusOutlined, UploadOutlined, ThunderboltOutlined, EyeOutlined } from '@ant-design/icons';
import { Spin, Table, Modal } from 'antd';
import { getAccessToken } from '../../components/Auth';

const { Option } = Select;

// Define profile interface
interface Profile {
    id: string;
    name: string;
    agent_type: string;
    count: number;
    created_at: string;
}

const ProfileGeneration: React.FC = () => {
    const [form] = Form.useForm();
    const [previewVisible, setPreviewVisible] = useState(false);
    const [previewLoading, setPreviewLoading] = useState(false);
    const [previewData, setPreviewData] = useState([]);
    const [previewColumns, setPreviewColumns] = useState([]);
    const [profilesData, setProfilesData] = useState<Profile[] | null>(null);
    const [profilesLoading, setProfilesLoading] = useState(false);
    const [generatingProfiles, setGeneratingProfiles] = useState(false);
    const [generatedData, setGeneratedData] = useState<Record<string, any>>({});
    const [generatingData, setGeneratingData] = useState(false);

    // Define distribution type options
    const distributionTypeOptions = [
        { label: 'Choice', value: 'choice' },
        { label: 'Uniform Integer', value: 'uniform_int' },
        { label: 'Uniform Float', value: 'uniform_float' },
        { label: 'Normal', value: 'normal' },
        { label: 'Constant', value: 'constant' },
    ];

    // Fetch profiles from API
    const fetchProfiles = async () => {
        try {
            setProfilesLoading(true);
            const response = await fetch('/api/agent-profiles');
            const data = await response.json();
            setProfilesData(data.data);
        } catch (error) {
            console.error('Failed to fetch profiles:', error);
            message.error('Failed to fetch agent profiles');
        } finally {
            setProfilesLoading(false);
        }
    };

    // Load profiles when component mounts
    useEffect(() => {
        fetchProfiles();
    }, []);

    // Handle profile preview
    const handleProfilePreview = async (profileId: string) => {
        try {
            setPreviewLoading(true);
            
            // Call the API to get profile data
            const response = await fetch(`/api/agent-profiles/${profileId}`);
            
            if (!response.ok) {
                throw new Error(`Failed to fetch profile: ${response.statusText}`);
            }
            
            const data = await response.json();
            
            if (data && data.data) {
                // Prepare data for table display
                const previewData = data.data.slice(0, 100); // Limit to first 100 records
                
                // Create columns for the table
                const firstRecord = previewData[0] || {};
                const columns = Object.keys(firstRecord).map(key => ({
                    title: key,
                    dataIndex: key,
                    key: key,
                }));
                
                setPreviewData(previewData);
                setPreviewColumns(columns);
                setPreviewVisible(true);
            } else {
                message.warning('No data available for preview');
            }
        } catch (error) {
            console.error('Failed to fetch profile preview:', error);
            message.error('Failed to fetch profile preview');
        } finally {
            setPreviewLoading(false);
        }
    };

    // Generate distribution data
    const handleGenerateDistribution = async () => {
        try {
            setGeneratingData(true);
            
            // Get form values
            const formValues = form.getFieldsValue();
            
            // Format the request payload
            const payload = {
                agent_type: formValues.agent_type,
                number: formValues.number,
                distributions: formValues.distributions || []
            };
            
            // Call the API to generate distribution data
            const response = await fetch('/api/agent-profiles/generate-data', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${getAccessToken()}`
                },
                body: JSON.stringify(payload)
            });
            
            if (!response.ok) {
                throw new Error(`Failed to generate distribution data: ${response.statusText}`);
            }
            
            const data = await response.json();
            
            if (data && data.data) {
                // Store the generated data
                setGeneratedData({
                    [`${formValues.agent_type}_0`]: data.data
                });
                message.success('Distribution data generated successfully');
            } else {
                message.warning('No distribution data was generated');
            }
        } catch (error) {
            console.error('Failed to generate distribution data:', error);
            message.error('Failed to generate distribution data');
        } finally {
            setGeneratingData(false);
        }
    };

    // Handle generate preview
    const handleGeneratePreview = () => {
        try {
            const formValues = form.getFieldsValue();
            const agentType = formValues.agent_type;
            
            // Check if we have generated data for this agent type
            const generatedKey = `${agentType}_0`;
            if (!generatedData[generatedKey]) {
                message.warning('Please generate distribution data first');
                return;
            }
            
            setGeneratingProfiles(true);
            
            // Use the already generated data
            const previewData = generatedData[generatedKey].slice(0, 100); // Limit to first 100 records
            
            // Create columns for the table
            const firstRecord = previewData[0] || {};
            const columns = Object.keys(firstRecord).map(key => ({
                title: key,
                dataIndex: key,
                key: key,
            }));
            
            setPreviewData(previewData);
            setPreviewColumns(columns);
            setPreviewVisible(true);
        } catch (error) {
            console.error('Failed to preview generated data:', error);
            message.error('Failed to preview generated data');
        } finally {
            setGeneratingProfiles(false);
        }
    };

    // Handle profile upload
    const handleUpload = async () => {
        try {
            const formValues = form.getFieldsValue();
            const agentType = formValues.agent_type;
            
            // Check if we have generated data for this agent type
            const generatedKey = `${agentType}_0`;
            if (!generatedData[generatedKey]) {
                message.warning('Please generate distribution data first');
                return;
            }
            
            // Prepare request payload
            const payload = {
                name: formValues.name || `${agentType.charAt(0).toUpperCase() + agentType.slice(1)} Profile ${new Date().toISOString().substring(0, 19)}`,
                description: `Generated ${agentType} profile with ${formValues.number} agents`,
                agent_type: agentType,
                data: generatedData[generatedKey]
            };
            
            // Call the API to save the profile
            const response = await fetch('/api/agent-profiles', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${getAccessToken()}`
                },
                body: JSON.stringify(payload)
            });
            
            if (!response.ok) {
                throw new Error(`Failed to upload profile: ${response.statusText}`);
            }
            
            const data = await response.json();
            message.success('Profile uploaded successfully');
            
            // Refresh profiles
            fetchProfiles();
        } catch (error) {
            console.error('Failed to upload profile:', error);
            message.error('Failed to upload profile');
        }
    };

    // Generate profiles (combined function for generate, preview, and upload)
    const handleGenerateProfiles = async () => {
        try {
            setGeneratingProfiles(true);
            
            // First generate the distribution data
            await handleGenerateDistribution();
            
            // Then upload the profile
            await handleUpload();
        } catch (error) {
            console.error('Failed to generate and upload profiles:', error);
            message.error('Failed to generate and upload profiles');
        } finally {
            setGeneratingProfiles(false);
        }
    };

    // Render distribution form based on type
    const renderDistributionForm = (type, basePath) => {
        switch (type) {
            case 'choice':
                return (
                    <Form.Item
                        name={[...basePath, 'params', 'choices']}
                        label="Choices (comma separated)"
                        rules={[{ required: true, message: 'Please enter choices' }]}
                    >
                        <Input placeholder="e.g. red,green,blue" />
                    </Form.Item>
                );
            case 'uniform_int':
                return (
                    <>
                        <Form.Item
                            name={[...basePath, 'params', 'low']}
                            label="Minimum Value"
                            rules={[{ required: true, message: 'Please enter minimum value' }]}
                            initialValue={0}
                        >
                            <InputNumber style={{ width: '100%' }} />
                        </Form.Item>
                        <Form.Item
                            name={[...basePath, 'params', 'high']}
                            label="Maximum Value"
                            rules={[{ required: true, message: 'Please enter maximum value' }]}
                            initialValue={10}
                        >
                            <InputNumber style={{ width: '100%' }} />
                        </Form.Item>
                    </>
                );
            case 'uniform_float':
                return (
                    <>
                        <Form.Item
                            name={[...basePath, 'params', 'low']}
                            label="Minimum Value"
                            rules={[{ required: true, message: 'Please enter minimum value' }]}
                            initialValue={0}
                        >
                            <InputNumber style={{ width: '100%' }} step={0.1} />
                        </Form.Item>
                        <Form.Item
                            name={[...basePath, 'params', 'high']}
                            label="Maximum Value"
                            rules={[{ required: true, message: 'Please enter maximum value' }]}
                            initialValue={1}
                        >
                            <InputNumber style={{ width: '100%' }} step={0.1} />
                        </Form.Item>
                    </>
                );
            case 'normal':
                return (
                    <>
                        <Form.Item
                            name={[...basePath, 'params', 'loc']}
                            label="Mean"
                            rules={[{ required: true, message: 'Please enter mean value' }]}
                            initialValue={0}
                        >
                            <InputNumber style={{ width: '100%' }} step={0.1} />
                        </Form.Item>
                        <Form.Item
                            name={[...basePath, 'params', 'scale']}
                            label="Standard Deviation"
                            rules={[{ required: true, message: 'Please enter standard deviation' }]}
                            initialValue={1}
                        >
                            <InputNumber style={{ width: '100%' }} step={0.1} min={0} />
                        </Form.Item>
                    </>
                );
            case 'constant':
                return (
                    <Form.Item
                        name={[...basePath, 'params', 'val']}
                        label="Value"
                        rules={[{ required: true, message: 'Please enter constant value' }]}
                        initialValue=""
                    >
                        <Input />
                    </Form.Item>
                );
            default:
                return null;
        }
    };

    return (
        <div style={{ padding: '24px' }}>
            <Card title="Generate Agent Profiles">
                <Form
                    form={form}
                    layout="vertical"
                    initialValues={{
                        agent_type: 'citizen',
                        number: 100
                    }}
                >
                    <Form.Item
                        name="name"
                        label="Profile Name"
                        rules={[{ required: true, message: 'Please enter a name for this profile' }]}
                    >
                        <Input placeholder="Enter profile name" />
                    </Form.Item>

                    <Form.Item
                        name="agent_type"
                        label="Agent Type"
                        rules={[{ required: true, message: 'Please select agent type' }]}
                    >
                        <Select>
                            <Option value="citizen">Citizen</Option>
                            <Option value="firm">Firm</Option>
                            <Option value="government">Government</Option>
                            <Option value="bank">Bank</Option>
                        </Select>
                    </Form.Item>

                    <Form.Item
                        name="number"
                        label="Number of Agents"
                        rules={[{ required: true, message: 'Please enter number of agents' }]}
                    >
                        <InputNumber min={1} style={{ width: '100%' }} />
                    </Form.Item>

                    <Card title="Attribute Distributions" bordered={false}>
                        <Form.List name="distributions" initialValue={[{ name: '', distribution: { type: 'constant', params: { val: '' } } }]}>
                            {(fields, { add, remove }) => (
                                <>
                                    {fields.map(({ key, name, ...restField }) => (
                                        <Card
                                            key={key}
                                            title={`Distribution ${name + 1}`}
                                            style={{ marginBottom: 16 }}
                                            size="small"
                                            extra={
                                                <Button
                                                    icon={<PlusOutlined />}
                                                    onClick={() => remove(name)}
                                                    danger
                                                    size="small"
                                                >
                                                    Remove
                                                </Button>
                                            }
                                        >
                                            <Form.Item
                                                {...restField}
                                                name={[name, 'name']}
                                                label="Attribute Name"
                                                rules={[{ required: true, message: 'Please enter attribute name' }]}
                                            >
                                                <Input placeholder="e.g. age, income, education" />
                                            </Form.Item>

                                            <Form.Item
                                                {...restField}
                                                name={[name, 'distribution', 'type']}
                                                label="Distribution Type"
                                                rules={[{ required: true, message: 'Please select distribution type' }]}
                                                initialValue="constant"
                                            >
                                                <Select
                                                    options={distributionTypeOptions}
                                                    onChange={(value) => {
                                                        // Reset params when distribution type changes
                                                        const currentValues = form.getFieldsValue();
                                                        let defaultParams = {};
                                                        
                                                        switch (value) {
                                                            case 'choice':
                                                                defaultParams = { choices: '' };
                                                                break;
                                                            case 'uniform_int':
                                                            case 'uniform_float':
                                                                defaultParams = { low: 0, high: 10 };
                                                                break;
                                                            case 'normal':
                                                                defaultParams = { loc: 0, scale: 1 };
                                                                break;
                                                            case 'constant':
                                                                defaultParams = { val: '' };
                                                                break;
                                                        }
                                                        
                                                        currentValues.distributions[name].distribution.params = defaultParams;
                                                        form.setFieldsValue(currentValues);
                                                    }}
                                                />
                                            </Form.Item>

                                            {renderDistributionForm(
                                                form.getFieldValue(['distributions', name, 'distribution', 'type']),
                                                ['distributions', name, 'distribution']
                                            )}
                                        </Card>
                                    ))}
                                    <Form.Item>
                                        <Button
                                            type="dashed"
                                            onClick={() => add({ name: '', distribution: { type: 'constant', params: { val: '' } } })}
                                            block
                                            icon={<PlusOutlined />}
                                        >
                                            Add Distribution
                                        </Button>
                                    </Form.Item>
                                </>
                            )}
                        </Form.List>
                    </Card>

                    <Form.Item>
                        <Space>
                            <Button
                                type="primary"
                                icon={<ThunderboltOutlined />}
                                onClick={handleGenerateDistribution}
                                loading={generatingData}
                            >
                                Generate Data
                            </Button>
                            <Button
                                icon={<EyeOutlined />}
                                onClick={handleGeneratePreview}
                                disabled={!Object.keys(generatedData).length}
                            >
                                Preview
                            </Button>
                            <Button
                                icon={<UploadOutlined />}
                                onClick={handleUpload}
                                disabled={!Object.keys(generatedData).length}
                            >
                                Upload Profile
                            </Button>
                            <Button
                                type="primary"
                                icon={<ThunderboltOutlined />}
                                onClick={handleGenerateProfiles}
                                loading={generatingProfiles}
                            >
                                Generate & Upload
                            </Button>
                        </Space>
                    </Form.Item>
                </Form>
            </Card>

            {/* Preview Modal */}
            <Modal
                title="Profile Preview"
                open={previewVisible}
                onCancel={() => setPreviewVisible(false)}
                width={1000}
                footer={[
                    <Button key="close" onClick={() => setPreviewVisible(false)}>
                        Close
                    </Button>
                ]}
            >
                {previewLoading ? (
                    <div style={{ textAlign: 'center', padding: '20px' }}>
                        <Spin size="large" />
                        <div style={{ marginTop: '10px' }}>Loading preview data...</div>
                    </div>
                ) : previewData.length > 0 ? (
                    <Table 
                        dataSource={previewData.map((item, index) => ({ ...item, key: index }))} 
                        columns={previewColumns} 
                        scroll={{ x: 'max-content', y: 400 }}
                        pagination={{ pageSize: 10 }}
                    />
                ) : (
                    <div>No preview data available</div>
                )}
            </Modal>
        </div>
    );
};

export default ProfileGeneration; 