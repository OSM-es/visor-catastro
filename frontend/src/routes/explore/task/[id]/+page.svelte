<script>
  import { Avatar, Badge, Button, Indicator, Listgroup, Tooltip } from 'flowbite-svelte'
  import { Clock } from 'svelte-heros-v2'
  import { afterNavigate } from '$app/navigation'
  import { goto } from '$app/navigation'
  import RelativeTime from 'svelte-relative-time'

  import { TASK_TYPE_VALUES, TASK_DIFFICULTY_VALUES, TASK_ACTION_VALUES, TASK_ACTION_TEXT } from '$lib/config'
  import FotosFachada from '$lib/components/FotosFachada.svelte'
  import Map from '$lib/components/maps/Map.svelte'
  import ConsLayer from '$lib/components/maps/ConsLayer.svelte'
  import FixmesLayer from '$lib/components/maps/FixmesLayer.svelte'
  import PartsLayer from '$lib/components/maps/PartsLayer.svelte'
  import StreetsLayer from '$lib/components/maps/StreetsLayer.svelte'
  import Tabs from '$lib/components/tabs/Tabs.svelte'
  import TabItem from '$lib/components/tabs/TabItem.svelte'
  import TaskActions from './TaskActions.svelte'
  
  export let data

  $: buildings = data.task.buildings

  let map, center, zoom, initialCenter, initialZoom, getConsLayer, getUrl
  let fixmes = data.task?.fixmes
  let scrollImage, viewImage, imageCount
  let taskColor = 'text-success-500'
  let tab = 'edicion'
  if (data.task.difficulty === 'MODERATE') taskColor = 'text-warning-500'
  if (data.task.difficulty === 'CHALLENGING') taskColor = 'text-danger-500'

  const rtf = new Intl.RelativeTimeFormat('es', {numeric: 'auto'})
  const indicatorClass = 'font-bold text-white dark:text-gray-800 mb-0.5 '

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

  function isSplitted(task) {
    const needMapping = ['READY', 'INVALIDATED', 'NEED_UPDATE']
    if (task.bu_status !== task.ad_status) {
      return !needMapping.includes(task.bu_status) || !needMapping.includes(task.ad_status)
    }
    return false
  }

  afterNavigate(({to}) => {
    if (to.route.id === '/explore/task/[id]') {
      viewImage = to.url.searchParams.get('ref')
      map.getMap().fitBounds(getConsLayer().getBounds())
      initialZoom = zoom
      initialCenter = center
    }
  })
</script>

<div class="flex flex-col md:flex-row flex-grow">
  <div class="w-full flex-grow z-0">
    <Map bind:map bind:center bind:zoom bind:getUrl minZoom=15>
      <StreetsLayer data={data.task.osmStreets}/>
      <PartsLayer data={data.task.parts}/>
      <ConsLayer
        data={buildings}
        api={data.api}
        bind:getConsLayer
        bind:imageRef={scrollImage}
      />
      {#if fixmes}<FixmesLayer data={fixmes}/>{/if}
    </Map>
  </div>municip
  <div class="md:max-w-md w-full flex-grow overflow-scroll px-4 border-l-2 border-gray-200 dark:border-gray-600">
    <div class="sticky top-0 z-10 bg-white dark:bg-neutral-900">
      <div class="prose dark:prose-invert pt-4">
        <h3>Catastro de {data.task.municipality.name} ({data.task.muncode}) · #{data.task.id}</h3>
      </div>
      <Tabs bind:tab>
        <TabItem key={'edicion'}>Edición</TabItem>
        {#if imageCount}
          <TabItem key={'fotos'}>
            Fotos
            <Indicator color="blue" size="lg" placement="center-right">
              <span class={indicatorClass + (imageCount < 10 ? 'text-xs' : 'text-[0.6rem]')}>
                {#if imageCount < 100}{imageCount}{/if}
              </span>
            </Indicator>
          </TabItem>
        {/if}
        <TabItem key={'historial'}>
          Historial
          {#if data.task.history?.length}
            <Indicator color="blue" size="lg" placement="center-right">
              <span class={indicatorClass + (data.task.history.length < 10 ? 'text-xs' : 'text-[0.6rem]')}>
                {#if data.task.history.length < 100}{data.task.history.length}{/if}
              </span>
            </Indicator>
          {/if}
        </TabItem>
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
        {#if data.task.municipality.lock }
          <p class="text-danger-500 font-bold">Municipio bloqueado para actualización.</p>
          <Button
            on:click={() => goto(`/explore?map=${getUrl(-1)}`)}
            color="alternative"
          >
            Cancelar
          </Button>
        {:else}
          {#if !data.task.lock || data.task.lock?.buildings}
            <TaskActions
              title={'buildings'}
              status={data.task.bu_status}
              mapper={data.task.bu_mapper}
              user={data.user}
              task={data.task}
              exitUrl={getUrl}
            />
          {/if}
          {#if isSplitted(data.task) || (data.task.lock?.addresses && !data.task.lock?.buildings)}
            <TaskActions
              title={'addresses'}
              status={data.task.ad_status}
              mapper={data.task.ad_mapper}
              user={data.user}
              task={data.task}
              exitUrl={getUrl}
            />
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
                    {fixme.properties.type}
                    {fixme.properties.fixme}
                  </a>
                </li>
              {/each}
            </ol>
          {/if}
        {/if}
      </div>
      <div class:hidden={tab !== 'fotos'}>
        <FotosFachada
          data={buildings.features}
          api={data.api}
          on:viewed={showBuilding}
          bind:scrollImage 
          bind:viewImage
          bind:imageCount
        />
      </div>
      <div class:hidden={tab !== 'historial'}>
        {#if data.task.history?.length}
        <Listgroup items={data.task.history} let:item>
          <div class="flex items-center space-x-4">
            <Avatar src={item.avatar} data-name={item.user}/>
            <p>
              {TASK_ACTION_VALUES[item.action]}
              {TASK_ACTION_TEXT[item.text]}
              {#if item.addresses != item.buildings}
                {item.buildings ? 'edificios' : 'direcciones'}
              {/if}
              <Badge color="black" border>
                <Clock size=14 variation="solid" class="mr-1"/>
                <RelativeTime date={new Date(item.date)} locale={'es-ES'}/>
              </Badge>
            </p>
          </div>
        </Listgroup>
        <Tooltip triggeredBy="[data-name]" on:show={e => name = e.target.dataset.name}>
          {name}
        </Tooltip>
        {:else}
          <div class="prose dark:prose-invert pt-4">
            <p>No ha habido actividad.</p>
          </div>
        {/if}
      </div>
    </div>
  </div>
</div>
