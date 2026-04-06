import { describe, it, expect, beforeEach } from 'vitest'
import { lazy } from 'react'
import type { ModuleDefinition } from '../../modules/types'

// Create a fresh registry for each test (don't use singleton)
class TestModuleRegistry {
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

const makeDef = (id: string, name: string): ModuleDefinition => ({
  id,
  name,
  component: lazy(() => Promise.resolve({ default: () => null })),
})

describe('ModuleRegistry', () => {
  let registry: TestModuleRegistry

  beforeEach(() => {
    registry = new TestModuleRegistry()
  })

  it('registers and retrieves a module', () => {
    const def = makeDef('test-mod', 'Test Module')
    registry.register(def)
    expect(registry.get('test-mod')).toBe(def)
  })

  it('returns undefined for unknown module', () => {
    expect(registry.get('nonexistent')).toBeUndefined()
  })

  it('has() returns true for registered, false for unknown', () => {
    registry.register(makeDef('foo', 'Foo'))
    expect(registry.has('foo')).toBe(true)
    expect(registry.has('bar')).toBe(false)
  })

  it('getAll() returns all registered modules', () => {
    registry.register(makeDef('a', 'Module A'))
    registry.register(makeDef('b', 'Module B'))
    const all = registry.getAll()
    expect(all).toHaveLength(2)
    expect(all.map((m) => m.id)).toEqual(['a', 'b'])
  })

  it('getAll() returns empty array when no modules registered', () => {
    expect(registry.getAll()).toEqual([])
  })

  it('overwrites module with same id', () => {
    registry.register(makeDef('dup', 'First'))
    registry.register(makeDef('dup', 'Second'))
    expect(registry.get('dup')?.name).toBe('Second')
    expect(registry.getAll()).toHaveLength(1)
  })
})
