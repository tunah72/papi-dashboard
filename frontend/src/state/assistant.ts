import { create } from 'zustand'
import { createJSONStorage, persist } from 'zustand/middleware'
import type { AssistantExecutionResponse, AssistantMessageResponse } from '../api/client'

export type UserTurn = { id: string; role: 'user'; text: string }
export type AssistantTurn = { id: string; role: 'assistant'; response: AssistantMessageResponse; superseded?: boolean; execution?: AssistantExecutionResponse }
export type ConversationTurn = UserTurn | AssistantTurn
export type AssistantMode = 'hidden' | 'minimized' | 'open'

type AssistantState = {
  mode: AssistantMode
  sessionId: string | null
  turns: ConversationTurn[]
  revisionOf: string | null
  busy: 'message' | 'execution' | null
  error: string | null
  setMode: (mode: AssistantMode) => void
  setSessionId: (sessionId: string) => void
  addUser: (text: string) => void
  addResponse: (response: AssistantMessageResponse) => void
  attachExecution: (proposalId: string, execution: AssistantExecutionResponse) => void
  setRevisionOf: (proposalId: string | null) => void
  setBusy: (busy: AssistantState['busy']) => void
  setError: (error: string | null) => void
  reset: () => void
}

const id = () => globalThis.crypto?.randomUUID?.() ?? `${Date.now()}-${Math.random()}`

export const useAssistantStore = create<AssistantState>()(persist((set) => ({
  mode: 'hidden', sessionId: null, turns: [], revisionOf: null, busy: null, error: null,
  setMode: (mode) => set({ mode }),
  setSessionId: (sessionId) => set({ sessionId }),
  addUser: (text) => set((state) => ({ turns: [...state.turns, { id: id(), role: 'user', text }] })),
  addResponse: (response) => set((state) => ({
    turns: [
      ...state.turns.map((turn) => turn.role === 'assistant' && turn.response.kind === 'proposal' && !turn.execution
        ? { ...turn, superseded: true } : turn),
      { id: id(), role: 'assistant', response },
    ],
  })),
  attachExecution: (proposalId, execution) => set((state) => ({ turns: state.turns.map((turn) =>
    turn.role === 'assistant' && turn.response.kind === 'proposal' && turn.response.proposalId === proposalId
      ? { ...turn, execution } : turn) })),
  setRevisionOf: (revisionOf) => set({ revisionOf }),
  setBusy: (busy) => set({ busy }),
  setError: (error) => set({ error }),
  reset: () => set({ sessionId: null, turns: [], revisionOf: null, busy: null, error: null, mode: 'open' }),
}), {
  name: 'papi.floating-assistant',
  storage: createJSONStorage(() => sessionStorage),
  partialize: (state) => ({ mode: state.mode, sessionId: state.sessionId, turns: state.turns, revisionOf: state.revisionOf }),
}))
