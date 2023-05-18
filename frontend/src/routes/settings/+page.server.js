import { PUBLIC_API_URL } from '$env/static/public'

export async function load({ locals }) {
  locals.loginRequired = true

  return { status: locals.status || ''}
}

export const actions = {
  default: async (event) => {
    const token = event.locals.token
    console.info('token', token)
    const data = await event.request.formData()
    const resp = await event.fetch(PUBLIC_API_URL + '/user', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: 'Bearer ' + token
      },
      body: JSON.stringify(Object.fromEntries(data))
    })
    event.locals.status = await resp.text()
  }
}