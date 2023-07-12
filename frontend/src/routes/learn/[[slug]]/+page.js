import { locale, locales } from '$lib/translations'

export async function load({ data, depends, params }) {
  depends('data:locale')

  const slug = params.slug || 'index'
  const lang = locale.get() || locales.get()[0]
  const post = await import(`../${lang}/${slug}.md`)
  const content = post.default

  return { content, locale: data.locale }
}
