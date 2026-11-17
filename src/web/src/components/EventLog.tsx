import type { StepEvent } from '../types'

interface Props {
  events: StepEvent[]
}

export function EventLog({ events }: Props) {
  return (
    <div className="surface surface-grow">
      <div className="surface-inner event-log">
        <div className="section-head">
          <h2>Events</h2>
          <span className="muted-count">{events.length}</span>
        </div>
        <ol className="event-list">
          {events.length === 0 && <li className="muted">Chưa có sự kiện.</li>}
          {events.map((e) => (
            <li key={e.id} className={`event kind-${e.kind}`}>
              <div className="event__top">
                <code>{e.nodeId}</code>
                <time>{new Date(e.at).toLocaleTimeString('vi-VN')}</time>
              </div>
              <p>{e.message}</p>
              {e.detail && <p className="event__detail">{e.detail}</p>}
            </li>
          ))}
        </ol>
      </div>
    </div>
  )
}
