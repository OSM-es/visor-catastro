import { redirect } from '@sveltejs/kit'

export function load({ depends, locals }) {
  depends('data:user')

  if (!locals.user) throw redirect(302, '/')
}

export const actions = {
  save: async ({ locals, request }) => {
    const formData = await request.formData()
    const data = Object.fromEntries(formData)
    const result = await locals.api.put('user', data, locals.user.token)
    return result
  }
}