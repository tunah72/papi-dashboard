import { useEffect, useMemo, useState } from 'react'
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

const number = new Intl.NumberFormat('vi-VN', { minimumFractionDigits: 1, maximumFractionDigits: 2 })
const validScale = (value: string | null): Scale => value === 'six' ? 'six' : 'eight'
const metric = (value: number | null) => value === null ? '—' : number.format(value)

export function Overview() {
  const [params, setParams] = useSearchParams()
  const metadata = useQuery({ queryKey: ['metadata'], queryFn: api.metadata })
  const geojson = useQuery({ queryKey: ['geojson'], queryFn: api.geojson })
  const scale = validScale(params.get('scale'))
  const available = metadata.data?.data.scales.find((item) => item.id === scale)
  const requestedYear = Number(params.get('year'))
  const year = available?.years.includes(requestedYear) ? requestedYear : (available?.years.at(-1) ?? 2024)
  const overview = useQuery({ queryKey: ['overview', scale, year], queryFn: () => api.overview(scale, year), enabled: Boolean(available) })
  const [selectedId, setSelectedId] = useState<number | null>(null)
  const [ranking, setRanking] = useState<'top' | 'bottom'>('top')

  useEffect(() => {
    if (available && (params.get('scale') !== scale || String(year) !== params.get('year'))) {
      setParams((current) => {
        current.set('scale', scale)
        current.set('year', String(year))
        return current
      }, { replace: true })
    }
  }, [available, params, scale, setParams, year])

  const update = (nextScale: Scale, candidateYear: number) => {
    const nextAvailability = metadata.data?.data.scales.find((item) => item.id === nextScale)
    const nextYear = nextAvailability?.years.includes(candidateYear) ? candidateYear : (nextAvailability?.years.at(-1) ?? candidateYear)
    setParams({ scale: nextScale, year: String(nextYear) })
  }
  const selected = useMemo(() => overview.data?.data.map.rows.find((row) => row.provinceVi === params.get('province'))
    ?? overview.data?.data.map.rows.find((row) => row.provinceId === selectedId) ?? null, [overview.data, params, selectedId])

  if (metadata.isLoading || overview.isLoading || geojson.isLoading) return <LoadingSkeleton label="Đang tải Tổng quan" />
  const fault = metadata.error ?? overview.error ?? geojson.error
  if (fault) return <ErrorState title="FastAPI local chưa phản hồi dữ liệu" description={fault.message} action={<><button onClick={() => { void metadata.refetch(); void geojson.refetch(); void overview.refetch() }}>Thử lại</button><button className="text-button" onClick={() => update('eight', 2024)}>Đặt lại bộ lọc</button></>} />
  if (!metadata.data || !geojson.data || !overview.data || !available) return <EmptyState title="Chưa có dữ liệu để hiển thị" description="Hãy chọn lại phạm vi hoặc năm có dữ liệu." action={<button onClick={() => update('eight', 2024)}>Đặt lại bộ lọc</button>} />

  const data = overview.data.data
  const meta = overview.data.meta
  const rows = data.map.rows
  if (!rows.length) return <EmptyState title="Không có tỉnh phù hợp" description="Không render biểu đồ từ tập rỗng. Hãy đổi phạm vi hoặc năm." action={<button onClick={() => update('eight', 2024)}>Đặt lại bộ lọc</button>} />

  const labels = new Map(metadata.data.data.dimensions.map((item) => [item.code, item.nameVi]))
  const shortLabels = new Map(metadata.data.data.dimensions.map((item) => [item.code, item.short]))
  const rankingRows = ranking === 'top' ? data.ranking.top10 : data.ranking.bottom10
  const selectedProvince = selected ?? rows[0]
  const selectedOutsideRanking = !rankingRows.some((row) => row.provinceId === selectedProvince.provinceId)
  const provincialLink = `/provincial?scale=${scale}&year=${year}&province=${encodeURIComponent(selectedProvince.provinceVi)}`
  const selectProvince = (provinceId: number) => {
    const province = rows.find((row) => row.provinceId === provinceId)
    if (province) {
      setSelectedId(provinceId)
      setParams({ scale, year: String(year), province: province.provinceVi })
    }
  }

  const trend = data.storyCards.trend
  const trendData: Data[] = [{
    type: 'scatter', mode: 'lines+markers',
    x: trend.rows.map((row) => row.year), y: trend.rows.map((row) => row.score),
    customdata: trend.rows.map((row) => row.contributorN),
    line: { color: uiColors.primary, width: 3 }, marker: { color: '#fff', line: { color: uiColors.primary, width: 2 }, size: 8 },
    hovertemplate: `%{x}: <b>%{y:.2f}</b><br>%{customdata} tỉnh<extra></extra>`,
  }]
  const regions = [...data.storyCards.regions.rows].sort((a, b) => (a.meanScore ?? -Infinity) - (b.meanScore ?? -Infinity))
  const regionData: Data[] = [{
    type: 'bar', orientation: 'h',
    x: regions.map((row) => row.meanScore), y: regions.map((row) => shortRegionLabel(row.region)),
    customdata: regions.map((row) => [row.region, row.minScore, row.maxScore, row.n]),
    marker: { color: regions.map((row) => colorForRegion(row.region)) },
    hovertemplate: '<b>%{customdata[0]}</b><br>Trung bình: %{x:.2f}<br>Khoảng: %{customdata[1]:.2f}–%{customdata[2]:.2f}<br>n = %{customdata[3]}<extra></extra>',
  }]
  const pair = data.storyCards.strongestPair
  const pairRegions = [...new Set(pair.rows.map((row) => row.region))]
  const pairData: Data[] = pairRegions.map((region) => ({
    type: 'scatter', mode: 'markers', name: region,
    x: pair.rows.filter((row) => row.region === region).map((row) => row.x),
    y: pair.rows.filter((row) => row.region === region).map((row) => row.y),
    text: pair.rows.filter((row) => row.region === region).map((row) => row.provinceVi),
    marker: { color: colorForRegion(region), size: 8, opacity: 0.82 },
    hovertemplate: '<b>%{text}</b><br>x = %{x:.2f}<br>y = %{y:.2f}<extra>%{fullData.name}</extra>',
  }))
  const changes = [...new Map([...data.storyCards.changeHighlights.top8, ...data.storyCards.changeHighlights.bottom8]
    .map((row) => [row.provinceVi, row])).values()].sort((a, b) => (a.change ?? 0) - (b.change ?? 0))
  const changeData: Data[] = [{
    type: 'bar', orientation: 'h',
    x: changes.map((row) => row.change), y: changes.map((row) => row.provinceVi),
    marker: { color: changes.map((row) => (row.change ?? 0) >= 0 ? uiColors.positive : uiColors.negative) },
    customdata: changes.map((row) => row.region),
    hovertemplate: '<b>%{y}</b><br>%{x:+.2f} điểm<br>%{customdata}<extra></extra>',
  }]
  const strongestRegion = [...regions].sort((a, b) => (b.meanScore ?? -Infinity) - (a.meanScore ?? -Infinity))[0]
  const pairLabel = `${labels.get(pair.x) ?? pair.x} × ${labels.get(pair.y) ?? pair.y}`

  return <article className="overview">
    <DashboardPageHeader eyebrow="Tổng quan · Bức tranh nhanh" title="Điểm quản trị, nhìn từ từng tỉnh" description="Từ phân bố không gian đến xu hướng, khác biệt vùng và các tín hiệu thay đổi nổi bật trong dữ liệu PAPI." aside={<p className="status">Dữ liệu đã xử lý · local</p>} />
    <FilterBar label="Bộ lọc Tổng quan" summary={data.measure.unit} onReset={() => update('eight', 2024)}>
      <label>Phạm vi<select value={scale} onChange={(event) => update(validScale(event.target.value), year)}><option value="six">Tổng 6 lĩnh vực gốc</option><option value="eight">Tổng PAPI (8 lĩnh vực)</option></select></label>
      <label>Năm<select value={year} onChange={(event) => update(scale, Number(event.target.value))}>{available.years.map((item) => <option key={item} value={item}>{item}</option>)}</select></label>
    </FilterBar>
    <KpiGrid>
      <KpiCard label="Tỉnh có dữ liệu" value={`${meta.n}/63`} detail={`Snapshot ${year}`} />
      <KpiCard label="Điểm trung bình" value={metric(data.metrics.mean)} detail={data.measure.unit} tone="accent" />
      <KpiCard label="Dẫn đầu" value={data.metrics.leader || '—'} detail={metric(data.metrics.max)} tone="positive" />
      <KpiCard label="Khoảng cách đầu–cuối" value={data.metrics.gap === null ? '—' : `${metric(data.metrics.gap)} điểm`} detail={data.metrics.last ? `${data.metrics.last} xếp cuối` : 'Thiếu dữ liệu'} tone="negative" />
    </KpiGrid>
    <InsightCard label="Điểm cần đọc">
      <p><strong>{data.metrics.leader}</strong> dẫn đầu, trong khi <strong>{data.metrics.last}</strong> ở cuối bảng. {strongestRegion ? `${strongestRegion.region} có trung bình vùng cao nhất trong snapshot này.` : ''}</p>
    </InsightCard>

    <section className="overview-grid">
      <ChartCard className="map-surface" eyebrow="01 · Phân bố không gian" title={`Bản đồ PAPI ${year}`} description="Màu đậm hơn biểu thị điểm cao hơn; viền đậm là tỉnh đang chọn." footer={<ChartMeta source={data.map.source} unit={data.map.unit} n={`${meta.n} tỉnh`} caveats={data.map.caveats} />}>
        <ProvinceMap title={`Bản đồ PAPI ${year}`} summary={`Điểm PAPI của ${meta.n} tỉnh; chọn tỉnh để đồng bộ xếp hạng.`} rows={rows} geojson={geojson.data.data.geojson} selectedId={selectedProvince.provinceId} unit={data.map.unit} onSelect={selectProvince} />
      </ChartCard>
      <aside className="ranking"><div className="section-heading"><div><p className="eyebrow">Xếp hạng liên kết</p><h2>Đọc hai cực trị</h2></div></div><div className="tabs" role="tablist" aria-label="Hướng xếp hạng"><button role="tab" aria-selected={ranking === 'top'} onClick={() => setRanking('top')}>Cao nhất</button><button role="tab" aria-selected={ranking === 'bottom'} onClick={() => setRanking('bottom')}>Thấp nhất</button></div>{selectedOutsideRanking && <button className="selected-pin selected" onClick={() => selectProvince(selectedProvince.provinceId)}><span>Tỉnh đang chọn: <strong>{selectedProvince.provinceVi}</strong></span><strong>{selectedProvince.score === null ? '—' : number.format(selectedProvince.score)}</strong></button>}<ol>{rankingRows.map((row) => <li key={row.provinceId}><button className={selectedProvince.provinceId === row.provinceId ? 'selected' : ''} onClick={() => selectProvince(row.provinceId)}><span><b>{row.rank}</b>{row.provinceVi}<small>{row.region}</small></span><strong>{row.score === null ? '—' : number.format(row.score)}</strong></button></li>)}</ol><ChartMeta source={data.ranking.source} unit={data.ranking.unit} n={`${meta.n} tỉnh`} caveats={data.ranking.caveats} /></aside>
    </section>
    <section className="selection" aria-live="polite"><p className="eyebrow">Tỉnh đang chọn</p><h2>{selectedProvince.provinceVi}</h2><p>{selectedProvince.region} · <strong>{selectedProvince.score === null ? 'Thiếu dữ liệu' : `${number.format(selectedProvince.score)} ${data.measure.unit}`}</strong></p><Link className="cta" to={provincialLink}>Xem hồ sơ tỉnh <span aria-hidden="true">→</span></Link></section>

    <section className="dashboard-grid overview-story-grid" aria-label="Bốn góc nhìn bổ trợ">
      <ChartCard className="chart-wide" eyebrow="02 · Xu hướng" title="Mặt bằng chung qua thời gian" description={`Chuỗi từ ${trend.rows[0]?.year ?? '—'} đến ${year}; mỗi điểm là trung bình các tỉnh có dữ liệu.`} footer={<ChartMeta source={trend.source} unit={trend.unit} n={`${trend.rowCount} mốc năm`} caveats={trend.caveats} />}>
        <CartesianChart title="Xu hướng điểm PAPI toàn quốc" summary="Đường thời gian của điểm trung bình PAPI." data={trendData} height={330} layout={{ xaxis: { dtick: 1, title: { text: 'Năm' } }, yaxis: { title: { text: trend.unit } }, showlegend: false }} />
      </ChartCard>
      <ChartCard className="chart-medium" eyebrow="03 · Khác biệt vùng" title="Vùng nào đang dẫn trước?" description="So sánh trung bình vùng, đồng thời giữ khoảng min–max trong tooltip." footer={<ChartMeta source={data.storyCards.regions.source} unit={data.storyCards.regions.unit} n={`${data.storyCards.regions.rowCount} vùng`} caveats={data.storyCards.regions.caveats} />}>
        <CartesianChart title="Điểm trung bình theo vùng" summary="Thanh ngang được sắp từ thấp đến cao." data={regionData} height={330} layout={{ xaxis: { title: { text: 'Điểm PAPI' } }, yaxis: { automargin: true }, showlegend: false, margin: { l: 112, r: 24, t: 12, b: 48 } }} />
      </ChartCard>
      <ChartCard className="chart-medium" eyebrow="04 · Mối quan hệ" title="Cặp lĩnh vực liên hệ mạnh nhất" description={`${pairLabel}; Pearson r = ${pair.pearsonR === null ? '—' : number.format(pair.pearsonR)}.`} footer={<ChartMeta source={pair.source} unit={pair.unit} n={`${pair.n} tỉnh`} caveats={pair.caveats} />}>
        <CartesianChart title={`Phân tán ${pairLabel}`} summary="Mỗi điểm là một tỉnh, màu biểu thị vùng." data={pairData} height={360} layout={{ xaxis: { title: { text: shortLabels.get(pair.x) ?? pair.x } }, yaxis: { title: { text: shortLabels.get(pair.y) ?? pair.y } }, shapes: [{ type: 'line', x0: pair.xMean ?? 0, x1: pair.xMean ?? 0, y0: 0, y1: 1, yref: 'paper', line: { color: uiColors.border, dash: 'dot' } }, { type: 'line', y0: pair.yMean ?? 0, y1: pair.yMean ?? 0, x0: 0, x1: 1, xref: 'paper', line: { color: uiColors.border, dash: 'dot' } }] }} />
      </ChartCard>
      <ChartCard className="chart-wide" eyebrow="05 · Thay đổi" title="Những tỉnh dịch chuyển mạnh nhất" description={`Chênh lệch giữa ${available.years[0]} và ${year}; chỉ dùng tỉnh đủ dữ liệu ở hai mốc.`} footer={<ChartMeta source={data.storyCards.changeHighlights.source} unit={data.storyCards.changeHighlights.unit} n={`${data.storyCards.changeHighlights.n} tỉnh`} caveats={data.storyCards.changeHighlights.caveats} />}>
        <CartesianChart title="Tăng và giảm nổi bật" summary="Thanh xanh là tăng, thanh đỏ là giảm so với mốc đầu." data={changeData} height={360} layout={{ xaxis: { title: { text: 'Thay đổi điểm' }, zeroline: true, zerolinewidth: 2 }, yaxis: { automargin: true }, showlegend: false, margin: { l: 120, r: 24, t: 12, b: 48 } }} />
      </ChartCard>
    </section>
    <section className="story"><p className="eyebrow">Bước đọc tiếp</p><h2>Đi sâu từ bản đồ tới hồ sơ địa phương</h2><p>Giữ nguyên phạm vi, năm và tỉnh đang chọn để tiếp tục khám phá mà không mất ngữ cảnh.</p><div className="story-links"><Link to={`/time-trend?scale=${scale}&year=${year}`}>Diễn biến theo thời gian</Link><Link to={provincialLink}>Vùng & tỉnh</Link><Link to={`/dimension?scale=${scale}&year=${year}`}>Mối quan hệ lĩnh vực</Link><Link to={`/dynamics?scale=${scale}&year=${year}`}>Thay đổi & phân nhóm</Link></div></section>
  </article>
}
