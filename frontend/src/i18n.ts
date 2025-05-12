import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';

i18n
    // detect user language
    // learn more: https://github.com/i18next/i18next-browser-languageDetector
    .use(LanguageDetector)
    // pass the i18n instance to react-i18next.
    .use(initReactI18next)
    // init i18next
    // for all options read: https://www.i18next.com/overview/configuration-options
    .init({
        debug: true,
        fallbackLng: 'zh',
        interpolation: {
            escapeValue: false, // not needed for react as it escapes by default
        },
        resources: {
            en: {
                translation: {
                    menu: {
                        experiments: 'Experiments',
                        survey: 'Survey',
                        documentation: 'Documentation',
                        github: 'GitHub',
                        mlflow: 'MLFlow',
                        llmConfigs: 'LLM Configs',
                        maps: 'Maps',
                        agents: 'Agents',
                        agentConfigs: 'Agent Configs',
                        agentTemplates: 'Agent Templates',
                        workflows: 'Workflows',
                        create: 'Create',
                        login: 'Login',
                        logout: 'Logout',
                        account: 'Account',
                        demo: 'Demo',
                        demoUser: 'Demo User',
                        bill: 'Billing',
                        profiles: 'Profiles',
                        profileGeneration: 'Generate Profiles',
                    },
                    home: {
                        whatsNew: "What's New",
                        releaseNotes: "Release v1.3. Click here to view the release notes.",
                        getStarted: "Get Started",
                        stars: "Stars",
                        mainDescription: "Create your society with <strong><em>Large Model-driven Social Human Agent</em></strong> and <strong><em>Realistic Urban Social Environment</em></strong>"
                    },
                    survey: {
                        createSurvey: "Create Survey",
                        editSurvey: "Edit Survey",
                        surveyName: "Survey Name",
                        surveyJsonData: "Survey JSON Data",
                        onlineVisualEditor: "Online Visual Editor",
                        submit: "Submit",
                        delete: "Delete",
                        deleteConfirm: "Are you sure to delete this survey?",
                        createSuccess: "Create success!",
                        updateSuccess: "Update success!",
                        deleteSuccess: "Delete success!",
                        createFailed: "Create failed:",
                        updateFailed: "Update failed:",
                        deleteFailed: "Delete failed:",
                        fetchFailed: "Fetch surveys failed:",
                        invalidJson: "Invalid JSON format",
                        pleaseInputName: "Please input name",
                        pleaseInputData: "Please input data JSON",
                        table: {
                            id: "ID",
                            name: "Name",
                            data: "Data",
                            createdAt: "Created At",
                            updatedAt: "Updated At",
                            action: "Action",
                            edit: "Edit",
                            delete: "Delete"
                        }
                    },
                    console: {
                        table: {
                            id: "ID",
                            name: "Name",
                            numDay: "Num Day",
                            status: "Status",
                            currentDay: "Current Day",
                            currentTime: "Current Time",
                            config: "Config",
                            error: "Error",
                            inputTokens: "Input Tokens",
                            outputTokens: "Output Tokens",
                            createdAt: "Created At",
                            updatedAt: "Updated At",
                            action: "Action"
                        },
                        statusEnum: {
                            "0": "Not Started",
                            "1": "Running",
                            "2": "Completed",
                            "3": "Error Interrupted",
                            "4": "Stopped"
                        },
                        buttons: {
                            goto: "Goto",
                            stop: "Stop",
                            detail: "Detail",
                            viewLog: "View Log",
                            export: "Export",
                            delete: "Delete"
                        },
                        modals: {
                            experimentDetail: "Experiment Detail",
                            experimentLog: "Experiment Log",
                            refresh: "Refresh",
                            manualRefresh: "Manual refresh",
                            refreshing: "Refreshing...",
                            refreshIntervals: {
                                oneSecond: "Every 1 second",
                                fiveSeconds: "Every 5 seconds",
                                tenSeconds: "Every 10 seconds",
                                thirtySeconds: "Every 30 seconds"
                            }
                        },
                        confirmations: {
                            stopExperiment: "Are you sure to stop this experiment?",
                            deleteExperiment: "Are you sure to delete this experiment?"
                        },
                        messages: {
                            stopSuccess: "Stop experiment successfully",
                            stopFailed: "Failed to stop experiment:",
                            deleteSuccess: "Delete experiment successfully",
                            deleteFailed: "Failed to delete experiment:",
                            noToken: "No token found, please login"
                        }
                    },
                    replay: {
                        day: "Day {{day}}",
                        chatbox: {
                            tabs: {
                                reflection: "Reflection",
                                agent: "Agent",
                                user: "User",
                                survey: "Survey",
                                metrics: "Metrics"
                            },
                            survey: {
                                preview: "Preview",
                                surveyName: "Survey Name",
                                surveySent: "Survey sent, you should wait for the agent to save the survey into database and respond",
                                messageSent: "Message sent, you should wait for the agent to save the message into database and respond",
                                sendFailed: "Failed to send:"
                            },
                            dialog: {
                                sendSuccess: "Message sent, you should wait for the agent to save the message into database and respond"
                            },
                            metrics: {
                                noMetrics: "No metrics data available",
                                step: "Step",
                                value: "Value"
                            }
                        },
                        infoPanel: {
                            title: "Agent Information",
                            chooseAgent: "Please choose an agent in map",
                            unknown: "[Unknown]",
                            currentStatus: "Current Status",
                            statusHistory: "Status History",
                            name: "name",
                            id: "ID",
                            showAsHeatmap: "Click to show as heatmap"
                        },
                        timelinePlayer: {
                            replay: "Replay",
                            live: "Live",
                            stepSpeed: {
                                "10s": "10s/step",
                                "5s": "5s/step",
                                "2s": "2s/step",
                                "1s": "1s/step",
                                "0.5s": "0.5s/step",
                                "0.25s": "0.25s/step",
                                "0.1s": "0.1s/step"
                            }
                        }
                    },
                    bill: {
                        balance: 'Balance',
                        recharge: 'Recharge',
                        refresh: 'Refresh',
                        refreshSuccess: 'Refresh success',
                        autoRefreshOn: 'Auto refresh enabled',
                        autoRefreshOff: 'Auto refresh disabled',
                        fetchAccountFailed: 'Failed to fetch account information',
                        confirmRecharge: {
                            title: 'Confirm Recharge',
                            content: 'Please confirm the following information:',
                            invited: 'You are an invited user.',
                            testing: 'You understand that the system is still in testing phase and not officially launched.',
                            incomplete: 'You understand that system features may be incomplete.',
                            changeable: 'You understand that system features and pricing may change without notice.',
                            okText: 'Confirm',
                            cancelText: 'Cancel'
                        },
                        payment: {
                            title: 'Payment',
                            instruction: 'Please complete the payment on the new opened payment page',
                            openPayment: 'Open Payment Page',
                            waiting: 'Waiting for payment completion...',
                            success: 'Payment Success',
                            failed: 'Payment Failed',
                            timeout: 'Payment Timeout',
                            checkFailed: 'Check Payment Status Failed',
                            createFailed: 'Create Payment Order Failed',
                            alipayOnly: 'Currently only Alipay payment is supported',
                            refundInvoice: 'Refund and invoice functions are under development. Please contact platform staff if needed',
                            billingItems: 'Billing items include LLM input tokens (¥1.5/million tokens), output tokens (¥1.5/million tokens), and runtime (¥0.001/second)'
                        },
                        table: {
                            title: 'Bill Details',
                            id: 'ID',
                            item: 'Item',
                            related_exp_id: 'Related Experiment ID',
                            amount: 'Amount (CNY)',
                            unit_price: 'Unit Price (CNY)',
                            quantity: 'Quantity',
                            description: 'Description',
                            createdAt: 'Created At',
                            updatedAt: 'Updated At',
                            llm_input_token: 'LLM Input Token',
                            llm_output_token: 'LLM Output Token',
                            run_time: 'Run Time',
                            recharge: 'Recharge'
                        }
                    }
                }
            },
            zh: {
                translation: {
                    menu: {
                        experiments: '实验',
                        survey: '问卷',
                        documentation: '文档',
                        github: 'GitHub',
                        mlflow: 'MLFlow',
                        llmConfigs: 'LLM配置',
                        maps: '地图',
                        agents: '智能体',
                        agentConfigs: '智能体配置',
                        agentTemplates: '智能体模板',
                        workflows: '工作流',
                        create: '创建',
                        login: '登录',
                        logout: '退出登录',
                        account: '账户',
                        demo: '示例',
                        demoUser: '示例用户',
                        bill: '账单',
                        profiles: '智能体配置',
                        profileGeneration: '生成配置',
                    },
                    home: {
                        whatsNew: "最新动态",
                        releaseNotes: "V1.3版本发布。点击此处查看发布说明。",
                        getStarted: "开始使用",
                        stars: "星标",
                        mainDescription: "使用<strong><em>大模型驱动的社会人智能体</em></strong>和<strong><em>真实城市社会环境</em></strong>构建虚拟社会"
                    },
                    survey: {
                        createSurvey: "创建问卷",
                        editSurvey: "编辑问卷",
                        surveyName: "问卷名称",
                        surveyJsonData: "问卷JSON数据",
                        onlineVisualEditor: "在线可视化编辑器",
                        submit: "提交",
                        delete: "删除",
                        deleteConfirm: "确定要删除这个问卷吗？",
                        createSuccess: "创建成功！",
                        updateSuccess: "更新成功！",
                        deleteSuccess: "删除成功！",
                        createFailed: "创建失败：",
                        updateFailed: "更新失败：",
                        deleteFailed: "删除失败：",
                        fetchFailed: "获取问卷失败：",
                        invalidJson: "JSON格式无效",
                        pleaseInputName: "请输入名称",
                        pleaseInputData: "请输入JSON数据",
                        table: {
                            id: "ID",
                            name: "名称",
                            data: "数据",
                            createdAt: "创建时间",
                            updatedAt: "更新时间",
                            action: "操作",
                            edit: "编辑",
                            delete: "删除"
                        }
                    },
                    console: {
                        table: {
                            id: "ID",
                            name: "名称",
                            numDay: "天数",
                            status: "状态",
                            currentDay: "当前天数",
                            currentTime: "当前时间",
                            config: "配置",
                            error: "报错",
                            inputTokens: "输入Token数",
                            outputTokens: "输出Token数",
                            createdAt: "创建时间",
                            updatedAt: "更新时间",
                            action: "操作"
                        },
                        statusEnum: {
                            "0": "未开始",
                            "1": "运行中",
                            "2": "已完成",
                            "3": "错误中断",
                            "4": "已停止"
                        },
                        buttons: {
                            goto: "查看",
                            stop: "停止",
                            detail: "详情",
                            viewLog: "查看日志",
                            export: "导出",
                            delete: "删除"
                        },
                        modals: {
                            experimentDetail: "实验详情",
                            experimentLog: "实验日志",
                            refresh: "刷新",
                            manualRefresh: "手动刷新",
                            refreshing: "正在刷新...",
                            refreshIntervals: {
                                oneSecond: "每秒刷新",
                                fiveSeconds: "每5秒刷新",
                                tenSeconds: "每10秒刷新",
                                thirtySeconds: "每30秒刷新"
                            }
                        },
                        confirmations: {
                            stopExperiment: "确定要停止这个实验吗？",
                            deleteExperiment: "确定要删除这个实验吗？"
                        },
                        messages: {
                            stopSuccess: "停止实验成功",
                            stopFailed: "停止实验失败：",
                            deleteSuccess: "删除实验成功",
                            deleteFailed: "删除实验失败：",
                            noToken: "未找到token，请登录"
                        }
                    },
                    replay: {
                        day: "第{{day}}天",
                        chatbox: {
                            tabs: {
                                reflection: "反思",
                                agent: "智能体",
                                user: "用户",
                                survey: "问卷",
                                metrics: "指标"
                            },
                            dialog: {
                                sendSuccess: "消息已发送，请等待智能体将消息保存到数据库并响应"
                            },
                            survey: {
                                preview: "预览",
                                surveyName: "问卷名称",
                                surveySent: "问卷已发送，请等待智能体将问卷保存到数据库并响应",
                                messageSent: "消息已发送，请等待智能体将消息保存到数据库并响应",
                                sendFailed: "发送失败："
                            },
                            metrics: {
                                noMetrics: "没有可用的指标数据",
                                step: "步数",
                                value: "值"
                            }
                        },
                        infoPanel: {
                            title: "智能体信息",
                            chooseAgent: "请在地图中选择一个智能体",
                            unknown: "[未知]",
                            currentStatus: "当前状态",
                            statusHistory: "状态历史",
                            name: "名称",
                            id: "ID",
                            showAsHeatmap: "点击显示为热力图"
                        },
                        timelinePlayer: {
                            replay: "回放",
                            live: "直播",
                            stepSpeed: {
                                "10s": "10秒/步",
                                "5s": "5秒/步",
                                "2s": "2秒/步",
                                "1s": "1秒/步",
                                "0.5s": "0.5秒/步",
                                "0.25s": "0.25秒/步",
                                "0.1s": "0.1秒/步"
                            }
                        }
                    },
                    bill: {
                        balance: '余额',
                        recharge: '充值',
                        refresh: '刷新',
                        refreshSuccess: '刷新成功',
                        autoRefreshOn: '自动刷新已开启',
                        autoRefreshOff: '自动刷新已关闭',
                        fetchAccountFailed: '获取账户信息失败',
                        confirmRecharge: {
                            title: '确认充值',
                            content: '请确认以下信息：',
                            invited: '您是受邀请的用户。',
                            testing: '您了解该系统目前仍处于测试阶段，尚未正式运行。',
                            incomplete: '您了解系统各项功能可能存在不完善的情况。',
                            changeable: '您了解系统功能、收费标准随时可能变更且不作通知。',
                            okText: '确认',
                            cancelText: '取消'
                        },
                        payment: {
                            title: '支付',
                            instruction: '请在新打开的支付页面完成支付',
                            openPayment: '打开支付页面',
                            waiting: '等待支付完成...',
                            success: '支付成功',
                            failed: '支付失败',
                            timeout: '支付超时',
                            checkFailed: '检查支付状态失败',
                            createFailed: '创建支付订单失败',
                            alipayOnly: '本平台支付目前仅支持支付宝',
                            refundInvoice: '退款与发票开具功能正在开发中，如有需要请联系平台工作人员',
                            billingItems: '计费项目目前包括大模型输入Token（1.5元/百万Token）、输出Token（1.5元/百万Token）、运行时长（0.001元/秒）'
                        },
                        table: {
                            title: '账单详情',
                            id: 'ID',
                            item: '项目',
                            related_exp_id: '关联实验ID',
                            amount: '金额 (元)',
                            unit_price: '单价 (元)',
                            quantity: '数量',
                            description: '描述',
                            createdAt: '创建时间',
                            updatedAt: '更新时间',
                            llm_input_token: 'LLM输入Token',
                            llm_output_token: 'LLM输出Token',
                            run_time: '运行时间',
                            recharge: '充值'
                        }
                    }
                }
            }
        }
    });

export default i18n;