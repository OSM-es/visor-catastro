<script>
	import { setContext } from 'svelte'
  import { writable } from 'svelte/store'

	import { Table } from 'flowbite-svelte'

  export let divClass
	export let striped
  export let data = []
  export let items = []
  export const getTable = () => table
  export let activeItem


  const table = writable({
		key: null,
		direction: 1,
    items: [],
	})

  setContext('table', table)

  $: {
    $table.items = [...data].sort((a, b) => {
      const aVal = a[$table.key]
      const bVal = b[$table.key]
      if (aVal < bVal) {
        return -$table.direction
      } else if (aVal > bVal) {
        return $table.direction
      }
      return 0
    })
    items = $table.items
  }

</script>

<Table {divClass} {striped}>
  <slot {activeItem} {items}></slot>
</Table>
