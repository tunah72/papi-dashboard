import { useEffect } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Link, useSearchParams } from 'react-router-dom'
import type { Data } from 'plotly.js'
import { api, type Scale } from '../api/client'
import { CartesianChart } from '../components/CartesianChart'

const fmt = new Intl.NumberFormat('vi-VN', { maximumFractionDigits: 2 })
const scaleOf = (value: string | null): Scale => value === 'eight' ? 'eight' : 'six'
const provinceN = (n: number) => `${n} tỉnh`
function axisLabel(value: string) { const words = value.split(' '); const lines: string[] = []; let line = ''; for (const word of words) { if (`${line} ${word}`.trim().length > 18 && line) { lines.push(line); line = word } else line = `${line} ${word}`.trim() } if (line) lines.push(line); return lines.join('<br>') }

function Meta({ source, unit, nLabel, caveats = [] }: { source: string; unit: string; nLabel: string; caveats?: string[] }) { return <footer className="meta"><span>Nguồn: {source}</span><span>Đơn vị: {unit}</span><span>Phạm vi: {nLabel}</span>{caveats.map((note) => <small key={note}>{note}</small>)}</footer> }
function Loading() { return <section className="loading" role="status" aria-live="polite" aria-label="Đang tải vùng và tỉnh"><div/><div/><div/><div/></section> }

export function Provincial() {
  const [params, setParams] = useSearchParams()
  const scale = scaleOf(params.get('scale'))
  const metadata = useQuery({ queryKey: ['metadata'], queryFn: api.metadata })
  const cfg = metadata.data?.data.scales.find((item) => item.id === scale)
  const year = cfg?.years.includes(Number(params.get('year'))) ? Number(params.get('year')) : (cfg?.years.at(-1) ?? 2024)
  const rawProvince = params.get('province') ?? ''
  const provinceRecord = metadata.data?.data.provinces.find((item) => item.provinceVi === rawProvince)
  const rawRegion = params.get('region') ?? ''
  const validRegion = metadata.data?.data.regions.includes(rawRegion) ? rawRegion : undefined
  const region = provinceRecord?.region ?? validRegion
  const scope = useQuery({ queryKey: ['provinces-scope', scale, year, region], queryFn: () => api.provinces(scale, year, region), enabled: Boolean(cfg) })
  const supportedProvince = scope.data?.data.availability.provinces.includes(rawProvince) ? rawProvince : undefined
  const selected = useQuery({ queryKey: ['provinces-selected', scale, year, region, supportedProvince], queryFn: () => api.provinces(scale, year, region, supportedProvince), enabled: Boolean(cfg && supportedProvince) })
  const result = selected.data ?? scope.data
  useEffect(() => {
    const filters = result?.meta.filters
    if (!filters || (supportedProvince && !selected.data)) return
    const canonical = { scale: filters.scale, year: String(filters.year), region: filters.region, province: filters.province }
    if (params.toString() !== new URLSearchParams(canonical).toString()) setParams(canonical, { replace: true })
  }, [params, result, selected.data, setParams, supportedProvince])
  const reset = () => setParams({ scale: 'six', year: '2024' })

  if (metadata.isLoading || scope.isLoading || (supportedProvince && selected.isLoading)) return <Loading />
  const fault = metadata.error ?? scope.error ?? selected.error
  if (fault) return <section className="state state-error" role="alert"><h1>Không tải được dữ liệu vùng</h1><p>{fault.message}</p><p>Hãy kiểm tra FastAPI local rồi thử lại.</p><button onClick={() => { void metadata.refetch(); void scope.refetch(); void selected.refetch() }}>Thử lại</button><button className="text-button" onClick={reset}>Đặt lại bộ lọc</button></section>
  if (!cfg || !result || !result.data.distribution.rows.length) return <section className="state"><h1>Chưa có dữ liệu vùng và tỉnh</h1><p>Hãy chọn lại phạm vi hoặc năm có dữ liệu.</p><button onClick={reset}>Đặt lại bộ lọc</button></section>

  const d = result.data
  const f = result.meta.filters
  const labels = new Map(metadata.data!.data.dimensions.map((item) => [item.code, item.nameVi]))
  const change = (next: Partial<{ scale: Scale; year: number; region: string; province: string }>) => {
    const nextScale = next.scale ?? scale
    const nextCfg = metadata.data!.data.scales.find((item) => item.id === nextScale)!
    const nextYear = next.scale ? nextCfg.years.at(-1)! : (next.year ?? year)
    if (next.province) setParams({ scale: nextScale, year: String(nextYear), region: next.region ?? f.region, province: next.province })
    else setParams({ scale: nextScale, year: String(nextYear), ...(next.region ? { region: next.region } : {}) })
  }
  const active = d.ranking.rows.find((row) => row.provinceVi === f.province)
  const groups = [...new Set(d.distribution.rows.map((row) => row.region))]
  const boxplots: Data[] = groups.map((group) => ({ type: 'box', name: group, y: d.distribution.rows.filter((row) => row.region === group).map((row) => row.score), boxpoints: 'all', jitter: 0.25, pointpos: 0, marker: { color: group === f.region ? '#a73b25' : '#9d8e7d' }, line: { color: group === f.region ? '#7d2b1a' : '#9d8e7d' }, hovertemplate: `${group}: %{y:.2f}<extra></extra>` }))
  const profileLabels = d.profile.rows.map((row) => labels.get(row.code) ?? row.code)
  const profileAxis = profileLabels.map(axisLabel)
  const profile: Data[] = [{ type: 'scatter', mode: 'markers', name: f.province, x: d.profile.rows.map((row) => row.provinceScore), y: profileAxis, customdata: profileLabels, marker: { color: '#a73b25', size: 12 }, hovertemplate: `%{customdata}: %{x:.2f}<extra>${f.province}</extra>` }, { type: 'scatter', mode: 'markers', name: 'Trung bình vùng', x: d.profile.rows.map((row) => row.regionMean), y: profileAxis, customdata: profileLabels, marker: { color: '#6d655c', size: 10 }, hovertemplate: '%{customdata}: %{x:.2f}<extra>Trung bình vùng</extra>' }, { type: 'scatter', mode: 'markers', name: 'Trung bình toàn quốc', x: d.profile.rows.map((row) => row.nationalMean), y: profileAxis, customdata: profileLabels, marker: { color: '#c7b7a6', size: 10 }, hovertemplate: '%{customdata}: %{x:.2f}<extra>Trung bình toàn quốc</extra>' }]
  const first = cfg.years[0] ?? f.year
  const second = cfg.years.find((item) => item > first) ?? first + 1
  const trendTo = f.year > first ? f.year : second
  return <article className="overview analysis-page">
    <p className="eyebrow">Vùng & tỉnh</p><h1>Khác biệt giữa vùng và tỉnh</h1><p className="lede">Chọn vùng rồi chọn tỉnh để đặt kết quả cạnh trung bình vùng và toàn quốc.</p>
    <section className="filter-bar" aria-label="Bộ lọc vùng và tỉnh"><label>Phạm vi<select value={f.scale} onChange={(event) => change({ scale: scaleOf(event.target.value) })}><option value="six">Tổng 6 lĩnh vực gốc</option><option value="eight">Tổng PAPI (8 lĩnh vực)</option></select></label><label>Năm<select value={f.year} onChange={(event) => change({ year: Number(event.target.value) })}>{cfg.years.map((item) => <option key={item} value={item}>{item}</option>)}</select></label><label>Vùng<select value={f.region} onChange={(event) => change({ region: event.target.value })}>{d.availability.regions.map((item) => <option key={item}>{item}</option>)}</select></label><label>Tỉnh<select value={f.province} onChange={(event) => change({ province: event.target.value })}>{d.availability.provinces.map((item) => <option key={item}>{item}</option>)}</select></label></section>
    <section className="kpis" aria-label="Chỉ số tóm tắt vùng và tỉnh"><Metric label="Điểm tỉnh" value={d.benchmark.provinceScore}/><Metric label="Trung bình vùng" value={d.benchmark.regionMean}/><Metric label="Trung bình toàn quốc" value={d.benchmark.nationalMean}/><Metric label="Thứ hạng trong vùng" value={active?.rankRegion ?? null}/></section>
    <section className="analysis-grid"><section className="map-surface"><h2>Phân phối theo vùng</h2><CartesianChart title="Phân phối điểm giữa các vùng" summary={`Mỗi chấm là một tỉnh; ${f.region} được tô màu nổi bật.`} data={boxplots} layout={{ yaxis: { title: { text: d.distribution.unit }, automargin: true }, xaxis: { title: { text: 'Vùng' }, automargin: true }, showlegend: false }} /><Meta source={d.distribution.source} unit={d.distribution.unit} nLabel={provinceN(d.distribution.rowCount)} caveats={d.distribution.caveats}/></section><section className="map-surface"><h2>{f.province} trong {f.region}</h2><ol className="province-ranking">{d.ranking.rows.map((row) => <li key={row.provinceId}><button className={row.provinceVi === f.province ? 'selected' : ''} onClick={() => change({ province: row.provinceVi })}><span>{row.rankRegion}. {row.provinceVi}</span><strong>{row.score === null ? '—' : fmt.format(row.score)}</strong></button></li>)}</ol><Meta source={d.ranking.source} unit={d.ranking.unit} nLabel={provinceN(d.ranking.rowCount)} caveats={d.ranking.caveats}/></section></section>
    <section className="map-surface"><h2>Hồ sơ lĩnh vực</h2><p>Ba dấu điểm giúp đọc chênh lệch giữa tỉnh, vùng và toàn quốc theo từng lĩnh vực.</p><CartesianChart title="So sánh điểm theo lĩnh vực" summary={`So sánh ${f.province}, trung bình ${f.region} và trung bình toàn quốc theo từng lĩnh vực.`} data={profile} layout={{ xaxis: { title: { text: d.profile.unit }, automargin: true }, yaxis: { automargin: true, tickfont: { size: 12 } }, legend: { orientation: 'h', y: -0.22 } }}><table><thead><tr><th>Lĩnh vực</th><th>Tỉnh</th><th>Vùng</th><th>Toàn quốc</th></tr></thead><tbody>{d.profile.rows.map((row) => <tr key={row.code}><th>{labels.get(row.code) ?? row.code}</th><td>{row.provinceScore === null ? '—' : fmt.format(row.provinceScore)}</td><td>{row.regionMean === null ? '—' : fmt.format(row.regionMean)}</td><td>{row.nationalMean === null ? '—' : fmt.format(row.nationalMean)}</td></tr>)}</tbody></table></CartesianChart><Meta source={d.profile.source} unit={d.profile.unit} nLabel={`${d.profile.rowCount} lĩnh vực`} caveats={d.profile.caveats}/></section>
    <section className="story"><h2>Xem diễn biến theo thời gian</h2><p>Chuyển sang chuỗi toàn quốc, giữ lại phạm vi và tỉnh đang chọn.</p><Link className="cta" to={`/time-trend?scale=${f.scale}&from=${first}&to=${trendTo}&province=${encodeURIComponent(f.province)}`}>Mở Diễn biến theo thời gian</Link></section>
  </article>
}

function Metric({ label, value }: { label: string; value: number | null }) { return <div className="kpi"><p>{label}</p><strong>{value === null ? '—' : fmt.format(value)}</strong></div> }
