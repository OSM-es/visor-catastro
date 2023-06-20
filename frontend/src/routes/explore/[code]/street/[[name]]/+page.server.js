export const ssr = false

export async function load({ locals, params, url }) {
  let uri = `streets/${params.code}`
  if (params.name) uri = `${uri}?name=${params.name}`
  const streets = await locals.api.get(uri)
  return streets
}

export const actions = {
  default: async ({ locals, request }) => {
    console.info(locals)
    console.info(request)
  }
}