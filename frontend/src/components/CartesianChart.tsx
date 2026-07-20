import { lazy, Suspense } from 'react'
import type { ReactNode } from 'react'
import type { Config, Data, Layout } from 'plotly.js'

const Plot = lazy(async () => {
  const [{ default: factory }, { default: plotly }] = await Promise.all([
    import('react-plotly.js/factory'),
    import('plotly.js/dist/plotly-cartesian'),
  ])
  return { default: factory(plotly) }
})

type Props = {
  title: string
  summary: string
  data: Data[]
  layout?: Partial<Layout>
  height?: number
  children?: ReactNode
  onClick?: (event: { points?: Array<{ pointIndex?: number | number[]; pointNumber?: number | number[]; x?: unknown; y?: unknown; customdata?: unknown }> }) => void
  className?: string
}

/** Biểu đồ 2D dùng bundle Plotly Cartesian, tách khỏi bundle bản đồ địa lý. */
export function CartesianChart({ title, summary, data, layout = {}, height = 360, children, onClick, className }: Props) {
  const baseLayout: Partial<Layout> = {
    autosize: true,
    paper_bgcolor: 'rgba(0,0,0,0)',
    plot_bgcolor: 'rgba(0,0,0,0)',
    margin: { t: 28, r: 44, b: 62, l: 160 },
    font: { color: '#22201d' },
    hoverlabel: { bgcolor: '#2b2824', font: { color: '#fffdf8' } },
    xaxis: { automargin: true, gridcolor: '#e7dfd3', zerolinecolor: '#bcae9e' },
    yaxis: { automargin: true, gridcolor: '#e7dfd3', zerolinecolor: '#bcae9e' },
    ...layout,
  }
  const config: Partial<Config> = { displayModeBar: false, responsive: true }
  return <figure className={`cartesian-chart${className ? ` ${className}` : ''}`} aria-label={title}>
    <figcaption><strong>{title}</strong><p>{summary}</p></figcaption>
    <div role="img" aria-label={`${title}. ${summary}`}>
      <Suspense fallback={<div className="chart-fallback" role="status" aria-live="polite" aria-label={`Đang tải ${title}`} />}>
        <Plot data={data} layout={baseLayout} config={config} style={{ width: '100%', height }} useResizeHandler onClick={onClick} />
      </Suspense>
    </div>
    {children && <details className="chart-table"><summary>Xem bảng tóm tắt</summary>{children}</details>}
  </figure>
}
