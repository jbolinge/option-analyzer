import type { ModuleDefinition } from './types'

/**
 * Registry for pluggable frontend modules.
 *
 * Modules self-register via their index.ts files. The layout shell's
 * TabFactory queries this registry to resolve component IDs to React
 * components.
 */
class ModuleRegistry {
  private modules = new Map<string, ModuleDefinition>()

  register(def: ModuleDefinition): void {
    this.modules.set(def.id, def)
  }

  get(id: string): ModuleDefinition | undefined {
    return this.modules.get(id)
  }

  getAll(): ModuleDefinition[] {
    return Array.from(this.modules.values())
  }

  has(id: string): boolean {
    return this.modules.has(id)
  }
}

/** Singleton module registry — import and use across the app. */
export const moduleRegistry = new ModuleRegistry()
