import { afterEach, expect, it, vi } from 'vitest'
import { api } from './client'

afterEach(() => vi.unstubAllGlobals())

it('chuẩn hóa lỗi mạng thành hướng dẫn khởi động FastAPI local', async () => {
  vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new TypeError('Failed to fetch')))
  await expect(api.metadata()).rejects.toMatchObject({ message: 'Không kết nối được FastAPI local. Hãy khởi động server rồi thử lại.', status: 0 })
})

it('báo rõ JSON lỗi thay vì trả dữ liệu hỏng', async () => {
  vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ ok: true, status: 200, json: vi.fn().mockRejectedValue(new SyntaxError('bad json')) }))
  await expect(api.metadata()).rejects.toMatchObject({ message: 'FastAPI local trả về dữ liệu không hợp lệ. Hãy khởi động lại server rồi thử lại.', status: 200 })
})

it('giữ thông tin HTTP nhưng không lộ lỗi trình duyệt', async () => {
  vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ ok: false, status: 503, json: vi.fn().mockResolvedValue({ detail: 'Dịch vụ đang bảo trì' }) }))
  await expect(api.metadata()).rejects.toMatchObject({ message: 'Không thể tải dữ liệu (503). Dịch vụ đang bảo trì', status: 503 })
})
