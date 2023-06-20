<script>
	import { setContext } from 'svelte'
  import { writable } from 'svelte/store'

	import { Table } from 'flowbite-svelte'

	export let data = []
	export let divClass = 'relative overflow-scroll max-sm:h-32 h-44'
	export let striped = 'striped'
  export let items

  const table = writable({
		key: null,
		direction: 1,
		items: data.slice(),
	})
	
	$: $table.items = [...$table.items].sort((a, b) => {
    const aVal = a[$table.key]
    const bVal = b[$table.key]
    if (aVal < bVal) {
      return -$table.direction
    } else if (aVal > bVal) {
      return $table.direction
    }
    return 0
  })
  $: {
    // $table.items = data.slice()
    items = $table.items
  }

  setContext('table', table)
</script>

<Table {divClass} {striped}>
	<slot></slot>
</Table>
