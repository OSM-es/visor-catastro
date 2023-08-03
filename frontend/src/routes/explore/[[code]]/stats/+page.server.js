export async function load({ locals, fetch, params }) {
  const url = `${locals.api.base}/stats/${params.code}/tasks`
  const response = await fetch(url)
  
  return {
    streamed: {
      taskStatus: response.json()
    }
  }
}
