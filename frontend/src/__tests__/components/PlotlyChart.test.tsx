import { render, screen } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'

// Mock react-plotly.js factory and custom plotly bundle
vi.mock('react-plotly.js/factory', () => ({
  default: () => {
    return function MockPlot(props: any) {
      return (
        <div data-testid="plotly-chart" data-traces={props.data?.length ?? 0}>
          Plotly Chart Mock
        </div>
      )
    }
  },
}))

vi.mock('../../lib/plotly-custom', () => ({
  default: { Plots: { resize: vi.fn() } },
}))

import PlotlyChart from '../../components/PlotlyChart'

const MOCK_FIGURE = {
  data: [
    { type: 'scatter', x: [1, 2, 3], y: [4, 5, 6] },
    { type: 'bar', x: [1, 2, 3], y: [7, 8, 9] },
  ],
  layout: { title: 'Test Chart' },
}

describe('PlotlyChart', () => {
  it('renders loading state when loading is true', () => {
    render(<PlotlyChart figure={undefined} loading />)
    expect(screen.getByText('Loading dashboard...')).toBeInTheDocument()
  })

  it('renders "No data" when figure is undefined and not loading', () => {
    render(<PlotlyChart figure={undefined} />)
    expect(screen.getByText('No data')).toBeInTheDocument()
  })

  it('renders Plotly chart when figure is provided', () => {
    render(<PlotlyChart figure={MOCK_FIGURE} />)
    expect(screen.getByTestId('plotly-chart')).toBeInTheDocument()
  })

  it('passes correct number of traces to Plot', () => {
    render(<PlotlyChart figure={MOCK_FIGURE} />)
    const chart = screen.getByTestId('plotly-chart')
    expect(chart.getAttribute('data-traces')).toBe('2')
  })
})
