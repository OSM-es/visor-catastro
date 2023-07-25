<script>
	import { createEventDispatcher } from 'svelte'
  import { TableBody, TableBodyCell, TableHead } from 'flowbite-svelte'

  import { goto } from '$app/navigation'

  import SortTable from '$lib/components/tables/SortTable.svelte'
  import SortTableHeadCell from '$lib/components/tables/SortTableHeadCell.svelte'
  import { locale } from '$lib/translations'

  export let data
  export let target
  export let activeItem = null

  let items = []

  const dispatch = createEventDispatcher()
  const tdClass = 'px-2 py-0.5 whitespace-nowrap'
  const trClass = 'hover:bg-amber-400 cursor-pointer border-b last:border-b-0 odd:bg-white even:bg-gray-50 odd:dark:bg-gray-800 even:dark:bg-gray-700'
  const fmt = new Intl.NumberFormat($locale, { maximumFractionDigits: 2, style: "percent" })

  const code = (item, target) => target === 'provinces' ? item.provcode : item.muncode
  const key = target => target === 'provinces' ? 'provcode' : 'muncode' 
</script>

<div>
  {#if data?.length > 0}
    <SortTable
      data={data.map(t => t.properties)}
      bind:items
      {activeItem}
      let:activeItem={active}
      divClass="overflow-scroll"
      striped
    >
      <caption class="text-left mb-2">
        {#if target === 'provinces'}
          Selecciona una provincia o haz zoom para ver los municipios.
        {:else}
          Selecciona un municipio o haz zoom para ver las tareas.
        {/if}
      </caption>
      <TableHead defaultRow={false} theadClass="bg-neutral-100 dark:bg-neutral-700">
        <tr class="text-xs uppercase">
          <SortTableHeadCell thClass="p-2" key={key(target)}>Código</SortTableHeadCell>
          <SortTableHeadCell thClass="p-2" key='name'>Nombre</SortTableHeadCell>
          <SortTableHeadCell thClass="p-2" key='task_count'>Tareas</SortTableHeadCell>
          <SortTableHeadCell thClass="p-2" key='mapped_count'>Mapeado</SortTableHeadCell>
        </tr>
      </TableHead>
      <TableBody>
        {#each items as item, i}
          <!-- svelte-ignore a11y-click-events-have-key-events -->
          <!-- svelte-ignore a11y-mouse-events-have-key-events -->
          <tr
            on:click={() => goto('/explore/' + code(item, target))}
            on:mouseover={() => dispatch('mouseover', { feature: data.find(t => code(t.properties, target) === item.muncode) })}
            on:mouseout={() => dispatch('mouseout')}
            class={trClass + (String(i) === active ? ' !bg-amber-400' : '')}
          >
            <TableBodyCell {tdClass}>{code(item, target)}</TableBodyCell>
            <TableBodyCell {tdClass}>{item.name}</TableBodyCell>
            <TableBodyCell {tdClass}>{item.task_count}</TableBodyCell>
            <TableBodyCell {tdClass}>{fmt.format(item.mapped_count / item.task_count)}</TableBodyCell>
          </tr>
        {/each}
      </TableBody>
    </SortTable>
  {:else}
    <p class="w-full bg-neutral-100 dark:bg-neutral-700 p-2">
      No hay {#if target === 'provinces'}provincias{:else}municipios{/if} aquí
    </p>
  {/if}
</div>