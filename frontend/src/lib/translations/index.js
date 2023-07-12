import i18n from 'sveltekit-i18n'
import lang from './lang.json'

export const config = {
  translations: {
    es: { lang },
    en: { lang },
  },
  loaders: [
    {
      locale: 'es',
      key: 'menu',
      loader: async () => (await import('./es/menu.json')).default,
    },
    {
      locale: 'en',
      key: 'menu',
      loader: async () => (await import('./en/menu.json')).default,
    },
    {
      locale: 'es',
      key: 'learn',
      loader: async () => (await import('./es/learn.json')).default,
    },
    {
      locale: 'en',
      key: 'learn',
      loader: async () => (await import('./en/learn.json')).default,
    },
  ]
}

export const { t, loading, locales, locale, loadTranslations } = new i18n(config)

loading.subscribe(($loading) => $loading && console.log('Loading translations...'))