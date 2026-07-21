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
import { colorForRegion, divergingScale, shortRegionLabel, uiColors } from '../theme/chartTheme'

const fmt = new Intl.NumberFormat('vi-VN', { maximumFractionDigits: 2 })
const signed = new Intl.NumberFormat('vi-VN', { maximumFractionDigits: 2, signDisplay: 'exceptZero' })
const scaleOf = (value: string | null): Scale => value === 'eight' ? 'eight' : 'six'
const sparseYears = (values: number[]) => values.filter((_, index) => index % 2 === 0 || index === values.length - 1)

function rangeFor(years: number[], rawFrom: number, rawTo: number, startAtFirst = false) {
  const fallbackTo = years.includes(rawTo) ? rawTo : (years.at(-1) ?? 2024)
  const validFrom = years.includes(rawFrom) && rawFrom < fallbackTo ? rawFrom : undefined
  if (validFrom) return { from: validFrom, to: fallbackTo }
  if (startAtFirst && (years[0] ?? fallbackTo) < fallbackTo) return { from: years[0]!, to: fallbackTo }
  const before = years.filter((year) => year < fallbackTo).at(-1)
  if (before) return { from: before, to: fallbackTo }
  return { from: years[0] ?? 2011, to: years[1] ?? 2012 }
}

export function TimeTrend() {
  const [params, setParams] = useSearchParams()
  const scale = scaleOf(params.get('scale'))
  const metadata = useQuery({ queryKey: ['metadata'], queryFn: api.metadata })
  const available = metadata.data?.data.scales.find((item) => item.id === scale)
  const years = available?.years ?? []
  const toAlias = Number(params.get('to') ?? params.get('year'))
  const { from, to } = rangeFor(years, Number(params.get('from')), toAlias, !params.has('from'))
  const provinceContext = params.get('province') ?? ''
  const provinceRecord = metadata.data?.data.provinces.find((item) => item.provinceVi === provinceContext)
  const requestedDimension = params.get('dimension') ?? ''

  useEffect(() => {
    if (!available || from >= to) return
    const canonical = { scale, from: String(from), to: String(to), ...(requestedDimension ? { dimension: requestedDimension } : {}), ...(provinceContext ? { province: provinceContext } : {}) }
    if (params.toString() !== new URLSearchParams(canonical).toString()) setParams(canonical, { replace: true })
  }, [available, from, params, provinceContext, requestedDimension, scale, setParams, to])
  const trend = useQuery({
    queryKey: ['trends', scale, from, to, provinceRecord?.region, provinceRecord?.provinceVi],
    queryFn: () => provinceRecord ? api.trends(scale, from, to, provinceRecord.region, provinceRecord.provinceVi) : api.trends(scale, from, to),
    enabled: Boolean(available && from < to),
  })
  const dimensions = trend.data?.data.dimensionDeltas.rows.map((row) => row.code) ?? []
  const selected = dimensions.includes(requestedDimension) ? requestedDimension : (dimensions[0] ?? '')
  useEffect(() => {
    if (selected && selected !== requestedDimension) setParams({ scale, from: String(from), to: String(to), dimension: selected, ...(provinceContext ? { province: provinceContext } : {}) }, { replace: true })
  }, [from, provinceContext, requestedDimension, scale, selected, setParams, to])
  const update = (next: Partial<Record<'scale' | 'from' | 'to' | 'dimension', string>>) => setParams({ scale, from: String(from), to: String(to), ...(selected ? { dimension: selected } : {}), ...(provinceContext ? { province: provinceContext } : {}), ...next })
  const reset = () => setParams({ scale: 'six', from: '2011', to: '2024' })

  if (metadata.isLoading || trend.isLoading) return <LoadingSkeleton label="Đang tải diễn biến" />
  const fault = metadata.error ?? trend.error
  if (fault) return <ErrorState title="Không tải được diễn biến" description={`${fault.message} Hãy kiểm tra FastAPI local rồi thử lại.`} action={<button onClick={() => { void metadata.refetch(); void trend.refetch() }}>Thử lại</button>} />
  if (!available || !trend.data || !trend.data.data.totalSeries.rows.length) return <EmptyState title="Chưa có diễn biến phù hợp" description="Hãy chọn khoảng năm có dữ liệu." action={<button onClick={reset}>Đặt lại bộ lọc</button>} />

  const d = trend.data.data
  const labelMap = new Map(metadata.data!.data.dimensions.map((item) => [item.code, item]))
  const compact = (code: string) => labelMap.get(code)?.short ?? code
  const resetRange = (next: Partial<Record<'from' | 'to', string>>) => rangeFor(years, Number(next.from ?? from), Number(next.to ?? to))
  const regions = [...new Set(d.regionalSeries.rows.map((row) => row.region))]
  const totalTraces: Data[] = [
    ...regions.map((region): Data => ({
      type: 'scatter', mode: 'lines', name: shortRegionLabel(region),
      x: d.regionalSeries.rows.filter((row) => row.region === region).map((row) => row.year),
      y: d.regionalSeries.rows.filter((row) => row.region === region).map((row) => row.score),
      line: { color: colorForRegion(region), width: 1.4 }, opacity: 0.58,
      hovertemplate: `%{x}: %{y:.2f}<extra>${region}</extra>`,
    })),
    {
      type: 'scatter', mode: 'lines+markers', name: 'Toàn quốc',
      x: d.totalSeries.rows.map((row) => row.year), y: d.totalSeries.rows.map((row) => row.score),
      customdata: d.totalSeries.rows.map((row) => row.contributorN),
      line: { color: uiColors.ink, width: 3.5 }, marker: { color: '#fff', line: { color: uiColors.ink, width: 2 }, size: 8 },
      hovertemplate: '%{x}: <b>%{y:.2f}</b><br>%{customdata} tỉnh<extra>Toàn quốc</extra>',
    },
    ...[...new Set(d.selectedSeries.rows.map((row) => `${row.scope}:${row.label}`))].map((key): Data => {
      const rows = d.selectedSeries.rows.filter((row) => `${row.scope}:${row.label}` === key)
      const isProvince = rows[0]?.scope === 'province'
      return {
        type: 'scatter', mode: 'lines+markers', name: rows[0]?.label ?? key,
        x: rows.map((row) => row.year), y: rows.map((row) => row.score),
        line: { color: isProvince ? uiColors.warning : uiColors.primary, width: isProvince ? 3 : 2.4, dash: isProvince ? 'solid' : 'dash' },
        marker: { size: isProvince ? 8 : 6 },
        hovertemplate: `%{x}: %{y:.2f}<extra>${rows[0]?.label ?? key}</extra>`,
      }
    }),
  ]
  const yoyYears = [...new Set(d.regionalYearOverYear.rows.map((row) => row.year))]
  const yoyTicks = sparseYears(yoyYears)
  const yoyHeatmap: Data = {
    type: 'heatmap', x: yoyYears, y: regions.map(shortRegionLabel),
    z: regions.map((region) => yoyYears.map((year) => d.regionalYearOverYear.rows.find((row) => row.region === region && row.year === year)?.change ?? null)),
    customdata: regions.map((region) => yoyYears.map(() => region)), colorscale: divergingScale, zmid: 0,
    colorbar: { title: { text: 'Δ điểm' }, thickness: 12, outlinewidth: 0 },
    hovertemplate: '<b>%{customdata}</b><br>%{x}: %{z:+.2f}<extra></extra>',
  } as unknown as Data
  const heatCodes = [...new Set(d.heatmap.rows.map((row) => row.code))]
  const heatYears = [...new Set(d.heatmap.rows.map((row) => row.year))]
  const heatTicks = sparseYears(heatYears)
  const dimensionHeatmap: Data = {
    type: 'heatmap', x: heatYears, y: heatCodes.map(compact),
    z: heatCodes.map((code) => heatYears.map((year) => d.heatmap.rows.find((row) => row.code === code && row.year === year)?.score ?? null)),
    customdata: heatCodes.map((code) => heatYears.map(() => labelMap.get(code)?.nameVi ?? code)),
    colorscale: [[0, '#E2F0ED'], [0.5, '#79B8AE'], [1, '#1E6F68']],
    colorbar: { title: { text: 'Điểm' }, thickness: 12, outlinewidth: 0 },
    hovertemplate: '<b>%{customdata}</b><br>%{x}: %{z:.2f}<extra></extra>',
  }
  const deltaRows = [...d.dimensionDeltas.rows].sort((a, b) => (a.delta ?? 0) - (b.delta ?? 0))
  const delta: Data = {
    type: 'bar', orientation: 'h', y: deltaRows.map((row) => compact(row.code)), x: deltaRows.map((row) => row.delta),
    customdata: deltaRows.map((row) => row.label),
    marker: { color: deltaRows.map((row) => (row.delta ?? 0) >= 0 ? uiColors.positive : uiColors.negative) },
    hovertemplate: '<b>%{customdata}</b><br>%{x:+.2f}<extra></extra>',
  }
  const turning = d.turningPoints.rows[0]
  const selectedDelta = d.dimensionDeltas.rows.find((row) => row.code === selected)
  const focusLabel = provinceRecord ? ` · theo dõi ${provinceRecord.provinceVi}` : ''

  return <article className="overview analysis-page">
    <DashboardPageHeader eyebrow="Diễn biến · 2011–2024" title="Điểm quản trị qua các năm" description={`Đọc xu hướng toàn quốc trong bối cảnh sáu vùng, sau đó đi từ biến động năm-kề-năm tới cấu trúc lĩnh vực${focusLabel}.`} aside={<p className="status">{from}–{to} · {trend.data.meta.n} tỉnh–năm</p>} />
    <FilterBar label="Bộ lọc diễn biến" summary={provinceRecord ? `Giữ ngữ cảnh ${provinceRecord.provinceVi}` : 'Bức tranh toàn quốc'} onReset={reset}>
      <label>Phạm vi<select value={scale} onChange={(event) => { const next = scaleOf(event.target.value); const nextYears = metadata.data!.data.scales.find((item) => item.id === next)!.years; const nextRange = rangeFor(nextYears, nextYears[0], nextYears.at(-1) ?? nextYears[0]); setParams({ scale: next, from: String(nextRange.from), to: String(nextRange.to), ...(provinceContext ? { province: provinceContext } : {}) }) }}><option value="six">Tổng 6 lĩnh vực gốc</option><option value="eight">Tổng PAPI (8 lĩnh vực)</option></select></label>
      <label>Từ năm<select value={from} onChange={(event) => { const nextRange = resetRange({ from: event.target.value }); update({ from: String(nextRange.from), to: String(nextRange.to) }) }}>{years.filter((year) => year < to).map((year) => <option key={year} value={year}>{year}</option>)}</select></label>
      <label>Đến năm<select value={to} onChange={(event) => { const nextRange = resetRange({ to: event.target.value }); update({ from: String(nextRange.from), to: String(nextRange.to) }) }}>{years.filter((year) => year > from).map((year) => <option key={year} value={year}>{year}</option>)}</select></label>
    </FilterBar>
    <KpiGrid>
      <KpiCard label={`Điểm đầu kỳ · ${d.summary.first}`} value={d.summary.vFirst === null ? '—' : fmt.format(d.summary.vFirst)} detail={d.measure.unit} />
      <KpiCard label={`Điểm cuối kỳ · ${d.summary.latest}`} value={d.summary.vLatest === null ? '—' : fmt.format(d.summary.vLatest)} detail={d.measure.unit} tone="accent" />
      <KpiCard label="Thay đổi ròng" value={d.summary.net === null ? '—' : signed.format(d.summary.net)} detail={`${from} → ${to}`} tone={(d.summary.net ?? 0) >= 0 ? 'positive' : 'negative'} />
      <KpiCard label="Biến động YoY lớn nhất" value={turning?.change === null || !turning ? '—' : signed.format(turning.change)} detail={turning ? `${turning.fromYear} → ${turning.year}` : 'Chưa đủ mốc'} />
    </KpiGrid>
    <InsightCard label="Tín hiệu cần đọc">
      <p>Chuỗi đạt đỉnh vào <strong>{d.summary.peakYear ?? '—'}</strong>. {selectedDelta ? `${selectedDelta.label} thay đổi ${signed.format(selectedDelta.delta ?? 0)} điểm trong khoảng đã chọn.` : ''} Các đường vùng và tỉnh là lớp so sánh, không thay thế chuỗi toàn quốc.</p>
    </InsightCard>

    <section className="dashboard-grid time-story-grid" aria-label="Bốn biểu đồ diễn biến">
      <ChartCard className="chart-full" eyebrow="01 · Xu hướng" title="Quốc gia trong bối cảnh sáu vùng" description="Đường quốc gia đậm; đường vùng mảnh hơn. Nếu có tỉnh từ trang trước, tỉnh và vùng tương ứng được nhấn mạnh." footer={<ChartMeta source={d.totalSeries.source} unit={d.totalSeries.unit} n={`${trend.data.meta.n} tỉnh–năm`} caveats={[...(d.totalSeries.caveats ?? []), ...(trend.data.meta.caveats ?? [])]} />}>
        <CartesianChart title="Đường điểm tổng theo năm" summary={`Điểm trung bình toàn quốc và các vùng trong giai đoạn ${from}–${to}.`} data={totalTraces} height={430} layout={{ xaxis: { title: { text: 'Năm' }, tickmode: 'array', tickvals: sparseYears(d.totalSeries.rows.map((row) => row.year)) }, yaxis: { title: { text: d.totalSeries.unit } }, legend: { orientation: 'h', y: -0.2 }, margin: { l: 72, r: 24, t: 20, b: 100 } }}>
          <table><thead><tr><th>Năm</th><th>Toàn quốc</th><th>Số tỉnh</th></tr></thead><tbody>{d.totalSeries.rows.map((row) => <tr key={row.year}><th>{row.year}</th><td>{fmt.format(row.score ?? 0)}</td><td>{row.contributorN}</td></tr>)}</tbody></table>
        </CartesianChart>
      </ChartCard>
      <ChartCard className="chart-medium" eyebrow="02 · Nhịp thay đổi" title="Vùng nào tăng hoặc giảm cùng năm?" description="Heatmap dùng chênh lệch so với năm liền trước, không phải mức điểm tuyệt đối." footer={<ChartMeta source={d.regionalYearOverYear.source} unit={d.regionalYearOverYear.unit} n={`${d.regionalYearOverYear.rowCount} vùng–năm`} caveats={d.regionalYearOverYear.caveats} />}>
        <CartesianChart title="Heatmap thay đổi năm-kề-năm theo vùng" summary="Xanh là tăng, đỏ là giảm so với năm trước." data={[yoyHeatmap]} height={390} layout={{ xaxis: { title: { text: 'Năm' }, tickmode: 'array', tickvals: yoyTicks }, yaxis: { automargin: true }, margin: { l: 112, r: 28, t: 18, b: 52 } }} />
      </ChartCard>
      <ChartCard className="chart-wide" eyebrow="03 · Cấu trúc" title="Mức điểm các lĩnh vực thay đổi ra sao?" description="Heatmap giúp nhận ra giai đoạn và lĩnh vực cùng chuyển màu, nhưng không khẳng định nguyên nhân." footer={<ChartMeta source={d.heatmap.source} unit={d.heatmap.unit} n={`${d.heatmap.rowCount} lĩnh vực–năm`} caveats={d.heatmap.caveats} />}>
        <CartesianChart title="Bản nhiệt điểm theo lĩnh vực và năm" summary="Màu đậm hơn biểu thị điểm lĩnh vực cao hơn." data={[dimensionHeatmap]} height={390} layout={{ xaxis: { title: { text: 'Năm' }, tickmode: 'array', tickvals: heatTicks }, yaxis: { automargin: true }, margin: { l: 112, r: 28, t: 18, b: 52 } }}>
          <table><thead><tr><th>Mốc</th><th>Điểm</th></tr></thead><tbody>{d.heatmap.rows.map((row) => <tr key={`${row.code}-${row.year}`}><th>{row.label} · {row.year}</th><td>{fmt.format(row.score ?? 0)}</td></tr>)}</tbody></table>
        </CartesianChart>
      </ChartCard>
      <ChartCard className="chart-full" eyebrow="04 · Đầu–cuối" title="Lĩnh vực nào thay đổi nhiều nhất?" description="Chọn một lĩnh vực để giữ context trong URL và đọc con số chính xác trên thẻ." footer={<ChartMeta source={d.dimensionDeltas.source} unit={d.dimensionDeltas.unit} n={`${d.dimensionDeltas.rowCount} lĩnh vực`} caveats={d.dimensionDeltas.caveats} />}>
        <div className="dimension-list">{d.dimensionDeltas.rows.map((row) => <button key={row.code} className={selected === row.code ? 'selected' : ''} onClick={() => update({ dimension: row.code })}>{row.label}<strong>{row.delta === null ? '—' : signed.format(row.delta)}</strong></button>)}</div>
        <CartesianChart title="Biểu đồ cột thay đổi lĩnh vực" summary={`Chênh lệch giữa đầu và cuối giai đoạn ${from}–${to}.`} data={[delta]} height={360} layout={{ xaxis: { title: { text: d.dimensionDeltas.unit }, zeroline: true, zerolinewidth: 2 }, yaxis: { automargin: true }, showlegend: false, margin: { l: 112, r: 24, t: 14, b: 54 } }} />
      </ChartCard>
    </section>
    <section className="story"><p className="eyebrow">Bước đọc tiếp</p><h2>Xem theo vùng và tỉnh</h2><p>Giữ lại phạm vi và năm cuối kỳ để chuyển từ thời gian sang không gian.</p><Link className="cta" to={`/provincial?scale=${scale}&year=${to}${provinceContext ? `&province=${encodeURIComponent(provinceContext)}` : ''}`}>Mở Vùng & tỉnh</Link></section>
  </article>
}
