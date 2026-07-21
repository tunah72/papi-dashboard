import { lazy, Suspense, type ReactNode } from 'react'
import type { Config, Data, Layout } from 'plotly.js'

import { basePlotLayout, uiColors } from '../theme/chartTheme'

const Plot = lazy(async () => {
  const [{ default: factory }, coreModule, traceModule] = await Promise.all([
    import('react-plotly.js/factory'),
    import('plotly.js/lib/core'),
    import('plotly.js/lib/scatterpolar'),
  ])
  const plotly = ('default' in coreModule ? coreModule.default : coreModule) as typeof import('plotly.js')
  const scatterpolar = 'default' in traceModule ? traceModule.default : traceModule
  const register = plotly.register as unknown as (modules: unknown[]) => void
  register([scatterpolar])
  return { default: factory(plotly) }
})

type PlotPoint = { curveNumber?: number; pointIndex?: number; pointNumber?: number; customdata?: unknown }

type Props = {
  title: string
  summary: string
  data: Data[]
  layout?: Partial<Layout>
  height?: number
  children?: ReactNode
  onClick?: (event: { points?: PlotPoint[] }) => void
  config?: Partial<Config>
}

/** Bundle Plotly tối thiểu cho radar; tách khỏi Cartesian để không tải polar ở các trang khác. */
export function PolarChart({ title, summary, data, layout = {}, height = 360, children, onClick, config }: Props) {
  const polar = layout.polar ?? {}
  const plotLayout: Partial<Layout> = {
    ...basePlotLayout,
    ...layout,
    polar: {
      bgcolor: 'rgba(0,0,0,0)',
      ...polar,
      radialaxis: {
        range: [1, 10],
        dtick: 1,
        gridcolor: '#DFE8E6',
        linecolor: uiColors.border,
        tickfont: { color: uiColors.muted, size: 10 },
        ...polar.radialaxis,
      },
      angularaxis: {
        gridcolor: '#DFE8E6',
        linecolor: uiColors.border,
        tickfont: { color: uiColors.text, size: 11 },
        ...polar.angularaxis,
      },
    },
  }
  const plotConfig: Partial<Config> = { displayModeBar: false, responsive: true, showTips: false, ...config }

  return <figure className="cartesian-chart polar-chart" aria-label={title}>
    <figcaption><strong>{title}</strong><p>{summary}</p></figcaption>
    <div role="img" aria-label={`${title}. ${summary}`}>
      <Suspense fallback={<div className="chart-fallback" role="status" aria-live="polite" aria-label={`Đang tải ${title}`} />}>
        <Plot data={data} layout={plotLayout} config={plotConfig} style={{ width: '100%', height }} useResizeHandler onClick={onClick} />
      </Suspense>
    </div>
    {children && <details className="chart-table"><summary>Xem bảng tóm tắt</summary>{children}</details>}
  </figure>
}
