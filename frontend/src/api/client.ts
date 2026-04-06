import type { DashboardResponse, PanelResponse, HealthResponse } from './types'

const BASE_URL = '/api'

async function fetchJson<T>(path: string): Promise<T> {
  const response = await fetch(`${BASE_URL}${path}`)
  if (!response.ok) {
    throw new Error(`API error: ${response.status} ${response.statusText}`)
  }
  return response.json()
}

export function fetchHealth(): Promise<HealthResponse> {
  return fetchJson('/health')
}

export function fetchDashboard(): Promise<DashboardResponse> {
  return fetchJson('/market-conditions/dashboard')
}

export function fetchPanel(panelName: string): Promise<PanelResponse> {
  return fetchJson(`/market-conditions/panels/${panelName}`)
}
