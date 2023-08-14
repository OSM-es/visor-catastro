import { writable } from 'svelte/store'


const storedExploreCode = localStorage.exploreCode

export const exploreCode = writable(storedExploreCode || null)

exploreCode.subscribe((value) => localStorage.exploreCode = value)


const storedExplorePath = localStorage.explorePath

export const explorePath = writable(storedExplorePath || null)

explorePath.subscribe((value) => localStorage.explorePath = value)
