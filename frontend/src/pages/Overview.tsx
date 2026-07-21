import { useEffect, useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import type { Data, Layout } from 'plotly.js'
import { Link, useNavigate, useSearchParams } from 'react-router-dom'

import { api, type GeojsonResponse, type OverviewResponse, type Scale } from '../api/client'
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
  ProvinceMap,
} from '../components/dashboard'
import { quadrantColors, uiColors } from '../theme/chartTheme'

const number = new Intl.NumberFormat('vi-VN', { minimumFractionDigits: 1, maximumFractionDigits: 2 })
const percentage = new Intl.NumberFormat('vi-VN', { maximumFractionDigits: 1 })
const validScale = (value: string | null): Scale => value === 'six' ? 'six' : 'eight'
const metric = (value: number | null) => value === null ? '—' : number.format(value)
const focusIds = new Set(['overview-map', 'overview-annual-change', 'overview-quadrants', 'overview-change-distribution'])

type OverviewData = OverviewResponse['data']
type OverviewMapRows = OverviewData['map']['rows']
type AnnualRows = OverviewData['storyCards']['annualChanges']['rows']
type QuadrantRows = OverviewData['storyCards']['quadrants']['rows']
type ChangeDistribution = OverviewData['storyCards']['changeDistribution']

function MapTable({ rows, selectedId }: { rows: OverviewMapRows; selectedId: number }) {
  return <details className="chart-table">
    <summary>Xem bảng tỉnh</summary>
    <div className="chart-table-scroll"><table><caption className="sr-only">Điểm và hạng PAPI theo tỉnh</caption><thead><tr><th>Tỉnh</th><th>Vùng</th><th>Điểm</th><th>Hạng</th></tr></thead><tbody>{rows.map((row) => <tr key={row.provinceId} className={row.provinceId === selectedId ? 'selected-row' : ''}><th scope="row">{row.provinceVi}</th><td>{row.region}</td><td>{metric(row.score)}</td><td>{row.rank}</td></tr>)}</tbody></table></div>
  </details>
}

function MapView({ rows, geojson, selectedId, unit, year, height, onSelect }: {
  rows: OverviewMapRows
  geojson: GeojsonResponse['data']['geojson']
  selectedId: number
  unit: string
  year: number
  height: number
  onSelect: (provinceId: number) => void
}) {
  return <>
    <ProvinceMap title={`Phân bố điểm PAPI năm ${year}`} summary={`Bản đồ của ${rows.length} tỉnh có dữ liệu; màu đậm biểu thị điểm cao hơn.`} rows={rows} geojson={geojson} selectedId={selectedId} unit={unit} onSelect={onSelect} height={height} />
    <MapTable rows={rows} selectedId={selectedId} />
  </>
}

function AnnualChangeTable({ rows }: { rows: AnnualRows }) {
  return <table><caption className="sr-only">Mức điểm và thay đổi theo năm</caption><thead><tr><th>Năm</th><th>Điểm</th><th>So với năm trước</th><th>Số tỉnh</th></tr></thead><tbody>{rows.map((row) => <tr key={row.year}><th scope="row">{row.year}</th><td>{metric(row.score)}</td><td>{row.change === null ? 'Mốc gốc' : `${row.change > 0 ? '+' : ''}${number.format(row.change)}`}</td><td>{row.contributorN}</td></tr>)}</tbody></table>
}

function AnnualChangeView({ rows, unit, height, onSelectYear }: { rows: AnnualRows; unit: string; height: number; onSelectYear: (year: number, baseline: boolean) => void }) {
  const trace: Data = {
    type: 'bar',
    x: rows.map((row) => row.year),
    y: rows.map((row) => row.baseline ? row.score : Math.abs(row.change ?? 0)),
    base: rows.map((row) => row.baseline ? 0 : (row.change ?? 0) >= 0 ? row.previousScore : row.score),
    text: rows.map((row) => row.baseline ? metric(row.score) : `${(row.change ?? 0) > 0 ? '+' : ''}${metric(row.change)}`),
    textposition: 'outside',
    customdata: rows.map((row) => [row.score, row.previousScore, row.change, row.contributorN, row.previousContributorN, row.baseline]),
    marker: {
      color: rows.map((row) => row.baseline ? uiColors.primary : (row.change ?? 0) >= 0 ? uiColors.positive : uiColors.negative),
      line: { color: uiColors.surface, width: 1 },
    },
    hovertemplate: '<b>%{x}</b><br>Điểm: %{customdata[0]:.2f}<br>Điểm năm trước: %{customdata[1]:.2f}<br>Thay đổi: %{customdata[2]:+.2f}<br>n = %{customdata[3]} tỉnh<extra></extra>',
  } as Data
  return <CartesianChart
    title="Mức thay đổi trung bình theo năm"
    summary="Mốc đầu là mức gốc; các thanh sau biểu thị tăng hoặc giảm so với năm trước."
    data={[trace]}
    height={height}
    onClick={(event) => {
      const point = event.points?.[0]
      const year = Number(point?.x)
      const custom = Array.isArray(point?.customdata) ? point.customdata : []
      if (Number.isInteger(year)) onSelectYear(year, Boolean(custom[5]))
    }}
    layout={{
      showlegend: false,
      bargap: 0.32,
      margin: { l: 62, r: 24, t: 28, b: 48 },
      xaxis: { dtick: 1, title: { text: 'Năm' } },
      yaxis: { title: { text: unit }, zeroline: true, zerolinewidth: 1.5 },
    } as Partial<Layout>}
  ><AnnualChangeTable rows={rows} /></CartesianChart>
}

function QuadrantTable({ rows }: { rows: QuadrantRows }) {
  return <table><caption className="sr-only">Phân bố tỉnh theo bốn nhóm lĩnh vực</caption><thead><tr><th>Nhóm</th><th>Số tỉnh</th><th>Tỷ lệ</th></tr></thead><tbody>{rows.map((row) => <tr key={row.label}><th scope="row">{row.label}</th><td>{row.n}</td><td>{percentage.format(row.percentage)}%</td></tr>)}</tbody></table>
}

function QuadrantView({ rows, pairLabel, pearsonR, height, hovered, onHover, onSelect }: {
  rows: QuadrantRows
  pairLabel: string
  pearsonR: number | null
  height: number
  hovered: number | null
  onHover: (index: number | null) => void
  onSelect: (label: string) => void
}) {
  const data: Data[] = rows.map((row, index) => ({
    type: 'bar',
    orientation: 'h',
    name: row.label,
    x: [row.n],
    y: ['Tỉnh'],
    text: [`${row.label}<br><b>${row.n}</b>`],
    textposition: 'inside',
    insidetextanchor: 'middle',
    customdata: [[row.label, row.percentage, row.provinces.slice(0, 5).join(', ')]],
    marker: { color: quadrantColors[row.label] ?? uiColors.muted, line: { color: hovered === index ? uiColors.ink : uiColors.surface, width: hovered === index ? 2.5 : 1 } },
    opacity: hovered === null || hovered === index ? 1 : 0.28,
    hovertemplate: '<b>%{customdata[0]}</b><br>%{x} tỉnh · %{customdata[1]:.1f}%<br>Ví dụ: %{customdata[2]}<extra></extra>',
  }))
  return <CartesianChart
    title={`Bốn nhóm của ${pairLabel}`}
    summary={`Pearson r = ${metric(pearsonR)}; đường chia dùng trung bình của từng lĩnh vực.`}
    data={data}
    height={height}
    onHover={(event) => onHover(event.points?.[0]?.curveNumber ?? null)}
    onUnhover={() => onHover(null)}
    onClick={(event) => {
      const custom = event.points?.[0]?.customdata
      if (Array.isArray(custom) && typeof custom[0] === 'string') onSelect(custom[0])
    }}
    layout={{
      barmode: 'stack', barnorm: 'percent', showlegend: false,
      uniformtext: { minsize: 10, mode: 'hide' },
      margin: { l: 16, r: 16, t: 44, b: 42 },
      xaxis: { range: [0, 100], ticksuffix: '%', title: { text: 'Tỷ lệ tỉnh' } },
      yaxis: { visible: false },
      annotations: [{ x: 0.5, y: 1.16, xref: 'paper', yref: 'paper', showarrow: false, text: `r = <b>${metric(pearsonR)}</b>`, font: { color: uiColors.ink, size: 13 } }],
    } as Partial<Layout>}
  ><QuadrantTable rows={rows} /></CartesianChart>
}

function DistributionTable({ distribution }: { distribution: ChangeDistribution }) {
  return <table><caption className="sr-only">Phân bố mức thay đổi điểm của tỉnh</caption><thead><tr><th>Khoảng thay đổi</th><th>Số tỉnh</th><th>Tỷ lệ</th></tr></thead><tbody>{distribution.bins.map((bin) => <tr key={`${bin.lower}-${bin.upper}`}><th scope="row">{number.format(bin.lower)} đến {number.format(bin.upper)}</th><td>{bin.count}</td><td>{percentage.format(bin.percentage)}%</td></tr>)}</tbody></table>
}

function ChangeDistributionView({ distribution, selectedRange, height, onSelect }: {
  distribution: ChangeDistribution
  selectedRange: [number, number] | null
  height: number
  onSelect: (lower: number, upper: number) => void
}) {
  const selected = (lower: number, upper: number) => selectedRange !== null && Math.abs(selectedRange[0] - lower) < 1e-8 && Math.abs(selectedRange[1] - upper) < 1e-8
  const trace: Data = {
    type: 'bar',
    x: distribution.bins.map((bin) => bin.center),
    y: distribution.bins.map((bin) => bin.count),
    width: distribution.bins.map((bin) => (bin.upper - bin.lower) * 0.94),
    customdata: distribution.bins.map((bin) => [bin.lower, bin.upper, bin.percentage, bin.provinces.slice(0, 6).join(', ')]),
    marker: {
      color: distribution.bins.map((bin) => bin.center >= 0 ? uiColors.positive : uiColors.negative),
      opacity: distribution.bins.map((bin) => selectedRange === null || selected(bin.lower, bin.upper) ? 0.9 : 0.3),
      line: { color: distribution.bins.map((bin) => selected(bin.lower, bin.upper) ? uiColors.ink : uiColors.surface), width: distribution.bins.map((bin) => selected(bin.lower, bin.upper) ? 2.5 : 1) },
    },
    hovertemplate: '<b>%{customdata[0]:+.2f} đến %{customdata[1]:+.2f}</b><br>%{y} tỉnh · %{customdata[2]:.1f}%<br>Ví dụ: %{customdata[3]}<extra></extra>',
  } as Data
  return <CartesianChart
    title={`Phân bố thay đổi ${distribution.fromYear}–${distribution.toYear}`}
    summary="Mỗi cột là một khoảng chênh lệch; đường dọc đánh dấu trung vị."
    data={[trace]}
    height={height}
    onClick={(event) => {
      const custom = event.points?.[0]?.customdata
      if (Array.isArray(custom)) onSelect(Number(custom[0]), Number(custom[1]))
    }}
    layout={{
      showlegend: false, bargap: 0.04,
      margin: { l: 54, r: 20, t: 28, b: 52 },
      xaxis: { title: { text: 'Thay đổi điểm' }, zeroline: true, zerolinewidth: 2 },
      yaxis: { title: { text: 'Số tỉnh' }, rangemode: 'tozero', dtick: 2 },
      shapes: distribution.median === null ? [] : [{ type: 'line', x0: distribution.median, x1: distribution.median, y0: 0, y1: 1, yref: 'paper', line: { color: uiColors.ink, dash: 'dot', width: 2 } }],
      annotations: distribution.median === null ? [] : [{ x: distribution.median, y: 1.03, yref: 'paper', text: `Trung vị ${number.format(distribution.median)}`, showarrow: false, font: { color: uiColors.ink, size: 11 } }],
    }}
  ><DistributionTable distribution={distribution} /></CartesianChart>
}

export function Overview() {
  const navigate = useNavigate()
  const [params, setParams] = useSearchParams()
  const metadata = useQuery({ queryKey: ['metadata'], queryFn: api.metadata })
  const geojson = useQuery({ queryKey: ['geojson'], queryFn: api.geojson })
  const scale = validScale(params.get('scale'))
  const available = metadata.data?.data.scales.find((item) => item.id === scale)
  const requestedYear = Number(params.get('year'))
  const year = available?.years.includes(requestedYear) ? requestedYear : (available?.years.at(-1) ?? 2024)
  const overview = useQuery({ queryKey: ['overview', scale, year], queryFn: () => api.overview(scale, year), enabled: Boolean(available) })
  const [hoveredQuadrant, setHoveredQuadrant] = useState<number | null>(null)
  const focusedChart = focusIds.has(params.get('focus') ?? '') ? params.get('focus') : null

  const updateParams = (changes: Record<string, string | null>, replace = false) => {
    setParams((current) => {
      const next = new URLSearchParams(current)
      for (const [key, value] of Object.entries(changes)) {
        if (value === null) next.delete(key)
        else next.set(key, value)
      }
      return next
    }, { replace })
  }

  useEffect(() => {
    const invalidFocus = params.has('focus') && !focusIds.has(params.get('focus') ?? '')
    if (available && (params.get('scale') !== scale || String(year) !== params.get('year') || invalidFocus)) {
      const next = new URLSearchParams(params)
      next.set('scale', scale)
      next.set('year', String(year))
      if (invalidFocus) next.delete('focus')
      setParams(next, { replace: true })
    }
  }, [available, params, scale, setParams, year])

  const updateFilter = (nextScale: Scale, candidateYear: number) => {
    const nextAvailability = metadata.data?.data.scales.find((item) => item.id === nextScale)
    const nextYear = nextAvailability?.years.includes(candidateYear) ? candidateYear : (nextAvailability?.years.at(-1) ?? candidateYear)
    setParams({ scale: nextScale, year: String(nextYear) })
  }

  if (metadata.isLoading || overview.isLoading || geojson.isLoading) return <LoadingSkeleton label="Đang tải Tổng quan" />
  const fault = metadata.error ?? overview.error ?? geojson.error
  if (fault) return <ErrorState title="FastAPI local chưa phản hồi dữ liệu" description={fault.message} action={<><button onClick={() => { void metadata.refetch(); void geojson.refetch(); void overview.refetch() }}>Thử lại</button><button className="text-button" onClick={() => updateFilter('eight', 2024)}>Đặt lại bộ lọc</button></>} />
  if (!metadata.data || !geojson.data || !overview.data || !available) return <EmptyState title="Chưa có dữ liệu để hiển thị" description="Hãy chọn lại phạm vi hoặc năm có dữ liệu." action={<button onClick={() => updateFilter('eight', 2024)}>Đặt lại bộ lọc</button>} />

  const data = overview.data.data
  const meta = overview.data.meta
  const rows = data.map.rows
  if (!rows.length) return <EmptyState title="Không có tỉnh phù hợp" description="Không render biểu đồ từ tập rỗng. Hãy đổi phạm vi hoặc năm." action={<button onClick={() => updateFilter('eight', 2024)}>Đặt lại bộ lọc</button>} />

  const labels = new Map(metadata.data.data.dimensions.map((item) => [item.code, item.nameVi]))
  const pair = data.storyCards.quadrants
  const pairLabel = `${labels.get(pair.x) ?? pair.x} × ${labels.get(pair.y) ?? pair.y}`
  const selectedProvince = rows.find((row) => row.provinceVi === params.get('province')) ?? null
  const selectedId = selectedProvince?.provinceId ?? -1
  const context = `${scale === 'six' ? '6 lĩnh vực' : '8 lĩnh vực'} · ${year} · ${meta.n} tỉnh`
  const selectedMinRaw = params.get('deltaMin')
  const selectedMaxRaw = params.get('deltaMax')
  const selectedMin = selectedMinRaw === null ? Number.NaN : Number(selectedMinRaw)
  const selectedMax = selectedMaxRaw === null ? Number.NaN : Number(selectedMaxRaw)
  const selectedRange: [number, number] | null = Number.isFinite(selectedMin) && Number.isFinite(selectedMax) ? [selectedMin, selectedMax] : null
  const isDefault = scale === 'eight' && year === (metadata.data.data.scales.find((item) => item.id === 'eight')?.years.at(-1) ?? 2024) && !params.has('province') && !params.has('deltaMin') && !params.has('focus')
  const focus = (id: string) => ({ id, activeContext: context, open: focusedChart === id, onOpenChange: (open: boolean) => updateParams({ focus: open ? id : null }) })
  const selectProvince = (provinceId: number) => {
    const province = rows.find((row) => row.provinceId === provinceId)
    if (province) updateParams({ province: province.provinceVi })
  }
  const selectRange = (lower: number, upper: number) => updateParams({ deltaMin: String(lower), deltaMax: String(upper) })

  const mapView = (height: number) => <MapView rows={rows} geojson={geojson.data.data.geojson} selectedId={selectedId} unit={data.map.unit} year={year} height={height} onSelect={selectProvince} />
  const annualView = (height: number) => <AnnualChangeView rows={data.storyCards.annualChanges.rows} unit={data.storyCards.annualChanges.unit} height={height} onSelectYear={(targetYear, baseline) => { if (!baseline) navigate(`/time-trend?scale=${scale}&from=${available.years[0]}&to=${targetYear}`) }} />
  const quadrantView = (height: number) => <QuadrantView rows={pair.rows} pairLabel={pairLabel} pearsonR={pair.pearsonR} height={height} hovered={hoveredQuadrant} onHover={setHoveredQuadrant} onSelect={(quadrant) => navigate(`/dimension?scale=${scale}&year=${year}&x=${pair.x}&y=${pair.y}&quadrant=${encodeURIComponent(quadrant)}`)} />
  const distributionView = (height: number) => <ChangeDistributionView distribution={data.storyCards.changeDistribution} selectedRange={selectedRange} height={height} onSelect={selectRange} />

  const mapInsight = <ChartInsight>{data.insights.map}</ChartInsight>
  const annualInsight = <ChartInsight>{data.insights.annualChange}</ChartInsight>
  const quadrantInsight = <ChartInsight>{data.insights.quadrants}</ChartInsight>
  const distributionInsight = <ChartInsight>{data.insights.changeDistribution}</ChartInsight>

  return <article className="overview overview-redesign">
    <DashboardPageHeader eyebrow="Tổng quan" title="Bức tranh PAPI toàn quốc" description="Nhìn nhanh phân bố, nhịp thay đổi, cấu trúc lĩnh vực và mức dịch chuyển của các tỉnh." aside={<p className="overview-scope">{context}</p>} />
    <FilterBar label="Bộ lọc Tổng quan" summary={<span aria-live="polite">Đang xem: <strong>{data.measure.label}</strong> · {year} · {meta.n} tỉnh có dữ liệu</span>} onReset={() => setParams({ scale: 'eight', year: '2024' })} resetDisabled={isDefault}>
      <label>Phạm vi so sánh<select value={scale} onChange={(event) => updateFilter(validScale(event.target.value), year)}><option value="six">6 lĩnh vực gốc</option><option value="eight">8 lĩnh vực</option></select></label>
      <label>Năm<select value={year} onChange={(event) => updateFilter(scale, Number(event.target.value))}>{available.years.map((item) => <option key={item} value={item}>{item}</option>)}</select></label>
    </FilterBar>
    <KpiGrid>
      <KpiCard label="Tỉnh có dữ liệu" value={`${meta.n}/63`} detail={`Năm ${year}`} />
      <KpiCard label="Điểm trung bình" value={metric(data.metrics.mean)} detail={data.measure.unit} />
      <KpiCard label="Tỉnh cao nhất" value={data.metrics.leader || '—'} detail={`${metric(data.metrics.max)} điểm`} />
      <KpiCard label="Khoảng cách cao nhất–thấp nhất" value={data.metrics.gap === null ? '—' : `${metric(data.metrics.gap)} điểm`} detail={data.metrics.last ? `Thấp nhất: ${data.metrics.last}` : 'Không đủ dữ liệu'} />
    </KpiGrid>

    <section className="overview-chart-grid" aria-label="Bốn góc nhìn Tổng quan">
      <ChartCard className="overview-chart-card" eyebrow="01 · Không gian" title="Điểm PAPI cao và thấp tập trung ở đâu?" description={`Phân bố ${data.measure.label} năm ${year}; click một tỉnh để giữ lựa chọn.`} insight={mapInsight} footer={<ChartMeta source={data.map.source} unit={data.map.unit} n={`${meta.n} tỉnh`} caveats={data.map.caveats} />} focus={{ ...focus('overview-map'), content: mapView(570) }}>
        {mapView(290)}
      </ChartCard>
      <ChartCard className="overview-chart-card" eyebrow="02 · Thời gian" title="Mặt bằng điểm thay đổi chủ yếu vào năm nào?" description={`Mức năm-kề-năm từ ${available.years[0]} đến ${year}; click một thanh để mở trang Diễn biến.`} insight={annualInsight} footer={<ChartMeta source={data.storyCards.annualChanges.source} unit={data.storyCards.annualChanges.unit} n={`${data.storyCards.annualChanges.rowCount} mốc năm`} caveats={data.storyCards.annualChanges.caveats} />} focus={{ ...focus('overview-annual-change'), content: annualView(570) }}>
        {annualView(290)}
      </ChartCard>
      <ChartCard className="overview-chart-card" eyebrow="03 · Quan hệ" title="Các tỉnh nằm trong bốn nhóm lĩnh vực nào?" description={`${pairLabel}; click một nhóm để xem quan hệ chi tiết.`} insight={quadrantInsight} footer={<ChartMeta source={pair.source} unit={pair.unit} n={`${pair.n} tỉnh`} caveats={pair.caveats} />} focus={{ ...focus('overview-quadrants'), content: quadrantView(520) }}>
        {quadrantView(290)}
      </ChartCard>
      <ChartCard className="overview-chart-card" eyebrow="04 · Thay đổi" title="Phần lớn tỉnh cải thiện hay suy giảm?" description={`Chênh lệch từ ${data.storyCards.changeDistribution.fromYear} đến ${year}; click một cột để giữ khoảng thay đổi.`} insight={distributionInsight} footer={<ChartMeta source={data.storyCards.changeDistribution.source} unit={data.storyCards.changeDistribution.unit} n={`${data.storyCards.changeDistribution.n} tỉnh`} caveats={data.storyCards.changeDistribution.caveats} />} focus={{ ...focus('overview-change-distribution'), content: distributionView(540) }}>
        {distributionView(290)}
      </ChartCard>
    </section>

    {(selectedProvince || selectedRange) && <section className="overview-selection" aria-live="polite">
      <div><p className="eyebrow">Đang chọn</p>{selectedProvince && <p><strong>{selectedProvince.provinceVi}</strong> · {selectedProvince.region} · hạng {selectedProvince.rank}</p>}{selectedRange && <p>Khoảng thay đổi {number.format(selectedRange[0])} đến {number.format(selectedRange[1])} điểm</p>}</div>
      <div>{selectedProvince && <Link to={`/provincial?scale=${scale}&year=${year}&province=${encodeURIComponent(selectedProvince.provinceVi)}`}>Xem hồ sơ tỉnh <span aria-hidden="true">→</span></Link>}<button type="button" className="text-button" onClick={() => updateParams({ province: null, deltaMin: null, deltaMax: null })}>Bỏ lựa chọn</button></div>
    </section>}
  </article>
}
