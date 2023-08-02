export async function load({ fetch, locals }) {
  const resp = await fetch(locals.api.base + '/stats')
  
  return {
    streamed: {
      stats: resp.json()
    }
  }
}