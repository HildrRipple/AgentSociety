import { ExportOutlined, GithubOutlined, PlusOutlined } from "@ant-design/icons";
import { Menu, MenuProps, Space } from "antd";
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
// import Account from "./components/Account";

const RootMenu = ({ selectedKey }: {
    selectedKey: string,
}) => {

    const [mlflowUrl, setMlflowUrl] = useState<string>("");

    useEffect(() => {
        fetch("/api/mlflow/url")
            .then(res => res.json())
            .then(res => {
                setMlflowUrl(res.data);
            });
    }, []);


    const menuItems: MenuProps['items'] = [
        { key: "/", label: <Link to="/">Experiments</Link> },
        { key: "/create-experiment", label: <Link to="/create-experiment"><Space>Create Experiment<PlusOutlined /></Space></Link> },
        { key: "/survey", label: <Link to="/survey">Survey</Link> },
        // { key: "/exp", label: <Link to="/exp">Replay & Live</Link> },
        // { key: "/sim", label: <Link to="/sim">平台</Link> },
        // { key: "/console", label: <Link to="/console">控制台</Link> },
        // { key: "文档", label: <Link to="https://docs-opencity.fiblab.net/docs/get-started" rel="noopener noreferrer" target="_blank"><Space>文档<ExportOutlined /></Space></Link> },
        // { key: "登录", label: <div style={{ marginLeft: "auto" }}><Account /></div> }
    ];
    if (mlflowUrl !== "") {
        menuItems.push({ key: "/mlflow", label: <Link to={mlflowUrl} rel="noopener noreferrer" target="_blank"><Space>MLFlow<ExportOutlined /></Space></Link> });
    }
    menuItems.push({ key: "/Documentation", label: <Link to="https://agentsociety.readthedocs.io/en/latest/" rel="noopener noreferrer" target="_blank"><Space>Documentation<ExportOutlined /></Space></Link> });
    menuItems.push({ key: "/Github", label: <Link to="https://github.com/tsinghua-fib-lab/agentsociety/" rel="noopener noreferrer" target="_blank"><Space>GitHub<GithubOutlined /><ExportOutlined /></Space></Link> });

    return <Menu
        mode="horizontal"
        items={menuItems}
        selectedKeys={[selectedKey]}
    />;
};

export default RootMenu;
