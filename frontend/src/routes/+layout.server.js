import { redirect } from '@sveltejs/kit'

export async function load({ locals, url }) {
  if (!locals.user) {
    if (url.pathname.startsWith('/settings')) {
      throw redirect(302, '/')
    }
  }
  return {
      user: locals.user
  }
}
