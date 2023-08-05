<script>
  import { Progressbar, Spinner } from 'flowbite-svelte'
  import { afterNavigate, goto } from '$app/navigation'
  import { GeoJSON } from 'svelte-leafletjs'
  import { locale, t } from '$lib/translations'
  import { page } from '$app/stores'
  import 'leaflet.pattern'

  import TaskList from './TaskList.svelte'
  import TaskStatus from './TaskStatus.svelte'
  import ProjList from './ProjList.svelte'
  import StatsSection from '$lib/components/StatsSection.svelte'
  import Map from '$lib/components/maps/Map.svelte'
  import Legend from '$lib/components/maps/Legend.svelte'
  import { exploreCode } from '$lib/stores.js'
  import { AREA_BORDER, TASK_COLORS, TASK_LOCKED_COLOR, TASK_THR, MUN_THR } from '$lib/config'

  export let data

  let map, geoJsonData, activeItem, getUrl, getGeoJSON
  let muncode, type, difficulty, ad_status, bu_status
  let center = data.center
  let zoom = data.zoom
  let project
  let timer
  let pattern
  
  const rightBarClass = 'md:max-w-md w-full flex-grow overflow-scroll px-4 '
    + 'border-l-2 border-neutral-300 dark:border-neutral-500 dark:bg-neutral-800'

  const target = (zoom) => (
    zoom >= TASK_THR ? 
    'tasks' : 
    (zoom >= MUN_THR ? 'municipalities' : 'provinces')
  )
  const fmt = new Intl.NumberFormat($locale, { maximumFractionDigits: 2, style: "percent" })

  $: code = $page?.params?.code
  $: tasks = filterTasks(geoJsonData, muncode, type, difficulty, ad_status, bu_status)
  $: dataPromise = fetchData(map, zoom, code)
  $: statsPromise = fetchStats(code)
  
  
  async function fetchData(map, zoom, code) {
    if (!map) return null
    const bounds = map?.getMap().getBounds().toBBoxString()
    geoJsonData = await data.streamed.geoJsonData(target(zoom), code, bounds)
    if (code && geoJsonData.features.length) {
      project = geoJsonData.features[0].properties
    }
    return geoJsonData
  }

  async function fetchStats(code) {
    if (code) return await data.streamed.stats(code)
  }

  function setZoom(zoom) {
    map.getMap().fitBounds(getGeoJSON().getBounds())
    map.getMap().setZoom(zoom)
  }

  afterNavigate(async ({to}) => {
    if (to?.route?.id === '/explore/[[code]]') {
      exploreCode.set(code)
      if (code && !to?.url?.searchParams?.get('map')) {
        setTimeout(() => {
          map.getMap().fitBounds(getGeoJSON().getBounds())
        }, 1000)
      }
    }
  })

  function filterTasks(geoJsonData, muncode, type, difficulty, ad_status, bu_status) {
    let data = geoJsonData?.features || []
    if (data) {
      if (muncode) data = data.filter(t => t.properties.muncode === muncode)
      if (type) data = data.filter(t => t.properties.type === type)
      if (difficulty) data = data.filter(t => t.properties.difficulty === difficulty)
      if (ad_status) data = data.filter(t => t.properties.ad_status === ad_status)
      if (bu_status) data = data.filter(t => t.properties.bu_status === bu_status)
    }
    return { type: 'FeatureCollection', features: data }
  }

  function handleMoveEnd() {
    if (geoJsonData) goto(`${$page.url.pathname}?map=${getUrl()}`, { replaceState: true })
  }

  function handleClick(event, feature) {
    const t = target(zoom)
    if (event.originalEvent.detail === 1) {
      timer = setTimeout(() => {
        if (t === 'tasks') {
          goto('/explore/task/' + feature.properties.id)
        } else if (t === 'municipalities') {
          goto('/explore/' + feature.properties.muncode)
        } else if (t === 'provinces') {
          goto('/explore/' + feature.properties.provcode)
        }
      }, 200)
    }
	}

  function handleMouseover(feature, layer) {
    if (activeItem && !layer) {
      activeItem = null
    } else if (!activeItem && layer) {
      activeItem = feature
    }
    layer?.bringToFront()
  }

  function setStyle(feature, activeItem) {
    let style

    if (!pattern) {
      const shape = new L.PatternPath({
        x: 6,
        y: 6,
        color: 'red',
        d: "M9.182 9.182C10.93935 7.4246 10.93935 4.57538 9.182 2.81802C7.4246 1.06066 4.57538 1.06066 2.81802 2.81802M9.182 9.182C7.4246 10.93935 4.57538 10.93935 2.81802 9.182C1.06066 7.4246 1.06066 4.57538 2.81802 2.81802M9.182 9.182L2.81802 2.81802",
        fill: false,
        opacity: 1,
      })
      pattern = new L.Pattern({width:18, height:18, color: 'red'})
      pattern.addShape(shape)
      pattern.addTo(map.getMap())
    }

    if (target(zoom) === 'tasks') {
      const options = {
        color: feature.properties.lock_id ? TASK_LOCKED_COLOR : TASK_COLORS[feature.properties.bu_status],
        spaceColor: feature.properties.lock_id ? TASK_LOCKED_COLOR : TASK_COLORS[feature.properties.ad_status],
        opacity: 1,
        spaceOpacity: 1,
        angle: -45,
      }
      const stripes = new L.StripePattern(options)
      stripes.addTo(map.getMap())
      style = {
        fillPattern: feature.properties.lock_id ? pattern : stripes,
        fillOpacity: 1,
      }
    } else {
      style = { 
        fillPattern: feature?.properties?.update_id ? pattern : null,
        fillColor: 'blue',
        fillOpacity: feature?.properties?.update_id ? 0.6 : 0.2,
      }
    }
    if (feature.properties.id === activeItem?.properties?.id) {
      style.weight = 2
      style.color = 'black'
    } else {
      style.weight = 1
      style.color = AREA_BORDER 
    }
    return style
  }

  function getStatus(feat) {
    if (feat.lock_id) {
      return $t('explore.locked')
    } else if (feat.bu_status === feat.ad_status) {
      return $t('explore.' + feat.bu_status)
    } else {
      let st = `${$t('explore.' + feat.bu_status)} (${$t('explore.buildings')})`
      st += `, ${$t('explore.' + feat.ad_status)} (${$t('explore.addresses')})`
      return st
    }
  }

  function featInfo(feat) {
    let info = ''
    if (feat.provcode) {
      info = `<ul><li>${$t('explore.Prov')}: ${feat.name} (${feat.provcode})</li>`
    } else {
      info = `<ul><li>${$t('explore.Mun')}: ${feat.name} (${feat.muncode})</li>`
    }
    if (feat.localid) {
      info += `
        <li>${$t('explore.type')}: ${$t('explore.' + feat.type)}</li>
        <li>${$t('explore.diff')}: ${$t('explore.' + feat.difficulty)}</li>
        <li>${$t('explore.status')}: ${getStatus(feat)}</li>
      `
    } else {
      const mapped = feat.mapped_count / feat.task_count
      info += `
        <li>${$t('explore.tasks')}: ${feat.task_count}</li>
        <li>${$t('explore.mapped')}: ${fmt.format(mapped)}</li>
      `
    }
    info += '</ul>'
    return info
  }

  $: geoJsonOptions = {
    style: (feature) => setStyle(feature, activeItem),
    onEachFeature: function(feature, layer) {
      layer.bindTooltip(featInfo(feature.properties))
      layer.on('click', (event) => handleClick(event, feature))
      layer.on('dblclick', () => clearTimeout(timer))
      layer.on('mouseover', () => handleMouseover(feature, layer))
      layer.on('mouseout', () => handleMouseover(null, null))
    },
  }
</script>

<div class="flex flex-col md:flex-row flex-grow">
  <div class="w-full flex-grow z-0">
    <Map
      bind:map
      bind:center
      bind:zoom
      bind:getUrl
      on:moveend={handleMoveEnd}
    >
      <GeoJSON data={tasks} options={geoJsonOptions} bind:getGeoJSON/>
      {#if zoom >= TASK_THR}
        <Legend title={$t('explore.legend')}>
          <TaskStatus status="READY"/>
          <TaskStatus status="MAPPED"/>
          <TaskStatus status="INVALIDATED"/>
          <TaskStatus status="VALIDATED"/>
          <TaskStatus status="NEED_UPDATE"/>
          <TaskStatus status="MIXED"/>
          <TaskStatus status="LOCKED"/>
        </Legend>
      {/if}
    </Map>
  </div>
  <div class={rightBarClass}>
    <div class="h-full max-h-0">
      {#await dataPromise}
        <p class="mt-4">{$t('common.loading')} <Spinner size={4}/></p>
      {:then geoJsonData}
        {#if target(zoom) === 'tasks'}
          {#if geoJsonData?.features?.length > 0}
            <TaskList
              tasks={tasks.features}
              bind:muncode
              bind:type
              bind:difficulty
              bind:ad_status
              bind:bu_status
              bind:activeItem
              on:click={(event) => handleClick(event.detail.feature)}
              on:mouseover={(event) => handleMouseover(event.detail.feature)}
              on:mouseout={() => handleMouseover()}
            />
          {:else}
            <p class="w-full bg-neutral-100 dark:bg-neutral-700 p-2 mt-3">
              {$t('explore.noitems', { items: $t('tasks') })}
            </p>
          {/if}
        {:else if target(zoom) === 'municipalities' && code?.length === 5}
          <div class="prose dark:prose-invert pt-3">
            <h3>{project?.name} ({project?.muncode})</h3>
          </div>
          <div class="space-y-6 pt-4">
            <div class="!space-y-1">
              <p class="flex justify-between">
                <span>{$t('explore.tasks')}:</span>
                <span>{project?.task_count}</span>
              </p>
              {#if project?.task_count}
                <p class="flex justify-between">
                  <span>{$t('explore.mapped')}:</span>
                  <span>{fmt.format(project.mapped_count / project?.task_count)}</span>
                </p>
                <Progressbar
                  progress = {100 * project.mapped_count / project.task_count}
                  size="h-4"
                  color="gray"
                />
              {/if}
            </div>
            {#await statsPromise}
              <p class="mt-4">{$t('common.loading')} <Spinner size={4}/></p>
            {:then stats}
              <StatsSection {stats} omit={['users']} size={'text-4xl'}/>
            {/await}
            <p>
              <button class="text-primary-600" on:click={() => setZoom(TASK_THR)}>
                {$t('explore.zoom')}
              </button>
              {@html $t('explore.fortasksorprovs')}</p>
          </div>
        {:else}
          {#if target(zoom) === 'provinces' && code?.length === 2}
            <div class="prose dark:prose-invert pt-3">
              <h3>{project?.name} ({project?.provcode})</h3>
            </div>
          {/if}
          <ProjList
            data={geoJsonData?.features}
            target={target(zoom)}
            bind:activeItem
            {map}
            on:mouseover={(event) => handleMouseover(event.detail.feature)}
            on:mouseout={() => handleMouseover()}
          />
          {#if code?.length == 2}
            <p class="pt-4">
              {@html $t('explore.remainingprovs')}
            </p>
          {/if}
        {/if}
      {/await}
    </div>
  </div>
</div>
