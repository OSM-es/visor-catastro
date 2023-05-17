import { PUBLIC_API_URL } from '$env/static/public'

export async function load({ fetch, locals, url }) {
  if (!locals.user) {
    try {
      const resp = await fetch(PUBLIC_API_URL + '/user')
      if (resp.ok) {
        locals.user = await resp.json()
      }
    } catch (e) {
      console.log('Falla comunicación con backend')
      console.log(e)
    }
  }
  return { user: locals.user }
}
