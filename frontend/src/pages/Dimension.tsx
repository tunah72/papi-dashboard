import { useEffect, useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import type { Data, Layout } from 'plotly.js'
import { useSearchParams } from 'react-router-dom'

import { api, type Scale } from '../api/client'
import { CartesianChart } from '../components/CartesianChart'
import {
  ChartCard,
  ChartInsight,
  ChartMeta,
  DashboardPageHeader,
  EmptyState,
  ErrorState,
  FilterBar,
  KpiCard,
  KpiGrid,
  LoadingSkeleton,
} from '../components/dashboard'
import { colorForDimension, colorForRegion, divergingScale, shortRegionLabel, uiColors } from '../theme/chartTheme'

const fmt = new Intl.NumberFormat('vi-VN', { maximumFractionDigits: 2 })
const compactNumber = new Intl.NumberFormat('vi-VN', { maximumFractionDigits: 1 })
const signed = new Intl.NumberFormat('vi-VN', { maximumFractionDigits: 2, signDisplay: 'exceptZero' })
const scaleOf = (value: string | null): Scale => value === 'six' ? 'six' : 'eight'
const focusIds = new Set(['dimension-correlation', 'dimension-pair', 'dimension-residual', 'dimension-variation'])
const score = (value: number | null) => value === null ? '—' : fmt.format(value)

export function Dimension() {
  const [params, setParams] = useSearchParams()
  const [hoveredRegion, setHoveredRegion] = useState<string | null>(null)
  const [residualSort, setResidualSort] = useState<'absolute' | 'direction'>('absolute')
  const [variationSort, setVariationSort] = useState<'sd' | 'mean'>('sd')
  const [variationTarget, setVariationTarget] = useState<'x' | 'y'>('x')
  const scale = scaleOf(params.get('scale'))
  const metadata = useQuery({ queryKey: ['metadata'], queryFn: api.metadata })
  const cfg = metadata.data?.data.scales.find((item) => item.id === scale)
  const year = cfg?.years.includes(Number(params.get('year'))) ? Number(params.get('year')) : (cfg?.years.at(-1) ?? 2024)
  const available = cfg?.dimensions ?? []
  const rawX = params.get('x')
  const rawY = params.get('y')
  const x = available.includes(rawX ?? '') ? rawX! : (available[1] ?? available[0] ?? 'D2')
  const y = available.includes(rawY ?? '') && rawY !== x ? rawY! : (available.find((code) => code !== x) ?? 'D1')
  const focused = focusIds.has(params.get('focus') ?? '') ? params.get('focus') : null
  const query = useQuery({ queryKey: ['dimensions', scale, year, x, y], queryFn: () => api.dimensions(scale, year, x, y), enabled: Boolean(cfg && x !== y) })

  useEffect(() => {
    const filters = query.data?.meta.filters
    if (!filters) return
    const canonical = new URLSearchParams({ scale: filters.scale, year: String(filters.year), x: filters.x, y: filters.y })
    const province = params.get('province')
    if (province) canonical.set('province', province)
    if (focused) canonical.set('focus', focused)
    if (params.toString() !== canonical.toString()) setParams(canonical, { replace: true })
  }, [focused, metadata.data, params, query.data, setParams])

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
  const selectedProvince = d.pair.rows.some((row) => row.provinceVi === params.get('province')) ? params.get('province') : null
  const update = (changes: Record<string, string | null>) => setParams((current) => {
    const next = new URLSearchParams(current)
    Object.entries(changes).forEach(([key, nextValue]) => nextValue === null ? next.delete(key) : next.set(key, nextValue))
    return next
  })
  const change = (next: Partial<{ scale: Scale; year: number; x: string; y: string }>) => {
    const nextScale = next.scale ?? f.scale
    const nextCfg = metadata.data!.data.scales.find((item) => item.id === nextScale)!
    const dimensions = nextCfg.dimensions
    let nextX = next.scale ? (dimensions[1] ?? dimensions[0]) : (next.x ?? f.x)
    let nextY = next.scale ? dimensions[0] : (next.y ?? f.y)
    if (nextX === nextY && next.x) nextY = dimensions.find((code) => code !== nextX) ?? nextY
    if (nextX === nextY && next.y) nextX = dimensions.find((code) => code !== nextY) ?? nextX
    const target = new URLSearchParams({
      scale: nextScale,
      year: String(next.scale ? nextCfg.years.at(-1)! : (next.year ?? f.year)),
      x: nextX,
      y: nextY,
    })
    if (selectedProvince) target.set('province', selectedProvince)
    if (focused) target.set('focus', focused)
    setParams(target)
  }
  const focus = (id: string, activeContext?: string) => ({ id, activeContext, open: focused === id, onOpenChange: (open: boolean) => update({ focus: open ? id : null }) })
  const pinProvince = (province: unknown) => { if (typeof province === 'string') update({ province }) }

  const codes = d.correlation.codes
  const selectedIndexes = [codes.indexOf(f.x), codes.indexOf(f.y)]
  const selectedRow = Math.max(...selectedIndexes)
  const selectedColumn = Math.min(...selectedIndexes)
  const heatmap: Data[] = [{
    type: 'heatmap', x: codes.map(compact), y: codes.map(compact),
    z: d.correlation.matrix.map((row, rowIndex) => row.map((value, columnIndex) => columnIndex < rowIndex ? value : null)),
    text: d.correlation.matrix.map((row, rowIndex) => row.map((value, columnIndex) => columnIndex < rowIndex && value !== null ? value.toFixed(2) : '')),
    texttemplate: '%{text}', textfont: { size: 10 },
    customdata: d.correlation.matrix.map((row, rowIndex) => row.map((value, columnIndex) => [
      label(codes[columnIndex]), label(codes[rowIndex]), value,
      d.correlation.counts[rowIndex][columnIndex], d.correlation.strengths[rowIndex][columnIndex],
    ])),
    colorscale: divergingScale, zmin: -1, zmax: 1, hoverongaps: false,
    hovertemplate: '<b>%{customdata[0]} × %{customdata[1]}</b><br>r = %{z:.2f} · %{customdata[4]}<br>n = %{customdata[3]} tỉnh<extra>Liên hệ quan sát</extra>',
    colorbar: {
      title: { text: 'Pearson r', side: 'top' },
      orientation: 'h', x: 0.55, xanchor: 'center', y: 1.03, yanchor: 'bottom',
      len: 0.52, thickness: 8, outlinewidth: 0,
    },
  } as unknown as Data]
  const heatmapPairs = codes.flatMap((rowCode, rowIndex) => codes.slice(0, rowIndex).map((columnCode, columnIndex) => ({
    x: columnCode, y: rowCode, r: d.correlation.matrix[rowIndex][columnIndex], n: d.correlation.counts[rowIndex][columnIndex],
  })))
  const pairCounts = heatmapPairs.map((item) => item.n)
  const correlationN = Math.min(...pairCounts) === Math.max(...pairCounts) ? `${pairCounts[0]} tỉnh/cặp` : `${Math.min(...pairCounts)}–${Math.max(...pairCounts)} tỉnh/cặp`
  const heatmapView = (height: number) => <CartesianChart title="Ma trận tương quan nửa dưới" summary="Mỗi ô là Pearson r của một cặp; đường viền đánh dấu cặp đang chọn." data={heatmap} height={height} onClick={(event) => {
    const point = event.points?.[0]
    const indexes = Array.isArray(point?.pointNumber) ? point.pointNumber : point?.pointIndex
    if (Array.isArray(indexes) && indexes[0] > indexes[1]) change({ x: codes[indexes[1]], y: codes[indexes[0]] })
  }} layout={{ shapes: [{ type: 'rect', x0: selectedColumn - 0.48, x1: selectedColumn + 0.48, y0: selectedRow - 0.48, y1: selectedRow + 0.48, line: { color: uiColors.ink, width: 3 }, fillcolor: 'rgba(0,0,0,0)' }], margin: { l: 78, r: 10, t: 58, b: 82 } }}>
    <div className="chart-table-scroll"><table><caption className="sr-only">Bảng tương quan giữa từng cặp lĩnh vực</caption><thead><tr><th>Cặp lĩnh vực</th><th>r</th><th>n</th><th>Chọn</th></tr></thead><tbody>{heatmapPairs.map((item) => <tr key={`${item.x}-${item.y}`}><th scope="row">{compact(item.x)} × {compact(item.y)}</th><td>{score(item.r)}</td><td>{item.n}</td><td><button type="button" aria-pressed={(f.x === item.x && f.y === item.y) || (f.x === item.y && f.y === item.x)} onClick={() => change({ x: item.x, y: item.y })}>Chọn cặp</button></td></tr>)}</tbody></table></div>
  </CartesianChart>

  const regressionByProvince = new Map(d.regression.rows.map((row) => [row.provinceVi, row]))
  const regions = [...new Set(d.pair.rows.map((row) => row.region))]
  const scatter: Data[] = regions.map((region) => {
    const rows = d.pair.rows.filter((row) => row.region === region)
    return {
      type: 'scatter', mode: 'markers+text', name: shortRegionLabel(region), x: rows.map((row) => row.x), y: rows.map((row) => row.y),
      text: rows.map((row) => row.provinceVi === selectedProvince ? row.provinceVi : ''), textposition: 'top center',
      customdata: rows.map((row) => [row.provinceVi, row.region, row.quadrant, regressionByProvince.get(row.provinceVi)?.residual]),
      marker: {
        color: colorForRegion(region), size: rows.map((row) => row.provinceVi === selectedProvince ? 15 : 9),
        symbol: rows.map((row) => row.provinceVi === selectedProvince ? 'diamond' : 'circle'),
        opacity: hoveredRegion && hoveredRegion !== region ? 0.22 : 0.84,
        line: { color: uiColors.ink, width: rows.map((row) => row.provinceVi === selectedProvince ? 2.5 : 0.7) },
      },
      hovertemplate: '<b>%{customdata[0]}</b><br>%{customdata[1]}<br>X = %{x:.2f} · Y = %{y:.2f}<br>%{customdata[2]} · residual %{customdata[3]:+.2f}<extra></extra>',
    } as unknown as Data
  })
  const regressionLine = [...d.regression.rows].filter((row) => row.x !== null && row.predicted !== null).sort((a, b) => (a.x ?? 0) - (b.x ?? 0))
  scatter.push({
    type: 'scatter', mode: 'lines', name: 'Hồi quy OLS', x: regressionLine.map((row) => row.x), y: regressionLine.map((row) => row.predicted),
    line: { color: uiColors.ink, width: 2.6 }, hoverinfo: 'skip',
  })
  const pairTitle = `${compact(f.x)} × ${compact(f.y)}`
  const pairValues = d.pair.rows.flatMap((row) => [row.x, row.y]).filter((item): item is number => item !== null)
  const pairMin = Math.min(...pairValues)
  const pairMax = Math.max(...pairValues)
  const pairPadding = Math.max((pairMax - pairMin) * 0.16, 0.35)
  const pairDomain: [number, number] = [Math.max(1, pairMin - pairPadding), Math.min(10, pairMax + pairPadding)]
  const scatterView = (height: number) => <CartesianChart className="dimension-scatter" title="Phân tán theo hai lĩnh vực" summary={`Lĩnh vực ngang: ${label(f.x)}. Lĩnh vực dọc: ${label(f.y)}. Màu biểu thị vùng; đường chấm là trung bình mẫu.`} data={scatter} height={height} onHover={(event) => {
    const raw = event.points?.[0]?.customdata
    if (Array.isArray(raw) && typeof raw[1] === 'string') setHoveredRegion(raw[1])
  }} onUnhover={() => setHoveredRegion(null)} onClick={(event) => { const raw = event.points?.[0]?.customdata; if (Array.isArray(raw)) pinProvince(raw[0]) }} layout={{
    xaxis: { title: { text: compact(f.x) }, range: pairDomain }, yaxis: { title: { text: compact(f.y) }, range: pairDomain, scaleanchor: 'x', scaleratio: 1 },
    shapes: [{ type: 'line', x0: d.pair.xMean ?? 0, x1: d.pair.xMean ?? 0, y0: 0, y1: 1, yref: 'paper', line: { color: uiColors.muted, dash: 'dot' } }, { type: 'line', x0: 0, x1: 1, xref: 'paper', y0: d.pair.yMean ?? 0, y1: d.pair.yMean ?? 0, line: { color: uiColors.muted, dash: 'dot' } }],
    legend: { orientation: 'h', y: -0.25 }, margin: { l: 64, r: 24, t: 22, b: 100 },
  }}>
    <div className="chart-table-scroll"><table><caption className="sr-only">Bảng điểm hai lĩnh vực và residual theo tỉnh</caption><thead><tr><th>Tỉnh</th><th>Vùng</th><th>{compact(f.x)}</th><th>{compact(f.y)}</th><th>Residual</th></tr></thead><tbody>{d.pair.rows.map((row) => <tr key={row.provinceVi}><th scope="row"><button type="button" aria-pressed={row.provinceVi === selectedProvince} onClick={() => pinProvince(row.provinceVi)}>{row.provinceVi}</button></th><td>{shortRegionLabel(row.region)}</td><td>{score(row.x)}</td><td>{score(row.y)}</td><td>{score(regressionByProvince.get(row.provinceVi)?.residual ?? null)}</td></tr>)}</tbody></table></div>
  </CartesianChart>

  const residualSample = [...d.regression.rows].filter((row) => row.residual !== null).sort((a, b) => Math.abs(b.residual ?? 0) - Math.abs(a.residual ?? 0)).slice(0, 12)
  const residualRows = [...residualSample].sort((a, b) => residualSort === 'absolute' ? Math.abs(b.residual ?? 0) - Math.abs(a.residual ?? 0) : (b.residual ?? 0) - (a.residual ?? 0))
  const residualShapes: Layout['shapes'] = residualRows.map((row) => ({ type: 'line', x0: 0, x1: row.residual ?? 0, y0: row.provinceVi, y1: row.provinceVi, line: { color: uiColors.border, width: 3 } }))
  const residualData: Data[] = [{
    type: 'scatter', mode: 'markers+text', x: residualRows.map((row) => row.residual), y: residualRows.map((row) => row.provinceVi),
    text: residualRows.map((row) => signed.format(row.residual ?? 0)), textposition: 'middle right',
    customdata: residualRows.map((row) => [row.provinceVi, row.region, row.y, row.predicted, row.residual]),
    marker: {
      color: residualRows.map((row) => (row.residual ?? 0) >= 0 ? uiColors.positive : uiColors.negative),
      size: residualRows.map((row) => row.provinceVi === selectedProvince ? 14 : 10),
      symbol: residualRows.map((row) => row.provinceVi === selectedProvince ? 'diamond' : 'circle'),
      line: { color: uiColors.ink, width: residualRows.map((row) => row.provinceVi === selectedProvince ? 2.5 : 0.7) },
    },
    hovertemplate: '<b>%{customdata[0]}</b><br>%{customdata[1]}<br>Thực tế %{customdata[2]:.2f} · dự đoán %{customdata[3]:.2f}<br>Residual %{customdata[4]:+.2f}<extra></extra>', showlegend: false,
  } as unknown as Data]
  const residualView = (height: number) => <CartesianChart title="Sai lệch so với đường hồi quy" summary="Mười hai tỉnh có trị tuyệt đối residual lớn nhất; dấu cho biết hướng lệch." data={residualData} height={height} onClick={(event) => { const raw = event.points?.[0]?.customdata; if (Array.isArray(raw)) pinProvince(raw[0]) }} layout={{ xaxis: { title: { text: `Residual của ${compact(f.y)}` }, zeroline: true, zerolinewidth: 2 }, yaxis: { categoryorder: 'array', categoryarray: residualRows.map((row) => row.provinceVi), autorange: 'reversed', automargin: true }, shapes: residualShapes, margin: { l: 106, r: 58, t: 22, b: 54 } }}>
    <div className="chart-table-scroll"><table><caption className="sr-only">Bảng mười hai residual lớn nhất</caption><thead><tr><th>Tỉnh</th><th>Thực tế</th><th>Dự đoán</th><th>Residual</th></tr></thead><tbody>{residualRows.map((row) => <tr key={row.provinceVi}><th scope="row"><button type="button" aria-pressed={row.provinceVi === selectedProvince} onClick={() => pinProvince(row.provinceVi)}>{row.provinceVi}</button></th><td>{score(row.y)}</td><td>{score(row.predicted)}</td><td>{row.residual === null ? '—' : signed.format(row.residual)}</td></tr>)}</tbody></table></div>
  </CartesianChart>

  const variationRows = [...d.standardDeviation.rows].sort((a, b) => variationSort === 'sd' ? (b.stdScore ?? -Infinity) - (a.stdScore ?? -Infinity) : (b.meanScore ?? -Infinity) - (a.meanScore ?? -Infinity))
  const variationShapes: Layout['shapes'] = variationRows.map((row) => ({
    type: 'line', x0: Math.max(1, (row.meanScore ?? 1) - (row.stdScore ?? 0)), x1: Math.min(10, (row.meanScore ?? 1) + (row.stdScore ?? 0)), y0: compact(row.code), y1: compact(row.code),
    line: { color: colorForDimension(row.code), width: 5 },
  }))
  const variationData: Data[] = [{
    type: 'scatter', mode: 'markers+text', x: variationRows.map((row) => row.meanScore), y: variationRows.map((row) => compact(row.code)),
    text: variationRows.map((row) => `${row.meanScore === null ? '—' : compactNumber.format(row.meanScore)} ± ${row.stdScore === null ? '—' : compactNumber.format(row.stdScore)}`),
    textposition: variationRows.map((row) => (row.meanScore ?? 0) > 7 ? 'middle left' : 'middle right'), textfont: { size: 10 },
    customdata: variationRows.map((row) => [row.code, label(row.code), row.stdScore, row.n, row.minScore, row.maxScore]),
    marker: {
      color: variationRows.map((row) => colorForDimension(row.code)), size: 12,
      symbol: variationRows.map((row) => row.code === f.x ? 'diamond' : row.code === f.y ? 'square' : 'circle'),
      line: { color: uiColors.surface, width: 2 },
    },
    hovertemplate: '<b>%{customdata[1]}</b><br>Trung bình %{x:.2f} · SD %{customdata[2]:.2f}<br>Min–max %{customdata[4]:.2f}–%{customdata[5]:.2f}<br>n = %{customdata[3]} tỉnh<extra></extra>', showlegend: false,
  } as unknown as Data]
  const variationNs = variationRows.map((row) => row.n)
  const variationN = Math.min(...variationNs) === Math.max(...variationNs) ? `${variationNs[0]} tỉnh/lĩnh vực` : `${Math.min(...variationNs)}–${Math.max(...variationNs)} tỉnh/lĩnh vực`
  const variationView = (height: number) => <CartesianChart title="Trung bình và độ lệch chuẩn theo lĩnh vực" summary="Chấm là trung bình; đoạn thẳng biểu thị trung bình cộng hoặc trừ một độ lệch chuẩn trên thang 1–10." data={variationData} height={height} onClick={(event) => {
    const raw = event.points?.[0]?.customdata
    if (Array.isArray(raw) && typeof raw[0] === 'string') change(variationTarget === 'x' ? { x: raw[0] } : { y: raw[0] })
  }} layout={{ xaxis: { title: { text: 'Điểm lĩnh vực PAPI' }, range: [1, 10], dtick: 1 }, yaxis: { categoryorder: 'array', categoryarray: variationRows.map((row) => compact(row.code)), autorange: 'reversed', automargin: true }, shapes: variationShapes, margin: { l: 112, r: 92, t: 22, b: 54 } }}>
    <table><caption className="sr-only">Bảng trung bình và độ lệch chuẩn theo lĩnh vực</caption><thead><tr><th>Lĩnh vực</th><th>Trung bình</th><th>SD</th><th>n</th><th>Gán</th></tr></thead><tbody>{variationRows.map((row) => <tr key={row.code}><th scope="row">{label(row.code)}</th><td>{score(row.meanScore)}</td><td>{score(row.stdScore)}</td><td>{row.n}</td><td><button type="button" onClick={() => change(variationTarget === 'x' ? { x: row.code } : { y: row.code })}>Đặt làm {variationTarget.toUpperCase()}</button></td></tr>)}</tbody></table>
  </CartesianChart>

  const defaultYear = metadata.data!.data.scales.find((item) => item.id === 'eight')?.years.at(-1) ?? 2024
  const defaultSelection = f.scale === 'eight' && f.year === defaultYear && f.x === 'D2' && f.y === 'D1' && !selectedProvince && !focused

  return <article className="overview analysis-page dimension-redesign">
    <DashboardPageHeader eyebrow="MỐI QUAN HỆ LĨNH VỰC" title="Các lĩnh vực cùng biến thiên ra sao?" description="So sánh liên hệ tuyến tính, hình dạng phân phối và các tỉnh lệch khỏi xu hướng trong một năm." />
    <FilterBar label="Bộ lọc mối quan hệ lĩnh vực" summary={`Đang xem: ${pairTitle} · ${f.year} · ${f.scale === 'six' ? '6 lĩnh vực' : '8 lĩnh vực'}`} onReset={reset} resetDisabled={defaultSelection}>
      <label>Phạm vi<select value={f.scale} onChange={(event) => change({ scale: scaleOf(event.target.value) })}><option value="six">6 lĩnh vực gốc</option><option value="eight">8 lĩnh vực</option></select></label>
      <label>Năm<select value={f.year} onChange={(event) => change({ year: Number(event.target.value) })}>{cfg.years.map((item) => <option key={item}>{item}</option>)}</select></label>
      <label>Lĩnh vực ngang<select value={f.x} onChange={(event) => change({ x: event.target.value })}>{d.availability.dimensions.map((code) => <option key={code} value={code} disabled={code === f.y}>{label(code)}</option>)}</select></label>
      <label>Lĩnh vực dọc<select value={f.y} onChange={(event) => change({ y: event.target.value })}>{d.availability.dimensions.map((code) => <option key={code} value={code} disabled={code === f.x}>{label(code)}</option>)}</select></label>
    </FilterBar>
    <KpiGrid label="Chỉ số tóm tắt mối quan hệ lĩnh vực">
      <KpiCard label="Pearson r" value={d.pair.pearsonR === null ? '—' : fmt.format(d.pair.pearsonR)} detail="Mô tả, không nhân quả" />
      <KpiCard label="Mức phù hợp tuyến tính R²" value={d.regression.rSquared === null ? '—' : `${fmt.format(d.regression.rSquared * 100)}%`} detail="Mô tả, không nhân quả" />
      <KpiCard label="Số tỉnh hợp lệ" value={`${d.pair.n} tỉnh`} detail={`Đủ điểm ${pairTitle}`} />
      <KpiCard label="Lệch xu hướng nhiều nhất" value={d.regression.largestResidualProvince || '—'} detail="Theo trị tuyệt đối residual" />
    </KpiGrid>

    <section className="dimension-chart-grid" aria-label="Bốn biểu đồ mối quan hệ lĩnh vực">
      <ChartCard className="dimension-chart-card" eyebrow="01 · TOÀN BỘ CẶP" title="Cặp lĩnh vực nào liên hệ mạnh nhất?" insight={<ChartInsight>{d.insights.correlation}</ChartInsight>} focus={{ ...focus('dimension-correlation', pairTitle), content: heatmapView(570) }} footer={<ChartMeta source={d.correlation.source} unit={d.correlation.unit} n={correlationN} caveats={[...(d.correlation.caveats ?? []), 'Số tỉnh hợp lệ được tính riêng cho từng cặp.']} />}>
        {heatmapView(310)}
      </ChartCard>
      <ChartCard className="dimension-chart-card" eyebrow="02 · CẶP ĐANG CHỌN" title="Mối quan hệ của cặp đang chọn nhất quán ra sao?" insight={<ChartInsight>{d.insights.pair}</ChartInsight>} focus={{ ...focus('dimension-pair', selectedProvince ?? pairTitle), content: scatterView(570) }} footer={<ChartMeta source={d.pair.source} unit={d.pair.unit} n={`${d.pair.n} tỉnh`} caveats={[...(d.pair.caveats ?? []), ...(result.meta.caveats ?? [])]} />}>
        {scatterView(310)}
      </ChartCard>
      <ChartCard className="dimension-chart-card" eyebrow="03 · LỆCH KHỎI XU HƯỚNG" title="Tỉnh nào lệch khỏi xu hướng tuyến tính nhiều nhất?" action={<button type="button" className="chart-sort" onClick={() => setResidualSort((current) => current === 'absolute' ? 'direction' : 'absolute')}>Sắp xếp: {residualSort === 'absolute' ? 'Độ lệch' : 'Hướng'}</button>} insight={<ChartInsight>{d.insights.residual}</ChartInsight>} focus={{ ...focus('dimension-residual', selectedProvince ?? pairTitle), content: residualView(570) }} footer={<ChartMeta source={d.regression.source} unit={d.regression.unit} n={`${d.regression.n} tỉnh`} caveats={d.regression.caveats} />}>
        {residualView(310)}
      </ChartCard>
      <ChartCard className="dimension-chart-card" eyebrow="04 · MẶT BẰNG & PHÂN TÁN" title="Lĩnh vực nào có mặt bằng và độ phân tán lớn nhất?" action={<><button type="button" className="chart-sort" onClick={() => setVariationSort((current) => current === 'sd' ? 'mean' : 'sd')}>Sắp xếp: {variationSort === 'sd' ? 'SD' : 'Trung bình'}</button><button type="button" className="chart-sort" onClick={() => setVariationTarget((current) => current === 'x' ? 'y' : 'x')}>Gán click: {variationTarget.toUpperCase()}</button></>} insight={<ChartInsight>{d.insights.variation}</ChartInsight>} focus={{ ...focus('dimension-variation', pairTitle), content: variationView(540) }} footer={<ChartMeta source={d.standardDeviation.source} unit={d.standardDeviation.unit} n={variationN} caveats={d.standardDeviation.caveats} />}>
        {variationView(310)}
      </ChartCard>
    </section>
  </article>
}
