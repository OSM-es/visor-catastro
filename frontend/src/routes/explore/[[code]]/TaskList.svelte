<script>
	import { createEventDispatcher } from 'svelte'
  import { TableBody, TableBodyCell, TableHead } from 'flowbite-svelte'

  import { goto } from '$app/navigation'

  import SortTable from '$lib/components/tables/SortTable.svelte'
  import SortTableHeadCell from '$lib/components/tables/SortTableHeadCell.svelte'
  import FilterTableHeadCell from '$lib/components/tables/FilterTableHeadCell.svelte'
  import { TASK_TYPE_VALUES, TASK_DIFFICULTY_VALUES, TASK_STATUS_VALUES } from '$lib/config'

  export let tasks
  export let muncode
  export let type
  export let difficulty
  export let ad_status
  export let bu_status
  export let activeItem = null

  let items = []

  $: munCount = (new Set(tasks?.map(t => t.properties.muncode))).size
  $: munItems = tasks?.reduce((i, v) => {
    i[v.properties.muncode] = `${v.properties.name} (${v.properties.muncode})`
    return i
  }, {}) || []
  
  const dispatch = createEventDispatcher()
  const tdClass = 'px-2 py-0.5 whitespace-nowrap'
  const trClass = 'hover:bg-amber-400 cursor-pointer border-b last:border-b-0 odd:bg-white even:bg-gray-50 odd:dark:bg-gray-800 even:dark:bg-gray-700'
</script>

<div>
  {#if tasks?.length > 0}
    <SortTable
      data={tasks.map(t => t.properties)}
      bind:items
      {activeItem}
      let:activeItem={active}
      let:items={prueba}
      divClass="overflow-scroll"
      striped
    >
      {#if munCount > 1 || muncode}
        <TableHead defaultRow={false} theadClass="bg-neutral-100 dark:bg-neutral-700">
          <tr class="text-xs uppercase"> 
            <SortTableHeadCell thClass="p-2" key='muncode'>Municipio</SortTableHeadCell>
            <SortTableHeadCell thClass="p-2" key='type'>Tipo</SortTableHeadCell>
            <SortTableHeadCell thClass="p-2" key='difficulty'>Dificultad</SortTableHeadCell>
            <SortTableHeadCell thClass="p-2" key='bu_status'>Estado edificios</SortTableHeadCell>
            <SortTableHeadCell thClass="p-2" key='ad_status'>Estado direcciones</SortTableHeadCell>
          </tr>
          <tr>
            <FilterTableHeadCell key='muncode' bind:value={muncode} items={munItems}></FilterTableHeadCell>
            <FilterTableHeadCell key='type' bind:value={type} items={TASK_TYPE_VALUES}></FilterTableHeadCell>
            <FilterTableHeadCell key='difficulty' bind:value={difficulty} items={TASK_DIFFICULTY_VALUES}></FilterTableHeadCell>
            <FilterTableHeadCell key='status' bind:value={bu_status} items={TASK_STATUS_VALUES}></FilterTableHeadCell>
            <FilterTableHeadCell key='status' bind:value={ad_status} items={TASK_STATUS_VALUES}></FilterTableHeadCell>
          </tr>
        </TableHead>
      {:else}
      <TableHead defaultRow={false} theadClass="bg-neutral-100 dark:bg-neutral-700">
        <tr class="text-xs uppercase"> 
          <SortTableHeadCell thClass="p-2" key='type'>Tipo</SortTableHeadCell>
          <SortTableHeadCell thClass="p-2" key='difficulty'>Dificultad</SortTableHeadCell>
          <SortTableHeadCell thClass="p-2" key='bu_status'>Estado edificios</SortTableHeadCell>
          <SortTableHeadCell thClass="p-2" key='ad_status'>Estado direcciones</SortTableHeadCell>
        </tr>
        <tr>
          <FilterTableHeadCell key='type' bind:value={type} items={TASK_TYPE_VALUES}></FilterTableHeadCell>
          <FilterTableHeadCell key='difficulty' bind:value={difficulty} items={TASK_DIFFICULTY_VALUES}></FilterTableHeadCell>
          <FilterTableHeadCell key='status' bind:value={bu_status} items={TASK_STATUS_VALUES}></FilterTableHeadCell>
          <FilterTableHeadCell key='status' bind:value={ad_status} items={TASK_STATUS_VALUES}></FilterTableHeadCell>
        </tr>
      </TableHead>
    {/if}
      <TableBody>
        {#each items as task, i}
          <!-- svelte-ignore a11y-click-events-have-key-events -->
          <!-- svelte-ignore a11y-mouse-events-have-key-events -->
          <tr
            on:click={() => goto('/explore/task/' + task.id)}
            on:mouseover={() => dispatch('mouseover', { feature: tasks.find(t => t.properties.id === task.id) })}
            on:mouseout={() => dispatch('mouseout')}
            class={trClass + (String(i) === active ? ' !bg-amber-400' : '')}
          >
            {#if munCount > 1 || muncode}
              <TableBodyCell {tdClass}>{task.muncode}</TableBodyCell>
            {/if}
            <TableBodyCell {tdClass}>{TASK_TYPE_VALUES[task.type]}</TableBodyCell>
            <TableBodyCell {tdClass}>{TASK_DIFFICULTY_VALUES[task.difficulty]}</TableBodyCell>
            <TableBodyCell {tdClass}>{task.lock_id ? 'Bloqueada' : TASK_STATUS_VALUES[task.bu_status]}</TableBodyCell>
            <TableBodyCell {tdClass}>{task.lock_id ? 'Bloqueada' : TASK_STATUS_VALUES[task.ad_status]}</TableBodyCell>
          </tr>
        {/each}
      </TableBody>
    </SortTable>
  {:else}
    <p class="w-full bg-neutral-100 dark:bg-neutral-700 p-2">
      No hay tareas aquí
    </p>
  {/if}
</div>