import { useEffect, useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import type { Data } from 'plotly.js'
import { Link, useSearchParams } from 'react-router-dom'

import { api, type Scale, type TrendsResponse } from '../api/client'
import { CartesianChart } from '../components/CartesianChart'
import { ChartCard, ChartInsight, ChartMeta, DashboardPageHeader, EmptyState, ErrorState, FilterBar, KpiCard, KpiGrid, LoadingSkeleton } from '../components/dashboard'
import { colorForDimension, colorForRegion, divergingScale, shortRegionLabel as fallbackRegionLabel, uiColors } from '../theme/chartTheme'

const number = new Intl.NumberFormat('vi-VN', { maximumFractionDigits: 2 })
const signed = new Intl.NumberFormat('vi-VN', { maximumFractionDigits: 2, signDisplay: 'exceptZero' })
const scaleOf = (raw: string | null): Scale => raw === 'eight' ? 'eight' : 'six'
const focusIds = new Set(['time-series', 'time-regional-yoy', 'time-regional-ranks', 'time-dimensions'])
const compactRegions: Record<string, string> = {
  'Trung du và miền núi phía Bắc': 'TDMNPB',
  'Đồng bằng sông Hồng': 'ĐBSH',
  'Bắc Trung Bộ và Duyên hải miền Trung': 'BTB & DHMT',
  'Tây Nguyên': 'Tây Nguyên',
  'Đông Nam Bộ': 'Đông Nam Bộ',
  'Đồng bằng sông Cửu Long': 'ĐBSCL',
}
const shortRegionLabel = (region: string) => compactRegions[region] ?? fallbackRegionLabel(region)
type TrendData = TrendsResponse['data']

function validRange(years: number[], rawFrom: number, rawTo: number) {
  const to = years.includes(rawTo) ? rawTo : years.at(-1) ?? 2024
  const from = years.includes(rawFrom) && rawFrom < to ? rawFrom : years[0] ?? 2011
  return { from, to: from < to ? to : (years.find((year) => year > from) ?? from + 1) }
}

function TrendTable({ data }: { data: TrendData }) {
  return <table><caption className="sr-only">Điểm PAPI trung bình theo năm</caption><thead><tr><th>Năm</th><th>Toàn quốc</th><th>Số tỉnh</th></tr></thead><tbody>{data.totalSeries.rows.map((row) => <tr key={row.year}><th scope="row">{row.year}</th><td>{row.score === null ? '—' : number.format(row.score)}</td><td>{row.contributorN}</td></tr>)}</tbody></table>
}

export function TimeTrend() {
  const [params, setParams] = useSearchParams()
  const [hoveredRegion, setHoveredRegion] = useState<string | null>(null)
  const [showValues, setShowValues] = useState(false)
  const [sortByDelta, setSortByDelta] = useState(true)
  const metadata = useQuery({ queryKey: ['metadata'], queryFn: api.metadata })
  const scale = scaleOf(params.get('scale'))
  const availability = metadata.data?.data.scales.find((item) => item.id === scale)
  const range = validRange(availability?.years ?? [], Number(params.get('from')), Number(params.get('to') ?? params.get('year')))
  const province = params.get('province') ?? ''
  const provinceRecord = metadata.data?.data.provinces.find((item) => item.provinceVi === province)
  const region = params.get('region') ?? provinceRecord?.region ?? ''
  const focused = focusIds.has(params.get('focus') ?? '') ? params.get('focus') : null
  const trend = useQuery({ queryKey: ['trends', scale, range.from, range.to, region, province], queryFn: () => api.trends(scale, range.from, range.to, region || undefined, province || undefined), enabled: Boolean(availability && range.from < range.to) })

  const update = (changes: Record<string, string | null>, replace = false) => setParams((current) => {
    const next = new URLSearchParams(current)
    Object.entries(changes).forEach(([key, value]) => value === null ? next.delete(key) : next.set(key, value))
    return next
  }, { replace })
  useEffect(() => {
    if (!availability) return
    const invalidFocus = params.has('focus') && !focusIds.has(params.get('focus') ?? '')
    if (params.get('scale') !== scale || params.get('from') !== String(range.from) || params.get('to') !== String(range.to) || params.has('year') || invalidFocus) update({ scale, from: String(range.from), to: String(range.to), year: null, ...(invalidFocus ? { focus: null } : {}) }, true)
  }, [availability, params, range.from, range.to, scale]) // eslint-disable-line react-hooks/exhaustive-deps

  const reset = () => setParams({ scale: 'six', from: '2011', to: '2024' })
  if (metadata.isLoading || trend.isLoading) return <LoadingSkeleton label="Đang tải diễn biến" />
  const error = metadata.error ?? trend.error
  if (error) return <ErrorState title="Không tải được diễn biến" description={`${error.message} Hãy kiểm tra FastAPI local rồi thử lại.`} action={<button onClick={() => { void metadata.refetch(); void trend.refetch() }}>Thử lại</button>} />
  if (!availability || !trend.data || !trend.data.data.totalSeries.rows.length) return <EmptyState title="Chưa có diễn biến phù hợp" description="Hãy chọn khoảng năm có dữ liệu." action={<button onClick={reset}>Đặt lại bộ lọc</button>} />

  const d = trend.data.data
  const years = d.totalSeries.rows.map((row) => row.year)
  const regions = [...new Set(d.regionalSeries.rows.map((row) => row.region))]
  const focus = (id: string) => ({ id, activeContext: province || region || undefined, open: focused === id, onOpenChange: (open: boolean) => update({ focus: open ? id : null }) })
  const lineData: Data[] = [
    ...regions.map((name): Data => {
      const rows = d.regionalSeries.rows.filter((row) => row.region === name)
      const active = hoveredRegion === null || hoveredRegion === name || region === name
      return { type: 'scatter', mode: 'lines', name: shortRegionLabel(name), x: rows.map((row) => row.year), y: rows.map((row) => row.score), customdata: rows.map((row) => row.contributorN), line: { color: colorForRegion(name), width: hoveredRegion === name || region === name ? 2.6 : 1.5 }, opacity: active ? 0.9 : 0.28, hovertemplate: `<b>${name}</b><br>%{x}: %{y:.2f}<br>n = %{customdata} tỉnh<extra></extra>` }
    }),
    { type: 'scatter', mode: 'text+lines+markers', name: 'Toàn quốc', x: years, y: d.totalSeries.rows.map((row) => row.score), text: d.totalSeries.rows.map((row, index) => index === years.length - 1 ? ` ${number.format(row.score ?? 0)}` : ''), textposition: 'middle right', customdata: d.totalSeries.rows.map((row) => row.contributorN), line: { color: uiColors.ink, width: 3.4 }, marker: { color: uiColors.surface, line: { color: uiColors.ink, width: 2 }, size: 7 }, hovertemplate: '<b>Toàn quốc</b><br>%{x}: %{y:.2f}<br>n = %{customdata} tỉnh<extra></extra>' },
    ...(d.selectedSeries.rows.length ? [{ type: 'scatter', mode: 'lines+markers', name: province || region, x: d.selectedSeries.rows.map((row) => row.year), y: d.selectedSeries.rows.map((row) => row.score), line: { color: province ? uiColors.warning : uiColors.primary, width: 3 }, marker: { symbol: province ? 'diamond' : 'circle', size: 8 }, hovertemplate: `<b>${province || region}</b><br>%{x}: %{y:.2f}<extra></extra>` } as Data] : []),
  ]
  const yoyYears = [...new Set(d.regionalYearOverYear.rows.map((row) => row.year))]
  const yoy: Data = { type: 'heatmap', x: yoyYears, y: regions.map(shortRegionLabel), z: regions.map((name) => yoyYears.map((year) => d.regionalYearOverYear.rows.find((row) => row.region === name && row.year === year)?.change ?? null)), text: regions.map((name) => yoyYears.map((year) => { const value = d.regionalYearOverYear.rows.find((row) => row.region === name && row.year === year)?.change; return value == null ? '' : signed.format(value) })), texttemplate: showValues ? '%{text}' : '', customdata: regions.map((name) => yoyYears.map((year) => { const row = d.regionalYearOverYear.rows.find((item) => item.region === name && item.year === year); return [name, row?.previousScore, row?.score, row?.contributorN] })), colorscale: divergingScale, zmid: 0, hovertemplate: '<b>%{customdata[0]}</b><br>%{x}: %{customdata[1]:.2f} → %{customdata[2]:.2f}<br>Thay đổi %{z:+.2f}<br>n = %{customdata[3]} tỉnh<extra></extra>' } as unknown as Data
  const rankData: Data[] = regions.map((name): Data => { const rows = d.regionalRanks.rows.filter((row) => row.region === name); const active = hoveredRegion === null || hoveredRegion === name || region === name; return { type: 'scatter', mode: 'text+lines+markers', name: shortRegionLabel(name), x: rows.map((row) => row.year), y: rows.map((row) => row.rank), text: rows.map((_, i) => i === rows.length - 1 ? shortRegionLabel(name) : ''), textposition: 'middle right', line: { color: colorForRegion(name), width: hoveredRegion === name || region === name ? 3 : 1.8 }, marker: { size: 7 }, opacity: active ? 1 : 0.26, customdata: rows.map((row) => [row.score, row.contributorN]), hovertemplate: `<b>${name}</b><br>%{x}: hạng %{y}<br>Điểm %{customdata[0]:.2f}<br>n = %{customdata[1]} tỉnh<extra></extra>` } })
  const dims = [...d.dimensionDeltas.rows].sort((a, b) => sortByDelta ? (b.delta ?? 0) - (a.delta ?? 0) : (b.toScore ?? 0) - (a.toScore ?? 0))
  const slopeData: Data[] = dims.map((row): Data => ({ type: 'scatter', mode: 'text+lines+markers', name: row.label, x: [range.from, range.to], y: [row.fromScore, row.toScore], text: ['', `${row.code} ${signed.format(row.delta ?? 0)}`], textposition: 'middle right', line: { color: colorForDimension(row.code), width: 2.3 }, marker: { size: 8 }, customdata: [[row.label, row.delta, row.contributorNFrom], [row.label, row.delta, row.contributorNTo]], hovertemplate: '<b>%{customdata[0]}</b><br>%{x}: %{y:.2f}<br>Thay đổi: %{customdata[1]:+.2f}<br>n = %{customdata[2]} tỉnh<extra></extra>' }))
  const turning = d.turningPoints.rows[0]
  const defaultRange = scale === 'six' && range.from === 2011 && range.to === 2024 && !province && !region && !focused

  return <article className="overview analysis-page time-redesign">
    <DashboardPageHeader eyebrow="DIỄN BIẾN" title="Điểm quản trị thay đổi khi nào?" description="Theo dõi mặt bằng điểm, nhịp vùng, thứ tự tương đối và lĩnh vực tạo khác biệt đầu–cuối." />
    <FilterBar label="Bộ lọc diễn biến" summary={`Đang xem: ${scale === 'six' ? '6 lĩnh vực' : '8 lĩnh vực'} · ${range.from}–${range.to} · ${province || region || 'Toàn quốc'}`} onReset={reset} resetDisabled={defaultRange}>
      <label>Phạm vi so sánh<select value={scale} onChange={(event) => { const next = scaleOf(event.target.value); const nextYears = metadata.data!.data.scales.find((item) => item.id === next)!.years; setParams({ scale: next, from: String(nextYears[0]), to: String(nextYears.at(-1)), ...(province ? { province } : {}), ...(region && !province ? { region } : {}) }) }}><option value="six">6 lĩnh vực gốc</option><option value="eight">8 lĩnh vực</option></select></label>
      <label>Từ năm<select value={range.from} onChange={(event) => update({ from: event.target.value })}>{availability.years.filter((year) => year < range.to).map((year) => <option key={year}>{year}</option>)}</select></label>
      <label>Đến năm<select value={range.to} onChange={(event) => update({ to: event.target.value })}>{availability.years.filter((year) => year > range.from).map((year) => <option key={year}>{year}</option>)}</select></label>
    </FilterBar>
    <KpiGrid>
      <KpiCard label="Điểm đầu → cuối" value={`${number.format(d.summary.vFirst ?? 0)} → ${number.format(d.summary.vLatest ?? 0)}`} detail={`${range.from} → ${range.to}`} />
      <KpiCard label="Mức thay đổi trong giai đoạn" value={d.summary.net === null ? '—' : `${(d.summary.net ?? 0) >= 0 ? 'Tăng ' : 'Giảm '}${signed.format(Math.abs(d.summary.net ?? 0))}`} detail={d.measure.unit} tone={(d.summary.net ?? 0) >= 0 ? 'positive' : 'negative'} />
      <KpiCard label="Năm biến động mạnh nhất" value={turning ? String(turning.year) : '—'} detail={turning ? `${signed.format(turning.change ?? 0)} so với năm trước` : 'Không đủ mốc'} />
      <KpiCard label="Mức cao nhất" value={d.summary.peakValue === null ? '—' : number.format(d.summary.peakValue)} detail={d.summary.peakYear ? `Năm ${d.summary.peakYear}` : 'Không đủ dữ liệu'} />
    </KpiGrid>
    <section className="time-chart-grid" aria-label="Bốn biểu đồ diễn biến">
      <ChartCard className="time-chart-card" eyebrow="01 · MỨC ĐIỂM" title="Điểm trung bình các tỉnh tăng, giảm hay ổn định?" insight={<ChartInsight>{d.insights.total}</ChartInsight>} focus={{ ...focus('time-series'), content: <CartesianChart title="Mức điểm theo thời gian" summary="Điểm trung bình theo năm của toàn quốc và sáu vùng." data={lineData} height={560} onHover={(event) => setHoveredRegion(regions[event.points?.[0]?.curveNumber ?? -1] ?? null)} onUnhover={() => setHoveredRegion(null)} layout={{ hovermode: 'x unified', xaxis: { title: { text: 'Năm' }, showspikes: true, spikemode: 'across', spikesnap: 'cursor' }, yaxis: { title: { text: d.totalSeries.unit } }, legend: { orientation: 'h', y: 1.12 }, margin: { l: 64, r: 42, t: 38, b: 50 } }}><TrendTable data={d} /></CartesianChart> }} footer={<ChartMeta source={d.totalSeries.source} unit={d.totalSeries.unit} n={`${trend.data.meta.n} tỉnh–năm`} caveats={d.totalSeries.caveats} />}>
        <CartesianChart title="Mức điểm theo thời gian" summary="Điểm trung bình theo năm của toàn quốc và sáu vùng." data={lineData} height={310} onHover={(event) => setHoveredRegion(regions[event.points?.[0]?.curveNumber ?? -1] ?? null)} onUnhover={() => setHoveredRegion(null)} layout={{ hovermode: 'x unified', xaxis: { title: { text: 'Năm' }, showspikes: true, spikemode: 'across', spikesnap: 'cursor' }, yaxis: { title: { text: d.totalSeries.unit } }, legend: { orientation: 'h', y: -0.22 }, margin: { l: 64, r: 32, t: 20, b: 86 } }}><TrendTable data={d} /></CartesianChart>
      </ChartCard>
      <ChartCard className="time-chart-card" eyebrow="02 · NHỊP THAY ĐỔI" title="Năm nào nhiều vùng cùng tăng hoặc cùng giảm?" action={<label className="chart-toggle"><input type="checkbox" checked={showValues} onChange={(event) => setShowValues(event.target.checked)} />Hiện số</label>} insight={<ChartInsight>{d.insights.regionalYearOverYear}</ChartInsight>} focus={{ ...focus('time-regional-yoy'), content: <CartesianChart title="Thay đổi năm-kề-năm theo vùng" summary="Mức thay đổi điểm của từng vùng so với năm liền trước." data={[yoy]} height={560} layout={{ xaxis: { title: { text: 'Năm' } }, yaxis: { automargin: true }, margin: { l: 120, r: 42, t: 30, b: 52 } }} /> }} footer={<ChartMeta source={d.regionalYearOverYear.source} unit={d.regionalYearOverYear.unit} n={`${d.regionalYearOverYear.rowCount} vùng–năm`} caveats={d.regionalYearOverYear.caveats} />}>
        <CartesianChart title="Thay đổi năm-kề-năm theo vùng" summary="Mỗi ô là điểm năm hiện tại trừ năm trước." data={[yoy]} height={310} onClick={(event) => { const point = event.points?.[0]; const name = Array.isArray(point?.customdata) ? point.customdata[0] : null; if (typeof name === 'string' && typeof point?.x === 'number') update({ region: name, year: String(point.x) }) }} layout={{ xaxis: { title: { text: 'Năm' } }, yaxis: { automargin: true }, margin: { l: 120, r: 32, t: 16, b: 48 } }} />
      </ChartCard>
      <ChartCard className="time-chart-card" eyebrow="03 · THỨ TỰ VÙNG" title="Thứ tự sáu vùng thay đổi ra sao?" insight={<ChartInsight>{d.insights.regionalRank}</ChartInsight>} focus={{ ...focus('time-regional-ranks'), content: <CartesianChart title="Bump chart thứ hạng vùng" summary="Thứ hạng điểm trung bình của sáu vùng theo năm." data={rankData} height={560} onHover={(event) => setHoveredRegion(regions[event.points?.[0]?.curveNumber ?? -1] ?? null)} onUnhover={() => setHoveredRegion(null)} layout={{ xaxis: { title: { text: 'Năm' } }, yaxis: { title: { text: 'Hạng vùng' }, autorange: 'reversed', dtick: 1 }, showlegend: false, margin: { l: 68, r: 100, t: 32, b: 48 } }} /> }} footer={<ChartMeta source={d.regionalRanks.source} unit={d.regionalRanks.unit} n={`${d.regionalRanks.rowCount} vùng–năm`} caveats={d.regionalRanks.caveats} />}>
        <CartesianChart title="Bump chart thứ hạng vùng" summary="Thứ hạng tương đối không cho biết khoảng cách điểm." data={rankData} height={310} onHover={(event) => setHoveredRegion(regions[event.points?.[0]?.curveNumber ?? -1] ?? null)} onUnhover={() => setHoveredRegion(null)} layout={{ xaxis: { title: { text: 'Năm' } }, yaxis: { title: { text: 'Hạng vùng' }, autorange: 'reversed', dtick: 1 }, showlegend: false, margin: { l: 68, r: 82, t: 22, b: 48 } }} />
      </ChartCard>
      <ChartCard className="time-chart-card" eyebrow="04 · LĨNH VỰC" title="Lĩnh vực nào cải thiện hoặc suy giảm mạnh nhất?" action={<button type="button" className="chart-sort" onClick={() => setSortByDelta((value) => !value)}>Sắp theo: {sortByDelta ? 'thay đổi' : 'điểm cuối'}</button>} insight={<ChartInsight>{d.insights.dimensions}</ChartInsight>} focus={{ ...focus('time-dimensions'), content: <CartesianChart title="Slopegraph thay đổi theo lĩnh vực" summary={`Điểm trung bình từng lĩnh vực ở hai mốc ${range.from} và ${range.to}.`} data={slopeData} height={560} layout={{ xaxis: { tickmode: 'array', tickvals: [range.from, range.to], title: { text: 'Mốc so sánh' } }, yaxis: { title: { text: 'Điểm lĩnh vực PAPI' } }, showlegend: false, margin: { l: 62, r: 125, t: 32, b: 48 } }} /> }} footer={<ChartMeta source={d.dimensionDeltas.source} unit={d.dimensionDeltas.unit} n={`${d.dimensionDeltas.rowCount} lĩnh vực`} caveats={d.dimensionDeltas.caveats} />}>
        <CartesianChart title="Slopegraph thay đổi theo lĩnh vực" summary={`Điểm đầu và cuối trong giai đoạn ${range.from}–${range.to}.`} data={slopeData} height={310} onClick={(event) => { const code = dims[event.points?.[0]?.curveNumber ?? -1]?.code; if (code) update({ dimension: code }) }} layout={{ xaxis: { tickmode: 'array', tickvals: [range.from, range.to], title: { text: 'Mốc so sánh' } }, yaxis: { title: { text: 'Điểm lĩnh vực PAPI' } }, showlegend: false, margin: { l: 62, r: 98, t: 18, b: 48 } }} />
      </ChartCard>
    </section>
    <section className="story"><p className="eyebrow">Bước đọc tiếp</p><h2>Xem khác biệt theo vùng và tỉnh</h2><p>Giữ phạm vi và năm cuối kỳ để chuyển từ thời gian sang không gian.</p><Link className="cta" to={`/provincial?scale=${scale}&year=${range.to}${province ? `&province=${encodeURIComponent(province)}` : ''}`}>Mở Vùng & tỉnh</Link></section>
  </article>
}
