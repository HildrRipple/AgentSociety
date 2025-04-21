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
                }
            },
            zh: {
                translation: {
                    experiments: '实验',
                    survey: '调查问卷',
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
                }
            }
        }
    });

export default i18n;