import React from 'react'
import ReactDOM from 'react-dom/client'
import './index.css'
import { Navigate, RouterProvider, createBrowserRouter } from 'react-router-dom'
import { ConfigProvider, ThemeConfig } from 'antd'
import RootLayout from './Layout'
import Console from './pages/Console/index'
import Replay from './pages/Replay/index'
import Survey from './pages/Survey/index'
import LLMList from './pages/LLM/LLMList'
import AgentList from './pages/Agent/AgentList'
import WorkflowList from './pages/Experiment/WorkflowList'
import MapList from './pages/Map/MapList'
import CreateExperiment from './pages/Experiment/CreateExperiment'
import ProfileList from './pages/Agent/ProfileList'
import ProfileGeneration from './pages/Agent/ProfileGeneration'
import AgentTemplate from './pages/Agent/AgentTemplateList'
import Home from './pages/Home'
import zhCN from 'antd/locale/zh_CN'
import enUS from 'antd/locale/en_US'
import Callback from './pages/Callback'
import { AuthProvider, sdkConfig } from './components/Auth'
import './i18n'
import { useTranslation } from 'react-i18next'
import Bill from './pages/Bill'
import AgentTemplateForm from './pages/Agent/AgentTemplateForm'

const router = createBrowserRouter([
    {
        path: "/",
        element: <RootLayout selectedKey='/' homePage><Home /></RootLayout>,
    },
    {
        path: "/console",
        element: (
            <AuthProvider sdkConfig={sdkConfig}>
                <RootLayout selectedKey='/console'><Console /></RootLayout>
            </AuthProvider>
        ),
    },
    {
        path: "/exp/:id",
        element: (
            <AuthProvider sdkConfig={sdkConfig}>
                <RootLayout selectedKey='/console'><Replay /></RootLayout>
            </AuthProvider>
        ),
    },
    {
        path: "/survey",
        element: (
            <AuthProvider sdkConfig={sdkConfig}>
                <RootLayout selectedKey='/survey'><Survey /></RootLayout>
            </AuthProvider>
        ),
    },
    {
        path: "/create-experiment",
        element: (
            <AuthProvider sdkConfig={sdkConfig}>
                <RootLayout selectedKey='/create-experiment'><CreateExperiment /></RootLayout>
            </AuthProvider>
        ),
    },
    {
        path: "/llms",
        element: (
            <AuthProvider sdkConfig={sdkConfig}>
                <RootLayout selectedKey='/llms'><LLMList /></RootLayout>
            </AuthProvider>
        ),
    },
    {
        path: "/agents",
        element: (
            <AuthProvider sdkConfig={sdkConfig}>
                <RootLayout selectedKey='/agents'><AgentList /></RootLayout>
            </AuthProvider>
        ),
    },
    {
        path: "/profiles",
        element: (
            <AuthProvider sdkConfig={sdkConfig}>
                <RootLayout selectedKey='/profiles'><ProfileList /></RootLayout>
            </AuthProvider>
        ),
    },
    {
        path: "/profile-generation",
        element: (
            <AuthProvider sdkConfig={sdkConfig}>
                <RootLayout selectedKey='/profile-generation'><ProfileGeneration /></RootLayout>
            </AuthProvider>
        ),
    },
    {
        path: "/workflows",
        element: (
            <AuthProvider sdkConfig={sdkConfig}>
                <RootLayout selectedKey='/workflows'><WorkflowList /></RootLayout>
            </AuthProvider>
        ),
    },
    {
        path: "/maps",
        element: (
            <AuthProvider sdkConfig={sdkConfig}>
                <RootLayout selectedKey='/maps'><MapList /></RootLayout>
            </AuthProvider>
        ),
    },
    {
        path: "/bill",
        element: (
            <AuthProvider sdkConfig={sdkConfig}>
                <RootLayout selectedKey='/bill'><Bill /></RootLayout>
            </AuthProvider>
        ),
    },
    {
        path: "/callback",
        element: <Callback />,
    },
    {
        path: "/agent-templates",
        element: (
            <AuthProvider sdkConfig={sdkConfig}>
                <RootLayout selectedKey='/agent-templates'><AgentTemplate /></RootLayout>
            </AuthProvider>
        ),
    },
    {
        path: "/agent-templates/create",
        element: (
            <AuthProvider sdkConfig={sdkConfig}>
                <RootLayout selectedKey='/agent-templates'><AgentTemplateForm /></RootLayout>
            </AuthProvider>
        ),
    },
    {
        path: "/agent-templates/edit/:id",
        element: (
            <AuthProvider sdkConfig={sdkConfig}>
                <RootLayout selectedKey='/agent-templates'><AgentTemplateForm /></RootLayout>
            </AuthProvider>
        ),
    },
    {
        path: "*",
        element: <Navigate to="/" />,
    }
])

const theme: ThemeConfig = {
    token: {
        colorPrimary: "#0000CC",
        colorInfo: "#0000CC",
        borderRadius: 16,
        colorBgContainer: "#FFFFFF",
        colorBgLayout: "#FFFFFF",
    },
    components: {
        Layout: {
            lightSiderBg: "#F8F8F8",
            headerBg: "#FFFFFF",
        },
        Button: {
            algorithm: true,
            colorBgContainer: "#FFFFFF",
        },
        Select: {
            colorBgContainer: "#FFFFFF",
        }
    }
};

const App = () => {
    const { i18n } = useTranslation()
    
    return (
        <ConfigProvider 
            theme={theme} 
            locale={i18n.language === 'zh' ? zhCN : enUS}
        >
            <RouterProvider router={router} />
        </ConfigProvider>
    )
}

ReactDOM.createRoot(document.getElementById('root')!).render(
    <App />
)
