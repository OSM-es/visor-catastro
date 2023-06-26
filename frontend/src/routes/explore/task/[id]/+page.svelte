<script>
  import { Button, Select, Label } from 'flowbite-svelte'
  import { onMount } from 'svelte'
  import { goto } from '$app/navigation'
	import { enhance } from '$app/forms'
  import { page } from '$app/stores'

  import { TASK_COLORS, TASK_TYPE_VALUES, TASK_DIFFICULTY_VALUES, TASK_STATUS_VALUES } from '$lib/config'
  import FotosFachada from '$lib/components/FotosFachada.svelte'
  import Map from '$lib/components/maps/Map.svelte'
  import ConsLayer from '$lib/components/maps/ConsLayer.svelte'
  import FixmesLayer from '$lib/components/maps/FixmesLayer.svelte'
  import PartsLayer from '$lib/components/maps/PartsLayer.svelte'
  import StreetsLayer from '$lib/components/maps/StreetsLayer.svelte'
  import { currentTask } from '$lib/stores.js'
  
  export let data

  let map, center, zoom, initialCenter, initialZoom, getConsLayer, getUrl
  let buildings = data.task.buildings
  let fixmes = data.task?.fixmes
  let scrollImage, viewImage
  
  $: isEditor = data.user?.role && data.user.role != 'READ_ONLY'
  
  
  function centerMap(event) {
    const point = event.target.attributes.href.value.split(',')
    map.getMap().panTo([point[1], point[0]])
    event.preventDefault()
  }

  function showBuilding({ detail }) {
    const ref = detail
    const building = buildings.features.find(building => building.properties.tags?.ref === ref)
    building.layer.openPopup()
  }

  function exit() {
    currentTask.set(null)
    goto(`/explore?map=${getUrl(-1)}`)
  }

  function updateStatus() {
    return async ({ update }) => {
      await update()
      exit()
    }
  }

  function doTutorial() {
    goto('/learn/' + (data?.user?.tutorial ? data.user.tutorial.next : 'login'))
  }

  currentTask.set(data.task.id)
  
  onMount(() => {
    map.getMap().fitBounds(getConsLayer().getBounds())
    initialZoom = zoom
    initialCenter = center
    page.subscribe(page => viewImage = page.url.searchParams.get('ref'))
  })
</script>

<div class="flex flex-col md:flex-row flex-grow">
  <div class="w-full flex-grow z-0">
    <Map bind:map bind:center bind:zoom bind:getUrl minZoom=15>
      <StreetsLayer data={data.task.osmStreets}/>
      <PartsLayer data={data.task.parts}/>
      <ConsLayer data={buildings} bind:getConsLayer bind:imageRef={scrollImage}/>
      {#if fixmes}<FixmesLayer data={fixmes}/>{/if}
    </Map>
  </div>
  <div class="md:max-w-md w-full flex-grow overflow-scroll px-4 pt-8 border-l-2 border-gray-200 dark:border-gray-600">
    <div class="h-full max-h-0">
      <div class="prose dark:prose-invert">
        <ul>
          <li>Catastro de {data.task.muncode}</li>
          <li>Referencia: {data.task.localId}</li>
          <li>Tipo: {TASK_TYPE_VALUES[data.task.type]}</li>
          <li>Dificultad: {TASK_DIFFICULTY_VALUES[data.task.difficulty]}</li>
        </ul>
        {#if fixmes}
          <p>Anotaciones:</p>
          {#each fixmes?.features as fixme}
            <ol>
              <li>
                <a
                  href="{fixme.geometry.coordinates}"
                  on:click={centerMap}
                  data-sveltekit-preload-data="off"
                >
                  {fixme.properties.fixme}
                </a>
              </li>
            </ol>
          {/each}
        {/if}
        {#if data.task.streets?.length}
          <p>Calles:</p>
          {#each data.task.streets as street}
            <ul>
              <li>
                <a href="/explore/{data.task.muncode}/street/{street.cat_name}">
                  {street.cat_name}
                </a>
              </li>
            </ul>
          {/each}
        {/if}
        <form use:enhance={updateStatus} method="POST" class="mb-4">
          <Label>
            Estado:
            <Select
              name="status"
              value={data.task.status}
              items={Object.entries(TASK_STATUS_VALUES).map(([value, name]) => ({ value, name }))}
              placeholder=""
              disabled={!isEditor}
            />
          </Label>
          <Button on:click={exit} color="alternative">Cancelar</Button>
          {#if isEditor}
            <Button type="submit">Guardar</Button>
          {:else}
            <Button on:click={doTutorial}>Completa el tutorial para editar</Button>
          {/if}
        </form>
      </div>
      <FotosFachada
        data={buildings.features}
        on:viewed={showBuilding}
        bind:scrollImage 
        bind:viewImage
      />
    </div>
  </div>
</div>
