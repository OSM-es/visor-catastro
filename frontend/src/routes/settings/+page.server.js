import { redirect } from '@sveltejs/kit'

export function load({ depends, locals }) {
  depends('data:user')
  depends('data:status')

  if (!locals.user) throw redirect(302, '/')

  return { status: locals.status || '--' }
}

export const actions = {
  save: async ({ locals, request }) => {
    const formData = await request.formData()
    const data = Object.fromEntries(formData)
    const result = await locals.api.post('user', data, locals.user.token)
    console.info(data.email)
    return {
      email: data.email,
      status: result.status,
    }
  }
}