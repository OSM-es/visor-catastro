<script>
  import { TableBody, TableBodyCell, TableHead } from 'flowbite-svelte'

  import { goto } from '$app/navigation'
  import { t } from '$lib/translations'

  import TaskStatus from './TaskStatus.svelte'
  import SortTable from '$lib/components/tables/SortTable.svelte'
  import SortTableHeadCell from '$lib/components/tables/SortTableHeadCell.svelte'
  import FilterTableHeadCell from '$lib/components/tables/FilterTableHeadCell.svelte'

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
  
  const tdClass = 'px-2 py-0.5 whitespace-nowrap'
  const trClass = 'cursor-pointer border-b last:border-b-0 odd:bg-white even:bg-gray-50 odd:dark:bg-gray-800 even:dark:bg-gray-700'

  const taskStatuses = {
    READY: $t('explore.READY'),
    MAPPED: $t('explore.MAPPED'),
    VALIDATED: $t('explore.VALIDATED'),
    INVALIDATED: $t('explore.INVALIDATED'),
    NEED_UPDATE: $t('explore.NEED_UPDATE'),
  }

  const taskDificulties = {
    EASY: $t('explore.EASY'),
    MODERATE: $t('explore.MODERATE'),
    CHALLENGING: $t('explore.CHALLENGING'),
  }

  const taskTypes = {
    "Urbana": $t('explore.Urbana'),
    "Rústica": $t('explore.Rústica'),
  }

  function diffColor(difficulty) {
    if (difficulty === 'EASY') return 'text-success-500'
    if (difficulty === 'MODERATE') return 'text-warning-500'
    return 'text-danger-500'
  }
</script>

<SortTable
  data={tasks.map(t => t.properties)}
  bind:items
  {activeItem}
  let:activeItem={active}
  let:items={items}
  divClass=""
  striped
>
  {#if munCount > 1 || muncode}
    <TableHead defaultRow={false} theadClass="sticky top-0 bg-neutral-100 dark:bg-neutral-700">
      <tr class="text-xs uppercase"> 
        <SortTableHeadCell thClass="p-2" key='muncode'>{$t('explore.mun')}</SortTableHeadCell>
        <SortTableHeadCell thClass="p-2" key='type'>{$t('explore.type')}</SortTableHeadCell>
        <SortTableHeadCell thClass="p-2" key='difficulty'>{$t('explore.diff')}</SortTableHeadCell>
        <SortTableHeadCell thClass="p-2" key='bu_status'>{$t('explore.bu_status')}</SortTableHeadCell>
        <SortTableHeadCell thClass="p-2" key='ad_status'>{$t('explore.ad_status')}</SortTableHeadCell>
      </tr>
      <tr>
        <FilterTableHeadCell key='muncode' bind:value={muncode} items={munItems}></FilterTableHeadCell>
        <FilterTableHeadCell key='type' bind:value={type} items={taskTypes}></FilterTableHeadCell>
        <FilterTableHeadCell key='difficulty' bind:value={difficulty} items={taskDificulties}></FilterTableHeadCell>
        <FilterTableHeadCell key='status' bind:value={bu_status} items={taskStatuses}></FilterTableHeadCell>
        <FilterTableHeadCell key='status' bind:value={ad_status} items={taskStatuses}></FilterTableHeadCell>
      </tr>
    </TableHead>
  {:else}
  <TableHead defaultRow={false} theadClass="sticky top-0 bg-neutral-100 dark:bg-neutral-700">
    <tr class="text-xs uppercase"> 
      <SortTableHeadCell thClass="p-2" key='type'>{$t('explore.type')}</SortTableHeadCell>
      <SortTableHeadCell thClass="p-2" key='difficulty'>{$t('explore.diff')}</SortTableHeadCell>
      <SortTableHeadCell thClass="p-2" key='bu_status'>{$t('explore.bu_status')}</SortTableHeadCell>
      <SortTableHeadCell thClass="p-2" key='ad_status'>{$t('explore.ad_status')}</SortTableHeadCell>
  </tr>
    <tr>
      <FilterTableHeadCell key='type' bind:value={type} items={taskTypes}></FilterTableHeadCell>
      <FilterTableHeadCell key='difficulty' bind:value={difficulty} items={taskDificulties}></FilterTableHeadCell>
      <FilterTableHeadCell key='status' bind:value={bu_status} items={taskStatuses}></FilterTableHeadCell>
      <FilterTableHeadCell key='status' bind:value={ad_status} items={taskStatuses}></FilterTableHeadCell>
    </tr>
  </TableHead>
{/if}
  <TableBody>
    {#each items as task, i}
      <!-- svelte-ignore a11y-click-events-have-key-events -->
      <!-- svelte-ignore a11y-mouse-events-have-key-events -->
      <tr
        on:click={() => goto('/explore/task/' + task.id)}
        on:mouseover={() => activeItem = tasks.find(t => t.properties.id === task.id)}
        on:mouseout={() => activeItem = null}
        class={trClass + (String(i) === active?.id ? ' !bg-amber-400' : '')}
      >
        {#if munCount > 1 || muncode}
          <TableBodyCell {tdClass}>{task.muncode}</TableBodyCell>
        {/if}
        <TableBodyCell {tdClass}>{taskTypes[task.type]}</TableBodyCell>
        <TableBodyCell {tdClass}>
          <span class={diffColor(task.difficulty)}>
            {taskDificulties[task.difficulty]}
          </span>
        </TableBodyCell>
        <TableBodyCell {tdClass}>
          <TaskStatus status={task.lock_id ? 'LOCKED' : task.bu_status}/>
        </TableBodyCell>
        <TableBodyCell {tdClass}>
          <TaskStatus status={task.lock_id ? 'LOCKED' : task.ad_status}/>
        </TableBodyCell>
      </tr>
    {/each}
  </TableBody>
</SortTable>
{#if tasks?.length === 0}
  <p class="w-full bg-neutral-100 dark:bg-neutral-700 p-2">
    {$t('explore.noresults')}
  </p>
{/if}
