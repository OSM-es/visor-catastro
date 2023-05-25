import { PUBLIC_API_URL } from '$lib/config'
import { invalidate } from '$app/navigation'

let signupUrl = 'https://www.openstreetmap.org/user/new'

export async function login(event) {
  if (event.detail === '/auth') {
    await invalidate('data:user')
  } else {
    const options = 'location=yes,height=620,width=550,scrollbars=yes,status=yes'
    window.open(PUBLIC_API_URL + '/login', '_blank', options)
  }
}

export async function logout() {
  const resp = await fetch(PUBLIC_API_URL + '/logout', { credentials: 'include'})
  if (resp.ok) {
    await invalidate('data:user')
  }
}

export function signup() {
  const options = 'location=yes,height=950,width=800,scrollbars=yes,status=yes'
  window.open(signupUrl, '_blank', options)
}
