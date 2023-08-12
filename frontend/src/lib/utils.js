import { t } from '$lib/translations'

export async function editInJosm(bounds) {
  let url = 'http://127.0.0.1:8111/load_and_zoom'
  url += `?left=${bounds._southWest.lng}&right=${bounds._northEast.lng}`
  url += `&top=${bounds._northEast.lat}&bottom=${bounds._southWest.lat}`
  try {
    await fetch(url)
  } catch {
    return t.get('task.josmerror')
  }
}
