import { act, fireEvent, render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { afterEach, beforeEach, expect, it, vi } from 'vitest'
import { FloatingAssistant } from './FloatingAssistant'
import { useAssistantStore } from '../state/assistant'

const renderAssistant = (route = '/overview?scale=eight&year=2024') => render(<MemoryRouter initialEntries={[route]} future={{ v7_startTransition: true, v7_relativeSplatPath: true }}><FloatingAssistant /></MemoryRouter>)

beforeEach(() => {
  sessionStorage.clear()
  useAssistantStore.setState({ mode: 'hidden', isMaximized: false, sessionId: null, turns: [], revisionOf: null, busy: null, error: null })
})
afterEach(() => vi.unstubAllGlobals())

it('mở từ launcher mà không gọi API và chỉ có một action đóng dialog', async () => {
  const fetch = vi.fn()
  vi.stubGlobal('fetch', fetch)
  renderAssistant()
  fireEvent.click(screen.getByRole('button', { name: 'Mở Trợ lý AI' }))
  expect(screen.getByRole('dialog', { name: 'Trợ lý AI' })).toBeInTheDocument()
  expect(screen.getByRole('button', { name: 'Bắt đầu cuộc trò chuyện mới' })).toHaveTextContent('+')
  expect(fetch).not.toHaveBeenCalled()
  expect(screen.queryByRole('button', { name: 'Thu nhỏ' })).not.toBeInTheDocument()
  act(() => useAssistantStore.getState().addUser('Giữ lại câu hỏi này'))
  fireEvent.click(screen.getByRole('button', { name: 'Đóng Trợ lý AI' }))
  expect(screen.queryByRole('dialog', { name: 'Trợ lý AI' })).not.toBeInTheDocument()
  fireEvent.click(screen.getByRole('button', { name: 'Mở Trợ lý AI' }))
  expect(screen.getByText('Giữ lại câu hỏi này')).toBeInTheDocument()
})

it('phóng to, khôi phục bằng Escape rồi đóng bằng Escape', async () => {
  renderAssistant()
  const launcher = screen.getByRole('button', { name: 'Mở Trợ lý AI' })
  fireEvent.click(launcher)
  const dialog = screen.getByRole('dialog', { name: 'Trợ lý AI' })
  fireEvent.click(screen.getByRole('button', { name: 'Phóng to Trợ lý AI' }))
  expect(dialog).toHaveClass('is-maximized')
  expect(screen.getByRole('button', { name: 'Khôi phục kích thước Trợ lý AI' })).toHaveAttribute('aria-pressed', 'true')
  fireEvent.keyDown(dialog, { key: 'Escape' })
  expect(dialog).not.toHaveClass('is-maximized')
  expect(dialog).toBeInTheDocument()
  fireEvent.keyDown(dialog, { key: 'Escape' })
  await waitFor(() => expect(launcher).toHaveFocus())
  expect(screen.queryByRole('dialog', { name: 'Trợ lý AI' })).not.toBeInTheDocument()
})

it('assistant=open mở panel nhưng không gửi request', async () => {
  const fetch = vi.fn()
  vi.stubGlobal('fetch', fetch)
  renderAssistant('/overview?assistant=open')
  await waitFor(() => expect(screen.getByRole('dialog', { name: 'Trợ lý AI' })).toBeInTheDocument())
  expect(fetch).not.toHaveBeenCalled()
})

it('hiển thị answer và nguồn từ API', async () => {
  vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ ok: true, status: 200, json: vi.fn().mockResolvedValue({ sessionId: 's1', turnId: 't1', kind: 'answer', answer: 'PAPI phản ánh trải nghiệm của người dân.', source: 'UNDP Việt Nam · CECODES · RTA' }) }))
  renderAssistant(); fireEvent.click(screen.getByRole('button', { name: 'Mở Trợ lý AI' }))
  fireEvent.change(screen.getByLabelText('Nhập câu hỏi hoặc yêu cầu sửa'), { target: { value: 'PAPI là gì?' } })
  fireEvent.click(screen.getByRole('button', { name: 'Gửi yêu cầu' }))
  await screen.findByText('PAPI phản ánh trải nghiệm của người dân.')
  expect(screen.getByText(/Nguồn: UNDP Việt Nam/)).toBeInTheDocument()
})

it('proposal read-only chỉ chạy sau click phê duyệt', async () => {
  const fetch = vi.fn()
    .mockResolvedValueOnce({ ok: true, status: 200, json: vi.fn().mockResolvedValue({ sessionId: 's1', turnId: 't1', kind: 'proposal', proposalId: 'p1', explanation: 'Tính trung bình.', code: '# Tính\nresult = prov_year.head()', status: 'pending_approval', source: 'UNDP Việt Nam · CECODES · RTA' }) })
    .mockResolvedValueOnce({ ok: true, status: 200, json: vi.fn().mockResolvedValue({ sessionId: 's1', proposalId: 'p1', status: 'succeeded', result: { kind: 'scalar', value: 1, totalRows: 1, truncated: false, shape: [] }, figure: null, stdout: '', warnings: [], error: null }) })
  vi.stubGlobal('fetch', fetch)
  renderAssistant(); fireEvent.click(screen.getByRole('button', { name: 'Mở Trợ lý AI' }))
  fireEvent.change(screen.getByLabelText('Nhập câu hỏi hoặc yêu cầu sửa'), { target: { value: 'Tính thử' } })
  fireEvent.click(screen.getByRole('button', { name: 'Gửi yêu cầu' }))
  await screen.findByText('CHỜ DUYỆT')
  expect(screen.getByText(/result = prov_year.head/).closest('pre')).toBeInTheDocument()
  expect(fetch).toHaveBeenCalledTimes(1)
  fireEvent.click(screen.getByRole('button', { name: 'Đồng ý và chạy local' }))
  await screen.findByText('Kết quả chạy local')
  expect(fetch).toHaveBeenCalledTimes(2)
  expect(JSON.parse(fetch.mock.calls[1][1].body)).toEqual({ sessionId: 's1', proposalId: 'p1', approved: true })
})

it('Escape ẩn panel và trả focus về launcher', async () => {
  renderAssistant(); const launcher = screen.getByRole('button', { name: 'Mở Trợ lý AI' })
  fireEvent.click(launcher)
  fireEvent.keyDown(screen.getByRole('dialog', { name: 'Trợ lý AI' }), { key: 'Escape' })
  await waitFor(() => expect(launcher).toHaveFocus())
  expect(screen.queryByRole('dialog', { name: 'Trợ lý AI' })).not.toBeInTheDocument()
})
