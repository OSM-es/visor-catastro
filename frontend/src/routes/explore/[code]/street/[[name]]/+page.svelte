<script>
  import { onMount } from 'svelte'
  import { Button, ButtonGroup, Input, Listgroup, ListgroupItem, Popover, Select, TableBody, TableBodyCell, TableBodyRow, TableHead, TableHeadCell, Tooltip } from 'flowbite-svelte'
  import { ArrowLeft, ArrowRight, ArrowUturnDown, MagnifyingGlass, PencilSquare, XMark } from 'svelte-heros-v2'
  
  import { currentTask } from '$lib/stores.js'
  import { goto } from '$app/navigation'
  import { page } from '$app/stores'
  
  import Map from '$lib/components/maps/Map.svelte'
  import FotosFachada from '$lib/components/FotosFachada.svelte'
  import ConsLayer from '$lib/components/maps/ConsLayer.svelte'
  import StreetsLayer from '$lib/components/maps/StreetsLayer.svelte'
  import SortTable from '$lib/components/tables/SortTable.svelte'
  import SortTableHeadCell from '$lib/components/tables/SortTableHeadCell.svelte'
  
  export let data

  const bounds = [[data.bounds[1], data.bounds[0]], [data.bounds[3], data.bounds[2]]]

  let map, getConsLayer, scrollImage, viewImage, center, zoom
  let filter
  let items = []
  
  $: isEditor = data.user?.role && data.user.role != 'READ_ONLY'
  $: osm_name = data.osm_name || ''
 
  const tdClass = "px-4 py-1 whitespace-nowrap"


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


  function filterStreet(filter, street, cat_name) {
    return street.cat_name !== cat_name && (
      street.cat_name.toLowerCase().includes(filter?.toLowerCase()) ||
      street.osm_name.toLowerCase().includes(filter?.toLowerCase())
    )
  }

  function showEntrance({ detail }) {
    const ref = detail
    const address = data.addresses.features.find(ad => ad.properties.tags?.ref === ref)
    address.layer.openPopup()
  }

  function viewStreet(name) {
    goto(`/explore/${data.mun_code}/street/${name}`)
  }
  
  function gotoOsm() {
    const edit = zoom < 19 ? '' : 'edit'
    const url = `https://www.openstreetmap.org/${edit}#map=${zoom}/${center[0]}/${center[1]}`
    window.open(url, '_blank')
  }

  function osmStreetNames(name) {
    let names = data.osmStreets.features.map((feat) => (feat.properties?.tags?.name || ''))
    names = Array.from(new Set(names.filter((name) => (name ? true : false)))).sort()
    names = names.map((name) => ({ value: name, name }))
    names.push({value: '', name: 'No importar'})
    return names
  }
</script>

<div class="flex flex-col flex-grow">
  <div class="border-b border-neutral-200 dark:border-neutral-700 ">
    <div class="flex flex-row px-4 py-1 space-x-2 bg-neutral-200 dark:bg-neutral-600">
      <div class="lg:w-96">
        <Input size="sm" bind:value={filter} class="max-md:text-xs">
          <MagnifyingGlass slot="left" size=20/>
          <XMark slot="right" size=16 on:click={() => (filter = '')}/>
        </Input>
      </div>
      <ButtonGroup>
        <Button size="xs" disabled><ArrowLeft size=14/></Button>
        <Button id="edit" size="xs">
          <PencilSquare size=18/>
        </Button>
        <Popover triggeredBy="#edit" placement="bottom-start" arrow={false} offset=2 class="flex flex-row" defaultClass="p-0 w-48">
          {#if zoom < 19}
            <p class="text-sm mx-3 my-2 whitespace-nowrap">Haz zoom para editar</p>
          {:else}
            <Listgroup class="divide-none" active>
              <ListgroupItem on:click={gotoOsm}>Editar en OSM</ListgroupItem>
              <ListgroupItem>Editar con JOSM</ListgroupItem>
            </Listgroup>
          {/if}
        </Popover>
        <Button size="xs" href="/explore/task/{$currentTask}">
          <ArrowUturnDown size=18/>
          <span class="max-lg:hidden ml-1">Regresar a la tarea</span>
        </Button>
        <Tooltip placement="bottom" class="lg:hidden">Regresar a la tarea</Tooltip>
        <Button size="xs"><ArrowRight size=14/></Button>
      </ButtonGroup>
    </div>
    <SortTable data={data.streets} bind:items>
      <TableHead defaultRow={false} theadClass="sticky top-0 bg-neutral-100 dark:bg-neutral-700">
        <tr class="text-xs uppercase"> 
          <SortTableHeadCell key='cat_name'>Catastro</SortTableHeadCell>
          <SortTableHeadCell key='osm_name'>Osm</SortTableHeadCell>
          <SortTableHeadCell key='source'>Source</SortTableHeadCell>
        </tr>
        <tr>
          <TableHeadCell padding="px-4 py-2 w-2/5">
            {data.cat_name}
          </TableHeadCell>
          <ButtonGroup class="w-full" size="sm">
            <Select
              size="sm"
              items={osmStreetNames(osm_name)}
              value={osm_name}
              placeholder=""
              class="ml-2 py-1.5 !rounded-r-sm"
            />
            <Button class="!px-2.5 !py-0 focus:!ring-0" on:click={() => (osm_name = '')}>
              <XMark size=14/>
            </Button>
          </ButtonGroup>
          <TableHeadCell padding="px-4 py-2 w-1/5">
            {data.source}
          </TableHeadCell>
        </tr>
      </TableHead>
      <TableBody>
        {#each items as street}
          {#if filterStreet(filter, street, data.cat_name)}
            <TableBodyRow class="hover:bg-amber-400 cursor-pointer" on:click={() => viewStreet(street.cat_name)}>
              <TableBodyCell {tdClass}>{street.cat_name}</TableBodyCell>
              <TableBodyCell {tdClass}>{street.osm_name}</TableBodyCell>
              <TableBodyCell {tdClass}>{street.source}</TableBodyCell>
            </TableBodyRow>
          {/if}
        {/each}
      </TableBody>
    </SortTable>
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
