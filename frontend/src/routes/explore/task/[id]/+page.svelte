<script>
  import { Button, Indicator } from 'flowbite-svelte'
  import { afterNavigate } from '$app/navigation'
  import { goto } from '$app/navigation'
  import { t } from '$lib/translations'

  import { exploreCode } from '$lib/stores.js'
  import FotosFachada from '$lib/components/FotosFachada.svelte'
  import Map from '$lib/components/maps/Map.svelte'
  import ConsLayer from '$lib/components/maps/ConsLayer.svelte'
  import FixmesLayer from '$lib/components/maps/FixmesLayer.svelte'
  import PartsLayer from '$lib/components/maps/PartsLayer.svelte'
  import StreetsLayer from '$lib/components/maps/StreetsLayer.svelte'
  import Tabs from '$lib/components/tabs/Tabs.svelte'
  import TabItem from '$lib/components/tabs/TabItem.svelte'
  import TaskActions from './TaskActions.svelte'
  import FixmeList from './FixmeList.svelte'
  import HistoryList from './HistoryList.svelte'
  
  export let data

  $: buildings = data.task.buildings

  let map, center, zoom, initialCenter, initialZoom, getConsLayer, getUrl
  let fixmes = data.task?.fixmes
  let selectedFixme = null
  let scrollImage, viewImage, imageCount
  let tab = 'edicion'
  let taskColor = 'text-success-500'
  if (data.task.difficulty === 'MODERATE') taskColor = 'text-warning-500'
  if (data.task.difficulty === 'CHALLENGING') taskColor = 'text-danger-500'

  const rtf = new Intl.RelativeTimeFormat('es', {numeric: 'auto'})
  const indicatorClass = 'font-bold text-white dark:text-gray-800 mb-0.5 '

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
  
  function exit() {
    const url = $exploreCode ? `/explore/${$exploreCode}` : '/explore'
    goto(`${url}?map=${getUrl(-1)}`)
  }

  afterNavigate(({from, to}) => {
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
      {#if fixmes}<FixmesLayer data={fixmes} bind:selected={selectedFixme}/>{/if}
    </Map>
  </div>
  <div class="md:max-w-md w-full flex-grow overflow-scroll px-4 border-l-2 border-gray-200 dark:border-gray-600">
    <div class="sticky top-0 z-10 bg-white dark:bg-neutral-900">
      <div class="prose dark:prose-invert pt-4">
        <h3>{$t('explore.cadastreof')} {data.task.municipality.name} ({data.task.muncode}) · #{data.task.id}</h3>
      </div>
      <Tabs bind:tab>
        <TabItem key={'edicion'}>{$t('task.edit')}</TabItem>
        {#if imageCount}
          <TabItem key={'fotos'}>
            {$t('task.images')}
            <Indicator color="blue" size="lg" placement="center-right">
              <span class={indicatorClass + (imageCount < 10 ? 'text-xs' : 'text-[0.6rem]')}>
                {#if imageCount < 100}{imageCount}{/if}
              </span>
            </Indicator>
          </TabItem>
        {/if}
        <TabItem key={'historial'}>
          {$t('task.history')}
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
          {@html $t('task.type', { type: $t('explore.' + data.task.type) })},
          {@html $t('task.diff', { diff: $t('explore.' + data.task.difficulty), taskColor })}
        </p>
        {#if data.task.municipality.lock }
          <p class="text-danger-500 font-bold">{$t('task.updatelock')}</p>
          <Button on:click={exit} color="alternative">{$t('common.back')}</Button>
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
            <FixmeList {fixmes} {map} bind:selected={selectedFixme} lock={data.task.lock}/>
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
        <HistoryList items={data.task.history}/>
      </div>
    </div>
  </div>
</div>
