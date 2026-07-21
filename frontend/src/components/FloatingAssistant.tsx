import { useEffect, useMemo, useRef, useState } from 'react'
import type { Data, Layout } from 'plotly.js'
import { useLocation, useNavigate } from 'react-router-dom'
import { api, type AssistantMessageRequest } from '../api/client'
import { useAssistantStore, type AssistantTurn } from '../state/assistant'
import { CartesianChart } from './CartesianChart'

const pageNames: Record<string, string> = {
  '/overview': 'Tổng quan', '/time-trend': 'Diễn biến', '/provincial': 'Vùng và tỉnh',
  '/dimension': 'Mối quan hệ', '/dynamics': 'Thay đổi và phân nhóm',
}

function contextLabel(pathname: string, search: string) {
  const params = new URLSearchParams(search)
  const page = pageNames[pathname] ?? 'PAPI'
  if (pathname === '/time-trend' || pathname === '/dynamics') {
    const from = params.get('from'); const to = params.get('to')
    return from && to ? `${page} · ${from}–${to}` : `${page} · 2011–2024`
  }
  if (pathname === '/dimension') {
    const x = params.get('x'); const y = params.get('y'); const year = params.get('year')
    return `${page}${x && y ? ` · ${x} × ${y}` : ''}${year ? ` · ${year}` : ''}`
  }
  const province = params.get('province'); const region = params.get('region'); const year = params.get('year')
  return `${page}${province || region ? ` · ${province || region}` : year ? ` · ${year}` : ''}`
}

function ResultView({ turn }: { turn: AssistantTurn }) {
  const execution = turn.execution
  if (!execution) return null
  const result = execution.result as { kind?: string; columns?: string[]; rows?: Record<string, unknown>[]; value?: unknown; totalRows?: number; truncated?: boolean } | null | undefined
  const figure = execution.figure as { data?: Data[]; layout?: Partial<Layout> } | null | undefined
  return <section className={`assistant-result ${execution.status === 'failed' ? 'is-error' : ''}`} aria-label="Kết quả thực thi">
    <strong>{execution.status === 'failed' ? 'Chạy local gặp lỗi' : 'Kết quả chạy local'}</strong>
    {execution.error && <p role="alert">{execution.error}</p>}
    {result?.kind === 'scalar' && <output>{String(result.value ?? 'Không có giá trị')}</output>}
    {result?.kind === 'table' && result.rows && <div className="assistant-table-scroll"><table><caption>Kết quả phân tích{result.truncated ? ` · hiển thị 500/${result.totalRows} dòng` : ''}</caption><thead><tr>{result.columns?.map((column) => <th key={column}>{column}</th>)}</tr></thead><tbody>{result.rows.map((row, index) => <tr key={index}>{result.columns?.map((column) => <td key={column}>{String(row[column] ?? '—')}</td>)}</tr>)}</tbody></table></div>}
    {figure?.data && <CartesianChart title="Biểu đồ kết quả" summary="Biểu đồ do code đã được phê duyệt tạo tại máy local." data={figure.data} layout={figure.layout} height={280} />}
    {execution.stdout && <details><summary>Output và cảnh báo</summary><pre>{execution.stdout}</pre></details>}
  </section>
}

export function FloatingAssistant() {
  const location = useLocation()
  const navigate = useNavigate()
  const launcher = useRef<HTMLButtonElement>(null)
  const composer = useRef<HTMLTextAreaElement>(null)
  const [draft, setDraft] = useState('')
  const state = useAssistantStore()
  const label = useMemo(() => contextLabel(location.pathname, location.search), [location.pathname, location.search])
  const queryOpen = new URLSearchParams(location.search).get('assistant') === 'open'

  const updateUrl = (open: boolean) => {
    const params = new URLSearchParams(location.search)
    if (open) params.set('assistant', 'open'); else params.delete('assistant')
    navigate({ pathname: location.pathname, search: params.toString() ? `?${params}` : '' }, { replace: true })
  }
  const open = () => { state.setMode('open'); updateUrl(true); window.setTimeout(() => composer.current?.focus(), 0) }
  const leave = (mode: 'hidden' | 'minimized') => { state.setMode(mode); updateUrl(false); window.setTimeout(() => launcher.current?.focus(), 0) }

  useEffect(() => { if (queryOpen) useAssistantStore.getState().setMode('open') }, [queryOpen])
  useEffect(() => {
    if (state.mode !== 'open') return
    const onEscape = (event: KeyboardEvent) => {
      if (event.key !== 'Escape' || document.querySelector('dialog[open], .sidebar.is-open')) return
      event.preventDefault(); leave('hidden')
    }
    document.addEventListener('keydown', onEscape)
    return () => document.removeEventListener('keydown', onEscape)
  })

  const submit = async () => {
    const message = draft.trim()
    if (!message || state.busy) return
    state.addUser(message); setDraft(''); state.setError(null); state.setBusy('message')
    const search = Object.fromEntries([...new URLSearchParams(location.search)].filter(([key]) => key !== 'assistant' && key !== 'focus'))
    try {
      const response = await api.assistantMessage({ sessionId: state.sessionId, message, context: { route: location.pathname as AssistantMessageRequest['context']['route'], search }, revisionOf: state.revisionOf })
      state.setSessionId(response.sessionId); state.addResponse(response); state.setRevisionOf(null)
    } catch (error) { state.setError(error instanceof Error ? error.message : 'Không thể gửi yêu cầu.') }
    finally { state.setBusy(null) }
  }

  const approve = async (proposalId: string) => {
    if (!state.sessionId || state.busy) return
    state.setError(null); state.setBusy('execution')
    try { state.attachExecution(proposalId, await api.executeProposal(state.sessionId, proposalId)) }
    catch (error) { state.setError(error instanceof Error ? error.message : 'Không thể chạy proposal.') }
    finally { state.setBusy(null) }
  }

  const latestPending = [...state.turns].reverse().find((turn): turn is AssistantTurn => turn.role === 'assistant' && turn.response.kind === 'proposal' && !turn.superseded && !turn.execution)
  const pill = latestPending ? 'Chờ duyệt' : state.turns.some((turn) => turn.role === 'assistant' && turn.execution) ? 'Đã có kết quả' : 'Mở lại cuộc trò chuyện'

  return <div className="floating-assistant">
    {state.mode === 'minimized' && <button className="assistant-pill" type="button" onClick={open}><span aria-hidden="true" />Trợ lý AI · {pill}</button>}
    {state.mode === 'open' && <section className="assistant-dialog" role="dialog" aria-modal="false" aria-labelledby="assistant-title" onKeyDown={(event) => { if (event.key === 'Escape') { event.stopPropagation(); leave('hidden') } }}>
      <header className="assistant-header">
        <div><h2 id="assistant-title">Trợ lý AI</h2><p>{label}</p></div>
        <div className="assistant-header-actions">
          <button type="button" onClick={() => state.reset()} aria-label="Bắt đầu cuộc trò chuyện mới">Mới</button>
          <button type="button" onClick={() => leave('minimized')}>Thu nhỏ</button>
          <button type="button" onClick={() => leave('hidden')} aria-label="Đóng Trợ lý AI">×</button>
        </div>
      </header>
      <div className="assistant-conversation" aria-live="polite">
        {!state.turns.length && <div className="assistant-empty"><strong>Hỏi về PAPI hoặc yêu cầu một phân tích mới.</strong><p>AI có thể trả lời kiến thức. Nếu cần tính toán, toàn bộ code sẽ chờ bạn duyệt trước khi chạy local.</p></div>}
        {state.turns.map((turn) => turn.role === 'user'
          ? <article className="assistant-message is-user" key={turn.id}><small>Người dùng</small><p>{turn.text}</p></article>
          : <article className="assistant-message is-ai" key={turn.id}><small>Trợ lý AI</small>
            {turn.response.kind === 'answer' && <><p>{turn.response.answer}</p><p className="assistant-source">Nguồn: {turn.response.source}</p></>}
            {turn.response.kind === 'clarification' && <p>{turn.response.question}</p>}
            {turn.response.kind === 'proposal' && <><div className={`proposal-status ${turn.superseded ? 'is-superseded' : ''}`}>{turn.superseded ? 'ĐÃ ĐƯỢC THAY THẾ' : turn.execution ? 'ĐÃ THỰC THI' : 'CHỜ DUYỆT'}</div><p>{turn.response.explanation}</p><div className="assistant-code"><strong>Mã Python được đề xuất</strong><pre><code>{turn.response.code}</code></pre></div><p className="assistant-source">Nguồn dữ liệu: {turn.response.source}</p>{!turn.superseded && !turn.execution && <div className="assistant-proposal-actions"><button type="button" onClick={() => { if (turn.response.kind === 'proposal') state.setRevisionOf(turn.response.proposalId); composer.current?.focus() }}>Yêu cầu chỉnh lại</button><button className="assistant-approve" type="button" disabled={Boolean(state.busy)} onClick={() => { if (turn.response.kind === 'proposal') void approve(turn.response.proposalId) }}>Đồng ý và chạy local</button></div>}<ResultView turn={turn} /></>}
          </article>)}
        {state.busy && <p className="assistant-busy" role="status">{state.busy === 'message' ? 'Trợ lý đang chuẩn bị phản hồi…' : 'Đang chạy code đã duyệt tại máy local…'}</p>}
        {state.error && <div className="assistant-error" role="alert"><strong>Chưa hoàn thành yêu cầu</strong><p>{state.error}</p></div>}
      </div>
      <footer className="assistant-composer">
        {state.revisionOf && <p>Đang yêu cầu AI sinh lại toàn bộ code mới. <button type="button" onClick={() => state.setRevisionOf(null)}>Hủy</button></p>}
        <label htmlFor="assistant-input">Nhập câu hỏi hoặc yêu cầu sửa</label>
        <div><textarea ref={composer} id="assistant-input" rows={2} value={draft} onChange={(event) => setDraft(event.target.value)} onKeyDown={(event) => { if (event.key === 'Enter' && !event.shiftKey) { event.preventDefault(); void submit() } }} placeholder={state.revisionOf ? 'Mô tả điều cần sửa trong code mới…' : 'Hỏi về PAPI hoặc yêu cầu phân tích…'} /><button type="button" aria-label="Gửi yêu cầu" disabled={!draft.trim() || Boolean(state.busy)} onClick={() => void submit()}>↑</button></div>
        <small>Code do AI đề xuất. Hãy kiểm tra trước khi phê duyệt.</small>
      </footer>
    </section>}
    <button ref={launcher} type="button" className="assistant-launcher" aria-label="Mở Trợ lý AI" title="Hỏi Trợ lý AI" aria-expanded={state.mode === 'open'} onClick={open}>
      <svg aria-hidden="true" viewBox="0 0 24 24"><path d="M12 3a7 7 0 0 0-7 7v2.5A2.5 2.5 0 0 0 7.5 15H9v-5H6.5a5.5 5.5 0 0 1 11 0H15v5h1.5c.17 0 .34-.02.5-.05V16a3 3 0 0 1-3 3h-2v2h2a5 5 0 0 0 5-5v-1.05a2.5 2.5 0 0 0 1-1.95v-3a7 7 0 0 0-7-7Z" fill="currentColor"/><circle cx="10" cy="11.5" r="1" fill="currentColor"/><circle cx="14" cy="11.5" r="1" fill="currentColor"/></svg>
    </button>
  </div>
}
