export async function load({ locals, fetch, params }) {
  const resp = await fetch(`${locals.api.base}/municipality/${params.code}`)
  const municipality = await resp.json()

  const fetchData = async (code, target) => {
    const url = `${locals.api.base}/stats/${code}/${target}`
    const resp = await fetch(url)  
    return await resp.json()
  }

  return {
    municipality,
    streamed: {
      taskStatus: fetchData(params.code, 'tasks'),
      contributors: fetchData(params.code, 'contributors'),
      timeStats: fetchData(params.code, 'timestats'),
    }
  }
}
