import type { Edge, Node } from '@xyflow/react'
import type { ShapeId } from '../types'

export type StepKind =
  | 'input'
  | 'process'
  | 'decision'
  | 'agent'
  | 'host'
  | 'output'

export interface StepNodeData extends Record<string, unknown> {
  label: string
  subtitle: string
  kind: StepKind
  runState: 'idle' | 'running' | 'success' | 'skipped' | 'error' | 'bottleneck'
}

const base = (
  id: string,
  label: string,
  subtitle: string,
  kind: StepKind,
  x: number,
  y: number,
): Node<StepNodeData> => ({
  id,
  type: 'step',
  position: { x, y },
  data: { label, subtitle, kind, runState: 'idle' },
})

const link = (source: string, target: string, label?: string): Edge => ({
  id: `${source}->${target}`,
  source,
  target,
  label,
  type: 'flow',
  animated: false,
  data: { active: false },
})

export function buildGraph(shape: ShapeId): {
  nodes: Node<StepNodeData>[]
  edges: Edge[]
} {
  switch (shape) {
    case 'workflow':
      return {
        nodes: [
          base('wf-load', 'Load claim', 'get_claim_view', 'input', 40, 180),
          base('wf-orderid', 'Có order_id?', 'Thiếu → needs_info', 'decision', 260, 180),
          base('wf-lookup', 'Lookup order', 'ownership + allowlist', 'process', 500, 80),
          base('wf-needs', 'needs_info', 'Không ghi ledger', 'output', 500, 300),
          base('wf-visible', 'Order visible?', 'Sai principal → escalate', 'decision', 740, 80),
          base('wf-escalate', 'escalated', 'Không lộ PII', 'output', 980, 200),
          base('wf-quote', 'Compute quote', 'Bỏ qua delay trong ticket', 'process', 980, 20),
          base('wf-amount', 'Quote > 0?', '0 → denied', 'decision', 1220, 20),
          base('wf-denied', 'denied', 'Không gọi host', 'output', 1460, 140),
          base('wf-host', 'Host issue_refund', 'Approval + trần đơn', 'host', 1460, -40),
          base('wf-result', 'Kết quả', 'resolved / denied', 'output', 1700, -40),
        ],
        edges: [
          link('wf-load', 'wf-orderid'),
          link('wf-orderid', 'wf-lookup', 'có'),
          link('wf-orderid', 'wf-needs', 'không'),
          link('wf-lookup', 'wf-visible'),
          link('wf-visible', 'wf-quote', 'yes'),
          link('wf-visible', 'wf-escalate', 'no'),
          link('wf-quote', 'wf-amount'),
          link('wf-amount', 'wf-host', '> 0'),
          link('wf-amount', 'wf-denied', '= 0'),
          link('wf-host', 'wf-result'),
        ],
      }
    case 'single':
      return {
        nodes: [
          base('sg-load', 'Load claim', 'claim + seed', 'input', 40, 160),
          base('sg-react', 'ReAct loop', '≤ 8 bước · tool đọc', 'agent', 280, 160),
          base('sg-think', 'Think / decide', 'MockLLM chọn tool', 'agent', 520, 40),
          base('sg-tools', 'Read tools', 'order · policy · history', 'process', 520, 260),
          base('sg-cap', 'Hết bước?', 'Budget steps ≤ 8', 'decision', 760, 160),
          base('sg-quote', 'Code tính quote', 'Model không quyết tiền', 'process', 1000, 160),
          base('sg-host', 'Host issue_refund', 'Ghi ledger duy nhất', 'host', 1240, 160),
          base('sg-result', 'Kết quả', 'RunResult + trace', 'output', 1480, 160),
        ],
        edges: [
          link('sg-load', 'sg-react'),
          link('sg-react', 'sg-think'),
          link('sg-think', 'sg-tools'),
          link('sg-tools', 'sg-cap'),
          link('sg-cap', 'sg-think', 'tiếp'),
          link('sg-cap', 'sg-quote', 'xong'),
          link('sg-quote', 'sg-host'),
          link('sg-host', 'sg-result'),
        ],
      }
    case 'orchestrator':
      return {
        nodes: [
          base('or-load', 'Load claim', 'claim row an toàn', 'input', 40, 160),
          base('or-check', 'Có order_id?', 'Thiếu → needs_info', 'decision', 260, 160),
          base('or-needs', 'needs_info', 'Early exit', 'output', 500, 300),
          base('or-handoff', 'make_handoff', 'Allowlist · không secret', 'process', 500, 80),
          base('or-invest', 'Investigator', 'Chỉ tool đọc', 'agent', 760, 80),
          base('or-visible', 'Order visible?', 'Ownership check', 'decision', 1020, 80),
          base('or-esc', 'escalated', 'Không copy PII', 'output', 1260, 220),
          base('or-quote', 'Orchestrator quote', 'Từ order view', 'process', 1260, 20),
          base('or-host', 'Host issue_refund', 'Full quote → host trừ', 'host', 1500, 20),
          base('or-result', 'Kết quả', 'resolved / denied', 'output', 1740, 20),
        ],
        edges: [
          link('or-load', 'or-check'),
          link('or-check', 'or-handoff', 'có'),
          link('or-check', 'or-needs', 'không'),
          link('or-handoff', 'or-invest'),
          link('or-invest', 'or-visible'),
          link('or-visible', 'or-quote', 'yes'),
          link('or-visible', 'or-esc', 'no'),
          link('or-quote', 'or-host'),
          link('or-host', 'or-result'),
        ],
      }
    case 'swarm':
      return {
        nodes: [
          base('sw-load', 'Load claim', 'claim + ticket', 'input', 40, 160),
          base('sw-peer', 'Peer chat', 'Extra model calls', 'agent', 260, 160),
          base('sw-parse', 'Parse ticket delay', 'Điểm yếu seed%5==0', 'agent', 500, 160),
          base('sw-handoff', 'Handoff peers', 'Investigators đọc', 'process', 740, 160),
          base('sw-trust', 'Tin ticket?', 'Lệch order → variance', 'decision', 980, 160),
          base('sw-wrong', 'Quote sai', 'Bottleneck ẩn', 'process', 1220, 280),
          base('sw-quote', 'Quote từ order', 'Đúng luật nghiệp vụ', 'process', 1220, 40),
          base('sw-host', 'Host issue_refund', 'Vẫn chặn approval', 'host', 1460, 100),
          base('sw-result', 'Kết quả', 'Đối chiếu cost/variance', 'output', 1700, 100),
        ],
        edges: [
          link('sw-load', 'sw-peer'),
          link('sw-peer', 'sw-parse'),
          link('sw-parse', 'sw-handoff'),
          link('sw-handoff', 'sw-trust'),
          link('sw-trust', 'sw-quote', 'không'),
          link('sw-trust', 'sw-wrong', 'có (weak)'),
          link('sw-quote', 'sw-host'),
          link('sw-wrong', 'sw-host'),
          link('sw-host', 'sw-result'),
        ],
      }
  }
}
