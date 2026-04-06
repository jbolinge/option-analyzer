/** Plotly figure JSON as returned by fig.to_plotly_json() */
export interface PlotlyFigure {
  data: Record<string, unknown>[]
  layout: Record<string, unknown>
}

/** Response from GET /api/market-conditions/dashboard */
export interface DashboardResponse {
  figure: PlotlyFigure
  computed_at: string
  symbol: string
}

/** Response from GET /api/market-conditions/panels/{name} */
export interface PanelResponse {
  figure: PlotlyFigure
  computed_at: string
  symbol: string
  panel: string
}

/** Response from GET /api/health */
export interface HealthResponse {
  status: string
  api_version: string
}
