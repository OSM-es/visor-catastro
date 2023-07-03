<script>
  import { Button, Select, Label } from 'flowbite-svelte'
  import { onMount } from 'svelte'
  import { goto } from '$app/navigation'
	import { enhance } from '$app/forms'
  import { page } from '$app/stores'

  import { TASK_TYPE_VALUES, TASK_DIFFICULTY_VALUES, TASK_STATUS_VALUES, TASK_UNDO_VALUES } from '$lib/config'
  import FotosFachada from '$lib/components/FotosFachada.svelte'
  import Map from '$lib/components/maps/Map.svelte'
  import ConsLayer from '$lib/components/maps/ConsLayer.svelte'
  import FixmesLayer from '$lib/components/maps/FixmesLayer.svelte'
  import PartsLayer from '$lib/components/maps/PartsLayer.svelte'
  import StreetsLayer from '$lib/components/maps/StreetsLayer.svelte'
  import TaskActions from './TaskActions.svelte'
  import { currentTask } from '$lib/stores.js'

  export let data

  let map, center, zoom, initialCenter, initialZoom, getConsLayer, getUrl
  let buildings = data.task.buildings
  let fixmes = data.task?.fixmes
  let scrollImage, viewImage
  let taskColor = 'text-success-500'
  if (data.task.difficulty === 'MODERATE') taskColor = 'text-warning-500'
  if (data.task.difficulty === 'CHALLENGING') taskColor = 'text-danger-500'
  
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

  function updateStatus() {
    return async ({ update }) => {
      await update({ reset: false })
      if (!data.task.is_locked) exit()
    }
  }

  function doTutorial() {
    goto('/learn/' + (data?.user?.tutorial ? data.user.tutorial.next : 'login'))
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
  <div class="md:max-w-md w-full flex-grow overflow-scroll px-4 pt-8 border-l-2 border-gray-200 dark:border-gray-600">
    <div class="h-full max-h-0">
      <div class="prose dark:prose-invert">
        <form use:enhance={updateStatus} method="POST" class="mb-4">
          <h3 class="mt-0">Catastro de {data.task.name} ({data.task.muncode}) · #{data.task.id}</h3>
          <p>
            Tarea tipo
            <span class="font-bold">{TASK_TYPE_VALUES[data.task.type]}</span>,
            dificultad
            <span class="font-bold {taskColor}">
              {TASK_DIFFICULTY_VALUES[data.task.difficulty]}</span>.
          </p>
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
          {#if data.task.undo_status}
            <Button type="submit" name="undo_status" value={data.task.undo_status} color="alternative">
              {TASK_UNDO_VALUES[data.task.undo_status]}
            </Button>
          {:else}
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
        <!--form use:enhance={updateStatus} method="POST" class="mb-4">
          bu: {data.task.bu_status}
          ad: {data.task.ad_status}
          <Label>
            Estado:
            <Select
              name="status"
              items={Object.entries(TASK_STATUS_VALUES).map(([value, name]) => ({ value, name }))}
              placeholder=""
              disabled={!isEditor}
            />
          </Label>
          <div class="flex space-x-8 mb-8">
            <label>
              <input
                type="radio"
                name="buildings"
                value="true"
              />
              Edificios
            </label>
            <label>
              <input
                type="radio"
                name="addresses"
                value="true"
              />
              Direcciones
            </label>
          </div>
          <Button on:click={exit} color="alternative">Cancelar</Button>
          {#if isEditor}
            <Button type="submit">Guardar</Button>
          {:else}
            <Button on:click={doTutorial}>Completa el tutorial para editar</Button>
          {/if}
        </form-->
      </div>
      <div class="hidden">
      <FotosFachada
        data={buildings.features}
        on:viewed={showBuilding}
        bind:scrollImage 
        bind:viewImage
      />
      </div>
      {data.task.history?.length}
      <ul>
        {#each data.task.history as h}
        <li>{h.date} {h.user} {h.action} bu:{h.buildings} ad:{h.addresses}</li>
        {/each}
      </ul>
    </div>
  </div>
</div>
