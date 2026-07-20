import { NavLink } from 'react-router-dom'
import { useEffect, useRef, useState } from 'react'
import { useNavigationStore } from '../state/navigation'
import { navigation } from './navigation'

type SidebarProps = { drawerOpen: boolean; closeDrawer: () => void; onOpenDrawer: () => void }

export function Sidebar({ drawerOpen, closeDrawer, onOpenDrawer }: SidebarProps) {
  const collapsed = useNavigationStore((state) => state.desktopCollapsed)
  const setCollapsed = useNavigationStore((state) => state.setDesktopCollapsed)
  const trigger = useRef<HTMLButtonElement>(null)
  const panel = useRef<HTMLElement>(null)
  const [compact, setCompact] = useState(() => window.matchMedia('(max-width: 1023px)').matches)
  const close = () => { closeDrawer(); window.setTimeout(() => trigger.current?.focus(), 0) }
  useEffect(() => { const query = window.matchMedia('(max-width: 1023px)'); const update = () => setCompact(query.matches); query.addEventListener('change', update); return () => query.removeEventListener('change', update) }, [])
  useEffect(() => { if (panel.current) panel.current.inert = compact && !drawerOpen }, [compact, drawerOpen])
  useEffect(() => {
    if (!drawerOpen || !panel.current) return
    const node = panel.current
    const items = () => [...node.querySelectorAll<HTMLElement>('a[href],button:not([disabled]),[tabindex]:not([tabindex="-1"])')]
    window.setTimeout(() => items().at(-1)?.focus(), 0)
    const trap = (event: KeyboardEvent) => { const all = items(); const first = all[0]; const last = all.at(-1); if (event.key === 'Tab' && first && last) { if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last.focus() } else if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first.focus() } } }
    node.addEventListener('keydown', trap)
    return () => node.removeEventListener('keydown', trap)
  }, [drawerOpen])
  return <>
    <button ref={trigger} className="menu-trigger" aria-label="Mở điều hướng" aria-expanded={drawerOpen} onClick={onOpenDrawer}>Mục lục</button>
    <aside ref={panel} className={`sidebar ${collapsed ? 'is-collapsed' : ''} ${drawerOpen ? 'is-open' : ''}`} aria-label="Điều hướng chính" aria-hidden={compact && !drawerOpen} aria-modal={compact && drawerOpen || undefined} role={compact && drawerOpen ? 'dialog' : undefined}>
      <div className="brand"><span className="brand-mark">P</span><span className="sidebar-copy"><strong>PAPI Việt Nam</strong><small>Dữ liệu công dân</small></span></div>
      <button className="collapse" aria-label={collapsed ? 'Mở rộng thanh điều hướng' : 'Thu gọn thanh điều hướng'} onClick={() => setCollapsed(!collapsed)}><span aria-hidden="true">{collapsed ? '›' : '‹'}</span><span className="sidebar-copy">Thu gọn</span></button>
      <nav><p className="nav-label sidebar-copy">Khám phá dữ liệu</p>{navigation.map(([label, to, no]) => <NavLink key={to} to={to} onClick={close} className={({ isActive }) => `nav-link ${isActive ? 'is-active' : ''}`}><span className="nav-no">{no}</span><span className="sidebar-copy">{label}</span></NavLink>)}</nav>
      <div className="sidebar-footer sidebar-copy"><span>2011–2024</span><small>Nguồn: PAPI · UNDP</small></div>
      <button className="drawer-close" onClick={close}>Đóng điều hướng</button>
    </aside>
    {drawerOpen && <button className="scrim" aria-label="Đóng điều hướng" onClick={close} />}
  </>
}
