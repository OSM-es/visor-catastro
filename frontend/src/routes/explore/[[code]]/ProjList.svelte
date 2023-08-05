<script>
  import { TableBody, TableBodyCell, TableHead } from 'flowbite-svelte'
  import { goto } from '$app/navigation'
  import { locale, t } from '$lib/translations'
  import SortTable from '$lib/components/tables/SortTable.svelte'
  import SortTableHeadCell from '$lib/components/tables/SortTableHeadCell.svelte'

  import { TASK_THR, MUN_THR } from '$lib/config'

  export let data
  export let target
  export let activeItem = null
  export let map

  let items = []

  const tdClass = 'px-2 py-0.5 whitespace-nowrap'
  const trClass = 'hover:bg-amber-400 cursor-pointer border-b last:border-b-0 odd:bg-white even:bg-gray-50 odd:dark:bg-gray-800 even:dark:bg-gray-700'
  const fmt = new Intl.NumberFormat($locale, { maximumFractionDigits: 2, style: "percent" })

  const code = (item, target) => target === 'provinces' ? item.provcode : item.muncode
  const key = target => target === 'provinces' ? 'provcode' : 'muncode' 

  function setZoom(zoom) {
    map.getMap().setZoom(zoom)
  }
</script>

{#if data?.length > 0}
  <SortTable
    data={data.map(t => t.properties)}
    bind:items
    {activeItem}
    let:activeItem={active}
    divClass="pt-3"
    striped
  >
    <caption class="text-left mb-2">
      {#if target === 'provinces'}
        {$t('explore.select', { item: $t('explore.prov')})}
        <button class="text-primary-600 lowercase" on:click={() => setZoom(MUN_THR)}>{$t('explore.zoom')}</button>
        {$t('explore.formuns')}
      {:else}
        {$t('explore.select', { item: $t('explore.mun')})}
        <button class="text-primary-600 lowercase" on:click={() => setZoom(TASK_THR)}>{$t('explore.zoom')}</button>
        {$t('explore.fortasks')}
      {/if}
    </caption>
    <TableHead defaultRow={false} theadClass="sticky top-0 bg-neutral-100 dark:bg-neutral-700">
      <tr class="text-xs uppercase">
        <SortTableHeadCell thClass="p-2" key={key(target)}>{$t('explore.code')}</SortTableHeadCell>
        <SortTableHeadCell thClass="p-2" key='name'>{$t('explore.name')}</SortTableHeadCell>
        <SortTableHeadCell thClass="p-2" key='task_count'>{$t('explore.tasks')}</SortTableHeadCell>
        <SortTableHeadCell thClass="p-2" key='mapped_count'>Mapeado</SortTableHeadCell>
      </tr>
    </TableHead>
    <TableBody>
      {#each items as item, i}
        <!-- svelte-ignore a11y-click-events-have-key-events -->
        <!-- svelte-ignore a11y-mouse-events-have-key-events -->
        <tr
          on:click={() => goto('/explore/' + code(item, target))}
          on:mouseover={() => activeItem = data.find(t => code(t.properties, target) === item.muncode)}
          on:mouseout={() => activeItem = null}
          class={trClass + (String(i) === active?.id ? ' !bg-amber-400' : '')}
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
  <p class="w-full bg-neutral-100 dark:bg-neutral-700 p-2 mt-3">
    No hay {#if target === 'provinces'}provincias{:else}municipios{/if} aquí
  </p>
{/if}
