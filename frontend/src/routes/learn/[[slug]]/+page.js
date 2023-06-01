export async function load({ params }) {
  const slug = params.slug || 'index'
  const post = await import(`../${slug}.md`)
  const content = post.default
  return { content }
}
