import { useCallback, useRef } from 'react'
import { Layout, type Model, type Action } from 'flexlayout-react'
import 'flexlayout-react/style/dark.css'
import '../theme/flexlayout-overrides.css'
import { createLayoutModel, persistLayout } from './layoutModel'
import { tabFactory } from './TabFactory'

/**
 * Main layout shell — wraps FlexLayout with Bloomberg theme and persistence.
 *
 * The layout model is created once (from localStorage or default) and
 * persisted on every change. Tabs are resolved via the module registry's
 * TabFactory.
 */
export default function LayoutShell() {
  const modelRef = useRef<Model>(createLayoutModel())

  const handleAction = useCallback((action: Action): Action | undefined => {
    return action
  }, [])

  const handleModelChange = useCallback((model: Model) => {
    persistLayout(model)
  }, [])

  return (
    <div style={{ position: 'relative', width: '100%', height: '100%' }}>
      <Layout
        model={modelRef.current}
        factory={tabFactory}
        onAction={handleAction}
        onModelChange={handleModelChange}
      />
    </div>
  )
}
