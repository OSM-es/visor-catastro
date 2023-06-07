import * as env from '$env/static/public'

export const PUBLIC_API_URL = env.PUBLIC_API_URL || 'http://127.0.0.1/api'
export const PUBLIC_INITIAL_VIEW = env.PUBLIC_INITIAL_VIEW.split(',') || [36, 1]
PUBLIC_INITIAL_VIEW.forEach((x, i) => PUBLIC_INITIAL_VIEW[i] = Number(x).toFixed(4))
export const PUBLIC_INITIAL_ZOOM = Number(env.PUBLIC_INITIAL_ZOOM) || 5

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

export const STREET_COLORS = [
  '#228b22',
  '#483d8b',
  '#008b8b',
  '#556b2f',
  '#000080',
  '#4682b4',
  '#7f007f',
  '#ff4500',
  '#8a2be2',
  '#dc143c',
  '#800000',
  '#0000ff',
  '#808080',
  '#da70d6',
  '#ff00ff',
  '#1e90ff',
  '#db7093',
  '#ff1493',
  '#7b68ee',
  '#b8860b',
  '#ff8c00',
  '#e9967a',
  '#00ffff',
  '#32cd32',
  '#87ceeb',
  '#8fbc8f',
  '#d8bfd8',
  '#f0e68c',
  '#00ff00',
  '#ffff00',
  '#adff2f',
  '#98fb98',
]
