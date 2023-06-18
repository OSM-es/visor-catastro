import { writable } from 'svelte/store'


const storedCurrentTask = localStorage.currentTask

export const currentTask = writable(storedCurrentTask || null)

currentTask.subscribe((value) => localStorage.currentTask = value)


export const streetNames = createStreetNames()

function createStreetNames() {
  const { subscribe, update } = writable([])

  return {
    subscribe,
    add: (features) => update(names => {
      for (const feat of features) {
        const tags = feat.properties?.tags || {}
        const name =('highway' in tags) ? tags?.name : (
          tags['addr:street'] || tags['addr:place'] || ''
        )
        if (name && !names.includes(name)) names.push(name)
      }
      return names
    })
  }
}