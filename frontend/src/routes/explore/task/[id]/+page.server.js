export const ssr = false

export async function load({ params, locals }) {
  const task = await locals.api.get(`task/${params.id}`)

  return { task }
}

export const actions = {
  task: async ({ locals, params, request }) => {
		if (!locals.user) throw error(401)
    
    const formData = await request.formData()
    const data = Object.fromEntries(formData)
    
    const result = await locals.api.put(
      `task/${params.id}`, data, locals.user.token
    )
  },
  fixme: (async ({ locals, request }) => {
		if (!locals.user) throw error(401)

    const formData = await request.formData()
    const data = Object.fromEntries(formData)

    const result = await locals.api.put(
      `fixme/${data.id}`, data, locals.user.token
    )
  }),
}
