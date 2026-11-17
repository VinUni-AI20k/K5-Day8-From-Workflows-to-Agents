import { buildGraph } from '../shapes/graphs'
import type { NodeRunState, ShapeId, StepEvent } from '../types'

interface Props {
  shape: ShapeId
  nodeId: string | null
  nodeStates: Record<string, NodeRunState>
  events: StepEvent[]
}

export function NodeInspector({ shape, nodeId, nodeStates, events }: Props) {
  const graph = buildGraph(shape)
  const node = nodeId ? graph.nodes.find((n) => n.id === nodeId) : null
  const related = nodeId ? events.filter((e) => e.nodeId === nodeId).slice(-3) : []
  const state = nodeId ? (nodeStates[nodeId] ?? 'idle') : 'idle'

  return (
    <div className="surface">
      <div className="surface-inner">
        <div className="section-head">
          <h2>Inspector</h2>
          {nodeId && <span className={`chip chip-${state}`}>{state}</span>}
        </div>

        {!nodeId && <p className="muted">Chọn một node trên canvas.</p>}

        {nodeId && (
          <>
            <p className="inspector-title">{node?.data.label ?? nodeId}</p>
            <p className="muted">{node?.data.subtitle}</p>
            <p className="inspector-id">
              <code>{nodeId}</code>
            </p>
            {related.length > 0 && (
              <ul className="inspector-events">
                {related.map((ev) => (
                  <li key={ev.id}>
                    <strong>{ev.message}</strong>
                    {ev.detail && <span>{ev.detail}</span>}
                  </li>
                ))}
              </ul>
            )}
          </>
        )}
      </div>
    </div>
  )
}
