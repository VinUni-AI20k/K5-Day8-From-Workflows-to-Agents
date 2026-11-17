import type { LiveRunResponse } from '../api/client'
import type { RunOutcome, ShapeId, StepEvent } from '../types'
import type { SimStep } from './simulate'

function edge(source: string, target: string) {
  return `${source}->${target}`
}

function money(n: number) {
  return `${n.toLocaleString('vi-VN')} VND`
}

function ev(
  nodeId: string,
  kind: StepEvent['kind'],
  message: string,
  detail?: string,
  state: SimStep['state'] = 'success',
  edgeId?: string,
): SimStep {
  return {
    nodeId,
    state,
    edgeId,
    delayMs: state === 'skipped' ? 0 : 420,
    event: { nodeId, kind, message, detail },
  }
}

function skip(ids: string[]): SimStep[] {
  return ids.map((nodeId) =>
    ev(nodeId, 'info', 'Bỏ qua (không đi nhánh này)', undefined, 'skipped'),
  )
}

function outcomeFromLive(live: LiveRunResponse): RunOutcome {
  const result = live.result
  const expected = live.claim.expected
  const status = result?.status ?? (live.crashed ? 'failed' : 'failed')
  const proposalAmount = result?.proposal_amount ?? 0
  const refundVnd = live.refund_vnd
  const policyDenied = Boolean(result?.error_reason?.includes('policy') || result?.error_reason?.includes('approval') || result?.error_reason?.includes('refunded'))
  const summary = live.crashed
    ? `InjectedCrash tại ${live.crash_at}`
    : `${status} · proposal ${money(proposalAmount)} · refund ${money(refundVnd)}${
        result?.error_reason ? ` · ${result.error_reason}` : ''
      }`

  return {
    status,
    proposalAmount,
    refundVnd,
    policyDenied,
    bottleneckNodeId: null,
    summary: `[${live.shape}] ${summary}`,
    matchesExpected:
      !!result &&
      result.status === expected.status &&
      proposalAmount === expected.proposal_amount &&
      refundVnd === expected.refund_vnd,
  }
}

function workflowFromLive(live: LiveRunResponse): { steps: SimStep[]; outcome: RunOutcome } {
  const events = live.trace.events || []
  const steps: SimStep[] = []
  const status = live.result?.status
  let bottleneck: string | null = null

  steps.push(ev('wf-load', 'start', `Load claim ${live.claim.claim_id}`, live.claim.ticket))

  const claimEv = events.find((e) => e.kind === 'claim')
  const orderId = (claimEv?.payload?.order_id as string | null | undefined) ?? live.claim.order_id
  if (!orderId) {
    steps.push(
      ev('wf-orderid', 'warn', 'Thiếu order_id', 'needs_info', 'error', edge('wf-load', 'wf-orderid')),
      ev('wf-needs', 'done', 'status = needs_info', undefined, 'success', edge('wf-orderid', 'wf-needs')),
      ...skip(['wf-lookup', 'wf-visible', 'wf-escalate', 'wf-quote', 'wf-amount', 'wf-denied', 'wf-host', 'wf-result']),
    )
    bottleneck = 'wf-orderid'
  } else {
    steps.push(
      ev('wf-orderid', 'info', `order_id = ${orderId}`, undefined, 'success', edge('wf-load', 'wf-orderid')),
      ev('wf-lookup', 'info', 'lookup_order', undefined, 'success', edge('wf-orderid', 'wf-lookup')),
    )

    const orderEv = events.find((e) => e.kind === 'order')
    const visible = Boolean(orderEv?.payload?.visible ?? status !== 'escalated')
    if (!visible || status === 'escalated') {
      steps.push(
        ev(
          'wf-visible',
          'error',
          'Order không visible',
          String(orderEv?.payload?.reason || live.result?.error_reason || ''),
          'error',
          edge('wf-lookup', 'wf-visible'),
        ),
        ev('wf-escalate', 'done', 'status = escalated', undefined, 'success', edge('wf-visible', 'wf-escalate')),
        ...skip(['wf-needs', 'wf-quote', 'wf-amount', 'wf-denied', 'wf-host', 'wf-result']),
      )
      bottleneck = 'wf-visible'
    } else {
      steps.push(ev('wf-visible', 'info', 'Order visible', undefined, 'success', edge('wf-lookup', 'wf-visible')))
      const quoteEv = events.find((e) => e.kind === 'quote')
      const amount = Number(quoteEv?.payload?.amount_vnd ?? live.result?.proposal_amount ?? 0)
      steps.push(
        ev(
          'wf-quote',
          'info',
          `Quote ${money(amount)}`,
          String(quoteEv?.payload?.reason || ''),
          'success',
          edge('wf-visible', 'wf-quote'),
        ),
      )

      if (amount <= 0) {
        steps.push(
          ev('wf-amount', 'warn', 'Quote = 0', undefined, 'error', edge('wf-quote', 'wf-amount')),
          ev('wf-denied', 'done', 'status = denied', undefined, 'success', edge('wf-amount', 'wf-denied')),
          ...skip(['wf-needs', 'wf-escalate', 'wf-host', 'wf-result']),
        )
        bottleneck = 'wf-amount'
      } else {
        steps.push(
          ev('wf-amount', 'info', `Quote ${money(amount)} > 0`, undefined, 'success', edge('wf-quote', 'wf-amount')),
        )
        const hostEv = events.find((e) => e.kind === 'host')
        const hostOk = hostEv ? Boolean(hostEv.payload.ok) : status === 'resolved'
        if (!hostOk) {
          steps.push(
            ev(
              'wf-host',
              'error',
              'Host từ chối / conflict',
              String(hostEv?.payload?.reason || live.result?.error_reason || ''),
              'error',
              edge('wf-amount', 'wf-host'),
            ),
            ev(
              'wf-result',
              'done',
              `status = ${status}`,
              undefined,
              'success',
              edge('wf-host', 'wf-result'),
            ),
            ...skip(['wf-needs', 'wf-escalate', 'wf-denied']),
          )
          bottleneck = 'wf-host'
        } else {
          steps.push(
            ev(
              'wf-host',
              'info',
              `issue_refund → ${money(live.refund_vnd)}`,
              undefined,
              'success',
              edge('wf-amount', 'wf-host'),
            ),
            ev(
              'wf-result',
              'done',
              `status = ${status}`,
              undefined,
              'success',
              edge('wf-host', 'wf-result'),
            ),
            ...skip(['wf-needs', 'wf-escalate', 'wf-denied']),
          )
        }
      }
    }
  }

  const outcome = outcomeFromLive(live)
  outcome.bottleneckNodeId = bottleneck
  return { steps, outcome }
}

function singleFromLive(live: LiveRunResponse): { steps: SimStep[]; outcome: RunOutcome } {
  const events = live.trace.events || []
  const steps: SimStep[] = [
    ev('sg-load', 'start', `Single agent · ${live.claim.claim_id}`),
    ev('sg-react', 'info', 'ReAct loop ≤ 8', undefined, 'success', edge('sg-load', 'sg-react')),
  ]

  const actions = events.filter((e) => e.kind === 'action')
  if (actions.length) {
    steps.push(
      ev(
        'sg-think',
        'info',
        `${actions.length} tool decision(s)`,
        actions.map((a) => String(a.payload.tool)).join(' → '),
        'success',
        edge('sg-react', 'sg-think'),
      ),
      ev('sg-tools', 'info', 'Read tools executed', undefined, 'success', edge('sg-think', 'sg-tools')),
    )
  } else {
    steps.push(
      ev('sg-think', 'info', 'decide()', undefined, 'success', edge('sg-react', 'sg-think')),
      ev('sg-tools', 'info', 'read tools', undefined, 'success', edge('sg-think', 'sg-tools')),
    )
  }

  steps.push(ev('sg-cap', 'info', 'Budget / max steps gate', undefined, 'success', edge('sg-tools', 'sg-cap')))

  const quoteEv = events.find((e) => e.kind === 'quote')
  const amount = Number(quoteEv?.payload?.amount_vnd ?? live.result?.proposal_amount ?? 0)
  const status = live.result?.status

  if (status === 'needs_info' || status === 'escalated' || (status === 'denied' && amount <= 0)) {
    steps.push(
      ev(
        'sg-quote',
        status === 'denied' ? 'warn' : 'info',
        `Early · ${status}`,
        live.result?.error_reason || undefined,
        status === 'denied' ? 'error' : 'skipped',
        edge('sg-cap', 'sg-quote'),
      ),
      ev('sg-host', 'info', 'Không ghi ledger', undefined, 'skipped'),
      ev('sg-result', 'done', `status = ${status}`),
    )
  } else {
    steps.push(
      ev('sg-quote', 'info', `Quote ${money(amount)}`, undefined, 'success', edge('sg-cap', 'sg-quote')),
    )
    const hostOk = status === 'resolved'
    steps.push(
      ev(
        'sg-host',
        hostOk ? 'info' : 'error',
        hostOk ? `Refund ${money(live.refund_vnd)}` : `Host ${status}`,
        live.result?.error_reason || undefined,
        hostOk ? 'success' : 'error',
        edge('sg-quote', 'sg-host'),
      ),
      ev('sg-result', 'done', `status = ${status}`, undefined, 'success', edge('sg-host', 'sg-result')),
    )
  }

  const outcome = outcomeFromLive(live)
  if (status === 'needs_info' || status === 'escalated') outcome.bottleneckNodeId = 'sg-tools'
  else if (!outcome.matchesExpected && status !== 'resolved') outcome.bottleneckNodeId = 'sg-host'
  return { steps, outcome }
}

function orchestratorFromLive(live: LiveRunResponse): { steps: SimStep[]; outcome: RunOutcome } {
  const events = live.trace.events || []
  const status = live.result?.status
  const steps: SimStep[] = [
    ev('or-load', 'start', `Orchestrator · ${live.claim.claim_id}`),
  ]

  if (status === 'needs_info' || !live.claim.order_id) {
    steps.push(
      ev('or-check', 'warn', 'Thiếu order_id', undefined, 'error', edge('or-load', 'or-check')),
      ev('or-needs', 'done', 'needs_info', undefined, 'success', edge('or-check', 'or-needs')),
      ...skip(['or-handoff', 'or-invest', 'or-visible', 'or-esc', 'or-quote', 'or-host', 'or-result']),
    )
    const outcome = outcomeFromLive(live)
    outcome.bottleneckNodeId = 'or-check'
    return { steps, outcome }
  }

  steps.push(
    ev('or-check', 'info', `order_id ${live.claim.order_id}`, undefined, 'success', edge('or-load', 'or-check')),
  )

  const handoff = events.find((e) => e.kind === 'handoff')
  steps.push(
    ev(
      'or-handoff',
      'info',
      'make_handoff',
      handoff ? JSON.stringify(handoff.payload).slice(0, 120) : 'allowlist',
      'success',
      edge('or-check', 'or-handoff'),
    ),
  )

  const inv = events.find((e) => e.kind === 'investigator')
  steps.push(
    ev(
      'or-invest',
      'info',
      'Investigator read-only',
      inv
        ? `visible=${String(inv.payload.lookup_order_visible)} · policies=${String(inv.payload.policy_count)}`
        : undefined,
      'success',
      edge('or-handoff', 'or-invest'),
    ),
  )

  if (status === 'escalated' || inv?.payload.lookup_order_visible === false) {
    steps.push(
      ev('or-visible', 'error', 'Order không visible', undefined, 'error', edge('or-invest', 'or-visible')),
      ev('or-esc', 'done', 'escalated', undefined, 'success', edge('or-visible', 'or-esc')),
      ...skip(['or-needs', 'or-quote', 'or-host', 'or-result']),
    )
    const outcome = outcomeFromLive(live)
    outcome.bottleneckNodeId = 'or-visible'
    return { steps, outcome }
  }

  steps.push(ev('or-visible', 'info', 'Order visible', undefined, 'success', edge('or-invest', 'or-visible')))
  const quoteEv = events.find((e) => e.kind === 'quote')
  const amount = Number(quoteEv?.payload?.amount_vnd ?? live.result?.proposal_amount ?? 0)
  steps.push(
    ev('or-quote', 'info', `Quote ${money(amount)}`, undefined, amount > 0 ? 'success' : 'error', edge('or-visible', 'or-quote')),
  )

  if (amount <= 0) {
    steps.push(
      ev('or-host', 'info', 'Bỏ qua host', undefined, 'skipped'),
      ev('or-result', 'done', `status = ${status}`),
      ...skip(['or-needs', 'or-esc']),
    )
  } else {
    const hostOk = status === 'resolved'
    steps.push(
      ev(
        'or-host',
        hostOk ? 'info' : 'error',
        hostOk ? `Refund ${money(live.refund_vnd)}` : `Host ${status}`,
        live.result?.error_reason || undefined,
        hostOk ? 'success' : 'error',
        edge('or-quote', 'or-host'),
      ),
      ev('or-result', 'done', `status = ${status}`, undefined, 'success', edge('or-host', 'or-result')),
      ...skip(['or-needs', 'or-esc']),
    )
  }

  const outcome = outcomeFromLive(live)
  if (!outcome.matchesExpected && status !== 'resolved') outcome.bottleneckNodeId = 'or-host'
  return { steps, outcome }
}

function swarmFromLive(live: LiveRunResponse): { steps: SimStep[]; outcome: RunOutcome } {
  const events = live.trace.events || []
  const status = live.result?.status
  const override = events.find((e) => e.kind === 'model_override')
  const steps: SimStep[] = [
    ev('sw-load', 'start', `Swarm · ${live.claim.claim_id}`, `seed ${live.seed}`),
    ev('sw-peer', 'info', 'Peer chat / extra model calls', undefined, 'success', edge('sw-load', 'sw-peer')),
    ev(
      'sw-parse',
      override ? 'warn' : 'info',
      override ? `Trust ticket delay=${String(override.payload.delay_days)}` : 'Parse ticket (no override)',
      undefined,
      override ? 'bottleneck' : 'success',
      edge('sw-peer', 'sw-parse'),
    ),
  ]

  if (status === 'needs_info' || !live.claim.order_id) {
    steps.push(
      ev('sw-handoff', 'info', 'Early exit', undefined, 'skipped'),
      ...skip(['sw-trust', 'sw-wrong', 'sw-quote', 'sw-host']),
      ev('sw-result', 'done', 'needs_info'),
    )
    const outcome = outcomeFromLive(live)
    outcome.bottleneckNodeId = 'sw-load'
    return { steps, outcome }
  }

  steps.push(
    ev('sw-handoff', 'info', 'Investigators', undefined, 'success', edge('sw-parse', 'sw-handoff')),
  )

  if (override) {
    steps.push(
      ev('sw-trust', 'warn', 'Swarm tin ticket', 'REFERENCE_WEAKNESS', 'bottleneck', edge('sw-handoff', 'sw-trust')),
      ev(
        'sw-wrong',
        'error',
        `Quote lệch · proposal ${money(live.result?.proposal_amount ?? 0)}`,
        'So với expected matrix',
        'error',
        edge('sw-trust', 'sw-wrong'),
      ),
      ev('sw-quote', 'info', 'Nhánh quote đúng bị bỏ', undefined, 'skipped'),
      ev(
        'sw-host',
        'info',
        `Host theo proposal · refund ${money(live.refund_vnd)}`,
        undefined,
        'success',
        edge('sw-wrong', 'sw-host'),
      ),
      ev('sw-result', 'error', `status = ${status}`, undefined, 'error', edge('sw-host', 'sw-result')),
    )
    const outcome = outcomeFromLive(live)
    outcome.bottleneckNodeId = 'sw-trust'
    return { steps, outcome }
  }

  steps.push(
    ev('sw-trust', 'info', 'Dùng order row', undefined, 'success', edge('sw-handoff', 'sw-trust')),
  )
  const quoteEv = events.find((e) => e.kind === 'quote')
  const amount = Number(
    (quoteEv?.payload?.amount_vnd as number | undefined) ?? live.result?.proposal_amount ?? 0,
  )

  if (status === 'escalated') {
    steps.push(
      ev('sw-quote', 'info', 'Escalate trước quote', undefined, 'skipped', edge('sw-trust', 'sw-quote')),
      ...skip(['sw-wrong', 'sw-host']),
      ev('sw-result', 'done', 'escalated'),
    )
  } else if (amount <= 0) {
    steps.push(
      ev('sw-quote', 'warn', 'Quote 0', undefined, 'error', edge('sw-trust', 'sw-quote')),
      ...skip(['sw-wrong', 'sw-host']),
      ev('sw-result', 'done', `status = ${status}`),
    )
  } else {
    steps.push(
      ev('sw-quote', 'info', `Quote ${money(amount)}`, undefined, 'success', edge('sw-trust', 'sw-quote')),
      ev('sw-wrong', 'info', 'Weakness không kích hoạt', undefined, 'skipped'),
      ev(
        'sw-host',
        status === 'resolved' ? 'info' : 'error',
        status === 'resolved' ? `Refund ${money(live.refund_vnd)}` : `Host ${status}`,
        live.result?.error_reason || undefined,
        status === 'resolved' ? 'success' : 'error',
        edge('sw-quote', 'sw-host'),
      ),
      ev('sw-result', 'done', `status = ${status}`, undefined, 'success', edge('sw-host', 'sw-result')),
    )
  }

  return { steps, outcome: outcomeFromLive(live) }
}

export function buildLivePlayback(live: LiveRunResponse): { steps: SimStep[]; outcome: RunOutcome } {
  const shape = live.shape as ShapeId
  switch (shape) {
    case 'workflow':
      return workflowFromLive(live)
    case 'single':
      return singleFromLive(live)
    case 'orchestrator':
      return orchestratorFromLive(live)
    case 'swarm':
      return swarmFromLive(live)
    default:
      return {
        steps: [ev('wf-load', 'error', `Unknown shape ${shape}`, undefined, 'error')],
        outcome: outcomeFromLive(live),
      }
  }
}
