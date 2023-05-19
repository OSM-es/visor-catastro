export async function load({ locals }) {
  locals.loginRequired = true
}

export const actions = {
  default: async ({ locals, request }) => {
    const token = locals.token
    const formData = await request.formData()
    const data = Object.fromEntries(formData)
    await locals.api.post('user', data, token)
  }
}