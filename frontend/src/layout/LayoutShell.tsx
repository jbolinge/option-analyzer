import { useCallback, useState } from 'react'
import { Layout, type Model, type Action } from 'flexlayout-react'
import 'flexlayout-react/style/dark.css'
import '../theme/flexlayout-overrides.css'
import {
  createLayoutModel,
  createDefaultModel,
  persistLayout,
  clearPersistedLayout,
} from './layoutModel'
import { tabFactory } from './TabFactory'

/**
 * Main layout shell — wraps FlexLayout with Bloomberg theme and persistence.
 */
export default function LayoutShell() {
  const [model, setModel] = useState<Model>(() => createLayoutModel())

  const handleAction = useCallback((action: Action): Action | undefined => {
    return action
  }, [])

  const handleModelChange = useCallback((m: Model) => {
    persistLayout(m)
  }, [])

  const handleResetLayout = useCallback(() => {
    clearPersistedLayout()
    setModel(createDefaultModel())
  }, [])

  return (
    <div style={{ display: 'flex', flexDirection: 'column', width: '100%', height: '100%' }}>
      {/* Status bar */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: '0 var(--bb-space-md)',
          height: '24px',
          background: 'var(--bb-bg-surface)',
          borderBottom: '1px solid var(--bb-grid)',
          fontFamily: 'var(--bb-font-mono)',
          fontSize: 'var(--bb-font-size-xs)',
          flexShrink: 0,
        }}
      >
        <span style={{ color: 'var(--bb-primary)', fontWeight: 'bold' }}>
          OPTIONS ANALYZER
        </span>
        <button
          onClick={handleResetLayout}
          data-testid="reset-layout"
          style={{
            background: 'none',
            border: 'none',
            color: 'var(--bb-text-secondary)',
            fontFamily: 'var(--bb-font-mono)',
            fontSize: 'var(--bb-font-size-xs)',
            cursor: 'pointer',
            padding: '0 var(--bb-space-sm)',
          }}
        >
          Reset Layout
        </button>
      </div>

      {/* FlexLayout */}
      <div style={{ position: 'relative', flex: 1 }}>
        <Layout
          model={model}
          factory={tabFactory}
          onAction={handleAction}
          onModelChange={handleModelChange}
        />
      </div>
    </div>
  )
}
