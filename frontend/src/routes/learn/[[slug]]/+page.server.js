export async function load({ depends, locals }) {
  return({locale: locals.locale})
}

export const actions = {
  default: async ({ locals, request }) => {
    const formData = await request.formData()
    const data = Object.fromEntries(formData)
    await locals.api.post('user', data, locals.user.token)
  }
}
