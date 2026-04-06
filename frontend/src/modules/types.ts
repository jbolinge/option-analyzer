import type { ComponentType, LazyExoticComponent } from 'react'

/**
 * Definition for a pluggable frontend module (view).
 *
 * Each module self-registers via the registry. The layout shell
 * resolves module IDs to React components through the TabFactory.
 */
export interface ModuleDefinition {
  /** Unique identifier used in layout model JSON (e.g. "market-conditions") */
  id: string
  /** Display name shown in tab headers */
  name: string
  /** Lazy-loaded React component */
  component: LazyExoticComponent<ComponentType>
  /** Optional description for tooltips or menus */
  description?: string
}
