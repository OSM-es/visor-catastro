export async function load({ data, url }) {
  let center, zoom

  const view = url.searchParams.get('map')?.split('/')
  const geojsonUrl = (target, code, bounds) => {
    return `${data.api}/${target}?${code ? 'code=' + code : ''}${bounds ? '&bounds=' + bounds : ''}`
  }

  if (view?.length === 3) {
    zoom = view[0]
    center = [view[1], view[2]]
  }

  const geoJsonData = async (target, code, bounds) => {
    if (target !== 'tasks' && code) bounds = null
    const url = geojsonUrl(target, code, bounds)
    const response = await fetch(url)
    return await response.json()
  }

  const stats = async (code) => {
    const url = data.api + '/stats/' + code
    const response = await fetch(url)
    return await response.json()
  }

  return {
    center,
    zoom,
    streamed: {
      geoJsonData,
      stats,
    }
  }
}
