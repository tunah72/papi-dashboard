import { useEffect, useRef, type ReactNode } from 'react'
import { createPortal } from 'react-dom'

type ChartFocusDialogProps = {
  chartId: string
  title: string
  subtitle?: string
  activeContext: string
  insight?: ReactNode
  footer?: ReactNode
  open: boolean
  onOpenChange: (open: boolean) => void
  children: ReactNode
}

export function ChartFocusDialog({
  chartId,
  title,
  subtitle,
  activeContext,
  insight,
  footer,
  open,
  onOpenChange,
  children,
}: ChartFocusDialogProps) {
  const dialogRef = useRef<HTMLDialogElement>(null)
  const triggerRef = useRef<HTMLButtonElement>(null)
  const wasOpen = useRef(false)
  const titleId = `${chartId}-focus-title`
  const descriptionId = `${chartId}-focus-description`

  useEffect(() => {
    const dialog = dialogRef.current
    if (open && dialog && !dialog.open) {
      if (typeof dialog.showModal === 'function') dialog.showModal()
      else dialog.setAttribute('open', '')
      wasOpen.current = true
    } else if (!open && dialog?.open) {
      if (typeof dialog.close === 'function') dialog.close()
      else dialog.removeAttribute('open')
    }
    if (!open && wasOpen.current) {
      wasOpen.current = false
      window.setTimeout(() => triggerRef.current?.focus(), 0)
    }
  }, [open])

  useEffect(() => {
    if (!open) return
    const previousOverflow = document.body.style.overflow
    document.body.style.overflow = 'hidden'
    return () => { document.body.style.overflow = previousOverflow }
  }, [open])

  const dialog = <dialog
    ref={dialogRef}
    className="chart-focus-dialog"
    aria-modal="true"
    aria-labelledby={titleId}
    aria-describedby={descriptionId}
    onCancel={(event) => {
      event.preventDefault()
      onOpenChange(false)
    }}
    onClose={() => { if (open) onOpenChange(false) }}
    onClick={(event) => {
      if (event.target === event.currentTarget) onOpenChange(false)
    }}
  >
    <div className="chart-focus-panel">
      <header className="chart-focus-header">
        <div>
          <p className="eyebrow">Chế độ xem riêng</p>
          <h2 id={titleId}>{title}</h2>
          <p id={descriptionId}>{subtitle}</p>
        </div>
        <div className="chart-focus-header-actions">
          <span>{activeContext}</span>
          <button type="button" className="chart-focus-close" onClick={() => onOpenChange(false)}>
            Thu nhỏ <span aria-hidden="true">×</span>
          </button>
        </div>
      </header>
      <div className="chart-focus-layout">
        <div className="chart-focus-plot">{children}</div>
        <aside className="chart-focus-rail" aria-label="Kết luận và thông tin biểu đồ">
          {insight}
          {footer}
        </aside>
      </div>
    </div>
  </dialog>

  return <>
    <button
      ref={triggerRef}
      type="button"
      className="chart-focus-trigger"
      aria-label={`Phóng to biểu đồ: ${title}`}
      title="Phóng to biểu đồ"
      onClick={() => onOpenChange(true)}
    >
      <svg aria-hidden="true" viewBox="0 0 24 24" width="20" height="20" fill="none">
        <path d="M8 3H3v5M16 3h5v5M8 21H3v-5M16 21h5v-5" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
      </svg>
    </button>
    {typeof document === 'undefined' || !open ? null : createPortal(dialog, document.body)}
  </>
}
