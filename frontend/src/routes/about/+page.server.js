export function load({ fetch, locals }) {
  const fetchStats = async () => {
    const resp = await fetch(locals.api.base + '/stats')
    return await resp.json()
  }
  
  return {
    streamed: {
      stats: fetchStats()
    }
  }
}
