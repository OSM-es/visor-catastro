import { redirect } from '@sveltejs/kit'

export async function handle({ event, resolve }) {
  event.locals.token = event.cookies.get('token') || ''
  const response = await resolve(event)
  if (event.locals.loginRequired && !event.locals.user) {
    throw redirect(302, '/')
  }
  return response
}
