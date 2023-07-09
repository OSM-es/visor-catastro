import { invalidate } from '$app/navigation'

import Api from '$lib/api'

let signupUrl = 'https://www.openstreetmap.org/user/new'

const loginOptions = 'location=yes,height=620,width=550,scrollbars=yes,status=yes'
const signupOptions = 'location=yes,height=950,width=800,scrollbars=yes,status=yes'

export function relogin() {
  window.open(Api.getBase(window.location) + '/relogin', '_blank', loginOptions)
}

export  function login() {
  window.open(Api.getBase(window.location) + '/login', '_blank', loginOptions)
}

export async function logout() {
  const resp = await fetch(Api.getBase(window.location) + '/logout', { credentials: 'include'})
  if (resp.ok) {
    await invalidate('data:user')
  }
}

export function signup() {
  window.open(signupUrl, '_blank', signupOptions)
}
