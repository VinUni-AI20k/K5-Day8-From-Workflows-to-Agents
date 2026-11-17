/** Ultra-light line icons — no Lucide/Material. */

type IconProps = { size?: number; className?: string }

const base = (size: number) => ({
  width: size,
  height: size,
  viewBox: '0 0 24 24',
  fill: 'none',
  stroke: 'currentColor',
  strokeWidth: 1.25,
  strokeLinecap: 'round' as const,
  strokeLinejoin: 'round' as const,
  'aria-hidden': true as const,
})

export function IconPanelLeft({ size = 18, className }: IconProps) {
  return (
    <svg {...base(size)} className={className}>
      <rect x="3.5" y="4.5" width="17" height="15" rx="2" />
      <path d="M9 4.5v15" />
    </svg>
  )
}

export function IconPanelRight({ size = 18, className }: IconProps) {
  return (
    <svg {...base(size)} className={className}>
      <rect x="3.5" y="4.5" width="17" height="15" rx="2" />
      <path d="M15 4.5v15" />
    </svg>
  )
}

export function IconExpand({ size = 18, className }: IconProps) {
  return (
    <svg {...base(size)} className={className}>
      <path d="M9 4.5H4.5V9" />
      <path d="M15 4.5h4.5V9" />
      <path d="M9 19.5H4.5V15" />
      <path d="M15 19.5h4.5V15" />
    </svg>
  )
}

export function IconCompress({ size = 18, className }: IconProps) {
  return (
    <svg {...base(size)} className={className}>
      <path d="M9 9H4.5V4.5" />
      <path d="M15 9h4.5V4.5" />
      <path d="M9 15H4.5v4.5" />
      <path d="M15 15h4.5v4.5" />
    </svg>
  )
}

export function IconPlay({ size = 16, className }: IconProps) {
  return (
    <svg {...base(size)} className={className}>
      <path d="M8 6.5v11l9-5.5-9-5.5z" fill="currentColor" stroke="none" />
    </svg>
  )
}

export function IconPause({ size = 16, className }: IconProps) {
  return (
    <svg {...base(size)} className={className}>
      <path d="M8 6.5v11M16 6.5v11" />
    </svg>
  )
}

export function IconStep({ size = 16, className }: IconProps) {
  return (
    <svg {...base(size)} className={className}>
      <path d="M6 6.5v11l7-5.5-7-5.5z" fill="currentColor" stroke="none" />
      <path d="M17.5 6.5v11" />
    </svg>
  )
}

export function IconReset({ size = 16, className }: IconProps) {
  return (
    <svg {...base(size)} className={className}>
      <path d="M4.5 12a7.5 7.5 0 1 0 1.8-4.9" />
      <path d="M4.5 5.5v3.8H8.2" />
    </svg>
  )
}
