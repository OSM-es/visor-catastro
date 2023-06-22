<script>
  import { onMount } from 'svelte'
	import { enhance } from '$app/forms'
  import { Button, ButtonGroup, Input, Listgroup, ListgroupItem, Popover, Select, TableBody, TableBodyCell, TableBodyRow, TableHead } from 'flowbite-svelte'
  import { ArrowLeft, ArrowRight, ArrowUturnDown, ArrowUturnLeft, Check, MagnifyingGlass, PencilSquare, XMark } from 'svelte-heros-v2'
  
  import { currentTask } from '$lib/stores.js'
  import { goto, invalidateAll } from '$app/navigation'
  import { page } from '$app/stores'

  import { login } from '$lib/user'
  import ResponsiveButton from '$lib/components/ResponsiveButton.svelte'
  import Map from '$lib/components/maps/Map.svelte'
  import FotosFachada from '$lib/components/FotosFachada.svelte'
  import ConsLayer from '$lib/components/maps/ConsLayer.svelte'
  import StreetsLayer from '$lib/components/maps/StreetsLayer.svelte'
  import SortTable from '$lib/components/tables/SortTable.svelte'
  import SortTableHeadCell from '$lib/components/tables/SortTableHeadCell.svelte'
  
  export let data

  const bounds = [[data.bounds[1], data.bounds[0]], [data.bounds[3], data.bounds[2]]]
  const tdClass = "px-4 py-1 whitespace-nowrap"
  const btnClass = "!px-2 h-8 focus:!ring-0"
  const noImportar = 'No importar'

  let map, getConsLayer, scrollImage, viewImage, center, zoom
  let filter
  let prev_name, name, validated
  
  $: streets = filterStreets(data.streets.slice(), filter, data.cat_name)
  $: index = streets.findIndex((st) => st.cat_name === data.cat_name)

  onMount(() => {
    const m = map.getMap()
    m.fitBounds(bounds)
    m.setMaxBounds(bounds)
    m.setMinZoom(m.getZoom())
    m.fitBounds(getConsLayer().getBounds())
    page.subscribe(page => {
      validated = data.validated
      name = validated ? data.name || '' : (data.source === 'OSM' ? data.osm_name : '')
      prev_name = name
      if (map) {
        map.getMap().invalidateSize()
        map.getMap().fitBounds(getConsLayer().getBounds())
      }
      viewImage = page.url.searchParams.get('ref')
    })
  })


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
    goto(`/explore/${data.mun_code}/street/${name}`)
  }

  function undoStreet() {
    validated = false
  }
  
  function validateStreet() {
    validated = true
  }
  
  function gotoOsm() {
    const edit = zoom < 19 ? '' : 'edit'
    const url = `https://www.openstreetmap.org/${edit}#map=${zoom}/${center[0]}/${center[1]}`
    window.open(url, '_blank')
  }

  function gotoNextStreet(next) {
    const url = `/explore/${data.mun_code}/street/${streets[index + next]?.cat_name}`
    goto(url)
  }

  function osmStreetNames(name) {
    let names = data.osmStreets.features.map((feat) => (feat.properties?.tags?.name || ''))
    names = Array.from(new Set(names.filter((name) => (name ? true : false)))).sort()
    names = names.map((name) => ({ value: name, name }))
    names.push({value: '', name: noImportar})
    return names
  }

  function dontReset() {
    return async ({ update }) => {
      await update({ reset: false })
      invalidateAll()
    }
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
        <Button
          size="xs"
          on:click={() => gotoNextStreet(-1)}
          disabled={index <= 0}
        >
          <ArrowLeft size=14/>
        </Button>
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
        <ResponsiveButton
          title="Regresar a la tarea"
          href="/explore/task/{$currentTask}"
        >
          <ArrowUturnDown size=18/>
        </ResponsiveButton>
        <Button
          size="xs"
          on:click={() => gotoNextStreet(1)}
          disabled={index < 0 || index >= (streets.length - 1)}
        >
          <ArrowRight size=14/>
        </Button>
      </ButtonGroup>
    </div>
    <form method="POST" use:enhance={dontReset}>
      <SortTable data={streets} let:items={items}>
        <TableHead defaultRow={false} theadClass="sticky top-0 bg-neutral-100 dark:bg-neutral-700">
          <tr class="text-xs uppercase"> 
            <SortTableHeadCell key='cat_name'>Catastro</SortTableHeadCell>
            <SortTableHeadCell key='osm_name'>Osm</SortTableHeadCell>
            <SortTableHeadCell key='validated'>Estado</SortTableHeadCell>
            <SortTableHeadCell key='source'>Source</SortTableHeadCell>
          </tr>
          <tr>
            <th class="px-4 py-2 w-1/3">
              <input name="mun_code" value={data.mun_code} hidden/>
              <input name="cat_name" value={data.cat_name} hidden/>
              {data.cat_name}
            </th>
            {#if data?.user}
              <th>
                <input name="osm_name" value={data.osm_name} hidden/>
                <ButtonGroup class="w-full" size="sm">
                  <Select
                    name="name"
                    size="sm"
                    items={osmStreetNames(data.osm_name)}
                    bind:value={name}
                    placeholder=""
                    class="ml-2 py-1.5 !rounded-r-sm"
                  />
                  <Button class="!px-2.5 focus:!ring-0" on:click={() => (name = '')}>
                    <XMark size=14/>
                  </Button>
                </ButtonGroup>
                <input name="validated" value={validated} hidden/>
              </th>
              <th class="px-2 py-0 w-1/6">
                {#if data.validated && name === prev_name}
                  <ResponsiveButton 
                    type="submit" title="Deshacer" {btnClass} on:click={undoStreet}
                  >
                    <ArrowUturnLeft size=18/>
                  </ResponsiveButton>
                {:else}
                  <ResponsiveButton 
                    type="submit" title="Confirmar" {btnClass} on:click={validateStreet}
                  >
                    <Check size=18/>
                  </ResponsiveButton>
                {/if}
              </th>
            {:else}
              <th>
                <Button size="sm" on:click={login}>Registrate para editar</Button>
              </th>
              <th class="px-4 py-0 w-1/6">
                {#if data.validated}<Check size=18/>{/if}
              </th>
            {/if}
            <th class="px-4 py-2 w-1/6">
              <input name="source" value={data.source} hidden/>
              {data.source}
            </th>
          </tr>
        </TableHead>
        <TableBody>
          {#each items as street}
            {#if street.cat_name !== data.cat_name}
              <TableBodyRow
                class="hover:bg-amber-400 cursor-pointer"
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
