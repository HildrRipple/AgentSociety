import { Divider, Flex, Layout } from "antd";
import { Content, Header } from "antd/es/layout/layout";
import RootMenu from "./Menu";

export default function RootLayout({
    children,
    selectedKey,
}: {
    children: React.ReactNode
    selectedKey: string
}) {
    return (
        <Layout>
            <Header>
                <Flex gap='small' align='center'>
                    <span>AgentSociety</span>
                    <Divider type="vertical" />
                    <RootMenu selectedKey={selectedKey} />
                </Flex>
            </Header>
            <Content style={{ height: "90vh" }}>
                {children}
            </Content>
        </Layout>
    )
}
