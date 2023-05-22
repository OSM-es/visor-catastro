export const ssr = false

export async function load({ params, locals }) {
  const task = await locals.api.get(`task/${params.id}`)

  return { task }
}