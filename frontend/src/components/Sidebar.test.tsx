import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { Sidebar } from './Sidebar'
import { useNavigationStore } from '../state/navigation'
import { vi } from 'vitest'

const renderSidebar = (route = '/overview') => render(<MemoryRouter initialEntries={[route]} future={{ v7_startTransition: true, v7_relativeSplatPath: true }}><Sidebar drawerOpen={false} closeDrawer={() => undefined} onOpenDrawer={() => undefined} /></MemoryRouter>)

beforeEach(() => { useNavigationStore.setState({ desktopCollapsed: false }) })

it('hiển thị năm route phân tích, đúng thứ tự và active route', () => {
  renderSidebar('/overview')
  expect(screen.getAllByRole('link').map((link) => link.textContent?.replace(/\d+/g, '').trim())).toEqual(['Tổng quan', 'Diễn biến theo thời gian', 'Vùng & tỉnh', 'Mối quan hệ lĩnh vực', 'Thay đổi & phân nhóm'])
  expect(screen.getByRole('link', { name: /Tổng quan/ })).toHaveClass('is-active')
})

it('thu gọn và lưu lựa chọn sidebar', () => {
  renderSidebar()
  fireEvent.click(screen.getByRole('button', { name: 'Thu gọn thanh điều hướng' }))
  expect(useNavigationStore.getState().desktopCollapsed).toBe(true)
})

it('drawer compact bị inert khi đóng, trap Tab khi mở và trả focus về nút mở', async () => {
  Object.defineProperty(window, 'matchMedia', { writable: true, value: () => ({ matches: true, media: '', onchange: null, addEventListener: () => undefined, removeEventListener: () => undefined, addListener: () => undefined, removeListener: () => undefined, dispatchEvent: () => false }) })
  const close = vi.fn()
  const view = render(<MemoryRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}><Sidebar drawerOpen={false} closeDrawer={close} onOpenDrawer={() => undefined} /></MemoryRouter>)
  const panel = screen.getByLabelText('Điều hướng chính')
  expect(panel).toHaveAttribute('aria-hidden', 'true')
  expect(panel).toHaveProperty('inert', true)
  view.rerender(<MemoryRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}><Sidebar drawerOpen closeDrawer={close} onOpenDrawer={() => undefined} /></MemoryRouter>)
  const drawerClose = panel.querySelector<HTMLButtonElement>('.drawer-close')!
  drawerClose.focus(); fireEvent.keyDown(panel, { key: 'Tab' })
  expect(screen.getByRole('button', { name: 'Thu gọn thanh điều hướng' })).toHaveFocus()
  fireEvent.click(drawerClose)
  await waitFor(() => expect(screen.getByRole('button', { name: 'Mở điều hướng' })).toHaveFocus())
})
