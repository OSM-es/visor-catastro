import Api from '$lib/api'

export async function handle({ event, resolve }) {
  event.locals.token = event.cookies.get('token') || ''
  event.locals.api = new Api(event.fetch)

  if (!event.url.pathname.startsWith('/api') && !event.locals.user) {
    event.locals.user = await event.locals.api.get('user')
  }
  
  return await resolve(event)
}
