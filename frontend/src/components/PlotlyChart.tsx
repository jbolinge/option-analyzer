import { useRef, useEffect, useCallback } from 'react'
import createPlotlyComponent from 'react-plotly.js/factory'
import Plotly from '../lib/plotly-custom'
import type { PlotlyFigure } from '../api/types'

// Handle CJS/ESM interop — factory may be on .default or the import itself
const createPlot =
  typeof createPlotlyComponent === 'function'
    ? createPlotlyComponent
    : (createPlotlyComponent as any).default
const Plot = createPlot(Plotly)

interface PlotlyChartProps {
  figure: PlotlyFigure | undefined
  loading?: boolean
}

/**
 * Reusable Plotly chart wrapper.
 *
 * Renders a Plotly figure from backend JSON. Handles loading state,
 * responsive sizing, and FlexLayout panel resizes.
 */
export default function PlotlyChart({ figure, loading }: PlotlyChartProps) {
  const containerRef = useRef<HTMLDivElement>(null)

  // Resize plotly chart when container size changes
  const handleResize = useCallback(() => {
    const container = containerRef.current
    if (!container) return
    const plotDiv = container.querySelector('.js-plotly-plot') as HTMLElement | null
    if (plotDiv) {
      Plotly.Plots.resize(plotDiv)
    }
  }, [])

  useEffect(() => {
    const container = containerRef.current
    if (!container) return

    const observer = new ResizeObserver(handleResize)
    observer.observe(container)
    return () => observer.disconnect()
  }, [handleResize])

  if (loading || !figure) {
    return (
      <div
        style={{
          height: '100%',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: 'var(--bb-text-secondary)',
          fontFamily: 'var(--bb-font-mono)',
        }}
      >
        {loading ? 'Loading dashboard...' : 'No data'}
      </div>
    )
  }

  return (
    <div ref={containerRef} style={{ width: '100%', height: '100%' }}>
      <Plot
        data={figure.data as Plotly.Data[]}
        layout={{
          ...figure.layout,
          autosize: true,
        } as Partial<Plotly.Layout>}
        config={{
          responsive: true,
          displayModeBar: true,
          displaylogo: false,
          modeBarButtonsToRemove: [
            'sendDataToCloud',
            'toImage',
            'select2d',
            'lasso2d',
          ] as Plotly.ModeBarDefaultButtons[],
        }}
        useResizeHandler
        style={{ width: '100%', height: '100%' }}
      />
    </div>
  )
}
