import type { components } from './schema'

export type MetadataResponse = components['schemas']['MetadataResponse']
export type GeojsonResponse = components['schemas']['GeojsonResponse']
export type OverviewResponse = components['schemas']['OverviewResponse']
export type TrendsResponse = components['schemas']['TrendsResponse']
export type ProvincesResponse = components['schemas']['ProvincesResponse']
export type DimensionsResponse = components['schemas']['DimensionsResponse']
export type DynamicsResponse = components['schemas']['DynamicsResponse']
export type AssistantMessageRequest = components['schemas']['AssistantMessageRequest']
export type AssistantMessageResponse = components['schemas']['AssistantAnswerResponse'] | components['schemas']['AssistantClarificationResponse'] | components['schemas']['AssistantProposalResponse']
export type AssistantExecutionResponse = components['schemas']['AssistantExecutionResponse']
export type Scale = 'six' | 'eight'

const baseUrl = import.meta.env.VITE_API_URL ?? 'http://127.0.0.1:8000'

export class ApiError extends Error {
  constructor(message: string, readonly status: number) { super(message) }
}

async function getJson<T>(path: string): Promise<T> {
  let response: Response
  try {
    response = await fetch(`${baseUrl}${path}`)
  } catch {
    throw new ApiError('Không kết nối được FastAPI local. Hãy khởi động server rồi thử lại.', 0)
  }
  if (!response.ok) {
    const payload: unknown = await response.json().catch(() => null)
    const detail = typeof payload === 'object' && payload !== null && 'detail' in payload && typeof payload.detail === 'string'
      ? payload.detail : 'Không thể tải dữ liệu. Hãy kiểm tra FastAPI local rồi thử lại.'
    throw new ApiError(`Không thể tải dữ liệu (${response.status}). ${detail}`, response.status)
  }
  try {
    return await response.json() as T
  } catch {
    throw new ApiError('FastAPI local trả về dữ liệu không hợp lệ. Hãy khởi động lại server rồi thử lại.', response.status)
  }
}

async function postJson<T>(path: string, body: unknown): Promise<T> {
  let response: Response
  try {
    response = await fetch(`${baseUrl}${path}`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) })
  } catch {
    throw new ApiError('Không kết nối được FastAPI local. Hãy khởi động server rồi thử lại.', 0)
  }
  if (!response.ok) {
    const payload: unknown = await response.json().catch(() => null)
    const detail = typeof payload === 'object' && payload !== null && 'detail' in payload && typeof payload.detail === 'string'
      ? payload.detail : 'Yêu cầu Trợ lý AI không thành công. Hãy thử lại.'
    throw new ApiError(`Không thể xử lý yêu cầu (${response.status}). ${detail}`, response.status)
  }
  try { return await response.json() as T } catch {
    throw new ApiError('FastAPI local trả về dữ liệu không hợp lệ. Hãy khởi động lại server rồi thử lại.', response.status)
  }
}

export const api = {
  metadata: () => getJson<MetadataResponse>('/api/v1/metadata'),
  geojson: () => getJson<GeojsonResponse>('/api/v1/geojson'),
  overview: (scale: Scale, year: number) => getJson<OverviewResponse>(`/api/v1/overview?scale=${scale}&year=${year}`),
  trends: (scale: Scale, from: number, to: number, region?: string, province?: string) => getJson<TrendsResponse>(`/api/v1/trends?scale=${scale}&from=${from}&to=${to}${region ? `&region=${encodeURIComponent(region)}` : ''}${province ? `&province=${encodeURIComponent(province)}` : ''}`),
  provinces: (scale: Scale, year: number, region?: string, province?: string) => getJson<ProvincesResponse>(`/api/v1/provinces?scale=${scale}&year=${year}${region ? `&region=${encodeURIComponent(region)}` : ''}${province ? `&province=${encodeURIComponent(province)}` : ''}`),
  dimensions: (scale: Scale, year: number, x: string, y: string) => getJson<DimensionsResponse>(`/api/v1/dimensions?scale=${scale}&year=${year}&x=${encodeURIComponent(x)}&y=${encodeURIComponent(y)}`),
  dynamics: (scale: Scale, from: number, to: number, k?: number) => getJson<DynamicsResponse>(`/api/v1/dynamics?scale=${scale}&from=${from}&to=${to}${k ? `&k=${k}` : ''}`),
  assistantMessage: (payload: AssistantMessageRequest) => postJson<AssistantMessageResponse>('/api/v1/assistant/messages', payload),
  executeProposal: (sessionId: string, proposalId: string) => postJson<AssistantExecutionResponse>('/api/v1/assistant/executions', { sessionId, proposalId, approved: true }),
}
