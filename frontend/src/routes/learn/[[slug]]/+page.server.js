export const actions = {
  default: async ({ locals, request }) => {
    const formData = await request.formData()
    const data = Object.fromEntries(formData)
    console.info(data)
  }
}
