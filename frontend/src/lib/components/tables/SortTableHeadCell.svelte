<script>
	import { getContext } from 'svelte'

  import { TableHeadCell } from 'flowbite-svelte'
  import { ArrowsUpDown, ArrowSmallDown, ArrowSmallUp } from 'svelte-heros-v2'


  export let key
  export let thClass = "px-4 py-2"
  
  const table = getContext('table')
  
  function sortTable() {
    if ($table.key === key) {
      $table.direction = -$table.direction
    } else {
      $table.key = key
      $table.direction = 1
    }
  }
</script>

<!-- svelte-ignore a11y-click-events-have-key-events -->
<!-- svelte-ignore a11y-mouse-events-have-key-events -->
<TableHeadCell padding={thClass}>
  <div on:click={sortTable} class="flex items-center space-x-1">
    <div>
      <slot></slot>
    </div>
    {#if $table.key === key}
      {#if $table.direction === 1}
        <ArrowSmallUp size="14"/>
      {:else}
        <ArrowSmallDown size="14"/>
      {/if}
    {:else}
      <ArrowsUpDown size="14"/>
    {/if}
  </div>
</TableHeadCell>
