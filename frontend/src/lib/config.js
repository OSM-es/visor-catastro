import * as env from '$env/static/public'
import { dev } from '$app/environment'

export const PUBLIC_API_URL = env.PUBLIC_API_URL || (dev ? ':5000/api' : '/api')
export const PUBLIC_INITIAL_VIEW = env.PUBLIC_INITIAL_VIEW.split(',') || [36, 1]
PUBLIC_INITIAL_VIEW.forEach((x, i) => PUBLIC_INITIAL_VIEW[i] = Number(x).toFixed(4))
export const PUBLIC_INITIAL_ZOOM = Number(env.PUBLIC_INITIAL_ZOOM) || 5
export const PUBLIC_INITIAL_SW = env.PUBLIC_INITIAL_SW.split(',') || [27, -30]
export const PUBLIC_INITIAL_NE = env.PUBLIC_INITIAL_NE.split(',') || [44, 4]
export const PUBLIC_MAX_SW = env.PUBLIC_MAX_SW.split(',') || [20, -35]
export const PUBLIC_MAX_NE = env.PUBLIC_MAX_NE.split(',') || [50, 20]
export const TASK_THR = 15
export const MUN_THR = 8
export const PROJECT_COMMENT = '#Spanish_Cadastre_Buildings_Import'

export const AREA_BORDER = '#3388ff'
export const TASK_COLORS = {
  READY: '#FFFFFF66',
  MAPPED: '#1E90FF99',
  VALIDATED: '#00800099',
  INVALIDATED: '#FF450099',
  NEED_UPDATE: '#FFD70099',
}

export const PROJ_COLORS = {
  READY: '#99999933',
  MAPPING: '#1E90FF44',
  MAPPED: '#1E90FF99',
  VALIDATED: '#00800099',
}


export const TASK_LOCKED_COLOR = '#80808099'

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