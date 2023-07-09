import { parseAcceptLanguage } from 'intl-parse-accept-language'
import decode from '$lib/flaskSession'
import Api from '$lib/api'

export async function handle({ event, resolve }) {
  const { locals, request } = event

  const session = await decode(event.cookies.get('session'))
  locals.user = session.user || null
  locals.api = new Api(event)
  
  const locales = parseAcceptLanguage(event.request.headers.get('accept-language') || '')
  locals.locale = locales.length ? locales[0].split('-', 1)[0] : ''

  return await resolve(event)
}
