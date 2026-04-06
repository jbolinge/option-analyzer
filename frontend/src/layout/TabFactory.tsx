import { Suspense } from 'react'
import type { TabNode } from 'flexlayout-react'
import { moduleRegistry } from '../modules/registry'

/**
 * FlexLayout factory function — resolves tab component IDs to React elements.
 *
 * Looks up the component name in the module registry and renders the
 * associated lazy-loaded component wrapped in Suspense.
 */
export function tabFactory(node: TabNode): React.ReactNode {
  const componentId = node.getComponent()
  if (!componentId) return <UnknownModule name="(no component)" />

  const moduleDef = moduleRegistry.get(componentId)
  if (!moduleDef) return <UnknownModule name={componentId} />

  const Component = moduleDef.component
  return (
    <Suspense fallback={<LoadingFallback />}>
      <Component />
    </Suspense>
  )
}

function LoadingFallback() {
  return (
    <div style={{ padding: 'var(--bb-space-lg)', color: 'var(--bb-text-secondary)' }}>
      Loading...
    </div>
  )
}

function UnknownModule({ name }: { name: string }) {
  return (
    <div
      style={{
        padding: 'var(--bb-space-lg)',
        color: 'var(--bb-negative)',
        fontFamily: 'var(--bb-font-mono)',
      }}
    >
      Unknown module: {name}
    </div>
  )
}
