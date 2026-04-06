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

// Must import App after mocks are set up
import App from '../App'

describe('App', () => {
  it('renders without crashing', () => {
    render(<App />)
    // FlexLayout mock renders
    expect(screen.getByTestId('flexlayout')).toBeInTheDocument()
  })

  it('renders the layout shell', () => {
    render(<App />)
    expect(screen.getByText('FlexLayout Mock')).toBeInTheDocument()
  })
})
