import { redirect } from '@sveltejs/kit'


export async function load({ fetch, locals }) {
  if (locals?.user) {
    if (!locals.user?.role || locals.user.role === 'READ_ONLY') {
      const url = locals?.user?.tutorial ? locals.user.tutorial.next : ''
      throw redirect(302, '/learn/' + url)
    } else {
      throw redirect(302, '/explore')
    }
  } else {
    throw redirect(302, '/about')
  }
}