import decode from '$lib/flaskSession'
import Api from '$lib/api'

export async function handle({ event, resolve }) {
  const session = await decode(event.cookies.get('session'))
  event.locals.user = session.user || null
  event.locals.api = new Api(event)

  return await resolve(event)
}
