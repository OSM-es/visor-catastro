export async function load({ locals, fetch, params }) {
  const resp = await fetch(`${locals.api.base}/municipality/${params.code}`)
  const municipality = await resp.json()

  const taskStatus = async () => {
    const url = `${locals.api.base}/stats/${params.code}/tasks`
    const resp = await fetch(url)  
    return await resp.json()
  }
  
  return {
    municipality,
    streamed: {
      taskStatus: taskStatus()
    }
  }
}
