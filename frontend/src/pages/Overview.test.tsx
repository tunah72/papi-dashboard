import { render, screen, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { vi } from 'vitest'

import { Overview } from './Overview'
import { api } from '../api/client'
import type { GeojsonResponse, MetadataResponse, OverviewResponse } from '../api/client'

vi.mock('../components/CartesianChart', () => ({
  CartesianChart: ({ title, summary, children }: { title: string; summary: string; children?: React.ReactNode }) => <figure aria-label={title}><figcaption>{summary}</figcaption>{children}</figure>,
}))
vi.mock('../components/dashboard/ProvinceMap', () => ({
  ProvinceMap: ({ title, onSelect }: { title: string; onSelect: (id: number) => void }) => <button type="button" aria-label={title} onClick={() => onSelect(2)}>Chọn Bắc Giang trên bản đồ</button>,
}))
vi.mock('../api/client', async (importOriginal) => {
  const actual = await importOriginal<typeof import('../api/client')>()
  return { ...actual, api: { metadata: vi.fn(), geojson: vi.fn(), overview: vi.fn() } }
})

const metadata = {
  meta: { source: 'PAPI', unit: 'metadata', n: 63, caveats: [], filters: {}, schemaVersion: 'v1' },
  data: {
    scales: [
      { id: 'six', label: '6', years: [2023, 2024], dimensions: ['D1', 'D2'], totalColumn: 'total' },
      { id: 'eight', label: '8', years: [2018, 2024], dimensions: ['D1', 'D2'], totalColumn: 'total8' },
    ],
    dimensions: [
      { code: 'D1', nameVi: 'Tham gia', nameEn: 'Participation', short: 'D1', color: '#111', sort: 1, fromYear: 2011 },
      { code: 'D2', nameVi: 'Minh bạch', nameEn: 'Transparency', short: 'D2', color: '#222', sort: 2, fromYear: 2011 },
    ],
    regions: [], provinces: [],
  },
} satisfies MetadataResponse

const geojson = { meta: metadata.meta, data: { geojson: { type: 'FeatureCollection', features: [] } } } satisfies GeojsonResponse

const overview = {
  meta: { source: 'PAPI', unit: 'điểm', n: 2, caveats: ['Caveat thật'], filters: { scale: 'six', year: 2024 }, schemaVersion: 'v1' },
  data: {
    measure: { id: 'total', label: 'Tổng 6 lĩnh vực gốc', unit: 'điểm' },
    metrics: { mean: 30, min: 20, max: 40, leader: 'An Giang', last: 'Bắc Giang', gap: 20 },
    map: { rowCount: 2, unit: 'điểm', source: 'PAPI', caveats: [], rows: [
      { provinceId: 1, provinceVi: 'An Giang', region: 'Mekong', score: 40, rank: 1 },
      { provinceId: 2, provinceVi: 'Bắc Giang', region: 'Bắc', score: 20, rank: 2 },
    ] },
    ranking: { rowCount: 2, unit: 'điểm', source: 'PAPI', caveats: [], rows: [], top10: [], bottom10: [] },
    storyCards: {
      trend: { rowCount: 2, unit: 'điểm', source: 'PAPI', rows: [{ year: 2023, score: 29, contributorN: 2 }, { year: 2024, score: 30, contributorN: 2 }] },
      regions: { rowCount: 0, unit: 'điểm', source: 'PAPI', rows: [] },
      strongestPair: { rowCount: 0, unit: 'điểm', source: 'PAPI', n: 0, x: 'D1', y: 'D2', xMean: 0, yMean: 0, pearsonR: 0.72, rows: [] },
      changeHighlights: { rowCount: 0, unit: 'điểm', source: 'PAPI', n: 0, median: null, rows: [], top8: [], bottom8: [] },
      annualChanges: {
        rowCount: 2, unit: 'điểm', source: 'PAPI', largestIncreaseYear: 2024, largestIncrease: 1,
        largestDecreaseYear: 2023, largestDecrease: -0.5,
        rows: [
          { year: 2023, score: 29, previousScore: null, change: null, contributorN: 2, previousContributorN: 0, baseline: true },
          { year: 2024, score: 30, previousScore: 29, change: 1, contributorN: 2, previousContributorN: 2, baseline: false },
        ],
      },
      quadrants: {
        rowCount: 4, unit: 'tỷ lệ tỉnh', source: 'PAPI', n: 2, x: 'D1', y: 'D2', pearsonR: 0.72, caveats: ['Không nhân quả'],
        rows: [
          { label: 'Cao–cao', n: 1, percentage: 50, provinces: ['An Giang'] },
          { label: 'Cao–thấp', n: 0, percentage: 0, provinces: [] },
          { label: 'Thấp–cao', n: 0, percentage: 0, provinces: [] },
          { label: 'Thấp–thấp', n: 1, percentage: 50, provinces: ['Bắc Giang'] },
        ],
      },
      changeDistribution: {
        rowCount: 2, unit: 'chênh lệch điểm', source: 'PAPI', caveats: [], n: 2, fromYear: 2023, toYear: 2024,
        median: 0, positiveN: 1, negativeN: 1, unchangedN: 0, positivePercentage: 50,
        bins: [
          { lower: -1, upper: 0, center: -0.5, count: 1, percentage: 50, provinces: ['Bắc Giang'] },
          { lower: 0, upper: 1, center: 0.5, count: 1, percentage: 50, provinces: ['An Giang'] },
        ],
        rows: [],
      },
    },
    insights: {
      map: 'An Giang cao nhất; Bắc Giang thấp nhất.',
      annualChange: 'Tăng mạnh nhất vào 2024.',
      quadrants: 'Nhóm Cao–cao chiếm nhiều nhất; không hàm ý nhân quả.',
      changeDistribution: '50% tỉnh tăng điểm.',
    },
  },
} satisfies OverviewResponse

function renderOverview(url = '/overview?scale=six&year=2024') {
  const query = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(<QueryClientProvider client={query}><MemoryRouter initialEntries={[url]} future={{ v7_startTransition: true, v7_relativeSplatPath: true }}><Routes><Route path="/overview" element={<Overview />} /></Routes></MemoryRouter></QueryClientProvider>)
}

beforeEach(() => {
  vi.mocked(api.metadata).mockResolvedValue(metadata)
  vi.mocked(api.geojson).mockResolvedValue(geojson)
  vi.mocked(api.overview).mockResolvedValue(overview)
})

it('dùng URL filters và render đúng bốn câu hỏi cùng bốn insight', async () => {
  renderOverview()
  expect(await screen.findByRole('heading', { name: 'Bức tranh PAPI toàn quốc' })).toBeInTheDocument()
  expect(api.overview).toHaveBeenCalledWith('six', 2024)
  const grid = screen.getByRole('region', { name: 'Bốn góc nhìn Tổng quan' })
  expect(grid).toBeInTheDocument()
  expect(within(grid).getAllByLabelText('Insight biểu đồ')).toHaveLength(4)
  expect(screen.getByRole('heading', { name: 'Điểm PAPI cao và thấp tập trung ở đâu?' })).toBeInTheDocument()
  expect(screen.getByRole('heading', { name: 'Mặt bằng điểm thay đổi chủ yếu vào năm nào?' })).toBeInTheDocument()
  expect(screen.getByRole('heading', { name: 'Các tỉnh nằm trong bốn nhóm lĩnh vực nào?' })).toBeInTheDocument()
  expect(screen.getByRole('heading', { name: 'Phần lớn tỉnh cải thiện hay suy giảm?' })).toBeInTheDocument()
})

it('click bản đồ giữ tỉnh trong URL state và hiện CTA hồ sơ', async () => {
  const user = userEvent.setup()
  renderOverview()
  await user.click(await screen.findByRole('button', { name: 'Phân bố điểm PAPI năm 2024' }))
  const link = screen.getByRole('link', { name: /Xem hồ sơ tỉnh/ })
  expect(link.closest('.overview-selection')).toHaveTextContent('Bắc Giang')
  expect(link).toHaveAttribute('href', expect.stringContaining('province=B%E1%BA%AFc%20Giang'))
})

it('mỗi chart có nút phóng to và dialog đóng trả focus về trigger', async () => {
  const user = userEvent.setup()
  renderOverview()
  const triggers = await screen.findAllByRole('button', { name: /Phóng to biểu đồ/ })
  expect(triggers).toHaveLength(4)
  await user.click(triggers[0])
  expect(screen.getByRole('dialog')).toHaveAccessibleName('Điểm PAPI cao và thấp tập trung ở đâu?')
  await user.click(screen.getByRole('button', { name: /Thu nhỏ/ }))
  expect(triggers[0]).toHaveFocus()
})

it('có error state hành động được', async () => {
  vi.mocked(api.metadata).mockRejectedValueOnce(new Error('API dừng'))
  renderOverview()
  expect(await screen.findByRole('alert')).toHaveTextContent('API dừng')
})
