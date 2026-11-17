import type { Claim, RunOutcome } from '../types'

interface Props {
  claim: Claim
  outcome: RunOutcome | null
  compact?: boolean
}

function fmt(n: number) {
  return n.toLocaleString('vi-VN')
}

export function ResultPanel({ claim, outcome, compact = false }: Props) {
  const expected = claim.expected

  return (
    <div className={`surface ${compact ? 'result-compact' : ''}`}>
      <div className="surface-inner">
        <div className="section-head">
          <h2>Result</h2>
          {outcome ? (
            <span className={`chip chip-${outcome.status}`}>{outcome.status}</span>
          ) : (
            <span className="chip">running…</span>
          )}
        </div>

        {!outcome && (
          <p className="muted">Đang chạy — xem Step journal bên dưới theo từng bước.</p>
        )}

        {outcome && (
          <>
            <p className="result-copy">{outcome.summary}</p>
            <p className={outcome.matchesExpected ? 'match match-ok' : 'match match-bad'}>
              {outcome.matchesExpected ? 'Matches expected matrix' : 'Diverges from expected'}
            </p>

            <div className="stat-grid">
              <div>
                <span>Proposal</span>
                <strong>{fmt(outcome.proposalAmount)}</strong>
              </div>
              <div>
                <span>Refund</span>
                <strong>{fmt(outcome.refundVnd)}</strong>
              </div>
              {!compact && (
                <>
                  <div>
                    <span>Denied</span>
                    <strong>{outcome.policyDenied ? 'yes' : 'no'}</strong>
                  </div>
                  <div>
                    <span>Bottleneck</span>
                    <strong>{outcome.bottleneckNodeId ?? '—'}</strong>
                  </div>
                </>
              )}
            </div>

            {!compact && (
              <div className="compare">
                <p className="field-label">Expected</p>
                <ul>
                  <li>
                    status <code>{expected.status}</code>
                    <span className={outcome.status === expected.status ? 'ok' : 'bad'}>
                      {outcome.status === expected.status ? 'ok' : 'diff'}
                    </span>
                  </li>
                  <li>
                    proposal <code>{fmt(expected.proposal_amount)}</code>
                    <span
                      className={
                        outcome.proposalAmount === expected.proposal_amount ? 'ok' : 'bad'
                      }
                    >
                      {outcome.proposalAmount === expected.proposal_amount ? 'ok' : 'diff'}
                    </span>
                  </li>
                  <li>
                    refund <code>{fmt(expected.refund_vnd)}</code>
                    <span className={outcome.refundVnd === expected.refund_vnd ? 'ok' : 'bad'}>
                      {outcome.refundVnd === expected.refund_vnd ? 'ok' : 'diff'}
                    </span>
                  </li>
                </ul>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  )
}
