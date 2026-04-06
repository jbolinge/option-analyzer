import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, it, expect, vi } from 'vitest'
import RefreshButton from '../../components/RefreshButton'

describe('RefreshButton', () => {
  it('renders refresh text', () => {
    render(<RefreshButton onClick={() => {}} />)
    expect(screen.getByTestId('refresh-button')).toHaveTextContent('Refresh')
  })

  it('calls onClick when clicked', async () => {
    const user = userEvent.setup()
    const onClick = vi.fn()
    render(<RefreshButton onClick={onClick} />)
    await user.click(screen.getByTestId('refresh-button'))
    expect(onClick).toHaveBeenCalledOnce()
  })

  it('shows loading state', () => {
    render(<RefreshButton onClick={() => {}} loading />)
    expect(screen.getByTestId('refresh-button')).toHaveTextContent('Loading...')
    expect(screen.getByTestId('refresh-button')).toBeDisabled()
  })

  it('does not call onClick when loading', async () => {
    const user = userEvent.setup()
    const onClick = vi.fn()
    render(<RefreshButton onClick={onClick} loading />)
    await user.click(screen.getByTestId('refresh-button'))
    expect(onClick).not.toHaveBeenCalled()
  })

  it('shows last updated timestamp', () => {
    const date = new Date(2026, 3, 5, 14, 30, 0)
    render(<RefreshButton onClick={() => {}} lastUpdated={date} />)
    expect(screen.getByTestId('last-updated')).toBeInTheDocument()
  })

  it('hides timestamp when not provided', () => {
    render(<RefreshButton onClick={() => {}} />)
    expect(screen.queryByTestId('last-updated')).not.toBeInTheDocument()
  })
})
