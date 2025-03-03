import React from 'react'
import ReactDOM from 'react-dom/client'
import './index.css'
import { Navigate, RouterProvider, createBrowserRouter } from 'react-router-dom'
import { ConfigProvider, ThemeConfig } from 'antd'
import RootLayout from './Layout'
import Console from './pages/Console/index'
import Replay from './pages/Replay/index'
import Survey from './pages/Survey'
import enUS from 'antd/locale/en_US'

const router = createBrowserRouter([
    {
        path: "/",
        element: <RootLayout selectedKey='/'><Console /></RootLayout>,
    },
    {
        path: "/exp/:id",
        element: <RootLayout selectedKey='/'><Replay /></RootLayout>,
    },
    {
        path: "/survey",
        element: <RootLayout selectedKey='/survey'><Survey /></RootLayout>,
    },
    {
        path: "*",
        element: <Navigate to="/" />,
    }
])

const theme: ThemeConfig = {
    token: {
        // colorTextHeading: "#007AFF",
        colorBgContainer: "#FFFFFF",
        colorBgLayout: "#FFFFFF",
    },
    components: {
        Layout: {
            lightSiderBg: "#F8F8F8",
            headerBg: "#FFFFFF",
        },
        Button: {
            colorBgContainer: "#FFFFFF",
        },
        Select: {
            colorBgContainer: "#FFFFFF",
        }
    }
};

ReactDOM.createRoot(document.getElementById('root')!).render(
    <ConfigProvider theme={theme} locale={enUS}>
        <RouterProvider router={router} />
    </ConfigProvider>,
)
