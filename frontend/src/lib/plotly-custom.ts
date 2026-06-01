/**
 * Custom Plotly.js bundle — registers only the trace types we need.
 *
 * The full plotly.js bundle includes an `image` trace that depends on
 * Node.js streams (probe-image-size/sync), which crashes in the browser.
 * This custom bundle avoids that by importing only core + our 4 traces.
 *
 * Core includes: scatter
 * Registered here: bar, candlestick, surface
 */
import Plotly from 'plotly.js/lib/core'
// @ts-expect-error — plotly trace modules lack type declarations
import bar from 'plotly.js/lib/bar'
// @ts-expect-error — plotly trace modules lack type declarations
import candlestick from 'plotly.js/lib/candlestick'
// @ts-expect-error — plotly trace modules lack type declarations
import surface from 'plotly.js/lib/surface'

Plotly.register([bar, candlestick, surface])

export default Plotly
