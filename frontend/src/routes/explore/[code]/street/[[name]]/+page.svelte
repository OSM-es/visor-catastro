<script>
  import { onMount } from 'svelte'
  import { writable } from 'svelte/store'
  import { Button, ButtonGroup, Table, TableBody, TableBodyCell, TableBodyRow, TableHead, TableHeadCell } from 'flowbite-svelte'

  import Map from '$lib/Map.svelte'
  import { currentTask } from '$lib/stores.js'
  import { goto } from '$app/navigation'
  import { page } from '$app/stores'

  import ConsLayer from '$lib/ConsLayer.svelte'
  import FotosFachada from '$lib/FotosFachada.svelte'
  import StreetsLayer from '$lib/StreetsLayer.svelte'

  export let data

  const bounds = [[data.bounds[1], data.bounds[0]], [data.bounds[3], data.bounds[2]]]
  const sortKey = writable(null)
  const sortDirection = writable(1)
  const sortItems = writable(data.streets.slice())

  let map, getConsLayer, scrollImage, viewImage
  
  $: isEditor = data.user?.role && data.user.role != 'READ_ONLY'
  $: {
    const key = $sortKey;
    const direction = $sortDirection;
    const sorted = [...$sortItems].sort((a, b) => {
      const aVal = a[key]
      const bVal = b[key]
      if (aVal < bVal) {
        return -direction
      } else if (aVal > bVal) {
        return direction
      }
      return 0
    })
    sortItems.set(sorted);
  }
 
  const tdClass = "px-6 whitespace-nowrap"
  const thClass = "px-6 py-2"


  onMount(() => {
    const m = map.getMap()
    m.fitBounds(bounds)
    m.setMaxBounds(bounds)
    m.setMinZoom(m.getZoom())
    m.fitBounds(getConsLayer().getBounds())
    page.subscribe(page => {
      if (map) {
        map.getMap().invalidateSize()
        map.getMap().fitBounds(getConsLayer().getBounds())
      }
      viewImage = page.url.searchParams.get('ref')
    })
  })


  function sortTable(key) {
    if ($sortKey === key) {
      sortDirection.update(val => -val)
    } else {
      sortKey.set(key)
      sortDirection.set(1)
    }
  }

  function showEntrance({ detail }) {
    const ref = detail
    const address = data.addresses.features.find(ad => ad.properties.tags?.ref === ref)
    address.layer.openPopup()
  }

  function viewStreet(name) {
    goto(`/explore/${data.mun_code}/street/${name}`)
  }
</script>

<div class="flex flex-col flex-grow">
  <div class="border-b border-neutral-200 dark:border-neutral-700">
    <div class="h-10 inline-flex place-content-center w-full pt-1 bg-neutral-200 dark:bg-neutral-600">
      <ButtonGroup>
        <Button size="xs">&lt;</Button>
        <Button size="xs">Editar en OSM</Button>
        <Button size="xs" href="/explore/task/{$currentTask}">Regresar a la tarea</Button>
        <Button size="xs">&gt;</Button>
      </ButtonGroup>
    </div>
    <Table divClass="relative overflow-scroll max-sm:h-32 h-44" striped>
      <!-- svelte-ignore a11y-click-events-have-key-events -->
      <!-- svelte-ignore a11y-mouse-events-have-key-events -->
      <TableHead theadClass="sticky top-0 text-xs uppercase bg-neutral-100 dark:bg-neutral-700">
        <TableHeadCell padding={thClass}>
          <span on:click={() => sortTable('cat_name')}>
            Catastro {#if $sortKey==='cat_name'}{#if $sortDirection === 1}+{:else}-{/if}{/if}
          </span>
        </TableHeadCell>
        <TableHeadCell padding={thClass}>
          <span on:click={() => sortTable('osm_name')}>
            OSM {#if $sortKey==='osm_name'}{#if $sortDirection === 1}+{:else}-{/if}{/if}
          </span>
        </TableHeadCell>
        <TableHeadCell padding={thClass}>
          <span on:click={() => sortTable('source')}>
            Origen {#if $sortKey==='source'}{#if $sortDirection === 1}+{:else}-{/if}{/if}
          </span>
        </TableHeadCell>
      </TableHead>
      <TableBody>
        {#each $sortItems as street, i}
        <TableBodyRow class="hover:bg-amber-400 cursor-pointer" on:click={() => viewStreet(street.cat_name)}>
          <TableBodyCell {tdClass}>{street.cat_name}</TableBodyCell>
          <TableBodyCell {tdClass}>{street.osm_name}</TableBodyCell>
          <TableBodyCell {tdClass}>{street.source}</TableBodyCell>
        </TableBodyRow>
      {/each}
        </TableBody>
    </Table>
  </div>
  <div class="flex flex-row flex-grow">
    <div class="w-full flex-grow z-0">
      <Map bind:map>
        <ConsLayer data={data.addresses} bind:getConsLayer bind:imageRef={scrollImage}/>
        <StreetsLayer data={data.osmStreets}/>
      </Map>
    </div>
    <div class="max-md:w-3/4 md:max-w-md flex-grow overflow-scroll px-4 border-l-2 border-gray-200 dark:border-gray-600">
      <div class="h-full max-h-0">
        <FotosFachada
          data={data.addresses.features}
          on:viewed={showEntrance}
          bind:scrollImage 
          bind:viewImage
        />
      </div>
    </div>
  </div>
</div>
