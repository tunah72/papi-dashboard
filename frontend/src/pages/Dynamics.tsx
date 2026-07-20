import { useEffect, useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Link, useSearchParams } from 'react-router-dom'
import type { Data } from 'plotly.js'
import { api, type Scale } from '../api/client'
import { CartesianChart } from '../components/CartesianChart'

const scoreFmt = new Intl.NumberFormat('vi-VN', { maximumFractionDigits: 2 })
const deltaFmt = new Intl.NumberFormat('vi-VN', { maximumFractionDigits: 2, signDisplay: 'always' })
const scaleOf = (value: string | null): Scale => value === 'eight' ? 'eight' : 'six'
const letters = ['A', 'B', 'C', 'D']
function Meta({ source, unit, n, caveats = [] }: { source: string; unit: string; n: string; caveats?: string[] }) { return <footer className="meta"><span>Nguồn: {source}</span><span>Đơn vị: {unit}</span><span>Phạm vi: {n}</span>{caveats.map((note) => <small key={note}>{note}</small>)}</footer> }
function Loading() { return <section className="loading" role="status" aria-live="polite" aria-label="Đang tải thay đổi và phân nhóm"><div/><div/><div/><div/></section> }
type Sort = 'provinceVi' | 'change' | 'fromScore' | 'toScore'

export function Dynamics() {
  const [params, setParams] = useSearchParams()
  const [search, setSearch] = useState('')
  const [sort, setSort] = useState<Sort>('change')
  const [descending, setDescending] = useState(true)
  const [activeCluster, setActiveCluster] = useState<string | null>(null)
  const scale = scaleOf(params.get('scale'))
  const metadata = useQuery({ queryKey: ['metadata'], queryFn: api.metadata })
  const cfg = metadata.data?.data.scales.find((item) => item.id === scale)
  const years = cfg?.years ?? []
  const rawFrom = Number(params.get('from'))
  const rawTo = Number(params.get('to'))
  const from = years.includes(rawFrom) ? rawFrom : (years[0] ?? 2011)
  const to = years.includes(rawTo) && rawTo > from ? rawTo : (years.at(-1) ?? 2024)
  const query = useQuery({ queryKey: ['dynamics', scale, from, to], queryFn: () => api.dynamics(scale, from, to), enabled: Boolean(cfg && from < to) })
  useEffect(() => {
    const f = query.data?.meta.filters
    if (!f) return
    const canonical = new URLSearchParams({ scale: f.scale, from: String(f.from), to: String(f.to) })
    const province = params.get('province')
    if (province) canonical.set('province', province)
    if (params.toString() !== canonical.toString()) setParams(canonical, { replace: true })
  }, [params, query.data, setParams])
  const reset = () => setParams({ scale: 'six', from: '2011', to: '2024' })
  if (metadata.isLoading || query.isLoading) return <Loading />
  const error = metadata.error ?? query.error
  if (error) return <section className="state state-error" role="alert"><h1>Không tải được thay đổi và phân nhóm</h1><p>{error.message}</p><button onClick={() => { void metadata.refetch(); void query.refetch() }}>Thử lại</button><button className="text-button" onClick={reset}>Đặt lại bộ lọc</button></section>
  if (!cfg || !query.data || !query.data.data.changes.rows.length) return <section className="state"><h1>Chưa có dữ liệu thay đổi</h1><p>Hãy chọn hai mốc năm khác nhau có dữ liệu.</p><button onClick={reset}>Đặt lại bộ lọc</button></section>

  const result = query.data
  const d = result.data
  const f = result.meta.filters
  const labels = new Map(metadata.data!.data.dimensions.map((item) => [item.code, item.short]))
  const clusterKeys = [...new Set(d.clusters.centroids.map((row) => row.cluster))].sort((a, b) => Number(a) - Number(b))
  const clusterName = (key: string) => `Hồ sơ ${letters[clusterKeys.indexOf(key)] ?? key}`
  const change = (next: Partial<{ scale: Scale; from: number; to: number }>) => {
    const nextScale = next.scale ?? f.scale
    const nextCfg = metadata.data!.data.scales.find((item) => item.id === nextScale)!
    const nextFrom = next.scale ? nextCfg.years[0] : (next.from ?? f.from)
    const nextTo = next.scale ? nextCfg.years.at(-1)! : (next.to ?? f.to)
    const safeTo = nextTo > nextFrom ? nextTo : (nextCfg.years.find((year) => year > nextFrom) ?? nextCfg.years.at(-1)!)
    setParams({ scale: nextScale, from: String(nextFrom), to: String(safeTo), ...(params.get('province') ? { province: params.get('province')! } : {}) })
  }
  const changeBars = (rows: typeof d.changes.rows, color: string): Data[] => [{ type: 'bar', orientation: 'h', x: rows.map((row) => row.change), y: rows.map((row) => row.provinceVi), text: rows.map((row) => deltaFmt.format(row.change ?? 0)), textposition: 'auto', marker: { color }, customdata: rows.map((row) => [row.fromScore, row.toScore, row.region]), hovertemplate: '%{y}<br>Thay đổi: %{x:.2f}<br>Từ: %{customdata[0]:.2f}<br>Đến: %{customdata[1]:.2f}<br>%{customdata[2]}<extra></extra>' }]
  const allRows = d.changes.rows.filter((row) => row.provinceVi.toLocaleLowerCase('vi').includes(search.toLocaleLowerCase('vi'))).sort((a, b) => {
    const av = a[sort]; const bv = b[sort]
    const resultSort = typeof av === 'string' && typeof bv === 'string' ? av.localeCompare(bv, 'vi') : Number(av ?? 0) - Number(bv ?? 0)
    return descending ? -resultSort : resultSort
  })
  const dimensionCodes = cfg.dimensions
  const centroidValue = (row: Record<string, unknown>, code: string) => Number(row[code] ?? 0)
  const clusterProfile = (row: Record<string, unknown>) => {
    const ranked = dimensionCodes.map((code) => ({ code, value: centroidValue(row, code) })).sort((a, b) => b.value - a.value)
    return `Điểm cao nhất ở ${labels.get(ranked[0]?.code ?? '') ?? ranked[0]?.code}; thấp nhất ở ${labels.get(ranked.at(-1)?.code ?? '') ?? ranked.at(-1)?.code}.`
  }
  const centroidHeatmap: Data[] = [{ type: 'heatmap', x: dimensionCodes.map((code) => labels.get(code) ?? code), y: d.clusters.centroids.map((row) => clusterName(row.cluster)), z: d.clusters.centroids.map((row) => dimensionCodes.map((code) => centroidValue(row as Record<string, unknown>, code))), colorscale: [[0, '#f5e6dc'], [0.5, '#e0a23b'], [1, '#a73b25']], hovertemplate: '%{y}<br>%{x}: %{z:.2f}<extra></extra>', colorbar: { title: { text: d.clusters.unit } } }]
  const profileDots: Data[] = d.clusters.centroids.map((row) => ({ type: 'scatter', mode: 'lines+markers', name: clusterName(row.cluster), x: dimensionCodes.map((code) => labels.get(code) ?? code), y: dimensionCodes.map((code) => centroidValue(row as Record<string, unknown>, code)), marker: { size: activeCluster === row.cluster ? 12 : 8 }, line: { width: activeCluster === row.cluster ? 3 : 1.5 }, customdata: dimensionCodes.map(() => row.cluster), hovertemplate: `${clusterName(row.cluster)}<br>%{x}: %{y:.2f}<extra></extra>` }))
  const active = activeCluster ?? clusterKeys[0]
  const nearby = d.clusters.profiles.find((profile) => profile.cluster === active)
  const contextProvince = params.get('province')
  const setSortField = (field: Sort) => { if (field === sort) setDescending((value) => !value); else { setSort(field); setDescending(field !== 'provinceVi') } }
  const sortDirection = (field: Sort) => sort === field ? (descending ? 'descending' : 'ascending') : 'none'
  const sortAction = (field: Sort, label: string) => sort === field ? `${label}, đang ${descending ? 'giảm dần' : 'tăng dần'}; chọn để đảo thứ tự` : `${label}; chọn để sắp xếp`
  return <article className="overview analysis-page">
    <p className="eyebrow">Thay đổi & phân nhóm</p><h1>Điểm thay đổi ra sao, các tỉnh giống nhau ở đâu?</h1><p className="lede">So sánh hai mốc theo tổng điểm rồi đọc các hồ sơ lĩnh vực tương đồng ở năm cuối.</p>
    <section className="filter-bar" aria-label="Bộ lọc thay đổi và phân nhóm"><label>Phạm vi<select value={f.scale} onChange={(e) => change({ scale: scaleOf(e.target.value) })}><option value="six">Tổng 6 lĩnh vực gốc</option><option value="eight">Tổng PAPI (8 lĩnh vực)</option></select></label><label>Từ năm<select value={f.from} onChange={(e) => change({ from: Number(e.target.value) })}>{cfg.years.filter((year) => year < f.to).map((year) => <option key={year}>{year}</option>)}</select></label><label>Đến năm<select value={f.to} onChange={(e) => change({ to: Number(e.target.value) })}>{cfg.years.filter((year) => year > f.from).map((year) => <option key={year}>{year}</option>)}</select></label></section>
    <section className="analysis-grid"><section className="map-surface"><h2>Tăng nhiều nhất</h2><p>Tối đa 8 tỉnh có chênh lệch dương lớn nhất từ {f.from} đến {f.to}.</p><CartesianChart title="8 tỉnh tăng nhiều nhất" summary="Thanh dài hơn là mức tăng tổng điểm PAPI lớn hơn." data={changeBars(d.changes.top8.slice(0, 8), '#a73b25')} layout={{ xaxis: { title: { text: d.changes.unit }, automargin: true } }}><table><thead><tr><th>Tỉnh</th><th>Thay đổi</th></tr></thead><tbody>{d.changes.top8.slice(0, 8).map((row) => <tr key={row.provinceVi}><th>{row.provinceVi}</th><td>{deltaFmt.format(row.change ?? 0)}</td></tr>)}</tbody></table></CartesianChart><Meta source={d.changes.source} unit={d.changes.unit} n={`${d.changes.n} tỉnh có đủ hai mốc`} caveats={d.changes.caveats}/></section><section className="map-surface"><h2>Giảm nhiều nhất</h2><p>Tối đa 8 tỉnh có chênh lệch thấp nhất; số âm là giảm điểm.</p><CartesianChart title="8 tỉnh giảm nhiều nhất" summary="Thanh nằm về bên trái 0 cho thấy tổng điểm giảm." data={changeBars(d.changes.bottom8.slice(0, 8), '#4c6a9c')} layout={{ xaxis: { title: { text: d.changes.unit }, automargin: true, zeroline: true } }}><table><thead><tr><th>Tỉnh</th><th>Thay đổi</th></tr></thead><tbody>{d.changes.bottom8.slice(0, 8).map((row) => <tr key={row.provinceVi}><th>{row.provinceVi}</th><td>{deltaFmt.format(row.change ?? 0)}</td></tr>)}</tbody></table></CartesianChart><Meta source={d.changes.source} unit={d.changes.unit} n={`${d.changes.n} tỉnh có đủ hai mốc`} caveats={d.changes.caveats}/></section></section>
    <section className="map-surface dynamics-table"><h2>Toàn bộ chênh lệch</h2><details><summary>Xem tất cả tỉnh</summary><div className="table-tools"><label>Tìm tỉnh<input aria-label="Tìm tỉnh" value={search} onChange={(e) => setSearch(e.target.value)} placeholder="Nhập tên tỉnh"/></label><span>{allRows.length}/{d.changes.rows.length} tỉnh</span></div><div className="table-scroll"><table><thead><tr><th aria-sort={sortDirection('provinceVi')}><button aria-label={sortAction('provinceVi', 'Tỉnh')} onClick={() => setSortField('provinceVi')}>Tỉnh {sort === 'provinceVi' && (descending ? '↓' : '↑')}</button></th><th aria-sort={sortDirection('fromScore')}><button aria-label={sortAction('fromScore', `Điểm năm ${f.from}`)} onClick={() => setSortField('fromScore')}>{f.from} {sort === 'fromScore' && (descending ? '↓' : '↑')}</button></th><th aria-sort={sortDirection('toScore')}><button aria-label={sortAction('toScore', `Điểm năm ${f.to}`)} onClick={() => setSortField('toScore')}>{f.to} {sort === 'toScore' && (descending ? '↓' : '↑')}</button></th><th aria-sort={sortDirection('change')}><button aria-label={sortAction('change', 'Thay đổi')} onClick={() => setSortField('change')}>Thay đổi {sort === 'change' && (descending ? '↓' : '↑')}</button></th></tr></thead><tbody>{allRows.map((row) => <tr key={row.provinceVi} className={row.provinceVi === contextProvince ? 'selected-row' : ''}><th>{row.provinceVi}<small>{row.region}</small></th><td>{scoreFmt.format(row.fromScore ?? 0)}</td><td>{scoreFmt.format(row.toScore ?? 0)}</td><td>{deltaFmt.format(row.change ?? 0)}</td></tr>)}</tbody></table></div></details><Meta source={d.changes.source} unit={d.measure.unit} n={`${d.changes.rowCount} tỉnh`} caveats={result.meta.caveats}/></section>
    <section className="analysis-grid"><section className="map-surface"><h2>Hồ sơ A–D</h2><p>Hồ sơ A–D là nhãn đọc biểu đồ, không phải thứ hạng. Màu phản ánh centroid theo lĩnh vực.</p><div className="profile-controls" role="group" aria-label="Chọn hồ sơ tỉnh">{clusterKeys.map((key) => <button key={key} aria-pressed={active === key} onClick={() => setActiveCluster(key)}>{clusterName(key)}</button>)}</div><CartesianChart title="Bản đồ nhiệt hồ sơ A–D" summary="Mỗi hàng là điểm trung tâm của một hồ sơ tỉnh ở năm cuối; dùng các nút Hồ sơ A–D để chọn bằng bàn phím." data={centroidHeatmap} height={360} onClick={(event) => { const point = event.points?.[0]; const indexes = Array.isArray(point?.pointNumber) ? point.pointNumber : point?.pointIndex; const index = Array.isArray(indexes) ? indexes[1] : undefined; if (typeof index === 'number') setActiveCluster(d.clusters.centroids[index]?.cluster ?? null) }}><table><thead><tr><th>Hồ sơ</th><th>Đặc điểm</th><th>Số tỉnh</th></tr></thead><tbody>{d.clusters.centroids.map((row) => <tr key={row.cluster}><th>{clusterName(row.cluster)}</th><td>{clusterProfile(row as Record<string, unknown>)}</td><td>{row.n}</td></tr>)}</tbody></table></CartesianChart><details className="method-details"><summary>Thông tin phương pháp</summary><p>KMeans chuẩn hoá các lĩnh vực, dùng random_state=42. Hồ sơ chỉ mô tả các tỉnh có mẫu gần nhau, không phải xếp hạng.</p></details><Meta source={d.clusters.source} unit={d.clusters.unit} n={`${d.clusters.n} tỉnh; ${d.clusters.count} hồ sơ`} caveats={d.clusters.caveats}/></section><section className="map-surface"><h2>Chọn hồ sơ để xem tỉnh gần nhau</h2><p>Chọn một hồ sơ để xem những tỉnh có mô hình điểm lĩnh vực gần nhau.</p><CartesianChart title="Hồ sơ centroid theo lĩnh vực" summary="Mỗi đường là một hồ sơ; dùng nút Hồ sơ A–D hoặc nhấp vào dấu điểm để chọn." data={profileDots} layout={{ yaxis: { title: { text: d.clusters.unit }, automargin: true }, legend: { orientation: 'h', y: -0.25 } }} onClick={(event) => { const key = event.points?.[0]?.customdata; if (typeof key === 'string') setActiveCluster(key) }} />{nearby && <div className="nearby-provinces" aria-live="polite"><h3>{clusterName(active)}: {nearby.n} tỉnh có hồ sơ gần nhau</h3><ul>{nearby.provinces.map((province) => <li key={province.provinceVi}>{province.provinceVi} <small>{province.region}</small></li>)}</ul></div>}<Meta source={d.clusters.source} unit={d.clusters.unit} n={`${d.clusters.n} tỉnh`} caveats={d.clusters.caveats}/></section></section>
    <section className="story"><h2>Đặt câu hỏi phân tích với trợ lý AI</h2><p>Ngữ cảnh phạm vi, hai mốc và tỉnh đang chọn được giữ lại; mọi đề xuất code sẽ chờ bạn duyệt ở bước tiếp theo.</p><Link className="cta" to={`/ai-assistant?scale=${f.scale}&from=${f.from}&to=${f.to}${contextProvince ? `&province=${encodeURIComponent(contextProvince)}` : ''}`}>Mở Trợ lý AI</Link></section>
  </article>
}
