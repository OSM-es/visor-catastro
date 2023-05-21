import { PUBLIC_API_URL } from '$lib/config'
import { error } from '@sveltejs/kit'


export default class Api {
  static base = PUBLIC_API_URL

  constructor(fetch) {
    this.fetch = fetch
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
  
    const resp = await this.fetch(`${Api.base}/${path}`, opts)
    if (resp.ok || resp.status === 422) {
      const data = await resp.json()
      return data
    }
  
    throw error(resp.status)
  }

  get(path, token) {
    return this.send({ method: 'GET', path, token })
  }
  
  del(path, token) {
    return this.send({ method: 'DELETE', path, token })
  }
  
  post(path, data, token) {
    return this.send({ method: 'POST', path, data, token })
  }
  
  put(path, data, token) {
    return this.send({ method: 'PUT', path, data, token })
  }
}
