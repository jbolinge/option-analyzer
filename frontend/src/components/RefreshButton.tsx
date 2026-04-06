import { useCallback } from 'react'

interface RefreshButtonProps {
  onClick: () => void
  loading?: boolean
  lastUpdated?: Date | null
}

/**
 * Bloomberg-styled refresh button with loading spinner and timestamp.
 */
export default function RefreshButton({
  onClick,
  loading,
  lastUpdated,
}: RefreshButtonProps) {
  const handleClick = useCallback(() => {
    if (!loading) onClick()
  }, [loading, onClick])

  return (
    <div
      style={{
        display: 'flex',
        alignItems: 'center',
        gap: 'var(--bb-space-md)',
        padding: 'var(--bb-space-sm) var(--bb-space-md)',
        fontFamily: 'var(--bb-font-mono)',
        fontSize: 'var(--bb-font-size-sm)',
      }}
    >
      <button
        onClick={handleClick}
        disabled={loading}
        data-testid="refresh-button"
        style={{
          background: loading ? 'var(--bb-grid)' : 'var(--bb-primary)',
          color: loading ? 'var(--bb-text-secondary)' : 'var(--bb-bg-paper)',
          border: 'none',
          padding: 'var(--bb-space-sm) var(--bb-space-md)',
          fontFamily: 'var(--bb-font-mono)',
          fontSize: 'var(--bb-font-size-sm)',
          cursor: loading ? 'wait' : 'pointer',
          borderRadius: '2px',
        }}
      >
        {loading ? 'Loading...' : 'Refresh'}
      </button>
      {lastUpdated && (
        <span
          data-testid="last-updated"
          style={{ color: 'var(--bb-text-secondary)' }}
        >
          {lastUpdated.toLocaleTimeString()}
        </span>
      )}
    </div>
  )
}
