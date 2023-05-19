import Api from '$lib/api'
import { redirect } from '@sveltejs/kit'

export async function handle({ event, resolve }) {
  event.locals.token = event.cookies.get('token') || ''
  event.locals.api = new Api(event.fetch)

  if (!event.url.pathname.startsWith('/api') && !event.locals.user) {
    event.locals.user = await event.locals.api.get('user')
  }
  
  const response = await resolve(event)
  
  if (event.locals.loginRequired && !event.locals.user) {
    throw redirect(302, '/')
  }
  
  return response
}
