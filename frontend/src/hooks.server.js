import { PUBLIC_API_URL } from '$env/static/public'
import { redirect } from '@sveltejs/kit'

export async function handle({ event, resolve }) {
  event.locals.token = event.cookies.get('token') || ''
  if (!event.url.pathname.startsWith('/api') && !event.locals.user) {
    try {
      const resp = await event.fetch(PUBLIC_API_URL + '/user')
      if (resp.ok) {
        event.locals.user = await resp.json()
        console.info(event.locals.user)
      }
    } catch (e) {
      console.log('Falla comunicación con backend')
      console.log(e)
    }
  }
  const response = await resolve(event)
  if (event.locals.loginRequired && !event.locals.user) {
    throw redirect(302, '/')
  }
  console.info('----------')
  return response
}
