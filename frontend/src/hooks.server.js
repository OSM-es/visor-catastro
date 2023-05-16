import { PUBLIC_API_URL } from '$env/static/public'

export async function handle({ event, resolve }) {
  if (!event.locals.user) {
    try {
      // const resp = await event.fetch(PUBLIC_API_URL + '/user')
      // https://github.com/sveltejs/kit/issues/8239
      const resp = await fetch(PUBLIC_API_URL + '/user', {
        headers: {
          cookie: 'session=' + event.cookies.get('session')
        }
      })
      if (resp.ok) {
        const user = await resp.json()
        event.locals.user = user
      }
    } catch (e) {
      console.log('Falla comunicación con backend')
      console.log(e)
    }
  }
  const token = event.cookies.get('token') || ''
  const response = await resolve(event)
  response.headers.set('Authorization', 'Bearer ' + token)
  return response
}
