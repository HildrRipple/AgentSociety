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
        fallbackLng: 'en',
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
                        workflows: 'Workflows',
                        create: 'Create',
                        login: 'Login',
                        logout: 'Logout',
                        account: 'Account',
                        demo: 'Demo',
                        demoUser: 'Demo User'
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
                        workflows: '工作流',
                        create: '创建',
                        login: '登录',
                        logout: '退出登录',
                        account: '账户',
                        demo: '示例',
                        demoUser: '示例用户'
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
                    }
                }
            }
        }
    });

export default i18n;