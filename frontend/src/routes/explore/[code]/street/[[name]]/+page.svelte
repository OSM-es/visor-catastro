<script>
  import { onMount, setContext } from 'svelte'
  import { writable } from 'svelte/store'
	import { enhance } from '$app/forms'
  import { Button, ButtonGroup, Input, Listgroup, ListgroupItem, Popover, TableBody, TableBodyCell, TableBodyRow, TableHead } from 'flowbite-svelte'
  import { ArrowLeft, ArrowRight, ArrowUturnDown, ArrowsPointingIn, Check, MagnifyingGlass, PencilSquare, XMark } from 'svelte-heros-v2'
  import debounce from 'lodash/debounce'

  import { currentTask } from '$lib/stores.js'
  import { afterNavigate, goto, invalidateAll } from '$app/navigation'
  import { page } from '$app/stores'

  import ResponsiveButton from '$lib/components/ResponsiveButton.svelte'
  import Map from '$lib/components/maps/Map.svelte'
  import FotosFachada from '$lib/components/FotosFachada.svelte'
  import ConsLayer from '$lib/components/maps/ConsLayer.svelte'
  import StreetsLayer from '$lib/components/maps/StreetsLayer.svelte'
  import SortTable from '$lib/components/tables/SortTable.svelte'
  import SortTableHeadCell from '$lib/components/tables/SortTableHeadCell.svelte'
  import StreetEdit from './StreetEdit.svelte'
  
  export let data

  const bounds = [[data.bounds[1], data.bounds[0]], [data.bounds[3], data.bounds[2]]]
  const tdClass = "px-4 py-1 whitespace-nowrap"
  const noImportar = 'No importar'

  const street = writable(data.street)

  setContext('street', street)

  let map, getConsLayer, scrollImage, viewImage, center, zoom
  let filter, items = [], getTable
  
  $: streets = filterStreets(data.streets.slice(), filter, $street.cat_name)
  $: index = items.findIndex((st) => st.cat_name === $street.cat_name)
  $: street.set(data.street)
  

  const focusEditor = debounce(() => {
    const editor = document.getElementById('editor')
    editor?.scrollIntoView({ block: 'center', behavior: 'smooth' })
  }, 100)


  onMount(() => {
    const m = map.getMap()
    m.fitBounds(bounds)
    m.setMaxBounds(bounds)
    m.setMinZoom(m.getZoom())
    m.fitBounds(getConsLayer().getBounds())
    getTable().subscribe(focusEditor)
  })

  afterNavigate(() => {
    viewImage = $page.url.searchParams.get('ref')
    focusEditor()
    centerMap()
  })


  const centerMap = debounce(() => {
    map.getMap().invalidateSize()
    map.getMap().fitBounds(getConsLayer().getBounds())
  }, 100)

  function filterStreets(streets, filter, cat_name) {
    return streets.filter((street) => {
      return (
        street.cat_name === cat_name || 
        street.cat_name.toLowerCase().includes(filter?.toLowerCase()) ||
        street.osm_name.toLowerCase().includes(filter?.toLowerCase())
      )
    })
  }

  function showEntrance({ detail }) {
    const ref = detail
    const address = data.addresses.features.find(ad => ad.properties.tags?.ref === ref)
    address.layer.openPopup()
  }

  function viewStreet(name) {
    goto(`/explore/${$street.mun_code}/street/${name}`)
  }

  function gotoOsm() {
    const edit = zoom < 19 ? '' : 'edit'
    const url = `https://www.openstreetmap.org/${edit}#map=${zoom}/${center[0]}/${center[1]}`
    window.open(url, '_blank')
  }

  function gotoNextStreet(next) {
    const url = `/explore/${$street.mun_code}/street/${items[index + next]?.cat_name}`
    goto(url)
  }

  function dontReset() {
    return async ({ update }) => {
      await update({ reset: false })
      invalidateAll()
    }
  }
</script>

<div class="flex flex-col flex-grow">
  <div class="border-b border-neutral-200 dark:border-neutral-700">
    <div class="flex flex-row px-4 pt-1 pb-0.5 space-x-2 bg-neutral-200 dark:bg-neutral-600 h-10">
      <div class="lg:w-96">
        <Input size="sm" bind:value={filter} class="max-md:text-xs">
          <MagnifyingGlass slot="left" size=20/>
          <XMark slot="right" size=16 on:click={() => (filter = '')}/>
        </Input>
      </div>
      <ButtonGroup>
        <Button
          class="!px-2"
          on:click={() => gotoNextStreet(-1)}
          disabled={index <= 0}
        >
          <ArrowLeft size=14/>
        </Button>
        <Button id="edit" class="!px-2" disabled={zoom < 19}>
          <PencilSquare size=18/>
        </Button>
        <Popover triggeredBy="#edit" placement="bottom-start" arrow={false} offset=2 class="flex flex-row" defaultClass="p-0 w-48">
          {#if zoom < 19}
            <p class="text-sm mx-3 my-2 whitespace-nowrap">Haz zoom en el mapa para editar</p>
          {:else}
            <Listgroup class="divide-none" active>
              <ListgroupItem on:click={gotoOsm}>Editar en OSM</ListgroupItem>
              <ListgroupItem>Editar con JOSM</ListgroupItem>
            </Listgroup>
          {/if}
        </Popover>
        <ResponsiveButton
          btnClass="!px-2"
          title="Regresar a la tarea"
          href="/explore/task/{$currentTask}"
        >
          <ArrowUturnDown size=18/>
        </ResponsiveButton>
        <Button
          class="!px-2"
          on:click={() => (centerMap() || focusEditor())}
          disabled={index < 0 || index >= (streets.length - 1)}
        >
          <ArrowsPointingIn size=20/>
        </Button>
        <Button
          class="!px-2"
          on:click={() => gotoNextStreet(1)}
          disabled={index < 0 || index >= (streets.length - 1)}
        >
          <ArrowRight size=14/>
        </Button>
      </ButtonGroup>
    </div>
    <form method="POST" use:enhance={dontReset}>
      <SortTable data={streets} bind:items bind:getTable divClass="relative overflow-scroll h-40" striped>
        <TableHead defaultRow={false} theadClass="sticky top-0 bg-neutral-100 dark:bg-neutral-700">
          <tr class="text-xs uppercase"> 
            <SortTableHeadCell key='cat_name'>Catastro</SortTableHeadCell>
            <SortTableHeadCell key='osm_name'>Osm</SortTableHeadCell>
            <SortTableHeadCell key='validated'>Estado</SortTableHeadCell>
            <SortTableHeadCell key='source'>Source</SortTableHeadCell>
          </tr>
        </TableHead>
        <TableBody>
          {#each items as street}
            {#if street.cat_name === data.street.cat_name}
              <StreetEdit id="editor" {data}></StreetEdit>
            {:else}
            <TableBodyRow
              id={street.cat_name === data.street.cat_name ? 'activeStreet' : undefined}
              class="hover:bg-amber-400 {street.cat_name === data.street.cat_name ? '!bg-amber-400' : 'cursor-pointer'}"
              on:click={() => viewStreet(street.cat_name)}
            >
              <TableBodyCell {tdClass}>{street.cat_name}</TableBodyCell>
              <TableBodyCell {tdClass} class={street.validated ? '' : '!text-neutral-500'}>
                {street.validated ? street.name || noImportar : street.osm_name}
              </TableBodyCell>
              <TableBodyCell {tdClass}>{#if street.validated}<Check size=18/>{/if}</TableBodyCell>
              <TableBodyCell {tdClass}>{street.source}</TableBodyCell>
            </TableBodyRow>
            {/if}
          {/each}
        </TableBody>
      </SortTable>
    </form>
  </div>
  <div class="flex flex-row flex-grow">
    <div class="w-full flex-grow z-0">
      <Map bind:map bind:zoom bind:center>
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
