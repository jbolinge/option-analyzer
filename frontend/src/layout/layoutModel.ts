import { Model, type IJsonModel } from 'flexlayout-react'

const LAYOUT_STORAGE_KEY = 'options-analyzer-layout'
const LAYOUT_VERSION = 1

/**
 * Default layout JSON: single tabset with Market Conditions tab.
 *
 * New modules added to the layout will appear as additional tabs.
 * Users can drag, split, and rearrange — the modified layout
 * persists to localStorage.
 */
const DEFAULT_LAYOUT: IJsonModel = {
  global: {
    tabEnablePopout: true,
    tabSetEnableMaximize: true,
    tabSetEnableTabStrip: true,
    tabSetMinWidth: 200,
    tabSetMinHeight: 200,
    borderSize: 30,
    splitterSize: 4,
  },
  borders: [],
  layout: {
    type: 'row',
    weight: 100,
    children: [
      {
        type: 'tabset',
        weight: 100,
        children: [
          {
            type: 'tab',
            name: 'Market Conditions',
            component: 'market-conditions',
          },
        ],
      },
    ],
  },
}

/** Create a FlexLayout Model, restoring from localStorage if available. */
export function createLayoutModel(): Model {
  const saved = loadPersistedLayout()
  if (saved) {
    try {
      return Model.fromJson(saved)
    } catch {
      // Corrupted or incompatible — fall back to default
      clearPersistedLayout()
    }
  }
  return Model.fromJson(DEFAULT_LAYOUT)
}

/** Create a fresh default model (ignoring localStorage). */
export function createDefaultModel(): Model {
  return Model.fromJson(DEFAULT_LAYOUT)
}

/** Persist the current layout JSON to localStorage. */
export function persistLayout(model: Model): void {
  try {
    const json = model.toJson()
    const envelope = { version: LAYOUT_VERSION, layout: json }
    localStorage.setItem(LAYOUT_STORAGE_KEY, JSON.stringify(envelope))
  } catch {
    // localStorage full or unavailable — silently ignore
  }
}

/** Load persisted layout from localStorage, or null. */
function loadPersistedLayout(): IJsonModel | null {
  try {
    const raw = localStorage.getItem(LAYOUT_STORAGE_KEY)
    if (!raw) return null
    const envelope = JSON.parse(raw)
    if (envelope.version !== LAYOUT_VERSION) return null
    return envelope.layout as IJsonModel
  } catch {
    return null
  }
}

/** Clear persisted layout (used for reset or corruption recovery). */
export function clearPersistedLayout(): void {
  localStorage.removeItem(LAYOUT_STORAGE_KEY)
}
