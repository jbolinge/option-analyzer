import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import './theme/bloomberg.css'
import './theme/global.css'

// Import all module registrations (side-effect imports)
import './modules/market-conditions'

import LayoutShell from './layout/LayoutShell'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: Infinity, // Manual refresh only
      retry: 1,
    },
  },
})

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <LayoutShell />
    </QueryClientProvider>
  )
}

export default App
