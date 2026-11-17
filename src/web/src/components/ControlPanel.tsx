import { SHAPE_META } from '../data/claims'
import type { Claim, RunnerMode, ShapeId } from '../types'
import { IconPause, IconPlay, IconReset, IconStep } from './Icons'

interface Props {
  shape: ShapeId
  claimId: string
  seed: number
  mode: RunnerMode
  progress: { current: number; total: number }
  collapsed: boolean
  claims: Claim[]
  apiOnline: boolean
  apiError: string | null
  onToggle: () => void
  onShapeChange: (s: ShapeId) => void
  onClaimChange: (id: string) => void
  onSeedChange: (n: number) => void
  onRun: () => void
  onPause: () => void
  onResume: () => void
  onStep: () => void
  onReset: () => void
  claim: Claim
}

export function ControlPanel({
  shape,
  claimId,
  seed,
  mode,
  progress,
  collapsed,
  claims,
  apiOnline,
  apiError,
  onToggle,
  onShapeChange,
  onClaimChange,
  onSeedChange,
  onRun,
  onPause,
  onResume,
  onStep,
  onReset,
  claim,
}: Props) {
  const busy = mode === 'running' || mode === 'paused'
  const pct = progress.total ? Math.min(1, progress.current / progress.total) : 0

  return (
    <aside className={`rail rail-left ${collapsed ? 'is-collapsed' : ''}`}>
      <button
        type="button"
        className="rail-toggle"
        onClick={onToggle}
        aria-label={collapsed ? 'Mở panel trái' : 'Thu panel trái'}
        title={collapsed ? 'Mở panel' : 'Thu panel'}
      >
        <span className="rail-toggle__bar" />
      </button>

      <div className="rail-body">
        <div className="surface">
          <div className="surface-inner stack-lg">
            <header className="brand-block">
              <span className="eyebrow">LogiX-VN · Lab 8</span>
              <h1>Claim Flow</h1>
              <p className="lede">Chạy thật `run_claim` qua API Python — canvas replay theo trace.</p>
              <span className={apiOnline ? 'live-chip' : 'sim-chip'}>
                {apiOnline ? 'LIVE · lab8.web_api' : 'API offline'}
              </span>
              {apiError && <p className="api-error">{apiError}</p>}
            </header>

            <section className="stack-md">
              <p className="field-label">Architecture</p>
              <div className="shape-list">
                {SHAPE_META.map((s) => (
                  <button
                    key={s.id}
                    type="button"
                    className={`shape-row ${shape === s.id ? 'is-active' : ''}`}
                    onClick={() => onShapeChange(s.id)}
                    disabled={busy}
                  >
                    <span className="shape-row__title">{s.label}</span>
                    <span className="shape-row__sub">{s.short}</span>
                  </button>
                ))}
              </div>
            </section>

            <section className="stack-md">
              <label className="field">
                <span className="field-label">Ticket</span>
                <select
                  value={claimId}
                  disabled={busy}
                  onChange={(e) => onClaimChange(e.target.value)}
                >
                  {claims.map((c) => (
                    <option key={c.claim_id} value={c.claim_id}>
                      {c.claim_id} · {c.matrix_id} · {c.expected.status}
                    </option>
                  ))}
                </select>
              </label>

              <div className="ticket-card">
                <div className="ticket-card__meta">
                  <span>{claim.principal_id}</span>
                  <span>{claim.order_id ?? 'no order'}</span>
                  <span>{claim.approval_id ?? 'no approval'}</span>
                </div>
                <p>{claim.ticket}</p>
              </div>

              <label className="field field-row">
                <span className="field-label">Seed</span>
                <select
                  value={seed}
                  disabled={busy}
                  onChange={(e) => onSeedChange(Number(e.target.value))}
                >
                  {[11, 22, 33, 44, 55].map((s) => (
                    <option key={s} value={s}>
                      {s}
                      {s % 5 === 0 ? ' · weakness' : ''}
                    </option>
                  ))}
                </select>
              </label>
            </section>

            <section className="stack-md">
              <div className="progress-meta">
                <span>Progress</span>
                <strong>
                  {progress.current}/{progress.total || '—'}
                </strong>
              </div>
              <div className="progress-track" aria-hidden>
                <div className="progress-fill" style={{ transform: `scaleX(${pct})` }} />
              </div>

              <div className="run-actions">
                {mode !== 'running' && mode !== 'paused' && (
                  <button
                    type="button"
                    className="btn btn-primary"
                    onClick={onRun}
                    disabled={!apiOnline}
                  >
                    <span>Run live</span>
                    <span className="btn-nest">
                      <IconPlay />
                    </span>
                  </button>
                )}
                {mode === 'running' && (
                  <button type="button" className="btn btn-primary" onClick={onPause}>
                    <span>Pause</span>
                    <span className="btn-nest">
                      <IconPause />
                    </span>
                  </button>
                )}
                {mode === 'paused' && (
                  <button type="button" className="btn btn-primary" onClick={onResume}>
                    <span>Resume</span>
                    <span className="btn-nest">
                      <IconPlay />
                    </span>
                  </button>
                )}
                <div className="run-actions__row">
                  <button
                    type="button"
                    className="btn btn-quiet"
                    onClick={onStep}
                    disabled={mode === 'running' || mode === 'done'}
                  >
                    <IconStep />
                    <span>Step</span>
                  </button>
                  <button type="button" className="btn btn-quiet" onClick={onReset}>
                    <IconReset />
                    <span>Reset</span>
                  </button>
                </div>
              </div>
            </section>
          </div>
        </div>
      </div>
    </aside>
  )
}
