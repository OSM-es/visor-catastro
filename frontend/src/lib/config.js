import * as env from '$env/static/public'

export const PUBLIC_API_URL = env.PUBLIC_API_URL || 'http://127.0.0.1/api'
export const PUBLIC_INITIAL_VIEW = env.PUBLIC_INITIAL_VIEW.split(',') || [36, 1]
PUBLIC_INITIAL_VIEW.forEach((x, i) => PUBLIC_INITIAL_VIEW[i] = Number(x).toFixed(4))
export const PUBLIC_INITIAL_ZOOM = Number(env.PUBLIC_INITIAL_ZOOM) || 5

export const FotoFachadaUrl = 'http://ovc.catastro.meh.es/OVCServWeb/OVCWcfLibres/OVCFotoFachada.svc/RecuperarFotoFachadaGet?ReferenciaCatastral='

export const TASK_COLORS = {
  READY_FOR_ADDRESSES: '#FFFFFF66',
  LOCKED_FOR_ADDRESSES: '#80808099',
  READY_FOR_MAPPING: '#ADFF2F66',
  LOCKED_FOR_MAPPING: '#80808099',
  MAPPED: '#1E90FF99',
  LOCKED_FOR_VALIDATION: '#80808099',
  VALIDATED: '#00800099',
  INVALIDATED: '#FF450099',
  BLOCKED_BY_SYSTEM: '#80808099',
  NEED_UPDATE: '#FFD70099',
}

// https://sashamaps.net/docs/resources/20-colors/
export const STREET_COLORS = [
  '#e6194b',
  '#3cb44b',
  '#ffe119',
  '#4363d8',
  '#f58231',
  '#911eb4',
  '#46f0f0',
  '#f032e6',
  '#bcf60c',
  '#fabebe',
  '#008080',
  '#e6beff',
  '#9a6324',
  '#fffac8',
  '#aaffc3',
  '#808000',
  '#ffd8b1',
  '#000075',
  '#800000',
]

export const STREET_COLORS_TEXT = [
  '#000000',
  '#000000',
  '#000000',
  '#000000',
  '#000000',
  '#000000',
  '#000000',
  '#000000',
  '#000000',
  '#000000',
  '#000000',
  '#000000',
  '#000000',
  '#000000',
  '#000000',
  '#000000',
  '#000000',
  '#ffffff',
  '#ffffff',
]

export const DEFAULT_STREET_COLOR = '#808080'