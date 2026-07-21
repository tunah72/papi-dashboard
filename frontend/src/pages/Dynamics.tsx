import { useEffect, useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import type { Data } from 'plotly.js'
import { Link, useSearchParams } from 'react-router-dom'

import { api, type Scale } from '../api/client'
import { CartesianChart } from '../components/CartesianChart'
import {
  ChartCard,
  ChartMeta,
  DashboardPageHeader,
  EmptyState,
  ErrorState,
  FilterBar,
  InsightCard,
  KpiCard,
  KpiGrid,
  LoadingSkeleton,
} from '../components/dashboard'
import { divergingScale, uiColors } from '../theme/chartTheme'

const scoreFmt = new Intl.NumberFormat('vi-VN', { maximumFractionDigits: 2 })
const deltaFmt = new Intl.NumberFormat('vi-VN', { maximumFractionDigits: 2, signDisplay: 'exceptZero' })
const scaleOf = (value: string | null): Scale => value === 'six' ? 'six' : 'eight'
const clusterColors: Record<string, string> = { A: '#25736F', B: '#4C78A8', C: '#E39A54', D: '#8A6CB1', E: '#C96B5C', F: '#6B8E45' }
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
  const from = years.includes(rawFrom) ? rawFrom : (years[0] ?? 2018)
  const to = years.includes(rawTo) && rawTo > from ? rawTo : (years.at(-1) ?? 2024)
  const rawK = Number(params.get('k'))
  const k = Number.isInteger(rawK) && rawK >= 2 && rawK <= 6 ? rawK : undefined
  const query = useQuery({ queryKey: ['dynamics', scale, from, to, k], queryFn: () => api.dynamics(scale, from, to, k), enabled: Boolean(cfg && from < to) })

  useEffect(() => {
    const f = query.data?.meta.filters
    if (!f) return
    const canonical = new URLSearchParams({ scale: f.scale, from: String(f.from), to: String(f.to), k: String(f.k) })
    const province = params.get('province')
    if (province) canonical.set('province', province)
    if (params.toString() !== canonical.toString()) setParams(canonical, { replace: true })
  }, [params, query.data, setParams])
  const reset = () => setParams({ scale: 'eight', from: '2018', to: '2024', k: 'auto' })

  if (metadata.isLoading || query.isLoading) return <LoadingSkeleton label="Đang tải thay đổi và phân nhóm" />
  const error = metadata.error ?? query.error
  if (error) return <ErrorState title="Không tải được thay đổi và phân nhóm" description={error.message} action={<><button onClick={() => { void metadata.refetch(); void query.refetch() }}>Thử lại</button><button className="text-button" onClick={reset}>Đặt lại bộ lọc</button></>} />
  if (!cfg || !query.data || !query.data.data.changes.rows.length) return <EmptyState title="Chưa có dữ liệu thay đổi" description="Hãy chọn hai mốc năm khác nhau có dữ liệu." action={<button onClick={reset}>Đặt lại bộ lọc</button>} />

  const result = query.data
  const d = result.data
  const f = result.meta.filters
  const model = d.clusterModel
  const labels = new Map(metadata.data!.data.dimensions.map((item) => [item.code, item.short]))
  const clusterKeys = model.centroids.map((row) => row.cluster)
  const active = activeCluster && clusterKeys.includes(activeCluster) ? activeCluster : clusterKeys[0]
  const clusterName = (key: string) => `Hồ sơ ${key}`
  const change = (next: Partial<{ scale: Scale; from: number; to: number; k: number | 'auto' }>) => {
    const nextScale = next.scale ?? f.scale
    const nextCfg = metadata.data!.data.scales.find((item) => item.id === nextScale)!
    const nextFrom = next.scale ? nextCfg.years[0] : (next.from ?? f.from)
    const nextTo = next.scale ? nextCfg.years.at(-1)! : (next.to ?? f.to)
    const safeTo = nextTo > nextFrom ? nextTo : (nextCfg.years.find((year) => year > nextFrom) ?? nextCfg.years.at(-1)!)
    const nextK = next.k ?? f.k
    setParams({ scale: nextScale, from: String(nextFrom), to: String(safeTo), k: String(nextK), ...(params.get('province') ? { province: params.get('province')! } : {}) })
  }
  const changeBars = (rows: typeof d.changes.rows, color: string): Data[] => [{
    type: 'bar', orientation: 'h', x: rows.map((row) => row.change), y: rows.map((row) => row.provinceVi),
    text: rows.map((row) => deltaFmt.format(row.change ?? 0)), textposition: 'auto', marker: { color },
    customdata: rows.map((row) => [row.fromScore, row.toScore, row.region]),
    hovertemplate: '<b>%{y}</b><br>Thay đổi: %{x:+.2f}<br>Từ: %{customdata[0]:.2f}<br>Đến: %{customdata[1]:.2f}<br>%{customdata[2]}<extra></extra>',
  }]
  const allRows = d.changes.rows.filter((row) => row.provinceVi.toLocaleLowerCase('vi').includes(search.toLocaleLowerCase('vi'))).sort((a, b) => {
    const av = a[sort]; const bv = b[sort]
    const resultSort = typeof av === 'string' && typeof bv === 'string' ? av.localeCompare(bv, 'vi') : Number(av ?? 0) - Number(bv ?? 0)
    return descending ? -resultSort : resultSort
  })
  const dimensionCodes = cfg.dimensions
  const centroidHeatmap: Data[] = [{
    type: 'heatmap', x: dimensionCodes.map((code) => labels.get(code) ?? code), y: clusterKeys.map(clusterName),
    z: model.centroids.map((centroid) => dimensionCodes.map((code) => centroid.values.find((value) => value.code === code)?.zScore ?? null)),
    customdata: model.centroids.map((centroid) => dimensionCodes.map((code) => [centroid.descriptor, centroid.values.find((value) => value.code === code)?.rawScore])),
    colorscale: divergingScale, zmid: 0, colorbar: { title: { text: 'z-score' }, thickness: 12, outlinewidth: 0 },
    hovertemplate: '<b>%{y}</b><br>%{x}: z = %{z:.2f}<br>Điểm gốc: %{customdata[1]:.2f}<br>%{customdata[0]}<extra></extra>',
  } as unknown as Data]
  const assignments = model.assignments
  const movementSegments: Data = {
    type: 'scatter', mode: 'lines', name: 'Quỹ đạo đầu → cuối', hoverinfo: 'skip', showlegend: false,
    x: assignments.flatMap((row) => [row.startPc1, row.endPc1, null]),
    y: assignments.flatMap((row) => [row.startPc2, row.endPc2, null]),
    line: { color: '#B8C4C2', width: 1 }, opacity: 0.55,
  }
  const pca: Data[] = [movementSegments, {
    type: 'scatter', mode: 'markers', name: `Mốc đầu · ${f.from}`,
    x: assignments.map((row) => row.startPc1), y: assignments.map((row) => row.startPc2),
    customdata: assignments.map((row) => [row.provinceVi, row.startCluster]),
    marker: { color: assignments.map((row) => clusterColors[row.startCluster] ?? uiColors.muted), size: 7, symbol: 'circle-open', line: { width: 1.5 } },
    hovertemplate: '<b>%{customdata[0]}</b><br>Hồ sơ đầu: %{customdata[1]}<extra></extra>',
  }, {
    type: 'scatter', mode: 'markers', name: `Mốc cuối · ${f.to}`,
    x: assignments.map((row) => row.endPc1), y: assignments.map((row) => row.endPc2),
    customdata: assignments.map((row) => [row.provinceVi, row.endCluster, row.changed ? 'Có đổi hồ sơ' : 'Giữ hồ sơ']),
    marker: { color: assignments.map((row) => clusterColors[row.endCluster] ?? uiColors.muted), size: 9, symbol: 'diamond' },
    hovertemplate: '<b>%{customdata[0]}</b><br>Hồ sơ cuối: %{customdata[1]}<br>%{customdata[2]}<extra></extra>',
  }]
  const transitionMatrix = clusterKeys.map((fromCluster) => clusterKeys.map((toCluster) => model.transitions.find((row) => row.fromCluster === fromCluster && row.toCluster === toCluster)?.n ?? 0))
  const transitionProvinces = clusterKeys.map((fromCluster) => clusterKeys.map((toCluster) => model.transitions.find((row) => row.fromCluster === fromCluster && row.toCluster === toCluster)?.provinces.join(', ') || 'Không có tỉnh'))
  const transitionHeatmap: Data[] = [{
    type: 'heatmap', x: clusterKeys.map(clusterName), y: clusterKeys.map(clusterName), z: transitionMatrix,
    customdata: transitionProvinces, colorscale: [[0, '#EEF3F2'], [1, '#1F6873']],
    colorbar: { title: { text: 'Số tỉnh' }, thickness: 12, outlinewidth: 0 },
    hovertemplate: 'Từ %{y} → %{x}<br><b>%{z} tỉnh</b><br>%{customdata}<extra></extra>',
  }]
  const nearby = assignments.filter((row) => row.endCluster === active)
  const activeCentroid = model.centroids.find((row) => row.cluster === active)
  const contextProvince = params.get('province')
  const changedCount = assignments.filter((row) => row.changed).length
  const setSortField = (field: Sort) => { if (field === sort) setDescending((value) => !value); else { setSort(field); setDescending(field !== 'provinceVi') } }
  const sortDirection = (field: Sort) => sort === field ? (descending ? 'descending' : 'ascending') : 'none'
  const sortAction = (field: Sort, label: string) => sort === field ? `${label}, đang ${descending ? 'giảm dần' : 'tăng dần'}; chọn để đảo thứ tự` : `${label}; chọn để sắp xếp`

  return <article className="overview analysis-page">
    <DashboardPageHeader eyebrow="Thay đổi & phân nhóm · Hai mốc ổn định" title="Điểm thay đổi ra sao, các tỉnh chuyển hồ sơ thế nào?" description="So sánh hai mốc bằng tổng điểm, sau đó đọc cấu trúc lĩnh vực chuẩn hóa, không gian PCA và luồng chuyển giữa các hồ sơ." aside={<p className="status">{f.from}–{f.to} · n = {model.n} tỉnh</p>} />
    <FilterBar label="Bộ lọc thay đổi và phân nhóm" summary={`K = ${model.selectedK} · ${model.selectionMode === 'auto' ? 'tự chọn' : 'thủ công'}`} onReset={reset}>
      <label>Phạm vi<select value={f.scale} onChange={(event) => change({ scale: scaleOf(event.target.value) })}><option value="six">Tổng 6 lĩnh vực gốc</option><option value="eight">Tổng PAPI (8 lĩnh vực)</option></select></label>
      <label>Từ năm<select value={f.from} onChange={(event) => change({ from: Number(event.target.value) })}>{cfg.years.filter((year) => year < f.to).map((year) => <option key={year}>{year}</option>)}</select></label>
      <label>Đến năm<select value={f.to} onChange={(event) => change({ to: Number(event.target.value) })}>{cfg.years.filter((year) => year > f.from).map((year) => <option key={year}>{year}</option>)}</select></label>
      <label>Số hồ sơ K<select value={f.k} onChange={(event) => change({ k: event.target.value === 'auto' ? 'auto' : Number(event.target.value) })}><option value="auto">Tự chọn 2–6</option>{[2, 3, 4, 5, 6].map((item) => <option key={item} value={item}>{item} hồ sơ</option>)}</select></label>
    </FilterBar>
    <KpiGrid>
      <KpiCard label="Trung vị thay đổi" value={d.changes.median === null ? '—' : deltaFmt.format(d.changes.median)} detail={`${f.from} → ${f.to}`} tone={(d.changes.median ?? 0) >= 0 ? 'positive' : 'negative'} />
      <KpiCard label="Số hồ sơ được chọn" value={`K = ${model.selectedK}`} detail={model.selectionMode === 'auto' ? 'Tối ưu silhouette trong K=2–6' : 'Người dùng chọn thủ công'} tone="accent" />
      <KpiCard label="Silhouette" value={model.silhouette === null ? '—' : scoreFmt.format(model.silhouette)} detail="Cao hơn nghĩa là nhóm tách rõ hơn" />
      <KpiCard label="Tỉnh đổi hồ sơ" value={`${changedCount}/${model.n}`} detail="So sánh nhãn ổn định đầu–cuối" tone={changedCount ? 'negative' : 'positive'} />
    </KpiGrid>
    <InsightCard label="Phương pháp cần nhớ">
      <p>Mỗi mốc được chuẩn hóa z-score trong năm, KMeans dùng <strong>n_init=50</strong> và <strong>random_state=42</strong>. Nhãn A–F ổn định để so sánh hai mốc, chỉ mô tả hồ sơ tương đồng và không phải thứ hạng.</p>
    </InsightCard>

    <section className="dashboard-grid dynamics-story-grid" aria-label="Năm biểu đồ thay đổi và phân nhóm">
      <ChartCard className="chart-half" eyebrow="01 · Tăng" title="Những tỉnh tăng mạnh nhất" description={`Tối đa 8 tỉnh có chênh lệch dương lớn nhất từ ${f.from} đến ${f.to}.`} footer={<ChartMeta source={d.changes.source} unit={d.changes.unit} n={`${d.changes.n} tỉnh`} caveats={d.changes.caveats} />}>
        <CartesianChart title="8 tỉnh tăng nhiều nhất" summary="Thanh dài hơn là mức tăng tổng điểm PAPI lớn hơn." data={changeBars(d.changes.top8.slice(0, 8), uiColors.positive)} height={360} layout={{ xaxis: { title: { text: 'Thay đổi điểm' }, zeroline: true }, yaxis: { automargin: true }, showlegend: false, margin: { l: 112, r: 20, t: 14, b: 52 } }}><table><thead><tr><th>Tỉnh</th><th>Thay đổi</th></tr></thead><tbody>{d.changes.top8.slice(0, 8).map((row) => <tr key={row.provinceVi}><th>{row.provinceVi}</th><td>{deltaFmt.format(row.change ?? 0)}</td></tr>)}</tbody></table></CartesianChart>
      </ChartCard>
      <ChartCard className="chart-half" eyebrow="02 · Giảm" title="Những tỉnh giảm mạnh nhất" description="Tối đa 8 tỉnh có chênh lệch thấp nhất; số âm là giảm điểm." footer={<ChartMeta source={d.changes.source} unit={d.changes.unit} n={`${d.changes.n} tỉnh`} caveats={d.changes.caveats} />}>
        <CartesianChart title="8 tỉnh giảm nhiều nhất" summary="Thanh nằm về bên trái 0 cho thấy tổng điểm giảm." data={changeBars(d.changes.bottom8.slice(0, 8), uiColors.negative)} height={360} layout={{ xaxis: { title: { text: 'Thay đổi điểm' }, zeroline: true }, yaxis: { automargin: true }, showlegend: false, margin: { l: 112, r: 20, t: 14, b: 52 } }}><table><thead><tr><th>Tỉnh</th><th>Thay đổi</th></tr></thead><tbody>{d.changes.bottom8.slice(0, 8).map((row) => <tr key={row.provinceVi}><th>{row.provinceVi}</th><td>{deltaFmt.format(row.change ?? 0)}</td></tr>)}</tbody></table></CartesianChart>
      </ChartCard>
      <ChartCard className="chart-medium" eyebrow="03 · Centroid" title="Mỗi hồ sơ mạnh, yếu ở lĩnh vực nào?" description="Heatmap dùng z-score trong năm; màu xanh là cao hơn mặt bằng năm, màu đỏ là thấp hơn." footer={<ChartMeta source={model.source} unit={model.unit} n={`${model.n} tỉnh`} caveats={model.caveats} />}>
        <div className="profile-controls" role="group" aria-label="Chọn hồ sơ tỉnh">{clusterKeys.map((key) => <button key={key} aria-pressed={active === key} onClick={() => setActiveCluster(key)}>{clusterName(key)}</button>)}</div>
        <CartesianChart title="Bản đồ nhiệt hồ sơ A–F" summary="Mỗi hàng là centroid chuẩn hóa của một hồ sơ ở hai mốc; dùng nút Hồ sơ A–F để chọn bằng bàn phím." data={centroidHeatmap} height={390} onClick={(event) => { const point = event.points?.[0]; const indexes = Array.isArray(point?.pointNumber) ? point.pointNumber : point?.pointIndex; const index = Array.isArray(indexes) ? indexes[1] : undefined; if (typeof index === 'number') setActiveCluster(model.centroids[index]?.cluster ?? null) }} layout={{ margin: { l: 92, r: 24, t: 14, b: 68 } }}>
          <table><thead><tr><th>Hồ sơ</th><th>Đặc điểm</th><th>Đầu</th><th>Cuối</th></tr></thead><tbody>{model.centroids.map((row) => <tr key={row.cluster}><th>{clusterName(row.cluster)}</th><td>{row.descriptor}</td><td>{row.nStart}</td><td>{row.nEnd}</td></tr>)}</tbody></table>
        </CartesianChart>
        <details className="method-details"><summary>Thông tin phương pháp</summary><p>Chuẩn hóa riêng từng năm; tự chọn K theo silhouette hoặc dùng K do người dùng phê duyệt. PCA chỉ để chiếu không gian hồ sơ, không thay đổi phân nhóm.</p></details>
        {activeCentroid && <div className="nearby-provinces" aria-live="polite"><h3>{clusterName(active)}: {nearby.length} tỉnh ở mốc cuối</h3><small>{activeCentroid.descriptor}</small><p><strong>Ví dụ:</strong> {nearby.slice(0, 6).map((row) => row.provinceVi).join(', ')}{nearby.length > 6 ? '…' : ''}</p><details><summary>Xem đủ {nearby.length} tỉnh</summary><ul>{nearby.map((row) => <li key={row.provinceVi}>{row.provinceVi} <small>{row.region}</small></li>)}</ul></details></div>}
      </ChartCard>
      <ChartCard className="chart-wide" eyebrow="04 · PCA" title="Các tỉnh dịch chuyển trong không gian hồ sơ" description="Vòng tròn rỗng là mốc đầu, hình thoi là mốc cuối; đoạn nối chỉ hướng dịch chuyển của cùng một tỉnh." footer={<ChartMeta source={model.source} unit="hai thành phần PCA" n={`${model.n} tỉnh`} caveats={[`PC1 + PC2 giải thích ${scoreFmt.format(model.pcaVariance.reduce((sum, item) => sum + item, 0) * 100)}% phương sai.`]} />}>
        <CartesianChart title="Dịch chuyển PCA đầu–cuối" summary="Màu điểm là hồ sơ ổn định A–F tại từng mốc." data={pca} height={470} layout={{ xaxis: { title: { text: 'PC1' }, zeroline: true }, yaxis: { title: { text: 'PC2' }, zeroline: true }, legend: { orientation: 'h', y: -0.18 }, margin: { l: 62, r: 24, t: 20, b: 86 } }} />
      </ChartCard>
      <ChartCard className="chart-full" eyebrow="05 · Chuyển hồ sơ" title="Luồng chuyển nào phổ biến nhất?" description="Hàng là hồ sơ đầu, cột là hồ sơ cuối; đường chéo là các tỉnh giữ nguyên hồ sơ." footer={<ChartMeta source={model.source} unit="số tỉnh" n={`${model.transitions.length} luồng có quan sát`} caveats={model.caveats} />}>
        <CartesianChart title="Ma trận chuyển hồ sơ đầu–cuối" summary="Màu đậm hơn biểu thị nhiều tỉnh hơn trong một luồng chuyển." data={transitionHeatmap} height={390} layout={{ xaxis: { title: { text: `Hồ sơ mốc cuối · ${f.to}` } }, yaxis: { title: { text: `Hồ sơ mốc đầu · ${f.from}` }, autorange: 'reversed' }, margin: { l: 112, r: 28, t: 20, b: 64 } }} />
      </ChartCard>
    </section>

    <section className="chart-card dynamics-table"><header className="chart-card-header"><div><p className="eyebrow">Bảng kiểm chứng</p><h2>Toàn bộ chênh lệch tỉnh</h2><p>Dùng bảng để tra cứu số chính xác phía sau hai biểu đồ cực trị.</p></div></header><details><summary>Xem tất cả tỉnh</summary><div className="table-tools"><label>Tìm tỉnh<input aria-label="Tìm tỉnh" value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Nhập tên tỉnh" /></label><span>{allRows.length}/{d.changes.rows.length} tỉnh</span></div><div className="table-scroll"><table><thead><tr><th aria-sort={sortDirection('provinceVi')}><button aria-label={sortAction('provinceVi', 'Tỉnh')} onClick={() => setSortField('provinceVi')}>Tỉnh {sort === 'provinceVi' && (descending ? '↓' : '↑')}</button></th><th aria-sort={sortDirection('fromScore')}><button aria-label={sortAction('fromScore', `Điểm năm ${f.from}`)} onClick={() => setSortField('fromScore')}>{f.from} {sort === 'fromScore' && (descending ? '↓' : '↑')}</button></th><th aria-sort={sortDirection('toScore')}><button aria-label={sortAction('toScore', `Điểm năm ${f.to}`)} onClick={() => setSortField('toScore')}>{f.to} {sort === 'toScore' && (descending ? '↓' : '↑')}</button></th><th aria-sort={sortDirection('change')}><button aria-label={sortAction('change', 'Thay đổi')} onClick={() => setSortField('change')}>Thay đổi {sort === 'change' && (descending ? '↓' : '↑')}</button></th></tr></thead><tbody>{allRows.map((row) => <tr key={row.provinceVi} className={row.provinceVi === contextProvince ? 'selected-row' : ''}><th>{row.provinceVi}<small>{row.region}</small></th><td>{scoreFmt.format(row.fromScore ?? 0)}</td><td>{scoreFmt.format(row.toScore ?? 0)}</td><td>{deltaFmt.format(row.change ?? 0)}</td></tr>)}</tbody></table></div></details><ChartMeta source={d.changes.source} unit={d.measure.unit} n={`${d.changes.rowCount} tỉnh`} caveats={result.meta.caveats} /></section>
    <section className="story"><p className="eyebrow">Bước đọc tiếp · Human-in-the-loop</p><h2>Đặt câu hỏi phân tích với trợ lý AI</h2><p>Ngữ cảnh phạm vi, hai mốc và tỉnh đang chọn được giữ lại; mọi đề xuất code phải hiện rõ và chờ bạn duyệt ở bước tiếp theo.</p><Link className="cta" to={`/ai-assistant?scale=${f.scale}&from=${f.from}&to=${f.to}${contextProvince ? `&province=${encodeURIComponent(contextProvince)}` : ''}`}>Mở Trợ lý AI</Link></section>
  </article>
}
