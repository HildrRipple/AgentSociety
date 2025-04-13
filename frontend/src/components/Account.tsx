/* eslint-disable @typescript-eslint/no-explicit-any */
// 账户管理的按钮，默认显示名称，下拉框可以进入个人主页与退出登录
import React, { useEffect, useState } from "react";
import { Avatar, Button, Dropdown, MenuProps, Space } from "antd";
import { DownOutlined } from "@ant-design/icons";
import { getAccessToken, getCasdoorSdk } from "./Auth";
import { sdkConfig } from "./Auth";

const DEFAULT_AVATAR = "https://cdn.casbin.org/img/casbin.svg";

const Account: React.FC = () => {
    const [userInfo, setUserInfo] = useState<any>(null);
    const sdk = getCasdoorSdk(sdkConfig);

    useEffect(() => {
        const token = getAccessToken();
        if (token !== null) {
            sdk.getUserInfo(token).then((res: any) => {
                console.log('Got user info:', res);
                setUserInfo(res);
            }).catch((err: any) => {
                console.error('Failed to get user info:', err);
                localStorage.removeItem("access_token");
            });
        }
    }, []);

    console.log('Account component rendered, userInfo:', userInfo);
    console.log('Access Token in Account:', localStorage.getItem("access_token"));

    const casdoorLogin = () => {
        const url = sdk.getSigninUrl();
        // 跳转到 Casdoor 登录页面
        window.location.href = url;
    };

    const casdoorLogout = () => {
        localStorage.removeItem("access_token");
        window.location.href = "/";
    };

    const gotoProfile = () => {
        const token = localStorage.getItem("access_token");
        if (!token) return;

        const url = sdk.getMyProfileUrl({ accessToken: token } as any);
        if (url === null || url === "") {
            return;
        }
        window.location.href = url;
    }

    const items: MenuProps['items'] = [
        {
            label: <a onClick={gotoProfile}>Account</a>,
            key: '0',
        },
        {
            type: 'divider',
        },
        {
            label: <a onClick={casdoorLogout}>Logout</a>,
            key: '3',
        },
    ];
    if (!userInfo) {
        return (
            <div style={{ marginLeft: "16px", marginRight: "16px" }}>
                <Button
                    type="default"
                    style={{
                        width: "80px",
                        textAlign: "center",
                        background: 'rgba(255, 255, 255, 0.2)',
                        borderColor: 'transparent',
                        color: 'white'
                    }} onClick={casdoorLogin}
                >Login</Button>
            </div >
        );
    }

    return (
        <Dropdown menu={{ items }} trigger={['click']} placement="bottom">
            <a onClick={(e) => e.preventDefault()}>
                <Space style={{ color: 'white' }}>
                    <Avatar src={userInfo.avatar || DEFAULT_AVATAR} />
                    {userInfo.name}
                    <DownOutlined />
                </Space>
            </a>
        </Dropdown>
    );
};

export default Account;
