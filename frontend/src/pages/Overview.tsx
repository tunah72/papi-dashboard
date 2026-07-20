import { lazy, Suspense, useEffect, useMemo, useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Link, useSearchParams } from 'react-router-dom'
import { api, type Scale } from '../api/client'

const number = new Intl.NumberFormat('vi-VN', { minimumFractionDigits: 1, maximumFractionDigits: 2 })
const Plot = lazy(async () => {
  const [{ default: createPlotlyComponent }, { default: Plotly }] = await Promise.all([import('react-plotly.js/factory'), import('plotly.js-geo-dist-min')])
  return { default: createPlotlyComponent(Plotly) }
})

function validScale(value: string | null): Scale { return value === 'eight' ? 'eight' : 'six' }

function Meta({ source, unit, n, caveats = [] }: { source: string; unit: string; n: number; caveats?: string[] }) {
  return <footer className="meta"><span>Nguồn: {source}</span><span>Đơn vị: {unit}</span><span>n = {n} tỉnh</span>{caveats.map((note) => <small key={note}>{note}</small>)}</footer>
}

function Loading() { return <section aria-label="Đang tải Tổng quan" className="loading"><div /><div /><div /><div /></section> }

export function Overview() {
  const [params, setParams] = useSearchParams()
  const metadata = useQuery({ queryKey: ['metadata'], queryFn: api.metadata })
  const geojson = useQuery({ queryKey: ['geojson'], queryFn: api.geojson })
  const scale = validScale(params.get('scale'))
  const available = metadata.data?.data.scales.find((item) => item.id === scale)
  const requestedYear = Number(params.get('year'))
  const year = available?.years.includes(requestedYear) ? requestedYear : (available?.years.at(-1) ?? 2024)
  const overview = useQuery({ queryKey: ['overview', scale, year], queryFn: () => api.overview(scale, year), enabled: Boolean(available) })
  const [selectedId, setSelectedId] = useState<number | null>(null)
  const [ranking, setRanking] = useState<'top' | 'bottom'>('top')

  useEffect(() => { if (available && (params.get('scale') !== scale || String(year) !== params.get('year'))) setParams((current) => { current.set('scale', scale); current.set('year', String(year)); return current }, { replace: true }) }, [available, params, scale, setParams, year])
  const update = (nextScale: Scale, candidateYear: number) => {
    const nextAvailability = metadata.data?.data.scales.find((item) => item.id === nextScale)
    const nextYear = nextAvailability?.years.includes(candidateYear) ? candidateYear : (nextAvailability?.years.at(-1) ?? candidateYear)
    setParams({ scale: nextScale, year: String(nextYear) })
  }
  const selected = useMemo(() => overview.data?.data.map.rows.find((row) => row.provinceVi === params.get('province')) ?? overview.data?.data.map.rows.find((row) => row.provinceId === selectedId) ?? null, [overview.data, params, selectedId])

  if (metadata.isLoading || overview.isLoading || geojson.isLoading) return <Loading />
  const fault = metadata.error ?? overview.error ?? geojson.error
  if (fault) return <section className="state state-error" role="alert"><p className="eyebrow">Không thể tải Tổng quan</p><h1>FastAPI local chưa phản hồi dữ liệu</h1><p>{fault.message}</p><button onClick={() => { void metadata.refetch(); void geojson.refetch(); void overview.refetch() }}>Thử lại</button><button className="text-button" onClick={() => update('six', 2024)}>Đặt lại bộ lọc</button></section>
  if (!metadata.data || !geojson.data || !overview.data || !available) return <section className="state"><h1>Chưa có dữ liệu để hiển thị</h1><p>Hãy chọn lại phạm vi hoặc năm có dữ liệu.</p><button onClick={() => update('six', 2024)}>Đặt lại bộ lọc</button></section>

  const data = overview.data.data
  const meta = overview.data.meta
  const rows = data.map.rows
  if (!rows.length) return <section className="state"><h1>Không có tỉnh phù hợp</h1><p>Không render biểu đồ từ tập rỗng. Hãy đổi phạm vi hoặc năm.</p><button onClick={() => update('six', 2024)}>Đặt lại bộ lọc</button></section>
  const rankingRows = ranking === 'top' ? data.ranking.top10 : data.ranking.bottom10
  const colorScale: [number, string][] = [[0, '#f5d9c8'], [0.5, '#de7b55'], [1, '#a73b25']]
  const selectedProvince = selected ?? rows[0]
  const selectedOutsideRanking = !rankingRows.some((row) => row.provinceId === selectedProvince.provinceId)
  const chartData = [{ type: 'choropleth' as const, geojson: geojson.data.data.geojson, featureidkey: 'properties.province_id', locations: rows.map((row) => row.provinceId), customdata: rows.map((row) => row.provinceId), z: rows.map((row) => row.score), text: rows.map((row) => `${row.provinceVi}: ${row.score === null ? 'thiếu dữ liệu' : number.format(row.score)}`), hovertemplate: '%{text}<extra></extra>', colorscale: colorScale, marker: { line: { color: '#fffaf2', width: 0.5 } }, colorbar: { title: { text: 'Điểm' } } }, { type: 'choropleth' as const, geojson: geojson.data.data.geojson, featureidkey: 'properties.province_id', locations: [selectedProvince.provinceId], z: [selectedProvince.score], colorscale: [[0, '#fffaf2'], [1, '#fffaf2']] as [number, string][], showscale: false, hoverinfo: 'skip' as const, marker: { line: { color: '#22201d', width: 3 } } }]
  const provincialLink = `/provincial?scale=${scale}&year=${year}&province=${encodeURIComponent(selectedProvince.provinceVi)}`
  const selectProvince = (provinceId: number) => { const province = rows.find((row) => row.provinceId === provinceId); if (province) { setSelectedId(provinceId); setParams({ scale, year: String(year), province: province.provinceVi }) } }

  return <article className="overview">
    <div className="title-row"><div><p className="eyebrow">Tổng quan</p><h1>Điểm quản trị, nhìn từ từng tỉnh</h1><p className="lede">So sánh cùng một thước đo để nhận ra khoảng cách và điểm sáng của quản trị địa phương.</p></div><p className="status">Dữ liệu đã xử lý · local</p></div>
    <section className="filter-bar" aria-label="Bộ lọc Tổng quan"><label>Phạm vi<select value={scale} onChange={(event) => update(validScale(event.target.value), year)}><option value="six">Tổng 6 lĩnh vực gốc</option><option value="eight">Tổng PAPI (8 lĩnh vực)</option></select></label><label>Năm<select value={year} onChange={(event) => update(scale, Number(event.target.value))}>{available.years.map((item) => <option key={item} value={item}>{item}</option>)}</select></label><p>{data.measure.unit}</p></section>
    <section className="kpis" aria-label="Chỉ số tóm tắt"><Kpi label="Tỉnh có dữ liệu" value={`${meta.n}/63`} /><Kpi label="Điểm trung bình" value={metric(data.metrics.mean)} /><Kpi label="Dẫn đầu" value={textMetric(data.metrics.leader)} detail={metric(data.metrics.max)} /><Kpi label="Khoảng cách đầu-cuối" value={data.metrics.gap === null ? '—' : `${metric(data.metrics.gap)} điểm`} detail={data.metrics.last ? `${data.metrics.last} xếp cuối` : 'Thiếu dữ liệu'} /></section>
    <section className="insight"><p className="eyebrow">Điểm cần đọc</p><p>{data.metrics.leader && data.metrics.last ? <><strong>{data.metrics.leader}</strong> dẫn đầu và <strong>{data.metrics.last}</strong> xếp cuối trong năm {year}.</> : 'Chưa đủ dữ liệu để xác định hai cực trị.'} Bản đồ và danh sách được liên kết: chọn một tỉnh ở bất kỳ bên nào để xem cùng một ngữ cảnh.</p></section>
    <section className="overview-grid"><div className="map-surface"><div className="section-heading"><div><p className="eyebrow">Phân bố theo tỉnh</p><h2>Bản đồ {year}</h2></div><span>Viền đen là tỉnh đang chọn</span></div><Suspense fallback={<div className="chart-fallback" aria-label="Đang tải bản đồ" />}><Plot data={chartData} layout={{ autosize: true, paper_bgcolor: 'rgba(0,0,0,0)', plot_bgcolor: 'rgba(0,0,0,0)', margin: { t: 8, r: 18, b: 8, l: 8 }, geo: { scope: 'asia', fitbounds: 'locations', bgcolor: 'rgba(0,0,0,0)', showframe: false, showcoastlines: false, projection: { type: 'mercator' } } }} config={{ displayModeBar: false, responsive: true }} style={{ width: '100%', height: 'min(66vw, 590px)' }} onClick={(event) => { const id = Number(event.points[0]?.customdata); if (Number.isInteger(id)) selectProvince(id) }} /></Suspense><p className="sr-only">Bản đồ hiển thị điểm PAPI của {meta.n} tỉnh năm {year}. Chọn tỉnh để đồng bộ với danh sách xếp hạng.</p><Meta {...meta} /></div>
      <aside className="ranking"><div className="section-heading"><div><p className="eyebrow">Xếp hạng</p><h2>Đọc hai cực trị</h2></div></div><div className="tabs" role="tablist" aria-label="Hướng xếp hạng"><button role="tab" aria-selected={ranking === 'top'} onClick={() => setRanking('top')}>Cao nhất</button><button role="tab" aria-selected={ranking === 'bottom'} onClick={() => setRanking('bottom')}>Thấp nhất</button></div>{selectedOutsideRanking && <button className="selected-pin selected" onClick={() => selectProvince(selectedProvince.provinceId)}><span>Tỉnh đang chọn: <strong>{selectedProvince.provinceVi}</strong></span><strong>{selectedProvince.score === null ? '—' : number.format(selectedProvince.score)}</strong></button>}<ol>{rankingRows.map((row) => <li key={row.provinceId}><button className={selectedProvince.provinceId === row.provinceId ? 'selected' : ''} onClick={() => selectProvince(row.provinceId)}><span><b>{row.rank}</b>{row.provinceVi}<small>{row.region}</small></span><strong>{row.score === null ? '—' : number.format(row.score)}</strong></button></li>)}</ol><Meta source={data.ranking.source} unit={data.ranking.unit} n={meta.n} caveats={data.ranking.caveats} /></aside></section>
    <section className="selection" aria-live="polite"><p className="eyebrow">Tỉnh đang chọn</p><h2>{selectedProvince.provinceVi}</h2><p>{selectedProvince.region} · <strong>{selectedProvince.score === null ? 'Thiếu dữ liệu' : `${number.format(selectedProvince.score)} ${data.measure.unit}`}</strong></p><Link className="cta" to={provincialLink}>Xem hồ sơ tỉnh <span aria-hidden="true">→</span></Link></section>
    <section className="story"><p className="eyebrow">Bước đọc tiếp</p><h2>Từ bản đồ tới câu chuyện thay đổi</h2><p>Chọn một hướng để tiếp tục khám phá với cùng phạm vi và năm đang xem.</p><div className="story-links"><Link to={`/time-trend?scale=${scale}&year=${year}`}>Diễn biến theo thời gian</Link><Link to={provincialLink}>Vùng & tỉnh</Link><Link to={`/dimension?scale=${scale}&year=${year}`}>Mối quan hệ lĩnh vực</Link><Link to={`/dynamics?scale=${scale}&year=${year}`}>Thay đổi & phân nhóm</Link></div></section>
  </article>
}

function Kpi({ label, value, detail }: { label: string; value: string; detail?: string }) { return <div className="kpi"><p>{label}</p><strong>{value}</strong>{detail && <small>{detail}</small>}</div> }
function metric(value: number | null) { return value === null ? '—' : number.format(value) }
function textMetric(value: string) { return value.trim() || 'Thiếu dữ liệu' }
