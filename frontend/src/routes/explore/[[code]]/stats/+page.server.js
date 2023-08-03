export async function load({ locals, fetch, params }) {
  const taskStatus = async () => {
    const url = `${locals.api.base}/stats/${params.code}/tasks`
    const resp = await fetch(url)  
    return await resp.json()
  }
  
  return {
    streamed: {
      taskStatus: taskStatus()
    }
  }
}
