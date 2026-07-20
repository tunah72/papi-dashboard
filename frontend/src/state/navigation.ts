import { create } from 'zustand'

type NavigationState = { desktopCollapsed: boolean; setDesktopCollapsed: (collapsed: boolean) => void }

const stored = (): boolean => {
  try { return localStorage.getItem('papi.sidebar.collapsed') === 'true' } catch { return false }
}

export const useNavigationStore = create<NavigationState>((set) => ({
  desktopCollapsed: stored(),
  setDesktopCollapsed: (desktopCollapsed) => {
    try { localStorage.setItem('papi.sidebar.collapsed', String(desktopCollapsed)) } catch { /* storage may be unavailable */ }
    set({ desktopCollapsed })
  },
}))
