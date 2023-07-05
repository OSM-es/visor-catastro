<script>
  import { Button } from 'flowbite-svelte'
  import { onMount } from 'svelte'
  import { goto } from '$app/navigation'
	import { enhance } from '$app/forms'
  import { page } from '$app/stores'

  import { TASK_TYPE_VALUES, TASK_DIFFICULTY_VALUES } from '$lib/config'
  import FotosFachada from '$lib/components/FotosFachada.svelte'
  import Map from '$lib/components/maps/Map.svelte'
  import ConsLayer from '$lib/components/maps/ConsLayer.svelte'
  import FixmesLayer from '$lib/components/maps/FixmesLayer.svelte'
  import PartsLayer from '$lib/components/maps/PartsLayer.svelte'
  import StreetsLayer from '$lib/components/maps/StreetsLayer.svelte'
  import Tabs from '$lib/components/tabs/Tabs.svelte'
  import TabItem from '$lib/components/tabs/TabItem.svelte'
  import TaskActions from './TaskActions.svelte'
  import { currentTask } from '$lib/stores.js'

  export let data

  let map, center, zoom, initialCenter, initialZoom, getConsLayer, getUrl
  let buildings = data.task.buildings
  let fixmes = data.task?.fixmes
  let scrollImage, viewImage
  let taskColor = 'text-success-500'
  let tab = 'edicion'
  if (data.task.difficulty === 'MODERATE') taskColor = 'text-warning-500'
  if (data.task.difficulty === 'CHALLENGING') taskColor = 'text-danger-500'
  
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

  function updateStatus() {
    return async ({ update }) => {
      await update({ reset: false })
      if (!data.task.lock) exit()
    }
  }

  function exit() {
    currentTask.set(null)
    goto(`/explore?map=${getUrl(-1)}`)
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
  <div class="md:max-w-md w-full flex-grow overflow-scroll px-4 border-l-2 border-gray-200 dark:border-gray-600">
    <div class="sticky top-0 z-10 bg-white dark:bg-neutral-900">
      <div class="prose dark:prose-invert pt-4">
        <h3>Catastro de {data.task.name} ({data.task.muncode}) · #{data.task.id}</h3>
      </div>
      <Tabs bind:tab>
        <TabItem key={'edicion'}>Edición</TabItem>
        <TabItem key={'fotos'}>Fotos</TabItem>
        <TabItem key={'historial'}>Historial</TabItem>
      </Tabs>
    </div>
    <div class="h-full max-h-0">
      <div class:hidden={tab !== 'edicion'} class="prose dark:prose-invert pt-4">
        <p>
          Tarea tipo
          <span class="font-bold">{TASK_TYPE_VALUES[data.task.type]}</span>,
          dificultad
          <span class="font-bold {taskColor}">
            {TASK_DIFFICULTY_VALUES[data.task.difficulty]}</span>.
        </p>
        <form use:enhance={updateStatus} method="POST" class="mb-4">
          {#if data.task.bu_status !== data.task.ad_status}
            <h4>Edificios:</h4>
          {/if}
          <TaskActions
            status={data.task.bu_status}
            user={data.user}
            mapper={data.task.bu_mapper}
            task={data.task}
          />
          {#if data.task.bu_status !== data.task.ad_status}
            <h4>Direcciones:</h4>
            <TaskActions
              status={data.task.ad_status}
              user={data.user}
              mapper={data.task.ad_mapper}
              task={data.task}
            />
          {/if}
          {#if data.task.lock}
            <Button type="submit" name="lock" value="UNLOCK" color="alternative">
              {data.task.lock.text === 'MAPPING' ? 'No, detener mapeo' : 'Detener validación'}
            </Button>
          {:else if !data.task.currentLock}
            <Button on:click={exit} color="alternative">Seleccionar otra tarea</Button>
          {/if}
          {#if fixmes && data.task.bu_status !== 'VALIDATED'}
            <h4>Anotaciones:</h4>
            <ol class="mt-0">
              {#each fixmes?.features as fixme}
                <li class="my-0">
                  <a
                    href="{fixme.geometry.coordinates}"
                    on:click={centerMap}
                    data-sveltekit-preload-data="off"
                  >
                    {fixme.properties.fixme}
                  </a>
                </li>
              {/each}
            </ol>
          {/if}
        </form>
      </div>
      <div class:hidden={tab !== 'fotos'}>
        <FotosFachada
          data={buildings.features}
          on:viewed={showBuilding}
          bind:scrollImage 
          bind:viewImage
        />
      </div>
      <div class:hidden={tab !== 'historial'} class="prose dark:prose-invert">
        {data.task.history?.length}
        <ul>
          {#each data.task.history as h}
          <li>{h.date} {h.user} {h.action} {h.text} bu:{h.buildings} ad:{h.addresses}</li>
          {/each}
        </ul>
      </div>
    </div>
  </div>
</div>
