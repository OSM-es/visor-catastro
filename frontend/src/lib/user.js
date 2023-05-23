import { PUBLIC_API_URL } from '$lib/config'
import { invalidate } from '$app/navigation'

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
