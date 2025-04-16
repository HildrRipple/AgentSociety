import { useEffect, useState, useRef } from "react";

import { Col, Row, message, Table, Button, Space, Popconfirm, Modal, Dropdown, Select } from 'antd';
import dayjs from "dayjs";
import { parseT } from "../../components/util";
import { useNavigate } from "react-router-dom";
import React from "react";
import { Experiment, experimentStatusMap } from "../../components/type";
import { ProColumns, ProDescriptions, ProTable } from "@ant-design/pro-components";
import { ActionType } from "@ant-design/pro-table";
import { EllipsisOutlined, ReloadOutlined } from "@ant-design/icons";
import { fetchCustom } from "../../components/fetch";
import { getAccessToken } from "../../components/Auth";

const Page = () => {
    const navigate = useNavigate(); // 获取导航函数
    const [detail, setDetail] = useState<Experiment | null>(null);
    const [logVisible, setLogVisible] = useState(false);
    const [logContent, setLogContent] = useState('');
    const [logLoading, setLogLoading] = useState(false);
    const actionRef = useRef<ActionType>();
    const [currentExpId, setCurrentExpId] = useState<string>('');
    const [refreshInterval, setRefreshInterval] = useState<number>(0);
    const refreshTimerRef = useRef<NodeJS.Timeout | null>(null);

    // 清理定时器
    const clearRefreshTimer = () => {
        if (refreshTimerRef.current) {
            clearInterval(refreshTimerRef.current);
            refreshTimerRef.current = null;
        }
    };

    // 设置新的定时器
    const setupRefreshTimer = (interval: number, expId: string) => {
        clearRefreshTimer();
        if (interval > 0) {
            refreshTimerRef.current = setInterval(() => {
                fetchLog(expId);
            }, interval * 1000);
        }
    };

    // 组件卸载时清理定时器
    useEffect(() => {
        return () => clearRefreshTimer();
    }, []);

    const fetchLog = async (experimentId: string) => {
        // 不清空现有内容，只显示loading状态
        setLogLoading(true);
        const oldContent = logContent;  // 保存现有内容
        try {
            const res = await fetchCustom(`/api/run-experiments/${experimentId}/log`);
            if (res.ok) {
                const log = await res.text();
                setLogContent(log.replace(/\\n/g, '\n'));
            } else {
                throw new Error(await res.text());
            }
        } catch (err) {
            message.error('Failed to fetch log: ' + err);
            clearRefreshTimer(); // 发生错误时停止刷新
            setLogContent(oldContent);  // 发生错误时恢复原有内容
        } finally {
            setLogLoading(false);
        }
    };

    const columns: ProColumns<Experiment>[] = [
        { title: 'ID', dataIndex: 'id', width: '10%' },
        { title: 'Name', dataIndex: 'name', width: '5%' },
        { title: 'Num Day', dataIndex: 'num_day', width: '5%', search: false },
        {
            title: 'Status',
            dataIndex: 'status',
            width: '5%',
            valueEnum: experimentStatusMap,
        },
        { title: 'Current Day', dataIndex: 'cur_day', width: '5%', search: false },
        { title: 'Current Time', dataIndex: 'cur_t', width: '5%', render: (t: number) => parseT(t), search: false },
        { title: 'Input Tokens', dataIndex: 'input_tokens', width: '5%', search: false },
        { title: 'Output Tokens', dataIndex: 'output_tokens', width: '5%', search: false },
        {
            title: 'Created At',
            dataIndex: 'created_at',
            width: '5%',
            valueType: "dateTime",
            search: false
        },
        {
            title: 'Updated At',
            dataIndex: 'updated_at',
            width: '5%',
            valueType: "dateTime",
            search: false,
        },
        {
            title: 'Action',
            width: '5%',
            search: false,
            render: (_, record) => {
                // copy record to avoid reference change
                record = { ...record };
                return <Space>
                    <Button
                        type="primary"
                        onClick={() => navigate(`/exp/${record.id}`)}
                        disabled={record.status === 0}
                    >Goto</Button>
                    {record.status === 1 && (  // Add Stop button for running experiments
                        <Popconfirm
                            title="Are you sure to stop this experiment?"
                            onConfirm={async () => {
                                try {
                                    const res = await fetchCustom(`/api/run-experiments/${record.id}`, {
                                        method: 'DELETE',
                                    });
                                    if (res.ok) {
                                        message.success('Stop experiment successfully');
                                        actionRef.current?.reload();
                                    } else {
                                        const errMessage = await res.text();
                                        throw new Error(errMessage);
                                    }
                                } catch (err) {
                                    message.error('Failed to stop experiment: ' + err);
                                }
                            }}
                        >
                            <Button danger>Stop</Button>
                        </Popconfirm>
                    )}
                    <Dropdown
                        menu={{
                            items: [
                                {
                                    key: 'detail',
                                    label: 'Detail',
                                    onClick: () => setDetail(record)
                                },
                                {
                                    key: 'log',
                                    label: 'View Log',
                                    onClick: () => {
                                        setLogVisible(true);
                                        setCurrentExpId(record.id);
                                        fetchLog(record.id);
                                    }
                                },
                                {
                                    key: 'export',
                                    label: 'Export',
                                    onClick: () => {
                                        const token = getAccessToken();
                                        if (!token) {
                                            message.error('No token found, please login');
                                            return;
                                        }
                                        const authorization = `Bearer ${token}`;
                                        const url = `/api/experiments/${record.id}/export`
                                        // use form post to download the file
                                        const form = document.createElement('form');
                                        // TODO: add authorization
                                        form.action = url;
                                        form.method = 'POST';
                                        form.target = '_blank';
                                        form.innerHTML = '<input type="hidden" name="authorization" value="' + authorization + '">';
                                        document.body.appendChild(form);
                                        form.submit();
                                        document.body.removeChild(form);
                                    }
                                },
                                {
                                    key: 'delete',
                                    label: (
                                        <Popconfirm
                                            title="Are you sure to delete this experiment?"
                                            onConfirm={async () => {
                                                try {
                                                    const res = await fetchCustom(`/api/experiments/${record.id}`, {
                                                        method: 'DELETE',
                                                    })
                                                    if (res.ok) {
                                                        message.success('Delete experiment successfully');
                                                        actionRef.current?.reload();
                                                    } else {
                                                        // Read the error message as text
                                                        const errMessage = await res.text();
                                                        throw new Error(errMessage);
                                                    }
                                                } catch (err) {
                                                    message.error('Failed to delete experiment: ' + err);
                                                }
                                            }}
                                        >
                                            <span style={{ color: '#ff4d4f' }}>Delete</span>
                                        </Popconfirm>
                                    )
                                }
                            ]
                        }}
                    >
                        <Button icon={<EllipsisOutlined />} />
                    </Dropdown>
                </Space>
            },
        },
    ];

    return (
        <>
            <Row>
                <Col span={24}>
                    <ProTable<Experiment>
                        actionRef={actionRef}
                        columns={columns}
                        request={async (params) => {
                            try {
                                const res = await fetchCustom('/api/experiments')
                                let data = await res.json()
                                data = data.data;
                                if (params.name !== undefined && params.name !== '') {
                                    console.log('params.name:', params.name)
                                    data = data.filter((d: Experiment) => d.name.includes(params.name))
                                }
                                if (params.id !== undefined && params.id !== '') {
                                    data = data.filter((d: Experiment) => d.id === params.id)
                                }
                                if (params.status !== undefined) {
                                    data = data.filter((d: Experiment) => d.status == params.status)
                                }
                                return { data, success: true };
                            } catch (err) {
                                console.error('Failed to fetch experiments:', err)
                                return { data: [], success: false }
                            }
                        }}
                        rowKey="id"
                        columnEmptyText="-"
                    />
                </Col>
            </Row>
            <Modal
                title="Experiment Detail"
                width="60vw"
                open={detail !== null}
                onCancel={() => setDetail(null)}
                footer={null}
            >
                <ProDescriptions<Experiment>
                    column={2}
                    title={detail?.name}
                    request={async () => {
                        return {
                            success: true,
                            data: detail,
                        };
                    }}
                    columns={[
                        { title: 'ID', dataIndex: 'id' },
                        { title: 'Name', dataIndex: 'name' },
                        { title: 'Created At', dataIndex: 'created_at', valueType: 'dateTime' },
                        { title: 'Updated At', dataIndex: 'updated_at', valueType: 'dateTime' },
                        { title: 'Num Day', dataIndex: 'num_day' },
                        { title: 'Status', dataIndex: 'status', valueEnum: experimentStatusMap },
                        { title: 'Current Day', dataIndex: 'cur_day' },
                        { title: 'Current Time', dataIndex: 'cur_t', render: (t: number) => parseT(t) },
                        { title: 'Config', dataIndex: 'config', span: 2, valueType: 'jsonCode' },
                        { title: 'Error', dataIndex: 'error', span: 2, valueType: 'code' },
                    ]}
                />
            </Modal>
            <Modal
                title="Experiment Log"
                width="80vw"
                open={logVisible}
                onCancel={() => {
                    setLogVisible(false);
                    setLogContent('');
                    setRefreshInterval(0);
                    clearRefreshTimer();
                }}
                footer={null}
            >
                <div style={{ marginBottom: '16px', display: 'flex', gap: '8px', alignItems: 'center' }}>
                    <Button
                        icon={<ReloadOutlined />}
                        onClick={() => fetchLog(currentExpId)}
                        loading={logLoading}
                    >
                        Refresh
                    </Button>
                    <Select
                        value={refreshInterval}
                        onChange={(value) => {
                            setRefreshInterval(value);
                            setupRefreshTimer(value, currentExpId);
                        }}
                        style={{ width: 200 }}
                        options={[
                            { value: 0, label: 'Manual refresh' },
                            { value: 1, label: 'Every 1 second' },
                            { value: 5, label: 'Every 5 seconds' },
                            { value: 10, label: 'Every 10 seconds' },
                            { value: 30, label: 'Every 30 seconds' },
                        ]}
                    />
                    {logLoading && <span style={{ color: '#1890ff' }}>Refreshing...</span>}
                </div>
                <pre style={{
                    maxHeight: '70vh',
                    overflow: 'auto',
                    padding: '12px',
                    backgroundColor: '#f5f5f5',
                    borderRadius: '4px'
                }}>
                    {logContent}
                </pre>
            </Modal>
        </>
    );
}

export default Page;
