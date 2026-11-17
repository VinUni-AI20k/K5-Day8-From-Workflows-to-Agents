import { useEffect, useMemo } from 'react'
import {
  Background,
  BackgroundVariant,
  Controls,
  MiniMap,
  ReactFlow,
  useEdgesState,
  useNodesState,
  type Edge,
  type Node,
} from '@xyflow/react'
import '@xyflow/react/dist/style.css'
import { FlowEdge, type FlowEdgeData } from './FlowEdge'
import { StepNode } from './StepNode'
import { buildGraph, type StepNodeData } from '../shapes/graphs'
import type { NodeRunState, ShapeId } from '../types'

const nodeTypes = { step: StepNode }
const edgeTypes = { flow: FlowEdge }

interface Props {
  shape: ShapeId
  nodeStates: Record<string, NodeRunState>
  activeEdgeIds: string[]
  selectedNodeId: string | null
  onSelectNode: (id: string | null) => void
  lively: boolean
}

export function FlowCanvas({
  shape,
  nodeStates,
  activeEdgeIds,
  selectedNodeId,
  onSelectNode,
  lively,
}: Props) {
  const initial = useMemo(() => buildGraph(shape), [shape])
  const [nodes, setNodes, onNodesChange] = useNodesState<Node<StepNodeData>>(initial.nodes)
  const [edges, setEdges, onEdgesChange] = useEdgesState<Edge<FlowEdgeData>>(
    initial.edges as Edge<FlowEdgeData>[],
  )

  useEffect(() => {
    const g = buildGraph(shape)
    setNodes(g.nodes)
    setEdges(g.edges as Edge<FlowEdgeData>[])
  }, [shape, setNodes, setEdges])

  useEffect(() => {
    setNodes((prev) =>
      prev.map((n) => ({
        ...n,
        selected: n.id === selectedNodeId,
        className: lively && nodeStates[n.id] === 'running' ? 'rf-node-active' : '',
        data: {
          ...n.data,
          runState: nodeStates[n.id] ?? 'idle',
        },
      })),
    )
  }, [nodeStates, selectedNodeId, lively, setNodes])

  useEffect(() => {
    setEdges((prev) =>
      prev.map((edge) => ({
        ...edge,
        animated: false,
        data: { ...edge.data, active: activeEdgeIds.includes(edge.id) },
      })),
    )
  }, [activeEdgeIds, setEdges])

  return (
    <div className={`flow-canvas ${lively ? 'is-lively' : ''}`}>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        nodeTypes={nodeTypes}
        edgeTypes={edgeTypes}
        fitView
        fitViewOptions={{ padding: 0.22 }}
        minZoom={0.3}
        maxZoom={1.6}
        proOptions={{ hideAttribution: true }}
        onNodeClick={(_, node) => onSelectNode(node.id)}
        onPaneClick={() => onSelectNode(null)}
      >
        <Background
          id="grid"
          variant={BackgroundVariant.Dots}
          gap={20}
          size={1.15}
          color="#d7dee8"
        />
        <Controls showInteractive={false} />
        <MiniMap
          pannable
          zoomable
          bgColor="#f8fafc"
          maskColor="rgba(255,255,255,0.72)"
          nodeColor={(n) => {
            const s = (n.data as StepNodeData)?.runState
            if (s === 'running') return '#0f766e'
            if (s === 'success') return '#15803d'
            if (s === 'error' || s === 'bottleneck') return '#c2410c'
            if (s === 'skipped') return '#94a3b8'
            return '#64748b'
          }}
        />
      </ReactFlow>
    </div>
  )
}
