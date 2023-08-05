import i18n from 'sveltekit-i18n'
import lang from './lang.json'
import { dev } from '$app/environment'

export const config = {
  log: {
    level: dev ? 'warn' : 'error',
  },
  translations: {
    es: { lang },
    en: { lang },
  },
  loaders: [
    {
      locale: 'es',
      key: 'common',
      loader: async () => (await import('./es/common.json')).default,
    },
    {
      locale: 'en',
      key: 'common',
      loader: async () => (await import('./en/common.json')).default,
    },
    {
      locale: 'es',
      key: 'explore',
      loader: async () => (await import('./es/explore.json')).default,
      routes: [/\/explore.*/],
    },
    {
      locale: 'en',
      key: 'explore',
      loader: async () => (await import('./en/explore.json')).default,
      routes: [/\/explore.*/],
    },
    {
      locale: 'es',
      key: 'about',
      loader: async () => (await import('./es/about.json')).default,
      routes: ['/about'],
    },
    {
      locale: 'en',
      key: 'about',
      loader: async () => (await import('./en/about.json')).default,
      routes: ['/about'],
    },
    {
      locale: 'es',
      key: 'task',
      loader: async () => (await import('./es/task.json')).default,
      routes: [/\/explore\/task\/.+/],
    },
    {
      locale: 'en',
      key: 'task',
      loader: async () => (await import('./en/task.json')).default,
      routes: [/\/explore\/task\/.+/],
    },
    {
      locale: 'es',
      key: 'stats',
      loader: async () => (await import('./es/stats.json')).default,
      routes: ['/about', /\/explore\/[0-9]{2,5}.*/],
    },
    {
      locale: 'en',
      key: 'stats',
      loader: async () => (await import('./en/stats.json')).default,
      routes: ['/about', /\/explore\/[0-9]{2,5}.*/],
    },
    {
      locale: 'es',
      key: 'learn',
      loader: async () => (await import('./es/learn.json')).default,
      routes: [/\/learn.*/],
    },
    {
      locale: 'en',
      key: 'learn',
      loader: async () => (await import('./en/learn.json')).default,
      routes: [/\/learn.*/],
    },
  ]
}

export const { t, loading, locales, locale, loadTranslations } = new i18n(config)

loading.subscribe(($loading) => $loading && console.log('Loading translations...'))
