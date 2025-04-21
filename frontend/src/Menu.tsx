import { ExportOutlined, GithubOutlined, PlusOutlined, ExperimentOutlined, ApiOutlined, TeamOutlined, GlobalOutlined, NodeIndexOutlined } from "@ant-design/icons";
import { Menu, MenuProps, Space, Dropdown, Button } from "antd";
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import Account from "./components/Account";
import { useTranslation } from 'react-i18next';
// import Account from "./components/Account";

const RootMenu = ({ selectedKey, style }: {
    selectedKey: string,
    style?: React.CSSProperties
}) => {
    const { t, i18n } = useTranslation();
    const [mlflowUrl, setMlflowUrl] = useState<string>("");

    useEffect(() => {
        fetch("/api/mlflow/url")
            .then(res => res.json())
            .then(res => {
                setMlflowUrl(res.data);
            });
    }, []);

    const handleLanguageChange = () => {
        const newLang = i18n.language === 'en' ? 'zh' : 'en';
        i18n.changeLanguage(newLang);
    };

    // Experiment submenu items - horizontal layout
    const experimentItems: MenuProps['items'] = [
        {
            key: '/llms',
            label: <Link to="/llms">{t('llmConfigs')}</Link>,
            icon: <ApiOutlined />,
        },
        {
            key: '/maps',
            label: <Link to="/maps">{t('maps')}</Link>,
            icon: <GlobalOutlined />,
        },
        {
            key: '/agents',
            label: <Link to="/agents">{t('agents')}</Link>,
            icon: <TeamOutlined />,
        },
        {
            key: '/workflows',
            label: <Link to="/workflows">{t('workflows')}</Link>,
            icon: <NodeIndexOutlined />,
        },
        {
            key: '/create-experiment',
            label: <Link to="/create-experiment">{t('create')}</Link>,
            icon: <PlusOutlined />,
        },
    ];

    const menuItems: MenuProps['items'] = [
        {
            key: "/console",
            label: (
                <Dropdown menu={{ items: experimentItems }} placement="bottomLeft" arrow>
                    <div>
                        <Link to="/console"><Space><ExperimentOutlined />{t('experiments')}</Space></Link>
                    </div>
                </Dropdown>
            ),
        },
        { key: "/survey", label: <Link to="/survey">{t('survey')}</Link> },
    ];
    if (mlflowUrl !== "") {
        menuItems.push({ key: "/mlflow", label: <Link to={mlflowUrl} rel="noopener noreferrer" target="_blank"><Space>{t('mlflow')}<ExportOutlined /></Space></Link> });
    }
    menuItems.push({ key: "/Documentation", label: <Link to="https://agentsociety.readthedocs.io/en/latest/" rel="noopener noreferrer" target="_blank"><Space>{t('documentation')}</Space></Link> });
    menuItems.push({ key: "/Github", label: <Link to="https://github.com/tsinghua-fib-lab/agentsociety/" rel="noopener noreferrer" target="_blank"><Space>{t('github')}<GithubOutlined /></Space></Link> });

    const menuStyle: React.CSSProperties = {
        ...style,
        display: 'flex',
        width: '100%',
        alignItems: 'center',
    };

    return (
        <div style={{ display: 'flex', width: '100%' }}>
            <Menu
                theme="dark"
                mode="horizontal"
                items={menuItems}
                selectedKeys={[selectedKey]}
                style={menuStyle}
            />
            <div style={{ 
                marginLeft: 'auto', 
                display: 'flex', 
                alignItems: 'center',
                minWidth: '320px',
                justifyContent: 'flex-end'
            }}>
                <Button 
                    type="text"
                    style={{ color: 'white' }}
                    onClick={handleLanguageChange}
                >
                    {i18n.language === 'en' ? '中文' : 'English'}
                </Button>
                <Account />
            </div>
        </div>
    );
};

export default RootMenu;
