export type ShapeId = 'workflow' | 'single' | 'orchestrator' | 'swarm'

export type NodeRunState = 'idle' | 'running' | 'success' | 'skipped' | 'error' | 'bottleneck'

export type ClaimStatus =
  | 'resolved'
  | 'needs_info'
  | 'escalated'
  | 'denied'
  | 'failed'

export interface ClaimExpected {
  status: ClaimStatus
  proposal_amount: number
  refund_vnd: number
  refund_count: number
  audit_refund_committed: number
  policy_denied: boolean
  approval_ok: boolean
}

export interface Claim {
  claim_id: string
  principal_id: string
  order_id: string | null
  ticket: string
  approval_id: string | null
  matrix_id: string
  expected: ClaimExpected
}

export interface StepEvent {
  id: string
  nodeId: string
  at: number
  kind: 'start' | 'info' | 'warn' | 'error' | 'done'
  message: string
  detail?: string
  /** Trạng thái bước trên canvas khi ghi / khi commit. */
  state?: NodeRunState
  stepIndex?: number
  label?: string
}

export interface RunOutcome {
  status: ClaimStatus
  proposalAmount: number
  refundVnd: number
  policyDenied: boolean
  bottleneckNodeId: string | null
  summary: string
  matchesExpected: boolean
}

export interface ShapeMeta {
  id: ShapeId
  label: string
  short: string
  description: string
}

export type RunnerMode = 'idle' | 'running' | 'paused' | 'done'
