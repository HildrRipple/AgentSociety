import { useEffect, useState } from "react";
import { Card, Row, Col, Button, message, Space, Modal, InputNumber } from "antd";
import { ProTable, ProColumns } from "@ant-design/pro-components";
import { ActionType } from "@ant-design/pro-table";
import { useRef } from "react";
import { useTranslation } from "react-i18next";
import { fetchCustom } from "../../components/fetch";

interface Account {
    id: string;
    balance: number;
    created_at: string;
    updated_at: string;
}

interface Bill {
    id: string;
    related_exp_id: string;
    item: string;
    amount: number;
    unit_price: number;
    quantity: number;
    description: string;
    created_at: string;
}

const Page = () => {
    const { t } = useTranslation();
    const [account, setAccount] = useState<Account | null>(null);
    const [rechargeVisible, setRechargeVisible] = useState(false);
    const [rechargeAmount, setRechargeAmount] = useState<number>(100);
    const actionRef = useRef<ActionType>();

    const fetchAccount = async () => {
        try {
            const res = await fetchCustom('/api/account');
            if (res.ok) {
                const data = await res.json();
                setAccount(data.data);
            } else {
                throw new Error(await res.text());
            }
        } catch (err) {
            message.error('Failed to fetch account: ' + err);
        }
    };

    useEffect(() => {
        fetchAccount();
    }, []);

    const handleRecharge = async () => {
        try {
            const res = await fetchCustom('/api/bill/recharge', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ amount: rechargeAmount }),
            });
            if (res.ok) {
                message.success('Recharge successful');
                setRechargeVisible(false);
                fetchAccount();
                actionRef.current?.reload();
            } else {
                throw new Error(await res.text());
            }
        } catch (err) {
            message.error('Failed to recharge: ' + err);
        }
    };

    const columns: ProColumns<Bill>[] = [
        {
            title: t('bill.table.id'),
            dataIndex: 'id',
            width: '10%',
            valueType: 'text'
        },
        {
            title: t('bill.table.related_exp_id'),
            dataIndex: 'related_exp_id',
            width: '20%',
            valueType: 'text',
        },
        {
            title: t('bill.table.item'),
            dataIndex: 'item',
            width: '20%',
            valueEnum: {
                'llm_input_token': t('bill.table.llm_input_token'),
                'llm_output_token': t('bill.table.llm_output_token'),
                'run_time': t('bill.table.run_time'),
                'recharge': t('bill.table.recharge'),
            },
        },
        {
            title: t('bill.table.amount'),
            dataIndex: 'amount',
            width: '10%',
            valueType: 'money',
            render: (_, record) => record.amount,
            search: false,
        },
        {
            title: t('bill.table.unit_price'),
            dataIndex: 'unit_price',
            width: '10%',
            valueType: 'money',
            render: (_, record) => record.unit_price,
            search: false,
        },
        {
            title: t('bill.table.quantity'),
            dataIndex: 'quantity',
            width: '10%',
            search: false,
        },
        {
            title: t('bill.table.description'),
            dataIndex: 'description',
            width: '10%',
            valueType: 'text',
            search: false,
        },
        {
            title: t('bill.table.createdAt'),
            dataIndex: 'created_at',
            width: '10%',
            valueType: 'dateTime',
            search: false,
        },
    ];

    return (
        <div style={{ margin: "16px" }}>
            <Row>
                <Col span={24}>
                    <Card>
                        <Row justify="space-between" align="middle">
                            <Col>
                                <h2>{t('bill.balance')}: ￥{account?.balance ? Number(account.balance).toFixed(2) : '0.00'}</h2>
                            </Col>
                            <Col>
                                <Button type="primary" onClick={() => setRechargeVisible(true)}>
                                    {t('bill.recharge')}
                                </Button>
                            </Col>
                        </Row>
                    </Card>
                </Col>
            </Row>

            <Row style={{ marginTop: "16px" }}>
                <Col span={24}>
                    <ProTable<Bill>
                        headerTitle={t('bill.table.title')}
                        actionRef={actionRef}
                        columns={columns}
                        cardBordered
                        request={async (params) => {
                            try {
                                const queryParams = new URLSearchParams();
                                if (params.item) queryParams.append('item', params.item);
                                if (params.current) queryParams.append('skip', ((params.current - 1) * (params.pageSize || 10)).toString());
                                if (params.pageSize) queryParams.append('limit', params.pageSize.toString());

                                const res = await fetchCustom(`/api/bills?${queryParams.toString()}`);
                                const data = await res.json();
                                return {
                                    data: data.data,
                                    success: true,
                                    total: data.total,
                                };
                            } catch (err) {
                                message.error('Failed to fetch bills: ' + err);
                                return { data: [], success: false };
                            }
                        }}
                        rowKey="id"
                        search={{
                            labelWidth: 120,
                        }}
                        pagination={{
                            pageSize: 10,
                        }}
                    />
                </Col>
            </Row>

            <Modal
                title={t('bill.recharge')}
                open={rechargeVisible}
                onOk={handleRecharge}
                onCancel={() => setRechargeVisible(false)}
            >
                <Space direction="vertical" style={{ width: '100%' }}>
                    <InputNumber
                        min={0.01}
                        value={rechargeAmount}
                        onChange={(value) => setRechargeAmount(value || 0)}
                        style={{ width: '100%' }}
                        addonBefore="￥"
                    />
                </Space>
            </Modal>
        </div>
    );
};

export default Page;
