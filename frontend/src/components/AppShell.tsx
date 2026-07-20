import { Outlet, useLocation } from 'react-router-dom'
import { useEffect, useState } from 'react'
import { Sidebar } from './Sidebar'
import { useNavigationStore } from '../state/navigation'
import { navigation } from './navigation'

export function AppShell() {
  const [drawerOpen, setDrawerOpen] = useState(false)
  const collapsed = useNavigationStore((state) => state.desktopCollapsed)
  const location = useLocation()
  const active = navigation.find(([, href]) => href === location.pathname)?.[0] ?? 'Không tìm thấy'
  useEffect(() => {
    const escape = (event: KeyboardEvent) => { if (event.key === 'Escape' && drawerOpen) { setDrawerOpen(false); window.setTimeout(() => document.querySelector<HTMLButtonElement>('.menu-trigger')?.focus(), 0) } }
    document.addEventListener('keydown', escape)
    return () => document.removeEventListener('keydown', escape)
  }, [drawerOpen])
  return <div className={`app-frame ${collapsed ? 'sidebar-collapsed' : ''}`}>
    <a className="skip-link" href="#noi-dung">Bỏ qua điều hướng</a>
    <Sidebar drawerOpen={drawerOpen} closeDrawer={() => setDrawerOpen(false)} onOpenDrawer={() => setDrawerOpen(true)} />
    <main id="noi-dung" className="main"><header className="page-header"><p className="product-context"><span aria-hidden="true" />PAPI Việt Nam · 2011–2024</p><p className="breadcrumb">Khám phá dữ liệu <span aria-hidden="true">/</span> <strong>{active}</strong></p></header><Outlet /></main>
  </div>
}
