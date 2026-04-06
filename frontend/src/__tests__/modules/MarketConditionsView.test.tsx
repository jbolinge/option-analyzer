import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'

// Mock Plotly components
vi.mock('react-plotly.js/factory', () => ({
  default: () =>
    function MockPlot() {
      return <div data-testid="plotly-chart">Chart</div>
    },
}))
vi.mock('plotly.js-cartesian-dist', () => ({
  default: { Plots: { resize: vi.fn() } },
}))

// Mock the API client
vi.mock('../../api/client', () => ({
  fetchDashboard: vi.fn(),
}))

import { fetchDashboard } from '../../api/client'
import MarketConditionsView from '../../modules/market-conditions/MarketConditionsView'

const mockFetchDashboard = vi.mocked(fetchDashboard)

function renderWithQuery(ui: React.ReactElement) {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
    },
  })
  return render(
    <QueryClientProvider client={queryClient}>{ui}</QueryClientProvider>,
  )
}

const MOCK_RESPONSE = {
  figure: {
    data: [{ type: 'scatter', x: [1], y: [2] }],
    layout: { title: 'Test' },
  },
  computed_at: '2026-04-05T12:00:00Z',
  symbol: 'SPX',
}

describe('MarketConditionsView', () => {
  beforeEach(() => {
    mockFetchDashboard.mockReset()
  })

  it('shows loading state initially', () => {
    mockFetchDashboard.mockReturnValue(new Promise(() => {}))
    renderWithQuery(<MarketConditionsView />)
    expect(screen.getByText('Loading dashboard...')).toBeInTheDocument()
  })

  it('renders chart after successful fetch', async () => {
    mockFetchDashboard.mockResolvedValue(MOCK_RESPONSE)
    renderWithQuery(<MarketConditionsView />)
    await waitFor(() => {
      expect(screen.getByTestId('plotly-chart')).toBeInTheDocument()
    })
  })

  it('displays symbol after fetch', async () => {
    mockFetchDashboard.mockResolvedValue(MOCK_RESPONSE)
    renderWithQuery(<MarketConditionsView />)
    await waitFor(() => {
      expect(screen.getByText('SPX')).toBeInTheDocument()
    })
  })

  it('shows error state on fetch failure', async () => {
    mockFetchDashboard.mockRejectedValue(new Error('Network error'))
    renderWithQuery(<MarketConditionsView />)
    await waitFor(() => {
      expect(screen.getByTestId('error-state')).toBeInTheDocument()
      expect(screen.getByText(/Network error/)).toBeInTheDocument()
    })
  })

  it('shows retry button on error', async () => {
    mockFetchDashboard.mockRejectedValue(new Error('fail'))
    renderWithQuery(<MarketConditionsView />)
    await waitFor(() => {
      expect(screen.getByTestId('retry-button')).toBeInTheDocument()
    })
  })

  it('has a refresh button', () => {
    mockFetchDashboard.mockReturnValue(new Promise(() => {}))
    renderWithQuery(<MarketConditionsView />)
    expect(screen.getByTestId('refresh-button')).toBeInTheDocument()
  })

  it('refetches when refresh button is clicked', async () => {
    const user = userEvent.setup()
    mockFetchDashboard.mockResolvedValue(MOCK_RESPONSE)
    renderWithQuery(<MarketConditionsView />)

    await waitFor(() => {
      expect(screen.getByTestId('plotly-chart')).toBeInTheDocument()
    })

    const callsBefore = mockFetchDashboard.mock.calls.length

    // Click refresh
    await user.click(screen.getByTestId('refresh-button'))

    await waitFor(() => {
      expect(mockFetchDashboard.mock.calls.length).toBeGreaterThan(callsBefore)
    })
  })
})
