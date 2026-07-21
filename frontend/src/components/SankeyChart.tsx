import { lazy, Suspense, type ReactNode } from 'react'
import type { Config, Data, Layout } from 'plotly.js'
import { basePlotLayout } from '../theme/chartTheme'

const Plot = lazy(async () => {
  const [{ default: factory }, { default: plotly }, { default: sankey }] = await Promise.all([
    import('react-plotly.js/factory'),
    import('plotly.js/lib/core'),
    import('plotly.js/lib/sankey'),
  ])
  plotly.register(sankey)
  return { default: factory(plotly) }
})

type PlotEvent = {
  points?: Array<{ pointIndex?: number; pointNumber?: number; customdata?: unknown }>
}

type Props = {
  title: string
  summary: string
  data: Data[]
  layout?: Partial<Layout>
  height?: number
  children?: ReactNode
  onClick?: (event: PlotEvent) => void
  onHover?: (event: PlotEvent) => void
  onUnhover?: () => void
  config?: Partial<Config>
}

/** Sankey được lazy-load riêng để không đưa trace flow vào bundle Cartesian của các trang khác. */
export function SankeyChart({ title, summary, data, layout = {}, height = 360, children, onClick, onHover, onUnhover, config }: Props) {
  const plotConfig: Partial<Config> = { displayModeBar: false, responsive: true, showTips: false, ...config }
  return <figure className="cartesian-chart sankey-chart" aria-label={title}>
    <figcaption><strong>{title}</strong><p>{summary}</p></figcaption>
    <div role="img" aria-label={`${title}. ${summary}`}>
      <Suspense fallback={<div className="chart-fallback" role="status" aria-live="polite" aria-label={`Đang tải ${title}`} />}>
        <Plot data={data} layout={{ ...basePlotLayout, ...layout }} config={plotConfig} style={{ width: '100%', height }} useResizeHandler onClick={onClick} onHover={onHover} onUnhover={onUnhover} />
      </Suspense>
    </div>
    {children && <details className="chart-table"><summary>Xem bảng tóm tắt</summary>{children}</details>}
  </figure>
}
