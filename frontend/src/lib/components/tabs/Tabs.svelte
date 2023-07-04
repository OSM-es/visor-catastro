<script>
  import { writable } from 'svelte/store'
  import { setContext } from 'svelte'

  export let tab

  $: tab = $selected

  let defaultClass = 'flex flex-wrap space-x-2'

  const selected = writable(tab)

  setContext('selected', selected)
</script>
  
<div class="pt-2 pb-1">
  <ul class={defaultClass}>
    <slot/>
  </ul>
  <div class="h-px bg-gray-200 dark:bg-gray-700" />
</div>