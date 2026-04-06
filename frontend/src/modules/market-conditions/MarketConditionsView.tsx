import PlotlyChart from '../../components/PlotlyChart'
import RefreshButton from '../../components/RefreshButton'
import { useMarketConditions } from './useMarketConditions'

/**
 * Market Conditions dashboard view.
 *
 * Fetches the 5-panel indicator grid from the backend and renders it
 * via PlotlyChart. Includes manual refresh and error handling.
 */
export default function MarketConditionsView() {
  const { data, isLoading, isFetching, isError, error, refetch, dataUpdatedAt } =
    useMarketConditions()

  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        height: '100%',
        background: 'var(--bb-bg-paper)',
      }}
    >
      {/* Toolbar */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          borderBottom: '1px solid var(--bb-grid)',
          flexShrink: 0,
        }}
      >
        <RefreshButton
          onClick={() => refetch()}
          loading={isFetching}
          lastUpdated={dataUpdatedAt}
        />
        {data && (
          <span
            style={{
              color: 'var(--bb-text-secondary)',
              fontFamily: 'var(--bb-font-mono)',
              fontSize: 'var(--bb-font-size-sm)',
              paddingRight: 'var(--bb-space-md)',
            }}
          >
            {data.symbol}
          </span>
        )}
      </div>

      {/* Chart area */}
      <div style={{ flex: 1, minHeight: 0 }}>
        {isError ? (
          <div
            data-testid="error-state"
            style={{
              height: '100%',
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              gap: 'var(--bb-space-md)',
              color: 'var(--bb-negative)',
              fontFamily: 'var(--bb-font-mono)',
            }}
          >
            <span>
              Error: {error instanceof Error ? error.message : 'Unknown error'}
            </span>
            <button
              onClick={() => refetch()}
              data-testid="retry-button"
              style={{
                background: 'var(--bb-primary)',
                color: 'var(--bb-bg-paper)',
                border: 'none',
                padding: 'var(--bb-space-sm) var(--bb-space-md)',
                fontFamily: 'var(--bb-font-mono)',
                cursor: 'pointer',
                borderRadius: '2px',
              }}
            >
              Retry
            </button>
          </div>
        ) : (
          <PlotlyChart figure={data?.figure} loading={isLoading} />
        )}
      </div>
    </div>
  )
}
