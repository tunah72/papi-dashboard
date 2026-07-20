import { useEffect } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Link, useSearchParams } from 'react-router-dom'
import type { Data } from 'plotly.js'
import { api, type Scale } from '../api/client'
import { CartesianChart } from '../components/CartesianChart'

const fmt = new Intl.NumberFormat('vi-VN', { maximumFractionDigits: 2 })
const scaleOf = (value: string | null): Scale => value === 'eight' ? 'eight' : 'six'
function Meta({ source, unit, n, caveats = [] }: { source: string; unit: string; n: string; caveats?: string[] }) { return <footer className="meta"><span>Nguồn: {source}</span><span>Đơn vị: {unit}</span><span>Phạm vi: {n}</span>{caveats.map((note) => <small key={note}>{note}</small>)}</footer> }
function Loading() { return <section className="loading" role="status" aria-live="polite" aria-label="Đang tải mối quan hệ lĩnh vực"><div/><div/><div/><div/></section> }

export function Dimension() {
  const [params, setParams] = useSearchParams()
  const scale = scaleOf(params.get('scale'))
  const metadata = useQuery({ queryKey: ['metadata'], queryFn: api.metadata })
  const cfg = metadata.data?.data.scales.find((item) => item.id === scale)
  const year = cfg?.years.includes(Number(params.get('year'))) ? Number(params.get('year')) : (cfg?.years.at(-1) ?? 2024)
  const available = cfg?.dimensions ?? []
  const rawX = params.get('x')
  const rawY = params.get('y')
  const x = available.includes(rawX ?? '') ? rawX! : (available[1] ?? available[0] ?? 'D2')
  const y = available.includes(rawY ?? '') && rawY !== x ? rawY! : (available.find((code) => code !== x) ?? 'D1')
  const query = useQuery({ queryKey: ['dimensions', scale, year, x, y], queryFn: () => api.dimensions(scale, year, x, y), enabled: Boolean(cfg && x !== y) })
  useEffect(() => {
    const f = query.data?.meta.filters
    if (!f) return
    const canonical = new URLSearchParams({ scale: f.scale, year: String(f.year), x: f.x, y: f.y })
    const province = params.get('province')
    if (province) canonical.set('province', province)
    if (params.toString() !== canonical.toString()) setParams(canonical, { replace: true })
  }, [params, query.data, setParams])
  const reset = () => setParams({ scale: 'six', year: '2024', x: 'D2', y: 'D1' })
  if (metadata.isLoading || query.isLoading) return <Loading />
  const error = metadata.error ?? query.error
  if (error) return <section className="state state-error" role="alert"><h1>Không tải được mối quan hệ lĩnh vực</h1><p>{error.message}</p><button onClick={() => { void metadata.refetch(); void query.refetch() }}>Thử lại</button><button className="text-button" onClick={reset}>Đặt lại bộ lọc</button></section>
  if (!cfg || !query.data || !query.data.data.pair.rows.length) return <section className="state"><h1>Chưa có dữ liệu mối quan hệ</h1><p>Hãy chọn lại phạm vi, năm hoặc cặp lĩnh vực khác.</p><button onClick={reset}>Đặt lại bộ lọc</button></section>

  const result = query.data
  const d = result.data
  const f = result.meta.filters
  const labels = new Map(d.labels.map((item) => [item.code, item]))
  const label = (code: string) => labels.get(code)?.nameVi ?? code
  const compact = (code: string) => labels.get(code)?.short ?? label(code)
  const preserve = params.get('province') ? `&province=${encodeURIComponent(params.get('province')!)}` : ''
  const change = (next: Partial<{ scale: Scale; year: number; x: string; y: string }>) => {
    const nextScale = next.scale ?? f.scale
    const nextCfg = metadata.data!.data.scales.find((item) => item.id === nextScale)!
    const dimensions = nextCfg.dimensions
    const nextX = next.scale ? (dimensions[1] ?? dimensions[0]) : (next.x ?? f.x)
    const nextY = next.scale ? dimensions[0] : (next.y ?? f.y)
    const safeY = nextY === nextX ? (dimensions.find((code) => code !== nextX) ?? nextY) : nextY
    setParams({ scale: nextScale, year: String(next.scale ? nextCfg.years.at(-1)! : (next.year ?? f.year)), x: nextX, y: safeY, ...(params.get('province') ? { province: params.get('province')! } : {}) })
  }
  const heatmap: Data[] = [{ type: 'heatmap', x: d.correlation.codes.map(compact), y: d.correlation.codes.map(compact), z: d.correlation.matrix.map((row, rowIndex) => row.map((value, columnIndex) => columnIndex <= rowIndex ? value : null)), customdata: d.correlation.matrix.map((row, rowIndex) => row.map((value, columnIndex) => [label(d.correlation.codes[columnIndex]), label(d.correlation.codes[rowIndex]), value])), colorscale: [[0, '#4c6a9c'], [0.5, '#fffdf8'], [1, '#a73b25']], zmin: -1, zmax: 1, hoverongaps: false, hovertemplate: '%{customdata[0]} × %{customdata[1]}<br>r = %{z:.2f}<extra></extra>', colorbar: { title: { text: 'r' } } } as unknown as Data]
  const selectedProvince = params.get('province')
  const colors: Record<string, string> = { 'Cao–cao': '#a73b25', 'Thấp–thấp': '#4c6a9c', 'Cao–thấp': '#e0a23b', 'Thấp–cao': '#578145' }
  const scatter: Data[] = Object.keys(colors).map((quadrant) => {
    const rows = d.pair.rows.filter((row) => row.quadrant === quadrant)
    return { type: 'scatter', mode: 'markers', name: quadrant, x: rows.map((row) => row.x), y: rows.map((row) => row.y), customdata: rows.map((row) => [row.provinceVi, row.region, row.quadrant]), marker: { color: colors[quadrant], size: rows.map((row) => row.provinceVi === selectedProvince ? 15 : 9), line: { color: '#22201d', width: rows.map((row) => row.provinceVi === selectedProvince ? 2 : 0) } }, hovertemplate: '%{customdata[0]}<br>%{customdata[1]}<br>Nhóm: %{customdata[2]}<br>X: %{x:.2f}<br>Y: %{y:.2f}<extra></extra>' }
  })
  const firstYear = cfg.years[0]
  const nextYear = cfg.years.find((item) => item > f.year) ?? f.year
  const dynamicsRange = f.year > firstYear ? { from: firstYear, to: f.year } : { from: f.year, to: nextYear }
  return <article className="overview analysis-page">
    <p className="eyebrow">Mối quan hệ lĩnh vực</p><h1>Cùng biến thiên, không vội kết luận nguyên nhân</h1><p className="lede">Đọc tương quan giữa hai lĩnh vực và vị trí từng tỉnh so với điểm trung bình của mẫu.</p>
    <section className="filter-bar" aria-label="Bộ lọc mối quan hệ lĩnh vực"><label>Phạm vi<select value={f.scale} onChange={(e) => change({ scale: scaleOf(e.target.value) })}><option value="six">Tổng 6 lĩnh vực gốc</option><option value="eight">Tổng PAPI (8 lĩnh vực)</option></select></label><label>Năm<select value={f.year} onChange={(e) => change({ year: Number(e.target.value) })}>{cfg.years.map((item) => <option key={item}>{item}</option>)}</select></label><label>Lĩnh vực ngang<select value={f.x} onChange={(e) => change({ x: e.target.value })}>{d.availability.dimensions.map((code) => <option key={code} value={code} disabled={code === f.y}>{label(code)}</option>)}</select></label><label>Lĩnh vực dọc<select value={f.y} onChange={(e) => change({ y: e.target.value })}>{d.availability.dimensions.map((code) => <option key={code} value={code} disabled={code === f.x}>{label(code)}</option>)}</select></label></section>
    <section className="analysis-grid"><section className="map-surface"><h2>Tương quan giữa các lĩnh vực</h2><p>Chỉ nửa tam giác dưới có dữ liệu để tránh lặp lại cùng một cặp. Chọn một ô ngoài đường chéo để đổi hai trục biểu đồ phân tán.</p><CartesianChart title="Ma trận tương quan nửa dưới" summary="Thang màu phân kỳ biểu thị hướng và độ mạnh tương quan; nửa trên để trống." data={heatmap} height={430} onClick={(event) => { const point = event.points?.[0]; const indexes = Array.isArray(point?.pointNumber) ? point.pointNumber : point?.pointIndex; if (Array.isArray(indexes) && indexes[0] < indexes[1]) change({ x: d.correlation.codes[indexes[0]], y: d.correlation.codes[indexes[1]] }) }}><table><thead><tr><th>Lĩnh vực</th><th>Điểm TB</th><th>Độ lệch chuẩn</th><th>n</th></tr></thead><tbody>{d.standardDeviation.rows.map((row) => <tr key={row.code}><th>{label(row.code)}</th><td>{fmt.format(row.meanScore ?? 0)}</td><td>{fmt.format(row.stdScore ?? 0)}</td><td>{row.n}</td></tr>)}</tbody></table></CartesianChart><Meta source={d.correlation.source} unit={d.correlation.unit} n={`${d.correlation.n} tỉnh; ${d.correlation.rowCount} lĩnh vực`} caveats={d.correlation.caveats}/></section><section className="map-surface"><h2>Cặp đang xem</h2><p><strong>{label(f.x)}</strong> và <strong>{label(f.y)}</strong> có Pearson r = {d.pair.pearsonR === null ? '—' : fmt.format(d.pair.pearsonR)}. Đây là mối liên hệ quan sát, không chứng minh quan hệ nhân quả.</p><CartesianChart className="dimension-scatter" title="Phân tán theo hai lĩnh vực" summary={`Lĩnh vực ngang: ${label(f.x)}. Lĩnh vực dọc: ${label(f.y)}. Đường dọc và ngang là điểm trung bình; màu thể hiện bốn nhóm cao-thấp.`} data={scatter} layout={{ xaxis: { title: { text: `${label(f.x)} (${d.pair.unit})` }, automargin: true }, yaxis: { title: { text: `${label(f.y)} (${d.pair.unit})` }, automargin: true }, shapes: [{ type: 'line', x0: d.pair.xMean ?? 0, x1: d.pair.xMean ?? 0, y0: 0, y1: 1, yref: 'paper', line: { color: '#706a61', dash: 'dot' } }, { type: 'line', x0: 0, x1: 1, xref: 'paper', y0: d.pair.yMean ?? 0, y1: d.pair.yMean ?? 0, line: { color: '#706a61', dash: 'dot' } }], legend: { title: { text: 'Nhóm vị trí' }, orientation: 'h', y: -0.24 } }}><table><thead><tr><th>Tỉnh</th><th>{compact(f.x)}</th><th>{compact(f.y)}</th><th>Nhóm</th></tr></thead><tbody>{d.pair.rows.map((row) => <tr key={row.provinceVi}><th>{row.provinceVi}</th><td>{fmt.format(row.x ?? 0)}</td><td>{fmt.format(row.y ?? 0)}</td><td>{row.quadrant}</td></tr>)}</tbody></table></CartesianChart><Meta source={d.pair.source} unit={d.pair.unit} n={`${d.pair.n} tỉnh`} caveats={[...(d.pair.caveats ?? []), ...(result.meta.caveats ?? [])]}/></section></section>
    <section className="story"><h2>Xem thay đổi và nhóm tương đồng</h2><p>Giữ phạm vi và ngữ cảnh tỉnh để xem chênh lệch giữa hai mốc và các hồ sơ gần nhau.</p><Link className="cta" to={`/dynamics?scale=${f.scale}&from=${dynamicsRange.from}&to=${dynamicsRange.to}${preserve}`}>Mở Thay đổi & phân nhóm</Link></section>
  </article>
}
