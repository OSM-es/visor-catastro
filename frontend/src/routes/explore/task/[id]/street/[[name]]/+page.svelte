<script>
  import { onMount, setContext } from 'svelte'
  import { writable } from 'svelte/store'
	import { enhance } from '$app/forms'
  import {
    Badge,
    Button,
    ButtonGroup,
    Checkbox,
    Input,
    Label,
    Listgroup,
    ListgroupItem,
    Popover,
    TableBody,
    TableBodyCell,
    TableBodyRow,
    TableHead
  } from 'flowbite-svelte'
  import { ArrowLeft, ArrowRight, ArrowUturnDown, ArrowsPointingIn, Check, LockClosed, MagnifyingGlass, PencilSquare, XMark } from 'svelte-heros-v2'
  import debounce from 'lodash/debounce'

  import { afterNavigate, beforeNavigate, goto, invalidateAll } from '$app/navigation'
  import { page } from '$app/stores'

  import { login } from '$lib/user'
  import ResponsiveIcon from '$lib/components/ResponsiveIcon.svelte'
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
  let filter, items = [], getTable, filterTask=true
  
  $: streets = filterStreets(data.streets.slice(), filter, $street.cat_name, filterTask)
  $: index = items.findIndex((st) => st.cat_name === $street.cat_name)
  $: street.set(data.street)
  $: streetsToValidate = streets?.filter(s => s.validated) || []

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

  beforeNavigate(() => {
    if (data.user) {
      const url = `/papi/street/${$street.mun_code}/${$street.cat_name}/lock`
      fetch(url, {method: 'DELETE'})
    }
  })


  const centerMap = debounce(() => {
    map.getMap().invalidateSize()
    map.getMap().fitBounds(getConsLayer().getBounds())
  }, 100)

  function filterStreets(streets, filter, cat_name, filterTask) {
    return streets.filter((street) => {
      return (
        (!filterTask || street.in_task === filterTask) && (
          street.cat_name === cat_name || 
          street.cat_name.toLowerCase().includes(filter?.toLowerCase()) ||
          street.osm_name.toLowerCase().includes(filter?.toLowerCase())
        )
      )
    })
  }

  function showEntrance({ detail }) {
    const ref = detail
    const address = data.addresses.features.find(ad => ad.properties.tags?.ref === ref)
    address.layer.openPopup()
  }

  function viewStreet(name) {
    goto(`/explore/task/${$page.params?.id}/street/${name}`)
  }

  function gotoOsm() {
    const edit = zoom < 19 ? '' : 'edit'
    const url = `https://www.openstreetmap.org/${edit}#map=${zoom}/${center[0]}/${center[1]}`
    window.open(url, '_blank')
  }

  function gotoNextStreet(next) {
    const url = `/explore/task/${$page.params?.id}/street/${items[index + next]?.cat_name}`
    goto(url)
  }

  function dontReset() {
    return async ({ update }) => {
      await update({ reset: false })
      invalidateAll()
    }
  }

  function isLocked() {
    return data.street.is_locked && data.user.id !== data.street.owner?.id
  }
</script>

<div class="flex flex-col flex-grow">
  <div class="border-b border-neutral-200 dark:border-neutral-700">
    <div class="flex flex-row max-sm:flex-col px-4 pt-1 pb-0.5 space-x-6 bg-neutral-200 dark:bg-neutral-600 h-10 max-sm:h-20 items-center">
      <div class="flex flex-row space-x-2">
        <div class="lg:w-96">
          <Input size="sm" bind:value={filter} class="max-md:text-xs">
            <MagnifyingGlass slot="left" size=20/>
            <XMark slot="right" size=16 on:click={() => (filter = '')}/>
          </Input>
        </div>
        <div class="flex flex-row space-x-1 items-center">
          <Checkbox id="filterTask" bind:checked={filterTask}/>
          <Label for="filterTask">En la tarea</Label>
        </div>
      </div>
      <div>
        <Badge large color={streetsToValidate.length === streets.length ? 'green' : 'dark'}>
          {streetsToValidate.length} / {streets.length}
        </Badge>
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
          <Popover triggeredBy="#edit" placement="bottom-start" arrow={false} offset=2 class="flex flex-row" defaultClass="p-0">
            {#if zoom < 19}
              <p class="text-sm mx-3 my-2 whitespace-nowrap">Haz zoom para editar</p>
            {:else}
              <Listgroup class="divide-none w-36" active>
                <ListgroupItem on:click={gotoOsm}>Editar en OSM</ListgroupItem>
                <ListgroupItem>Editar con JOSM</ListgroupItem>
              </Listgroup>
            {/if}
          </Popover>
          <Button href="/explore/task/{$page.params?.id}" class="!px-2">
            <ResponsiveIcon title="Regresar a la tarea">
              <ArrowUturnDown size=18/>
            </ResponsiveIcon>
          </Button>
          <Button
            class="!px-2"
            on:click={() => (centerMap() || focusEditor())}
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
    </div>
    <form method="POST" use:enhance={dontReset}>
      <SortTable data={streets} bind:items bind:getTable divClass="relative overflow-scroll h-40" striped>
        <TableHead defaultRow={false} theadClass="sticky top-0 bg-neutral-100 dark:bg-neutral-700">
          <tr class="text-xs uppercase"> 
            <SortTableHeadCell key='cat_name' thClass="px-4 py-2 w-1/3">Catastro</SortTableHeadCell>
            <SortTableHeadCell key='osm_name' thClass="px-4 py-2 w-1/3">Osm</SortTableHeadCell>
            <SortTableHeadCell key='validated' thClass="px-4 py-2 w-1/6">Estado</SortTableHeadCell>
            <SortTableHeadCell key='source' thClass="px-4 py-2 w-1/6">Source</SortTableHeadCell>
          </tr>
        </TableHead>
        <TableBody>
          {#each items as street}
            {#if street.cat_name === data.street.cat_name}
              <tr id="editor" class="bg-amber-400 text-gray-900 dark:text-white font-medium">
                <td class="px-4 py-2">
                  <input name="mun_code" value={street.mun_code} hidden/>
                  <input name="cat_name" value={street.cat_name} hidden/>
                  {street.cat_name}
                </td>
                {#if data?.user && !isLocked()}
                  <StreetEdit osmStreets={data.osmStreets}></StreetEdit>
                {:else}
                  {#if isLocked()}
                    <td class="px-4 py-0">
                      Edición bloqueada por {street.owner.display_name}
                    </td>
                  {:else}
                    <td>
                      <Button size="sm" on:click={login} class="!px-2 h-8 focus:!ring-0">Registrate para editar</Button>
                    </td>
                  {/if}
                  <td class="px-4 py-0">
                    {#if isLocked()}
                      <LockClosed size=18/>
                    {:else if street.validated}
                      <Check size=18/>
                    {/if}
                  </td>
                {/if}
                <td class="px-4 py-2">
                  <input name="source" value={street.source} hidden/>
                  {street.source}
                </td>
              </tr>
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
              <TableBodyCell {tdClass}>
                {#if street.validated}<Check size=18/>{/if}
              </TableBodyCell>
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
        <ConsLayer
          data={data.addresses}
          api={data.api}
          bind:getConsLayer
          bind:imageRef={scrollImage}
        />
        <StreetsLayer data={data.osmStreets}/>
      </Map>
    </div>
    <div class="max-md:w-3/4 md:max-w-md flex-grow overflow-scroll px-4 border-l-2 border-gray-200 dark:border-gray-600">
      <div class="h-full max-h-0">
        <FotosFachada
          data={data.addresses.features}
          api={data.api}
          on:viewed={showEntrance}
          bind:scrollImage 
          bind:viewImage
        />
      </div>
    </div>
  </div>
</div>
