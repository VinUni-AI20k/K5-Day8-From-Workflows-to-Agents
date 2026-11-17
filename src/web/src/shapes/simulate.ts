import type { Claim, ClaimStatus, RunOutcome, ShapeId, StepEvent } from '../types'

export interface SimStep {
  nodeId: string
  state: 'success' | 'skipped' | 'error' | 'bottleneck'
  event: Omit<StepEvent, 'id' | 'at'>
  /** Edge just traversed into this node (if any). */
  edgeId?: string
  delayMs?: number
}

function money(n: number) {
  return `${n.toLocaleString('vi-VN')} VND`
}

function e(source: string, target: string) {
  return `${source}->${target}`
}

function earlyPath(claim: Claim): 'needs_info' | 'escalated' | 'denied_zero' | 'host' | 'denied_host' {
  if (claim.expected.status === 'needs_info' || !claim.order_id) return 'needs_info'
  if (claim.expected.status === 'escalated') return 'escalated'
  if (claim.expected.proposal_amount === 0 && claim.expected.status === 'denied') {
    return 'denied_zero'
  }
  if (
    claim.expected.policy_denied ||
    (claim.expected.status === 'denied' && claim.expected.refund_vnd === 0 && claim.expected.proposal_amount > 0)
  ) {
    return 'denied_host'
  }
  return 'host'
}

function makeOutcome(
  shape: ShapeId,
  claim: Claim,
  actual: {
    status: ClaimStatus
    proposalAmount: number
    refundVnd: number
    policyDenied: boolean
    bottleneckNodeId: string | null
    summary: string
  },
): RunOutcome {
  const exp = claim.expected
  const matchesExpected =
    actual.status === exp.status &&
    actual.proposalAmount === exp.proposal_amount &&
    actual.refundVnd === exp.refund_vnd
  return { ...actual, matchesExpected, summary: `[${shape}] ${actual.summary}` }
}

function skip(ids: string[]): SimStep[] {
  return ids.map((nodeId) => ({
    nodeId,
    state: 'skipped' as const,
    event: {
      nodeId,
      kind: 'info' as const,
      message: 'Bỏ qua (không đi nhánh này)',
    },
    delayMs: 0,
  }))
}

function workflowSteps(claim: Claim): { steps: SimStep[]; outcome: RunOutcome } {
  const path = earlyPath(claim)
  const shape: ShapeId = 'workflow'
  const steps: SimStep[] = [
    {
      nodeId: 'wf-load',
      state: 'success',
      event: {
        nodeId: 'wf-load',
        kind: 'start',
        message: `Đọc claim ${claim.claim_id}`,
        detail: claim.ticket,
      },
    },
  ]

  if (path === 'needs_info') {
    steps.push(
      {
        nodeId: 'wf-orderid',
        state: 'error',
        edgeId: e('wf-load', 'wf-orderid'),
        event: {
          nodeId: 'wf-orderid',
          kind: 'warn',
          message: 'Thiếu order_id',
          detail: 'Không lấy mã đơn từ chữ trong ticket',
        },
      },
      {
        nodeId: 'wf-needs',
        state: 'success',
        edgeId: e('wf-orderid', 'wf-needs'),
        event: { nodeId: 'wf-needs', kind: 'done', message: 'status = needs_info' },
      },
      ...skip(['wf-lookup', 'wf-visible', 'wf-escalate', 'wf-quote', 'wf-amount', 'wf-denied', 'wf-host', 'wf-result']),
    )
    return {
      steps,
      outcome: makeOutcome(shape, claim, {
        status: 'needs_info',
        proposalAmount: 0,
        refundVnd: 0,
        policyDenied: false,
        bottleneckNodeId: 'wf-orderid',
        summary: 'Thiếu order_id — dừng sớm, không ghi ledger.',
      }),
    }
  }

  steps.push({
    nodeId: 'wf-orderid',
    state: 'success',
    edgeId: e('wf-load', 'wf-orderid'),
    event: { nodeId: 'wf-orderid', kind: 'info', message: `order_id = ${claim.order_id}` },
  })
  steps.push({
    nodeId: 'wf-lookup',
    state: 'success',
    edgeId: e('wf-orderid', 'wf-lookup'),
    event: { nodeId: 'wf-lookup', kind: 'info', message: 'lookup_order (allowlist fields)' },
  })

  if (path === 'escalated') {
    steps.push(
      {
        nodeId: 'wf-visible',
        state: 'error',
        edgeId: e('wf-lookup', 'wf-visible'),
        event: {
          nodeId: 'wf-visible',
          kind: 'error',
          message: 'Order không visible',
          detail: `principal ${claim.principal_id} không sở hữu đơn`,
        },
      },
      {
        nodeId: 'wf-escalate',
        state: 'success',
        edgeId: e('wf-visible', 'wf-escalate'),
        event: { nodeId: 'wf-escalate', kind: 'done', message: 'status = escalated' },
      },
      ...skip(['wf-needs', 'wf-quote', 'wf-amount', 'wf-denied', 'wf-host', 'wf-result']),
    )
    return {
      steps,
      outcome: makeOutcome(shape, claim, {
        status: 'escalated',
        proposalAmount: 0,
        refundVnd: 0,
        policyDenied: false,
        bottleneckNodeId: 'wf-visible',
        summary: 'Order không visible — escalate, không lộ PII.',
      }),
    }
  }

  steps.push({
    nodeId: 'wf-visible',
    state: 'success',
    edgeId: e('wf-lookup', 'wf-visible'),
    event: { nodeId: 'wf-visible', kind: 'info', message: 'Order visible' },
  })
  steps.push({
    nodeId: 'wf-quote',
    state: 'success',
    edgeId: e('wf-visible', 'wf-quote'),
    event: {
      nodeId: 'wf-quote',
      kind: 'info',
      message: 'compute_compensation từ order row',
      detail: 'Bỏ qua số ngày ghi trong ticket',
    },
  })

  if (path === 'denied_zero') {
    steps.push(
      {
        nodeId: 'wf-amount',
        state: 'error',
        edgeId: e('wf-quote', 'wf-amount'),
        event: {
          nodeId: 'wf-amount',
          kind: 'warn',
          message: 'Quote = 0',
          detail: 'Trễ < 3 ngày / policy cũ / không đủ điều kiện',
        },
      },
      {
        nodeId: 'wf-denied',
        state: 'success',
        edgeId: e('wf-amount', 'wf-denied'),
        event: { nodeId: 'wf-denied', kind: 'done', message: 'status = denied' },
      },
      ...skip(['wf-needs', 'wf-escalate', 'wf-host', 'wf-result']),
    )
    return {
      steps,
      outcome: makeOutcome(shape, claim, {
        status: 'denied',
        proposalAmount: 0,
        refundVnd: 0,
        policyDenied: false,
        bottleneckNodeId: 'wf-amount',
        summary: 'Denied — quote 0, không ghi ledger.',
      }),
    }
  }

  steps.push({
    nodeId: 'wf-amount',
    state: 'success',
    edgeId: e('wf-quote', 'wf-amount'),
    event: {
      nodeId: 'wf-amount',
      kind: 'info',
      message: `Quote ${money(claim.expected.proposal_amount)}`,
    },
  })

  if (path === 'denied_host') {
    steps.push(
      {
        nodeId: 'wf-host',
        state: 'error',
        edgeId: e('wf-amount', 'wf-host'),
        event: {
          nodeId: 'wf-host',
          kind: 'error',
          message: 'Host từ chối ghi ledger',
          detail: claim.expected.policy_denied
            ? 'policy_denied (approval / order_already_refunded)'
            : 'approval / cap check fail',
        },
      },
      {
        nodeId: 'wf-result',
        state: 'success',
        edgeId: e('wf-host', 'wf-result'),
        event: {
          nodeId: 'wf-result',
          kind: 'done',
          message: `denied · proposal ${money(claim.expected.proposal_amount)}`,
        },
      },
      ...skip(['wf-needs', 'wf-escalate', 'wf-denied']),
    )
    return {
      steps,
      outcome: makeOutcome(shape, claim, {
        status: 'denied',
        proposalAmount: claim.expected.proposal_amount,
        refundVnd: 0,
        policyDenied: claim.expected.policy_denied,
        bottleneckNodeId: 'wf-host',
        summary: `Host từ chối. Quote ${money(claim.expected.proposal_amount)}, refund 0.`,
      }),
    }
  }

  steps.push(
    {
      nodeId: 'wf-host',
      state: 'success',
      edgeId: e('wf-amount', 'wf-host'),
      event: {
        nodeId: 'wf-host',
        kind: 'info',
        message: `issue_refund → ${money(claim.expected.refund_vnd)}`,
        detail: 'Một dòng ledger · audit refund_committed',
      },
    },
    {
      nodeId: 'wf-result',
      state: 'success',
      edgeId: e('wf-host', 'wf-result'),
      event: {
        nodeId: 'wf-result',
        kind: 'done',
        message: `resolved · ${money(claim.expected.refund_vnd)}`,
      },
    },
    ...skip(['wf-needs', 'wf-escalate', 'wf-denied']),
  )
  return {
    steps,
    outcome: makeOutcome(shape, claim, {
      status: 'resolved',
      proposalAmount: claim.expected.proposal_amount,
      refundVnd: claim.expected.refund_vnd,
      policyDenied: false,
      bottleneckNodeId: null,
      summary: `Hoàn ${money(claim.expected.refund_vnd)} (quote ${money(claim.expected.proposal_amount)}).`,
    }),
  }
}

function singleSteps(claim: Claim): { steps: SimStep[]; outcome: RunOutcome } {
  const path = earlyPath(claim)
  const shape: ShapeId = 'single'
  const steps: SimStep[] = [
    {
      nodeId: 'sg-load',
      state: 'success',
      event: {
        nodeId: 'sg-load',
        kind: 'start',
        message: `Single agent nhận ${claim.claim_id}`,
      },
    },
    {
      nodeId: 'sg-react',
      state: 'success',
      edgeId: e('sg-load', 'sg-react'),
      event: { nodeId: 'sg-react', kind: 'info', message: 'Bắt đầu ReAct (max 8)' },
    },
    {
      nodeId: 'sg-think',
      state: 'success',
      edgeId: e('sg-react', 'sg-think'),
      event: {
        nodeId: 'sg-think',
        kind: 'info',
        message: 'decide() chọn tool đọc',
        detail: 'Không được gọi issue_refund từ model',
      },
      delayMs: 700,
    },
    {
      nodeId: 'sg-tools',
      state: 'success',
      edgeId: e('sg-think', 'sg-tools'),
      event: {
        nodeId: 'sg-tools',
        kind: 'info',
        message:
          path === 'needs_info'
            ? 'Không có order_id để lookup'
            : 'lookup_order / policy / refund_history',
      },
      delayMs: 650,
    },
    {
      nodeId: 'sg-cap',
      state: 'success',
      edgeId: e('sg-tools', 'sg-cap'),
      event: {
        nodeId: 'sg-cap',
        kind: 'info',
        message: 'Dừng vòng lặp trong ngân sách 8 bước',
      },
    },
  ]

  if (path === 'needs_info' || path === 'escalated' || path === 'denied_zero') {
    const status = path === 'needs_info' ? 'needs_info' : path === 'escalated' ? 'escalated' : 'denied'
    const bottleneck = path === 'denied_zero' ? 'sg-quote' : 'sg-tools'
    steps.push(
      {
        nodeId: 'sg-quote',
        state: path === 'denied_zero' ? 'error' : 'skipped',
        edgeId: e('sg-cap', 'sg-quote'),
        event: {
          nodeId: 'sg-quote',
          kind: path === 'denied_zero' ? 'warn' : 'info',
          message:
            path === 'needs_info'
              ? 'Early: needs_info'
              : path === 'escalated'
                ? 'Early: escalated'
                : 'Quote = 0 → denied',
        },
      },
      {
        nodeId: 'sg-host',
        state: 'skipped',
        event: { nodeId: 'sg-host', kind: 'info', message: 'Không gọi host / không ghi ledger' },
      },
      {
        nodeId: 'sg-result',
        state: 'success',
        event: { nodeId: 'sg-result', kind: 'done', message: `status = ${status}` },
      },
    )
    return {
      steps,
      outcome: makeOutcome(shape, claim, {
        status,
        proposalAmount: 0,
        refundVnd: 0,
        policyDenied: false,
        bottleneckNodeId: bottleneck,
        summary:
          status === 'needs_info'
            ? 'Thiếu order_id — dừng sớm.'
            : status === 'escalated'
              ? 'Escalate — order không visible.'
              : 'Denied — quote 0.',
      }),
    }
  }

  steps.push({
    nodeId: 'sg-quote',
    state: 'success',
    edgeId: e('sg-cap', 'sg-quote'),
    event: {
      nodeId: 'sg-quote',
      kind: 'info',
      message: `Code quote ${money(claim.expected.proposal_amount)}`,
    },
  })

  if (path === 'denied_host') {
    steps.push(
      {
        nodeId: 'sg-host',
        state: 'error',
        edgeId: e('sg-quote', 'sg-host'),
        event: {
          nodeId: 'sg-host',
          kind: 'error',
          message: 'Host chặn refund',
          detail: 'policy_denied / approval fail',
        },
      },
      {
        nodeId: 'sg-result',
        state: 'success',
        edgeId: e('sg-host', 'sg-result'),
        event: { nodeId: 'sg-result', kind: 'done', message: 'denied (host)' },
      },
    )
    return {
      steps,
      outcome: makeOutcome(shape, claim, {
        status: 'denied',
        proposalAmount: claim.expected.proposal_amount,
        refundVnd: 0,
        policyDenied: true,
        bottleneckNodeId: 'sg-host',
        summary: `Host chặn. Quote ${money(claim.expected.proposal_amount)}.`,
      }),
    }
  }

  steps.push(
    {
      nodeId: 'sg-host',
      state: 'success',
      edgeId: e('sg-quote', 'sg-host'),
      event: {
        nodeId: 'sg-host',
        kind: 'info',
        message: `Ghi ledger ${money(claim.expected.refund_vnd)}`,
      },
    },
    {
      nodeId: 'sg-result',
      state: 'success',
      edgeId: e('sg-host', 'sg-result'),
      event: { nodeId: 'sg-result', kind: 'done', message: 'resolved' },
    },
  )
  return {
    steps,
    outcome: makeOutcome(shape, claim, {
      status: 'resolved',
      proposalAmount: claim.expected.proposal_amount,
      refundVnd: claim.expected.refund_vnd,
      policyDenied: false,
      bottleneckNodeId: null,
      summary: `Hoàn ${money(claim.expected.refund_vnd)}.`,
    }),
  }
}

function orchestratorSteps(claim: Claim): { steps: SimStep[]; outcome: RunOutcome } {
  const path = earlyPath(claim)
  const shape: ShapeId = 'orchestrator'
  const steps: SimStep[] = [
    {
      nodeId: 'or-load',
      state: 'success',
      event: {
        nodeId: 'or-load',
        kind: 'start',
        message: `Orchestrator load ${claim.claim_id}`,
      },
    },
  ]

  if (path === 'needs_info') {
    steps.push(
      {
        nodeId: 'or-check',
        state: 'error',
        edgeId: e('or-load', 'or-check'),
        event: { nodeId: 'or-check', kind: 'warn', message: 'Thiếu order_id' },
      },
      {
        nodeId: 'or-needs',
        state: 'success',
        edgeId: e('or-check', 'or-needs'),
        event: { nodeId: 'or-needs', kind: 'done', message: 'needs_info' },
      },
      ...skip(['or-handoff', 'or-invest', 'or-visible', 'or-esc', 'or-quote', 'or-host', 'or-result']),
    )
    return {
      steps,
      outcome: makeOutcome(shape, claim, {
        status: 'needs_info',
        proposalAmount: 0,
        refundVnd: 0,
        policyDenied: false,
        bottleneckNodeId: 'or-check',
        summary: 'Thiếu order_id — early exit.',
      }),
    }
  }

  steps.push(
    {
      nodeId: 'or-check',
      state: 'success',
      edgeId: e('or-load', 'or-check'),
      event: { nodeId: 'or-check', kind: 'info', message: `order_id ${claim.order_id}` },
    },
    {
      nodeId: 'or-handoff',
      state: 'success',
      edgeId: e('or-check', 'or-handoff'),
      event: {
        nodeId: 'or-handoff',
        kind: 'info',
        message: 'make_handoff allowlist',
        detail: 'Không đưa parent_secret / headers / full claim',
      },
    },
    {
      nodeId: 'or-invest',
      state: 'success',
      edgeId: e('or-handoff', 'or-invest'),
      event: {
        nodeId: 'or-invest',
        kind: 'info',
        message: 'Investigator chạy tool đọc',
        detail: 'lookup_order · lookup_policy · compute_compensation',
      },
      delayMs: 750,
    },
  )

  if (path === 'escalated') {
    steps.push(
      {
        nodeId: 'or-visible',
        state: 'error',
        edgeId: e('or-invest', 'or-visible'),
        event: { nodeId: 'or-visible', kind: 'error', message: 'Order không visible' },
      },
      {
        nodeId: 'or-esc',
        state: 'success',
        edgeId: e('or-visible', 'or-esc'),
        event: { nodeId: 'or-esc', kind: 'done', message: 'escalated' },
      },
      ...skip(['or-needs', 'or-quote', 'or-host', 'or-result']),
    )
    return {
      steps,
      outcome: makeOutcome(shape, claim, {
        status: 'escalated',
        proposalAmount: 0,
        refundVnd: 0,
        policyDenied: false,
        bottleneckNodeId: 'or-visible',
        summary: 'Escalate — ownership fail.',
      }),
    }
  }

  steps.push({
    nodeId: 'or-visible',
    state: 'success',
    edgeId: e('or-invest', 'or-visible'),
    event: { nodeId: 'or-visible', kind: 'info', message: 'Order visible' },
  })

  if (path === 'denied_zero') {
    steps.push(
      {
        nodeId: 'or-quote',
        state: 'error',
        edgeId: e('or-visible', 'or-quote'),
        event: { nodeId: 'or-quote', kind: 'warn', message: 'Quote = 0 → denied' },
      },
      {
        nodeId: 'or-host',
        state: 'skipped',
        event: { nodeId: 'or-host', kind: 'info', message: 'Bỏ qua host' },
      },
      {
        nodeId: 'or-result',
        state: 'success',
        event: { nodeId: 'or-result', kind: 'done', message: 'denied' },
      },
      ...skip(['or-needs', 'or-esc']),
    )
    return {
      steps,
      outcome: makeOutcome(shape, claim, {
        status: 'denied',
        proposalAmount: 0,
        refundVnd: 0,
        policyDenied: false,
        bottleneckNodeId: 'or-quote',
        summary: 'Denied — quote 0.',
      }),
    }
  }

  steps.push({
    nodeId: 'or-quote',
    state: 'success',
    edgeId: e('or-visible', 'or-quote'),
    event: {
      nodeId: 'or-quote',
      kind: 'info',
      message: `Quote ${money(claim.expected.proposal_amount)}`,
    },
  })

  if (path === 'denied_host') {
    steps.push(
      {
        nodeId: 'or-host',
        state: 'error',
        edgeId: e('or-quote', 'or-host'),
        event: { nodeId: 'or-host', kind: 'error', message: 'Host policy_denied' },
      },
      {
        nodeId: 'or-result',
        state: 'success',
        edgeId: e('or-host', 'or-result'),
        event: { nodeId: 'or-result', kind: 'done', message: 'denied' },
      },
      ...skip(['or-needs', 'or-esc']),
    )
    return {
      steps,
      outcome: makeOutcome(shape, claim, {
        status: 'denied',
        proposalAmount: claim.expected.proposal_amount,
        refundVnd: 0,
        policyDenied: true,
        bottleneckNodeId: 'or-host',
        summary: `Host policy_denied. Quote ${money(claim.expected.proposal_amount)}.`,
      }),
    }
  }

  steps.push(
    {
      nodeId: 'or-host',
      state: 'success',
      edgeId: e('or-quote', 'or-host'),
      event: {
        nodeId: 'or-host',
        kind: 'info',
        message: `Refund ${money(claim.expected.refund_vnd)}`,
      },
    },
    {
      nodeId: 'or-result',
      state: 'success',
      edgeId: e('or-host', 'or-result'),
      event: { nodeId: 'or-result', kind: 'done', message: 'resolved' },
    },
    ...skip(['or-needs', 'or-esc']),
  )
  return {
    steps,
    outcome: makeOutcome(shape, claim, {
      status: 'resolved',
      proposalAmount: claim.expected.proposal_amount,
      refundVnd: claim.expected.refund_vnd,
      policyDenied: false,
      bottleneckNodeId: null,
      summary: `Hoàn ${money(claim.expected.refund_vnd)}.`,
    }),
  }
}

function swarmSteps(claim: Claim, seed: number): { steps: SimStep[]; outcome: RunOutcome } {
  /** Swarm weakness: seed % 5 === 0 (e.g. 55) trusts ticket delay on C-002. */
  const ticketLie = claim.claim_id === 'C-002' && seed % 5 === 0
  const path = earlyPath(claim)
  const shape: ShapeId = 'swarm'

  const steps: SimStep[] = [
    {
      nodeId: 'sw-load',
      state: 'success',
      event: {
        nodeId: 'sw-load',
        kind: 'start',
        message: `Swarm nhận ${claim.claim_id}`,
        detail: `seed ${seed}`,
      },
    },
    {
      nodeId: 'sw-peer',
      state: 'success',
      edgeId: e('sw-load', 'sw-peer'),
      event: {
        nodeId: 'sw-peer',
        kind: 'info',
        message: 'Peer agents trao đổi',
        detail: 'Thêm model calls → cost/variance cao hơn',
      },
      delayMs: 700,
    },
    {
      nodeId: 'sw-parse',
      state: ticketLie ? 'bottleneck' : 'success',
      edgeId: e('sw-peer', 'sw-parse'),
      event: {
        nodeId: 'sw-parse',
        kind: ticketLie ? 'warn' : 'info',
        message: ticketLie
          ? 'Parse delay từ ticket = 5 (lệch order)'
          : seed % 5 === 0
            ? 'Parse ticket (weakness cửa sổ mở, claim khác)'
            : 'Parse ticket (seed không kích hoạt weakness)',
        detail: ticketLie ? 'REFERENCE_WEAKNESS: seed%5==0 tin ticket' : undefined,
      },
    },
  ]

  if (path === 'needs_info') {
    steps.push(
      {
        nodeId: 'sw-handoff',
        state: 'skipped',
        event: { nodeId: 'sw-handoff', kind: 'info', message: 'Early exit trước handoff' },
      },
      ...skip(['sw-trust', 'sw-wrong', 'sw-quote', 'sw-host']),
      {
        nodeId: 'sw-result',
        state: 'success',
        event: { nodeId: 'sw-result', kind: 'done', message: 'needs_info' },
      },
    )
    return {
      steps,
      outcome: makeOutcome(shape, claim, {
        status: 'needs_info',
        proposalAmount: 0,
        refundVnd: 0,
        policyDenied: false,
        bottleneckNodeId: 'sw-load',
        summary: 'needs_info.',
      }),
    }
  }

  steps.push({
    nodeId: 'sw-handoff',
    state: 'success',
    edgeId: e('sw-parse', 'sw-handoff'),
    event: {
      nodeId: 'sw-handoff',
      kind: 'info',
      message: 'Investigators đọc order/policy',
    },
  })

  if (ticketLie) {
    steps.push(
      {
        nodeId: 'sw-trust',
        state: 'bottleneck',
        edgeId: e('sw-handoff', 'sw-trust'),
        event: {
          nodeId: 'sw-trust',
          kind: 'warn',
          message: 'Swarm tin số ngày trong ticket',
          detail: 'Khúc mắc: ticket ≠ order.delay_days',
        },
      },
      {
        nodeId: 'sw-wrong',
        state: 'error',
        edgeId: e('sw-trust', 'sw-wrong'),
        event: {
          nodeId: 'sw-wrong',
          kind: 'error',
          message: 'Quote sai 20.000 thay vì denied',
          detail: 'Đúng phải denied vì delay_days order = 2',
        },
      },
      {
        nodeId: 'sw-quote',
        state: 'skipped',
        event: { nodeId: 'sw-quote', kind: 'info', message: 'Nhánh quote đúng bị bỏ qua' },
      },
      {
        nodeId: 'sw-host',
        state: 'success',
        edgeId: e('sw-wrong', 'sw-host'),
        event: {
          nodeId: 'sw-host',
          kind: 'info',
          message: 'Host ghi theo proposal lệch',
          detail: 'Host không sửa logic tin ticket của swarm',
        },
      },
      {
        nodeId: 'sw-result',
        state: 'error',
        edgeId: e('sw-host', 'sw-result'),
        event: {
          nodeId: 'sw-result',
          kind: 'error',
          message: 'resolved 20.000 — lệch expected denied/0',
          detail: 'Variance cố ý để đo đối chứng',
        },
      },
    )
    return {
      steps,
      outcome: makeOutcome(shape, claim, {
        status: 'resolved',
        proposalAmount: 20000,
        refundVnd: 20000,
        policyDenied: false,
        bottleneckNodeId: 'sw-trust',
        summary: 'WEAKNESS: tin ticket → refund 20.000 (expected denied / 0).',
      }),
    }
  }

  steps.push({
    nodeId: 'sw-trust',
    state: 'success',
    edgeId: e('sw-handoff', 'sw-trust'),
    event: {
      nodeId: 'sw-trust',
      kind: 'info',
      message: 'Không tin ticket — dùng order row',
    },
  })

  if (path === 'escalated') {
    steps.push(
      {
        nodeId: 'sw-quote',
        state: 'skipped',
        edgeId: e('sw-trust', 'sw-quote'),
        event: { nodeId: 'sw-quote', kind: 'info', message: 'Escalate trước quote' },
      },
      ...skip(['sw-wrong', 'sw-host']),
      {
        nodeId: 'sw-result',
        state: 'success',
        event: { nodeId: 'sw-result', kind: 'done', message: 'escalated' },
      },
    )
    return {
      steps,
      outcome: makeOutcome(shape, claim, {
        status: 'escalated',
        proposalAmount: 0,
        refundVnd: 0,
        policyDenied: false,
        bottleneckNodeId: 'sw-handoff',
        summary: 'escalated.',
      }),
    }
  }

  if (path === 'denied_zero') {
    steps.push(
      {
        nodeId: 'sw-quote',
        state: 'error',
        edgeId: e('sw-trust', 'sw-quote'),
        event: { nodeId: 'sw-quote', kind: 'warn', message: 'Quote 0' },
      },
      ...skip(['sw-wrong', 'sw-host']),
      {
        nodeId: 'sw-result',
        state: 'success',
        event: { nodeId: 'sw-result', kind: 'done', message: 'denied' },
      },
    )
    return {
      steps,
      outcome: makeOutcome(shape, claim, {
        status: 'denied',
        proposalAmount: 0,
        refundVnd: 0,
        policyDenied: false,
        bottleneckNodeId: 'sw-quote',
        summary: 'Denied — quote 0 (đúng với C-002 khi seed không kích hoạt weakness).',
      }),
    }
  }

  steps.push({
    nodeId: 'sw-quote',
    state: 'success',
    edgeId: e('sw-trust', 'sw-quote'),
    event: {
      nodeId: 'sw-quote',
      kind: 'info',
      message: `Quote ${money(claim.expected.proposal_amount)}`,
    },
  })
  steps.push({
    nodeId: 'sw-wrong',
    state: 'skipped',
    event: { nodeId: 'sw-wrong', kind: 'info', message: 'Nhánh yếu không kích hoạt' },
  })

  if (path === 'denied_host') {
    steps.push(
      {
        nodeId: 'sw-host',
        state: 'error',
        edgeId: e('sw-quote', 'sw-host'),
        event: { nodeId: 'sw-host', kind: 'error', message: 'Host policy_denied' },
      },
      {
        nodeId: 'sw-result',
        state: 'success',
        edgeId: e('sw-host', 'sw-result'),
        event: { nodeId: 'sw-result', kind: 'done', message: 'denied' },
      },
    )
    return {
      steps,
      outcome: makeOutcome(shape, claim, {
        status: 'denied',
        proposalAmount: claim.expected.proposal_amount,
        refundVnd: 0,
        policyDenied: true,
        bottleneckNodeId: 'sw-host',
        summary: 'Host policy_denied.',
      }),
    }
  }

  steps.push(
    {
      nodeId: 'sw-host',
      state: 'success',
      edgeId: e('sw-quote', 'sw-host'),
      event: {
        nodeId: 'sw-host',
        kind: 'info',
        message: `Refund ${money(claim.expected.refund_vnd)}`,
      },
    },
    {
      nodeId: 'sw-result',
      state: 'success',
      edgeId: e('sw-host', 'sw-result'),
      event: { nodeId: 'sw-result', kind: 'done', message: 'resolved' },
    },
  )
  return {
    steps,
    outcome: makeOutcome(shape, claim, {
      status: 'resolved',
      proposalAmount: claim.expected.proposal_amount,
      refundVnd: claim.expected.refund_vnd,
      policyDenied: false,
      bottleneckNodeId: null,
      summary: `Hoàn ${money(claim.expected.refund_vnd)}.`,
    }),
  }
}

export function buildSimulation(shape: ShapeId, claim: Claim, seed: number) {
  switch (shape) {
    case 'workflow':
      return workflowSteps(claim)
    case 'single':
      return singleSteps(claim)
    case 'orchestrator':
      return orchestratorSteps(claim)
    case 'swarm':
      return swarmSteps(claim, seed)
  }
}
