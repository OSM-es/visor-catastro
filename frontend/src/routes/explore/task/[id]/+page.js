export function load({ url, data }) {
  data.imageRef = url.searchParams.get('ref')

  return data
}
