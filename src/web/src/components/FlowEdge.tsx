import {
  BaseEdge,
  EdgeLabelRenderer,
  getSmoothStepPath,
  type Edge,
  type EdgeProps,
} from '@xyflow/react'

export type FlowEdgeData = {
  active?: boolean
}

export function FlowEdge({
  id,
  sourceX,
  sourceY,
  targetX,
  targetY,
  sourcePosition,
  targetPosition,
  label,
  data,
  markerEnd,
}: EdgeProps<Edge<FlowEdgeData>>) {
  const [path, labelX, labelY] = getSmoothStepPath({
    sourceX,
    sourceY,
    targetX,
    targetY,
    sourcePosition,
    targetPosition,
    borderRadius: 18,
  })

  const active = Boolean(data?.active)

  return (
    <>
      <BaseEdge
        id={id}
        path={path}
        markerEnd={markerEnd}
        className={active ? 'flow-edge-path is-active' : 'flow-edge-path'}
      />
      {active && (
        <>
          <circle r="4" className="flow-particle">
            <animateMotion dur="1.1s" repeatCount="indefinite" path={path} />
          </circle>
          <circle r="3" className="flow-particle flow-particle--lag">
            <animateMotion dur="1.1s" begin="0.35s" repeatCount="indefinite" path={path} />
          </circle>
        </>
      )}
      {label && (
        <EdgeLabelRenderer>
          <div
            className={`flow-edge-label ${active ? 'is-active' : ''}`}
            style={{
              transform: `translate(-50%, -50%) translate(${labelX}px, ${labelY}px)`,
            }}
          >
            {label}
          </div>
        </EdgeLabelRenderer>
      )}
    </>
  )
}
