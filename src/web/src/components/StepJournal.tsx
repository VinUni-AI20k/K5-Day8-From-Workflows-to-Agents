import { useEffect, useRef } from 'react'
import type { StepEvent } from '../types'

interface Props {
  events: StepEvent[]
  activeNodeId: string | null
  onSelect: (nodeId: string) => void
}

export function StepJournal({ events, activeNodeId, onSelect }: Props) {
  const bottomRef = useRef<HTMLLIElement | null>(null)
  const listRef = useRef<HTMLOListElement | null>(null)

  useEffect(() => {
    const el = bottomRef.current
    if (!el) return
    el.scrollIntoView({ behavior: 'smooth', block: 'nearest' })
  }, [events.length, events[events.length - 1]?.state])

  return (
    <div className="surface surface-grow journal-surface">
      <div className="surface-inner step-journal">
        <div className="section-head">
          <h2>Step journal</h2>
          <span className="muted-count">{events.length} bước</span>
        </div>
        <p className="journal-hint">Mỗi bước khi chạy được ghi lại — kéo xuống để xem lịch sử.</p>
        <ol className="journal-list" ref={listRef}>
          {events.length === 0 && (
            <li className="muted journal-empty">Chưa chạy — nhấn Run live để xem từng bước.</li>
          )}
          {events.map((e, i) => {
            const isLast = i === events.length - 1
            const active = e.nodeId === activeNodeId
            return (
              <li
                key={e.id}
                ref={isLast ? bottomRef : undefined}
                className={[
                  'journal-item',
                  `kind-${e.kind}`,
                  e.state ? `state-${e.state}` : '',
                  active ? 'is-active' : '',
                ]
                  .filter(Boolean)
                  .join(' ')}
              >
                <button type="button" className="journal-item__btn" onClick={() => onSelect(e.nodeId)}>
                  <div className="journal-item__top">
                    <span className="journal-step">
                      #{e.stepIndex ?? i + 1}
                    </span>
                    <code>{e.nodeId}</code>
                    {e.state && <span className={`chip chip-${e.state}`}>{e.state}</span>}
                    <time>{new Date(e.at).toLocaleTimeString('vi-VN')}</time>
                  </div>
                  {e.label && <p className="journal-label">{e.label}</p>}
                  <p className="journal-msg">{e.message}</p>
                  {e.detail && <p className="journal-detail">{e.detail}</p>}
                </button>
              </li>
            )
          })}
        </ol>
      </div>
    </div>
  )
}
