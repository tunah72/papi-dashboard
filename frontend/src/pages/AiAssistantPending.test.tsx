import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { describe, expect, it } from 'vitest'
import { AiAssistantPending } from './AiAssistantPending'

describe('Trợ lý AI trong giai đoạn migration', () => {
  it('công bố ranh giới và giữ quyền phê duyệt cho người dùng', () => {
    render(<MemoryRouter initialEntries={['/ai-assistant?scale=eight&year=2024']} future={{ v7_startTransition: true, v7_relativeSplatPath: true }}><AiAssistantPending /></MemoryRouter>)

    expect(screen.getByRole('heading', { name: 'Quyền chạy code vẫn thuộc về bạn' })).toBeInTheDocument()
    expect(screen.getByText(/mở trang không sinh code và không chạy/)).toBeInTheDocument()
    expect(screen.getByText('Xem code và giải thích')).toBeInTheDocument()
    expect(screen.getByText('Sửa và quyết định')).toBeInTheDocument()
    expect(screen.getByText('Chạy local và lưu log')).toBeInTheDocument()
    expect(screen.queryByRole('button', { name: /thực thi/i })).not.toBeInTheDocument()
    expect(screen.getByRole('link', { name: 'Quay lại Tổng quan' })).toHaveAttribute('href', '/overview?scale=eight&year=2024')
  })
})
