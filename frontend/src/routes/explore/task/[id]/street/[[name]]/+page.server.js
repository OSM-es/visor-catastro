export const ssr = false


export async function load({ locals, params }) {
  let uri = `task/${params.id}/street/${params.name || ''}`
  const streets = await locals.api.get(uri)

  return streets
}

export const actions = {
  default: async ({ locals, request }) => {
    const formData = await request.formData()
    const data = Object.fromEntries(formData)
    const uri = `street/${data.mun_code}/${data.cat_name}`
    await locals.api.put(uri, data, locals.user.token)
  }
}