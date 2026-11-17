import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { checkHealth, fetchClaims, runLive } from './api/client'
import { ControlPanel } from './components/ControlPanel'
import { FlowCanvas } from './components/FlowCanvas'
import {
  IconCompress,
  IconExpand,
  IconPanelLeft,
  IconPanelRight,
} from './components/Icons'
import { RightRail } from './components/RightRail'
import { CLAIMS as FALLBACK_CLAIMS } from './data/claims'
import { buildLivePlayback } from './shapes/fromTrace'
import type { SimStep } from './shapes/simulate'
import type { Claim, NodeRunState, RunOutcome, RunnerMode, ShapeId, StepEvent } from './types'
import './App.css'

export default function App() {
  const [shape, setShape] = useState<ShapeId>('workflow')
  const [claimId, setClaimId] = useState('C-001')
  const [seed, setSeed] = useState(11)
  const [claims, setClaims] = useState<Claim[]>(FALLBACK_CLAIMS)
  const [apiOnline, setApiOnline] = useState(false)
  const [apiError, setApiError] = useState<string | null>(null)
  const [mode, setMode] = useState<RunnerMode>('idle')
  const [nodeStates, setNodeStates] = useState<Record<string, NodeRunState>>({})
  const [activeEdgeIds, setActiveEdgeIds] = useState<string[]>([])
  const [events, setEvents] = useState<StepEvent[]>([])
  const [outcome, setOutcome] = useState<RunOutcome | null>(null)
  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null)
  const [progress, setProgress] = useState({ current: 0, total: 0 })
  const [lively, setLively] = useState(false)
  const [leftCollapsed, setLeftCollapsed] = useState(false)
  const [rightCollapsed, setRightCollapsed] = useState(false)
  const [canvasFullscreen, setCanvasFullscreen] = useState(false)

  const stageRef = useRef<HTMLElement | null>(null)
  const runIdRef = useRef(0)
  const pausedRef = useRef(false)
  const stepResolveRef = useRef<(() => void) | null>(null)
  const stepsRef = useRef<SimStep[]>([])
  const indexRef = useRef(0)
  const statesRef = useRef<Record<string, NodeRunState>>({})
  const outcomeRef = useRef<RunOutcome | null>(null)
  const mountedRef = useRef(true)

  const claim = useMemo(
    () => claims.find((c) => c.claim_id === claimId) ?? claims[0] ?? FALLBACK_CLAIMS[0],
    [claims, claimId],
  )

  useEffect(() => {
    mountedRef.current = true
    return () => {
      mountedRef.current = false
      runIdRef.current += 1
      stepResolveRef.current?.()
    }
  }, [])

  useEffect(() => {
    let cancelled = false
    const boot = async () => {
      const ok = await checkHealth()
      if (cancelled) return
      setApiOnline(ok)
      if (!ok) {
        setApiError('Không kết nối được lab8.web_api — chạy: python -m lab8.web_api')
        return
      }
      try {
        const data = await fetchClaims()
        if (cancelled) return
        setClaims(data.claims)
        setApiError(null)
        if (!data.claims.some((c) => c.claim_id === claimId) && data.claims[0]) {
          setClaimId(data.claims[0].claim_id)
        }
      } catch (err) {
        if (!cancelled) setApiError(err instanceof Error ? err.message : String(err))
      }
    }
    void boot()
    const timer = window.setInterval(() => {
      void checkHealth().then((ok) => {
        if (!cancelled) {
          setApiOnline(ok)
          if (!ok) {
            setApiError('Không kết nối được lab8.web_api — chạy: python -m lab8.web_api')
          }
        }
      })
    }, 5000)
    return () => {
      cancelled = true
      window.clearInterval(timer)
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps -- boot once on mount
  }, [])

  useEffect(() => {
    const onFs = () => {
      const el = stageRef.current
      setCanvasFullscreen(Boolean(el && document.fullscreenElement === el))
    }
    document.addEventListener('fullscreenchange', onFs)
    return () => document.removeEventListener('fullscreenchange', onFs)
  }, [])

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && canvasFullscreen && !document.fullscreenElement) {
        setCanvasFullscreen(false)
      }
      if (e.key === '[' && !e.metaKey && !e.ctrlKey) setLeftCollapsed((v) => !v)
      if (e.key === ']' && !e.metaKey && !e.ctrlKey) setRightCollapsed((v) => !v)
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [canvasFullscreen])

  const clearVisual = useCallback(() => {
    setNodeStates({})
    setActiveEdgeIds([])
    setEvents([])
    setOutcome(null)
    setProgress({ current: 0, total: 0 })
    setLively(false)
    statesRef.current = {}
    stepsRef.current = []
    indexRef.current = 0
    outcomeRef.current = null
  }, [])

  const hardStop = useCallback(() => {
    runIdRef.current += 1
    pausedRef.current = false
    stepResolveRef.current?.()
    stepResolveRef.current = null
    setMode('idle')
    setLively(false)
  }, [])

  const resetAll = useCallback(() => {
    hardStop()
    clearVisual()
    setSelectedNodeId(null)
  }, [clearVisual, hardStop])

  const handleShapeChange = (s: ShapeId) => {
    resetAll()
    setShape(s)
  }

  const handleClaimChange = (id: string) => {
    resetAll()
    setClaimId(id)
  }

  const waitGate = (runId: number, ms: number) =>
    new Promise<void>((resolve) => {
      let remaining = ms
      let last = performance.now()
      let timer: number | undefined
      let settled = false

      const finish = () => {
        if (settled) return
        settled = true
        if (timer !== undefined) window.clearTimeout(timer)
        if (stepResolveRef.current === finish) stepResolveRef.current = null
        resolve()
      }
      stepResolveRef.current = finish

      const loop = () => {
        if (runId !== runIdRef.current || !mountedRef.current) {
          finish()
          return
        }
        const now = performance.now()
        if (!pausedRef.current) remaining -= now - last
        last = now
        if (remaining <= 0) {
          finish()
          return
        }
        timer = window.setTimeout(loop, Math.min(50, remaining))
      }
      loop()
    })

  const applyStep = (step: SimStep, stepIndex: number) => {
    const states = { ...statesRef.current }
    const eventId = `${step.nodeId}-${Date.now()}-${Math.random().toString(36).slice(2, 6)}`

    if (step.state === 'skipped') {
      states[step.nodeId] = 'skipped'
      statesRef.current = states
      setNodeStates(states)
      setEvents((prev) => [
        ...prev,
        {
          id: eventId,
          at: Date.now(),
          ...step.event,
          state: 'skipped',
          stepIndex,
          label: step.nodeId,
        },
      ])
      return
    }

    states[step.nodeId] = 'running'
    statesRef.current = states
    setNodeStates({ ...states })
    setSelectedNodeId(step.nodeId)
    if (step.edgeId) setActiveEdgeIds([step.edgeId])

    setEvents((prev) => [
      ...prev,
      {
        id: eventId,
        at: Date.now(),
        ...step.event,
        state: 'running',
        stepIndex,
        label: step.nodeId,
      },
    ])
  }

  const commitStep = (step: SimStep) => {
    const states = { ...statesRef.current, [step.nodeId]: step.state }
    statesRef.current = states
    setNodeStates(states)
    setEvents((prev) => {
      const next = [...prev]
      for (let i = next.length - 1; i >= 0; i -= 1) {
        if (next[i].nodeId === step.nodeId && next[i].state === 'running') {
          next[i] = { ...next[i], state: step.state, at: Date.now() }
          break
        }
      }
      return next
    })
  }

  const finishRun = (runId: number) => {
    if (runId !== runIdRef.current || !mountedRef.current) return
    const next = outcomeRef.current
    if (next?.bottleneckNodeId) {
      const states = {
        ...statesRef.current,
        [next.bottleneckNodeId]: 'bottleneck' as NodeRunState,
      }
      statesRef.current = states
      setNodeStates(states)
      setSelectedNodeId(next.bottleneckNodeId)
    }
    setOutcome(next)
    setActiveEdgeIds([])
    setLively(false)
    setMode('done')
  }

  const playFrom = async (runId: number) => {
    setMode('running')
    setLively(true)
    const steps = stepsRef.current

    while (indexRef.current < steps.length) {
      if (runId !== runIdRef.current || !mountedRef.current) return
      const step = steps[indexRef.current]
      const stepNo = indexRef.current + 1
      applyStep(step, stepNo)

      if (step.state !== 'skipped') {
        await waitGate(runId, step.delayMs ?? 560)
        if (runId !== runIdRef.current || !mountedRef.current) return
        commitStep(step)
      }

      indexRef.current += 1
      setProgress({ current: indexRef.current, total: steps.length })

      if (pausedRef.current) {
        setMode('paused')
        setLively(false)
        return
      }
    }

    finishRun(runId)
  }

  const prepareLivePlayback = async () => {
    setApiError(null)
    const live = await runLive({
      shape,
      claim_id: claim.claim_id,
      seed,
    })
    if (live.claim) {
      setClaims((prev) => {
        const others = prev.filter((c) => c.claim_id !== live.claim.claim_id)
        return [...others, live.claim]
      })
    }
    const playback = buildLivePlayback(live)
    stepsRef.current = playback.steps
    outcomeRef.current = playback.outcome
    indexRef.current = 0
    setProgress({ current: 0, total: playback.steps.length })
    return live
  }

  const startRun = async () => {
    if (!apiOnline) {
      setApiError('API offline — chạy python -m lab8.web_api trong thư mục src/')
      return
    }

    runIdRef.current += 1
    stepResolveRef.current?.()
    stepResolveRef.current = null
    pausedRef.current = false
    clearVisual()
    setMode('running')
    setApiError('Đang gọi backend…')

    const runId = runIdRef.current
    try {
      await prepareLivePlayback()
      setApiError(null)
      await playFrom(runId)
    } catch (err) {
      if (runId !== runIdRef.current) return
      setMode('idle')
      setLively(false)
      setApiError(err instanceof Error ? err.message : String(err))
    }
  }

  const onPause = () => {
    if (mode === 'running') pausedRef.current = true
  }

  const onResume = () => {
    if (mode !== 'paused') return
    pausedRef.current = false
    setLively(true)
    void playFrom(runIdRef.current)
  }

  const onStep = async () => {
    if (mode === 'running' || mode === 'done') return
    if (!apiOnline) {
      setApiError('API offline — chạy python -m lab8.web_api trong thư mục src/')
      return
    }

    if (mode === 'idle' || stepsRef.current.length === 0) {
      hardStop()
      clearVisual()
      const runId = runIdRef.current + 1
      runIdRef.current = runId
      try {
        setApiError('Đang gọi backend…')
        await prepareLivePlayback()
        setApiError(null)
        pausedRef.current = true
        setMode('paused')
      } catch (err) {
        setMode('idle')
        setApiError(err instanceof Error ? err.message : String(err))
        return
      }
    }

    const runId = runIdRef.current
    if (indexRef.current >= stepsRef.current.length) {
      finishRun(runId)
      return
    }

    const step = stepsRef.current[indexRef.current]
    const stepNo = indexRef.current + 1
    setLively(true)
    applyStep(step, stepNo)
    if (step.state !== 'skipped') {
      await waitGate(runId, step.delayMs ?? 320)
      if (runId !== runIdRef.current) return
      commitStep(step)
    }
    indexRef.current += 1
    setProgress({ current: indexRef.current, total: stepsRef.current.length })
    setLively(false)

    if (indexRef.current >= stepsRef.current.length) finishRun(runId)
    else setMode('paused')
  }

  const toggleFullscreen = async () => {
    const el = stageRef.current
    if (!el) return

    try {
      if (document.fullscreenElement === el) {
        await document.exitFullscreen()
        setCanvasFullscreen(false)
        return
      }
      if (document.fullscreenElement) await document.exitFullscreen()
      if (el.requestFullscreen) {
        await el.requestFullscreen()
        setCanvasFullscreen(true)
        return
      }
    } catch {
      // Fallback CSS fullscreen
    }
    setCanvasFullscreen((v) => !v)
  }

  const shellClass = [
    'app-shell',
    leftCollapsed ? 'left-collapsed' : '',
    rightCollapsed ? 'right-collapsed' : '',
    canvasFullscreen ? 'canvas-fs' : '',
  ]
    .filter(Boolean)
    .join(' ')

  return (
    <div className={shellClass}>
      <ControlPanel
        shape={shape}
        claimId={claim.claim_id}
        seed={seed}
        mode={mode}
        progress={progress}
        claim={claim}
        claims={claims}
        apiOnline={apiOnline}
        apiError={apiError}
        collapsed={leftCollapsed}
        onToggle={() => setLeftCollapsed((v) => !v)}
        onShapeChange={handleShapeChange}
        onClaimChange={handleClaimChange}
        onSeedChange={(n) => {
          resetAll()
          setSeed(n)
        }}
        onRun={startRun}
        onPause={onPause}
        onResume={onResume}
        onStep={onStep}
        onReset={resetAll}
      />

      <main className="main-stage" ref={stageRef}>
        <div className="stage-chrome">
          <div className="stage-chrome__left">
            <button
              type="button"
              className="icon-btn"
              onClick={() => setLeftCollapsed((v) => !v)}
              aria-label="Toggle left panel"
              title="Toggle left ([)"
            >
              <IconPanelLeft />
            </button>
            <div className="stage-title">
              <strong>{shape}</strong>
              <span>
                {claim.claim_id} · seed {seed} · {mode}
                {apiOnline ? ' · live' : ' · offline'}
              </span>
            </div>
          </div>

          <div className="stage-chrome__right">
            <div className="legend">
              <span className="lg running">run</span>
              <span className="lg success">ok</span>
              <span className="lg error">err</span>
              <span className="lg bottleneck">block</span>
              <span className="lg skipped">skip</span>
            </div>
            <button
              type="button"
              className="icon-btn"
              onClick={() => setRightCollapsed((v) => !v)}
              aria-label="Toggle right panel"
              title="Toggle right (])"
            >
              <IconPanelRight />
            </button>
            <button
              type="button"
              className="icon-btn icon-btn--accent"
              onClick={toggleFullscreen}
              aria-label={canvasFullscreen ? 'Exit fullscreen' : 'Fullscreen canvas'}
              title={canvasFullscreen ? 'Exit fullscreen' : 'Fullscreen canvas'}
            >
              {canvasFullscreen ? <IconCompress /> : <IconExpand />}
            </button>
          </div>
        </div>

        <FlowCanvas
          shape={shape}
          nodeStates={nodeStates}
          activeEdgeIds={activeEdgeIds}
          selectedNodeId={selectedNodeId}
          onSelectNode={setSelectedNodeId}
          lively={lively}
        />
      </main>

      <RightRail
        collapsed={rightCollapsed}
        onToggle={() => setRightCollapsed((v) => !v)}
        claim={claim}
        outcome={outcome}
        shape={shape}
        selectedNodeId={selectedNodeId}
        nodeStates={nodeStates}
        events={events}
        onSelectNode={setSelectedNodeId}
      />
    </div>
  )
}
