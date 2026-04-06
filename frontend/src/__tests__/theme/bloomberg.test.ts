import { describe, it, expect } from 'vitest'
import { PALETTE, BACKGROUNDS, TEXT, GRID_COLOR, FONT_FAMILY } from '../../theme'

describe('Bloomberg theme constants', () => {
  it('exports core palette colors', () => {
    expect(PALETTE.primary).toBe('#ff6600')
    expect(PALETTE.secondary).toBe('#00cccc')
    expect(PALETTE.tertiary).toBe('#cc00cc')
    expect(PALETTE.positive).toBe('#00cc66')
    expect(PALETTE.negative).toBe('#cc3333')
    expect(PALETTE.neutral).toBe('#888888')
  })

  it('exports background colors', () => {
    expect(BACKGROUNDS.paper).toBe('#000000')
    expect(BACKGROUNDS.plot).toBe('#1a1a2e')
    expect(BACKGROUNDS.surface).toBe('#0d0d1a')
    expect(BACKGROUNDS.panel).toBe('#111122')
  })

  it('exports text colors', () => {
    expect(TEXT.primary).toBe('#e0e0e0')
    expect(TEXT.secondary).toBe('#888888')
    expect(TEXT.accent).toBe('#ff6600')
  })

  it('exports grid color', () => {
    expect(GRID_COLOR).toBe('#2d2d44')
  })

  it('exports monospace font family', () => {
    expect(FONT_FAMILY).toContain('Consolas')
    expect(FONT_FAMILY).toContain('monospace')
  })

  it('palette values match theme.py exactly', () => {
    // Cross-reference: theme.py PALETTE dict
    const expectedPalette: Record<string, string> = {
      primary: '#ff6600',
      secondary: '#00cccc',
      tertiary: '#cc00cc',
      positive: '#00cc66',
      negative: '#cc3333',
      neutral: '#888888',
    }
    for (const [key, value] of Object.entries(expectedPalette)) {
      expect(PALETTE[key as keyof typeof PALETTE]).toBe(value)
    }
  })
})
