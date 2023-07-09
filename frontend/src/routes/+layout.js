import { locale, loadTranslations } from '$lib/translations'

export async function load({ data, url }) {
  let defaultLocale = data.locale

  if (typeof localStorage !== 'undefined') {
    defaultLocale = localStorage.locale || defaultLocale
    locale.subscribe((value) => {
      localStorage.locale = value
      data.locale = value
    })
  }
  const initLocale = locale.get() || defaultLocale

  await loadTranslations(initLocale, url.pathname)
}
