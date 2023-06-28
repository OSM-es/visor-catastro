<script>
	import { getContext } from 'svelte'

  import { Select, TableHeadCell } from 'flowbite-svelte'

  const table = getContext('table')
  
  export let key
  export let value
  export let items = defaultItems()
  export let thClass = "p-0.5 font-normal"
  
  items = getItems()
  
  function defaultItems() {
    return Array.from(
      new Set($table.items.map(it => it[key]))
    ).reduce(
      (i, v) => {
        i[v] = v
        return i
      }, {}
    )
  }
  
  function getItems() {
    return ([['', 'Ninguno']].concat(Object.entries(items))).map(([value, name]) => ({ value, name }))
  }
</script>

<TableHeadCell padding={thClass}>
  <Select size="sm" {items} bind:value placeholder="Filtro ..." class="py-0.5"
/>
</TableHeadCell>
