export async function load({ depends, locals, url }) {
  depends('data:user')

  return { 
    user: locals.user,
    api: locals.api.base,
    locale: locals.locale,
  }
}
