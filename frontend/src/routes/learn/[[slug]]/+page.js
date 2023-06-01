export async function load({ params }) {
  const slug = params.slug || 'index'
  const post = await import(`../${slug}.svx`)
  const content = post.default
  return { content }
}
