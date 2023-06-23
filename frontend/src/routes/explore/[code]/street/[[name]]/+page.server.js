export const ssr = false


export async function load({ locals, params, url }) {
  console.info('load')
  let uri = `streets/${params.code}`
  if (params.name) uri = `${uri}?name=${params.name}`
  const streets = await locals.api.get(uri)

  return streets
}

export const actions = {
  default: async ({ locals, request }) => {
    const formData = await request.formData()
    const data = Object.fromEntries(formData)
    const uri = `street/${data.mun_code}/${data.cat_name}`
    const result = await locals.api.put(uri, data, locals.user.token)
  }
}