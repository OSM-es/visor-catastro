export async function load({ depends, locals }) {
  depends('data:user')

  return { 
    user: locals.user 
  }
}
