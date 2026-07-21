import { fireEvent, render, screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'

import {
  ChartCard,
  ChartMeta,
  ErrorState,
  FilterBar,
  KpiCard,
  LoadingSkeleton,
} from './DashboardPrimitives'

describe('dashboard primitives', () => {
  it('keeps filters labelled and exposes reset as a real button', () => {
    const onReset = vi.fn()

    render(<FilterBar summary="Năm 2024" onReset={onReset}><label>Năm<select><option>2024</option></select></label></FilterBar>)

    expect(screen.getByRole('region', { name: 'Bộ lọc dữ liệu' })).toBeInTheDocument()
    fireEvent.click(screen.getByRole('button', { name: 'Đặt lại' }))
    expect(onReset).toHaveBeenCalledOnce()
  })

  it('renders KPI and chart semantics without hiding metadata', () => {
    render(<>
      <KpiCard label="Điểm trung bình" value="43,43" detail="61 tỉnh/thành" tone="accent" />
      <ChartCard title="Phân bố điểm" description="So sánh theo địa phương" footer={<ChartMeta source="PAPI" unit="điểm" n={61} />}>
        <div>Biểu đồ</div>
      </ChartCard>
    </>)

    expect(screen.getByText('43,43').closest('article')).toHaveClass('kpi-accent')
    expect(screen.getByRole('heading', { name: 'Phân bố điểm' })).toBeInTheDocument()
    expect(screen.getByText('Nguồn: PAPI')).toBeVisible()
    expect(screen.getByText('n = 61')).toBeVisible()
  })

  it('announces loading and error states to assistive technology', () => {
    render(<><LoadingSkeleton label="Đang tải dữ liệu" cards={2} /><ErrorState title="Không tải được" description="Hãy thử lại." /></>)

    expect(screen.getByRole('status', { name: 'Đang tải dữ liệu' }).children).toHaveLength(2)
    expect(screen.getByRole('alert')).toHaveTextContent('Không tải được')
  })
})
