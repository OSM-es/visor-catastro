<script>
  import { getContext } from 'svelte'
  import { writable } from 'svelte/store'

  export let key
  let activeClasses = 'px-4 py-2 bg-neutral-100 dark:bg-neutral-800 rounded-t-lg text-primary-600 border-b-2 border-primary-600 dark:text-primary-500 dark:border-primary-500 active'
  let inactiveClasses = 'px-4 py-2 hover:bg-neutral-50 dark:hover:bg-neutral-800 rounded-t-lg border-b-2 border-transparent hover:text-neutral-600 hover:border-neutral-300 dark:hover:text-neutral-300 text-neutral-500 dark:text-neutral-400'
  let defaultClass = 'inline-block text-sm font-medium text-center disabled:cursor-not-allowed '

  const selected = getContext('selected') ?? writable()

  $: open = ($selected === key)
  $: buttonClass = (
    open ? (defaultClass + activeClasses) : (defaultClass + inactiveClasses)
  )
</script>

<li class="group" role="presentation">
  <button
    type="button"
    on:click={() => ($selected = key)}
    on:blur
    on:click
    on:contextmenu
    on:focus
    on:keydown
    on:keypress
    on:keyup
    on:mouseenter
    on:mouseleave
    on:mouseover
    role="tab"
    class={buttonClass}>
    <slot/>
  </button>
</li>
  