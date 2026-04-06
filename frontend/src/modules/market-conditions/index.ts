import { lazy } from 'react'
import { moduleRegistry } from '../registry'

moduleRegistry.register({
  id: 'market-conditions',
  name: 'Market Conditions',
  component: lazy(() => import('./MarketConditionsView')),
  description: 'SPX market conditions dashboard with EMA cloud, DSTFS, IVTS, and Borg indicators',
})
