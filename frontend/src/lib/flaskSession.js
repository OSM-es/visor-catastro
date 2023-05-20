import { unzip } from 'zlib'
import { promisify } from 'util'

const doUnzip = promisify(unzip)

/**
 * Decodifica el contenido de la cookie de sessión de Flask
 */
export default async function decode(cookie) {
  let compressed = false
  let payload = cookie

  if (payload.startsWith('.')) {
    compressed = true
    payload = payload.substring(1)
  }
  let buffer = Buffer.from(payload.split('.')[0], 'base64')
  if (compressed) {
    buffer = await doUnzip(buffer)
  }
  const data = JSON.parse(buffer.toString())

  return data
}
