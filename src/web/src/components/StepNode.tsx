import { Handle, Position, type Node, type NodeProps } from '@xyflow/react'
import type { StepNodeData } from '../shapes/graphs'

const kindLabel: Record<string, string> = {
  input: 'IN',
  process: 'STEP',
  decision: 'GATE',
  agent: 'AGENT',
  host: 'HOST',
  output: 'OUT',
}

export function StepNode({ data, selected }: NodeProps<Node<StepNodeData>>) {
  const state = data.runState ?? 'idle'

  return (
    <div className={`step-node kind-${data.kind} state-${state} ${selected ? 'is-selected' : ''}`}>
      <Handle type="target" position={Position.Left} className="step-handle" />
      <div className="step-node__top">
        <span className="step-node__badge">{kindLabel[data.kind] ?? 'STEP'}</span>
        <span className={`step-node__dot state-${state}`} aria-hidden />
      </div>
      <div className="step-node__label">{data.label}</div>
      <div className="step-node__sub">{data.subtitle}</div>
      <Handle type="source" position={Position.Right} className="step-handle" />
    </div>
  )
}
