export const ssr = false

export async function load({ locals }) {
  return {api: locals.api.base}
}
