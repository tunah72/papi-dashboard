import { useEffect, useRef, useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import type { Data, Layout } from 'plotly.js'
import { useSearchParams } from 'react-router-dom'

import { api, type Scale } from '../api/client'
import { CartesianChart } from '../components/CartesianChart'
import { SankeyChart } from '../components/SankeyChart'
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
import { uiColors } from '../theme/chartTheme'

const scoreFmt = new Intl.NumberFormat('vi-VN', { maximumFractionDigits: 2 })
const deltaFmt = new Intl.NumberFormat('vi-VN', { maximumFractionDigits: 2, signDisplay: 'exceptZero' })
const percentFmt = new Intl.NumberFormat('vi-VN', { maximumFractionDigits: 1 })
const scaleOf = (value: string | null): Scale => value === 'six' ? 'six' : 'eight'
const clusterColors: Record<string, string> = { A: '#25736F', B: '#4C78A8', C: '#E39A54', D: '#8A6CB1', E: '#C96B5C', F: '#6B8E45' }
const focusIds = new Set(['dynamics-change', 'dynamics-profiles', 'dynamics-pca', 'dynamics-transition'])
type Sort = 'provinceVi' | 'change' | 'fromScore' | 'toScore' | 'startCluster' | 'endCluster'
type Direction = 'both' | 'increase' | 'decrease'

function alpha(hex: string, opacity: number) {
  const value = hex.replace('#', '')
  const red = Number.parseInt(value.slice(0, 2), 16)
  const green = Number.parseInt(value.slice(2, 4), 16)
  const blue = Number.parseInt(value.slice(4, 6), 16)
  return `rgba(${red}, ${green}, ${blue}, ${opacity})`
}

export function Dynamics() {
  const [params, setParams] = useSearchParams()
  const [search, setSearch] = useState('')
  const [sort, setSort] = useState<Sort>('change')
  const [descending, setDescending] = useState(true)
  const [direction, setDirection] = useState<Direction>('both')
  const [hoveredProfile, setHoveredProfile] = useState<string | null>(null)
  const [hoveredProvince, setHoveredProvince] = useState<string | null>(null)
  const [hoveredFlow, setHoveredFlow] = useState<string | null>(null)
  const [tableOpen, setTableOpen] = useState(false)
  const tableRef = useRef<HTMLDetailsElement>(null)
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
    const response = query.data
    if (!response) return
    const f = response.meta.filters
    const model = response.data.clusterModel
    const clusterKeys = model.centroids.map((row) => row.cluster)
    const province = params.get('province')
    const profile = params.get('profile')
    const flow = params.get('flow')
    const focus = params.get('focus')
    const canonical = new URLSearchParams({ scale: f.scale, from: String(f.from), to: String(f.to), k: String(f.k) })
    if (province && model.assignments.some((row) => row.provinceVi === province)) canonical.set('province', province)
    if (profile && clusterKeys.includes(profile)) canonical.set('profile', profile)
    if (flow && model.transitions.some((row) => `${row.fromCluster}-${row.toCluster}` === flow)) canonical.set('flow', flow)
    if (focus && focusIds.has(focus)) canonical.set('focus', focus)
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
  const clusterName = (key: string) => `Hồ sơ ${key}`
  const profileParam = params.get('profile')
  const activeProfile = profileParam && clusterKeys.includes(profileParam) ? profileParam : clusterKeys[0]
  const provinceParam = params.get('province')
  const selectedProvince = model.assignments.find((row) => row.provinceVi === provinceParam)?.provinceVi ?? null
  const flowParam = params.get('flow')
  const selectedFlow = model.transitions.find((row) => `${row.fromCluster}-${row.toCluster}` === flowParam) ?? null
  const focused = focusIds.has(params.get('focus') ?? '') ? params.get('focus') : null

  const update = (changes: Record<string, string | null>) => setParams((current) => {
    const next = new URLSearchParams(current)
    Object.entries(changes).forEach(([key, value]) => value === null ? next.delete(key) : next.set(key, value))
    return next
  })
  const change = (next: Partial<{ scale: Scale; from: number; to: number; k: number | 'auto' }>) => {
    const nextScale = next.scale ?? f.scale
    const nextCfg = metadata.data!.data.scales.find((item) => item.id === nextScale)!
    const nextFrom = next.scale ? nextCfg.years[0] : (next.from ?? f.from)
    const nextTo = next.scale ? nextCfg.years.at(-1)! : (next.to ?? f.to)
    const safeTo = nextTo > nextFrom ? nextTo : (nextCfg.years.find((year) => year > nextFrom) ?? nextCfg.years.at(-1)!)
    const target = new URLSearchParams({ scale: nextScale, from: String(nextFrom), to: String(safeTo), k: String(next.k ?? f.k) })
    for (const key of ['province', 'profile', 'flow', 'focus']) {
      const value = params.get(key)
      if (value) target.set(key, value)
    }
    setParams(target)
  }
  const focus = (id: string, activeContext?: string) => ({ id, activeContext, open: focused === id, onOpenChange: (open: boolean) => update({ focus: open ? id : null }) })
  const pinProvince = (province: unknown) => {
    if (typeof province !== 'string') return
    update({ province })
    setTableOpen(true)
  }
  const selectProfile = (profile: unknown) => { if (typeof profile === 'string' && clusterKeys.includes(profile)) update({ profile }) }
  const selectFlow = (fromCluster: unknown, toCluster: unknown) => {
    if (typeof fromCluster === 'string' && typeof toCluster === 'string') update({ flow: `${fromCluster}-${toCluster}` })
  }

  const assignmentsByProvince = new Map(model.assignments.map((row) => [row.provinceVi, row]))
  const verificationRows = d.changes.rows.map((row) => {
    const assignment = assignmentsByProvince.get(row.provinceVi)
    return { ...row, startCluster: assignment?.startCluster ?? '—', endCluster: assignment?.endCluster ?? '—' }
  })
  const allRows = verificationRows.filter((row) => row.provinceVi.toLocaleLowerCase('vi').includes(search.toLocaleLowerCase('vi'))).sort((a, b) => {
    const av = a[sort]; const bv = b[sort]
    const resultSort = typeof av === 'string' && typeof bv === 'string' ? av.localeCompare(bv, 'vi') : Number(av ?? 0) - Number(bv ?? 0)
    return descending ? -resultSort : resultSort
  })
  const setSortField = (field: Sort) => { if (field === sort) setDescending((value) => !value); else { setSort(field); setDescending(field !== 'provinceVi') } }
  const sortDirection = (field: Sort) => sort === field ? (descending ? 'descending' : 'ascending') : 'none'
  const sortAction = (field: Sort, label: string) => sort === field ? `${label}, đang ${descending ? 'giảm dần' : 'tăng dần'}; chọn để đảo thứ tự` : `${label}; chọn để sắp xếp`

  const allExtremeRows = [...new Map([...d.changes.top8, ...d.changes.bottom8].map((row) => [row.provinceVi, row])).values()]
  const filteredExtremeRows = allExtremeRows.filter((row) => direction === 'both' || (direction === 'increase' ? (row.change ?? 0) >= 0 : (row.change ?? 0) < 0))
  const extremeRows = (filteredExtremeRows.length ? filteredExtremeRows : allExtremeRows).sort((a, b) => (b.change ?? 0) - (a.change ?? 0))
  const dumbbellData: Data[] = extremeRows.map((row) => {
    const positive = (row.change ?? 0) >= 0
    const color = positive ? uiColors.positive : uiColors.negative
    const selected = !selectedProvince || selectedProvince === row.provinceVi
    return {
      type: 'scatter', mode: 'lines+markers+text', name: row.provinceVi,
      x: [row.fromScore, row.toScore], y: [row.provinceVi, row.provinceVi],
      text: ['', deltaFmt.format(row.change ?? 0)], textposition: ['middle left', 'middle right'],
      customdata: [[row.provinceVi, row.region, row.fromScore, row.toScore, row.change], [row.provinceVi, row.region, row.fromScore, row.toScore, row.change]],
      line: { color, width: selectedProvince === row.provinceVi ? 4 : 2.5 },
      marker: { color, size: [9, selectedProvince === row.provinceVi ? 15 : 11], symbol: ['circle-open', 'circle'], line: { color: uiColors.ink, width: [1.4, selectedProvince === row.provinceVi ? 2.5 : 0.7] } },
      opacity: selected ? 0.92 : 0.2, showlegend: false,
      hovertemplate: '<b>%{customdata[0]}</b><br>%{customdata[1]}<br>Đầu %{customdata[2]:.2f} · cuối %{customdata[3]:.2f}<br>Thay đổi %{customdata[4]:+.2f}<extra></extra>',
    } as unknown as Data
  })
  const endpointScores = extremeRows.flatMap((row) => [row.fromScore, row.toScore]).filter((value): value is number => value !== null)
  const scoreMin = Math.min(...endpointScores)
  const scoreMax = Math.max(...endpointScores)
  const scorePadding = Math.max((scoreMax - scoreMin) * 0.12, 0.5)
  const dumbbellView = (height: number) => <CartesianChart title="Điểm đầu–cuối của các tỉnh thay đổi mạnh" summary="Chấm rỗng là mốc đầu, chấm đặc là mốc cuối; dấu của nhãn cho biết hướng thay đổi." data={dumbbellData} height={height} onClick={(event) => { const raw = event.points?.[0]?.customdata; if (Array.isArray(raw)) pinProvince(raw[0]) }} layout={{ xaxis: { title: { text: d.measure.unit }, range: [scoreMin - scorePadding, scoreMax + scorePadding] }, yaxis: { categoryorder: 'array', categoryarray: extremeRows.map((row) => row.provinceVi), autorange: 'reversed', automargin: true }, margin: { l: 108, r: 62, t: 22, b: 54 } }}>
    <div className="chart-table-scroll"><table><caption className="sr-only">Các tỉnh thay đổi mạnh nhất</caption><thead><tr><th>Tỉnh</th><th>{f.from}</th><th>{f.to}</th><th>Thay đổi</th></tr></thead><tbody>{extremeRows.map((row) => <tr key={row.provinceVi}><th scope="row"><button type="button" aria-pressed={selectedProvince === row.provinceVi} onClick={() => pinProvince(row.provinceVi)}>{row.provinceVi}</button></th><td>{scoreFmt.format(row.fromScore ?? 0)}</td><td>{scoreFmt.format(row.toScore ?? 0)}</td><td>{deltaFmt.format(row.change ?? 0)}</td></tr>)}</tbody></table></div>
  </CartesianChart>

  const dimensionCodes = cfg.dimensions
  const profileColumns = clusterKeys.length > 4 ? 2 : Math.ceil(clusterKeys.length / 2)
  const profileRows = Math.ceil(clusterKeys.length / profileColumns)
  const profilePinned = profileParam && clusterKeys.includes(profileParam) ? profileParam : null
  const profileData: Data[] = model.centroids.map((centroid, index) => ({
    type: 'bar', orientation: 'h', name: clusterName(centroid.cluster),
    x: dimensionCodes.map((code) => centroid.values.find((value) => value.code === code)?.zScore ?? null),
    y: dimensionCodes.map((code) => labels.get(code) ?? code),
    text: clusterKeys.length > 4 ? undefined : dimensionCodes.map((code) => deltaFmt.format(centroid.values.find((value) => value.code === code)?.zScore ?? 0)), textposition: 'auto',
    customdata: dimensionCodes.map((code) => {
      const value = centroid.values.find((item) => item.code === code)
      return [centroid.cluster, labels.get(code) ?? code, value?.rawScore, value?.zScore, centroid.nStart, centroid.nEnd]
    }),
    marker: {
      color: dimensionCodes.map((code) => (centroid.values.find((value) => value.code === code)?.zScore ?? 0) >= 0 ? uiColors.positive : uiColors.negative),
      line: { color: uiColors.ink, width: activeProfile === centroid.cluster ? 1.5 : 0 },
    },
    opacity: (hoveredProfile || profilePinned) && (hoveredProfile ?? profilePinned) !== centroid.cluster ? 0.22 : 0.9,
    xaxis: index === 0 ? 'x' : `x${index + 1}`, yaxis: index === 0 ? 'y' : `y${index + 1}`,
    hovertemplate: '<b>Hồ sơ %{customdata[0]} · %{customdata[1]}</b><br>z-score %{customdata[3]:+.2f}<br>Điểm gốc %{customdata[2]:.2f}<br>n đầu/cuối %{customdata[4]}/%{customdata[5]}<extra></extra>',
    showlegend: false,
  } as unknown as Data))
  const maxProfileZ = Math.max(1, ...model.centroids.flatMap((centroid) => centroid.values.map((value) => Math.abs(value.zScore ?? 0))))
  const profileLayout: Partial<Layout> & Record<string, unknown> = {
    grid: { rows: profileRows, columns: profileColumns, pattern: 'independent', roworder: 'top to bottom', xgap: 0.14, ygap: 0.26 },
    margin: { l: 88, r: 18, t: 46, b: 42 },
    annotations: model.centroids.map((centroid, index) => ({
      xref: 'paper', yref: 'paper', showarrow: false,
      x: (index % profileColumns + 0.5) / profileColumns,
      y: 1.06 - Math.floor(index / profileColumns) / profileRows,
      text: `<b>Hồ sơ ${centroid.cluster}</b> · ${centroid.nStart}/${centroid.nEnd}`,
      font: { size: clusterKeys.length > 4 ? 9 : 11, color: activeProfile === centroid.cluster ? uiColors.primary : uiColors.ink },
    })),
  }
  model.centroids.forEach((_, index) => {
    const suffix = index === 0 ? '' : String(index + 1)
    profileLayout[`xaxis${suffix}`] = { range: [-maxProfileZ, maxProfileZ], zeroline: true, zerolinewidth: 1.5, tickfont: { size: 9 } }
    profileLayout[`yaxis${suffix}`] = { automargin: true, autorange: 'reversed', showticklabels: index % profileColumns === 0, tickfont: { size: 9 } }
  })
  const profileView = (height: number) => <CartesianChart title="Đặc trưng chuẩn hóa của từng hồ sơ" summary="Mỗi panel dùng cùng trục z-score; thanh phải cao hơn và thanh trái thấp hơn mặt bằng năm." data={profileData} height={height} onHover={(event) => { const raw = event.points?.[0]?.customdata; if (Array.isArray(raw) && typeof raw[0] === 'string') setHoveredProfile(raw[0]) }} onUnhover={() => setHoveredProfile(null)} onClick={(event) => { const raw = event.points?.[0]?.customdata; if (Array.isArray(raw)) selectProfile(raw[0]) }} layout={profileLayout as Partial<Layout>}>
    <div className="chart-table-scroll"><table><caption className="sr-only">Đặc trưng các hồ sơ</caption><thead><tr><th>Hồ sơ</th><th>Lĩnh vực</th><th>z-score</th><th>Điểm gốc</th></tr></thead><tbody>{model.centroids.flatMap((centroid) => centroid.values.map((value) => <tr key={`${centroid.cluster}-${value.code}`}><th scope="row">{clusterName(centroid.cluster)}</th><td>{labels.get(value.code) ?? value.code}</td><td>{deltaFmt.format(value.zScore ?? 0)}</td><td>{scoreFmt.format(value.rawScore ?? 0)}</td></tr>))}</tbody></table></div>
  </CartesianChart>

  const matchesSelection = (row: typeof model.assignments[number]) => {
    if (selectedProvince && row.provinceVi !== selectedProvince) return false
    if (selectedFlow && (row.startCluster !== selectedFlow.fromCluster || row.endCluster !== selectedFlow.toCluster)) return false
    if (profilePinned && row.startCluster !== profilePinned && row.endCluster !== profilePinned) return false
    if (hoveredProvince && row.provinceVi !== hoveredProvince) return false
    return true
  }
  const segmentData: Data[] = model.assignments.map((row) => ({
    type: 'scatter', mode: 'lines', name: row.provinceVi, legendgroup: row.endCluster, showlegend: false,
    x: [row.startPc1, row.endPc1], y: [row.startPc2, row.endPc2],
    customdata: [[row.provinceVi, row.region, row.startCluster, row.endCluster, row.pcaDistance], [row.provinceVi, row.region, row.startCluster, row.endCluster, row.pcaDistance]],
    line: { color: clusterColors[row.endCluster] ?? uiColors.muted, width: selectedProvince === row.provinceVi ? 4 : 1.4 },
    opacity: matchesSelection(row) ? 0.72 : 0.08,
    hovertemplate: '<b>%{customdata[0]}</b><br>%{customdata[1]}<br>Hồ sơ %{customdata[2]} → %{customdata[3]}<br>Khoảng cách PCA %{customdata[4]:.2f}<extra></extra>',
  } as unknown as Data))
  const endpointData: Data[] = clusterKeys.flatMap((cluster) => {
    const startRows = model.assignments.filter((row) => row.startCluster === cluster)
    const endRows = model.assignments.filter((row) => row.endCluster === cluster)
    const trace = (rows: typeof model.assignments, endpoint: 'start' | 'end'): Data => ({
      type: 'scatter', mode: endpoint === 'end' ? 'markers+text' : 'markers',
      name: clusterName(cluster), legendgroup: cluster, showlegend: endpoint === 'end',
      x: rows.map((row) => endpoint === 'start' ? row.startPc1 : row.endPc1),
      y: rows.map((row) => endpoint === 'start' ? row.startPc2 : row.endPc2),
      text: endpoint === 'end' ? rows.map((row) => row.provinceVi === selectedProvince ? row.provinceVi : '') : undefined,
      textposition: 'top center',
      customdata: rows.map((row) => [row.provinceVi, row.region, row.startCluster, row.endCluster, row.changed ? 'Đổi hồ sơ' : 'Giữ hồ sơ', row.pcaDistance]),
      marker: {
        color: clusterColors[cluster] ?? uiColors.muted,
        size: rows.map((row) => row.provinceVi === selectedProvince ? 15 : endpoint === 'start' ? 8 : 10),
        symbol: endpoint === 'start' ? 'circle-open' : 'diamond',
        opacity: rows.map((row) => matchesSelection(row) ? 0.9 : 0.12),
        line: { color: uiColors.ink, width: rows.map((row) => row.provinceVi === selectedProvince ? 2.5 : endpoint === 'start' ? 1.4 : 0.7) },
      },
      hovertemplate: `<b>%{customdata[0]}</b><br>%{customdata[1]}<br>Hồ sơ %{customdata[2]} → %{customdata[3]}<br>%{customdata[4]} · khoảng cách PCA %{customdata[5]:.2f}<extra>${endpoint === 'start' ? `Mốc đầu ${f.from}` : `Mốc cuối ${f.to}`}</extra>`,
    } as unknown as Data)
    return [trace(startRows, 'start'), trace(endRows, 'end')]
  })
  const pcaData = [...segmentData, ...endpointData]
  const pcaVariance = model.pcaVariance.reduce((sum, item) => sum + item, 0)
  const pcaView = (height: number) => <CartesianChart title="Dịch chuyển PCA đầu–cuối" summary={`PC1 và PC2 giải thích ${percentFmt.format(pcaVariance * 100)}% phương sai; trục không biểu thị tốt hoặc xấu.`} data={pcaData} height={height} onHover={(event) => { const raw = event.points?.[0]?.customdata; if (Array.isArray(raw) && typeof raw[0] === 'string') setHoveredProvince(raw[0]) }} onUnhover={() => setHoveredProvince(null)} onClick={(event) => { const raw = event.points?.[0]?.customdata; if (Array.isArray(raw)) pinProvince(raw[0]) }} layout={{ xaxis: { title: { text: 'PC1' }, zeroline: true }, yaxis: { title: { text: 'PC2' }, zeroline: true }, legend: { orientation: 'h', y: -0.2, groupclick: 'togglegroup' }, margin: { l: 62, r: 28, t: 24, b: 92 } }}>
    <div className="chart-table-scroll"><table><caption className="sr-only">Tọa độ PCA đầu và cuối theo tỉnh</caption><thead><tr><th>Tỉnh</th><th>Hồ sơ đầu</th><th>Hồ sơ cuối</th><th>Khoảng cách</th></tr></thead><tbody>{model.assignments.map((row) => <tr key={row.provinceVi}><th scope="row"><button type="button" aria-pressed={selectedProvince === row.provinceVi} onClick={() => pinProvince(row.provinceVi)}>{row.provinceVi}</button></th><td>{row.startCluster}</td><td>{row.endCluster}</td><td>{scoreFmt.format(row.pcaDistance ?? 0)}</td></tr>)}</tbody></table></div>
  </CartesianChart>

  const sankeyLabels = [
    ...model.centroids.map((row) => `${row.cluster} · ${f.from} · n=${row.nStart}`),
    ...model.centroids.map((row) => `${row.cluster} · ${f.to} · n=${row.nEnd}`),
  ]
  const flowHighlight = hoveredFlow ?? (selectedFlow ? `${selectedFlow.fromCluster}-${selectedFlow.toCluster}` : null)
  const sankeyData: Data[] = [{
    type: 'sankey', arrangement: 'snap', orientation: 'h',
    node: {
      label: sankeyLabels,
      color: [...clusterKeys, ...clusterKeys].map((cluster) => clusterColors[cluster] ?? uiColors.muted),
      pad: 18, thickness: 18, line: { color: uiColors.surface, width: 1 },
      customdata: [...clusterKeys.map((cluster) => [cluster, 'start']), ...clusterKeys.map((cluster) => [cluster, 'end'])],
      hovertemplate: '<b>Hồ sơ %{customdata[0]}</b><br>%{label}<extra></extra>',
    },
    link: {
      source: model.transitions.map((row) => clusterKeys.indexOf(row.fromCluster)),
      target: model.transitions.map((row) => clusterKeys.length + clusterKeys.indexOf(row.toCluster)),
      value: model.transitions.map((row) => row.n),
      color: model.transitions.map((row) => {
        const key = `${row.fromCluster}-${row.toCluster}`
        const active = !flowHighlight || flowHighlight === key
        if (row.fromCluster === row.toCluster) return alpha(clusterColors[row.fromCluster] ?? '#71837F', active ? 0.58 : 0.1)
        return active ? 'rgba(92, 113, 118, 0.5)' : 'rgba(92, 113, 118, 0.08)'
      }),
      customdata: model.transitions.map((row) => [row.fromCluster, row.toCluster, row.share, row.provinces.slice(0, 6).join(', '), row.provinces.length > 6 ? '…' : '']),
      hovertemplate: '<b>Hồ sơ %{customdata[0]} → %{customdata[1]}</b><br>%{value} tỉnh · %{customdata[2]:.1%}<br>%{customdata[3]}%{customdata[4]}<extra></extra>',
    },
  } as unknown as Data]
  const sankeyView = (height: number) => <SankeyChart title="Luồng chuyển hồ sơ đầu–cuối" summary="Độ rộng đường nối là số tỉnh; đường cùng nhãn thể hiện giữ hồ sơ." data={sankeyData} height={height} onHover={(event) => { const raw = event.points?.[0]?.customdata; if (Array.isArray(raw) && typeof raw[0] === 'string' && typeof raw[1] === 'string') setHoveredFlow(`${raw[0]}-${raw[1]}`) }} onUnhover={() => setHoveredFlow(null)} onClick={(event) => { const raw = event.points?.[0]?.customdata; if (Array.isArray(raw)) selectFlow(raw[0], raw[1]) }} layout={{ margin: { l: 18, r: 18, t: 26, b: 26 } }}>
    <div className="chart-table-scroll"><table><caption className="sr-only">Các luồng chuyển hồ sơ</caption><thead><tr><th>Hồ sơ đầu</th><th>Hồ sơ cuối</th><th>Số tỉnh</th><th>Tỷ lệ</th><th>Chọn</th></tr></thead><tbody>{model.transitions.map((row) => <tr key={`${row.fromCluster}-${row.toCluster}`}><th scope="row">{row.fromCluster}</th><td>{row.toCluster}</td><td>{row.n}</td><td>{percentFmt.format(row.share * 100)}%</td><td><button type="button" aria-pressed={selectedFlow?.fromCluster === row.fromCluster && selectedFlow?.toCluster === row.toCluster} onClick={() => selectFlow(row.fromCluster, row.toCluster)}>Chọn luồng</button></td></tr>)}</tbody></table></div>
  </SankeyChart>

  const activeProfileInsight = d.insights.profiles.find((item) => item.cluster === activeProfile)?.text ?? d.insights.profiles[0]?.text ?? 'Không đủ dữ liệu mô tả hồ sơ.'
  const profileCardHeight = clusterKeys.length > 4 ? 440 : clusterKeys.length > 2 ? 380 : 320
  const defaultSelection = f.scale === 'eight' && f.from === 2018 && f.to === 2024 && f.k === 'auto' && !selectedProvince && !profilePinned && !selectedFlow && !focused

  return <article className="overview analysis-page dynamics-redesign">
    <DashboardPageHeader eyebrow="THAY ĐỔI & PHÂN NHÓM" title="Tỉnh thay đổi và chuyển hồ sơ ra sao?" description="Tách biệt thay đổi tổng điểm, cấu trúc lĩnh vực và luồng chuyển giữa các hồ sơ trong hai mốc." />
    <FilterBar label="Bộ lọc thay đổi và phân nhóm" summary={`Đang xem: ${f.from}–${f.to} · K=${model.selectedK} · ${model.selectionMode === 'auto' ? 'tự chọn' : 'thủ công'}`} onReset={reset} resetDisabled={defaultSelection}>
      <label>Phạm vi<select value={f.scale} onChange={(event) => change({ scale: scaleOf(event.target.value) })}><option value="six">6 lĩnh vực gốc</option><option value="eight">8 lĩnh vực</option></select></label>
      <label>Từ năm<select value={f.from} onChange={(event) => change({ from: Number(event.target.value) })}>{cfg.years.filter((year) => year < f.to).map((year) => <option key={year}>{year}</option>)}</select></label>
      <label>Đến năm<select value={f.to} onChange={(event) => change({ to: Number(event.target.value) })}>{cfg.years.filter((year) => year > f.from).map((year) => <option key={year}>{year}</option>)}</select></label>
      <label>Số hồ sơ K<select value={f.k} onChange={(event) => change({ k: event.target.value === 'auto' ? 'auto' : Number(event.target.value) })}><option value="auto">Tự chọn 2–6</option>{[2, 3, 4, 5, 6].map((item) => <option key={item} value={item}>{item} hồ sơ</option>)}</select></label>
    </FilterBar>
    <KpiGrid label="Chỉ số tóm tắt thay đổi và phân nhóm">
      <KpiCard label="Trung vị thay đổi" value={d.changes.median === null ? '—' : deltaFmt.format(d.changes.median)} detail={`${f.from} → ${f.to}`} tone={(d.changes.median ?? 0) >= 0 ? 'positive' : 'negative'} />
      <KpiCard label="Số hồ sơ được chọn" value={`K = ${model.selectedK}`} detail={model.selectionMode === 'auto' ? 'Theo silhouette trong K=2–6' : 'Người dùng chọn thủ công'} />
      <KpiCard label="Độ tách profile" value={model.silhouette === null ? '—' : scoreFmt.format(model.silhouette)} detail="Silhouette của mô hình đang xem" />
      <KpiCard label="Tỉnh chuyển profile" value={`${model.changedN}/${model.n}`} detail={`${percentFmt.format(model.changedPct * 100)}% mẫu đủ hai mốc`} />
    </KpiGrid>

    <section className="dynamics-chart-grid" aria-label="Bốn biểu đồ thay đổi và phân nhóm">
      <ChartCard className="dynamics-chart-card" eyebrow="01 · THAY ĐỔI TỔNG ĐIỂM" title="Tỉnh nào tăng hoặc giảm tổng điểm nhiều nhất?" action={<button type="button" className="chart-sort" onClick={() => setDirection((current) => current === 'both' ? 'increase' : current === 'increase' ? 'decrease' : 'both')}>Hiện: {direction === 'both' ? 'Cả hai' : direction === 'increase' ? 'Tăng' : 'Giảm'}</button>} insight={<ChartInsight>{d.insights.change}</ChartInsight>} focus={{ ...focus('dynamics-change', selectedProvince ?? `${f.from}–${f.to}`), content: dumbbellView(570) }} footer={<ChartMeta source={d.changes.source} unit={d.changes.unit} n={`${d.changes.n} tỉnh`} caveats={d.changes.caveats} />}>
        {dumbbellView(320)}
      </ChartCard>
      <ChartCard className="dynamics-chart-card" eyebrow="02 · CHỮ KÝ HỒ SƠ" title="Mỗi profile mạnh hoặc yếu tương đối ở lĩnh vực nào?" insight={<ChartInsight>{activeProfileInsight}</ChartInsight>} focus={{ ...focus('dynamics-profiles', clusterName(activeProfile)), content: profileView(570) }} footer={<ChartMeta source={model.source} unit={model.unit} n={`${model.n} tỉnh`} caveats={model.caveats} />}>
        <div className="profile-controls dynamics-profile-controls" role="group" aria-label="Chọn hồ sơ">{clusterKeys.map((key) => <button type="button" key={key} aria-label={clusterName(key)} aria-pressed={activeProfile === key} onClick={() => selectProfile(key)}>{key}</button>)}</div>
        {profileView(profileCardHeight)}
      </ChartCard>
      <ChartCard className="dynamics-chart-card" eyebrow="03 · DỊCH CHUYỂN PCA" title="Các tỉnh dịch chuyển ra sao trong không gian profile?" insight={<ChartInsight>{d.insights.pca}</ChartInsight>} focus={{ ...focus('dynamics-pca', selectedProvince ?? `${percentFmt.format(pcaVariance * 100)}% phương sai`), content: pcaView(570) }} footer={<ChartMeta source={model.source} unit="tọa độ PCA không đơn vị" n={`${model.n} tỉnh`} caveats={[...(model.caveats ?? []), `PC1 + PC2 giải thích ${percentFmt.format(pcaVariance * 100)}% phương sai.`]} />}>
        {pcaView(320)}
      </ChartCard>
      <ChartCard className="dynamics-chart-card" eyebrow="04 · LUỒNG HỒ SƠ" title="Luồng chuyển profile nào phổ biến nhất?" insight={<ChartInsight>{d.insights.transition}</ChartInsight>} focus={{ ...focus('dynamics-transition', selectedFlow ? `${selectedFlow.fromCluster} → ${selectedFlow.toCluster}` : `${percentFmt.format(model.retentionPct * 100)}% giữ hồ sơ`), content: sankeyView(540) }} footer={<ChartMeta source={model.source} unit="số tỉnh" n={`${model.transitions.length} luồng có quan sát`} caveats={model.caveats} />}>
        {sankeyView(320)}
      </ChartCard>
    </section>

    <section className="chart-card dynamics-table"><header className="chart-card-header"><div><p className="eyebrow">BẢNG KIỂM CHỨNG</p><h2>Toàn bộ chênh lệch và profile tỉnh</h2><p>Tra cứu giá trị chính xác, profile đầu/cuối và các selection đang ghim trên biểu đồ.</p></div></header><details ref={tableRef} open={tableOpen} onToggle={(event) => setTableOpen(event.currentTarget.open)}><summary>Xem tất cả tỉnh</summary><div className="table-tools"><label>Tìm tỉnh<input aria-label="Tìm tỉnh" value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Nhập tên tỉnh" /></label><span>{allRows.length}/{d.changes.rows.length} tỉnh</span></div><div className="table-scroll"><table><thead><tr><th aria-sort={sortDirection('provinceVi')}><button aria-label={sortAction('provinceVi', 'Tỉnh')} onClick={() => setSortField('provinceVi')}>Tỉnh {sort === 'provinceVi' && (descending ? '↓' : '↑')}</button></th><th aria-sort={sortDirection('fromScore')}><button aria-label={sortAction('fromScore', `Điểm năm ${f.from}`)} onClick={() => setSortField('fromScore')}>{f.from} {sort === 'fromScore' && (descending ? '↓' : '↑')}</button></th><th aria-sort={sortDirection('toScore')}><button aria-label={sortAction('toScore', `Điểm năm ${f.to}`)} onClick={() => setSortField('toScore')}>{f.to} {sort === 'toScore' && (descending ? '↓' : '↑')}</button></th><th aria-sort={sortDirection('change')}><button aria-label={sortAction('change', 'Thay đổi')} onClick={() => setSortField('change')}>Thay đổi {sort === 'change' && (descending ? '↓' : '↑')}</button></th><th aria-sort={sortDirection('startCluster')}><button aria-label={sortAction('startCluster', 'Profile đầu')} onClick={() => setSortField('startCluster')}>Profile đầu {sort === 'startCluster' && (descending ? '↓' : '↑')}</button></th><th aria-sort={sortDirection('endCluster')}><button aria-label={sortAction('endCluster', 'Profile cuối')} onClick={() => setSortField('endCluster')}>Profile cuối {sort === 'endCluster' && (descending ? '↓' : '↑')}</button></th></tr></thead><tbody>{allRows.map((row) => { const flowSelected = selectedFlow && row.startCluster === selectedFlow.fromCluster && row.endCluster === selectedFlow.toCluster; return <tr key={row.provinceVi} className={row.provinceVi === selectedProvince || flowSelected ? 'selected-row' : ''}><th scope="row"><button type="button" aria-pressed={row.provinceVi === selectedProvince} onClick={() => pinProvince(row.provinceVi)}>{row.provinceVi}</button><small>{row.region}</small></th><td>{scoreFmt.format(row.fromScore ?? 0)}</td><td>{scoreFmt.format(row.toScore ?? 0)}</td><td>{deltaFmt.format(row.change ?? 0)}</td><td>{row.startCluster}</td><td>{row.endCluster}</td></tr> })}</tbody></table></div></details><ChartMeta source={d.changes.source} unit={d.measure.unit} n={`${d.changes.rowCount} tỉnh`} caveats={result.meta.caveats} /></section>
  </article>
}
