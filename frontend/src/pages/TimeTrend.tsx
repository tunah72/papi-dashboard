import { useEffect } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Link, useSearchParams } from 'react-router-dom'
import type { Data } from 'plotly.js'
import { api, type Scale } from '../api/client'
import { CartesianChart } from '../components/CartesianChart'

const fmt = new Intl.NumberFormat('vi-VN', { maximumFractionDigits: 2 })
const scaleOf = (value: string | null): Scale => value === 'eight' ? 'eight' : 'six'
function axisLabel(value: string) { const words = value.split(' '); const lines: string[] = []; let line = ''; for (const word of words) { if (`${line} ${word}`.trim().length > 18 && line) { lines.push(line); line = word } else line = `${line} ${word}`.trim() } if (line) lines.push(line); return lines.join('<br>') }

function rangeFor(years: number[], rawFrom: number, rawTo: number, startAtFirst = false) {
  const fallbackTo = years.includes(rawTo) ? rawTo : (years.at(-1) ?? 2024)
  const validFrom = years.includes(rawFrom) && rawFrom < fallbackTo ? rawFrom : undefined
  if (validFrom) return { from: validFrom, to: fallbackTo }
  if (startAtFirst && (years[0] ?? fallbackTo) < fallbackTo) return { from: years[0]!, to: fallbackTo }
  const before = years.filter((year) => year < fallbackTo).at(-1)
  if (before) return { from: before, to: fallbackTo }
  return { from: years[0] ?? 2011, to: years[1] ?? 2012 }
}

function Meta({ source, unit, nLabel, caveats = [] }: { source: string; unit: string; nLabel: string; caveats?: string[] }) {
  return <footer className="meta"><span>Nguồn: {source}</span><span>Đơn vị: {unit}</span><span>Phạm vi: {nLabel}</span>{caveats.map((note) => <small key={note}>{note}</small>)}</footer>
}

function Loading() { return <section className="loading" role="status" aria-live="polite" aria-label="Đang tải diễn biến"><div/><div/><div/><div/></section> }

export function TimeTrend() {
  const [params, setParams] = useSearchParams()
  const scale = scaleOf(params.get('scale'))
  const metadata = useQuery({ queryKey: ['metadata'], queryFn: api.metadata })
  const available = metadata.data?.data.scales.find((item) => item.id === scale)
  const years = available?.years ?? []
  const hasExplicitTo = params.has('to')
  const toAlias = Number(params.get('to') ?? params.get('year'))
  const { from, to } = rangeFor(years, Number(params.get('from')), toAlias, !hasExplicitTo && params.has('year'))
  const provinceContext = params.get('province') ?? ''
  const requestedDimension = params.get('dimension') ?? ''
  useEffect(() => {
    if (!available || from >= to) return
    const canonical = { scale, from: String(from), to: String(to), ...(requestedDimension ? { dimension: requestedDimension } : {}), ...(provinceContext ? { province: provinceContext } : {}) }
    if (params.toString() !== new URLSearchParams(canonical).toString()) setParams(canonical, { replace: true })
  }, [available, from, params, provinceContext, requestedDimension, scale, setParams, to])
  const trend = useQuery({ queryKey: ['trends', scale, from, to], queryFn: () => api.trends(scale, from, to), enabled: Boolean(available && from < to) })
  const dimensions = trend.data?.data.dimensionDeltas.rows.map((row) => row.code) ?? []
  const selected = dimensions.includes(requestedDimension) ? requestedDimension : (dimensions[0] ?? '')
  useEffect(() => {
    if (selected && selected !== requestedDimension) setParams({ scale, from: String(from), to: String(to), dimension: selected, ...(provinceContext ? { province: provinceContext } : {}) }, { replace: true })
  }, [from, provinceContext, requestedDimension, scale, selected, setParams, to])
  const update = (next: Partial<Record<'scale' | 'from' | 'to' | 'dimension', string>>) => setParams({ scale, from: String(from), to: String(to), ...(selected ? { dimension: selected } : {}), ...(provinceContext ? { province: provinceContext } : {}), ...next })

  if (metadata.isLoading || trend.isLoading) return <Loading />
  const fault = metadata.error ?? trend.error
  if (fault) return <section className="state state-error" role="alert"><h1>Không tải được diễn biến</h1><p>{fault.message}</p><p>Hãy kiểm tra FastAPI local rồi thử lại.</p><button onClick={() => { void metadata.refetch(); void trend.refetch() }}>Thử lại</button></section>
  if (!available || !trend.data || !trend.data.data.totalSeries.rows.length) return <section className="state"><h1>Chưa có diễn biến phù hợp</h1><p>Hãy chọn khoảng năm có dữ liệu.</p><button onClick={() => update({ scale: 'six' })}>Đặt lại bộ lọc</button></section>

  const d = trend.data.data
  const selectedSeries = d.dimensionSeries.rows.filter((row) => row.code === selected)
  const selectedLabel = selectedSeries[0]?.label ?? 'Lĩnh vực'
  const labels = [...new Set(d.heatmap.rows.map((row) => row.label))]
  const heatYears = [...new Set(d.heatmap.rows.map((row) => row.year))]
  const heatmap: Data = { type: 'heatmap', x: heatYears, y: labels.map(axisLabel), z: labels.map((label) => heatYears.map((year) => d.heatmap.rows.find((row) => row.label === label && row.year === year)?.score ?? null)), colorscale: [[0, '#f5d9c8'], [1, '#a73b25']], colorbar: { title: { text: d.heatmap.unit } }, hovertemplate: '%{y}, %{x}: %{z:.2f}<extra></extra>' }
  const delta: Data = { type: 'bar', orientation: 'h', y: d.dimensionDeltas.rows.map((row) => axisLabel(row.label)), x: d.dimensionDeltas.rows.map((row) => row.delta), marker: { color: '#a73b25' }, hovertemplate: '%{y}: %{x:.2f}<extra></extra>' }
  const covid: Data[] = d.covid.rows.map((row) => ({ type: 'scatter', mode: 'text+lines+markers', x: [row.beforeScore, row.afterScore], y: [row.label, row.label], text: ['', row.change === null ? '—' : `${row.change > 0 ? '+' : ''}${fmt.format(row.change)}`], textposition: 'middle right', name: row.label, line: { color: '#a73b25', width: 3 }, marker: { size: 9 }, hovertemplate: `${row.label}: %{x:.2f}<extra></extra>` }))
  const resetRange = (next: Partial<Record<'from' | 'to', string>>) => rangeFor(years, Number(next.from ?? from), Number(next.to ?? to))
  return <article className="overview analysis-page">
    <p className="eyebrow">Diễn biến theo thời gian</p><h1>Điểm quản trị qua các năm</h1><p className="lede">Mỗi điểm là trung bình của các tỉnh có dữ liệu trong năm; đây là bức tranh toàn quốc.</p>
    <section className="filter-bar" aria-label="Bộ lọc diễn biến"><label>Phạm vi<select value={scale} onChange={(event) => { const next = scaleOf(event.target.value); const nextYears = metadata.data!.data.scales.find((item) => item.id === next)!.years; const nextRange = rangeFor(nextYears, nextYears[0], nextYears.at(-1) ?? nextYears[0]); setParams({ scale: next, from: String(nextRange.from), to: String(nextRange.to), ...(provinceContext ? { province: provinceContext } : {}) }) }}><option value="six">Tổng 6 lĩnh vực gốc</option><option value="eight">Tổng PAPI (8 lĩnh vực)</option></select></label><label>Từ năm<select value={from} onChange={(event) => { const nextRange = resetRange({ from: event.target.value }); update({ from: String(nextRange.from), to: String(nextRange.to) }) }}>{years.filter((year) => year < to).map((year) => <option key={year} value={year}>{year}</option>)}</select></label><label>Đến năm<select value={to} onChange={(event) => { const nextRange = resetRange({ to: event.target.value }); update({ from: String(nextRange.from), to: String(nextRange.to) }) }}>{years.filter((year) => year > from).map((year) => <option key={year} value={year}>{year}</option>)}</select></label></section>
    <section className="kpis" aria-label="Chỉ số tóm tắt"><Metric label="Điểm đầu kỳ" value={d.summary.vFirst}/><Metric label="Điểm cuối kỳ" value={d.summary.vLatest}/><Metric label="Thay đổi ròng" value={d.summary.net}/><Metric label="Đỉnh chuỗi" value={d.summary.peakValue} detail={d.summary.peakYear ? String(d.summary.peakYear) : undefined}/></section>
    <section className="map-surface"><h2>Xu hướng tổng thể</h2><CartesianChart title="Đường điểm tổng theo năm" summary={`Điểm tổng thay đổi từ ${fmt.format(d.summary.vFirst ?? 0)} đến ${fmt.format(d.summary.vLatest ?? 0)} trong giai đoạn ${from}–${to}.`} data={[{ type: 'scatter', mode: 'lines+markers', x: d.totalSeries.rows.map((row) => row.year), y: d.totalSeries.rows.map((row) => row.score), line: { color: '#a73b25', width: 3 }, hovertemplate: '%{x}: %{y:.2f}<extra></extra>' }]} layout={{ xaxis: { title: { text: 'Năm' }, automargin: true }, yaxis: { title: { text: d.totalSeries.unit }, automargin: true } }}><TrendTable rows={d.totalSeries.rows.map((row) => [String(row.year), fmt.format(row.score ?? 0)])}/></CartesianChart><Meta source={d.totalSeries.source} unit={d.totalSeries.unit} nLabel={`${d.totalSeries.rowCount} mốc năm; ${trend.data.meta.n} quan sát tỉnh–năm`} caveats={d.totalSeries.caveats}/></section>
    <section className="analysis-grid"><section className="map-surface"><h2>Thay đổi theo lĩnh vực</h2><div className="dimension-list">{d.dimensionDeltas.rows.map((row) => <button key={row.code} className={selected === row.code ? 'selected' : ''} onClick={() => update({ dimension: row.code })}>{row.label}<strong>{row.delta === null ? '—' : `${row.delta > 0 ? '+' : ''}${fmt.format(row.delta)}`}</strong></button>)}</div><CartesianChart title="Biểu đồ cột thay đổi lĩnh vực" summary="Các cột thể hiện chênh lệch điểm giữa đầu và cuối khoảng năm đã chọn." data={[delta]} layout={{ xaxis: { title: { text: d.dimensionDeltas.unit }, automargin: true }, yaxis: { automargin: true } }} /><Meta source={d.dimensionDeltas.source} unit={d.dimensionDeltas.unit} nLabel={`${d.dimensionDeltas.rowCount} lĩnh vực`} caveats={d.dimensionDeltas.caveats}/></section><section className="map-surface"><h2>{selectedLabel}</h2><CartesianChart title={`Đường điểm ${selectedLabel}`} summary={`Chuỗi điểm của lĩnh vực ${selectedLabel} theo năm.`} data={[{ type: 'scatter', mode: 'lines+markers', x: selectedSeries.map((row) => row.year), y: selectedSeries.map((row) => row.score), line: { color: '#a73b25' }, hovertemplate: '%{x}: %{y:.2f}<extra></extra>' }]} layout={{ xaxis: { title: { text: 'Năm' }, automargin: true }, yaxis: { title: { text: d.dimensionSeries.unit }, automargin: true } }} /><Meta source={d.dimensionSeries.source} unit={d.dimensionSeries.unit} nLabel={`${selectedSeries.length} mốc năm của lĩnh vực đang chọn`} caveats={d.dimensionSeries.caveats}/></section></section>
    <section className="map-surface"><h2>Toàn cảnh lĩnh vực theo năm</h2><CartesianChart title="Bản nhiệt điểm theo lĩnh vực và năm" summary="Màu đậm hơn biểu thị điểm cao hơn; bảng tóm tắt có số điểm theo từng lĩnh vực và năm." data={[heatmap]} layout={{ xaxis: { title: { text: 'Năm' }, automargin: true }, yaxis: { title: { text: 'Lĩnh vực' }, automargin: true } }}><TrendTable rows={d.heatmap.rows.map((row) => [`${row.label} · ${row.year}`, fmt.format(row.score ?? 0)])}/></CartesianChart><Meta source={d.heatmap.source} unit={d.heatmap.unit} nLabel={`${d.heatmap.rowCount} giá trị lĩnh vực–năm`} caveats={d.heatmap.caveats}/></section>
    <section className="map-surface"><h2>Trước và sau COVID-19</h2>{d.covid.available ? <><CartesianChart title="So sánh điểm trước và sau COVID-19" summary="Mỗi đoạn nối hai mốc; nhãn ở đầu phải là mức chênh lệch điểm." data={covid} layout={{ xaxis: { title: { text: d.covid.unit }, automargin: true }, yaxis: { automargin: true } }} /><Meta source={d.covid.source} unit={d.covid.unit} nLabel={`${d.covid.rowCount} lĩnh vực có cặp so sánh`} caveats={d.covid.caveats}/></> : <p>Khoảng năm này chưa đủ hai mốc để so sánh trước và sau COVID-19.</p>}</section>
    <section className="story"><h2>Xem theo vùng và tỉnh</h2><p>Giữ lại phạm vi và năm cuối kỳ để so sánh không gian.</p><Link className="cta" to={`/provincial?scale=${scale}&year=${to}${provinceContext ? `&province=${encodeURIComponent(provinceContext)}` : ''}`}>Mở Vùng & tỉnh</Link></section>
  </article>
}

function TrendTable({ rows }: { rows: string[][] }) { return <table><thead><tr><th>Mốc</th><th>Điểm</th></tr></thead><tbody>{rows.map(([label, value]) => <tr key={label}><th>{label}</th><td>{value}</td></tr>)}</tbody></table> }
function Metric({ label, value, detail }: { label: string; value: number | null; detail?: string }) { return <div className="kpi"><p>{label}</p><strong>{value === null ? '—' : fmt.format(value)}</strong>{detail && <small>{detail}</small>}</div> }
