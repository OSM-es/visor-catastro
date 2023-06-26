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
  export let status

  let items = []

  $: munCount = (new Set(tasks?.map(t => t.properties.muncode))).size
  
  const dispatch = createEventDispatcher()
  const tdClass = 'px-2 py-0.5 whitespace-nowrap'
  const trClass = 'hover:bg-amber-400 cursor-pointer border-b last:border-b-0 odd:bg-white even:bg-gray-50 odd:dark:bg-gray-800 even:dark:bg-gray-700'
</script>

<div>
  <SortTable data={tasks.map(t => t.properties)} bind:items divClass="overflow-scroll" striped>
    <caption class="text-left mb-2">Selecciona una tarea:</caption>
    <TableHead defaultRow={false} theadClass="bg-neutral-100 dark:bg-neutral-700">
      <tr class="text-xs uppercase"> 
        {#if munCount > 1}<SortTableHeadCell thClass="p-2" key='muncode'>Municipio</SortTableHeadCell>{/if}
        <SortTableHeadCell thClass="p-2" key='type'>Tipo</SortTableHeadCell>
        <SortTableHeadCell thClass="p-2" key='difficulty'>Dificultad</SortTableHeadCell>
        <SortTableHeadCell thClass="p-2" key='status'>Estado</SortTableHeadCell>
      </tr>
      <tr>
        {#if munCount > 1}<FilterTableHeadCell key='muncode' bind:value={muncode}></FilterTableHeadCell>{/if}
        <FilterTableHeadCell key='type' bind:value={type} items={TASK_TYPE_VALUES}></FilterTableHeadCell>
        <FilterTableHeadCell key='difficulty' bind:value={difficulty} items={TASK_DIFFICULTY_VALUES}></FilterTableHeadCell>
        <FilterTableHeadCell key='status' bind:value={status} items={TASK_STATUS_VALUES}></FilterTableHeadCell>
      </tr>
    </TableHead>
    <TableBody>
      {#each items as task}
        <!-- svelte-ignore a11y-click-events-have-key-events -->
        <!-- svelte-ignore a11y-mouse-events-have-key-events -->
        <tr
          on:click={() => goto('/explore/task/' + task.id)}
          on:mouseover={() => dispatch('mouseover', { feature: tasks.find(t => t.properties.id === task.id) })}
          on:mouseout={() => dispatch('mouseout')}
          class={trClass}
        >
          {#if munCount > 1}<TableBodyCell {tdClass}>{task.muncode}</TableBodyCell>{/if}
          <TableBodyCell {tdClass}>{TASK_TYPE_VALUES[task.type]}</TableBodyCell>
          <TableBodyCell {tdClass}>{TASK_DIFFICULTY_VALUES[task.difficulty]}</TableBodyCell>
          <TableBodyCell {tdClass}>{TASK_STATUS_VALUES[task.status]}</TableBodyCell>
        </tr>
      {/each}
    </TableBody>
  </SortTable>
  {#if !tasks || tasks.length === 0}
    <div class="prose dark:prose-invert">No hay tareas aquí.</div>
  {/if}
</div>