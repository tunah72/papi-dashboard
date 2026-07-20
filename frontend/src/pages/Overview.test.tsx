import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { vi } from 'vitest'
import { Overview } from './Overview'
import { api } from '../api/client'
import type { GeojsonResponse, MetadataResponse, OverviewResponse } from '../api/client'

vi.mock('react-plotly.js/factory', () => ({ default: () => (props: { onClick?: (event: { points: Array<{ customdata: number }> }) => void }) => <button data-testid="ban-do" onClick={() => props.onClick?.({ points: [{ customdata: 2 }] })}>Chọn từ bản đồ</button> }))
vi.mock('plotly.js-geo-dist-min', () => ({ default: {} }))
vi.mock('../api/client', async (importOriginal) => {
  const actual = await importOriginal<typeof import('../api/client')>()
  return { ...actual, api: { metadata: vi.fn(), geojson: vi.fn(), overview: vi.fn() } }
})

const metadata = { meta: { source: 'PAPI', unit: 'metadata', n: 63, caveats: [], filters: {}, schemaVersion: 'v1' }, data: { scales: [{ id: 'six', label: '6', years: [2023, 2024], dimensions: [], totalColumn: 'total' }, { id: 'eight', label: '8', years: [2018, 2024], dimensions: [], totalColumn: 'total8' }], dimensions: [], regions: [], provinces: [] } } satisfies MetadataResponse
const geojson = { meta: metadata.meta, data: { geojson: { type: 'FeatureCollection', features: [] } } } satisfies GeojsonResponse
const overview = { meta: { source: 'PAPI', unit: 'điểm', n: 2, caveats: ['Caveat thật'], filters: { scale: 'six', year: 2024 }, schemaVersion: 'v1' }, data: { measure: { id: 'total', label: 'Tổng', unit: 'điểm' }, metrics: { mean: 30, min: 20, max: 40, leader: 'An Giang', last: 'Bắc Giang', gap: 20 }, map: { rowCount: 2, unit: 'điểm', source: 'PAPI', caveats: [], rows: [{ provinceId: 1, provinceVi: 'An Giang', region: 'Mekong', score: 40 }, { provinceId: 2, provinceVi: 'Bắc Giang', region: 'Bắc', score: 20 }] }, ranking: { rowCount: 2, unit: 'điểm', source: 'PAPI', caveats: [], rows: [], top10: [{ provinceId: 1, provinceVi: 'An Giang', region: 'Mekong', score: 40, rank: 1 }], bottom10: [{ provinceId: 2, provinceVi: 'Bắc Giang', region: 'Bắc', score: 20, rank: 2 }] } } } satisfies OverviewResponse

function renderOverview(url = '/overview?scale=six&year=2024') { const query = new QueryClient({ defaultOptions: { queries: { retry: false } } }); return render(<QueryClientProvider client={query}><MemoryRouter initialEntries={[url]} future={{ v7_startTransition: true, v7_relativeSplatPath: true }}><Routes><Route path="/overview" element={<Overview />} /></Routes></MemoryRouter></QueryClientProvider>) }
beforeEach(() => { vi.mocked(api.metadata).mockResolvedValue(metadata); vi.mocked(api.geojson).mockResolvedValue(geojson); vi.mocked(api.overview).mockResolvedValue(overview) })

it('dùng URL filters và hiển thị metadata thực', async () => { renderOverview(); expect(await screen.findByRole('heading', { name: /Điểm quản trị/ })).toBeInTheDocument(); expect(api.overview).toHaveBeenCalledWith('six', 2024); expect(screen.getAllByText('n = 2 tỉnh')).toHaveLength(2) })
it('liên kết ranking với lựa chọn và CTA hồ sơ tỉnh', async () => { const user = userEvent.setup(); renderOverview(); await screen.findByRole('heading', { name: /Điểm quản trị/ }); await user.click(screen.getByRole('tab', { name: 'Thấp nhất' })); await user.click(screen.getByRole('button', { name: /Bắc Giang/ })); expect(screen.getByRole('heading', { name: 'Bắc Giang' })).toBeInTheDocument(); expect(screen.getByRole('link', { name: /Xem hồ sơ tỉnh/ })).toHaveAttribute('href', expect.stringContaining('province=B%E1%BA%AFc%20Giang')) })
it('map click pin tỉnh ngoài tab xếp hạng để đọc và chọn bằng bàn phím', async () => { const user = userEvent.setup(); renderOverview(); await screen.findByRole('heading', { name: /Điểm quản trị/ }); await user.click(screen.getByTestId('ban-do')); const pin = screen.getByRole('button', { name: /Tỉnh đang chọn: Bắc Giang/ }); expect(pin).toHaveClass('selected'); pin.focus(); await user.keyboard('{Enter}'); expect(screen.getByRole('heading', { name: 'Bắc Giang' })).toBeInTheDocument() })
it('có error state hành động được', async () => { vi.mocked(api.metadata).mockRejectedValueOnce(new Error('API dừng')); renderOverview(); expect(await screen.findByRole('alert')).toHaveTextContent('API dừng') })
