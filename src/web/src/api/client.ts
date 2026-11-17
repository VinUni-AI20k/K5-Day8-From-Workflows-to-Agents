import type { Claim, ClaimStatus, ShapeId } from '../types'

export interface ApiRunResult {
  run_id: string
  claim_id: string
  shape: string
  seed: number
  status: ClaimStatus
  proposal_amount: number
  refund_effects: Array<Record<string, unknown>>
  committed_audit_count: number
  model_calls: number
  tool_calls: number
  input_tokens: number
  output_tokens: number
  cost_estimate: number
  trace_path: string
  error_reason: string | null
}

export interface ApiTraceEvent {
  kind: string
  payload: Record<string, unknown>
}

export interface ApiTrace {
  run_id: string | null
  steps?: number
  events: ApiTraceEvent[]
  missing?: boolean
  path?: string
}

export interface LiveRunResponse {
  ok: boolean
  crashed: boolean
  crash_at: string | null
  shape: ShapeId
  seed: number
  claim: Claim
  result: ApiRunResult | null
  trace: ApiTrace
  refund_vnd: number
  store_path: string
  error?: string
  traceback?: string
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(path, {
    headers: { 'Content-Type': 'application/json', ...(init?.headers || {}) },
    ...init,
  })
  const data = (await res.json()) as T & { error?: string }
  if (!res.ok) {
    throw new Error(data.error || `HTTP ${res.status}`)
  }
  return data
}

export function fetchClaims() {
  return request<{ claims: Claim[] }>('/api/claims')
}

export function fetchShapes() {
  return request<{ shapes: ShapeId[]; seeds: number[] }>('/api/shapes')
}

export function runLive(body: {
  shape: ShapeId
  claim_id: string
  seed: number
  crash_at?: string | null
}) {
  return request<LiveRunResponse>('/api/run', {
    method: 'POST',
    body: JSON.stringify(body),
  })
}

export async function checkHealth(): Promise<boolean> {
  try {
    const data = await request<{ ok: boolean }>('/api/health')
    return Boolean(data.ok)
  } catch {
    return false
  }
}
