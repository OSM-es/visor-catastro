import { writable } from 'svelte/store'


const storedExploreCode = localStorage.exploreCode

export const exploreCode = writable(storedExploreCode || null)

exploreCode.subscribe((value) => localStorage.exploreCode = value)