import i18n from 'sveltekit-i18n'
import lang from './lang.json'

export const config = {
  translations: {
    en: { lang },
    es: { lang },
  },
  loaders: [
    {
      locale: 'en',
      key: 'menu',
      loader: async () => (await import('./en/menu.json')).default,
    }, 
    {
      locale: 'es',
      key: 'menu',
      loader: async () => (await import('./es/menu.json')).default,
    },
  ]
}

export const { t, loading, locales, locale, loadTranslations } = new i18n(config)

loading.subscribe(($loading) => $loading && console.log('Loading translations...'))