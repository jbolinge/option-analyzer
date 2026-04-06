import { useEffect, useState } from 'react'

interface HealthResponse {
  status: string
  api_version: string
}

function App() {
  const [health, setHealth] = useState<HealthResponse | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetch('/api/health')
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`)
        return res.json()
      })
      .then(setHealth)
      .catch((err) => setError(err.message))
  }, [])

  return (
    <div data-testid="app-root">
      <h1>options-analyzer</h1>
      {error && <p data-testid="error">API Error: {error}</p>}
      {health && (
        <p data-testid="health-status">
          API: {health.status} (v{health.api_version})
        </p>
      )}
      {!health && !error && <p data-testid="loading">Connecting...</p>}
    </div>
  )
}

export default App
