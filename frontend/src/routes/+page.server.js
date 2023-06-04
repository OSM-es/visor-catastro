import { redirect } from '@sveltejs/kit';


export function load({ locals }) {
  if (locals?.user) {
    if (!locals.user?.user?.role || locals.user.role === 'READ_ONLY') {
      const url = locals?.user?.user ? locals.user.user.tutorial.next : ''
      throw redirect(302, '/learn/' + url)
    } else {
      throw redirect(302, '/explore')
    }
  }
}