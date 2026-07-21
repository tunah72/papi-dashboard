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
  ProvinceMap,
} from '../components/dashboard'
import { colorForRegion, shortRegionLabel, uiColors } from '../theme/chartTheme'

const fmt = new Intl.NumberFormat('vi-VN', { maximumFractionDigits: 2 })
const signed = new Intl.NumberFormat('vi-VN', { maximumFractionDigits: 2, signDisplay: 'exceptZero' })
const scaleOf = (value: string | null): Scale => value === 'six' ? 'six' : 'eight'
const value = (score: number | null) => score === null ? '—' : fmt.format(score)
function axisLabel(label: string) {
  const words = label.split(' ')
  const lines: string[] = []
  let line = ''
  for (const word of words) {
    if (`${line} ${word}`.trim().length > 18 && line) { lines.push(line); line = word }
    else line = `${line} ${word}`.trim()
  }
  if (line) lines.push(line)
  return lines.join('<br>')
}

export function Provincial() {
  const [params, setParams] = useSearchParams()
  const scale = scaleOf(params.get('scale'))
  const metadata = useQuery({ queryKey: ['metadata'], queryFn: api.metadata })
  const geojson = useQuery({ queryKey: ['geojson'], queryFn: api.geojson })
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
  const reset = () => setParams({ scale: 'eight', year: '2024' })

  if (metadata.isLoading || geojson.isLoading || scope.isLoading || (supportedProvince && selected.isLoading)) return <LoadingSkeleton label="Đang tải vùng và tỉnh" />
  const fault = metadata.error ?? geojson.error ?? scope.error ?? selected.error
  if (fault) return <ErrorState title="Không tải được dữ liệu vùng" description={`${fault.message} Hãy kiểm tra FastAPI local rồi thử lại.`} action={<><button onClick={() => { void metadata.refetch(); void geojson.refetch(); void scope.refetch(); void selected.refetch() }}>Thử lại</button><button className="text-button" onClick={reset}>Đặt lại bộ lọc</button></>} />
  if (!cfg || !result || !geojson.data || !result.data.distribution.rows.length) return <EmptyState title="Chưa có dữ liệu vùng và tỉnh" description="Hãy chọn lại phạm vi hoặc năm có dữ liệu." action={<button onClick={reset}>Đặt lại bộ lọc</button>} />

  const d = result.data
  const f = result.meta.filters
  const labels = new Map(metadata.data!.data.dimensions.map((item) => [item.code, item.nameVi]))
  const shortLabels = new Map(metadata.data!.data.dimensions.map((item) => [item.code, item.short]))
  const change = (next: Partial<{ scale: Scale; year: number; region: string; province: string }>) => {
    const nextScale = next.scale ?? scale
    const nextCfg = metadata.data!.data.scales.find((item) => item.id === nextScale)!
    const nextYear = next.scale ? nextCfg.years.at(-1)! : (next.year ?? year)
    if (next.province) setParams({ scale: nextScale, year: String(nextYear), region: next.region ?? f.region, province: next.province })
    else setParams({ scale: nextScale, year: String(nextYear), ...(next.region ? { region: next.region } : {}) })
  }
  const active = d.ranking.rows.find((row) => row.provinceVi === f.province) ?? d.ranking.rows[0]
  const mapActive = d.distribution.rows.find((row) => row.provinceVi === f.province)
  const groups = [...new Set(d.distribution.rows.map((row) => row.region))]
  const boxplots: Data[] = groups.map((group) => ({
    type: 'box', name: shortRegionLabel(group), orientation: 'h',
    x: d.distribution.rows.filter((row) => row.region === group).map((row) => row.score),
    text: d.distribution.rows.filter((row) => row.region === group).map((row) => row.provinceVi),
    customdata: d.distribution.rows.filter((row) => row.region === group).map(() => group),
    boxpoints: 'all', jitter: 0.28, pointpos: 0,
    marker: { color: colorForRegion(group), size: group === f.region ? 7 : 5, opacity: group === f.region ? 0.9 : 0.48 },
    line: { color: colorForRegion(group), width: group === f.region ? 2.5 : 1.2 },
    hovertemplate: '<b>%{text}</b><br>%{x:.2f}<extra>%{customdata}</extra>',
  }))
  const ranking = [...d.ranking.rows].sort((a, b) => (a.score ?? -Infinity) - (b.score ?? -Infinity))
  const rankingChart: Data[] = [{
    type: 'bar', orientation: 'h',
    x: ranking.map((row) => row.score), y: ranking.map((row) => row.provinceVi),
    customdata: ranking.map((row) => row.provinceVi),
    marker: { color: ranking.map((row) => row.provinceVi === f.province ? uiColors.primary : '#A9C2BE') },
    hovertemplate: '<b>%{y}</b><br>%{x:.2f}<extra></extra>',
  }]
  const profileLabels = d.profile.rows.map((row) => labels.get(row.code) ?? row.code)
  const profileAxis = d.profile.rows.map((row) => axisLabel(shortLabels.get(row.code) ?? row.code))
  const profile: Data[] = [
    { type: 'scatter', mode: 'markers', name: f.province, x: d.profile.rows.map((row) => row.provinceScore), y: profileAxis, customdata: profileLabels, marker: { color: uiColors.primary, size: 13, symbol: 'diamond' }, hovertemplate: `%{customdata}: %{x:.2f}<extra>${f.province}</extra>` },
    { type: 'scatter', mode: 'markers', name: 'Trung bình vùng', x: d.profile.rows.map((row) => row.regionMean), y: profileAxis, customdata: profileLabels, marker: { color: uiColors.warning, size: 10 }, hovertemplate: '%{customdata}: %{x:.2f}<extra>Trung bình vùng</extra>' },
    { type: 'scatter', mode: 'markers', name: 'Trung bình toàn quốc', x: d.profile.rows.map((row) => row.nationalMean), y: profileAxis, customdata: profileLabels, marker: { color: uiColors.muted, size: 10, symbol: 'circle-open', line: { width: 2 } }, hovertemplate: '%{customdata}: %{x:.2f}<extra>Trung bình toàn quốc</extra>' },
  ]
  const first = cfg.years[0] ?? f.year
  const second = cfg.years.find((item) => item > first) ?? first + 1
  const trendTo = f.year > first ? f.year : second

  return <article className="overview analysis-page">
    <DashboardPageHeader eyebrow="Vùng & tỉnh · Hồ sơ địa phương" title="Khác biệt giữa vùng và tỉnh" description="Đặt một tỉnh vào đúng bối cảnh không gian, phân phối vùng, thứ hạng và cấu trúc tám lĩnh vực quản trị." aside={<p className="status">Snapshot {f.year} · {result.meta.n} tỉnh</p>} />
    <FilterBar label="Bộ lọc vùng và tỉnh" summary={`${f.province} · ${f.region}`} onReset={reset}>
      <label>Phạm vi<select value={f.scale} onChange={(event) => change({ scale: scaleOf(event.target.value) })}><option value="six">Tổng 6 lĩnh vực gốc</option><option value="eight">Tổng PAPI (8 lĩnh vực)</option></select></label>
      <label>Năm<select value={f.year} onChange={(event) => change({ year: Number(event.target.value) })}>{cfg.years.map((item) => <option key={item} value={item}>{item}</option>)}</select></label>
      <label>Vùng<select value={f.region} onChange={(event) => change({ region: event.target.value })}>{d.availability.regions.map((item) => <option key={item}>{item}</option>)}</select></label>
      <label>Tỉnh<select value={f.province} onChange={(event) => change({ province: event.target.value })}>{d.availability.provinces.map((item) => <option key={item}>{item}</option>)}</select></label>
    </FilterBar>
    <KpiGrid label="Chỉ số tóm tắt vùng và tỉnh">
      <KpiCard label={`Điểm ${f.province}`} value={value(d.benchmark.provinceScore)} detail={d.measure.unit} tone="accent" />
      <KpiCard label="So với trung bình vùng" value={d.benchmark.vsRegion === null ? '—' : signed.format(d.benchmark.vsRegion)} detail={`${f.region} · n = ${d.benchmark.regionN}`} tone={(d.benchmark.vsRegion ?? 0) >= 0 ? 'positive' : 'negative'} />
      <KpiCard label="So với toàn quốc" value={d.benchmark.vsNational === null ? '—' : signed.format(d.benchmark.vsNational)} detail={`n = ${d.benchmark.nationalN} tỉnh`} tone={(d.benchmark.vsNational ?? 0) >= 0 ? 'positive' : 'negative'} />
      <KpiCard label="Thứ hạng trong vùng" value={`${d.benchmark.rankRegion}/${d.benchmark.regionTotal}`} detail="Cùng năm, cùng thước đo" />
    </KpiGrid>
    <InsightCard label="Đọc nhanh hồ sơ" value={f.province}>
      <p>{d.benchmark.vsRegion === null ? 'Chưa đủ dữ liệu so sánh với vùng.' : `${f.province} ${d.benchmark.vsRegion >= 0 ? 'cao hơn' : 'thấp hơn'} trung bình ${f.region} ${fmt.format(Math.abs(d.benchmark.vsRegion))} điểm`} và đứng thứ {d.benchmark.rankRegion} trong {d.benchmark.regionTotal} tỉnh của vùng.</p>
    </InsightCard>

    <section className="dashboard-grid provincial-grid" aria-label="Bốn biểu đồ vùng và tỉnh">
      <ChartCard className="chart-wide map-surface" eyebrow="01 · Không gian" title={`${f.province} trong bản đồ ${f.year}`} description="Chọn một tỉnh trên bản đồ để chuyển đồng thời vùng, tỉnh và toàn bộ benchmark." footer={<ChartMeta source={d.distribution.source} unit={d.distribution.unit} n={`${d.distribution.rowCount} tỉnh`} caveats={d.distribution.caveats} />}>
        <ProvinceMap title={`Bản đồ hồ sơ ${f.province}`} summary={`Phân bố PAPI năm ${f.year}; ${f.province} có viền đậm.`} rows={d.distribution.rows} geojson={geojson.data.data.geojson} selectedId={mapActive?.provinceId ?? active.provinceId} unit={d.distribution.unit} onSelect={(provinceId) => { const row = d.distribution.rows.find((item) => item.provinceId === provinceId); if (row) change({ region: row.region, province: row.provinceVi }) }} height={460} />
      </ChartCard>
      <ChartCard className="chart-medium" eyebrow="02 · Phân phối" title="Vị trí của vùng trong toàn quốc" description={`${f.region} được nhấn mạnh; mỗi chấm vẫn là một tỉnh cụ thể.`} footer={<ChartMeta source={d.distribution.source} unit={d.distribution.unit} n={`${d.distribution.rowCount} tỉnh`} caveats={d.distribution.caveats} />}>
        <CartesianChart title="Phân phối điểm giữa các vùng" summary={`Mỗi chấm là một tỉnh; ${f.region} được tô đậm.`} data={boxplots} height={460} layout={{ xaxis: { title: { text: 'Điểm PAPI' }, automargin: true }, yaxis: { automargin: true }, showlegend: false, margin: { l: 112, r: 18, t: 10, b: 52 } }} />
      </ChartCard>
      <ChartCard className="chart-medium" eyebrow="03 · Xếp hạng" title={`Thứ tự trong ${f.region}`} description="Thanh đậm là tỉnh đang chọn; có thể chọn tỉnh chính xác bằng bộ lọc phía trên." footer={<ChartMeta source={d.ranking.source} unit={d.ranking.unit} n={`${d.ranking.rowCount} tỉnh`} caveats={d.ranking.caveats} />}>
        <CartesianChart title="Xếp hạng tỉnh trong vùng" summary={`${f.province} đứng thứ ${d.benchmark.rankRegion}/${d.benchmark.regionTotal}.`} data={rankingChart} height={390} onClick={(event) => { const province = String(event.points?.[0]?.customdata ?? ''); if (province) change({ province }) }} layout={{ xaxis: { title: { text: d.ranking.unit } }, yaxis: { automargin: true }, showlegend: false, margin: { l: 118, r: 20, t: 10, b: 48 } }}>
          <table><thead><tr><th>Tỉnh</th><th>Hạng vùng</th><th>Điểm</th></tr></thead><tbody>{d.ranking.rows.map((row) => <tr key={row.provinceId}><th>{row.provinceVi}</th><td>{row.rankRegion}/{d.benchmark.regionTotal}</td><td>{value(row.score)}</td></tr>)}</tbody></table>
        </CartesianChart>
      </ChartCard>
      <ChartCard className="chart-wide" eyebrow="04 · Cấu trúc lĩnh vực" title="Tỉnh khác vùng và toàn quốc ở đâu?" description="Ba mốc trên mỗi dòng giúp tách khác biệt tổng điểm khỏi khác biệt cấu trúc." footer={<ChartMeta source={d.profile.source} unit={d.profile.unit} n={`${d.profile.rowCount} lĩnh vực`} caveats={d.profile.caveats} />}>
        <CartesianChart title="So sánh điểm theo lĩnh vực" summary={`So sánh ${f.province}, trung bình ${f.region} và trung bình toàn quốc.`} data={profile} height={430} layout={{ xaxis: { title: { text: 'Điểm lĩnh vực' }, automargin: true }, yaxis: { automargin: true, tickfont: { size: 11 } }, legend: { orientation: 'h', y: -0.2 }, margin: { l: 112, r: 24, t: 24, b: 82 } }}>
          <table><thead><tr><th>Lĩnh vực</th><th>Tỉnh</th><th>Vùng</th><th>Toàn quốc</th></tr></thead><tbody>{d.profile.rows.map((row) => <tr key={row.code}><th>{labels.get(row.code) ?? row.code}</th><td>{value(row.provinceScore)}</td><td>{value(row.regionMean)}</td><td>{value(row.nationalMean)}</td></tr>)}</tbody></table>
        </CartesianChart>
      </ChartCard>
    </section>
    <section className="story"><p className="eyebrow">Bước đọc tiếp</p><h2>Xem diễn biến của chính tỉnh này</h2><p>Chuyển sang chuỗi thời gian nhưng giữ nguyên phạm vi và tỉnh đang chọn.</p><Link className="cta" to={`/time-trend?scale=${f.scale}&from=${first}&to=${trendTo}&province=${encodeURIComponent(f.province)}`}>Mở Diễn biến theo thời gian</Link></section>
  </article>
}
