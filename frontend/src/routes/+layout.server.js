export async function load({ depends, locals }) {
  depends('data:user')
  depends('data:locale')

  return { 
    user: locals.user,
    api: locals.api.base,
    locale: locals.locale,
  }
}
