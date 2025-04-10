import { Divider, Flex, Layout } from "antd";
import { Content, Header } from "antd/es/layout/layout";
import RootMenu from "./Menu";
import { Link } from "react-router-dom";
import React, { useEffect, useRef } from "react";

export default function RootLayout({
    children,
    selectedKey,
    homePage,
}: {
    children: React.ReactNode
    selectedKey: string
    homePage?: boolean
}) {
    const headerRef = useRef<HTMLDivElement>(null);
    const contentRef = useRef<HTMLDivElement>(null);

    const headerStyle = {
        background: '#000088',
        color: 'white',
    }

    const menuStyle = {
        background: '#000088',
        color: 'white',
    }

    // get the height of the header to set the content height
    useEffect(() => {
        if (contentRef.current === null) {
            return
        }
        if (headerRef.current) {
            const headerHeight = headerRef.current.clientHeight;
            if (contentRef.current) {
                contentRef.current.style.minHeight = `calc(100vh - ${headerHeight}px)`;
                return
            }
        }
        contentRef.current.style.minHeight = `90vh`;
    }, [headerRef, contentRef]);

    const contentStyle: React.CSSProperties = homePage ? {
        width: "100vw",
        background: '#000088',
        top: 0,
        left: 0,
        alignContent: "center",
        justifyContent: "center",
    } : {
    }

    return (
        <Layout>
            <Header ref={headerRef} style={headerStyle}>
                <Flex gap='small' align='center'>
                    <Link to="/" style={{ color: 'white', fontSize: '1.1rem' }}>AgentSociety</Link>
                    <Divider type="vertical" />
                    <RootMenu selectedKey={homePage ? "" : selectedKey} style={menuStyle} />
                </Flex>
            </Header>
            <Content ref={contentRef} style={contentStyle}>
                {children}
            </Content>
        </Layout>
    )
}
