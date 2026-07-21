import { Navigate, createBrowserRouter } from 'react-router-dom'
import { AppShell } from './components/AppShell'
import { Overview } from './pages/Overview'
import { TimeTrend } from './pages/TimeTrend'
import { Provincial } from './pages/Provincial'
import { Dimension } from './pages/Dimension'
import { Dynamics } from './pages/Dynamics'

export const router = createBrowserRouter([{ element: <AppShell />, children: [
  { path: '/', element: <Navigate to="/overview" replace /> },
  { path: '/overview', element: <Overview /> },
  { path: '/time-trend', element: <TimeTrend /> },
  { path: '/provincial', element: <Provincial /> },
  { path: '/dimension', element: <Dimension /> },
  { path: '/dimensions', element: <Navigate to="/dimension" replace /> },
  { path: '/dynamics', element: <Dynamics /> },
  { path: '/ai-assistant', element: <Navigate to="/overview?assistant=open" replace /> },
  { path: '*', element: <section className="placeholder"><p className="eyebrow">404</p><h1>Không tìm thấy trang này</h1><p>Đường dẫn không thuộc dashboard. Hãy quay về Tổng quan để tiếp tục.</p><a className="text-link" href="/overview">Về Tổng quan</a></section> },
] }])
