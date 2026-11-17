import type { Claim, NodeRunState, RunOutcome, ShapeId, StepEvent } from '../types'
import { ResultPanel } from './ResultPanel'
import { StepJournal } from './StepJournal'

interface Props {
  collapsed: boolean
  onToggle: () => void
  claim: Claim
  outcome: RunOutcome | null
  shape: ShapeId
  selectedNodeId: string | null
  nodeStates: Record<string, NodeRunState>
  events: StepEvent[]
  onSelectNode: (id: string | null) => void
}

export function RightRail({
  collapsed,
  onToggle,
  claim,
  outcome,
  selectedNodeId,
  events,
  onSelectNode,
}: Props) {
  return (
    <aside className={`rail rail-right ${collapsed ? 'is-collapsed' : ''}`}>
      <button
        type="button"
        className="rail-toggle rail-toggle--right"
        onClick={onToggle}
        aria-label={collapsed ? 'Mở panel phải' : 'Thu panel phải'}
        title={collapsed ? 'Mở panel' : 'Thu panel'}
      >
        <span className="rail-toggle__bar" />
      </button>

      <div className="rail-body">
        <div className="right-stack right-stack--journal">
          <ResultPanel claim={claim} outcome={outcome} compact />
          <StepJournal
            events={events}
            activeNodeId={selectedNodeId}
            onSelect={(id) => onSelectNode(id)}
          />
        </div>
      </div>
    </aside>
  )
}
