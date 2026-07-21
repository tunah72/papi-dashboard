import { useEffect, useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import type { Data, Layout } from 'plotly.js'
import { useNavigate, useSearchParams } from 'react-router-dom'

import { api, type Scale } from '../api/client'
import { CartesianChart } from '../components/CartesianChart'
import { PolarChart } from '../components/PolarChart'
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
import { colorForRegion, shortRegionLabel, uiColors } from '../theme/chartTheme'

const fmt = new Intl.NumberFormat('vi-VN', { maximumFractionDigits: 2 })
const signed = new Intl.NumberFormat('vi-VN', { maximumFractionDigits: 2, signDisplay: 'exceptZero' })
const scaleOf = (value: string | null): Scale => value === 'six' ? 'six' : 'eight'
const focusIds = new Set(['provincial-distribution', 'provincial-ranking', 'provincial-benchmark', 'provincial-profile'])
const value = (score: number | null) => score === null ? '—' : fmt.format(score)
const rgba = (hex: string, alpha: number) => {
  const raw = hex.replace('#', '')
  const [r, g, b] = [0, 2, 4].map((index) => Number.parseInt(raw.slice(index, index + 2), 16))
  return `rgba(${r}, ${g}, ${b}, ${alpha})`
}

export function Provincial() {
  const [params, setParams] = useSearchParams()
  const navigate = useNavigate()
  const [rankLabelMode, setRankLabelMode] = useState<'value' | 'rank'>('value')
  const [benchmarkFocus, setBenchmarkFocus] = useState<'region' | 'national' | null>(null)
  const scale = scaleOf(params.get('scale'))
  const metadata = useQuery({ queryKey: ['metadata'], queryFn: api.metadata })
  const cfg = metadata.data?.data.scales.find((item) => item.id === scale)
  const year = cfg?.years.includes(Number(params.get('year'))) ? Number(params.get('year')) : (cfg?.years.at(-1) ?? 2024)
  const rawProvince = params.get('province') ?? ''
  const provinceRecord = metadata.data?.data.provinces.find((item) => item.provinceVi === rawProvince)
  const rawRegion = params.get('region') ?? ''
  const validRegion = metadata.data?.data.regions.includes(rawRegion) ? rawRegion : undefined
  const region = provinceRecord?.region ?? validRegion
  const focused = focusIds.has(params.get('focus') ?? '') ? params.get('focus') : null
  const scope = useQuery({ queryKey: ['provinces-scope', scale, year, region], queryFn: () => api.provinces(scale, year, region), enabled: Boolean(cfg) })
  const supportedProvince = scope.data?.data.availability.provinces.includes(rawProvince) ? rawProvince : undefined
  const selected = useQuery({ queryKey: ['provinces-selected', scale, year, region, supportedProvince], queryFn: () => api.provinces(scale, year, region, supportedProvince), enabled: Boolean(cfg && supportedProvince) })
  const result = selected.data ?? scope.data

  useEffect(() => {
    const filters = result?.meta.filters
    if (!filters || (supportedProvince && !selected.data)) return
    const canonical = new URLSearchParams({ scale: filters.scale, year: String(filters.year), region: filters.region, province: filters.province })
    if (focused) canonical.set('focus', focused)
    if (params.toString() !== canonical.toString()) setParams(canonical, { replace: true })
  }, [focused, params, result, selected.data, setParams, supportedProvince])

  const reset = () => setParams({ scale: 'eight', year: '2024' })
  if (metadata.isLoading || scope.isLoading || (supportedProvince && selected.isLoading)) return <LoadingSkeleton label="Đang tải vùng và tỉnh" />
  const fault = metadata.error ?? scope.error ?? selected.error
  if (fault) return <ErrorState title="Không tải được dữ liệu vùng" description={`${fault.message} Hãy kiểm tra FastAPI local rồi thử lại.`} action={<><button onClick={() => { void metadata.refetch(); void scope.refetch(); void selected.refetch() }}>Thử lại</button><button className="text-button" onClick={reset}>Đặt lại bộ lọc</button></>} />
  if (!cfg || !result || !result.data.distribution.rows.length) return <EmptyState title="Chưa có dữ liệu vùng và tỉnh" description="Hãy chọn lại phạm vi hoặc năm có dữ liệu." action={<button onClick={reset}>Đặt lại bộ lọc</button>} />

  const d = result.data
  const f = result.meta.filters
  const labels = new Map(metadata.data!.data.dimensions.map((item) => [item.code, item.nameVi]))
  const shortLabels = new Map(metadata.data!.data.dimensions.map((item) => [item.code, item.short]))
  const update = (changes: Record<string, string | null>) => setParams((current) => {
    const next = new URLSearchParams(current)
    Object.entries(changes).forEach(([key, nextValue]) => nextValue === null ? next.delete(key) : next.set(key, nextValue))
    return next
  })
  const change = (next: Partial<{ scale: Scale; year: number; region: string; province: string }>) => {
    const nextScale = next.scale ?? scale
    const nextCfg = metadata.data!.data.scales.find((item) => item.id === nextScale)!
    const nextYear = next.scale ? nextCfg.years.at(-1)! : (next.year ?? year)
    const target = new URLSearchParams({ scale: nextScale, year: String(nextYear) })
    if (next.province) { target.set('region', next.region ?? f.region); target.set('province', next.province) }
    else if (next.region) target.set('region', next.region)
    else { target.set('region', f.region); target.set('province', f.province) }
    if (focused) target.set('focus', focused)
    setParams(target)
  }
  const selectProvince = (province: string, nextRegion = f.region) => change({ region: nextRegion, province })
  const focus = (id: string) => ({ id, activeContext: f.province, open: focused === id, onOpenChange: (open: boolean) => update({ focus: open ? id : null }) })
  const active = d.ranking.rows.find((row) => row.provinceVi === f.province) ?? d.ranking.rows[0]
  const groups = [...new Set(d.distribution.rows.map((row) => row.region))]

  const distributionData: Data[] = groups.map((group) => {
    const rows = d.distribution.rows.filter((row) => row.region === group)
    const activeGroup = group === f.region
    return {
      type: 'box', name: shortRegionLabel(group), orientation: 'h', x: rows.map((row) => row.score), y: rows.map(() => shortRegionLabel(group)),
      text: rows.map((row) => row.provinceVi), customdata: rows.map((row) => [row.provinceVi, group, row.rank]),
      boxpoints: 'all', jitter: 0.32, pointpos: 0, fillcolor: rgba(colorForRegion(group), activeGroup ? 0.23 : 0.1),
      marker: { color: colorForRegion(group), size: activeGroup ? 7 : 5, opacity: activeGroup ? 0.88 : 0.42 },
      line: { color: colorForRegion(group), width: activeGroup ? 2.4 : 1.2 },
      hovertemplate: '<b>%{customdata[0]}</b><br>%{x:.2f} điểm · hạng %{customdata[2]}<br>%{customdata[1]}<extra></extra>',
    }
  })
  distributionData.push({
    type: 'scatter', mode: 'text+markers', name: f.province, x: [active.score], y: [shortRegionLabel(f.region)], text: [f.province], textposition: 'top left',
    customdata: [[f.province, f.region]], marker: { color: uiColors.surface, size: 13, symbol: 'diamond', line: { color: uiColors.ink, width: 2.5 } },
    hovertemplate: `<b>${f.province}</b><br>%{x:.2f} điểm<extra>Đang chọn</extra>`, showlegend: false,
  })

  const ranking = [...d.ranking.rows].sort((a, b) => (b.score ?? -Infinity) - (a.score ?? -Infinity))
  const scores = ranking.flatMap((row) => row.score === null ? [] : [row.score])
  const scoreSpan = Math.max(...scores) - Math.min(...scores)
  const rankBaseline = Math.min(...scores) - Math.max(scoreSpan * 0.08, 0.2)
  const rankingShapes: Layout['shapes'] = ranking.map((row) => ({
    type: 'line', x0: rankBaseline, x1: row.score ?? rankBaseline, y0: row.provinceVi, y1: row.provinceVi,
    line: { color: row.provinceVi === f.province ? uiColors.primary : uiColors.border, width: row.provinceVi === f.province ? 3 : 2 },
  }))
  const rankingData: Data[] = [{
    type: 'scatter', mode: 'text+markers', name: 'Tỉnh trong vùng', x: ranking.map((row) => row.score), y: ranking.map((row) => row.provinceVi),
    text: ranking.map((row) => rankLabelMode === 'value' ? value(row.score) : `Hạng ${row.rankRegion}`),
    textposition: 'middle right', cliponaxis: false,
    customdata: ranking.map((row) => [row.provinceVi, row.rankRegion]),
    marker: {
      color: ranking.map((row) => row.provinceVi === f.province ? uiColors.primary : '#9CB8B3'),
      size: ranking.map((row) => row.provinceVi === f.province ? 13 : 9),
      line: { color: uiColors.surface, width: 1.5 },
    },
    hovertemplate: '<b>%{customdata[0]}</b><br>Hạng %{customdata[1]} · %{x:.2f} điểm<extra></extra>',
  } as unknown as Data]

  const bulletRows = [
    { id: 'province', label: f.province, score: d.benchmark.provinceScore, n: 1, delta: 0, symbol: 'diamond', color: uiColors.primary },
    { id: 'region', label: 'Trung bình vùng', score: d.benchmark.regionMean, n: d.benchmark.regionN, delta: d.benchmark.regionMean === null || d.benchmark.provinceScore === null ? null : d.benchmark.regionMean - d.benchmark.provinceScore, symbol: 'circle', color: uiColors.warning },
    { id: 'national', label: 'Trung bình toàn bộ mẫu', score: d.benchmark.nationalMean, n: d.benchmark.nationalN, delta: d.benchmark.nationalMean === null || d.benchmark.provinceScore === null ? null : d.benchmark.nationalMean - d.benchmark.provinceScore, symbol: 'circle-open', color: uiColors.muted },
  ] as const
  const bulletData: Data[] = [{
    type: 'scatter', mode: 'text+markers', x: bulletRows.map((row) => row.score), y: bulletRows.map((row) => row.label),
    text: bulletRows.map((row) => value(row.score)), textposition: 'top center', cliponaxis: false,
    customdata: bulletRows.map((row) => [row.id, row.label, row.n, row.delta]),
    marker: { symbol: bulletRows.map((row) => row.symbol), color: bulletRows.map((row) => row.color), size: [17, 13, 14], line: { width: 2 } },
    hovertemplate: '<b>%{customdata[1]}</b><br>%{x:.2f} điểm · n = %{customdata[2]}<br>Chênh với tỉnh: %{customdata[3]:+.2f}<extra></extra>', showlegend: false,
  } as unknown as Data]
  const rangeSpan = Math.max((d.benchmark.nationalMax ?? 1) - (d.benchmark.nationalMin ?? 0), 1)
  const bulletShapes: Layout['shapes'] = [
    ...bulletRows.map((row) => ({ type: 'line' as const, x0: d.benchmark.nationalMin, x1: d.benchmark.nationalMax, y0: row.label, y1: row.label, line: { color: uiColors.border, width: 8 }, layer: 'below' as const })),
    { type: 'rect', x0: d.benchmark.nationalQ1, x1: d.benchmark.nationalQ3, y0: -0.45, y1: 2.45, fillcolor: rgba(uiColors.primary, 0.1), line: { width: 0 }, layer: 'below' },
  ]

  const profileRows = d.profile.rows
  const radarData: Data[] = [
    {
      type: 'scatterpolar', mode: 'lines+markers', name: f.province, r: profileRows.map((row) => row.provinceScore), theta: profileRows.map((row) => shortLabels.get(row.code) ?? row.code),
      fill: 'toself', fillcolor: rgba(uiColors.primary, 0.14), line: { color: uiColors.primary, width: 3 }, marker: { color: uiColors.primary, size: 7 },
      customdata: profileRows.map((row) => [row.code, labels.get(row.code) ?? row.code, row.regionMean === null || row.provinceScore === null ? null : row.provinceScore - row.regionMean]),
      hovertemplate: '<b>%{customdata[1]}</b><br>%{r:.2f} điểm<br>So với vùng: %{customdata[2]:+.2f}<extra>' + f.province + '</extra>',
    },
    {
      type: 'scatterpolar', mode: 'lines+markers', name: 'Trung bình vùng', r: profileRows.map((row) => row.regionMean), theta: profileRows.map((row) => shortLabels.get(row.code) ?? row.code),
      line: { color: uiColors.warning, width: benchmarkFocus === 'region' ? 3.5 : 2, dash: 'dash' }, marker: { color: uiColors.warning, size: 6 }, opacity: benchmarkFocus === 'national' ? 0.3 : 1,
      customdata: profileRows.map((row) => [row.code, labels.get(row.code) ?? row.code, row.regionN]), hovertemplate: '<b>%{customdata[1]}</b><br>%{r:.2f} điểm · n = %{customdata[2]}<extra>Trung bình vùng</extra>',
    },
    {
      type: 'scatterpolar', mode: 'lines+markers', name: 'Trung bình toàn bộ mẫu', r: profileRows.map((row) => row.nationalMean), theta: profileRows.map((row) => shortLabels.get(row.code) ?? row.code),
      line: { color: uiColors.muted, width: benchmarkFocus === 'national' ? 3.5 : 2, dash: 'dot' }, marker: { color: uiColors.surface, line: { color: uiColors.muted, width: 2 }, size: 6 }, opacity: benchmarkFocus === 'region' ? 0.3 : 1,
      customdata: profileRows.map((row) => [row.code, labels.get(row.code) ?? row.code, row.nationalN]), hovertemplate: '<b>%{customdata[1]}</b><br>%{r:.2f} điểm · n = %{customdata[2]}<extra>Trung bình toàn bộ mẫu</extra>',
    },
  ]

  const selectFromPoint = (customdata: unknown) => {
    if (!Array.isArray(customdata)) return
    const province = customdata[0]
    const nextRegion = customdata[1]
    if (typeof province === 'string') selectProvince(province, typeof nextRegion === 'string' ? nextRegion : f.region)
  }
  const distributionView = (height: number) => <CartesianChart title="Phân phối điểm giữa sáu vùng" summary="Trung vị, khoảng tứ phân vị và từng tỉnh trong cùng snapshot." data={distributionData} height={height} onClick={(event) => selectFromPoint(event.points?.[0]?.customdata)} layout={{ xaxis: { title: { text: d.distribution.unit } }, yaxis: { automargin: true }, showlegend: false, margin: { l: 112, r: 28, t: 24, b: 52 } }} />
  const rankingView = (height: number) => <CartesianChart title="Xếp hạng tỉnh trong vùng" summary={`Điểm và thứ hạng của ${d.ranking.rowCount} tỉnh thuộc ${f.region}.`} data={rankingData} height={height} onClick={(event) => selectFromPoint(event.points?.[0]?.customdata)} layout={{ xaxis: { title: { text: d.ranking.unit }, range: [rankBaseline, Math.max(...scores) + Math.max(scoreSpan * 0.2, 0.6)] }, yaxis: { categoryorder: 'array', categoryarray: ranking.map((row) => row.provinceVi), autorange: 'reversed', automargin: true }, shapes: rankingShapes, showlegend: false, margin: { l: 118, r: 72, t: 22, b: 48 } }}><table><caption className="sr-only">Bảng xếp hạng tỉnh trong vùng</caption><thead><tr><th>Tỉnh</th><th>Hạng</th><th>Điểm</th></tr></thead><tbody>{ranking.map((row) => <tr key={row.provinceId}><th scope="row">{row.provinceVi}</th><td>{row.rankRegion}/{d.benchmark.regionTotal}</td><td>{value(row.score)}</td></tr>)}</tbody></table></CartesianChart>
  const benchmarkView = (height: number) => <CartesianChart title="So sánh điểm với hai benchmark" summary="Điểm tỉnh, trung bình vùng và trung bình toàn bộ mẫu trên cùng một thang đo." data={bulletData} height={height} onClick={(event) => { const raw = event.points?.[0]?.customdata; const id = Array.isArray(raw) ? raw[0] : null; if (id === 'region' || id === 'national') setBenchmarkFocus((current) => current === id ? null : id) }} layout={{ xaxis: { title: { text: d.measure.unit }, range: [(d.benchmark.nationalMin ?? 0) - rangeSpan * 0.08, (d.benchmark.nationalMax ?? 1) + rangeSpan * 0.12] }, yaxis: { categoryorder: 'array', categoryarray: bulletRows.map((row) => row.label), autorange: 'reversed', automargin: true, fixedrange: true }, shapes: bulletShapes, showlegend: false, margin: { l: 138, r: 48, t: 34, b: 58 } }}><table><caption className="sr-only">Bảng benchmark tổng điểm</caption><thead><tr><th>Mốc</th><th>Điểm</th><th>n</th></tr></thead><tbody>{bulletRows.map((row) => <tr key={row.id}><th scope="row">{row.label}</th><td>{value(row.score)}</td><td>{row.n}</td></tr>)}</tbody></table></CartesianChart>
  const profileView = (height: number) => <PolarChart title="Hồ sơ lĩnh vực của tỉnh" summary={`So sánh ${f.province}, ${f.region} và toàn bộ mẫu trên thang điểm 1–10.`} data={radarData} height={height} onClick={(event) => { const raw = event.points?.[0]?.customdata; const code = Array.isArray(raw) ? raw[0] : null; if (typeof code === 'string') { const other = profileRows.find((row) => row.code !== code)?.code ?? code; navigate(`/dimension?scale=${f.scale}&year=${f.year}&x=${code}&y=${other}&province=${encodeURIComponent(f.province)}`) } }} layout={{ polar: { radialaxis: { range: [1, 10], tickvals: [2, 4, 6, 8, 10] } }, legend: { orientation: 'h', y: -0.13 }, margin: { l: 70, r: 70, t: 32, b: 78 } }}><table><caption className="sr-only">Bảng điểm lĩnh vực của tỉnh và benchmark</caption><thead><tr><th>Lĩnh vực</th><th>Tỉnh</th><th>Vùng</th><th>Toàn bộ mẫu</th></tr></thead><tbody>{profileRows.map((row) => <tr key={row.code}><th scope="row">{labels.get(row.code) ?? row.code}</th><td>{value(row.provinceScore)}</td><td>{value(row.regionMean)}</td><td>{value(row.nationalMean)}</td></tr>)}</tbody></table></PolarChart>

  const defaultYear = metadata.data!.data.scales.find((item) => item.id === 'eight')?.years.at(-1) ?? 2024
  const defaultSelection = f.scale === 'eight' && f.year === defaultYear && f.region === d.availability.regions[0] && f.province === d.availability.provinces[0] && !focused
  const benchmarkLabel = benchmarkFocus === 'region' ? 'Vùng' : benchmarkFocus === 'national' ? 'Toàn bộ mẫu' : 'Cả hai'

  return <article className="overview analysis-page provincial-redesign">
    <DashboardPageHeader eyebrow="VÙNG & TỈNH" title="Khác biệt giữa vùng và tỉnh" description="Đặt một tỉnh vào phân phối vùng, thứ hạng và cấu trúc lĩnh vực trong cùng một snapshot." />
    <FilterBar label="Bộ lọc vùng và tỉnh" summary={`Đang xem: ${f.province} · ${f.region} · ${f.year} · ${f.scale === 'six' ? '6 lĩnh vực' : '8 lĩnh vực'}`} onReset={reset} resetDisabled={defaultSelection}>
      <label>Phạm vi so sánh<select value={f.scale} onChange={(event) => change({ scale: scaleOf(event.target.value) })}><option value="six">6 lĩnh vực gốc</option><option value="eight">8 lĩnh vực</option></select></label>
      <label>Năm<select value={f.year} onChange={(event) => change({ year: Number(event.target.value) })}>{cfg.years.map((item) => <option key={item} value={item}>{item}</option>)}</select></label>
      <label>Vùng<select value={f.region} onChange={(event) => change({ region: event.target.value })}>{d.availability.regions.map((item) => <option key={item}>{item}</option>)}</select></label>
      <label>Tỉnh<select value={f.province} onChange={(event) => change({ province: event.target.value })}>{d.availability.provinces.map((item) => <option key={item}>{item}</option>)}</select></label>
    </FilterBar>
    <KpiGrid label="Chỉ số tóm tắt vùng và tỉnh">
      <KpiCard label="Điểm của tỉnh" value={value(d.benchmark.provinceScore)} detail={f.province} />
      <KpiCard label="Hạng trong vùng" value={`${d.benchmark.rankRegion}/${d.benchmark.regionTotal}`} detail={f.region} />
      <KpiCard label="So với trung bình vùng" value={d.benchmark.vsRegion === null ? '—' : signed.format(d.benchmark.vsRegion)} detail={`n = ${d.benchmark.regionN} tỉnh`} tone={(d.benchmark.vsRegion ?? 0) >= 0 ? 'positive' : 'negative'} />
      <KpiCard label="So với toàn bộ mẫu" value={d.benchmark.vsNational === null ? '—' : signed.format(d.benchmark.vsNational)} detail={`n = ${d.benchmark.nationalN} tỉnh`} tone={(d.benchmark.vsNational ?? 0) >= 0 ? 'positive' : 'negative'} />
    </KpiGrid>

    <section className="provincial-chart-grid" aria-label="Bốn biểu đồ vùng và tỉnh">
      <ChartCard className="provincial-chart-card" eyebrow="01 · PHÂN PHỐI VÙNG" title="Vùng nào có mặt bằng cao và phân hóa rộng nhất?" insight={<ChartInsight>{d.insights.distribution}</ChartInsight>} focus={{ ...focus('provincial-distribution'), content: distributionView(560) }} footer={<ChartMeta source={d.distribution.source} unit={d.distribution.unit} n={`${d.distribution.rowCount} tỉnh`} caveats={d.distribution.caveats} />}>
        {distributionView(310)}
      </ChartCard>
      <ChartCard className="provincial-chart-card" eyebrow="02 · THỨ HẠNG TRONG VÙNG" title={`${f.province} đứng ở đâu trong ${f.region}?`} action={<button type="button" className="chart-sort" onClick={() => setRankLabelMode((current) => current === 'value' ? 'rank' : 'value')}>Nhãn: {rankLabelMode === 'value' ? 'Điểm' : 'Hạng'}</button>} insight={<ChartInsight>{d.insights.ranking}</ChartInsight>} focus={{ ...focus('provincial-ranking'), content: rankingView(560) }} footer={<ChartMeta source={d.ranking.source} unit={d.ranking.unit} n={`${d.ranking.rowCount} tỉnh`} caveats={d.ranking.caveats} />}>
        {rankingView(310)}
      </ChartCard>
      <ChartCard className="provincial-chart-card" eyebrow="03 · BENCHMARK TỔNG ĐIỂM" title="Điểm tỉnh cách vùng và toàn bộ mẫu bao xa?" action={<button type="button" className="chart-sort" onClick={() => setBenchmarkFocus((current) => current === null ? 'region' : current === 'region' ? 'national' : null)}>Benchmark: {benchmarkLabel}</button>} insight={<ChartInsight>{d.insights.benchmark}</ChartInsight>} focus={{ ...focus('provincial-benchmark'), content: benchmarkView(500) }} footer={<ChartMeta source={d.benchmark.source} unit={d.benchmark.unit} n={`${d.benchmark.nationalN} tỉnh`} caveats={d.benchmark.caveats} />}>
        {benchmarkView(310)}
      </ChartCard>
      <ChartCard className="provincial-chart-card" eyebrow="04 · HỒ SƠ LĨNH VỰC" title="Tỉnh mạnh hoặc yếu ở lĩnh vực nào so với vùng?" insight={<ChartInsight>{d.insights.profile}</ChartInsight>} focus={{ ...focus('provincial-profile'), content: profileView(540) }} footer={<ChartMeta source={d.profile.source} unit={d.profile.unit} n={`${d.profile.rowCount} lĩnh vực`} caveats={d.profile.caveats} />}>
        {profileView(310)}
      </ChartCard>
    </section>
  </article>
}
