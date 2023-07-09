import { PUBLIC_API_URL } from '$lib/config'
import { error } from '@sveltejs/kit'

import { parse as cookieParser } from 'cookie'

export default class Api {
  static getBase = (url) => `${url.protocol}//${url.hostname}${PUBLIC_API_URL}`

  constructor(event) {
    this.base = Api.getBase(event.url)
    this.event = event
    this.fetch = event.fetch
  }

  async send({ method, path, data, token }) {
    const opts = { method, headers: {} }

    if (data) {
      opts.headers['Content-Type'] = 'application/json'
      opts.body = JSON.stringify(data)
    }
    if (token) {
      opts.headers['Authorization'] = `Bearer ${token}`
    }
  
    const resp = await this.fetch(`${this.base}/${path}`, opts)
    if (resp.ok || resp.status === 422) {
      const cookie = resp.headers.get('set-cookie')
      if (cookie) {
        const {session, ...opts} = cookieParser(cookie)
        if (session) {
          const options = {
            expires: new Date(opts.Expires),
            path: '/',
          }
          this.event.cookies.set('session', session, options)
        }
      }
      const data = await resp.json()
      return data
    }
  
    throw error(resp.status)
  }

  get(path, token) {
    return this.send({ method: 'GET', path, token })
  }
  
  delete(path, token) {
    return this.send({ method: 'DELETE', path, token })
  }
  
  post(path, data, token) {
    return this.send({ method: 'POST', path, data, token })
  }
  
  put(path, data, token) {
    return this.send({ method: 'PUT', path, data, token })
  }
}
