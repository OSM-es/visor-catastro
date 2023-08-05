import * as env from '$env/static/public'
import { dev } from '$app/environment'

export const PUBLIC_API_URL = env.PUBLIC_API_URL || (dev ? ':5000/api' : '/api')
export const PUBLIC_INITIAL_VIEW = env.PUBLIC_INITIAL_VIEW.split(',') || [36, 1]
PUBLIC_INITIAL_VIEW.forEach((x, i) => PUBLIC_INITIAL_VIEW[i] = Number(x).toFixed(4))
export const PUBLIC_INITIAL_ZOOM = Number(env.PUBLIC_INITIAL_ZOOM) || 5
export const PUBLIC_MAX_SW = env.PUBLIC_MAX_SW.split(',') || [20, -35]
export const PUBLIC_MAX_NE = env.PUBLIC_MAX_NE.split(',') || [50, 20]
export const TASK_THR = 15
export const MUN_THR = 8

export const TASK_ACTION_VALUES = {
  LOCKED: 'Bloqueado para',
  STATE_CHANGE: 'Marcado como',
  COMMENT: 'Comentó',
  UNLOCKED: 'Desbloquedo para',
  AUTO_UNLOCKED: 'Desbloquedo para',
}

export const TASK_ACTION_TEXT = {
  MAPPING: 'importar',
  VALIDATION: 'validar',
  MAPPED: 'mapeada',
  VALIDATED: 'validada',
  INVALIDATED: 'se necesita más mapeo',
}

export const FIXME_MSG = {
  CA2O_PART_BIGGER: 'Parte mayor que edificio',
  CA2O_SMALL_AREA: 'Área demasiado pequeña',
  CA2O_BIG_AREA: 'Área demasiado grande',
  CA2O_MISSING_PARTS: 'Partes no cubren edificio',
  CA2O_GEOS: 'Error de validación GEOS:',
  UPDATE_DEL: 'Eliminar',
  UPDATE_ADD: 'Añadir',
  UPDATE_TAGS: 'Han cambiado las etiquetas',
  UPDATE_GEOM: 'Ha cambiado la geometría',
  UPDATE_FULL: 'Cambian tanto etiquetas como geometría',
  UPDATE_ORPHAN: 'Tarea eliminada',
  UPDATE_DEL_CHECK: 'Comprobar si hay que eliminar',
}

export const AREA_BORDER = '#3388ff'
export const TASK_COLORS = {
  READY: '#FFFFFF66',
  MAPPED: '#1E90FF99',
  VALIDATED: '#00800099',
  INVALIDATED: '#FF450099',
  NEED_UPDATE: '#FFD70099',
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