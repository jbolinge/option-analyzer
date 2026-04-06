import { Suspense } from 'react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import './theme/bloomberg.css'
import './theme/global.css'

// Import all module registrations (side-effect imports)
import './modules/market-conditions'

import { moduleRegistry } from './modules/registry'
import LayoutShell from './layout/LayoutShell'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: Infinity, // Manual refresh only
      retry: 1,
    },
  },
})

/**
 * Detect if this window was opened as a pop-out.
 *
 * FlexLayout pop-out windows load the same SPA URL with a special
 * query parameter. When detected, we render only the specified module
 * instead of the full layout shell.
 */
function getPopoutModuleId(): string | null {
  const params = new URLSearchParams(window.location.search)
  return params.get('popout')
}

function PopoutView({ moduleId }: { moduleId: string }) {
  const moduleDef = moduleRegistry.get(moduleId)
  if (!moduleDef) {
    return (
      <div style={{ padding: 16, color: 'var(--bb-negative)' }}>
        Unknown module: {moduleId}
      </div>
    )
  }
  const Component = moduleDef.component
  return (
    <Suspense fallback={<div style={{ padding: 16, color: 'var(--bb-text-secondary)' }}>Loading...</div>}>
      <div style={{ width: '100%', height: '100%' }}>
        <Component />
      </div>
    </Suspense>
  )
}

function App() {
  const popoutModuleId = getPopoutModuleId()

  return (
    <QueryClientProvider client={queryClient}>
      {popoutModuleId ? (
        <PopoutView moduleId={popoutModuleId} />
      ) : (
        <LayoutShell />
      )}
    </QueryClientProvider>
  )
}

export default App
