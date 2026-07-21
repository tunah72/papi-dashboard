declare module 'plotly.js/lib/core' {
  const Plotly: typeof import('plotly.js')
  export default Plotly
}

declare module 'plotly.js/lib/sankey' {
  const sankey: Parameters<typeof import('plotly.js').register>[0]
  export default sankey
}
