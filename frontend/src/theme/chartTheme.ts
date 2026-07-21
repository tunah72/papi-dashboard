import type { Layout } from 'plotly.js'

export const uiColors = {
  canvas: '#F5F7F6',
  surface: '#FFFFFF',
  surfaceMuted: '#EEF3F2',
  ink: '#17313A',
  text: '#243B43',
  muted: '#64757B',
  border: '#D8E2E0',
  primary: '#1F6873',
  primaryDark: '#154D56',
  positive: '#2E7D6C',
  negative: '#C96B5C',
  warning: '#B38335',
  missing: '#D8DEDD',
  focus: '#0B6E99',
} as const

export const dimensionColors: Record<string, string> = {
  D1: '#4C6A9C', D2: '#C38A2D', D3: '#578145', D4: '#B45D45',
  D5: '#765A9F', D6: '#2C7F88', D7: '#8C6D3F', D8: '#A85B73',
}

export const regionColors: Record<string, string> = {
  'Trung du và miền núi phía Bắc': '#4C78A8',
  'Đồng bằng sông Hồng': '#72A7A2',
  'Bắc Trung Bộ và Duyên hải miền Trung': '#E39A54',
  'Tây Nguyên': '#9678B6',
  'Đông Nam Bộ': '#5E9460',
  'Đồng bằng sông Cửu Long': '#C87368',
}

const regionShortLabels: Record<string, string> = {
  'Trung du và miền núi phía Bắc': 'Trung du phía Bắc',
  'Đồng bằng sông Hồng': 'ĐBSH',
  'Bắc Trung Bộ và Duyên hải miền Trung': 'Bắc Trung Bộ',
  'Tây Nguyên': 'Tây Nguyên',
  'Đông Nam Bộ': 'Đông Nam Bộ',
  'Đồng bằng sông Cửu Long': 'ĐBSCL',
}

export const sequentialScale: [number, string][] = [
  [0, '#E2F0ED'], [0.5, '#78B7AE'], [1, '#1E6F68'],
]

export const divergingScale: [number, string][] = [
  [0, uiColors.negative], [0.5, '#F0F2F1'], [1, uiColors.positive],
]

export const quadrantColors: Record<string, string> = {
  'Cao–cao': '#2C6E75',
  'Cao–thấp': '#C18A45',
  'Thấp–cao': '#7E6F9F',
  'Thấp–thấp': '#8A9B9A',
}

export const basePlotLayout: Partial<Layout> = {
  autosize: true,
  paper_bgcolor: 'rgba(0,0,0,0)',
  plot_bgcolor: 'rgba(0,0,0,0)',
  margin: { t: 20, r: 28, b: 54, l: 76 },
  font: { family: '"Be Vietnam Pro", system-ui, sans-serif', size: 12, color: uiColors.text },
  hoverlabel: { bgcolor: uiColors.ink, bordercolor: uiColors.ink, font: { color: uiColors.surface, size: 12 } },
  xaxis: { automargin: true, gridcolor: '#E7ECEB', zerolinecolor: '#AAB9B6', tickfont: { color: uiColors.muted } },
  yaxis: { automargin: true, gridcolor: '#E7ECEB', zerolinecolor: '#AAB9B6', tickfont: { color: uiColors.muted } },
  legend: { orientation: 'h', yanchor: 'bottom', y: 1.02, xanchor: 'left', x: 0 },
}

export function colorForDimension(code: string) { return dimensionColors[code] ?? uiColors.primary }
export function colorForRegion(region: string) { return regionColors[region] ?? uiColors.muted }
export function shortRegionLabel(region: string) { return regionShortLabels[region] ?? region }
