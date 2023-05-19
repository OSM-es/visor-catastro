import { redirect } from '@sveltejs/kit'

export function load({ depends, locals }) {
  depends('data:user')

  if (!locals.user) throw redirect(302, '/')
}

export const actions = {
  default: async ({ locals, request }) => {
    const token = locals.token
    const formData = await request.formData()
    const data = Object.fromEntries(formData)
    await locals.api.post('user', data, token)
  }
}