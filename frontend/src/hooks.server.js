import { PUBLIC_API_URL } from '$env/static/public'
import { redirect } from '@sveltejs/kit'

export async function handle({ event, resolve }) {
  const response = await resolve(event)
  if (!event.locals.user) {
    if (event.url.pathname.startsWith('/settings')) {
      throw redirect(302, '/')
    }
  }
  if (!event.url.pathname.startsWith('/api')) {
    const token = event.cookies.get('token') || ''
    response.headers.set('Authorization', 'Bearer ' + token)
  }
  return response
}
