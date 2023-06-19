import { writable } from 'svelte/store'


const storedCurrentTask = localStorage.currentTask

export const currentTask = writable(storedCurrentTask || null)

currentTask.subscribe((value) => localStorage.currentTask = value)
