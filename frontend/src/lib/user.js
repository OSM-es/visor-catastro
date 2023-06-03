import { PUBLIC_API_URL } from '$lib/config'
import { invalidate } from '$app/navigation'

let signupUrl = 'https://www.openstreetmap.org/user/new'

const loginOptions = 'location=yes,height=620,width=550,scrollbars=yes,status=yes'
const signupOptions = 'location=yes,height=950,width=800,scrollbars=yes,status=yes'

export function relogin() {
  window.open(PUBLIC_API_URL + '/relogin', '_blank', loginOptions)
}

export  function login() {
  window.open(PUBLIC_API_URL + '/login', '_blank', loginOptions)
}

export async function logout() {
  const resp = await fetch(PUBLIC_API_URL + '/logout', { credentials: 'include'})
  if (resp.ok) {
    await invalidate('data:user')
  }
}

export function signup() {
  window.open(signupUrl, '_blank', signupOptions)
}
