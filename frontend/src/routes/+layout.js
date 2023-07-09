import { locale, locales, loadTranslations } from '$lib/translations'

export async function load({ data, url }) {
  const _locales = locales.get()
  let defaultLocale = data.locale

  if (typeof localStorage !== 'undefined') {
    defaultLocale = localStorage.locale || defaultLocale
    defaultLocale = _locales.includes(defaultLocale) ? defaultLocale : _locales[0]
    locale.subscribe((value) => {
      localStorage.locale = value
      data.locale = value
    })
  }
  const initLocale = locale.get() || defaultLocale

  await loadTranslations(initLocale, url.pathname)

  return data
}
