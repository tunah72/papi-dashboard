import { lazy, Suspense } from 'react'

import type { GeojsonResponse } from '../../api/client'
import { sequentialScale, uiColors } from '../../theme/chartTheme'

const Plot = lazy(async () => {
  const [{ default: createPlotlyComponent }, { default: Plotly }] = await Promise.all([
    import('react-plotly.js/factory'),
    import('plotly.js-geo-dist-min'),
  ])
  return { default: createPlotlyComponent(Plotly) }
})

type ProvinceMapRow = {
  provinceId: number
  provinceVi: string
  region: string
  score: number | null
}

type ProvinceMapProps = {
  title: string
  summary: string
  rows: ProvinceMapRow[]
  geojson: GeojsonResponse['data']['geojson']
  selectedId: number
  unit: string
  onSelect: (provinceId: number) => void
  height?: number
}

export function ProvinceMap({ title, summary, rows, geojson, selectedId, unit, onSelect, height = 500 }: ProvinceMapProps) {
  const selected = rows.find((row) => row.provinceId === selectedId)
  const traces = [
    {
      type: 'choropleth' as const,
      geojson,
      featureidkey: 'properties.province_id',
      locations: rows.map((row) => row.provinceId),
      customdata: rows.map((row) => row.provinceId),
      z: rows.map((row) => row.score),
      text: rows.map((row) => `${row.provinceVi} · ${row.region}`),
      hovertemplate: `%{text}<br><b>%{z:.2f} ${unit}</b><extra></extra>`,
      colorscale: sequentialScale,
      marker: { line: { color: '#F8FBFA', width: 0.65 } },
      colorbar: { title: { text: unit }, thickness: 12, outlinewidth: 0 },
    },
    ...(selected ? [{
      type: 'choropleth' as const,
      geojson,
      featureidkey: 'properties.province_id',
      locations: [selected.provinceId],
      z: [selected.score],
      colorscale: [[0, '#EAF3F2'], [1, '#EAF3F2']] as [number, string][],
      showscale: false,
      hoverinfo: 'skip' as const,
      marker: { line: { color: uiColors.ink, width: 3 } },
    }] : []),
  ]

  return <figure className="province-map">
    <div role="img" aria-label={`${title}. ${summary}`}>
    <Suspense fallback={<div className="chart-fallback" aria-label="Đang tải bản đồ" />}>
      <Plot
        data={traces}
        layout={{
          autosize: true,
          paper_bgcolor: 'rgba(0,0,0,0)',
          plot_bgcolor: 'rgba(0,0,0,0)',
          font: { family: '"Be Vietnam Pro", system-ui, sans-serif', color: uiColors.text },
          margin: { t: 4, r: 10, b: 4, l: 10 },
          geo: {
            scope: 'asia',
            fitbounds: 'locations',
            bgcolor: 'rgba(0,0,0,0)',
            showframe: false,
            showcoastlines: false,
            projection: { type: 'mercator' },
          },
        }}
        config={{ displayModeBar: false, responsive: true, showTips: false }}
        style={{ width: '100%', height }}
        onClick={(event) => {
          const id = Number(event.points[0]?.customdata)
          if (Number.isInteger(id)) onSelect(id)
        }}
      />
    </Suspense>
    </div>
    <figcaption className="sr-only">{summary}</figcaption>
  </figure>
}
