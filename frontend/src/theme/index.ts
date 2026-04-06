/**
 * Bloomberg theme constants for TypeScript usage.
 *
 * Mirrors src/options_analyzer/visualization/theme.py PALETTE.
 * Use CSS custom properties (--bb-*) in styles; use these constants
 * only when JS needs direct color values (e.g., Plotly config overrides).
 */

export const PALETTE = {
  primary: '#ff6600',
  secondary: '#00cccc',
  tertiary: '#cc00cc',
  positive: '#00cc66',
  negative: '#cc3333',
  neutral: '#888888',
} as const

export const BACKGROUNDS = {
  paper: '#000000',
  plot: '#1a1a2e',
  surface: '#0d0d1a',
  panel: '#111122',
} as const

export const TEXT = {
  primary: '#e0e0e0',
  secondary: '#888888',
  accent: '#ff6600',
  muted: '#555555',
} as const

export const GRID_COLOR = '#2d2d44'

export const FONT_FAMILY = "Consolas, Monaco, 'Courier New', monospace"
