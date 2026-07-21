import { useEffect } from 'react'
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

const fmt = new Intl.NumberFormat('vi-VN', { maximumFractionDigits: 2 })
const scaleOf = (value: string | null): Scale => value === 'six' ? 'six' : 'eight'

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
  const reset = () => setParams({ scale: 'eight', year: '2024', x: 'D2', y: 'D1' })

  if (metadata.isLoading || query.isLoading) return <LoadingSkeleton label="Đang tải mối quan hệ lĩnh vực" />
  const error = metadata.error ?? query.error
  if (error) return <ErrorState title="Không tải được mối quan hệ lĩnh vực" description={error.message} action={<><button onClick={() => { void metadata.refetch(); void query.refetch() }}>Thử lại</button><button className="text-button" onClick={reset}>Đặt lại bộ lọc</button></>} />
  if (!cfg || !query.data || !query.data.data.pair.rows.length) return <EmptyState title="Chưa có dữ liệu mối quan hệ" description="Hãy chọn lại phạm vi, năm hoặc cặp lĩnh vực khác." action={<button onClick={reset}>Đặt lại bộ lọc</button>} />

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

  const heatmap: Data[] = [{
    type: 'heatmap', x: d.correlation.codes.map(compact), y: d.correlation.codes.map(compact),
    z: d.correlation.matrix.map((row, rowIndex) => row.map((value, columnIndex) => columnIndex <= rowIndex ? value : null)),
    customdata: d.correlation.matrix.map((row, rowIndex) => row.map((value, columnIndex) => [label(d.correlation.codes[columnIndex]), label(d.correlation.codes[rowIndex]), value])),
    colorscale: divergingScale, zmin: -1, zmax: 1, hoverongaps: false,
    hovertemplate: '%{customdata[0]} × %{customdata[1]}<br>r = %{z:.2f}<extra></extra>', colorbar: { title: { text: 'r' }, thickness: 12, outlinewidth: 0 },
  } as unknown as Data]
  const selectedProvince = params.get('province')
  const quadrantColors: Record<string, string> = { 'Cao–cao': uiColors.positive, 'Thấp–thấp': '#4C6A9C', 'Cao–thấp': uiColors.warning, 'Thấp–cao': '#8A6CB1' }
  const scatter: Data[] = Object.keys(quadrantColors).map((quadrant) => {
    const rows = d.pair.rows.filter((row) => row.quadrant === quadrant)
    return {
      type: 'scatter', mode: 'markers', name: quadrant,
      x: rows.map((row) => row.x), y: rows.map((row) => row.y), customdata: rows.map((row) => [row.provinceVi, row.region, row.quadrant]),
      marker: { color: quadrantColors[quadrant], size: rows.map((row) => row.provinceVi === selectedProvince ? 15 : 9), opacity: 0.84, line: { color: uiColors.ink, width: rows.map((row) => row.provinceVi === selectedProvince ? 2 : 0) } },
      hovertemplate: '<b>%{customdata[0]}</b><br>%{customdata[1]}<br>Nhóm: %{customdata[2]}<br>X: %{x:.2f}<br>Y: %{y:.2f}<extra></extra>',
    }
  })
  const regressionLine = [...d.regression.rows].filter((row) => row.x !== null && row.predicted !== null).sort((a, b) => (a.x ?? 0) - (b.x ?? 0))
  scatter.push({
    type: 'scatter', mode: 'lines', name: 'Đường hồi quy OLS',
    x: regressionLine.map((row) => row.x), y: regressionLine.map((row) => row.predicted),
    line: { color: uiColors.ink, width: 2.5 }, hoverinfo: 'skip',
  })
  const residualRows = [...d.regression.rows].sort((a, b) => Math.abs(b.residual ?? 0) - Math.abs(a.residual ?? 0)).slice(0, 12).reverse()
  const residuals: Data[] = [{
    type: 'bar', orientation: 'h', y: residualRows.map((row) => row.provinceVi), x: residualRows.map((row) => row.residual),
    customdata: residualRows.map((row) => row.region),
    marker: { color: residualRows.map((row) => (row.residual ?? 0) >= 0 ? uiColors.positive : uiColors.negative) },
    hovertemplate: '<b>%{y}</b><br>Sai lệch: %{x:+.2f}<br>%{customdata}<extra></extra>',
  }]
  const stdRows = [...d.standardDeviation.rows].sort((a, b) => (a.stdScore ?? 0) - (b.stdScore ?? 0))
  const standardDeviation: Data[] = [{
    type: 'bar', orientation: 'h', y: stdRows.map((row) => compact(row.code)), x: stdRows.map((row) => row.stdScore),
    customdata: stdRows.map((row) => [label(row.code), row.meanScore, row.n]), marker: { color: uiColors.primary },
    hovertemplate: '<b>%{customdata[0]}</b><br>Độ lệch chuẩn: %{x:.2f}<br>Trung bình: %{customdata[1]:.2f}<br>n = %{customdata[2]}<extra></extra>',
  }]
  const firstYear = cfg.years[0]
  const nextYear = cfg.years.find((item) => item > f.year) ?? f.year
  const dynamicsRange = f.year > firstYear ? { from: firstYear, to: f.year } : { from: f.year, to: nextYear }
  const pairTitle = `${compact(f.x)} × ${compact(f.y)}`

  return <article className="overview analysis-page">
    <DashboardPageHeader eyebrow="Mối quan hệ lĩnh vực · Không suy diễn nhân quả" title="Cùng biến thiên, không vội kết luận nguyên nhân" description="Đi từ ma trận toàn bộ lĩnh vực tới một cặp cụ thể, đường hồi quy, sai lệch địa phương và mức phân tán của từng chỉ số." aside={<p className="status">Snapshot {f.year} · n = {d.pair.n} tỉnh</p>} />
    <FilterBar label="Bộ lọc mối quan hệ lĩnh vực" summary={pairTitle} onReset={reset}>
      <label>Phạm vi<select value={f.scale} onChange={(event) => change({ scale: scaleOf(event.target.value) })}><option value="six">Tổng 6 lĩnh vực gốc</option><option value="eight">Tổng PAPI (8 lĩnh vực)</option></select></label>
      <label>Năm<select value={f.year} onChange={(event) => change({ year: Number(event.target.value) })}>{cfg.years.map((item) => <option key={item}>{item}</option>)}</select></label>
      <label>Lĩnh vực ngang<select value={f.x} onChange={(event) => change({ x: event.target.value })}>{d.availability.dimensions.map((code) => <option key={code} value={code} disabled={code === f.y}>{label(code)}</option>)}</select></label>
      <label>Lĩnh vực dọc<select value={f.y} onChange={(event) => change({ y: event.target.value })}>{d.availability.dimensions.map((code) => <option key={code} value={code} disabled={code === f.x}>{label(code)}</option>)}</select></label>
    </FilterBar>
    <KpiGrid>
      <KpiCard label="Pearson r" value={d.pair.pearsonR === null ? '—' : fmt.format(d.pair.pearsonR)} detail={pairTitle} tone="accent" />
      <KpiCard label="R² của hồi quy" value={d.regression.rSquared === null ? '—' : `${fmt.format(d.regression.rSquared * 100)}%`} detail={`Mức liên hệ ${d.regression.strength}`} />
      <KpiCard label="Tỉnh lệch xu hướng nhất" value={d.regression.largestResidualProvince || '—'} detail="Theo trị tuyệt đối residual" tone="negative" />
      <KpiCard label="Quan sát hợp lệ" value={`${d.regression.n} tỉnh`} detail="Đủ dữ liệu ở cả hai lĩnh vực" />
    </KpiGrid>
    <InsightCard label="Cách đọc đúng">
      <p>Pearson r mô tả mức cùng biến thiên; R² cho biết tỷ lệ biến thiên tuyến tính được giải thích trong mẫu. <strong>{d.regression.largestResidualProvince}</strong> xa đường hồi quy nhất, nhưng đây vẫn không phải bằng chứng nhân quả.</p>
    </InsightCard>

    <section className="dashboard-grid dimension-story-grid" aria-label="Bốn biểu đồ mối quan hệ lĩnh vực">
      <ChartCard className="chart-medium" eyebrow="01 · Toàn ma trận" title="Lĩnh vực nào thường đi cùng nhau?" description="Chỉ hiển thị nửa tam giác dưới để mỗi cặp xuất hiện một lần; chọn ô để đổi hai trục." footer={<ChartMeta source={d.correlation.source} unit={d.correlation.unit} n={`${d.correlation.n} tỉnh`} caveats={d.correlation.caveats} />}>
        <CartesianChart title="Ma trận tương quan nửa dưới" summary="Thang màu phân kỳ biểu thị hướng và độ mạnh tương quan; nửa trên để trống." data={heatmap} height={420} onClick={(event) => { const point = event.points?.[0]; const indexes = Array.isArray(point?.pointNumber) ? point.pointNumber : point?.pointIndex; if (Array.isArray(indexes) && indexes[0] < indexes[1]) change({ x: d.correlation.codes[indexes[0]], y: d.correlation.codes[indexes[1]] }) }} layout={{ margin: { l: 96, r: 30, t: 18, b: 72 } }}>
          <table><thead><tr><th>Lĩnh vực</th><th>Điểm TB</th><th>Độ lệch chuẩn</th><th>n</th></tr></thead><tbody>{d.standardDeviation.rows.map((row) => <tr key={row.code}><th>{label(row.code)}</th><td>{fmt.format(row.meanScore ?? 0)}</td><td>{fmt.format(row.stdScore ?? 0)}</td><td>{row.n}</td></tr>)}</tbody></table>
        </CartesianChart>
      </ChartCard>
      <ChartCard className="chart-wide" eyebrow="02 · Độ phân tán" title="Lĩnh vực nào khác biệt nhiều giữa các tỉnh?" description="Độ lệch chuẩn lớn hơn nghĩa là điểm tỉnh phân tán rộng hơn quanh trung bình." footer={<ChartMeta source={d.standardDeviation.source} unit={d.standardDeviation.unit} n={`${d.standardDeviation.rowCount} lĩnh vực`} caveats={d.standardDeviation.caveats} />}>
        <CartesianChart title="Độ phân tán theo lĩnh vực" summary="Thanh ngang biểu thị độ lệch chuẩn giữa các tỉnh." data={standardDeviation} height={420} layout={{ xaxis: { title: { text: 'Độ lệch chuẩn' }, rangemode: 'tozero' }, yaxis: { automargin: true }, showlegend: false, margin: { l: 112, r: 24, t: 18, b: 54 } }} />
      </ChartCard>
      <ChartCard className="chart-wide" eyebrow="03 · Cặp đang xem" title={pairTitle} description={`${label(f.x)} và ${label(f.y)}; đường đen là hồi quy OLS, đường chấm là trung bình mẫu.`} footer={<ChartMeta source={d.pair.source} unit={d.pair.unit} n={`${d.pair.n} tỉnh`} caveats={[...(d.pair.caveats ?? []), ...(result.meta.caveats ?? [])]} />}>
        <CartesianChart className="dimension-scatter" title="Phân tán theo hai lĩnh vực" summary={`Lĩnh vực ngang: ${label(f.x)}. Lĩnh vực dọc: ${label(f.y)}. Đường dọc và ngang là điểm trung bình; màu thể hiện bốn nhóm cao-thấp.`} data={scatter} height={440} layout={{ xaxis: { title: { text: compact(f.x) } }, yaxis: { title: { text: compact(f.y) } }, shapes: [{ type: 'line', x0: d.pair.xMean ?? 0, x1: d.pair.xMean ?? 0, y0: 0, y1: 1, yref: 'paper', line: { color: uiColors.muted, dash: 'dot' } }, { type: 'line', x0: 0, x1: 1, xref: 'paper', y0: d.pair.yMean ?? 0, y1: d.pair.yMean ?? 0, line: { color: uiColors.muted, dash: 'dot' } }], legend: { orientation: 'h', y: -0.22 }, margin: { l: 72, r: 24, t: 18, b: 98 } }}>
          <table><thead><tr><th>Tỉnh</th><th>{compact(f.x)}</th><th>{compact(f.y)}</th><th>Nhóm</th></tr></thead><tbody>{d.pair.rows.map((row) => <tr key={row.provinceVi}><th>{row.provinceVi}</th><td>{fmt.format(row.x ?? 0)}</td><td>{fmt.format(row.y ?? 0)}</td><td>{row.quadrant}</td></tr>)}</tbody></table>
        </CartesianChart>
      </ChartCard>
      <ChartCard className="chart-medium" eyebrow="04 · Ngoại lệ" title="Tỉnh nào xa đường hồi quy nhất?" description="Residual dương là cao hơn dự đoán tuyến tính, residual âm là thấp hơn; chỉ hiển thị 12 trị tuyệt đối lớn nhất." footer={<ChartMeta source={d.regression.source} unit={d.regression.unit} n={`${d.regression.n} tỉnh`} caveats={d.regression.caveats} />}>
        <CartesianChart title="Sai lệch so với đường hồi quy" summary="Mười hai tỉnh có residual tuyệt đối lớn nhất." data={residuals} height={440} layout={{ xaxis: { title: { text: 'Residual' }, zeroline: true, zerolinewidth: 2 }, yaxis: { automargin: true }, showlegend: false, margin: { l: 112, r: 22, t: 18, b: 54 } }} />
      </ChartCard>
    </section>
    <section className="story"><p className="eyebrow">Bước đọc tiếp</p><h2>Xem thay đổi và nhóm tương đồng</h2><p>Giữ phạm vi và ngữ cảnh tỉnh để xem chênh lệch giữa hai mốc và các hồ sơ gần nhau.</p><Link className="cta" to={`/dynamics?scale=${f.scale}&from=${dynamicsRange.from}&to=${dynamicsRange.to}${preserve}`}>Mở Thay đổi & phân nhóm</Link></section>
  </article>
}
