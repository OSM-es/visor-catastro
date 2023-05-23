export async function load({ url }) {
  let center, zoom

  const view = url.searchParams.get('map')?.split('/')

  if (view?.length === 3) {
    zoom = view[0]
    center = [view[1], view[2]]
  }

  return { center, zoom }
}
