import { render, screen } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'

// Mock flexlayout-react since it requires DOM measurements
vi.mock('flexlayout-react', () => ({
  Layout: (_props: any) => (
    <div data-testid="flexlayout">FlexLayout Mock</div>
  ),
  Model: {
    fromJson: (json: any) => ({
      toJson: () => json,
    }),
  },
}))

import App from '../App'

describe('App', () => {
  it('renders the layout shell in normal mode', () => {
    render(<App />)
    // LayoutShell renders the status bar with app title
    expect(screen.getByText('OPTIONS ANALYZER')).toBeInTheDocument()
  })

  it('renders FlexLayout', () => {
    render(<App />)
    expect(screen.getByTestId('flexlayout')).toBeInTheDocument()
  })

  it('shows reset layout button', () => {
    render(<App />)
    expect(screen.getByTestId('reset-layout')).toBeInTheDocument()
  })
})
