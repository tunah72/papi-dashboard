import type { ReactNode } from 'react'

import { ChartFocusDialog } from './ChartFocusDialog'

export function DashboardPageHeader({ eyebrow, title, description, aside }: {
  eyebrow: string
  title: string
  description: string
  aside?: ReactNode
}) {
  return <header className="dashboard-title">
    <div><p className="eyebrow">{eyebrow}</p><h1>{title}</h1><p className="lede">{description}</p></div>
    {aside && <div className="dashboard-title-aside">{aside}</div>}
  </header>
}

export function FilterBar({ children, summary, onReset, resetDisabled = false, label = 'Bộ lọc dữ liệu' }: {
  children: ReactNode
  summary?: ReactNode
  onReset?: () => void
  resetDisabled?: boolean
  label?: string
}) {
  return <section className="filter-bar" aria-label={label}>
    <div className="filter-controls">{children}</div>
    <div className="filter-summary">{summary}{onReset && <button className="filter-reset" type="button" disabled={resetDisabled} onClick={onReset}>Đặt lại</button>}</div>
  </section>
}

export function KpiGrid({ children, label = 'Chỉ số tóm tắt' }: { children: ReactNode; label?: string }) {
  return <section className="kpi-grid" aria-label={label}>{children}</section>
}

export function KpiCard({ label, value, detail, tone = 'default' }: {
  label: string
  value: ReactNode
  detail?: ReactNode
  tone?: 'default' | 'positive' | 'negative' | 'accent'
}) {
  return <article className={`kpi-card kpi-${tone}`}><p>{label}</p><strong>{value}</strong>{detail && <small>{detail}</small>}</article>
}

export function ChartCard({ eyebrow, title, description, action, children, footer, insight, focus, className = '' }: {
  eyebrow?: string
  title: string
  description?: string
  action?: ReactNode
  children: ReactNode
  footer?: ReactNode
  insight?: ReactNode
  className?: string
  focus?: {
    id: string
    activeContext?: string
    open: boolean
    onOpenChange: (open: boolean) => void
    content?: ReactNode
  }
}) {
  return <section className={`chart-card ${className}`.trim()}>
    <header className="chart-card-header"><div>{eyebrow && <p className="eyebrow">{eyebrow}</p>}<h2>{title}</h2>{description && <p>{description}</p>}</div>{(action || focus) && <div className="chart-card-action">{action}{focus && <ChartFocusDialog chartId={focus.id} title={title} activeContext={focus.activeContext} insight={insight} footer={footer} open={focus.open} onOpenChange={focus.onOpenChange}>{focus.content ?? children}</ChartFocusDialog>}</div>}</header>
    <div className="chart-card-body">{children}</div>
    {insight}
    {footer && <footer className="chart-card-footer">{footer}</footer>}
  </section>
}

export function ChartInsight({ children }: { children: ReactNode }) {
  return <aside className="chart-insight" aria-label="Insight biểu đồ" aria-live="polite"><strong>Insight</strong><p>{children}</p></aside>
}

export function InsightCard({ label, value, children }: { label: string; value?: ReactNode; children: ReactNode }) {
  return <article className="insight-card"><p className="eyebrow">{label}</p>{value && <strong>{value}</strong>}<div>{children}</div></article>
}

export function ChartMeta({ source, unit, n, caveats = [] }: {
  source: string
  unit: string
  n: number | string
  caveats?: string[]
}) {
  return <div className="chart-meta"><span>Nguồn: {source}</span><span>Đơn vị: {unit}</span><span>n = {n}</span>{caveats.map((note) => <small key={note}>{note}</small>)}</div>
}

export function LoadingSkeleton({ label, cards = 4 }: { label: string; cards?: number }) {
  return <section className="dashboard-loading" role="status" aria-live="polite" aria-label={label}>{Array.from({ length: cards }, (_, index) => <div key={index} />)}</section>
}

export function EmptyState({ title, description, action }: { title: string; description: string; action?: ReactNode }) {
  return <section className="dashboard-state"><span aria-hidden="true">○</span><h1>{title}</h1><p>{description}</p>{action}</section>
}

export function ErrorState({ title, description, action }: { title: string; description: string; action?: ReactNode }) {
  return <section className="dashboard-state dashboard-state-error" role="alert"><span aria-hidden="true">×</span><h1>{title}</h1><p>{description}</p>{action}</section>
}
